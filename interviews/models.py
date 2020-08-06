from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PersonalInfo(models.Model):
    # fields
    degree_one = models.CharField(max_length=150, blank=True)
    degree_two = models.CharField(max_length=150, blank=True)
    major_one = models.CharField(max_length=150, blank=True)
    major_two = models.CharField(max_length=150, blank=True)


class Interviewer(models.Model):
    # fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # one user to one interviewer
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.CASCADE)  # to streamline all the personal info
    digital_impact = models.BooleanField(default=False)  # false = strategy

    class Meta:
        ordering = ['user']

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class Interviewee(models.Model):
    # fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # one user to one interviwee
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.CASCADE)  # to streamline all the personal info
    digital_impact = models.BooleanField(default=False)  # false = strategy
    previous_score = models.IntegerField()

    class Meta:
        ordering = ['user']

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class InterviewSlot(models.Model):
    # fields
    # setting day choices
    MONDAY = "MON"
    TUESDAY = "TUE"
    WEDNESDAY = "WED"
    THURSDAY = "THU"
    FRIDAY = "FRI"
    SATURDAY = "SAT"
    SUNDAY = "SUN"
    DAY_CHOICES = (
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    )
    day = models.CharField(
        max_length=3,
        choices=DAY_CHOICES,
        # fail safe but ideally should never default (should always be set)
        default=MONDAY,
    )

    datetime = models.DateTimeField()
    max_interviewees = models.IntegerField()
    current_interviewees = models.IntegerField()
    max_interviewers = models.IntegerField()
    current_interviewers = models.IntegerField()

    class Meta:
        ordering = ['datetime']

    def __str__(self):
        return "%s" % self.datetime


class InterviewData(models.Model):
    interviewer = models.ForeignKey(Interviewer, on_delete=models.PROTECT, null=True)
    interviewee = models.ForeignKey(Interviewee, on_delete=models.PROTECT, null=True)
    interview_slot = models.ForeignKey(InterviewSlot, on_delete=models.PROTECT)
    invigilator = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, null=True, related_name='invigilator')
    standby = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, null=True, related_name='standby')
    room = models.CharField(null=True, blank=True, max_length=50)
    stream = models.CharField(null=True, blank=True, max_length=150)
    full = models.BooleanField(default=False)
    digital_impact = models.BooleanField(default=False)  # false = strategy

    class Meta:
        ordering = ['interview_slot']

    def __str__(self):
        if self.room is None:
            return "%s %s, Room Not Set" % (self.interviewer, self.interviewee)
        else:
            return "%s %s, Room %s" % (self.interviewer, self.interviewee, self.room)
