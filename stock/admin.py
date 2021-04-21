from django.contrib import admin
from .models import Suppliers, StockItems, settings, OrderEmail, company_email, version, StoreGroupList, \
    company_email_preference
from .models import Profile

admin.site.site_header = 'Stock-IO Control Panel'
admin.site.site_title = "Stock-IO"
admin.site.index_title = "Stock-IO Portal"


class stockInfo(admin.ModelAdmin):
    list_display = ('name', 'barCode', 'stockAmount', 'price', 'supplier')
    search_fields = ('name', 'barCode')


class orderInfo(admin.ModelAdmin):
    list_display = ('runOrderDay', 'runOrderTime', 'emailSent')


# Register your models here
admin.site.register(Profile)
admin.site.register(company_email_preference)
admin.site.register(OrderEmail)
admin.site.register(settings, orderInfo)
admin.site.register(Suppliers)
admin.site.register(StoreGroupList)
admin.site.register(StockItems, stockInfo)
admin.site.register(company_email)
admin.site.register(version)
