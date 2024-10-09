from . import views
from django.urls import path

app_name = "funding_route_app"

urlpatterns = [
    path(
        "add_funding_route/<int:council_id>",
        views.add_funding_route,
        name="add_funding_route",
    ),
    path(
        "edit_funding_route/<int:funding_route_id>",
        views.edit_funding_route,
        name="edit_funding_route",
    ),
    path(
        "add_council_funding_route/<int:council_id>",
        views.add_council_funding_route,
        name="add_council_funding_route",
    ),
    path(
        "remove_funding_route/<int:route_id>",
        views.remove_funding_route,
        name="remove_funding_route",
    ),
    path("funding_route", views.funding_route, name="funding_route"),
    
    path(
        "edit_local_funding_route/<int:funding_route_id>",
        views.edit_local_funding_route,
        name="edit_local_funding_route",
    ),
    path(
        "add_new_funding_route",
        views.add_new_funding_route,
        name="add_new_funding_route",
    ),
    path(
        "edit_new_funding_route/<int:route_id>",
        views.edit_new_funding_route,
        name="edit_new_funding_route",
    ),
    path("delete_route/<int:route_id>", views.delete_route, name="delete_route"),
    path("edit_route/<int:route_id>", views.edit_route, name="edit_route"),
    path(
        "archive_global_funding_route/<int:funding_route_id>",
        views.archive_global_funding_route,
        name="archive_global_funding_route",
    ),
]