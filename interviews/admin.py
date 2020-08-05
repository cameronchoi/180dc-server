from django.contrib import admin
from .models import PersonalInfo, Interviewer, Interviewee, InterviewSlot, InterviewData

# Register your models here.
admin.site.register(PersonalInfo)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(InterviewSlot)
admin.site.register(InterviewData)
