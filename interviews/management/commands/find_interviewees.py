import pandas as pd
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from interviews.models import InterviewData, Interviewee


def find_interviewees_df():
    # create dataframe
    df = pd.DataFrame(columns=[
        'Interviewee',
        'Email',
    ])

    print('please tell me it comes here')
    for interviewee_data in Interviewee.objects.all():
        interview_data = InterviewData.objects.filter(
            interviewees=interviewee_data)
        if(len(interview_data) == 0):
            df = df.append(
                {
                    'Interviewee': "{} {}".format(
                        interviewee_data.user.first_name, interviewee_data.user.last_name),
                    'Email': interviewee_data.user.email,
                },
                ignore_index=True)

    return df


class Command(BaseCommand):
    help = "generates current interview schedule"

    def handle(self, *args, **options):
        interview_data_df = find_interviewees_df()

        # finally output to csv
        output_file = os.path.join(
            settings.BASE_DIR, "interviews/csv-files/interviews.csv")
        interview_data_df.to_csv(output_file, index=False)

        self.stdout.write("success!")
