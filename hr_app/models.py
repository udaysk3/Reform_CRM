from django.db import models
from user.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_user', blank=True, null=True)
    employee_image = models.ImageField(upload_to='employee_images', blank=True, null=True)
    reporting_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='emp_reporting_to')
    work_setup = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    personal_email = models.EmailField(max_length=100, blank=True, null=True)
    personal_phon = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    work_history = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    client = models.ForeignKey('client_app.Clients', on_delete=models.SET_NULL, blank=True, null=True)
    data_of_joining = models.DateField(blank=True, null=True)
    employee_type = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    tenure = models.CharField(max_length=100, blank=True, null=True)
    action = models.ForeignKey('home.Action', on_delete=models.SET_NULL, blank=True, null=True)
    onboarding = models.DateField(blank=True, null=True)
    probation = models.DateField(blank=True, null=True)
    regularised = models.DateField(blank=True, null=True)
    holiday= models.IntegerField(blank=True, null=True)
    sick= models.IntegerField(blank=True, null=True)
    compassionate = models.IntegerField(blank=True, null=True)
    duvey= models.IntegerField(blank=True, null=True)
    
    def add_emp_action(self, text=None, agent=None, created_at=None, action_type=None,):
        return Employee_Action.objects.create(employee=self, text=text, agent=agent,created_at=created_at,  action_type=action_type,)

    def get_created_at_emp_action_history(self):
        return (Employee_Action.objects.filter(employee=self).order_by("-created_at"))

class Emergency_contact(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='emp_emergency_contact')
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)

class Employee_Action(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(max_length=999, blank= True, null=True)
    action_type = models.CharField(max_length=225, blank= True, null=True)

class Upcoming_time_off(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='emp_upcoming_time_off')
    leave_type = models.CharField(max_length=100, blank=True, null=True)
    duration = models.DateTimeField(blank=True, null=True)
    hours = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    leave_file = models.FileField(upload_to='leave_files', blank=True, null=True)

class Requests_time_off(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='emp_requests_time_off')
    leave_type = models.CharField(max_length=100, blank=True, null=True)
    duration = models.DateTimeField(blank=True, null=True)
    hours = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    leave_file = models.FileField(upload_to='leave_files', blank=True, null=True)

class Time_off_summary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='emp_time_off_summary')
    leave_type = models.CharField(max_length=100, blank=True, null=True)
    beginning_balance = models.IntegerField(blank=True, null=True)
    accrued = models.IntegerField(blank=True, null=True)
    used = models.IntegerField(blank=True, null=True)
    scheduled = models.IntegerField(blank=True, null=True)
    current_balance = models.IntegerField(blank=True, null=True)

class Courses(models.Model):
    assigned = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='emp_courses')
    status = models.CharField(max_length=100, blank=True, null=True)
    due_on = models.DateField(blank=True, null=True)
    completed = models.TextField(blank=True, null=True)
    view_certificate = models.FileField(upload_to='certificates', blank=True, null=True)