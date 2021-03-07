from django.http.response import JsonResponse
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import PasswordResetForm

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from django.db.models import F, Q, Count

import csv
import io
import yagmail
import smtplib

from .models import Option, Interviewer, Interviewee, InterviewData
from .serializers import InterviewerSerializer, IntervieweeSerializer, InterviewTimeslotSerializer, \
    GetIntervieweeSlotSerializer, GetInterviewerSlotSerializer, GetInterviewDetailsSerializer, CreateTimesSerializer, \
    PasswordChangeSerializer, PasswordResetSerializer, InterviewerRegisterSerializer, IntervieweeRegisterSerializer, \
    SendEmailSerializer


class LoginView(APIView):
    def post(self, request):
        print(request)
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        if hasattr(user, 'interviewer'):
            position = 'interviewer'
        elif hasattr(user, 'interviewee'):
            position = 'interviewee'
        else:
            raise Exception("Error in config")

        response = {
            'token': token.key,
            'position': position,
            'is_staff': user.is_staff
        }
        return JsonResponse(response)


class IntervieweeDetails(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            interviewee = Interviewee.objects.get(user=request.user)
            interviewee_serializer = IntervieweeSerializer(interviewee)
            return JsonResponse(interviewee_serializer.data)
        except ObjectDoesNotExist:
            response = {'errors': "user isn't an interviewee"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


class InterviewerDetails(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            interviewer = Interviewer.objects.get(user=request.user)
            interviewer_serializer = InterviewerSerializer(interviewer)
            return JsonResponse(interviewer_serializer.data)
        except ObjectDoesNotExist:
            response = {'errors': "user isn't an interviewer"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


class InterviewDetails(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if hasattr(request.user, 'interviewer'):
            interview_data = InterviewData.objects.filter(interviewers__user=request.user)
        elif hasattr(request.user, 'interviewee'):
            interview_data = InterviewData.objects.filter(interviewees__user=request.user)
        else:
            response = {'errors': "user isn't an interviewer or interviewee"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        interview_details_serializer = GetInterviewDetailsSerializer(interview_data, many=True)
        return JsonResponse(interview_details_serializer.data, safe=False)


class InterviewerSlotList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        interview_slots = InterviewData.objects.annotate(current_interviewers=interviewers.count()) \
                                               .filter(Q(current_interviewers__lt=F('max_interviewers')) | Q(interviewers__user=request.user))

        if hasattr(request.user, 'interviewer'):
            interview_slots = interview_slots.filter(digital_impact=request.user.interviewer.digital_impact)
        else:
            response = {'errors': "current user isn't an interviewer"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

        interviewer_slot_serializer = GetInterviewerSlotSerializer(interview_slots, many=True)
        return JsonResponse(interviewer_slot_serializer.data, safe=False)

    # POST request receives a list of chosen times
    # and returns their allocation(s)
    # NB interviewers can have multiple allocations as long as they don't clash
    # resubmissions will just reset old times and reallocate
    def post(self, request):
        # check if interviewer "applications" are closed
        interviewer_option = Option.objects.get(name="interviewer_register")
        if interviewer_option.option is True:
            # parse and generate serializer
            interviewer_slot_data = JSONParser().parse(request)
            interviewer_slot_serializer = InterviewTimeslotSerializer(data=interviewer_slot_data)
            interviewer_slot_serializer.is_valid(raise_exception=True)
            interviewer = Interviewer.objects.get(user=request.user)  # get model for current user

            # if interviewer already has times, nuke all their old times
            old_interview_slots = InterviewData.objects.filter(interviewers=interviewer)
            for old_interview_slot in old_interview_slots:
                old_interview_slot.interviewers.remove(interviewer)
                old_interview_slot.save()

            # pull all available times
            count = 0
            for timeslot in interviewer_slot_serializer.validated_data['availableTimes']:
                interview_slots = InterviewData.objects.filter(digital_impact=request.user.interviewer.digital_impact, datetime=timeslot)

                for interview_slot in interview_slots:
                    # assign slot if there's space and max assigned interviews not hit yet
                    if (interview_slot.interviewers.count() < interview_slot.max_interviewers):
                        count += 1
                        interview_slot.interviewers.add(interviewer)
                        interview_slot.save()
                        break

            if count == 0:
                response = {'errors': 'Not allocated a time'}
                return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse(interviewer_slot_serializer.data, status=status.HTTP_201_CREATED)
        else:
            response = {'errors': 'interviewer applications closed'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


class IntervieweeSlotList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        interview_slots = InterviewData.objects.annotate(current_interviewees=Count('interviewees'), current_interviewers=Count('interviewers')) \
                                               .filter(current_interviewees__lt=F('max_interviewees')).filter(current_interviewers__exact=F('max_interviewers'))

        if hasattr(request.user, 'interviewee'):
            interview_slots = interview_slots.filter(digital_impact=request.user.interviewee.digital_impact)
        else:
            response = {'errors': "current user isn't an interviewee"}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

        interviewee_slot_serializer = GetIntervieweeSlotSerializer(interview_slots, many=True)
        return JsonResponse(interviewee_slot_serializer.data, safe=False)

    # POST request receives a list of chosen times
    # and returns their allocation
    # NB interviewees can only have 1 allocated time, so a redo will delete old allocation and reallocate
    # atm not implemented, 1 submission = 1 time
    def post(self, request):
        # check if interviewee "applications" are closed
        interviewer_option = Option.objects.get(name="interviewee_register")
        if interviewer_option.option is True:
            # parse and generate serializer
            interviewee_slot_data = JSONParser().parse(request)
            interviewee_slot_serializer = InterviewTimeslotSerializer(data=interviewee_slot_data)
            interviewee_slot_serializer.is_valid(raise_exception=True)
            interviewee = Interviewee.objects.get(digital_impact=request.user.interviewee.digital_impact, user=request.user)  # get model for current user

            # if interviewee already has times, nuke all their old times
            old_interview_slots = InterviewData.objects.filter(interviewees=interviewee)
            for old_interview_slot in old_interview_slots:
                old_interview_slot.interviewees.remove(interviewee)
                old_interview_slot.save()

            # pull all available times
            for timeslot in interviewee_slot_serializer.validated_data['availableTimes']:
                interview_slots = InterviewData.objects.filter(digital_impact=request.user.interviewee.digital_impact,datetime=timeslot)

                for interview_slot in interview_slots:
                    # check if there's space
                    if interview_slot.interviewees.count() < interview_slot.max_interviewees and interview_slot.interviewers.count() == interview_slot.max_interviewers:
                        interview_slot.interviewees.add(interviewee)
                        interview_slot.save()

                        if interview_slot.room is None:
                            interviewRoom = 'Room Not Set'
                        else:
                            interviewRoom = interview_slot.room

                        response = {
                            'interviewTime': timeslot,
                            'interviewRoom': interviewRoom
                        }
                        return JsonResponse(response, status=status.HTTP_201_CREATED)

            # if we exit the for loop we didn't find anything
            # temp error response
            response = {'errors': 'Not able to be allocated'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {'errors': 'interviewee applications closed'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


# API view for bulk creating interview times
class CreateTimes(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        request_data = JSONParser().parse(request)
        create_times_serializer = CreateTimesSerializer(data=request_data)
        create_times_serializer.is_valid(raise_exception=True)
        interviewer_num = create_times_serializer.validated_data['interviewer_num']
        interviewee_num = create_times_serializer.validated_data['interviewee_num']
        for i in range(create_times_serializer.validated_data['digital_impact_num']):
            for timeslot in create_times_serializer.validated_data['times']:
                InterviewData.objects.create(datetime=timeslot, digital_impact=True, max_interviewers=interviewer_num, max_interviewees=interviewee_num)
        for j in range(create_times_serializer.validated_data['strategy_num']):
            for timeslot in create_times_serializer.validated_data['times']:
                InterviewData.objects.create(datetime=timeslot, digital_impact=False, max_interviewers=interviewer_num, max_interviewees=interviewee_num)
        response = {'status': 'times successfully made'}
        return JsonResponse(response)


# API view for updating if interviewers can submit or not
class InterviewerOpen(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        interviewer_option = Option.objects.get(name="interviewer_register")
        response = {'interviewer_registration_open': interviewer_option.option}
        return JsonResponse(response)
        
    def post(self, request):
        interviewer_register_data = JSONParser().parse(request)
        interviewer_register_data_serializer = InterviewerRegisterSerializer(data=interviewer_register_data)
        interviewer_register_data_serializer.is_valid(raise_exception=True)
        interviewer_option = Option.objects.get(name="interviewer_register")
        interviewer_option.option = interviewer_register_data_serializer.validated_data['interviewer_registration_open']
        interviewer_option.save()
        response = {'status': 'success'}
        return JsonResponse(response)


# API view for updating if interviewees can submit or not

class IntervieweeOpen(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        interviewee_option = Option.objects.get(name="interviewee_register")
        response = {'interviewee_registration_open': interviewee_option.option}
        return JsonResponse(response)

    def post(self, request):
        interviewee_register_data = JSONParser().parse(request)
        interviewee_register_data_serializer = IntervieweeRegisterSerializer(data=interviewee_register_data)
        interviewee_option = Option.objects.get(name="interviewee_register")
        interviewee_register_data_serializer.is_valid(raise_exception=True)
        interviewee_option.option = interviewee_register_data_serializer.validated_data['interviewee_registration_open']
        interviewee_option.save()
        response = {'status': 'success'}
        return JsonResponse(response)


# API view for changing password
class ChangePassword(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # parse and generate serializer
        password_data = JSONParser().parse(request)
        password_data_serializer = PasswordChangeSerializer(data=password_data)

        password_data_serializer.is_valid(raise_exception=True)
        # check if old password matches
        if request.user.check_password(password_data_serializer.data['old_password']) is True:
            # if it does then set new password
            request.user.set_password(password_data_serializer.data['new_password'])
            request.user.save()
            response = {'status': 'success'}
            return JsonResponse(response)
        else:
            # if old password is wrong don't change password
            response = {'errors': 'old password incorrect'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


class SendEmail(APIView):

    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        send_email_data_serializer = SendEmailSerializer(data=request.data)
        send_email_data_serializer.is_valid(raise_exception=True)
        email = send_email_data_serializer.validated_data["email"]
        password = send_email_data_serializer.validated_data["password"]
        file_bytes = send_email_data_serializer.validated_data["file_dict"].read()
        subject_raw = send_email_data_serializer.validated_data["subject"]
        content_raw = send_email_data_serializer.validated_data["content"]
        try:
            sig_bytes = send_email_data_serializer.validated_data["signature"].read()
            sig = sig_bytes.decode("utf-8").replace('\n', '')
        except KeyError:
            sig = None
        dict_reader = csv.DictReader(io.StringIO(file_bytes.decode("utf-8")))
        
        try:
            with yagmail.SMTP(email, password) as yag:
                for row in dict_reader:
                    to_addr = row['address']
                    subject = subject_raw.format(**row)
                    content = content_raw.format(**row)
                    contents = [content]
                    if (sig):
                        contents.append(sig)
                    yag.send(to=to_addr, subject=subject, contents=contents)
            status_str = "success"
            message = ""
            status_code = status.HTTP_200_OK
        except smtplib.SMTPAuthenticationError:
            status_str = "fail"
            message = "Authentication error"
            status_code = status.HTTP_401_UNAUTHORIZED
        except KeyError as e:
            status_str = "fail"
            message = "Key error"
            status_code = status.HTTP_403_FORBIDDEN
        except ValueError:
            status_str = "fail"
            message = "Value error"
            status_code = status.HTTP_403_FORBIDDEN
        return JsonResponse({"status": status_str, "message": message}, status=status_code)


# # API view for resetting password
# # doesn't work rn
# @api_view(['POST'])
# def reset_password(request):
#     if request.method == 'POST':
#         # parse and generate serializer
#         email_data = JSONParser().parse(request)
#         email_data_serializer = PasswordResetSerializer(data=email_data)

#         if email_data_serializer.is_valid():
#             password_reset_form = PasswordResetForm(
#                 data=email_data_serializer.data)
#             print(email_data_serializer.data)
#             if password_reset_form.is_valid():
#                 password_reset_form.save(domain_override="testdomain.com")
#                 response = {'status': 'success'}
#                 return JsonResponse(response)
#             else:
#                 return JsonResponse(password_reset_form.errors, status=status.HTTP_400_BAD_REQUEST)

#         else:
#             return JsonResponse(email_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# def reset_password_confirm(request, uidb64, token):
#     return


# outputs a csv of all interviewees
class CSVInterviewees(APIView):

    def get(self, request):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="interviewee_list.csv"'
        writer = csv.writer(response)
        header = ['First Name', 'Last Name', 'Interview Slot(s)', 'Digital Impact']
        writer.writerow(header)
        for interviewee in Interviewee.objects.all():
            interview_slots = []
            for interview_slot in interviewee.interviewdata_set.all():
                interview_data = [
                    interview_slot.datetime.strftime("%d/%m/%y,%H:%M"),
                    interview_slot.room
                ]
                interview_slots.append(interview_data)

            row = [
                interviewee.user.first_name,
                interviewee.user.last_name,
                interview_slots,
                interviewee.digital_impact,
            ]

            writer.writerow(row)

        return response


# outputs a csv of all interviewers
class CSVInterviewers(APIView):

    def get(self, request):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="interviewer_list.csv"'
        writer = csv.writer(response)
        header = ['First Name', 'Last Name', 'Interview Slot(s)', 'Digital Impact']
        writer.writerow(header)
        for interviewer in Interviewer.objects.all():
            interview_slots = []
            for interview_slot in interviewer.interviewdata_set.all():
                interview_data = [
                    interview_slot.datetime.strftime("%d/%m/%y,%H:%M"),
                    interview_slot.room
                ]
                interview_slots.append(interview_data)

            row = [
                interviewer.user.first_name,
                interviewer.user.last_name,
                interview_slots,
                interviewer.digital_impact,
            ]

            writer.writerow(row)

        return response