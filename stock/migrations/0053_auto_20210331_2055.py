# Generated by Django 3.0.8 on 2021-03-31 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0052_shopifyinventory_stock_io_unique_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifyinventory',
            name='stock_io_unique_number',
            field=models.CharField(max_length=225),
        ),
    ]
