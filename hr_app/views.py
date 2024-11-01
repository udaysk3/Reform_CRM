from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from datetime import datetime
import pytz
from user.models import User
from security_app.models import Role
from .models import Employee


@login_required
def employee(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.all().filter(is_employee=True).filter(is_archive=False)
    return render(request, "home/employee.html", {'emps':employes})

@login_required
def off_boarding(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.all().filter(is_employee=True).filter(is_archive=True)
    return render(request, "home/off_boarding.html", {'emps':employes})

@login_required
def emp_profile(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    return render(request, "home/profile.html", {'emp':emp})

@login_required
def job_info(request):
    return render(request, "home/job_info.html")

@login_required
def time_off(request):
    return render(request, "home/time_off.html")

@login_required
def courses(request):
    return render(request, "home/courses.html")

def add_employee(request):
    roles = Role.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Agent with this email already exists!')
            return redirect('admin_app:admin') 
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role')
        department = request.POST.get('department')
        dob = request.POST.get('dob')
        hashed_password = make_password(password) 
        emp = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password= hashed_password,
            role=role,
            department=department,
            dob=dob,
            is_employee=True,
        )
        employee = Employee.objects.create(user=emp)
        employee.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Employee added',
            agent=request.user,
        )

        messages.success(request, 'Agnet added successfully!')
        return redirect('hr_app:employee')
    return render(request, 'home/add_employee.html', {'roles':roles})

def edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    roles = Role.objects.all()
    if emp.dob:
        emp_dob_formatted = emp.dob.strftime('%Y-%m-%d')
    else:
        emp_dob_formatted = ''
    if request.method == 'POST':
        if request.POST.get('password'):
            emp.password = make_password(request.POST.get('password'))
        if emp.role != request.POST.get('role'):
            emp.approved = ''
        emp.first_name = request.POST.get('first_name')
        emp.last_name = request.POST.get('last_name')
        emp.role = request.POST.get('role')
        emp.department = request.POST.get('department')
        emp.dob = request.POST.get('dob')
        emp.save()

        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Employee updated',
            agent=request.user,
        )

        messages.success(request, 'User updated successfully!')
        return redirect('hr_app:employee')  

    return render(request, 'home/edit_employee.html', {'emp':emp, 'emp_dob':emp_dob_formatted, 'roles':roles})

def bulk_archive_employes(request):
    if request.method == "GET":
        emp_ids_str = request.GET.get("ids", "")
        try:
            emp_ids = [
                int(id) for id in emp_ids_str.split(",") if id.isdigit()
            ]
            if emp_ids:
                emps = User.objects.filter(id__in=emp_ids)
                for emp in emps:
                    print(emp)
                    if emp.is_archive == True:
                        emp.is_archive = False
                    else:
                        emp.is_archive = True
                    emp.save()

                messages.success(request, "Selected employes archived successfully.")
            else:
                messages.warning(
                    request, "No valid employes IDs provided for deletion."
                )
        except Exception as e:
            messages.error(request, f"Error deleting employes: {e}")
        return redirect("hr_app:employee")

def delete_customer_session(request):
    del request.session['first_name']
    del request.session['last_name']
    del request.session['phone_number']
    del request.session['email']
    del request.session['postcode']
    del request.session['street_name']
    del request.session['house_name']
    del request.session['city']
    del request.session['county']
    del request.session['country']
    del request.session['campaign']
    del request.session['client']
