from . import views
from django.urls import path

app_name = "client_app"

urlpatterns = [  
    path("client", views.Client, name="client"),
    path("add_client", views.add_client, name="add_client"),
    path(
        "client_action_submit/<int:client_id>/",
        views.client_action_submit,
        name="client_action_submit",
    ),
    path(
        "client_note_submit/<int:client_id>/",
        views.client_note_submit,
        name="client_note_submit",
    ),
    path(
        "close_client_action_submit/<int:customer_id>/",
        views.close_client_action_submit,
        name="close_client_action_submit",
    ),
    path(
        "na_client_action_submit/<int:client_id>/",
        views.na_client_action_submit,
        name="na_client_action_submit",
    ),
    path(
        "lm_client_action_submit/<int:client_id>/",
        views.lm_client_action_submit,
        name="lm_client_action_submit",
    ),
    path("edit_client/<int:client_id>", views.edit_client, name="edit_client"),
    path(
        "remove_client/<int:client_id>",
        views.remove_client,
        name="remove_client",
    ),
    path(
        "client-detail/<int:client_id>",
        views.client_detail,
        name="client_detail",
    ),
    path("add_client", views.add_client, name="add_client"),
    path("add_campaign/<int:client_id>", views.add_campaign, name="add_campaign"),
    path("add_product/<int:client_id>", views.add_product, name="add_product"),
    path("edit_client/<int:client_id>", views.edit_client, name="edit_client"),
    path("remove_client/<int:client_id>", views.remove_client, name="remove_client"),
    path(
        "remove_campaign/<int:campaign_id>/<int:client_id>",
        views.remove_campaign,
        name="remove_campaign",
    ),
    path("stages/<int:client_id>", views.create_stage, name="create_stage"),
    path(
        "add_product_client/<int:client_id>",
        views.add_product_client,
        name="add_product_client",
    ),
    path(
        "add_route_client/<int:client_id>",
        views.add_route_client,
        name="add_route_client",
    ),
    path("remove_stage/<int:stage_id>", views.remove_stage, name="remove_stage"),
    path("edit_stage/<int:stage_id>", views.edit_stage, name="edit_stage"),
    path(
        "send_client_email/<int:customer_id>",
        views.send_client_email,
        name="send_client_email",
    ),
    path(
        "add_coverage_areas/<int:client_id>",
        views.add_coverage_areas,
        name="add_coverage_areas",
    ),
    path(
        "archive_campaign/<int:client_id>/<int:campaign_id>",
        views.archive_campaign,
        name="archive_campaign",
    ),
    path(
        "archive_product/<int:client_id>/<int:product_id>",
        views.archive_product,
        name="archive_product",
    ),
    path(
        "archive_route/<int:client_id>/<int:route_id>/<int:council_id>",
        views.archive_route,
        name="archive_route",
    ),
    path(
        "get_campaign/<int:client_id>",
        views.get_campaign,
        name="get_campaign",
    ),
    path("stage_template", views.stage_template, name="stage_template"),
    path(
        "edit_local_funding_route/<int:funding_route_id>",
        views.edit_local_funding_route,
        name="edit_local_funding_route",
    ),
    path(
        "make_template_stage/<int:stage_id>",
        views.make_template_stage,
        name="make_template_stage",
    ),
    path(
        "add_client_stage_rule/<int:route_id>/<int:product_id>/<int:stage_id>/<int:question_id>/<int:client_id>",
        views.add_client_stage_rule,
        name="add_client_stage_rule",
    ),
    path("add_priority/<int:stage_id>/<int:client_id>", views.add_priority, name="add_priority"),
    path("add__route_priority/<int:route_id>/<int:client_id>", views.add_route_priority, name="add_route_priority"),
    path("customer_jr_order/<int:client_id>", views.customer_jr_order, name="customer_jr_order"),
    path("add_product/<int:client_id>", views.add_product, name="add_product"),
]
