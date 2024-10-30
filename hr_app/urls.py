from . import views
from django.urls import path

app_name = "hr_app"

urlpatterns = [
    path("employee", views.employee, name="employee"),
    path("off_boarding", views.off_boarding, name="off_boarding"),
    path("emp_profile/<int:emp_id>", views.emp_profile, name="emp_profile"),
    path("job_info", views.job_info, name="job_info"),
    path("time_off", views.time_off, name="time_off"),
    path("courses", views.courses, name="courses"),
    path('add_employee', views.add_employee, name="add_employee"),
    path('bulk_archive_employes', views.bulk_archive_employes, name="bulk_archive_employes"),
    path('edit_employee/<int:emp_id>', views.edit_employee, name="edit_employee"),
]