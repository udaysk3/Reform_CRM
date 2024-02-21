from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = "app"

urlpatterns = [
    path("", views.home),
    path("dashboard", views.dashboard),
    path("customer", views.Customer, name="customer"),
    path("finance", views.Finance, name="finance"),
    path("adminview", views.Admin, name="admin"),
    path("hr", views.HR, name="hr"),
    path("add_customer", views.add_customer, name="add_customer"),
     path('import_customers/', views.import_customers_view, name='import_customers'),
     path('bulk_remove_customers/', views.bulk_remove_customers, name='bulk_remove_customers'),
    path("action_submit/<int:customer_id>", views.action_submit, name="action_submit"),
    path("na_action_submit/<int:customer_id>", views.na_action_submit, name="na_action_submit"),
    path("edit_customer/<int:customer_id>", views.edit_customer, name="edit_customer"),
    path(
        "remove_customer/<int:customer_id>",
        views.remove_customer,
        name="remove_customer",
    ),
    path(
        "customer-detail/<int:customer_id>",
        views.customer_detail,
        name="customer_detail",
    ),
    path('add_client',views.add_client,name='add_client'),
    path('add_campaign',views.add_campaign,name='add_campaign'),
    path('edit_client/<int:client_id>',views.edit_client,name='edit_client'),
    path('remove_client/<int:client_id>',views.remove_client,name='remove_client'),
    path('remove_campaign/<int:campaign_id>',views.remove_campaign,name='remove_campaign'),
]