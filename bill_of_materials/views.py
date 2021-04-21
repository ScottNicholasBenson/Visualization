import ast

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from functions.views import getStaffStatus, getUserCompany, global_context, getOrderReviewCount, \
    sendRequestOrderEmail, getNotificationsObj, generateRandomInt

from stock.models import StockItems, BillOfMaterials, dupePOST, BOMProjects, version


@login_required(login_url='/login/')
def billOfMaterials(request):
    if getStaffStatus(request) == 0:
        return
    tokenCheck = dupePOST.objects.all()
    context = {}
    BOMDict = {}
    stockObj = StockItems.objects.filter(company=getUserCompany(request))
    BOMObj = BillOfMaterials.objects.filter(company=getUserCompany(request))
    BOMObjList = BillOfMaterials.objects.filter(company=getUserCompany(request)).values('BOMname').distinct()
    if request.POST:
        if dupePOST.objects.filter(lastToken=request.POST['csrfmiddlewaretoken']).exists():
            pass
        else:
            saveToken = dupePOST.objects.create(lastToken=request.POST['csrfmiddlewaretoken'])
            if 'BOMproject' in request.POST:
                if 'delete' in request.POST:
                    delete = BillOfMaterials.objects.get(company=getUserCompany(request),
                                                         BOMname=request.POST['BOMname'],
                                                         projectName=request.POST['BOMproject'])
                    stockSoftLock = delete.bomStock
                    if stockSoftLock:
                        stockDict = ast.literal_eval(stockSoftLock)
                        delete.status = 'Canceled'
                        delete.save()
                        # Remove Soft locked items on delete
                        for stock, requestedAmount in stockDict.items():
                            bookOutBOM = StockItems.objects.get(company=getUserCompany(request), name=stock)
                            if bookOutBOM.reserved > 0:
                                bookOutBOM.reserved = bookOutBOM.reserved - int(requestedAmount)
                                bookOutBOM.save()
                    else:
                        delete.status = 'Canceled'
                        delete.save()
                if 'deleteApproved' in request.POST:
                    delete = BillOfMaterials.objects.get(company=getUserCompany(request),
                                                         BOMname=request.POST['BOMname'],
                                                         projectName=request.POST['BOMproject'])
                    stockSoftLock = delete.bomStock
                    stockDict = ast.literal_eval(stockSoftLock)
                    delete.status = 'Canceled'
                    delete.save()
                    # Remove Soft locked items on delete
                    for stock, requestedAmount in stockDict.items():
                        bookOutBOM = StockItems.objects.get(company=getUserCompany(request), name=stock)
                        returnStock = int(requestedAmount) + bookOutBOM.stockAmount
                        bookOutBOM.stockAmount = returnStock
                        bookOutBOM.save()
                if 'approve' in request.POST:
                    emailBOMBody = []
                    approve = BillOfMaterials.objects.get(company=getUserCompany(request),
                                                          BOMname=request.POST['BOMname'],
                                                          projectName=request.POST['BOMproject'])
                    if approve.status == "approved":
                        pass
                    else:
                        approve.status = "approved"
                        approve.save()
                        stockSoftLock = approve.bomStock
                        stockDict = ast.literal_eval(stockSoftLock)
                        for stock, requestedAmount in stockDict.items():
                            bookOutBOM = StockItems.objects.get(company=getUserCompany(request), name=stock)
                            if int(requestedAmount) > bookOutBOM.stockAmount:
                                emailBOMBody.append(
                                    "Stock Name: " + stock + " Currently in stock: " + str(bookOutBOM.stockAmount) +
                                    " Requested Amount: " + str(int(requestedAmount)) + "\n Price per Unit: " + str(
                                        bookOutBOM.price) +
                                    " Requested Stock Value: " + str(float(requestedAmount) * float(bookOutBOM.price)) +
                                    "\n Supplier: " + str(bookOutBOM.supplier) +
                                    " Order Code: " + str(bookOutBOM.orderCode) + str("\n\n"))
                                bookOutBOM.reserved = int(requestedAmount) - bookOutBOM.reserved
                                bookOutBOM.save()
                            else:
                                # If enough in stock, book out stock items and update reserved amount and stock amount
                                bookOutBOM.stockAmount = int(bookOutBOM.stockAmount) - int(requestedAmount)
                                bookOutBOM.reserved = int(bookOutBOM.reserved) - int(requestedAmount)
                                bookOutBOM.save()

                    if emailBOMBody:
                        str1 = ''.join(emailBOMBody)
                        sendRequestOrderEmail('BOM Stock Request for Project: ' +
                                              request.POST['BOMname'] +
                                              ' - ' +
                                              request.POST['BOMproject'], str1, request)
                if 'pending' in request.POST:
                    approve = BillOfMaterials.objects.get(company=getUserCompany(request),
                                                          BOMname=request.POST['BOMname'],
                                                          projectName=request.POST['BOMproject'])
                    approve.status = "pending"
                    approve.save()
                if 'complete' in request.POST:
                    approve = BillOfMaterials.objects.get(company=getUserCompany(request),
                                                          BOMname=request.POST['BOMname'],
                                                          projectName=request.POST['BOMproject'])
                    approve.status = "complete"
                    approve.save()
                if 'createBOM' in request.POST:
                    if BOMProjects.objects.filter(company=getUserCompany(request),
                                                  BOMName=request.POST['BOMname']).exists():
                        getUBN = BOMProjects.objects.filter(company=getUserCompany(request),
                                                  BOMName=request.POST['BOMname']).first()

                        BOMProjects.objects.create(company=getUserCompany(request),
                                                   BOMName=request.POST['BOMname'],
                                                   BOMProject=request.POST['BOMproject'],
                                                   uniqueBOMNameNumber=getUBN.uniqueBOMNameNumber,
                                                   uniqueBOMProjectNumber=generateRandomInt())

                        BillOfMaterials.objects.create(company=getUserCompany(request),
                                                       BOMname=request.POST['BOMname'],
                                                       projectName=request.POST['BOMproject'],
                                                       status='pending')
                    else:
                        BOMProjects.objects.create(company=getUserCompany(request),
                                                   BOMName=request.POST['BOMname'],
                                                   BOMProject=request.POST['BOMproject'],
                                                   uniqueBOMNameNumber=generateRandomInt(),
                                                   uniqueBOMProjectNumber=generateRandomInt())

                        BillOfMaterials.objects.create(company=getUserCompany(request),
                                                       BOMname=request.POST['BOMname'],
                                                       projectName=request.POST['BOMproject'],
                                                       status='pending')
            if 'createBOMStock' in request.POST:
                for key in request.POST:
                    if key == 'createBOMStock' or key == 'csrfmiddlewaretoken':
                        continue
                    value = str(request.POST[key])
                    if value:
                        BOMDict[key.replace("_amount", "")] = value

                addItemsToBom = BillOfMaterials.objects.get(company=getUserCompany(request),
                                                            projectName=BOMDict['BOMProj'])
                del BOMDict['BOMProj']
                # account for adding same item twice
                for k, v in BOMDict.items():  # BOM project dict
                    softLock = StockItems.objects.get(company=getUserCompany(request), name=k)
                    if softLock.reserved > 0:
                        if softLock.stockAmount > int(v):
                            softLock.reserved = softLock.reserved + int(v)
                            softLock.save()
                    else:
                        if softLock.stockAmount > int(v):
                            softLock.reserved = int(v)
                            softLock.save()

                if addItemsToBom.bomStock:
                    oldBOM = ast.literal_eval(addItemsToBom.bomStock)  # Previous BOM Stock
                    for k, v in oldBOM.items():
                        if k in BOMDict:
                            BOMDict[k] = int(BOMDict[k]) + int(oldBOM[k])
                    newBOM = {**oldBOM, **BOMDict}
                    addItemsToBom.bomStock = newBOM
                else:
                    addItemsToBom.bomStock = BOMDict
                addItemsToBom.save()
    context['active'] = 'BOM'
    context['PageName'] = 'Bill of Materials'
    context['BOMObj'] = BOMObj
    context['BOMObjList'] = BOMObjList
    context['stockObj'] = stockObj
    notification = getNotificationsObj(request)
    context['notification'] = notification[0]
    context['notifyAmount'] = notification[1]
    context['orderReviewCount'] = getOrderReviewCount(request)
    context['pendingBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                status='pending').count()
    context['approvedBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                 status='approved').count()
    context['version'] = version.objects.all()
    return render(request, 'stock/billOfMaterials.html', context=context)


@login_required(login_url='/login/')
def viewBillOfMaterials(request):
    if getStaffStatus(request) == 0:
        return
    context = {}
    BOMreview = BillOfMaterials.objects.filter(company=getUserCompany(request), status='pending')
    context['BOMreview'] = BOMreview
    if 'approve' in request.POST:
        bomString = request.POST['BOM']
        BOM = bomString.split('||||')
        BOMname = BOM[0]
        BOMProj = BOM[1]
        updateBOM = BillOfMaterials.objects.get(company=getUserCompany(request), BOMname=BOMname, projectName=BOMProj)
        updateBOM.status = 'approved'
        updateBOM.save()

    if 'viewBOM' in request.POST:
        BOM = str(request.POST['BOM']).split('||||')
        BOMname = BOM[0]
        BOMProj = BOM[1]

        BOMStock = BillOfMaterials.objects.get(company=getUserCompany(request), BOMname=BOMname, projectName=BOMProj)
        if BOMStock.bomStock:
            stockDict = ast.literal_eval(BOMStock.bomStock)
            stocklist = []
            for key in stockDict:
                stocklist.append(key)
            stockBOM = StockItems.objects.filter(company=getUserCompany(request), name__in=stocklist)
            BOMsum = {}
            BOMsumMinusInStock = {}

            for i in stockBOM:
                BOMAmount = int(stockDict[i.name])
                stockValue = BOMAmount * i.price
                stockValueDecimel = "£%.2f" % round(stockValue, 2)
                if (BOMAmount - i.stockAmount) * i.price < 0:
                    DecimalSum = 0.00
                else:
                    DecimalSum = (BOMAmount - i.stockAmount) * i.price
                stockValueMinusInStock = "£%.2f" % round(DecimalSum, 2)
                BOMsum[i.name] = stockValueDecimel
                BOMsumMinusInStock[i.name] = stockValueMinusInStock

            BOMDict = {}
            row = []
            rowList = {}
            rowList['rows'] = []

            for i in stockBOM:
                row.append(i.name)
                row.append(i.orderCode)
                row.append(i.barCode)
                row.append(i.supplier)
                row.append(int(stockDict[i.name]))
                row.append(i.stockAmount)
                row.append("£%.2f" % round(i.price, 2))
                if int(stockDict[i.name]) - int(i.stockAmount) < 0:
                    row.append(0)
                else:
                    row.append(int(stockDict[i.name]) - int(i.stockAmount))
                row.append(BOMsum[i.name])
                row.append(BOMsumMinusInStock[i.name])  # 1 list

            def split_list(x):
                return [row[i:i + x] for i in range(0, len(row), x)]

            rowList['rows'].append(split_list(10))
            field = {}
            field['headers'] = ['ItemName',
                                'OrderCode',
                                'Barcode',
                                'Supplier',
                                'RequestedAmount',
                                'AmountInStock',
                                'UnitPrice',
                                'Stock Needed',
                                'TotalCost',
                                'TotalCostMinusInStock']
            field['rows'] = rowList['rows']
            context['field'] = field
            context['stockValueMinusInStock'] = BOMsumMinusInStock
            context['BOMDict'] = BOMDict
            context['stockValue'] = BOMsum
            context['stockObj'] = stockBOM
    notification = getNotificationsObj(request)
    context['notification'] = notification[0]
    context['notifyAmount'] = notification[1]
    context['orderReviewCount'] = getOrderReviewCount(request)
    context['pendingBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                status='pending').count()
    context['approvedBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                 status='approved').count()
    context['active'] = 'viewBOM'
    context['PageName'] = 'Pending BOMs'
    context['version'] = version.objects.all()
    return render(request, 'stock/viewBillOfMaterials.html', context=context)


@login_required(login_url='/login/')
def approvedBillOfMaterials(request):
    if getStaffStatus(request) == 0:
        return
    notification = getNotificationsObj(request)
    context = {}
    BOMreview = BillOfMaterials.objects.filter(company=getUserCompany(request), status='approved')
    context['BOMreview'] = BOMreview
    if 'viewBOM' in request.POST:
        BOM = str(request.POST['BOM']).split('||||')
        BOMname = BOM[0]
        BOMProj = BOM[1]

        BOMStock = BillOfMaterials.objects.get(company=getUserCompany(request), BOMname=BOMname, projectName=BOMProj)
        if BOMStock.bomStock:
            stockDict = ast.literal_eval(BOMStock.bomStock)
            stocklist = []
            for key in stockDict:
                stocklist.append(key)
            stockBOM = StockItems.objects.filter(company=getUserCompany(request), name__in=stocklist)
            BOMsum = {}
            BOMsumMinusInStock = {}

            for i in stockBOM:
                BOMAmount = int(stockDict[i.name])
                stockValue = BOMAmount * i.price
                stockValueDecimel = "£%.2f" % round(stockValue, 2)
                if (BOMAmount - i.stockAmount) * i.price < 0:
                    DecimalSum = 0.00
                else:
                    DecimalSum = (BOMAmount - i.stockAmount) * i.price
                stockValueMinusInStock = "£%.2f" % round(DecimalSum, 2)
                BOMsum[i.name] = stockValueDecimel
                BOMsumMinusInStock[i.name] = stockValueMinusInStock

            BOMDict = {}
            row = []
            rowList = {}
            rowList['rows'] = []

            for i in stockBOM:
                row.append(i.name)
                row.append(i.orderCode)
                row.append(i.barCode)
                row.append(i.supplier)
                row.append(int(stockDict[i.name]))
                row.append(i.stockAmount)
                row.append("£%.2f" % round(i.price, 2))
                if int(stockDict[i.name]) - int(i.stockAmount) < 0:
                    row.append(0)
                else:
                    row.append(int(stockDict[i.name]) - int(i.stockAmount))
                row.append(BOMsum[i.name])
                row.append(BOMsumMinusInStock[i.name])  # 1 list

            def split_list(x):
                return [row[i:i + x] for i in range(0, len(row), x)]

            rowList['rows'].append(split_list(10))
            field = {}
            field['headers'] = ['ItemName',
                                'OrderCode',
                                'Barcode',
                                'Supplier',
                                'RequestedAmount',
                                'AmountInStock',
                                'UnitPrice',
                                'Stock Needed',
                                'TotalCost',
                                'TotalCostMinusInStock']
            field['rows'] = rowList['rows']
            context['field'] = field
            context['stockValueMinusInStock'] = BOMsumMinusInStock
            context['BOMDict'] = BOMDict
            context['stockValue'] = BOMsum
            context['stockObj'] = stockBOM
    context = global_context(request)
    context['active'] = 'approvedBOM'
    context['PageName'] = 'Approved BOMs'
    return render(request, 'stock/viewApprovedBillOfMaterials.html', context=context)
