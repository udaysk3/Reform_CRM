from . import views
from django.urls import path,include

app_name= 'security_app'

urlpatterns = [
    path('s_employee',views.s_employee,name='s_employee'),
    path('s_edit_employee/<int:emp_id>',views.s_edit_employee,name='s_edit_employee'),
    path('approve_role/<int:emp_id>',views.approve_role,name='approve_role'),
    path('deny_role/<int:emp_id>',views.deny_role,name='deny_role'),
]
