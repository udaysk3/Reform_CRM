from . import views
from django.urls import path,include

app_name= 'security_app'

urlpatterns = [
    path('s_employee',views.s_employee,name='s_employee'),
    path('s_edit_employee/<int:emp_id>',views.s_edit_employee,name='s_edit_employee'),
    path('approve_role/<int:emp_id>',views.approve_role,name='approve_role'),
    path('deny_role/<int:emp_id>',views.deny_role,name='deny_role'),
    path('role',views.role,name='role'),
    path('client_assign_agents',views.assign_agents,name='assign_agents'),
    path('s_client',views.s_client,name='s_client'),
    path('add_role',views.add_role,name='add_role'),
    path('change_otp_mail/<int:emp_id>',views.change_otp_mail,name='change_otp_mail'),
    path('reset_password/<int:emp_id>',views.reset_password,name='reset_password'),
    path('upload_profile/<int:emp_id>',views.upload_profile,name='upload_profile'),
    path('edit_role/<int:role_id>',views.edit_role,name='edit_role'),
    path('bulk_delete_roles',views.bulk_delete_roles,name='bulk_delete_roles'),
]