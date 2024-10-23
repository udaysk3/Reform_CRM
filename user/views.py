from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import datetime

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        # Check if the user exists
        if not User.objects.filter(email=email).exists():
            messages.error(request,"User doesn't exist.")
            return render(request, 'user/login.html', {'message': "User doesn't exist. Please sign up"})
        
        user = User.objects.get(email=email)
        
        authenticated_user = authenticate(email=email, password=password)
        if authenticated_user is not None:
                # Check the password using check_password
                if check_password(password, authenticated_user.password):
                    request.session['email'] = email
                    request.session.save()
                    login(request, authenticated_user)
                    user.last_login = datetime.datetime.now()
                    messages.success(request, 'Login Successful')
                    return redirect('/dashboard')

        messages.error(request,'Incorrect email or password')
        return render(request, 'user/login.html', {'message': 'Incorrect email or password'})
    
    return render(request, 'user/login.html')

def logout_view(request):
    if request.session.get('email',''):
        del request.session['email']
    request.session.save()
    logout(request)
    messages.success(request,'Logout Successful')
    return redirect('user:login')

def add_employee(request):
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
        messages.success(request, 'Agnet added successfully!')
        return redirect('hr_app:employee')

    return render(request, 'your_template.html')

def edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
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

        messages.success(request, 'User updated successfully!')
        return redirect('hr_app:employee')  # Redirect to the appropriate URL

    return redirect('hr_app:employee')

def remove_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.is_superuser:
        messages.error(request, 'SuperUser cannot be deleted!')
        return redirect('admin_app:admin')
    user.delete()

    messages.success(request, 'User deleted successfully!')
    return redirect('admin_app:admin')