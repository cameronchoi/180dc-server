# Generated by Django 3.0.6 on 2020-08-06 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0006_auto_20200806_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewdata',
            name='interviewee',
        ),
        migrations.AddField(
            model_name='interviewdata',
            name='interviewee',
            field=models.ManyToManyField(null=True, to='interviews.Interviewee'),
        ),
        migrations.RemoveField(
            model_name='interviewdata',
            name='interviewer',
        ),
        migrations.AddField(
            model_name='interviewdata',
            name='interviewer',
            field=models.ManyToManyField(null=True, to='interviews.Interviewer'),
        ),
    ]