from . import views
from django.urls import path

app_name = "dashboard_app"

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
]
