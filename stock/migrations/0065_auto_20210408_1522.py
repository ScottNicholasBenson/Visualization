# Generated by Django 3.0.8 on 2021-04-08 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0064_email_formats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliers',
            name='name',
            field=models.CharField(blank=True, default=0, max_length=225, null=True),
        ),
    ]