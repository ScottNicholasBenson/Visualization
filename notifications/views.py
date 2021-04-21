
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.contrib import messages

from functions.views import getStaffStatus, getCompanyList, global_context

from stock.models import notifications


@login_required(login_url='/login/')
def notificationHistory(request):
    if getStaffStatus(request) == 0:
        messages.error(request, 'you do not have the privileges to view this.')
    else:
        context = {}
        context = global_context(request)
        context['notifications'] = notifications.objects.filter(company__in=getCompanyList(request)).order_by(
            '-created_at')
        return render(request, 'stock/notificationHistory.html', context=context)
