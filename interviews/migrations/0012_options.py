# Generated by Django 3.0.6 on 2020-08-22 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0011_interviewer_max_interviews'),
    ]

    operations = [
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interviewer_closed', models.BooleanField(default=False)),
            ],
        ),
    ]
