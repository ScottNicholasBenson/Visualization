import ast
import random
import string
from datetime import datetime
from random import randint
from time import strftime, gmtime

import pytz
import requests
from django.core.mail import EmailMessage
from django.db.models import F
from django.contrib import messages
from django_common.auth_backends import User
from user_control.models import shopify_API
from stock.models import StockItems, BillOfMaterials, version, Profile, notifications, orderRequest, Suppliers, \
    company_email, StoreGroupList, shopifyInventory, company_email_preference
from user_control.models import shopify_API


def global_context(request):
    """

    :param request: Default Django View
    :return: Dict of global args to pass with view render
    """
    current_user = request.user
    name = Profile.objects.get(user_id=current_user.id)
    notification = getNotificationsObj(request)
    tz = pytz.timezone('Europe/London')
    berlin_now = datetime.now(tz)
    context = {}
    context['time'] = str(berlin_now.strftime("%H:%M"))
    context['shopify_active'] = shopify_API.objects.filter(company__in=getCompanyList(request))
    context['itemsOnDeliveryCount'] = StockItems.objects.filter(company__in=getCompanyList(request),
                                                     onOrder=True).count()
    context['orderReviewCount'] = getOrderReviewCount(request)
    context['approvedBOMCount'] = BillOfMaterials.objects.filter(company__in=getCompanyList(request),
                                                                 status='approved').count()
    context['pendingBOMCount'] = BillOfMaterials.objects.filter(company__in=getCompanyList(request),
                                                                status='pending').count()
    context['review_order_count'] = getRequestedStockAmount(request)
    context['version'] = version.objects.all()
    context['notification'] = notification[0]
    context['notifyAmount'] = notification[1]
    context['currentUser'] = request.user.get_short_name()
    return context


def getStaffStatus(request):
    """
    :param request: Default Django View
    :return: Bool int for testing user level
    """
    current_user = request.user
    userStatus = User.objects.get(id=current_user.id)
    if userStatus.is_staff:
        return 1
    else:
        return 0
    return


def getOrderReviewCount(request):
    """
    :param request:
    :return: Count() of all stock items currently on order
    """
    orderReviewCount = StockItems.objects.filter(company__in=getCompanyList(request)).filter(
        stockAmount__lte=F('orderTrigger')).filter(onOrder=False).filter(allow_reorder=True).all().count()
    return orderReviewCount


def getUserId(request):
    """
    :param request: Default Django View
    :return: Current logged in user ID
    """
    current_user = request.user
    return current_user.id


def getUserName(request):
    """
    :param request: Default Django View
    :return: Currently logged in user's username
    """
    current_user = request.user
    return current_user.username


def getUserCompany(request):
    """
    :param request: Default Django View
    :return: Name of company for currently logged in user
    """
    company = Profile.objects.get(user_id=getUserId(request))
    return company.company


def getNotificationsObj(request):
    """
    :param request: Default Django View
    :return: Object of notifications [0] Number of notifications [1]
    """
    notification = notifications.objects.filter(company__in=getCompanyList(request)).order_by('-id')[:5]
    nCount = int(notifications.objects.filter(company__in=getCompanyList(request)).order_by('-id')[:5].count())
    return notification, nCount


def saveNotification(request, message: str):
    """
    :param request: Default Django View
    :param message: Notification Message to be saved
    :return: NULL
    """
    current_user = request.user
    notify = notifications(user_id=current_user.username,
                           notification=message,
                           created_at=datetime.time(datetime.now()),
                           company=getUserCompany(request))
    notify.save()
    return


