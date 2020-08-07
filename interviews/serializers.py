from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Interviewer, Interviewee, InterviewData


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


class IntervieweeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        fields = [
            'user',
            'degree_one',
            'degree_two',
            'major_one',
            'major_two',
            'digital_impact',
            'previous_score',
        ]
        model = Interviewee

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        interviewee = Interviewee.objects.create(user=user, **validated_data)
        return interviewee


class InterviewerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        fields = (
            'user',
            'degree_one',
            'degree_two',
            'major_one',
            'major_two',
            'digital_impact',
        )
        model = Interviewer

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        interviewer = Interviewer.objects.create(user=user, **validated_data)
        return interviewer


class InterviewDataSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'interviewers',
            'interviewees',
            'interview_slot',
            'invigilator',
            'standby',
            'room',
            'stream',
            'full',
            'digital_impact',
        )
        model = InterviewData


# test
class GetInterviewerSlotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    datetime = serializers.DateTimeField()


class GetIntervieweeSlotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    datetime = serializers.DateTimeField()


class InterviewTimeslotSerializer(serializers.Serializer):
    availableTimes = serializers.ListField(
        child=serializers.DateTimeField()
    )
