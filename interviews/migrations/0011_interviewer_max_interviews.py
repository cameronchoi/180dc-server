# Generated by Django 3.0.6 on 2020-08-22 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0010_auto_20200806_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewer',
            name='max_interviews',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
    ]
