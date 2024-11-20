from . import views
from django.urls import path

app_name = "customer_app"

urlpatterns = [
    path("customer", views.Customer, name="customer"),
    path("archive", views.archive, name="archive"),
    path("add_customer", views.add_customer, name="add_customer"),
    path("import_customers/", views.import_customers_view, name="import_customers"),
    path("send_email/<int:customer_id>/", views.send_email, name="send_email"),
    path(
        "bulk_remove_customers/",
        views.bulk_remove_customers,
        name="bulk_remove_customers",
    ),
    path("action_submit/<int:customer_id>/", views.action_submit, name="action_submit"),
    path("note_submit/<int:customer_id>/", views.note_submit, name="note_submit"),
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
    path("edit_customer/<int:customer_id>", views.edit_customer, name="edit_customer"),
    path(
        "remove_customer/<int:customer_id>",
        views.remove_customer,
        name="remove_customer",
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
        "set_customer_route/<int:customer_id>/<int:route_id>",
        views.set_customer_route,
        name="set_customer",
    ),
    path(
        "remove_customer_route/<int:customer_id>",
        views.remove_customer_route,
        name="remove_customer_route",
    ),
    path("assign_agents", views.assign_agents, name="assign_agents"),
    path("assign_agent", views.assign_agent, name="assign_agent"),
    path(
        "change_customer_client/<int:customer_id>",
        views.change_customer_client,
        name="change_customer_client",
    ),
    path(
        "add_stage_ans/<int:route_id>/<int:product_id>/<int:stage_id>/<int:question_id>/<int:customer_id>",
        views.add_stage_ans,
        name="add_stage_ans",
    ),
    path("get_agent_customers/<int:agent_id>", views.get_agent_customers, name="get_agent_customers"),
    path("refresh_epc/<int:customer_id>", views.refresh_epc, name="refresh_epc"),
]
