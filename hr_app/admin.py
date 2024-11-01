from django.contrib import admin

# Register your models here.

from .models import Employee, Emergency_contact, Employee_Action

admin.site.register(Employee)
admin.site.register(Emergency_contact)
admin.site.register(Employee_Action)