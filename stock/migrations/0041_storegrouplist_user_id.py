# Generated by Django 3.0.8 on 2021-03-15 08:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stock', '0040_remove_storegrouplist_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='storegrouplist',
            name='User_id',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
