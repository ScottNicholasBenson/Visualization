# Generated by Django 3.0.8 on 2021-03-31 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='shopify_API',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, default=0, max_length=225, null=True, unique=True)),
                ('API_Key', models.CharField(blank=True, default=0, max_length=225, null=True)),
                ('password', models.CharField(default=0, max_length=255)),
                ('store_name', models.CharField(default=0, max_length=255)),
            ],
        ),
    ]