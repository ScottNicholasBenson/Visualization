import json

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django_common.auth_backends import User
from django.contrib.auth import logout, login, authenticate

from functions.views import getStaffStatus, getCompanyList, global_context, getUserCompany, generateStockUniqueNumber
from stock.models import Profile, StockItems
from user_control.models import shopify_API


@login_required(login_url='/login/')
def register(request):
    # stock = StockItems.objects.all()
    # for i in stock:
    #     print(i.name)
    #     StockItems.objects.filter(name=i.name).update(uniqueStockNumber=generateStockUniqueNumber())
    current_user = request.user
    context = global_context(request)
    if shopify_API.objects.filter(company__in=getCompanyList(request)).exists():
        context['shopify'] = shopify_API.objects.filter(company__in=getCompanyList(request))

    if 'unregister_shopify' in request.POST:
        unRegister = shopify_API.objects.get(user_id=current_user.id).delete()
        return redirect('stock:register')
    if 'register_shopify' in request.POST:
        PARAMS = {
            'since_id': 0
        }
        r = requests.get(
            url='https://' + request.POST['API_Key'] + ':' + request.POST['password'] + '@' + request.POST['shop_name'] + '/admin/api/2021-01/products.json',
            params=PARAMS)
        data = r.json()

        if 'errors' in data:
            if data['errors'] == 'Not Found':
                messages.error(request, 'Store Name Incorrect')
            else:
                messages.error(request, data['errors'])
            return redirect('stock:register')
        messages.success(request, 'Shopify Account Linked!')
        register = shopify_API.objects.create(user_id=current_user.id,
                                              company=getUserCompany(request),
                                              API_Key=request.POST['API_Key'],
                                              password=request.POST['password'],
                                              store_name=request.POST['shop_name'])
        register.save()

        return redirect('stock:register')
    if getStaffStatus(request) == 0:
        return
    if request.method == 'POST':
        if 'delete' in request.POST:
            current_user = request.user
            if current_user.username == request.POST['name']:
                messages.info(request, "Trying to delete yourself can be painful, wouldn't recommend it...")
            else:
                userID = User.objects.get(username=request.POST['name']).pk
                userProfile = Profile.objects.get(user_id=userID).delete()
                userUser = User.objects.get(username=request.POST['name']).delete()
                messages.success(request, "User: " + request.POST['name'] + " Deleted!")
        else:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                userID = User.objects.get(username=form.cleaned_data['username']).pk
                newUserCompanyAssign = Profile.objects.get(user_id=userID)
                newUserCompanyAssign.company = getUserCompany(request)
                newUserCompanyAssign.save()
                messages.success(request, "User: " + form.cleaned_data['username'] + " Registered!")
                return redirect('stock:register')
            else:
                for msg in form.error_messages:
                    messages.error(request, f"{msg}: {form.error_messages[msg]}")
    companyAccounts = Profile.objects.filter(company__in=getCompanyList(request))
    form = UserCreationForm


    context['form'] = form
    context['active'] = 'register'
    context['PageName'] = 'Register'
    context['companyAccounts'] = companyAccounts

    return render(request,
                  'stock/register.html',
                  context)


def login_request(request):
    context = {}
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Now Logged in as: ' + username)
                return redirect('stock:homepage')
            else:
                context['message'] = 'Invalid Username or Password.'
                return redirect('stock:login')
        else:
            context['message'] = 'Invalid Username or Password.'
    form = AuthenticationForm()
    context['form'] = form
    return render(request,
                  'stock/login.html',
                  context=context)


def logout_request(request):
    logout(request)
    return redirect("stock:login")


class user_settings:
    uSettings = ""
