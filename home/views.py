from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "home/index.html")

@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")

@login_required
def Customer(request):
    return render(request, "home/customer.html")

@login_required
def Admin(request):
    return render(request, "home/admin.html")


@login_required
def Finance(request):
    return render(request, "home/finance.html")

@login_required
def HR(request):
    return render(request, "home/HR.html")


