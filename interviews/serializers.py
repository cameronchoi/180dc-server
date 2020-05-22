from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PersonalInfo, Interviewer, Interviewee, InterviewSlot, InterviewData


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        ]
        model = User


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'degree_one',
            'degree_two',
            'major_one',
            'major_two',
        )
        model = PersonalInfo


class IntervieweeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    personal_info = PersonalInfoSerializer()

    class Meta:
        fields = [
            'user',
            'personal_info',
            'digital_impact',
            'previous_score',
        ]
        model = Interviewee

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        personal_info_data = validated_data.pop('personal_info')
        user = User.objects.create(**user_data)
        personal_info = PersonalInfo.objects.create(**personal_info_data)
        interviewee = Interviewee.objects.create(user=user, personal_info=personal_info, **validated_data)
        return interviewee


class InterviewerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    personal_info = PersonalInfoSerializer()

    class Meta:
        fields = (
            'user',
            'personal_info',
            'digital_impact',
        )
        model = Interviewer

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        personal_info_data = validated_data.pop('personal_info')
        user = User.objects.create(**user_data)
        personal_info = PersonalInfo.objects.create(**personal_info_data)
        interviewer = Interviewer.objects.create(user=user, personal_info=personal_info, **validated_data)
        return interviewer


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
