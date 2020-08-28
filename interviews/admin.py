import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Option, Interviewer, Interviewee, InterviewData
from .management.commands.generate_interview_schedule import generate_interview_data_df


def download_interview_date(modeladmin, request, queryset):
    interview_data_df = generate_interview_data_df()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="interviews.csv"'

    writer = csv.writer(response)
    for row in interview_data_df.values.tolist():
        writer.writerow(row)

    return response


download_interview_date.short_description = "Download all interview slots as a csv"


class InterviewDataAdmin(admin.ModelAdmin):
    actions = [download_interview_date]


# Register your models here.
admin.site.register(Option)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(InterviewData, InterviewDataAdmin)
