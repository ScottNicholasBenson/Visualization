# Generated by Django 3.0.8 on 2021-03-03 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0016_auto_20210303_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequest',
            name='dateOrdered',
            field=models.DateTimeField(auto_now=True),
        ),
    ]