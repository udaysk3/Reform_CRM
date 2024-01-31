from . import views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

app_name= 'app'

urlpatterns = [
    path('',views.home),
    path("dashboard", views.dashboard),
    path("customer", views.Customer, name="customer" ),
    path("finance", views.Finance, name="finance" ),
    path("adminview", views.Admin, name="admin" ),
    path("hr", views.HR, name="hr" ),
    path("customer_detail",views.customer_detail,name="customer_detail"),
]