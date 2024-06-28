from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

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

def add_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists!')
            return redirect('app:admin') 
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password') 
        dashboard = request.POST.get('dashboard') == 'on'
        customer = request.POST.get('customer') == 'on'
        client = request.POST.get('client') == 'on'
        stage = request.POST.get('stage') == 'on'
        product = request.POST.get('product') == 'on'
        council = request.POST.get('council') == 'on'
        funding_route = request.POST.get('funding_route') == 'on'
        admin = request.POST.get('admin') == 'on'
        finance = request.POST.get('finance') == 'on'
        hr = request.POST.get('hr') == 'on'
        hashed_password = make_password(password) 
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password= hashed_password,
            dashboard=dashboard,
            customer=customer,
            client=client,
            council=council,
            stage=stage,
            product=product,
            funding_route=funding_route,
            admin=admin,
            finance=finance,
            hr=hr
        )
        messages.success(request, 'User added successfully!')
        return redirect('app:admin')  # Redirect to the appropriate URL

    return render(request, 'your_template.html')

def edit_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        print(request.POST)
        user.email = request.POST.get('email')
        if request.POST.get('password'):
            user.password = make_password(request.POST.get('password'))
        user.dashboard = request.POST.get('dashboard') == 'on'
        user.customer = request.POST.get('customer') == 'on'
        user.client = request.POST.get('client') == 'on'
        user.council = request.POST.get('council') == 'on'
        user.stage = request.POST.get('stage') == 'on'
        user.product = request.POST.get('product') == 'on'
        user.funding_route = request.POST.get('funding_route') == 'on'
        user.admin = request.POST.get('admin') == 'on'
        user.finance = request.POST.get('finance') == 'on'
        user.hr = request.POST.get('hr') == 'on'
        # user.set_password(user.password)
        user.save()

        messages.success(request, 'User updated successfully!')
        return redirect('app:admin')  # Redirect to the appropriate URL

    context = {'user': user}
    return redirect('app:adminview')

def remove_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.is_superuser:
        messages.error(request, 'SuperUser cannot be deleted!')
        return redirect('app:admin')
    user.delete()

    messages.success(request, 'User deleted successfully!')
    return redirect('app:admin')