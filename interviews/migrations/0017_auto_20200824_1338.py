# Generated by Django 3.0.6 on 2020-08-24 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0016_option_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewee',
            name='previous_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='interviewer',
            name='max_interviews',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
