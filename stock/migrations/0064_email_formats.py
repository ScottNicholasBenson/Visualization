# Generated by Django 3.0.8 on 2021-04-08 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0063_company_email_preference_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='email_formats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=0, max_length=255)),
            ],
        ),
    ]
