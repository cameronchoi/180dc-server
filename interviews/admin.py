from django.contrib import admin
from .models import Option, Interviewer, Interviewee, InterviewData

# Register your models here.
admin.site.register(Option)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(InterviewData)
