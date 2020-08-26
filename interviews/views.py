from django.http.response import JsonResponse
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import PasswordResetForm

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token

from django.db.models import F
from django.db.models import Q

import csv

from .models import Option, Interviewer, Interviewee, InterviewData
from .serializers import InterviewerSerializer, IntervieweeSerializer, InterviewTimeslotSerializer, \
    GetIntervieweeSlotSerializer, GetInterviewerSlotSerializer, GetInterviewDetailsSerializer, \
    PasswordChangeSerializer, PasswordResetSerializer, InterviewerRegisterSerializer


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
            'position': position,
            'is_staff': user.is_staff
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
            interview_data = InterviewData.objects.filter(
                interviewers__user=request.user)
        else:
            interview_data = InterviewData.objects.filter(
                interviewees__user=request.user)

        interview_details_serializer = GetInterviewDetailsSerializer(
            interview_data, many=True)
        return JsonResponse(interview_details_serializer.data, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def interviewer_slot_list(request):
    # GET request is a list of available times that interviewers can submit to
    if request.method == 'GET':
        interview_slots = InterviewData.objects.all().filter(
            Q(current_interviewers__lt=F('max_interviewers')) | Q(interviewers__user=request.user))

        if hasattr(request.user, 'interviewer'):
            interview_slots = interview_slots.filter(
                digital_impact=request.user.interviewer.digital_impact
            )
        else:
            response = {'errors': "current user isn't an interviewer"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

        interviewer_slot_serializer = GetInterviewerSlotSerializer(
            interview_slots, many=True)
        return JsonResponse(interviewer_slot_serializer.data, safe=False)

    # POST request receives a list of chosen times
    # and returns their allocation(s)
    # NB interviewers can have multiple allocations as long as they don't clash
    # resubmissions will just reset old times and reallocate
    elif request.method == 'POST':
        # check if interviewer "applications" are closed
        interviewer_option = Option.objects.get(name="interviewer_register")
        if interviewer_option.option is True:
            # parse and generate serializer
            interviewer_slot_data = JSONParser().parse(request)
            interviewer_slot_serializer = InterviewTimeslotSerializer(
                data=interviewer_slot_data)
            if interviewer_slot_serializer.is_valid():
                interviewer = Interviewer.objects.get(
                    user=request.user)  # get model for current user

                # if interviewer already has times, nuke all their old times
                old_interview_slots = InterviewData.objects.filter(
                    interviewers=interviewer)
                for old_interview_slot in old_interview_slots:
                    old_interview_slot.current_interviewers -= 1
                    old_interview_slot.interviewers.remove(interviewer)
                    old_interview_slot.save()

                # pull all available times
                count = 0
                for timeslot in interviewer_slot_serializer.data['availableTimes']:
                    interview_slot = InterviewData.objects.get(
                        digital_impact=request.user.interviewer.digital_impact,
                        datetime=timeslot)

                    # assign slot if there's space and max assigned interviews not hit yet
                    if (
                            interview_slot.current_interviewers < interview_slot.max_interviewers
                    ):
                        try:  # general try catch for now
                            count += 1
                            interview_slot.interviewers.add(interviewer)
                            interview_slot.current_interviewers += 1
                            interview_slot.save()
                        except:
                            pass

                if count == 0:
                    response = {'errors': 'Not allocated a time'}
                    return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

                return JsonResponse(interviewer_slot_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(interviewer_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            response = {'errors': 'interviewer applications closed'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def interviewee_slot_list(request):
    # GET request is a list of available times that interviewees can submit to
    if request.method == 'GET':
        interview_slots = InterviewData.objects.filter(current_interviewees__lt=F(
            'max_interviewees')).filter(current_interviewers__exact=F('max_interviewers'))

        if hasattr(request.user, 'interviewee'):
            interview_slots = interview_slots.filter(
                digital_impact=request.user.interviewee.digital_impact
            )
        else:
            response = {'errors': "current user isn't an interviewee"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

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
            interviewee = Interviewee.objects.get(
                digital_impact=request.user.interviewee.digital_impact,
                user=request.user)  # get model for current user

            # if interviewee already has times, nuke all their old times
            old_interview_slots = InterviewData.objects.filter(
                interviewees=interviewee)
            for old_interview_slot in old_interview_slots:
                old_interview_slot.current_interviewees -= 1
                old_interview_slot.interviewees.remove(interviewee)
                old_interview_slot.save()

            # pull all available times
            for timeslot in interviewee_slot_serializer.data['availableTimes']:
                interview_slot = InterviewData.objects.get(datetime=timeslot)

                # check if there's space
                if interview_slot.current_interviewees < interview_slot.max_interviewees:
                    try:  # general try catch for now
                        print("it comes here")
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
                        # temp error response
                        response = {'errors': 'try/catch'}
                        return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

            # if we exit the for loop we didn't find anything
            # temp error response
            response = {'errors': 'Was not able to be allocated'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(interviewee_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API view for updating if interviewers can submit or not
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def interviewer_open(request):
    if request.method == 'GET':
        interviewer_option = Option.objects.get(name="interviewer_register")
        if interviewer_option.option is True:
            response = {'interviewer_registration_open': True}
        else:
            response = {'interviewer_registration_open': False}
        return JsonResponse(response)
    elif request.method == 'POST':
        interviewer_register_data = JSONParser().parse(request)
        interviewer_register_data_serializer = InterviewerRegisterSerializer(
            data=interviewer_register_data)
        interviewer_option = Option.objects.get(name="interviewer_register")
        if interviewer_register_data_serializer.is_valid():
            if interviewer_register_data_serializer.data['interviewer_registration_open'] is True:
                interviewer_option.option = True
                interviewer_option.save()
            else:
                interviewer_option.option = False
                interviewer_option.save()
            response = {'status': 'success'}
            return JsonResponse(response)
        else:
            return JsonResponse(interviewer_register_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API view for changing password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        # parse and generate serializer
        password_data = JSONParser().parse(request)
        password_data_serializer = PasswordChangeSerializer(data=password_data)

        if password_data_serializer.is_valid():
            # check if old password matches
            if request.user.check_password(password_data_serializer.data['old_password']) is True:
                # if it does then set new password
                request.user.set_password(
                    password_data_serializer.data['new_password'])
                request.user.save()
                response = {'status': 'success'}
                return JsonResponse(response)
            else:
                # if old password is wrong don't change password
                response = {'errors': 'old password incorrect'}
                return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(password_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API view for resetting password
# doesn't work rn
@api_view(['POST'])
def reset_password(request):
    if request.method == 'POST':
        # parse and generate serializer
        email_data = JSONParser().parse(request)
        email_data_serializer = PasswordResetSerializer(data=email_data)

        if email_data_serializer.is_valid():
            password_reset_form = PasswordResetForm(
                data=email_data_serializer.data)
            print(email_data_serializer.data)
            if password_reset_form.is_valid():
                password_reset_form.save(domain_override="testdomain.com")
                response = {'status': 'success'}
                return JsonResponse(response)
            else:
                return JsonResponse(password_reset_form.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return JsonResponse(email_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def reset_password_confirm(request, uidb64, token):
    return


# outputs a csv of all interviewees
def csv_interviewees(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="interviewee_list.csv"'

    writer = csv.writer(response)
    test = ['First Name', 'Last Name', 'Interview Slot(s)', 'Digital Impact']
    writer.writerow(test)

    for interviewee in Interviewee.objects.all():
        interview_slots = []

        for interview_slot in interviewee.interviewdata_set.all():
            interview_data = [
                interview_slot.datetime.strftime("%d/%m/%y,%H:%M"),
                interview_slot.room
            ]
            interview_slots.append(interview_data)

        if interviewee.digital_impact is True:
            digital_impact = "True"
        else:
            digital_impact = "False"

        row = [
            interviewee.user.first_name,
            interviewee.user.last_name,
            interview_slots,
            digital_impact,
        ]

        writer.writerow(row)

    return response


# outputs a csv of all interviewees
def csv_interviewers(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="interviewer_list.csv"'

    writer = csv.writer(response)
    test = ['First Name', 'Last Name', 'Interview Slot(s)', 'Digital Impact']
    writer.writerow(test)

    for interviewer in Interviewer.objects.all():
        interview_slots = []

        for interview_slot in interviewer.interviewdata_set.all():
            interview_data = [
                interview_slot.datetime.strftime("%d/%m/%y,%H:%M"),
                interview_slot.room
            ]
            interview_slots.append(interview_data)

        if interviewer.digital_impact is True:
            digital_impact = "True"
        else:
            digital_impact = "False"

        row = [
            interviewer.user.first_name,
            interviewer.user.last_name,
            interview_slots,
            digital_impact,
        ]

        writer.writerow(row)

    return response
