from . import views
from django.urls import path

app_name = "customer_journey_app"

urlpatterns = [
    path("customer_journey", views.customer_journey, name="customer_journey"),
    path("add_stage", views.add_stage, name="add_stage"),
    path("cj_route/<int:route_id>", views.cj_route, name="cj_route"),
    path(
        "cj_product/<int:route_id>/<int:product_id>",
        views.cj_product,
        name="cj_product",
    ),
    path(
        "cj_stage/<int:route_id>/<int:product_id>/<int:stage_id>",
        views.cj_stage,
        name="cj_stage",
    ),
    path(
        "add_stage_rule/<int:route_id>/<int:product_id>/<int:stage_id>/<int:question_id>",
        views.add_stage_rule,
        name="add_stage_rule",
    ),
    path(
        "delete_stage/<int:stage_id>",
        views.delete_stage,
        name="delete_stage",
    ),
    path(
        "delete_cj_stage/<int:route_id>/<int:product_id>/<int:stage_id>",
        views.delete_cj_stage,
        name="delete_cj_stage",
    ),
    path(
        "delete_cj_stage_question/<int:route_id>/<int:product_id>/<int:stage_id>/<int:question_id>",
        views.delete_cj_stage_question,
        name="delete_cj_stage_question",
    ),
    path("archive_global_stage/<int:stage_id>", views.archive_global_stage, name="archive_global_stage"),
]
