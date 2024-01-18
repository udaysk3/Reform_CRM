from . import views
from django.urls import path,include

app_name= 'user'

urlpatterns = [
    path('login',views.signin,name='login'),
    path('logout',views.logout_view,name='logout'),
]
