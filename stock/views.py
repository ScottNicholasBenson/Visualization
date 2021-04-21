
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.contrib import messages

from functions.views import getStaffStatus, getUserCompany, getCompanyList, global_context, getStockInfoObj, \
    requestStock, stockAdjust, saveNotification, getOrderReviewCount, sendRequestOrderEmail, getSingleStockInfo, \
    sendStockEmail, getUserName

from stock.models import StockItems, notifications, orderRequest, Projects, \
     BillOfMaterials,  version


@login_required(login_url='/login/')
def homepage(request):
    if getStaffStatus(request) == 0:
        return HttpResponseRedirect('/stock_in/')
    else:
        return HttpResponseRedirect('/stock_in/')
    # importXML()
    itemsInStock = StockItems.objects.filter(company=getUserCompany(request)).aggregate(Sum('stockAmount'))
    nStock = StockItems.objects.filter(company=getUserCompany(request)).count()
    itemsOutOnDelivery = StockItems.objects.filter(onOrder=True).count()
    tValueStock = StockItems.objects.aggregate(Sum('price'))
    # intN = itemsInStock['stockAmount__sum']
    # floatN = tValueStock['price__sum']
    # totalValueOfStock = intN * floatN/int(nStock)

    context = {'items_in_stock': itemsInStock['stockAmount__sum'],
               'items_on_delivery': itemsOutOnDelivery,
               'active': 'dashboard',
               'PageName': 'Dashboard',
               'orderReviewCount': getOrderReviewCount(request), }

    context['pendingBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                status='pending').count()
    context['version'] = version.objects.all()
    return render(request,
                  'stock/home.html',
                  context)


@login_required(login_url='/login/')
def stock_in(request):
    context = global_context(request)
    companyList = getCompanyList(request)
    stockItems = StockItems.objects.filter(company__in=companyList)
    # First pass from form submit will only contain a stockName
    if request.method == 'POST':
        if 'CreateProject' in request.POST:
            companyList = getCompanyList(request)

            for i in companyList:
                if Projects.objects.filter(company=i, project=request.POST['projectName']).exists():
                    continue
                else:
                    createProject = Projects.objects.create(company=i, project=request.POST['projectName'])
                    return redirect('stock:stock_in')
        else:
            if 'name' in request.POST:
                stockName = request.POST['name']
                stockObj = getStockInfoObj(request)
            else:
                messages.info(request, 'Please Select a Stock Item to search.')
            # Return stock Obj from stockName

            # Second pass will also contain an amount
            newFig = ''
            if 'amount' in request.POST:
                if 'request' in request.POST:
                    requestStock(request)
                else:
                    # Book in stock item
                    if 'stock_out' in request.POST:
                        newFig = stockAdjust(request, stockName, "OUT")
                        # Save notification of item booked
                        if newFig == 'reserved':
                            pass
                        else:
                            saveNotification(request, request.POST['notification'] +
                                             " Booked Out: " +
                                             request.POST['amount'] +
                                             " | New Amount: " +
                                             newFig)
                            messages.success(request, request.POST['notification'] +
                                             " Booked Out: " +
                                             request.POST['amount'])
                    else:
                        newFig = stockAdjust(request, stockName, "IN")
                        # Save notification of item booked
                        saveNotification(request, request.POST['notification'] +
                                         " Booked In: " +
                                         request.POST['amount'] +
                                         " | New Amount: " +
                                         newFig)
                        messages.success(request, request.POST['notification'] +
                                         " Booked In: " +
                                         request.POST['amount'])
                # Retrieve notifications Obj
                context = global_context(request)
                stockObj = getStockInfoObj(request)
                projObj = Projects.objects.filter(company=getUserCompany(request))
                context['stockObj'] = stockObj
                context['projects'] = projObj
                context['stockitems'] = stockItems
                context['active'] = 'stock_in'
                context['PageName'] = 'Stock In'
                return render(request,
                              'stock/stock_in.html', context=context)
            else:
                # First pass form data with no amount
                context = global_context(request)
                stockObj = getStockInfoObj(request)
                projObj = Projects.objects.filter(company=getUserCompany(request))
                context['stockObj'] = stockObj
                context['projects'] = projObj
                context['stockitems'] = stockItems
                context['active'] = 'stock_in'
                context['PageName'] = 'Stock In'

                return render(request,
                              'stock/stock_in.html', context=context)
    # Page load
    context = global_context(request)
    projObj = Projects.objects.filter(company=getUserCompany(request))
    context['projects'] = projObj
    context['stockitems'] = stockItems
    context['active'] = 'stock_in'
    context['PageName'] = 'Stock In/Out'
    return render(request,
                  'stock/stock_in.html', context=context)


@login_required(login_url='/login/')
def search_stock(request):
    stockItems = StockItems.objects.filter(company__in=getCompanyList(request))
    context = global_context(request)
    context['stockitems'] = stockItems
    context['orderReviewCount'] = getOrderReviewCount(request)
    context['active'] = 'search'
    context['PageName'] = 'Search'
    return render(request, 'stock/search.html', context=context)


@login_required(login_url='/login/')
def OrderReview(request):

    context = global_context(request)
    # Check if trigger value higher than stock amount
    orderReview = StockItems.objects.filter(company__in=getCompanyList(request)).filter(
        stockAmount__lte=F('orderTrigger')).filter(onOrder=False).filter(allow_reorder=True).all()
    if request.method == 'POST':
        if 'order' in request.POST:
            sendRequestOrderEmail(orderReview, "Early Order Email", request)
    context = global_context(request)
    context['list'] = orderReview
    context['active'] = 'order_review'
    context['PageName'] = 'Order Review'

    return render(request, 'stock/orderReview.html', context=context)


@login_required(login_url='/login/')
def review_requested_stock(request):
    if getStaffStatus(request) == 0:
        return
    companyList = getCompanyList(request)
    context = global_context(request)
    company = getCompanyList(request)
    reviewList = orderRequest.objects.filter(company__in=company, reviewed=False)
    pastRequestedStock = orderRequest.objects.filter(company__in=company, reviewed=True)
    if request.POST:
        if 'remove' in request.POST:
            removeRequest = orderRequest.objects.get(reason=request.POST['supplier'],
                                                     uniqueStockNumber=request.POST['nameID'], reviewed=False)
            removeRequest.reviewed = True
            removeRequest.status = 'Denied'
            removeRequest.save()
        else:
            stockInfo = getSingleStockInfo(request)
            stockSupplier = stockInfo.supplier
            stockOrderCode = stockInfo.orderCode

        if 'request' in request.POST:
            message = "Item requested for order: " + request.POST['name'] + \
                      '\n' + \
                      'Amount Requested: ' + request.POST['amount'] + ' Order Value: ' + str(
                request.POST['totalOrderValue']) + \
                      '\n' + \
                      'Order from supplier: ' + str(stockSupplier) + ' using OrderCode: ' + stockOrderCode + \
                      '\n' + \
                      'Requested by user: ' + getUserName(request) + '\n ' \
                                                                     'Reason: ' + request.POST['supplier'] + '\n\n'
            sendStockEmail('Requested Order REF: ' + request.POST['orderNumber'], message, request)

            markAsOrdered = orderRequest.objects.get(orderNumber=str(request.POST['orderNumber']))
            markAsOrdered.reviewed = True
            markAsOrdered.status = 'Submitted'
            markAsOrdered.save()
            messages.success(request, 'Order Email sent')
            return HttpResponseRedirect("/review_requested_stock/")
    context = global_context(request)
    context['pastRequestedStock'] = pastRequestedStock
    context['reviewList'] = reviewList
    context['active'] = 'review_requested_stock'
    context['PageName'] = 'Request Review'

    return render(request, 'stock/review_requested_stock.html', context=context)


@login_required(login_url='/login/')
def deliveryBookIn(request):
    deliveryDict = {}
    context = global_context(request)
    itemsOnDelivery = StockItems.objects.filter(company__in=getCompanyList(request),
                                                onOrder=True)
    if 'delivery' in request.POST:
        for key in request.POST:
            if key == 'delivery' or key == 'csrfmiddlewaretoken':
                continue
            if request.POST[key] == '':
                continue
            value = request.POST[key]
            deliveryDict[key] = value
        # Got dictionary to book in
        for item, amount in deliveryDict.items():
            delivery = StockItems.objects.get(uniqueStockNumber=item)
            delivery.stockAmount = delivery.stockAmount + int(amount)
            delivery.onOrder = False
            delivery.save()
            current_user = request.user
            current_user.id
            messages.success(request, 'Items Fully booked in and removed from "ON ORDER" status')
            saveNotification(request, "Booked in " + str(amount) + " " + delivery.name + "'s from delivery")

    if 'partialDelivery' in request.POST:
        for key in request.POST:
            if key == 'partialDelivery' or key == 'csrfmiddlewaretoken':
                continue
            if request.POST[key] == '':
                continue
            value = request.POST[key]
            deliveryDict[key] = value
        # Got dictionary to book in
        for item, amount in deliveryDict.items():
            delivery = StockItems.objects.get(uniqueStockNumber=item)
            delivery.stockAmount = delivery.stockAmount + int(amount)
            delivery.save()
            saveNotification(request, "Partially booked in " + str(amount) + " " + delivery.name + "'s from delivery")
            messages.success(request, 'Items Partially booked in')
    context = global_context(request)
    context['active'] = 'itemsOnDelivery'
    context['PageName'] = 'Book In Delivery'
    context['itemsOnDelivery'] = itemsOnDelivery
    return render(request, 'stock/deliveryBookIn.html', context=context)


def shopfiy_stock_controller():

    return 0

