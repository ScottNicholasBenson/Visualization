# Generated by Django 3.0.8 on 2021-03-07 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0022_auto_20210307_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockitems',
            name='consignment',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
