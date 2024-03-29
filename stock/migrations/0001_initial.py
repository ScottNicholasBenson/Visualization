# Generated by Django 3.0.8 on 2020-08-07 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=200)),
                ('barcode', models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='supplier_details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier_name', models.CharField(max_length=200)),
                ('supplier_email', models.EmailField(max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='item_status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('on_order', models.BooleanField(null=True)),
                ('order_date', models.DateField(null=True)),
                ('last_order_date', models.DateField(null=True)),
                ('item_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stock.stock')),
            ],
        ),
    ]
