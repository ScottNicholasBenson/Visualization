# Generated by Django 3.0.8 on 2021-03-03 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_remove_profile_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='company',
            field=models.CharField(default=0, max_length=255),
        ),
    ]
