# Generated by Django 3.0.6 on 2020-08-06 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0005_auto_20200806_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewdata',
            name='datetime',
            field=models.DateTimeField(),
        ),
    ]