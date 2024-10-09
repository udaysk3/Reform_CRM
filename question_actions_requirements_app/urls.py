from . import views
from django.urls import path

app_name = "question_actions_requirements_app"

urlpatterns = [
    path("questions", views.questions, name="questions"),
    path("add_question", views.add_question, name="add_question"),
    path("edit_question/<int:question_id>", views.edit_question, name="edit_question"),
    path(
        "delete_question/<int:question_id>",
        views.delete_question,
        name="delete_question",
    ),
]
