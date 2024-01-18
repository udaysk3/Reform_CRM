from . import views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

app_name= 'app'

urlpatterns = [
    path('',views.home),
    path("dashboard", views.dashboard),
    path("customer", views.Customer, name="customer" ),
    path("finance", views.Finance, name="finance" ),
    path("adminview", views.Admin, name="admin" ),
    path("hr", views.HR, name="hr" ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)