from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status

from django.db.models import F

from .models import *
from .serializers import *


# class based views
class ListPersonalInfo(generics.ListCreateAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer


class DetailPersonalInfo(generics.RetrieveUpdateDestroyAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer


class ListInterviewer(generics.ListCreateAPIView):
    queryset = Interviewer.objects.all()
    serializer_class = InterviewerSerializer


class DetailInterviewer(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interviewer.objects.all()
    serializer_class = InterviewerSerializer


class ListInterviewee(generics.ListCreateAPIView):
    queryset = Interviewee.objects.all()
    serializer_class = IntervieweeSerializer


class DetailInterviewee(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interviewee.objects.all()
    serializer_class = IntervieweeSerializer


class ListInterviewSlot(generics.ListCreateAPIView):
    queryset = InterviewSlot.objects.all()
    serializer_class = InterviewSlotSerializer


class DetailInterviewSlot(generics.RetrieveUpdateDestroyAPIView):
    queryset = InterviewSlot.objects.all()
    serializer_class = InterviewSlotSerializer


class ListInterviewData(generics.ListCreateAPIView):
    queryset = InterviewData.objects.all()
    serializer_class = InterviewDataSerializer


class DetailInterviewData(generics.RetrieveUpdateDestroyAPIView):
    queryset = InterviewData.objects.all()
    serializer_class = InterviewDataSerializer


# other views
@api_view(['GET', 'POST'])
def interviewer_slot_list(request):
    if request.method == 'GET':
        interview_slots = InterviewSlot.objects.all().filter(current_interviewers__lt=F('max_interviewers'))

        interviewer_slot_serializer = GetInterviewerSlotSerializer(interview_slots, many=True)
        return JsonResponse(interviewer_slot_serializer.data, safe=False)

        # serialized_data = serializers.serialize('json', interview_slots, fields='datetime')
        # print(serialized_data)
        # interview_slot_serializer = InterviewSlotSerializer(interview_slots, many=True)
        # return JsonResponse(interview_slot_serializer.data, safe=False)

    elif request.method == 'POST':
        interviewer_slot_data = JSONParser().parse(request)
        interviewer_slot_serializer = PostInterviewerSlotSerializer(data=interviewer_slot_data)
        if interviewer_slot_serializer.is_valid():
            # print(interviewer_slot_serializer.data['availableTimes'])
            for timeslot in interviewer_slot_serializer.data['availableTimes']:
                # print(timeslot)
                interviewer = Interviewer.objects.get(user__first_name='Jane')
                interviewee = Interviewee.objects.get(user__first_name='John')
                interview_slot = InterviewSlot.objects.get(datetime=timeslot)

                # general try catch for now
                try:
                    InterviewData.objects.create(
                        interviewer=interviewer,
                        interviewee=interviewee,
                        interview_slot=interview_slot,
                    )
                except:
                    pass
            return JsonResponse(interviewer_slot_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(interviewer_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def interviewee_slot_list(request):
    if request.method == 'GET':
        interview_slots = InterviewSlot.objects.all().filter(
            current_interviewers__lt=F('max_interviewers')
        ).filter(
            current_interviewers__gt=0
        )

        interviewee_slot_serializer = GetIntervieweeSlotSerializer(interview_slots, many=True)
        return JsonResponse(interviewee_slot_serializer.data, safe=False)

        # interviewee_slot_serializer = InterviewSlotSerializer(interview_slots, many=True)
        # return JsonResponse(interviewee_slot_serializer.data, safe=False)

    elif request.method == 'POST':
        interviewee_slot_data = JSONParser().parse(request)
        interviewee_slot_serializer = InterviewSlotSerializer(data=interviewee_slot_data)
        if interviewee_slot_serializer.is_valid():
            interviewee_slot_serializer.save()
            return JsonResponse(interviewee_slot_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(interviewee_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