def stockAdjust(request, stockName: str, func: str):
    """
    Secondary function checks if stock item is on order, if it is, changes 'OnOrder' value to false
    Checks if stock adjustment returns a negative number
    :param request: Default Django View
    :param stockName: Item to be booked in/out
    :param amount: amount of stock
    :param func: string = 'IN' or 'OUT'
    :return: newFig: Updated stock amount
    """
    newFig = ''
    # Rudimentary test to check if multiple areas under company name
    stock = StockItems.objects.get(uniqueStockNumber=stockName)
    if func == "IN":
        # Check if user linked shopify account
        newFig = stock.stockAmount + int(request.POST['amount'])
        if shopify_API.objects.filter(company=getUserCompany(request)).exists():
            shopify_stock_controller(request, stockName, newFig)
        stock.stockAmount = stock.stockAmount + int(request.POST['amount'])
        if stock.onOrder == 1:
            saveNotification(request, stock.name + " Booked In while Out for order!")
        stock.save()
    if func == "OUT":
        if stock.reserved > int(int(stock.stockAmount - int(request.POST['amount']))):
            messages.error(request, stock.name +
                           ' is reserved, If needed Urgently please request stock against project.')
            return 'reserved'
        else:
            sFigure = stock.stockAmount - int(request.POST['amount'])
            if sFigure < 0:
                saveNotification(request, stock.name + " NEGATIVE STOCK DETECTED")
            newFig = stock.stockAmount - int(request.POST['amount'])
            stock.stockAmount = stock.stockAmount - int(request.POST['amount'])
            stock.save()
    return str(newFig)


def requestStock(request):
    """
    Creates and handles order requests from /stockin
    :param request: Default Django View
    :return:
    """
    range_start = 10 ** (10 - 1)
    range_end = (10 ** 10) - 1
    requestOrderNumber = randint(range_start, range_end)
    if 'supplier' in request.POST:
        pass
    else:
        messages.error(request, 'No Project Selected, Please Add Project to request stock!')
        return 0
    reason = request.POST['supplier']
    stock_name = StockItems.objects.get(uniqueStockNumber=request.POST['name'])
    stockName = stock_name.name
    userCompany = getUserCompany(request)
    amountRequested = request.POST['amount']

    stockRequest = StockItems.objects.get(uniqueStockNumber=request.POST['name'])

    supplier = stockRequest.supplier
    stockPrice = float(stockRequest.price) * float(amountRequested)

    stockSupplierDetails = Suppliers.objects.get(name=supplier,
                                                 company=userCompany)
    if orderRequest.objects.filter(company=userCompany,
                                   user=getUserId(request),
                                   stockName=stockName,
                                   supplier=stockSupplierDetails.name,
                                   reviewed=0,
                                   reason=reason,
                                   uniqueStockNumber=request.POST['name']).exists():
        orderRequestUpdate = orderRequest.objects.get(company=userCompany,
                                                      user=getUserId(request),
                                                      stockName=stockName, supplier=stockSupplierDetails.name,
                                                      reviewed=0,
                                                      reason=reason,
                                                      uniqueStockNumber=request.POST['name'])
        orderRequestUpdate.amount = orderRequestUpdate.amount + int(amountRequested)
        orderRequestUpdate.orderValue = float(orderRequestUpdate.orderValue) + float(stockPrice)
        orderRequestUpdate.save()
        return

    orderSave = orderRequest.objects.create(company=userCompany,
                                            user=getUserId(request),
                                            stockName=stockName,
                                            amount=amountRequested,
                                            supplier=stockSupplierDetails.name,
                                            reviewed=0,
                                            dateOrdered=datetime.now(),
                                            reason=reason,
                                            orderNumber=requestOrderNumber,
                                            orderValue=stockPrice,
                                            uniqueStockNumber=request.POST['name'])
    orderSave.save()
    return


def getRequestedStockAmount(request):
    """
    :param request: Default Django View
    :return: Int of requested stock items for company
    """
    userCompany = getUserCompany(request)
    requestFigure = orderRequest.objects.filter(company__in=getCompanyList(request), reviewed=0).count()
    return requestFigure


def getStockInfoObj(request):
    """
    :param request: POST
    :return: Stock Item Object
    """
    stockObj = ''
    if 'name' in request.POST:
        stockObj = StockItems.objects.get(uniqueStockNumber=request.POST['name'])
    if 'barcode' in request.POST:
        if len(request.POST['barcode']) == 0:
            pass
        else:
            stockObj = StockItems.objects.get(barCode=request.POST['barcode'])
    return stockObj


def getSingleStockInfo(request):
    """
    :param request: request.POST['name']
    :return: A single stock items information
    """
    if 'nameID' in request.POST:
        stockInfo = StockItems.objects.get(uniqueStockNumber=request.POST['nameID'])
        return stockInfo
    else:
        messages.info(request, 'Please enter a valid stock name.')



