from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages


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
            if authenticated_user.is_active:
                request.session['email'] = email
                request.session.save()
                login(request, authenticated_user)
                messages.success(request,'Login Successful')
                return redirect('/dashboard')
        messages.error(request,'Incorrect email or password')
        return render(request, 'user/login.html', {'message': 'Incorrect email or password'})
    
    return render(request, 'user/login.html')

def logout_view(request):
    
    del request.session['email']
    request.session.save()
    logout(request)
    messages.success(request,'Logout Successful')
    return redirect('user:login')
