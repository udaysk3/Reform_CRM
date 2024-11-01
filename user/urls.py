from . import views
from django.urls import path,include

app_name= 'user'

urlpatterns = [
    path('login',views.signin,name='login'),
    path('logout',views.logout_view,name='logout'),
    path('remove_user/<int:user_id>',views.remove_user,name='remove_user'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
]
