# Generated by Django 3.0.8 on 2021-03-05 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0019_auto_20210304_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email_schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=225)),
                ('scheduleRun', models.CharField(max_length=225)),
            ],
        ),
    ]
