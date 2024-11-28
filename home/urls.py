from . import views
from django.urls import path

app_name = "app"

urlpatterns = [
    path("", views.home),
    path("finance", views.Finance, name="finance"),
    path("suggestion", views.suggestion, name="suggestion"),
    path("add_suggestion", views.add_suggestion, name="add_suggestion"),
    path("detail_suggestion/<int:suggestion_id>", views.detail_suggestion, name="detail_suggestion"),
    path("edit_suggestion/<int:suggestion_id>", views.edit_suggestion, name="edit_suggestion"),
    path("add_sub_suggestion/<int:suggestion_id>", views.add_sub_suggestion, name="add_sub_suggestion"),
    path("add_comment/<int:suggestion_id>", views.add_comment, name="add_comment"),
    path("merge_suggestions/<int:suggestion_id>", views.merge_suggestions, name="merge_suggestions"),
    path('delete_sub_suggestion/<int:sub_suggestion_id>', views.delete_sub_suggestion, name='delete_sub_suggestion'),
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
    path("suggestion_order", views.suggestion_order, name="suggestion_order"),
    path("get_postcodes/<str:region>", views.get_postcodes, name="get_postcodes"),
    path("assign_agents_suggestions", views.assign_agents, name="assign_agents"),
    path("assign_agent_suggestions", views.assign_agent, name="assign_agent"),
    path("change_sub_suggestion_status/<int:sub_suggestion_id>", views.change_sub_suggestion_status, name="change_sub_suggestion_status"),
    path("change_sub_suggestion_agent/<int:sub_suggestion_id>", views.change_sub_suggestion_agent, name="change_sub_suggestion_agent"),
]
