# Generated by Django 3.0.8 on 2021-03-15 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0044_auto_20210315_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequest',
            name='uniqueStockNumber',
            field=models.CharField(default=0, max_length=22500),
        ),
    ]