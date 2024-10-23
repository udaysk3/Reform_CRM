from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import User
from .models import Role
from django.contrib.auth.hashers import make_password


@login_required
def s_employee(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.all().filter(is_employee=True).filter(is_archive=False)
    return render(request, "home/s_employee.html", {'emps':employes})

@login_required
def role(request):
    roles = Role.objects.all()
    return render(request, 'home/role.html', {'roles':roles})

def add_role(request):
    if request.method == 'POST':
        name = request.POST.get('role')
        dashboard = request.POST.get('dashboard') == 'on'
        customer = request.POST.get('customer') == 'on'
        client = request.POST.get('client') == 'on'
        council = request.POST.get('council') == 'on'
        admin = request.POST.get('admin') == 'on'
        product = request.POST.get('product') == 'on'
        globals = request.POST.get('global') == 'on'
        finance = request.POST.get('finance') == 'on'
        hr = request.POST.get('hr') == 'on'
        security = request.POST.get('security') == 'on'
        Role.objects.create(
            name=name,
            dashboard=dashboard,
            customer=customer,
            client=client,
            council=council,
            admin=admin,
            product=product,
            globals=globals,
            finance=finance,
            hr=hr,
            security=security
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
    return render(request, 'home/s_edit_employee.html', {'emp':emp})

def approve_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'approve'
    role = Role.objects.get(name=emp.role)
    emp.dashboard = role.dashboard
    emp.customer = role.customer
    emp.client = role.client
    emp.council = role.council
    emp.admin = role.admin
    emp.globals = role.globals
    emp.finance = role.finance
    emp.hr = role.hr
    emp.security = role.security
    emp.save()
    messages.success(request, 'Role approved successfully!')
    return redirect('security_app:s_employee')

def deny_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'deny'
    emp.save()
    messages.success(request, 'Role denied successfully!')
    return redirect('security_app:s_employee')

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