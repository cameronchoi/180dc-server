from django.http.response import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token

from django.db.models import F

from .models import Interviewer, Interviewee, InterviewData
from .serializers import InterviewerSerializer, IntervieweeSerializer, InterviewTimeslotSerializer, \
    GetIntervieweeSlotSerializer, GetInterviewerSlotSerializer, GetInterviewDetailsSerializer


@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        serializer = AuthTokenSerializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        if hasattr(user, 'interviewer'):
            position = 'interviewer'
        elif hasattr(user, 'interviewee'):
            position = 'interviewee'
        else:
            position = 'error'

        response = {
            'token': token.key,
            'position': position
        }
        return JsonResponse(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interviewee_details(request):
    if request.method == 'GET':
        try:
            interviewee = Interviewee.objects.get(user=request.user)
            interviewee_serializer = IntervieweeSerializer(interviewee)
            return JsonResponse(interviewee_serializer.data)
        except ObjectDoesNotExist:
            response = {'errors': "user isn't an interviewee"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interviewer_details(request):
    if request.method == 'GET':
        # first check if user is an interviewer
        try:
            interviewer = Interviewer.objects.get(user=request.user)
        except ObjectDoesNotExist:
            response = {'errors': "user isn't an interviewer"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

        interviewer_serializer = InterviewerSerializer(interviewer)
        return JsonResponse(interviewer_serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interview_details(request):
    if request.method == 'GET':
        # check if user is interviewer or interviewee
        if hasattr(request.user, 'interviewer'):
            interviewer = True
        elif hasattr(request.user, 'interviewee'):
            interviewer = False
        else:
            response = {'errors': "user isn't an interviewer or interviewee"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

        # now get all relevant interview data
        if interviewer:
            interview_data = InterviewData.objects.filter(interviewers__user=request.user)
        else:
            interview_data = InterviewData.objects.filter(interviewees__user=request.user)

        interview_details_serializer = GetInterviewDetailsSerializer(interview_data, many=True)
        return JsonResponse(interview_details_serializer.data, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def interviewer_slot_list(request):
    # GET request is a list of available times that interviewers can submit to
    if request.method == 'GET':
        interview_slots = InterviewData.objects.all().filter(
            current_interviewers__lt=F('max_interviewers'))

        interviewer_slot_serializer = GetInterviewerSlotSerializer(
            interview_slots, many=True)
        return JsonResponse(interviewer_slot_serializer.data, safe=False)

    # POST request receives a list of chosen times
    # and returns their allocation(s)
    # NB interviewers can have multiple allocations as long as they don't clash
    # resubmissions will just reset old times and reallocate
    elif request.method == 'POST':
        # parse and generate serializer
        interviewer_slot_data = JSONParser().parse(request)
        interviewer_slot_serializer = InterviewTimeslotSerializer(
            data=interviewer_slot_data)
        if interviewer_slot_serializer.is_valid():
            interviewer = Interviewer.objects.get(user=request.user)  # get model for current user

            # if interviewer already has times, nuke all their old times
            old_interview_slots = InterviewData.objects.filter(interviewers=interviewer)
            for old_interview_slot in old_interview_slots:
                old_interview_slot.interviewers.remove(interviewer)

            # pull all available times
            for timeslot in interviewer_slot_serializer.data['availableTimes']:
                interview_slot = InterviewData.objects.get(datetime=timeslot)

                # assign slot if there's space
                if interview_slot.current_interviewers < interview_slot.max_interviewers:
                    try:  # general try catch for now
                        interview_slot.interviewers.add(interviewer)
                        interview_slot.current_interviewers += 1
                        interview_slot.save()
                    except:
                        pass
            return JsonResponse(interviewer_slot_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(interviewer_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def interviewee_slot_list(request):
    # GET request is a list of available times that interviewees can submit to
    if request.method == 'GET':
        interview_slots = InterviewData.objects.all().filter(
            current_interviewees__lt=F('max_interviewees')
        )

        interviewee_slot_serializer = GetIntervieweeSlotSerializer(
            interview_slots, many=True)
        return JsonResponse(interviewee_slot_serializer.data, safe=False)

    # POST request receives a list of chosen times
    # and returns their allocation
    # NB interviewees can only have 1 allocated time, so a redo will delete old allocation and reallocate
    # atm not implemented, 1 submission = 1 time
    elif request.method == 'POST':
        # parse and generate serializer
        interviewee_slot_data = JSONParser().parse(request)
        interviewee_slot_serializer = InterviewTimeslotSerializer(
            data=interviewee_slot_data)
        if interviewee_slot_serializer.is_valid():
            interviewee = Interviewee.objects.get(user=request.user)  # get model for current user

            # if interviewee already has times, nuke all their old times
            old_interview_slots = InterviewData.objects.filter(interviewees=interviewee)
            for old_interview_slot in old_interview_slots:
                old_interview_slot.interviewees.remove(interviewee)

            # pull all available times
            for timeslot in interviewee_slot_serializer.data['availableTimes']:
                interview_slot = InterviewData.objects.get(datetime=timeslot)

                # check if there's space
                if interview_slot.current_interviewees < interview_slot.max_interviewees:
                    try:  # general try catch for now
                        interview_slot.interviewees.add(interviewee)
                        interview_slot.current_interviewees += 1
                        interview_slot.save()

                        # generate appropriate response (if room has been set already or not)
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
