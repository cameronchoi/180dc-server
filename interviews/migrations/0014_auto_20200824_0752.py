# Generated by Django 3.0.6 on 2020-08-24 07:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0013_auto_20200824_0750'),
    ]

    operations = [
        migrations.RenameField(
            model_name='option',
            old_name='interviewer_closed',
            new_name='closed',
        ),
    ]