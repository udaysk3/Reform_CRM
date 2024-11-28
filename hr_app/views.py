from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from datetime import datetime
import pytz
from user.models import User
from security_app.models import Role
from .models import Employee, Emergency_contact
from django.db.models.functions import Lower


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
def job_info(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    return render(request, "home/job_info.html", {'emp':emp})

@login_required
def time_off(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    return render(request, "home/time_off.html", {'emp':emp})

@login_required
def courses(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    return render(request, "home/courses.html", {'emp':emp})

def add_employee(request):
    roles = Role.objects.all()
    users = User.objects.all().filter(is_employee=False, is_client=False)
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        if User.objects.annotate(lower_email=Lower('email')).filter(Lower_email=email).exists():
            messages.error(request, 'Agent with this email already exists!')
            return redirect('admin_app:admin') 
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        employee_image = request.FILES.get('profile')
        hashed_password = make_password('123') 
        emp = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password= hashed_password,
            role=role,
            is_employee=True,
        )
        employee = Employee.objects.create(
            user=emp,
            reporting_to=User.objects.get(pk=request.POST.get('reporting_to')),
            phone_number=request.POST.get('phone'),
            work_setup=request.POST.get('work_setup'),
            employee_image=employee_image,
            data_of_joining=datetime.now(pytz.timezone("Europe/London")),
        )
        employee.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Employee added',
            agent=request.user,
        )

        messages.success(request, 'Agnet added successfully!')
        return redirect('hr_app:employee')
    return render(request, 'home/add_employee.html', {'roles':roles, 'users':users})

def edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    roles = Role.objects.all()
    users = User.objects.all().filter(is_employee=False, is_client=False)
    if request.method == 'POST':
        if request.POST.get('password'):
            emp.password = make_password(request.POST.get('password'))
        if emp.role != request.POST.get('role'):
            emp.approved = ''
        emp.employee_user.employee_image = request.FILES.get('profile')
        emp.first_name = request.POST.get('first_name')
        emp.last_name = request.POST.get('last_name')
        emp.role = request.POST.get('role')
        emp.employee_user.reporting_to = User.objects.get(pk=request.POST.get('reporting_to'))
        emp.employee_user.phone_number = request.POST.get('phone')
        emp.employee_user.work_setup = request.POST.get('work_setup')
        emp.save()
        emp.employee_user.save()

        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Employee updated',
            agent=request.user,
        )

        messages.success(request, 'Employee Details updated successfully!')
        return redirect('/emp_profile/'+str(emp_id))  

    return render(request, 'home/edit_employee.html', {'emp':emp, 'roles':roles, 'users':users,})

def add_emergency_contact(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        phno = request.POST.get('phno')
        email = request.POST.get('email').lower()
        emergency_contact = Emergency_contact.objects.create(
            name=name,
            phone=phno,
            email=email,
            employee=emp.employee_user,
        )
        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Emergency Contact added',
            agent=request.user,
        )

        messages.success(request, 'Emergency contact added successfully!')
        return redirect('/emp_profile/'+str(emp_id))  

    return render(request, 'home/add_emergency_contact.html', {'emp':emp})

def edit_emergency_contact(request, contact_id):
    contact = Emergency_contact.objects.get(pk=contact_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        phno = request.POST.get('phno')
        email = request.POST.get('email').lower()
        contact.name = name
        contact.phone = phno
        contact.email = email
        contact.save()
        contact.employee.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Emergency contact updated',
            agent=request.user,
        )

        messages.success(request, 'Emergency contact updated successfully!')
        return redirect('/emp_profile/'+str(contact.employee.user.id))  

    return render(request, 'home/edit_emergency_contact.html', {'contact':contact})

def edit_basic_information(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    if emp.employee_user.dob:
        emp_dob_formatted = emp.employee_user.dob.strftime('%Y-%m-%d')
    else:
        emp_dob_formatted = ''
    if request.method == 'POST':
        emp.first_name = request.POST.get('first_name')
        emp.last_name = request.POST.get('last_name')
        emp.employee_user.gender = request.POST.get('gender')
        emp.employee_user.religion = request.POST.get('religion')
        emp.employee_user.nationality = request.POST.get('nationality')
        emp.employee_user.dob = request.POST.get('dob')
        emp.employee_user.personal_email = request.POST.get('personal_email').lower()
        emp.employee_user.personal_phon = request.POST.get('personal_phon')
        emp.employee_user.city = request.POST.get('city')
        emp.employee_user.region = request.POST.get('region')
        emp.employee_user.country = request.POST.get('country')
        emp.employee_user.postal_code = request.POST.get('postal_code')
        emp.save()
        emp.employee_user.save()

        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Basic Information updated',
            agent=request.user,
        )

        messages.success(request, 'Basic Information updated successfully!')
        return redirect('/emp_profile/'+str(emp_id))  

    return render(request, 'home/edit_basic_information.html', {'emp':emp, 'emp_dob':emp_dob_formatted,})

def edit_job_detail(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    if request.method == 'POST':
        emp.employee_user.designation = request.POST.get('designation')
        emp.employee_user.employee_type = request.POST.get('employee_type')
        emp.employee_user.qualification = request.POST.get('qualifications')
        emp.employee_user.tenure = request.POST.get('tenure')
        emp.employee_user.save()

        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Job Detail updated',
            agent=request.user,
        )

        messages.success(request, 'Job Detail updated successfully!')
        return redirect('/job_info/'+str(emp_id))  

    return render(request, 'home/edit_job_details.html', {'emp':emp,})

def edit_employment_status(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    if emp.employee_user.onboarding:
        emp_onboarding_formatted = emp.employee_user.onboarding.strftime('%Y-%m-%d')
        print(emp_onboarding_formatted)
    else:
        emp_onboarding_formatted = ''
    if emp.employee_user.probation:
        emp_probation_formatted = emp.employee_user.probation.strftime('%Y-%m-%d')
    else:
        emp_probation_formatted = ''
    if emp.employee_user.regularised:
        emp_regularised_formatted = emp.employee_user.regularised.strftime('%Y-%m-%d')
    else:
        emp_regularised_formatted = ''
    if request.method == 'POST':
        emp.employee_user.onboarding = request.POST.get('onboarding')
        emp.employee_user.probation = request.POST.get('probation')
        emp.employee_user.regularised = request.POST.get('regularised')
        emp.employee_user.save()

        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type='Employment Status updated',
            agent=request.user,
        )

        messages.success(request, 'Employment Status updated successfully!')
        return redirect('/emp_profile/'+str(emp_id))  

    return render(request, 'home/edit_employment_status.html', {'emp':emp, 'emp_onboarding':emp_onboarding_formatted, 'emp_probation':emp_probation_formatted, 'emp_regularised':emp_regularised_formatted,})

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