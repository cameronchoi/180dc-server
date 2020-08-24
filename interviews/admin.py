from django.contrib import admin
from .models import Options, Interviewer, Interviewee, InterviewData

# Register your models here.
admin.site.register(Options)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(InterviewData)
