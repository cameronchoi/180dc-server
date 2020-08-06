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
    interviewer = models.ManyToManyField(Interviewer)
    interviewee = models.ManyToManyField(Interviewee)
    max_interviewees = models.IntegerField(default=1)
    current_interviewees = models.IntegerField(default=0)
    max_interviewers = models.IntegerField(default=1)
    current_interviewers = models.IntegerField(default=0)
    # invigilator = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, null=True, related_name='invigilator')
    # standby = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, null=True, related_name='standby')
    room = models.CharField(null=True, blank=True, max_length=50)
    # stream = models.CharField(null=True, blank=True, max_length=150)
    # full = models.BooleanField(default=False)
    digital_impact = models.BooleanField(default=False)  # false = strategy

    class Meta:
        ordering = ['datetime']

    def __str__(self):
        if self.room is None:
            if self.interviewer is None:
                return "No Interviewer, %s, Room Not Set" % self.interviewee
            elif self.interviewee is None:
                return "%s, No Interviewee, Room Not Set" % self.interviewer
            else:
                return "%s, %s, Room Not Set" % (self.interviewer, self.interviewee)
        else:
            if self.interviewer is None:
                return "No Interviewer, %s, Room %s" % (self.interviewee, self.room)
            elif self.interviewee is None:
                return "%s, No Interviewee, Room %s" % (self.interviewer, self.room)
            else:
                return "%s, %s, Room %s" % (self.interviewer, self.interviewee, self.room)
