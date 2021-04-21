import ast

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.contrib import messages

from functions.views import getStaffStatus, getUserCompany, getCompanyList, global_context, getOrderReviewCount, \
    getNotificationsObj, getRequestedStockAmount, sendOrderEmail

from stock.models import StockItems, consignmentProfiles, BillOfMaterials, version


@login_required(login_url='/login/')
def consignmentView(request):
    if getStaffStatus(request) == 0:
        return
    consignObj = consignmentProfiles.objects.filter(company=getUserCompany(request))
    notification = getNotificationsObj(request)
    context = {}
    consignDict = {}
    context = global_context(request)
    if 'delete' in request.POST:
        if consignmentProfiles.objects.filter(company=getUserCompany(request),
                                              name=request.POST['profile']).exists():
            consignmentProfiles.objects.get(company=getUserCompany(request),
                                            name=request.POST['profile']).delete()
            messages.success(request, request.POST['profile'] + ' deleted!')
        else:
            messages.error(request, 'Inventory Profile ' + request.POST['profile'] + ' doesn\'t exist')

    if 'Create' in request.POST:
        profileName = request.POST['profile']
        if consignmentProfiles.objects.filter(company=getUserCompany(request),
                                              name=profileName, ).exists():
            messages.info(request, 'Tried creating a profile that already exists!')
        else:
            createProfile = consignmentProfiles.objects.create(company=getUserCompany(request),
                                                               name=profileName,
                                                               )
            createProfile.save()
        context['consignmentProfile'] = request.POST['profile']
        context['name'] = request.POST['profile']

    if 'Send Consignment Email' in request.POST:
        if consignmentProfiles.objects.filter(company=getUserCompany(request), name=request.POST['profile']).exists():
            consignmentObj = consignmentProfiles.objects.get(company=getUserCompany(request),
                                                             name=request.POST['profile'])
            if consignmentObj.details == '':
                messages.info(request, "Cannot Email empty Inventory profile, think of the trees!")
            else:
                consignDict = ast.literal_eval(consignmentObj.details)
                consignmentList = list(consignDict.keys())
                consignmentStockObj = StockItems.objects.filter(company=getUserCompany(request),
                                                                name__in=consignmentList)
                sendOrderEmail(consignmentStockObj, "Consignment Email Profile: " + request.POST['profile'],
                               getUserCompany(request))
                messages.success(request, 'Email Sent!')
        else:
            messages.error(request, request.POST['profile'] + ' doesn\'t exist!')

    if 'consignment' in request.POST:
        for key in request.POST:
            if key == 'consignmentProfile' or key == 'consignment' or key == 'csrfmiddlewaretoken':
                continue
            value = request.POST[key]
            consignDict[key] = value
        if consignmentProfiles.objects.filter(company=getUserCompany(request),
                                              name=request.POST['consignmentProfile']).exists():
            saveConsignment = consignmentProfiles.objects.get(company=getUserCompany(request),
                                                              name=request.POST['consignmentProfile'])
            saveConsignment.details = consignDict
            saveConsignment.save()
            consignmentObj = consignmentProfiles.objects.get(company=getUserCompany(request),
                                                             name=request.POST['consignmentProfile'])
            consignDict = ast.literal_eval(consignmentObj.details)
            consignmentList = list(consignDict.keys())
            consignmentStockObj = StockItems.objects.filter(company=getUserCompany(request), name__in=consignmentList)
            context['consignmentStockObj'] = consignmentStockObj
            context['consignmentProfile'] = request.POST['consignmentProfile']
            context['name'] = request.POST['consignmentProfile']
        else:
            saveConsignment = consignmentProfiles.objects.create(company=getUserCompany(request),
                                                                 name=request.POST['consignmentProfile'])
            saveConsignment.details = consignDict
            saveConsignment.save()

    if 'viewConsignment' in request.POST:
        if consignmentProfiles.objects.filter(company=getUserCompany(request), name=request.POST['profile']).exists():
            consignmentObj = consignmentProfiles.objects.get(company=getUserCompany(request),
                                                             name=request.POST['profile'])
            if consignmentObj.details == "":
                context['consignmentStockObj'] = ''
                context['consignmentProfile'] = request.POST['profile']

            else:
                consignDict = ast.literal_eval(consignmentObj.details)
                consignmentList = list(consignDict.keys())
                consignmentStockObj = StockItems.objects.filter(company__in=getCompanyList(request),
                                                                name__in=consignmentList)
                context['consignmentStockObj'] = consignmentStockObj
                context['consignmentProfile'] = request.POST['profile']
        else:
            if 'delete' in request.POST:
                messages.info(request, "Stock Profile " + request.POST['profile'] + " deleted..")
            else:
                messages.error(request, "Stock Profile " + request.POST['profile'] + " doesn't exist.")
        context['name'] = request.POST['profile']

    context['consignObj'] = consignObj
    context['orderReviewCount'] = getOrderReviewCount(request)
    context['review_order_count'] = getRequestedStockAmount(request)
    context['active'] = 'consignmentView'
    context['PageName'] = 'Inventory Profiles'
    context['notification'] = notification[0]
    context['notifyAmount'] = notification[1]
    context['pendingBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                status='pending').count()
    context['approvedBOMCount'] = BillOfMaterials.objects.filter(company=getUserCompany(request),
                                                                 status='approved').count()
    context['version'] = version.objects.all()

    if 'editConsignment' in request.POST:
        if request.POST['name'] == '':
            messages.info(request, 'Please load an Inventory Profile before trying to edit.')
        else:
            consignObj = consignmentProfiles.objects.filter(company=getUserCompany(request))
            stockObj = StockItems.objects.filter(company=getUserCompany(request))
            context['stockObj'] = stockObj
            context['consignObj'] = consignObj
            consignDict = {}
            consignmentObj = consignmentProfiles.objects.get(company=getUserCompany(request),
                                                             name=request.POST['name'])
            if consignmentObj.details == "":
                pass
            else:
                consignDict = ast.literal_eval(consignmentObj.details)
                consignmentList = list(consignDict.keys())
                context['consignmentObj'] = consignmentList
            context['consignProfileName'] = request.POST['name']
            return render(request, 'stock/consignment.html', context=context)

    return render(request, 'stock/consignmentView.html', context=context)
