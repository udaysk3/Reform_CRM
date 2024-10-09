from . import views
from django.urls import path

app_name = "admin_app"

urlpatterns = [
    path("adminview", views.Admin, name="admin"),
    path("add_template", views.add_template, name="add_template"),
    path("edit_template/<int:template_id>", views.edit_template, name="edit_template"),
    path(
        "remove_template/<int:template_id>",
        views.remove_template,
        name="remove_template",
    ),
    path("add_reason", views.add_reason, name="add_reason"),
    path("edit_reason/<int:reason_id>", views.edit_reason, name="edit_reason"),
    path("remove_reason/<int:reason_id>", views.remove_reason, name="remove_reason"),
    path("add_signature", views.add_signature, name="add_signature"),
    path(
        "edit_signature/<int:signature_id>", views.edit_signature, name="edit_signature"
    ),
    path(
        "remove_signature/<int:signature_id>",
        views.remove_signature,
        name="remove_signature",
    ),
    path(
        "get_campaign/<int:client_id>",
        views.get_campaign,
        name="get_campaign",
    ),
]
