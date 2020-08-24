import random
import string
import pandas as pd
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from interviews.models import Interviewer, Interviewee


# generate a password of length x, alphanumeric
def generate_password(length):
    password_valid = False
    password = ''
    while not password_valid:
        valid_characters = string.ascii_letters + string.digits
        password = password.join(random.choice(valid_characters)
                                 for char in range(length))
        if any(char.isdigit() for char in password):
            if any(char.isalpha() for char in password):
                password_valid = True
            else:
                password = ''
        else:
            password = ''
    return password


class Command(BaseCommand):
    help = "generates passwords and users"

    def handle(self, *args, **options):
        # get df and add new password column
        input_file = os.path.join(
            settings.BASE_DIR, "interviews/csv-files/list.csv")
        candidates = pd.read_csv(input_file)
        candidates['Password'] = ''

        # iterate over df and assign passwords
        for index in candidates.index:
            candidates.at[index, 'Password'] = generate_password(12)

        # now spit out to new csv
        output_file = os.path.join(
            settings.BASE_DIR, "interviews/csv-files/password-list.csv")
        candidates.to_csv(output_file, index=False)

        # now create objects in database
        # for now, skip if username already exists
        for index, row in candidates.iterrows():
            try:
                user = User.objects.get(username=row['Email'])
                user.set_password(row['Password'])
                user.save()
            except User.DoesNotExist:
                # create User objects
                user = User.objects.create_user(
                    row['Email'].lower(), row['Email'], row['Password'])
                user.first_name = row['First Name']
                user.last_name = row['Last Name']

                if row['Admin Status'] == 'Admin':
                    user.is_staff = True
                else:
                    user.is_staff = False

                user.save()

                # now create interviewer/interviewee objects
                if row['Assignment'] == "Interviewer":
                    interviewer = Interviewer.objects.create(
                        user=user,
                        digital_impact=(
                            True if row['Stream'] == "DI" else False)
                    )
                    interviewer.save()
                else:
                    interviewee = Interviewee.objects.create(
                        user=user,
                        digital_impact=(
                            True if row['Stream'] == "DI" else False)
                    )
                    interviewee.save()

        self.stdout.write("success!")
