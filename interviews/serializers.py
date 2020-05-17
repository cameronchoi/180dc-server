from rest_framework import serializers
from .models import PersonalInfo, Interviewer, Interviewee, InterviewSlot, InterviewData

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'degree_one',
            'degree_two',
            'major_one',
            'major_two',
        )
        model = PersonalInfo

class InterviewerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user',
            'personal_info',
            'digital_impact',
        )
        model = Interviewer

class IntervieweeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user',
            'personal_info',
            'digital_impact',
            'previous_score',
        )
        model = Interviewee

class InterviewSlotSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'day',
            'datetime',
            'max_interviewees',
            'max_interviewers',
        )
        model = InterviewSlot

class InterviewDataSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'interviewer',
            'interviewee',
            'interview_slot',
            'invigilator',
            'standby',
            'room',
            'stream',
            'full',
            'digital_impact',
        )
        model = InterviewData