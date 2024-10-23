from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import User

@login_required
def s_employee(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.all().filter(is_employee=True).filter(is_archive=False)
    return render(request, "home/s_employee.html", {'emps':employes})

@login_required
def s_edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    return render(request, 'home/s_edit_employee.html', {'emp':emp})

def approve_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'approve'
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