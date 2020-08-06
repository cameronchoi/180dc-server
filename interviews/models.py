from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Interviewer(models.Model):
    # fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # one user to one interviewer
    degree_one = models.CharField(max_length=150, blank=True)
    degree_two = models.CharField(max_length=150, blank=True)
    major_one = models.CharField(max_length=150, blank=True)
    major_two = models.CharField(max_length=150, blank=True)
    digital_impact = models.BooleanField(default=False)  # false = strategy

    class Meta:
        ordering = ['user']

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class Interviewee(models.Model):
    # fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # one user to one interviwee
    degree_one = models.CharField(max_length=150, blank=True)
    degree_two = models.CharField(max_length=150, blank=True)
    major_one = models.CharField(max_length=150, blank=True)
    major_two = models.CharField(max_length=150, blank=True)
    digital_impact = models.BooleanField(default=False)  # false = strategy
    previous_score = models.IntegerField()

    class Meta:
        ordering = ['user']

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class InterviewData(models.Model):
    datetime = models.DateTimeField()
    interviewers = models.ManyToManyField(Interviewer, blank=True)
    interviewees = models.ManyToManyField(Interviewee, blank=True)
    max_interviewees = models.IntegerField(default=1)
    current_interviewees = models.IntegerField(default=0)
    max_interviewers = models.IntegerField(default=1)
    current_interviewers = models.IntegerField(default=0)
    room = models.CharField(null=True, blank=True, max_length=50)
    digital_impact = models.BooleanField(default=False)  # false = strategy

    # unneeded stuff for now
    # invigilator = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, null=True, related_name='invigilator')
    # standby = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, null=True, related_name='standby')
    # stream = models.CharField(null=True, blank=True, max_length=150)
    # full = models.BooleanField(default=False)

    class Meta:
        ordering = ['datetime']

    def __str__(self):
        if self.room is None:
            return "%s, Room Not Set" % self.datetime
        else:
            return "%s, Room %s" % (self.datetime, self.room)
