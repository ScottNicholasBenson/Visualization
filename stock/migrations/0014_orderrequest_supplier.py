# Generated by Django 3.0.8 on 2021-03-03 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0013_orderrequest_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequest',
            name='supplier',
            field=models.CharField(default=0, max_length=225),
            preserve_default=False,
        ),
    ]
