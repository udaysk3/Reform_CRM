from . import views
from django.urls import path

app_name = "app"

urlpatterns = [
    path("", views.home),
    path("dashboard", views.dashboard),
    path("customer", views.Customer, name="customer"),
    path("client", views.Client, name="client"),
    path("council", views.council, name="council"),
    path("archive", views.archive, name="archive"),
    path("finance", views.Finance, name="finance"),
    path("adminview", views.Admin, name="admin"),
    path("funding_route", views.funding_route, name="funding_route"),
    path("hr", views.HR, name="hr"),
    path("add_customer", views.add_customer, name="add_customer"),
    path("add_client", views.add_client, name="add_client"),
    path("add_funding_route", views.add_funding_route, name="add_funding_route"),
    path("import_customers/", views.import_customers_view, name="import_customers"),
    path(
        "bulk_remove_customers/",
        views.bulk_remove_customers,
        name="bulk_remove_customers",
    ),
    path("bulk_remove_clients/", views.bulk_remove_clients, name="bulk_remove_clients"),
    path("action_submit/<int:customer_id>/", views.action_submit, name="action_submit"),
    path(
        "close_action_submit/<int:customer_id>/",
        views.close_action_submit,
        name="close_action_submit",
    ),
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
        "client_action_submit/<int:client_id>/",
        views.client_action_submit,
        name="client_action_submit",
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
    path("edit_customer/<int:customer_id>", views.edit_customer, name="edit_customer"),
    path("edit_client/<int:client_id>", views.edit_client, name="edit_client"),
    path(
        "remove_customer/<int:customer_id>",
        views.remove_customer,
        name="remove_customer",
    ),
    path(
        "remove_client/<int:client_id>",
        views.remove_client,
        name="remove_client",
    ),
    path("edit_council/<int:council_id>", views.edit_council, name="edit_council"),
    path(
        "remove_council/<int:council_id>",
        views.remove_council,
        name="remove_council",
    ),
    path(
        "customer-detail/<int:customer_id>/<int:s_customer_id>",
        views.customer_detail,
        name="customer_detail",
    ),
    path(
        "customer-detail/<int:customer_id>",
        views.customer_detail,
        name="customer_detail",
    ),
    path(
        "client-detail/<int:client_id>",
        views.client_detail,
        name="client_detail",
    ),
    path(
        "council-detail/<int:council_id>",
        views.council_detail,
        name="council_detail",
    ),
    path("add_client", views.add_client, name="add_client"),
    path("add_campaign/<int:client_id>", views.add_campaign, name="add_campaign"),
    path("add_product_view/<int:client_id>", views.add_product_view, name="add_product_view"),
    path("add_product/<int:client_id>", views.add_product, name="add_product"),
    path("edit_client/<int:client_id>", views.edit_client, name="edit_client"),
    path("remove_client/<int:client_id>", views.remove_client, name="remove_client"),
    path(
        "remove_campaign/<int:campaign_id>/<int:client_id>",
        views.remove_campaign,
        name="remove_campaign",
    ),
    path(
        "remove_product/<int:product_id>/<int:client_id>",
        views.remove_product,
        name="remove_product",
    ),
    path(
        "add_child_customer/<int:customer_id>",
        views.add_child_customer,
        name="add_child_customer",
    ),
    path(
        "make_primary/<int:parent_customer_id>/<int:child_customer_id>",
        views.make_primary,
        name="make_primary",
    ),
    path(
        "add_council_funding_route/<int:council_id>",
        views.add_council_funding_route,
        name="add_council_funding_route",
    ),
    path(
        "edit_funding_route/<int:route_id>",
        views.edit_funding_route,
        name="edit_funding_route",
    ),
    path(
        "remove_funding_route/<int:route_id>",
        views.remove_funding_route,
        name="remove_funding_route",
    ),
    path("<int:route_id>/stages", views.create_stage, name="create_stage"),
    path("remove_stage/<int:stage_id>", views.remove_stage, name="remove_stage"),
    path(
        "edit_stage/<int:route_id>/<int:stage_id>", views.edit_stage, name="edit_stage"
    ),
    path(
        "set_customer_route/<int:customer_id>/<int:route_id>",
        views.set_customer_route,
        name="set_customer",
    ),
    path(
        "set_stage_values/<int:customer_id>",
        views.set_stage_values,
        name="set_stage_values",
    ),
    path(
        "remove_customer_route/<int:customer_id>",
        views.remove_customer_route,
        name="remove_customer_route",
    ),
    path(
        "funding_route_detail/<int:route_id>",
        views.funding_route_detail,
        name="funding_route_detail",
    ),
    path("assign_agents", views.assign_agents, name="assign_agents"),
    path("assign_agent", views.assign_agent, name="assign_agent"),
    path("send_email/<int:customer_id>", views.send_email, name="send_email"),
    path(
        "send_client_email/<int:customer_id>",
        views.send_client_email,
        name="send_client_email",
    ),
    path("query/cities/<str:q>", views.query_city, name="query_city"),
    path("query/countys/<str:q>", views.query_county, name="query_county"),
    path("query/countries/<str:q>", views.query_country, name="query_country"),
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
    path("get_notifications", views.get_notifications, name="get_notifications"),
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
        "get_campaign/<int:client_id>",
        views.get_campaign,
        name="get_campaign",
    ),
]
