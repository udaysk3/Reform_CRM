from . import views
from django.urls import path

app_name = "hr_app"

urlpatterns = [
    path("employee", views.employee, name="employee"),
    path("off_boarding", views.off_boarding, name="off_boarding"),
    path("emp_profile/<int:emp_id>", views.emp_profile, name="emp_profile"),
    path("job_info/<int:emp_id>", views.job_info, name="job_info"),
    path("time_off/<int:emp_id>", views.time_off, name="time_off"),
    path("courses/<int:emp_id>", views.courses, name="courses"),
    path('add_employee', views.add_employee, name="add_employee"),
    path('bulk_archive_employes', views.bulk_archive_employes, name="bulk_archive_employes"),
    path('edit_employee/<int:emp_id>', views.edit_employee, name="edit_employee"),
    path('edit_basic_information/<int:emp_id>', views.edit_basic_information, name="edit_basic_information"),
    path('edit_job_detail/<int:emp_id>', views.edit_job_detail, name="edit_job_detail"),
    path('edit_employment_status/<int:emp_id>', views.edit_employment_status, name="edit_employment_status"),
    path('add_emergency_contact/<int:emp_id>', views.add_emergency_contact, name="add_emergency_contact"),
    path('edit_emergency_contact/<int:contact_id>', views.edit_emergency_contact, name="edit_emergency_contact"),
]