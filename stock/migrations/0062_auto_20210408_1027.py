# Generated by Django 3.0.8 on 2021-04-08 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0061_auto_20210408_1016'),
    ]

    operations = [
        migrations.CreateModel(
            name='company_email_preference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_format', models.CharField(default=0, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='company_email',
            name='email_format',
        ),
    ]
