from . import views
from django.urls import path

app_name = "hr_app"

urlpatterns = [
    path("hr", views.HR, name="hr"),
]