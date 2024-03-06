from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = "app"

urlpatterns = [
    path("", views.home),
    path("dashboard", views.dashboard),
    path("customer", views.Customer, name="customer"),
    path("funding_route", views.funding_route, name="funding_route"),
    path("finance", views.Finance, name="finance"),
    path("adminview", views.Admin, name="admin"),
    path("hr", views.HR, name="hr"),
    path("add_customer", views.add_customer, name="add_customer"),
    path("add_funding_route", views.add_funding_route, name="add_funding_route"),
     path('import_customers/', views.import_customers_view, name='import_customers'),
     path('bulk_remove_customers/', views.bulk_remove_customers, name='bulk_remove_customers'),
    path("action_submit/<int:customer_id>/", views.action_submit, name="action_submit"),
    path("na_action_submit/<int:customer_id>/", views.na_action_submit, name="na_action_submit"),
    path("funding_route_action_submit/<int:funding_route_id>/", views.funding_route_action_submit, name="funding_route_action_submit"),
    path("na_funding_route_action_submit/<int:funding_route_id>/", views.na_funding_route_action_submit, name="na_funding_route_action_submit"),
    path("edit_customer/<int:customer_id>", views.edit_customer, name="edit_customer"),
    path(
        "remove_customer/<int:customer_id>",
        views.remove_customer,
        name="remove_customer",
    ),
    path("edit_funding_route/<int:funding_route_id>", views.edit_funding_route, name="edit_funding_route"),
    path(
        "remove_funding_route/<int:funding_route_id>",
        views.remove_funding_route,
        name="remove_funding_route",
    ),
    path(
        "customer-detail/<int:customer_id>",
        views.customer_detail,
        name="customer_detail",
    ),
    path(
        "funding_route-detail/<int:funding_route_id>",
        views.funding_route_detail,
        name="funding_route_detail",
    ),
    path('add_client',views.add_client,name='add_client'),
    path('add_campaign',views.add_campaign,name='add_campaign'),
    path('edit_client/<int:client_id>',views.edit_client,name='edit_client'),
    path('remove_client/<int:client_id>',views.remove_client,name='remove_client'),
    path('remove_campaign/<int:campaign_id>',views.remove_campaign,name='remove_campaign'),
    path('add_child_customer/<int:customer_id>', views.add_child_customer,name='add_child_customer'),
    path('make_primary/<int:parent_customer_id>/<int:child_customer_id>', views.make_primary, name='make_primary'),
    # path('add_funding_route/<int:customer_id>', views.add_funding_route,name='add_funding_route'),
    # path('add_funding_route/<int:funding_route_id>', views.add_funding_route,name='add_funding_route'),
]