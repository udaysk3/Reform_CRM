from django.db import models
from user.models import User

class Role(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    dashboard = models.BooleanField(default=False)
    mcustomer = models.BooleanField(default=False)
    customer = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    client = models.BooleanField(default=False)
    council = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    product = models.BooleanField(default=False)
    globals = models.BooleanField(default=False)
    finance = models.BooleanField(default=False)
    hr = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    funding_route = models.BooleanField(default=False)
    CJ = models.BooleanField(default=False)
    QA = models.BooleanField(default=False)
    h_dashboard = models.BooleanField(default=False)
    h_employee = models.BooleanField(default=False)
    h_application = models.BooleanField(default=False)
    h_onboarding = models.BooleanField(default=False)
    h_timesheet = models.BooleanField(default=False)
    h_emp_action = models.BooleanField(default=False)
    h_emp_notify = models.BooleanField(default=False)
    h_offboarding = models.BooleanField(default=False)
    h_org_chart = models.BooleanField(default=False)
    knowledge_base = models.BooleanField(default=False)
    s_employee = models.BooleanField(default=False)
    s_role = models.BooleanField(default=False)
    s_client = models.BooleanField(default=False)

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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


class Emergency_contact(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)