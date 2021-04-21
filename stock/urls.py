"""Visualization URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from management import views as management
from user_control import views as user_control
from bill_of_materials import views as bill_of_materials
from consignment import views as consignment
from notifications import views as notifications
from shopifyRESTfullAPI import views as shopify

app_name = "stock"

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', user_control.register, name='register'),
    path('logout/', user_control.logout_request, name='logout'),
    path('login/', user_control.login_request, name='login'),
    path('stock_in/', views.stock_in, name='stock_in'),
    path('order_review/', views.OrderReview, name='order_review'),
    path('search/', views.search_stock, name='search_stock'),
    path('review_requested_stock/', views.review_requested_stock, name='review_requested_stock'),
    path('inventoryManagement/', management.inventoryManagement, name='inventoryManagement'),
    path('InventoryProfiles/', consignment.consignmentView, name='consignmnetView'),
    path('billOfMaterials/', bill_of_materials.billOfMaterials, name='billOfMaterials'),
    path('viewBillOfMaterials/', bill_of_materials.viewBillOfMaterials, name='viewBillOfMaterials'),
    path('approvedBillOfMaterials/', bill_of_materials.approvedBillOfMaterials, name='approvedBillOfMaterials'),
    path('notificationHistory/', notifications.notificationHistory, name='notificationHistory'),
    path('deliveryBookIn/', views.deliveryBookIn, name='deliveryBookIn'),
    path('shopify/', shopify.manage, name='shopfiy')
]
