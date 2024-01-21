from . import views
from django.urls import path,include

app_name= 'user'

urlpatterns = [
    path('login',views.signin,name='login'),
    path('logout',views.logout_view,name='logout'),
    path('add_user',views.add_user,name='add_user'),
    path('edit_user/<int:user_id>',views.edit_user,name='edit_user'),
    path('remove_user/<int:user_id>',views.remove_user,name='remove_user'),
    
]
