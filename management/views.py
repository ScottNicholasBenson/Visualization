import re
from datetime import datetime, time, timezone, date
from time import strftime, gmtime

import pytz
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from functions.views import getStaffStatus, getUserCompany, getCompanyList, global_context, generateStockUniqueNumber, \
    saveNotification, getSingleStockInfo, sendOrderEmail
from stock.models import Suppliers, Projects, StockItems, Email_schedule, company_email_preference, email_formats


@login_required(login_url='/login/')
def inventoryManagement(request):
    if getStaffStatus(request) == 0:
        return
    print(request.POST)
    company = getCompanyList(request)
    suppliers = Suppliers.objects.filter(company__in=company)
    email_format = email_formats.objects.all()
    emailFormat = company_email_preference.objects.get(company=getUserCompany(request))
    projects = Projects.objects.filter(company__in=company)
    allStockitems = StockItems.objects.filter(company__in=company)
    emailSchedules = Email_schedule.objects.filter(company__in=company)
    context = global_context(request)
    if 'Delete' in request.POST:
        StockItems.objects.get(uniqueStockNumber=request.POST['nameUpdate']).delete()
        saveNotification(request, request.POST['name'] + " deleted")
    if 'SaveMethod' in request.POST:
        update = company_email_preference.objects.get(company=getUserCompany(request))
        saveNotification(request, " Email Format changed to " + request.POST['format'])
        update.email_format = request.POST['format']
        update.save()
        messages.success(request, 'Email format Updated!')
        return redirect('stock:inventoryManagement')
    if 'Create' in request.POST:
        supplier = Suppliers.objects.get(name=request.POST['supplier'], company=getUserCompany(request))
        if str(request.POST['amount']).isnumeric():
            if str(request.POST['triggerAmount']).isnumeric():
                if str(request.POST['reOrderAmount']).isnumeric():
                    upperName = str(request.POST['name']).upper()
                    if StockItems.objects.filter(name=upperName, company=getUserCompany(request)).exists():
                        messages.info(request, "An Item with this name already exists, please use another.")
                        context['errorName'] = 'CHANGE THIS VALUE'
                        context['errorBarcode'] = request.POST['barcode']
                        context['errorAmount'] = request.POST['amount']
                        context['errorTrigger'] = request.POST['triggerAmount']
                        context['errorPrice'] = request.POST['price']
                        context['errorReorder'] = request.POST['reOrderAmount']
                        context['errorSupplier'] = request.POST['supplier']
                        context['errorOrderCode'] = request.POST['supplierOrderCode']
                    else:
                        if '£' in request.POST['price']:
                            price = str(request.POST['price']).replace('£','').replace(',','')
                        if 'auto' in request.POST:
                            create = StockItems.objects.create(name=str(request.POST['name']).upper(),
                                                               barCode=request.POST['barcode'],
                                                               stockAmount=request.POST['amount'],
                                                               orderTrigger=request.POST['triggerAmount'],
                                                               price=float(price),
                                                               reOrderAmount=request.POST['reOrderAmount'],
                                                               supplier_id=supplier.id,
                                                               orderCode=request.POST['supplierOrderCode'],
                                                               company=getUserCompany(request),
                                                               uniqueStockNumber=generateStockUniqueNumber(),
                                                               allow_reorder=True
                                                               )
                        else:
                            create = StockItems.objects.create(name=str(request.POST['name']).upper(),
                                                               barCode=request.POST['barcode'],
                                                               stockAmount=request.POST['amount'],
                                                               orderTrigger=request.POST['triggerAmount'],
                                                               price=float(price),
                                                               reOrderAmount=request.POST['reOrderAmount'],
                                                               supplier_id=supplier.id,
                                                               orderCode=request.POST['supplierOrderCode'],
                                                               company=getUserCompany(request),
                                                               uniqueStockNumber=generateStockUniqueNumber(),
                                                               allow_reorder=False
                                                               )
                        create.save()
                        saveNotification(request, 'New Item Created:' + request.POST['name'])
                else:
                    messages.error(request, "ReOrderAmount must be a Number...")
            else:
                messages.error(request, "Trigger Amount must be a Number...")
        else:
            messages.error(request, "Initial Stock Amount must be a Number...")
    if 'Retrieve' in request.POST:
        # Gets a list of all stock for currently logged in user
        stockInfo = StockItems.objects.get(uniqueStockNumber=request.POST['nameID'])
        context['auto'] = stockInfo.allow_reorder
        context['projects'] = projects
        context['stockDetails'] = stockInfo
        context['PageName'] = 'Management'
        context['suppliers'] = suppliers
        context['emailSchedules'] = emailSchedules
        context['allStockitems'] = allStockitems
        context['active'] = 'inventoryManagement'

        return render(request, 'stock/inventoryManagement.html', context=context)
    if 'Update' in request.POST:
        supplier = Suppliers.objects.get(company=getUserCompany(request), name=request.POST['supplier'])
        stockItem = StockItems.objects.get(uniqueStockNumber=request.POST['nameUpdate'])
        stockItem.name = request.POST['name']
        stockItem.barCode = request.POST['barcode']
        stockItem.stockAmount = request.POST['amount']
        stockItem.orderTrigger = request.POST['triggerAmount']
        stockItem.price = request.POST['price']
        stockItem.reOrderAmount = request.POST['reOrderAmount']
        stockItem.supplier_id = supplier.id
        stockItem.orderCode = request.POST['supplierOrderCode']
        if 'auto' in request.POST:
            stockItem.allow_reorder = True
        else:
            stockItem.allow_reorder = False
        stockItem.save()
        saveNotification(request, request.POST['name'] + "Stock details updated")
    if 'DeleteProject' in request.POST:
        Projects.objects.filter(company=request.POST['projectCompany'], project=request.POST['projectName']).delete()
        messages.info(request, "Deleted - PROJECT: " + request.POST['projectName'])
        return HttpResponseRedirect("/inventoryManagement/")
    if 'CreateProject' in request.POST:
        companyList = getCompanyList(request)

        for i in companyList:
            if Projects.objects.filter(company=i, project=request.POST['projectName']).exists():
                continue
            else:
                createProject = Projects.objects.create(company=i, project=request.POST['projectName'])
        createProject.save()
    if 'SaveSchedule' in request.POST:
        dateSave = str(request.POST['day']) + "@" + str(request.POST['time'])
        count = Email_schedule.objects.filter(scheduleRun=dateSave, company=company).count()
        if count == 1:
            messages.error(request, 'Schedule already exists!')
        else:
            Email_schedule.objects.create(company=getUserCompany(request), scheduleRun=dateSave)
    if 'DeleteSchedule' in request.POST:
        Email_schedule.objects.get(company__in=company, scheduleRun=request.POST['scheduleRun']).delete()
    if 'DeleteSupplier' in request.POST:
        Suppliers.objects.get(company=getUserCompany(request), name=request.POST['supplierName']).delete()
    if 'CreateSupplier' in request.POST:
        if 'supplierContact' in request.POST:
            if len(request.POST['supplierContact']) == 0:
                if Suppliers.objects.filter(company=getUserCompany(request), name=request.POST['supplierName']).exists():
                    messages.error(request, "Supplier already exists")
                else:
                    Suppliers.objects.create(company=getUserCompany(request), name=request.POST['supplierName'],
                                         email='Not Supplied')
            else:
                if Suppliers.objects.filter(company=getUserCompany(request), name=request.POST['supplierName']).exists():
                    messages.error(request, "Supplier already exists")
                else:
                    Suppliers.objects.create(company=getUserCompany(request), name=request.POST['supplierName'],
                                             email=request.POST['supplierContact'])

    context['email_format'] = email_format
    context['emailFormat'] = emailFormat
    context['projects'] = projects
    context['PageName'] = 'Management'
    context['suppliers'] = suppliers
    context['emailSchedules'] = emailSchedules
    context['allStockitems'] = allStockitems
    context['active'] = 'inventoryManagement'
    return render(request, 'stock/inventoryManagement.html', context=context)

def timed_job():
    # auto_import()
    email = Email_schedule.objects.all()
    dayDic = {'Monday': 0,
              'Tuesday': 1,
              'Wednesday': 2,
              'Thursday': 3,
              'Friday': 4,
              'Saturday': 5,
              'Sunday': 6
              }
    tz = pytz.timezone('Europe/London')
    berlin_now = datetime.now(tz)
    for entry in email:
        stockToOrder = StockItems.objects.filter(company=entry.company, stockAmount__lte=F('orderTrigger'), onOrder=0)
        if date.today().weekday() == dayDic.get(entry.scheduleRun.split('@')[0]):
            if str(berlin_now.strftime("%H:%M")) == str(entry.scheduleRun.split('@')[1]):
                sendOrderEmail(stockToOrder, "Stock To Order", entry.company)