from django.shortcuts import render
from rest_framework import generics
from .models import PersonalInfo, Interviewer, Interviewee, InterviewSlot, InterviewData
from .serializers import PersonalInfoSerializer, InterviewerSerializer, IntervieweeSerializer, InterviewSlotSerializer, \
    InterviewDataSerializer


# Create your views here.

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