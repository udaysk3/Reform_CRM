from . import views
from django.urls import path

app_name = "region_app"

urlpatterns = [
    path("council", views.council, name="council"),
    path(
        "na_action_submit/<int:customer_id>/",
        views.na_action_submit,
        name="na_action_submit",
    ),
    path(
        "lm_action_submit/<int:customer_id>/",
        views.lm_action_submit,
        name="lm_action_submit",
    ),
    path(
        "council_action_submit/<int:council_id>/",
        views.council_action_submit,
        name="council_action_submit",
    ),
    path(
        "na_council_action_submit/<int:council_id>/",
        views.na_council_action_submit,
        name="na_council_action_submit",
    ),
    path("edit_council/<int:council_id>", views.edit_council, name="edit_council"),
    path(
        "remove_council/<int:council_id>",
        views.remove_council,
        name="remove_council",
    ),
    path(
        "council-detail/<int:council_id>",
        views.council_detail,
        name="council_detail",
    ),
    path("add_local_authority", views.add_local_authority, name="add_local_authority"),
    path(
        "add_council_funding_route/<int:council_id>",
        views.add_council_funding_route,
        name="add_council_funding_route",
    ),
    path(
        "delete_council/<int:council_id>",
        views.delete_council,
        name="delete_council",
    ),
    path("region_archive/<int:council_id>/<int:route_id>", views.region_archive, name="region_archive"),
]
