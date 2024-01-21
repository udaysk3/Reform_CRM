from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user.models import User

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
    if request.GET.get('page') == 'edit':
        user_id = request.GET.get('id')
        user = User.objects.get(pk=user_id)
        return render(request, 'home/admin.html', {'user': user})
    users = User.objects.filter(is_superuser=False).values()
    return render(request, "home/admin.html", {"users":users})


@login_required
def Finance(request):
    return render(request, "home/finance.html")

@login_required
def HR(request):
    return render(request, "home/hr.html")


