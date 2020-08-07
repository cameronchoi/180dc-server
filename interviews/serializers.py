from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class IntervieweeSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Interviewee
        fields = '__all__'


class InterviewerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Interviewer
        fields = '__all__'



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