def generateRandomInt():
    """
    :return: Random Int
    """
    range_start = 10 ** (15 - 1)
    range_end = (10 ** 15) - 1
    UBOMN = randint(range_start, range_end)
    return UBOMN

# def importXML():
#     tree = ET.parse("xml.xml")
#     root = tree.getroot()
#     headers = []
#     count = 0
#     xml_data_to_csv = open('csv.csv', 'w')
#
#     csvWriter = csv.writer(xml_data_to_csv)
#     supplier = []
#     for customer in root.findall('Stock'):
#         data = []
#         export = stockDatabase.stock
#         name = customer.get('Stock_Item')
#         barcode = customer.get('Barcode')
#
#         create = StockItems.objects.create(name=name)
#         create.barCode = barcode
#
#         for detail in customer:
#             if (detail.tag == 'FullAddress'):
#                 for addresspart in detail:
#                     if addresspart.tag == 'OrderDate':
#                         continue
#                     if addresspart.tag == 'OnOrder':
#                         continue
#                     else:
#                         data.append(addresspart.text.rstrip('/n/r'))
#                     if (count == 0):
#                         headers.append(addresspart.tag)
#             else:
#                 if detail.tag == 'OrderDate':
#                     continue
#                 else:
#                     if detail.tag == 'OnOrder':
#                         continue
#                     else:
#                         if detail.text:
#                             data.append(detail.text.rstrip('/n/r'))
#                         if (count == 0):
#                             headers.append(detail.tag)
#         if (count == 0):
#             csvWriter.writerow(headers)
#         csvWriter.writerow(data)
#         count = count + 1
#         counter = 0
#
#         for i in data:
#             if counter == 0:
#                 create.stockAmount = i
#                 counter = counter + 1
#             else:
#                 if counter == 1:
#                     create.orderTrigger = i
#                     counter = counter + 1
#                 else:
#                     if counter == 2:
#                         inst = Suppliers.objects.filter(name=i)
#                         for sup in inst:
#                             create.supplier = sup
#                         counter = counter + 1
#                     else:
#                         if counter == 3:
#                             create.price = i
#                             counter = counter + 1
#                         else:
#                             if counter == 4:
#                                 create.reOrderAmount = i
#                                 counter = counter + 1
#                             else:
#                                 if counter == 5:
#                                     create.orderCode = i
#                                     counter = 0
#                                     create.save()


def sendScheduleStockEmail(subject, message, company):
    """
    :param subject: Subject of Email
    :param message: Message Body
    :param company: User's company
    :return: 'No Email Registered to account' or 'Email Sent'
    """
    if company_email.objects.filter(company=company).exists():
        pass
    else:
        return 'No Email Registered to account'
    recipient = company_email.objects.filter(company=company)
    for email in recipient:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='notification@stockio.co.uk',
            to=[email.email],
            reply_to=['notification@stockio.co.uk'],
            headers={'Content-Type': 'text/plain'},
        )
        email.send()
    return 'Email Sent'


def sendStockEmail(subject, message, request):
    current_user = request.user
    emails = company_email.objects.filter(company=getUserCompany(request))
    emailList = []
    for email in emails:
        emailList.append(email.email)
    recipient = Profile.objects.get(user_id=current_user.id)
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email='notification@stockio.co.uk',
        to=emailList,
        reply_to=['notification@stockio.co.uk'],
        headers={'Content-Type': 'text/plain'},
    )
    email.send()
    return


def sendOrderEmailInventoryProfile(message, subject, company):
    messageBody = []
    for lineItem in message.order_by('supplier_id'):
        tz = pytz.timezone('Europe/London')
        berlin_now = datetime.now(tz)
        lineItem.onOrder = True
        lineItem.lastOrdered = berlin_now.strftime("%Y-%m-%d %H:%M")
        lineItem.save()
        supplierEmail = Suppliers.objects.get(name=lineItem.supplier)
        messageBody.append(str("STOCK ITEM: " + lineItem.name + "\n" + \
                               " SUPPLIER: " + supplierEmail.name  + "\n"+ \
                               " ORDER-CODE: " + lineItem.orderCode  + "\n"+ \
                               " SUPPLIER EMAIL: " + supplierEmail.email + "\n" + \
                               " CURRENT STOCK LEVEL: " + str(lineItem.stockAmount) + "\n"+ \
                               " RE-ORDER AMOUNT: " + str(lineItem.reOrderAmount) + "\n\n\n"))
    if not messageBody:
        return
    item = (["{}".format(x) for x in messageBody])
    html = ' '.join(item)

    # notifications.objects.create()
    return sendScheduleStockEmail(subject, html, company)


