from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django_otp.plugins.otp_email.models import EmailDevice

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Check if the user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User doesn't exist. Please sign up")
            return render(request, 'user/login.html', {'message': "User doesn't exist. Please sign up"})

        if user.is_employee:
            if user.status:
                pass
            else:
                messages.error(request, 'Employee is not active. Please contact admin')
                return render(request, 'user/login.html')

        # Authenticate the user
        authenticated_user = authenticate(email=email, password=password)
        if authenticated_user is not None and check_password(password, authenticated_user.password):
            # Authentication passed, now send OTP via email
            request.session['email'] = email  # Store email in session for OTP verification

            device, created = EmailDevice.objects.get_or_create(user=authenticated_user)
            device.generate_challenge()  # Send OTP email

            return redirect('user:verify_otp')  # Redirect to OTP verification

        else:
            messages.error(request, 'Incorrect email or password')
            return render(request, 'user/login.html', {'message': 'Incorrect email or password'})

    return render(request, 'user/login.html')

def verify_otp(request):
    """Handle OTP verification"""
    if request.method == 'POST':
        email = request.session.get('email')
        otp = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Session expired. Please login again.')
            return redirect('user:login')

        # Fetch the email-based device for the user
        device = EmailDevice.objects.get(user=user)

        # Verify the entered OTP
        if device.verify_token(otp):
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('/dashboard')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'user/verify_otp.html')

    return render(request, 'user/verify_otp.html')

def logout_view(request):
    """Logout view"""
    if request.session.get('email'):
        del request.session['email']
    request.session.save()
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('user:login')

def remove_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.is_superuser:
        messages.error(request, 'SuperUser cannot be deleted!')
        return redirect('admin_app:admin')
    user.delete()

    messages.success(request, 'User deleted successfully!')
    return redirect('admin_app:admin')