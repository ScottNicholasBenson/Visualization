# Generated by Django 3.0.8 on 2021-03-02 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_auto_20210302_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]