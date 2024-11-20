from . import views
from django.urls import path

app_name = "app"

urlpatterns = [
    path("", views.home),
    path("finance", views.Finance, name="finance"),
    path("suggestion", views.suggestion, name="suggestion"),
    path("add_suggestion", views.add_suggestion, name="add_suggestion"),
    path("query/cities/<str:q>", views.query_city, name="query_city"),
    path("query/countys/<str:q>", views.query_county, name="query_county"),
    path("query/countries/<str:q>", views.query_country, name="query_country"),
    path("get_notifications", views.get_notifications, name="get_notifications"),
    path(
        "get_campaign/<int:client_id>",
        views.get_campaign,
        name="get_campaign",
    ),
    path("stage_template", views.stage_template, name="stage_template"),
    path("get_postcodes/<str:region>", views.get_postcodes, name="get_postcodes"),
]
