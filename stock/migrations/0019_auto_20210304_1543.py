# Generated by Django 3.0.8 on 2021-03-04 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0018_orderrequest_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='projects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=225)),
                ('project', models.CharField(max_length=225)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='phone_number',
        ),
    ]
