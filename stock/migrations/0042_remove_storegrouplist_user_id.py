# Generated by Django 3.0.8 on 2021-03-15 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0041_storegrouplist_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storegrouplist',
            name='User_id',
        ),
    ]
