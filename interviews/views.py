from django.http.response import JsonResponse
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status

from django.db.models import F

from .models import *
from .serializers import *


# class based views
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
        interview_slots = InterviewData.objects.all().filter(
            current_interviewers__lt=F('max_interviewers'))

        interviewer_slot_serializer = GetInterviewerSlotSerializer(
            interview_slots, many=True)
        return JsonResponse(interviewer_slot_serializer.data, safe=False)

    elif request.method == 'POST':
        interviewer_slot_data = JSONParser().parse(request)
        interviewer_slot_serializer = InterviewTimeslotSerializer(
            data=interviewer_slot_data)
        if interviewer_slot_serializer.is_valid():
            for timeslot in interviewer_slot_serializer.data['availableTimes']:
                interviewer = Interviewer.objects.get(user__first_name='Jane')
                interview_slot = InterviewData.objects.get(datetime=timeslot)

                # check if got space
                if interview_slot.current_interviewers < interview_slot.max_interviewers:
                    # general try catch for now
                    try:
                        interview_slot.interviewers.add(interviewer)
                        interview_slot.current_interviewers += 1
                        interview_slot.save()
                    except:
                        pass
            return JsonResponse(interviewer_slot_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(interviewer_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def interviewee_slot_list(request):
    if request.method == 'GET':
        interview_slots = InterviewData.objects.all().filter(
            current_interviewees__lt=F('max_interviewees')
        )

        interviewee_slot_serializer = GetIntervieweeSlotSerializer(
            interview_slots, many=True)
        return JsonResponse(interviewee_slot_serializer.data, safe=False)

    elif request.method == 'POST':
        interviewee_slot_data = JSONParser().parse(request)
        interviewee_slot_serializer = InterviewTimeslotSerializer(
            data=interviewee_slot_data)
        if interviewee_slot_serializer.is_valid():
            for timeslot in interviewee_slot_serializer.data['availableTimes']:
                interview_slot = InterviewData.objects.get(datetime=timeslot)

                # if there's space
                if interview_slot.current_interviewees < interview_slot.max_interviewees:
                    interviewee = Interviewee.objects.get(
                        user__first_name='John')

                    try:
                        interview_slot.interviewees.add(interviewee)
                        interview_slot.current_interviewees += 1
                        interview_slot.save()

                        if interview_slot.room is not None:
                            response = {
                                'interviewTime': timeslot,
                                'interviewRoom': interview_slot.room
                            }
                            return JsonResponse(response, status=status.HTTP_201_CREATED)
                        else:
                            response = {
                                'interviewTime': timeslot,
                                'interviewRoom': 'Room Not Set'
                            }
                            return JsonResponse(response, status=status.HTTP_201_CREATED)
                    except:
                        response = {'errors': 'try/catch'}  # temp error response
                        return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

            # if we exit the for loop we didn't find anything
            response = {'errors': 'exit for loop'}  # temp error response
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(interviewee_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
