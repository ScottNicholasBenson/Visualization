# Generated by Django 3.0.8 on 2021-03-03 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0014_orderrequest_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequest',
            name='reviewed',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]