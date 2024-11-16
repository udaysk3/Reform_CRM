from . import views
from django.urls import path

app_name = "question_actions_requirements_app"

urlpatterns = [
    path("questions", views.questions, name="questions"),
    path("add_question", views.add_question, name="add_question"),
    path("edit_question/<int:question_id>", views.edit_question, name="edit_question"),
    path(
        "archive_question/<int:question_id>",
        views.archive_question,
        name="archive_question",
    ),
    path(
        "client_archive_question/<int:question_id>/<int:client_id>",
        views.client_archive_question,
        name="client_archive_question",
    ),
]
