import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Option, Interviewer, Interviewee, InterviewData
from .management.commands.generate_interview_schedule import generate_interview_data_df
from .management.commands.generate_interview_schedule_second import generate_interview_data_second


def download_interview_date(modeladmin, request, queryset):
    interview_data_df = generate_interview_data_df()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="interviews.csv"'

    writer = csv.writer(response)
    header_row = [
        'Date',
        'Time',
        'Room',
        'Digital Impact',
        'Interviewers',
        'Interviewees'
    ]
    writer.writerow(header_row)

    for row in interview_data_df.values.tolist():
        writer.writerow(row)

    return response


download_interview_date.short_description = "Download SOME interview slots which contain interviewees as a csv"


def download_interview_date_second(modeladmin, request, queryset):
    interview_data_df = generate_interview_data_second()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="interviews.csv"'

    writer = csv.writer(response)
    header_row = [
        'Date',
        'Time',
        'Room',
        'Digital Impact',
        'Interviewers',
        'Interviewees'
    ]
    writer.writerow(header_row)

    for row in interview_data_df.values.tolist():
        writer.writerow(row)

    return response


download_interview_date_second.short_description = "Download ALL interview slots as a csv"


class InterviewDataAdmin(admin.ModelAdmin):
    actions = [download_interview_date, download_interview_date_second]


# Register your models here.
admin.site.register(Option)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(InterviewData, InterviewDataAdmin)
