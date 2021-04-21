from django.db import models


class shopify_API(models.Model):
    user_id = models.CharField(unique=True, max_length=225, default=0, blank=True, null=True)
    company = models.CharField(max_length=225, default=0, blank=True, null=True)
    API_Key = models.CharField(max_length=225, default=0, blank=True, null=True)
    password = models.CharField(max_length=255, default=0)
    store_name = models.CharField(max_length=255, default=0)

    def __str__(self):
        return self.store_name


# Create your models here.
