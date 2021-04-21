import json
from datetime import date
from time import strftime, gmtime
from django.db.models import F
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from functions.views import global_context, getUserCompany, generateStockUniqueNumber, sendOrderEmail
from stock.models import shopifyInventory, StockItems, Email_schedule
from user_control.models import shopify_API


def auto_import():
    active_companies = shopify_API.objects.values_list('company', flat=True)
    for company in active_companies:
        shopify_info = shopify_API.objects.get(company=company)
        # PARAMS = {
        #     'since_id': 0
        # }
        # r = requests.get(
        #     url='https://' + shopify_info.API_Key + ':' + shopify_info.password + '@' + shopify_info.store_name + '/admin/api/2021-01/products.json',
        #     params=PARAMS)
        # data = r.json()
        PARAMS = {
            'since_id': 0
        }
        r = requests.get(url='https://' + shopify_info.API_Key + ':' +
                             shopify_info.password + '@' + shopify_info.store_name +
                             '/admin/api/2021-04/locations.json')
        data = r.json()

        list = []
        for i in data['locations']:
            list.append(i['id'])
        # cleanUp = shopifyInventory.objects.values('title').exclude(location_id__in=list)
        # StockItems.objects.exclude(name__in=cleanUp).delete()
        for id in list:
            r = requests.get(url='https://' + shopify_info.API_Key + ':' +
                                 shopify_info.password + '@' + shopify_info.store_name +
                                 '/admin/api/2021-04/inventory_levels.json?location_ids=' + str(id))
            data = r.json()
            for i in data['inventory_levels']:
                if shopifyInventory.objects.filter(inventory_item_id=i['inventory_item_id'],
                                                   location_id=i['location_id']).exists():
                    pass
                else:
                    create = shopifyInventory.objects.create(inventory_item_id=i['inventory_item_id'],
                                                             location_id=i['location_id'])

        r = requests.get(url='https://' + shopify_info.API_Key + ':' +
                             shopify_info.password + '@' + shopify_info.store_name +
                             '/admin/api/2021-04/products.json')
        data = r.json()
        for i in data['products']:
            for o in i['variants']:
                UN = generateStockUniqueNumber()
                create = shopifyInventory.objects.get(inventory_item_id=o['inventory_item_id'])
                if o['title'] == 'Default Title':
                    create.title = i['title']
                    if StockItems.objects.filter(uniqueStockNumber=create.stock_io_unique_number).exists():
                        update = StockItems.objects.get(uniqueStockNumber=create.stock_io_unique_number)
                        update.name = i['title']
                        update.barCode = o['barcode']
                        update.price = o['price']
                        update.stockAmount = o['inventory_quantity']
                        update.orderTrigger = 0
                        update.company = company
                        update.uniqueStockNumber = UN
                        update.save()
                    else:
                        stockio_create = StockItems.objects.create(name=i['title'],
                                                                   barCode=o['barcode'],
                                                                   price=o['price'],
                                                                   stockAmount=o['inventory_quantity'],
                                                                   orderTrigger=0,
                                                                   company=company,
                                                                   uniqueStockNumber=UN)

                else:
                    if StockItems.objects.filter(uniqueStockNumber=create.stock_io_unique_number).exists():
                        update = StockItems.objects.get(uniqueStockNumber=create.stock_io_unique_number)
                        update.name = i['title']
                        update.barCode = o['barcode']
                        update.price = o['price']
                        update.stockAmount = o['inventory_quantity']
                        update.orderTrigger = 0
                        update.company = company
                        update.uniqueStockNumber = UN
                        update.save()
                    else:
                        create.title = i['title'] + " : " + o['title']
                        stockio_create = StockItems.objects.create(name=i['title'] + " : " + o['title'],
                                                                   barCode=o['barcode'],
                                                                   price=o['price'],
                                                                   stockAmount=o['inventory_quantity'],
                                                                   orderTrigger=0,
                                                                   company=company,
                                                                   uniqueStockNumber=UN)
                create.price = o['price']
                create.bardocde = o['barcode']
                create.inventory_quantity = o['inventory_quantity']
                create.old_inventory_quantity = o['old_inventory_quantity']
                create.stock_io_unique_number = UN
                create.SKU = o['sku']
                create.save()

                # shopifyInventory.objects.create(inventory_item_id=i['inventory_item_id'], location_id=i['location_id'])
        shopify_list = []
        # migrate_shopify = shopifyInventory.objects
        # for products in data:
        #     for i in data[products]:
        #         UN = generateStockUniqueNumber()
        #         for o in i['variants']:
        #             if migrate_shopify.filter(SID=o['id']).exists():
        #                 continue
        #             migrate_shopify.create(SID=o['id'],
        #                                    PID=o['product_id'],
        #                                    title=i['title'],
        #                                    price=o['price'],
        #                                    SKU=o['sku'],
        #                                    bardocde=o['barcode'],
        #                                    inventory_id=o['id'],
        #                                    inventory_quantity=o['inventory_quantity'],
        #                                    old_inventory_quantity=o['old_inventory_quantity'],
        #                                    stock_io_unique_number=UN)
        #
        #             StockItems.objects.create(name=i['title'].upper(),
        #                                       barCode=o['barcode'],
        #                                       stockAmount=o['inventory_quantity'],
        #                                       orderTrigger=0,
        #                                       price=float(o['price']),
        #                                       reOrderAmount=0,
        #                                       supplier_id=None,
        #                                       orderCode=0,
        #                                       company=company,
        #                                       uniqueStockNumber=UN
        #                                       )


@login_required(login_url='/login/')
def manage(request):
    context = global_context(request)
    context['active'] = 'shopify'
    if 'shopify_stock' in request.POST:
        auto_import()

    return render(request, 'stock/shopify.html', context)
