from django.db import models
from user.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_user', blank=True, null=True)
    employee_image = models.ImageField(upload_to='employee_images', blank=True, null=True)
    status = models.BooleanField(default=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    reporting_to = models.CharField(max_length=100, blank=True, null=True)
    work_setup = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    personal_email = models.EmailField(max_length=100, blank=True, null=True)
    personal_phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    work_history = models.TextField(blank=True, null=True)
    emergency_contact = models.ForeignKey('Emergency_contact', on_delete=models.CASCADE, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    client = models.ForeignKey('client_app.Clients', on_delete=models.CASCADE, blank=True, null=True)
    data_of_joining = models.DateField(blank=True, null=True)
    employee_type = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    tenure = models.CharField(max_length=100, blank=True, null=True)
    action = models.ForeignKey('home.Action', on_delete=models.CASCADE, blank=True, null=True)

    def add_emp_action(self, text=None, agent=None, created_at=None, action_type=None,):
        return Employee_Action.objects.create(employee=self, text=text, agent=agent,created_at=created_at,  action_type=action_type,)

    def get_created_at_emp_action_history(self):
        return (Employee_Action.objects.filter(employee=self).order_by("-created_at"))

class Emergency_contact(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)

class Employee_Action(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    text = models.TextField(max_length=999, blank= True, null=True)
    action_type = models.CharField(max_length=225, blank= True, null=True)