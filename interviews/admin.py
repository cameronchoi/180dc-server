import csv

from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path

from .models import Option, Interviewer, Interviewee, InterviewData
from .management.commands.generate_interview_schedule import generate_interview_data_df
from .management.commands.generate_interview_schedule_second import generate_interview_data_second
from .management.commands.find_interviewees import find_interviewees_df


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


def download_find_interviewees(modeladmin, request, queryset):
    interview_data_df = find_interviewees_df()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="interviewees.csv"'

    writer = csv.writer(response)
    header_row = [
        'Interviewee',
        'Email'
    ]
    writer.writerow(header_row)

    for row in interview_data_df.values.tolist():
        writer.writerow(row)

    return response


download_find_interviewees.short_description = "Download interviewees who have not selected times yet as csv"


class InterviewDataAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'digital_impact',
                    'current_interviewers', 'current_interviewees', 'room')
    actions = [download_interview_date,
               download_interview_date_second, download_find_interviewees]


class OptionDataAdmin(admin.ModelAdmin):
    list_display = ("description", "option")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle/<str:option>/', self.admin_site.admin_view(self.toggle_option))
        ]
        return custom_urls + urls

    def toggle_option(self, request, **kwargs):
        interviewee_object = Option.objects.get(name=kwargs['option'])
        interviewee_object.option = not interviewee_object.option
        interviewee_object.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(Option, OptionDataAdmin)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(InterviewData, InterviewDataAdmin)
