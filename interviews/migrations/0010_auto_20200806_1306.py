# Generated by Django 3.0.6 on 2020-08-06 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0009_auto_20200806_1259'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interviewdata',
            old_name='interviewer',
            new_name='interviewers',
        ),
        migrations.RemoveField(
            model_name='interviewdata',
            name='interviewee',
        ),
        migrations.AddField(
            model_name='interviewdata',
            name='interviewees',
            field=models.ManyToManyField(blank=True, to='interviews.Interviewee'),
        ),
    ]
