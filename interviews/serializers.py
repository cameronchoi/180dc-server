from rest_framework import serializers

from .models import Interviewee, Interviewer, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']


class IntervieweeSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Interviewee
        exclude = ['previous_score']


class InterviewerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Interviewer
        fields = '__all__'


class GetInterviewDetailsSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    interviewers = serializers.StringRelatedField(many=True)
    interviewees = serializers.StringRelatedField(many=True)
    room = serializers.CharField(max_length=50)
    digital_impact = serializers.BooleanField()


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

# serializer for bulk creating times


class CreateTimesSerializer(serializers.Serializer):
    times = serializers.ListField(
        child=serializers.DateTimeField()
    )
    digital_impact_num = serializers.IntegerField()
    strategy_num = serializers.IntegerField()
    interviewer_num = serializers.IntegerField()
    interviewee_num = serializers.IntegerField()

# serializer for interviewer registration option


class InterviewerRegisterSerializer(serializers.Serializer):
    interviewer_registration_open = serializers.BooleanField()


# serializer for interviewee registration option
class IntervieweeRegisterSerializer(serializers.Serializer):
    interviewee_registration_open = serializers.BooleanField()


# serializer for password change
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# serializer for password reset
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
