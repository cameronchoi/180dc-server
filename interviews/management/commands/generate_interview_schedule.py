import pandas as pd
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from interviews.models import Interviewer, Interviewee, InterviewData


class Command(BaseCommand):
    help = "generates current interview schedule"

    def handle(self, *args, **options):
        # create dataframe
        interview_data_df = pd.DataFrame(columns=[
            'Date',
            'Time',
            'Room',
            'Digital Impact',
            'Interviewers',
            'Interviewees'
        ])

        # iterate thru db to process interviews
        for interview_data in InterviewData.objects.all():
            # generate interviewee list (of their full names)
            interviewees = []
            for interviewee in interview_data.interviewees.all():
                full_name = "{} {}".format(interviewee.user.first_name, interviewee.user.last_name)
                interviewees.append(full_name)

            # generate interviewer list (of their full names)
            interviewers = []
            for interviewer in interview_data.interviewers.all():
                full_name = "{} {}".format(interviewer.user.first_name, interviewer.user.last_name)
                interviewers.append(full_name)

            # append to the dataframe
            # we don't need to check for unique
            # because that constraint is assumed to be true on a db level
            interview_data_df = interview_data_df.append(
                {
                    'Date': interview_data.datetime.date(),
                    'Time': interview_data.datetime.time(),
                    'Room': interview_data.room,
                    'Digital Impact': interview_data.digital_impact,
                    'Interviewers': (interviewers if interviewers else None),
                    'Interviewees': (interviewees if interviewees else None)
                },
                ignore_index=True)

            # finally output to csv
            output_file = os.path.join(
                settings.BASE_DIR, "interviews/csv-files/interviews.csv")
            interview_data_df.to_csv(output_file, index=False)

        self.stdout.write("success!")
