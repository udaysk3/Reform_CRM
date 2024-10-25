from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from user.models import User
from .models import Role
from django.contrib.auth.hashers import make_password

@login_required
def s_employee(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.filter(is_employee=True, is_archive=False)
    return render(request, "home/s_employee.html", {'emps': employes})

@login_required
def role(request):
    roles = Role.objects.all()
    return render(request, 'home/role.html', {'roles': roles})

def add_role(request):
    if request.method == 'POST':
        name = request.POST.get('role')
        dashboard = request.POST.get('dashboard') == 'on'
        mcustomer = request.POST.get('mcustomer') == 'on'
        customer = request.POST.get('customer') == 'on'
        client = request.POST.get('client') == 'on'
        council = request.POST.get('council') == 'on'
        admin = request.POST.get('admin') == 'on'
        product = request.POST.get('product') == 'on'
        globals = request.POST.get('global') == 'on'
        finance = request.POST.get('finance') == 'on'
        hr = request.POST.get('hr') == 'on'
        security = request.POST.get('security') == 'on'
        funding_route = request.POST.get('funding_route') == 'on'
        CJ = request.POST.get('CJ') == 'on'
        QA = request.POST.get('QA') == 'on'
        h_dashboard = request.POST.get('h_dashboard') == 'on'
        h_employee = request.POST.get('h_employee') == 'on'
        h_application = request.POST.get('h_application') == 'on'
        h_onboarding = request.POST.get('h_onboarding') == 'on'
        h_timesheet = request.POST.get('h_timesheet') == 'on'
        h_emp_action = request.POST.get('h_emp_action') == 'on'
        h_emp_notify = request.POST.get('h_emp_notify') == 'on'
        h_offboarding = request.POST.get('h_offboarding') == 'on'
        h_org_chart = request.POST.get('h_org_chart') == 'on'
        knowledge_base = request.POST.get('knowledge_base') == 'on'
        s_employee = request.POST.get('s_employee') == 'on'
        s_role = request.POST.get('s_role') == 'on'
        s_client = request.POST.get('s_client') == 'on'

        Role.objects.create(
            name=name,
            dashboard=dashboard,
            mcustomer=mcustomer,
            client=client,
            council=council,
            admin=admin,
            product=product,
            globals=globals,
            finance=finance,
            hr=hr,
            security=security,
            funding_route=funding_route,
            CJ=CJ,
            QA=QA,
            customer=customer,
            h_dashboard=h_dashboard,
            h_employee=h_employee,
            h_application=h_application,
            h_onboarding=h_onboarding,
            h_timesheet=h_timesheet,
            h_emp_action=h_emp_action,
            h_emp_notify=h_emp_notify,
            h_offboarding=h_offboarding,
            h_org_chart=h_org_chart,
            knowledge_base=knowledge_base,
            s_employee=s_employee,
            s_role=s_role,
            s_client=s_client
        )
        return redirect('security_app:role')
    return render(request, 'home/add_role.html')

@login_required
def s_edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    if request.method == 'POST':
        if request.POST.get('password'):
            emp.password = make_password(request.POST.get('password'))
        emp.status = request.POST.get('status') == 'on'
        emp.save()
        return redirect('security_app:s_employee')
    return render(request, 'home/s_edit_employee.html', {'emp': emp})

def approve_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'approve'
    role = Role.objects.get(name=emp.role)
    emp.dashboard = role.dashboard
    emp.mcustomer = role.mcustomer
    emp.customer = role.customer
    emp.client = role.client
    emp.council = role.council
    emp.admin = role.admin
    emp.product = role.product
    emp.globals = role.globals
    emp.finance = role.finance
    emp.hr = role.hr
    emp.security = role.security
    emp.funding_route = role.funding_route
    emp.CJ = role.CJ
    emp.QA = role.QA
    emp.h_dashboard = role.h_dashboard
    emp.h_employee = role.h_employee
    emp.h_application = role.h_application
    emp.h_onboarding = role.h_onboarding
    emp.h_timesheet = role.h_timesheet
    emp.h_emp_action = role.h_emp_action
    emp.h_emp_notify = role.h_emp_notify
    emp.h_offboarding = role.h_offboarding
    emp.h_org_chart = role.h_org_chart
    emp.knowledge_base = role.knowledge_base
    emp.s_employee = role.s_employee
    emp.s_role = role.s_role
    emp.s_client = role.s_client
    emp.save()
    messages.success(request, 'Role approved successfully!')
    return redirect('security_app:s_employee')

def deny_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'deny'
    emp.save()
    messages.success(request, 'Role denied successfully!')
    return redirect('security_app:s_employee')

def change_otp_mail(request, emp_id):
    emp = get_object_or_404(User, pk=emp_id)
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            if User.objects.filter(email=new_email).exists():
                messages.error(request, 'This email is already in use!')
                return redirect('security_app:s_employee')
            emp.email = new_email
            emp.save()
            messages.success(request, 'OTP mail changed successfully!')
        else:
            messages.error(request, 'Email cannot be empty.')
    return redirect('security_app:s_employee')

def edit_role(request, role_id):
    role = Role.objects.get(pk=role_id)
    if request.method == 'POST':
        role.name = request.POST.get('role')
        role.dashboard = request.POST.get('dashboard') == 'on'
        role.mcustomer = request.POST.get('mcustomer') == 'on'
        role.customer = request.POST.get('customer') == 'on'
        role.client = request.POST.get('client') == 'on'
        role.council = request.POST.get('council') == 'on'
        role.admin = request.POST.get('admin') == 'on'
        role.product = request.POST.get('product') == 'on'
        role.globals = request.POST.get('global') == 'on'
        role.finance = request.POST.get('finance') == 'on'
        role.hr = request.POST.get('hr') == 'on'
        role.security = request.POST.get('security') == 'on'
        role.funding_route = request.POST.get('funding_route') == 'on'
        role.CJ = request.POST.get('CJ') == 'on'
        role.QA = request.POST.get('QA') == 'on'
        role.h_dashboard = request.POST.get('h_dashboard') == 'on'
        role.h_employee = request.POST.get('h_employee') == 'on'
        role.h_application = request.POST.get('h_application') == 'on'
        role.h_onboarding = request.POST.get('h_onboarding') == 'on'
        role.h_timesheet = request.POST.get('h_timesheet') == 'on'
        role.h_emp_action = request.POST.get('h_emp_action') == 'on'
        role.h_emp_notify = request.POST.get('h_emp_notify') == 'on'
        role.h_offboarding = request.POST.get('h_offboarding') == 'on'
        role.h_org_chart = request.POST.get('h_org_chart') == 'on'
        role.knowledge_base = request.POST.get('knowledge_base') == 'on'
        role.s_employee = request.POST.get('s_employee') == 'on'
        role.s_role = request.POST.get('s_role') == 'on'
        role.s_client = request.POST.get('s_client') == 'on'
        role.save()
        return redirect('security_app:role')
    return render(request, 'home/edit_role.html', {'role': role})

def bulk_delete_roles(request):
    if request.method == "GET":
        role_ids_str = request.GET.get("ids", "")
        try:
            role_ids = [int(id) for id in role_ids_str.split(",") if id.isdigit()]
            if role_ids:
                Role.objects.filter(id__in=role_ids).delete()
                messages.success(request, "Selected roles deleted successfully.")
            else:
                messages.warning(request, "No valid role IDs provided for deletion.")
        except Exception as e:
            messages.error(request, f"Error deleting roles: {e}")
        return redirect("security_app:role")

def delete_customer_session(request):
    keys_to_delete = [
        'first_name', 'last_name', 'phone_number', 'email', 'postcode',
        'street_name', 'house_name', 'city', 'county', 'country',
        'campaign', 'client'
    ]
    for key in keys_to_delete:
        request.session.pop(key, None)