def sendOrderEmail(message, subject, company):
    messageBody = []
    email_format = company_email_preference.objects.get(company=company)
    if email_format.email_format == 'Email Per Supplier':
        messageBody = []
        sHold1 = ''
        sHold2 = ''
        loopLen = len(message)
        counter = 0
        for lineItem in message.order_by('supplier_id'):
            sHold1 = lineItem.supplier
            tz = pytz.timezone('Europe/London')
            berlin_now = datetime.now(tz)
            lineItem.onOrder = True
            lineItem.lastOrdered = berlin_now.strftime("%Y-%m-%d %H:%M")
            lineItem.save()
            if Suppliers.objects.filter(name=lineItem.supplier, company=company).exists():
                supplierEmail = Suppliers.objects.get(name=lineItem.supplier, company=company)
            else:
                supplierEmail = ''
            if str(sHold1) != str(sHold2):
                if sHold2 == '':
                    messageBody.append(str("Supplier Contact Details: " + supplierEmail.email + "\n\n\n"))
                    messageBody.append(str("Stock Item: " + lineItem.name +
                                           " | Re-Order Amount: " + str(
                        lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                           "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                           "Price per unit:" + str(lineItem.price) + "\n" + \
                                           "Order Value: " + str(round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2 )) + "\n\n\n"))
                else:
                    if not messageBody:
                        continue
                    item = (["{}".format(x) for x in messageBody])
                    html = ' '.join(item)
                    subject = str(sHold2) + ' Automated Order Email'
                    sendScheduleStockEmail(subject, html, company)
                    messageBody.clear()
                    messageBody.append(str("Supplier Contact Details: " + supplierEmail.email + "\n\n\n"))
                    messageBody.append(str("Stock Item: " + lineItem.name +
                                           " | Re-Order Amount: " + str(
                        lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                           "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                           "Price per unit:" + str(lineItem.price) + "\n" + \
                                           "Order Value: " + str(round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2 )) + "\n\n\n"))
                sHold2 = supplierEmail.name
            else:
                # Second Pass

                messageBody.append(str("Stock Item: " + lineItem.name +
                                       " | Re-Order Amount: " + str(
                    lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                       "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                       "Price per unit:" + str(lineItem.price) + "\n" + \
                                       "Order Value: " + str(round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2 )) + "\n\n\n"))
            sHold2 = supplierEmail.name
            counter += 1
            if counter == loopLen:
                if not messageBody:
                    return
                item = (["{}".format(x) for x in messageBody])
                html = ' '.join(item)
                subject = str(sHold1) + ' Automated Order Email'
                sendScheduleStockEmail(subject, html, company)
                messageBody.clear()
                return
    if email_format.email_format == 'All in One Email':
        gate = 0
        for lineItem in message.order_by('supplier_id'):
            tz = pytz.timezone('Europe/London')
            berlin_now = datetime.now(tz)
            lineItem.onOrder = True
            lineItem.lastOrdered = berlin_now.strftime("%Y-%m-%d %H:%M")
            lineItem.save()
            supplierEmail = Suppliers.objects.get(name=lineItem.supplier)
            if gate == 0:
                messageBody.append(str("Supplier Contact Details: " + supplierEmail.email + "\n\n\n"))
            else:
                messageBody.append(str("Stock Item: " + lineItem.name +
                                       " | Re-Order Amount: " + str(lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                       "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                       "Price per unit:" + str(lineItem.price) + "\n" + \
                                       "Item Order Value: " + str(round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2 )) +  "\n\n\n"))
            gate += 1
        if not messageBody:
            return
        item = (["{}".format(x) for x in messageBody])
        html = ' '.join(item)
        sendScheduleStockEmail(subject, html, company)
    return


def sendRequestOrderEmail(message, subject, request):
    messageBody = []
    email_format = company_email_preference.objects.get(company=getUserCompany(request))
    if email_format.email_format == 'Email Per Supplier':
        messageBody = []
        sHold1 = ''
        sHold2 = ''
        loopLen = len(message)
        counter = 0
        for lineItem in message.order_by('supplier_id'):
            sHold1 = lineItem.supplier
            tz = pytz.timezone('Europe/London')
            berlin_now = datetime.now(tz)
            lineItem.onOrder = True
            lineItem.lastOrdered = berlin_now.strftime("%Y-%m-%d %H:%M")
            lineItem.save()
            if Suppliers.objects.filter(name=lineItem.supplier, company=getUserCompany(request)).exists():
                supplierEmail = Suppliers.objects.get(name=lineItem.supplier, company=getUserCompany(request))
            else:
                supplierEmail = ''
            if str(sHold1) != str(sHold2):
                if sHold2 == '':
                    messageBody.append(str("Supplier Contact Details: " + supplierEmail.email + "\n\n\n"))
                    messageBody.append(str("Stock Item: " + lineItem.name +
                                           " | Re-Order Amount: " + str(
                        lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                           "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                           "Price per unit:" + str(lineItem.price) + "\n" + \
                                           "Order Value: " + str(
                        round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2)) + "\n\n\n"))
                else:
                    if not messageBody:
                        continue
                    item = (["{}".format(x) for x in messageBody])
                    html = ' '.join(item)
                    subject = str(sHold2) + ' Automated Order Email'
                    sendScheduleStockEmail(subject, html, getUserCompany(request))
                    messageBody.clear()
                    messageBody.append(str("Supplier Contact Details: " + supplierEmail.email + "\n\n\n"))
                    messageBody.append(str("Stock Item: " + lineItem.name +
                                           " | Re-Order Amount: " + str(
                        lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                           "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                           "Price per unit:" + str(lineItem.price) + "\n" + \
                                           "Order Value: " + str(
                        round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2)) + "\n\n\n"))
                sHold2 = supplierEmail.name
            else:
                # Second Pass

                messageBody.append(str("Stock Item: " + lineItem.name +
                                       " | Re-Order Amount: " + str(
                    lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                       "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                       "Price per unit:" + str(lineItem.price) + "\n" + \
                                       "Order Value: " + str(
                    round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2)) + "\n\n\n"))
            sHold2 = supplierEmail.name
            counter += 1
            if counter == loopLen:
                if not messageBody:
                    return
                item = (["{}".format(x) for x in messageBody])
                html = ' '.join(item)
                subject = str(sHold1) + ' Automated Order Email'
                sendScheduleStockEmail(subject, html, getUserCompany(request))
                messageBody.clear()
                return
    if email_format.email_format == 'All in One Email':
        gate = 0
        for lineItem in message.order_by('supplier_id'):
            tz = pytz.timezone('Europe/London')
            berlin_now = datetime.now(tz)
            lineItem.onOrder = True
            lineItem.lastOrdered = berlin_now.strftime("%Y-%m-%d %H:%M")
            lineItem.save()
            supplierEmail = Suppliers.objects.get(name=lineItem.supplier)
            if gate == 0:
                messageBody.append(str("Supplier Contact Details: " + supplierEmail.email + "\n\n\n"))
            else:
                messageBody.append(str("Stock Item: " + lineItem.name +
                                       " | Re-Order Amount: " + str(
                    lineItem.reOrderAmount) + " | Order-Code: " + lineItem.orderCode + "\n" + \
                                       "Current Stock Level: " + str(lineItem.stockAmount) + "\n" + \
                                       "Price per unit:" + str(lineItem.price) + "\n" + \
                                       "Item Order Value: " + str(
                    round(float(float(lineItem.reOrderAmount) * float(lineItem.price)), 2)) + "\n\n\n"))
            gate += 1
        if not messageBody:
            return
        item = (["{}".format(x) for x in messageBody])
        html = ' '.join(item)
        sendScheduleStockEmail(subject, html, company)
    return


def generateStockUniqueNumber():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))


def getCompanyList(request):
    companylist = StoreGroupList.objects.get(companyGroupName=getUserCompany(request))
    companyArray = ast.literal_eval(companylist.companyGroupList)
    return companyArray


def shopify_stock_controller(request,uniqueStockNumber,updatedFigure):

    return