import random
import string

from django.db import models
from django.contrib.auth.models import User
import datetime
import calendar
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, default=0)
    company = models.CharField(max_length=255, default=0)

    def __str__(self):
        return self.company + " - " + self.user.username + ' Profile'

    def create_profile(sender, **kwargs):
        if kwargs['created']:
            user_profile = Profile.objects.create(user=kwargs['instance'])

    post_save.connect(create_profile, sender=User)


class Suppliers(models.Model):
    name = models.CharField(max_length=225, default=0, blank=True, null=True)
    email = models.CharField(max_length=225, default=0, blank=True, null=True)
    company = models.CharField(max_length=255, default=0)

    def __str__(self):
        return self.name


class StockItems(models.Model):
    company = models.CharField(max_length=225, blank=True, null=True)
    name = models.CharField(max_length=225, default=0)
    barCode = models.CharField(max_length=100, default=0, null=True)
    stockAmount = models.IntegerField(default=0)
    price = models.FloatField(default=0.0)
    # Order Details ------------------------------------------------------------
    reOrderAmount = models.IntegerField(null=True, default=0)
    orderCode = models.CharField(max_length=100, default=0, null=True)
    orderTrigger = models.IntegerField(default=0, null=True, blank=True)
    orderTriggerByUser = models.CharField(max_length=225, default=0, null=True)
    itemBookedInByUser = models.CharField(max_length=225, default=0, null=True)
    lastOrdered = models.DateTimeField(default=None, blank=True, null=True)
    onOrder = models.BooleanField(default=False, null=True, blank=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, null=True)
    consignment = models.BooleanField(default=False, null=True, blank=True)
    reserved = models.IntegerField(null=True, default=0)
    uniqueStockNumber = models.CharField(max_length=22500, default=0, null=True)
    shopify_id = models.IntegerField(null=True, default=0)
    allow_reorder = models.BooleanField(default=1)
    def __str__(self):
        return self.name


DAYS = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thrusday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]


class settings(models.Model):
    runOrderDay = models.CharField(
        max_length=2,
        choices=DAYS,
        blank=True,
        null=True)
    runOrderTime = models.TimeField(default=datetime.time(0))
    emailSent = models.BooleanField(blank=True, null=True)
    list(calendar.day_abbr)

    def __str__(self):
        return calendar.day_name[int(self.runOrderDay)]


class OrderEmail(models.Model):
    email = models.CharField(max_length=50, default=0)

    def __str__(self):
        return self.email


class notifications(models.Model):
    company = models.CharField(max_length=225)
    user_id = models.CharField(max_length=225)
    notification = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)


class orderRequest(models.Model):
    orderNumber = models.CharField(max_length=225)
    company = models.CharField(max_length=225)
    user = models.CharField(max_length=225)
    stockName = models.CharField(max_length=255)
    amount = models.IntegerField()
    supplier = models.CharField(max_length=225)
    reviewed = models.BooleanField(default=False)
    dateOrdered = models.DateTimeField(auto_now=True)
    reason = models.CharField(max_length=225)
    orderValue = models.CharField(max_length=225)
    status = models.CharField(max_length=225)
    uniqueStockNumber = models.CharField(max_length=22500, default=0)


class Projects(models.Model):
    company = models.CharField(max_length=225)
    project = models.CharField(max_length=225)


class Email_schedule(models.Model):
    company = models.CharField(max_length=225)
    scheduleRun = models.CharField(max_length=225)


class company_email(models.Model):
    company = models.CharField(max_length=225)
    email = models.CharField(max_length=225)


class company_email_preference(models.Model):
    company = models.CharField(max_length=225)
    email_format = models.CharField(max_length=255, default=0)


class email_formats(models.Model):
    name = models.CharField(max_length=255, default=0)


class consignmentProfiles(models.Model):
    company = models.CharField(max_length=225)
    name = models.CharField(max_length=225)
    details = models.CharField(max_length=5000)


class BillOfMaterials(models.Model):
    company = models.CharField(max_length=225)
    BOMname = models.CharField(max_length=225)
    projectName = models.CharField(max_length=225)
    status = models.CharField(max_length=225)
    bomStock = models.CharField(max_length=50000)


class BOMProjects(models.Model):
    company = models.CharField(max_length=225)
    BOMProject = models.CharField(max_length=225)
    BOMName = models.CharField(max_length=225)
    uniqueBOMNameNumber = models.CharField(max_length=225)
    uniqueBOMProjectNumber = models.CharField(max_length=225)


class dupePOST(models.Model):
    lastToken = models.CharField(max_length=1000)


class version(models.Model):
    version = models.CharField(max_length=225)


class StoreGroupList(models.Model):
    companyGroupList = models.CharField(max_length=225)
    companyGroupName = models.CharField(max_length=225)

    def __str__(self):
        return self.companyGroupName


class shopifyInventory(models.Model):
    inventory_item_id = models.IntegerField(default=0)
    location_id = models.IntegerField(default=0)
    shopifyID = models.IntegerField(default=0)
    title = models.CharField(max_length=225, null=True, blank=True)
    variant_name = models.CharField(max_length=225, null=True, blank=True)
    PID = models.CharField(max_length=225, null=True, blank=True)
    price = models.CharField(max_length=225, null=True, blank=True)
    SKU = models.CharField(max_length=225, null=True, blank=True)
    bardocde = models.CharField(max_length=225, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    old_inventory_quantity = models.IntegerField(default=0)
    stock_io_unique_number = models.CharField(max_length=225, null=True, blank=True)
