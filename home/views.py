from django.contrib.auth.decorators import login_required
from user.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customers
from datetime import datetime 

def home(request):
    return render(request, "home/index.html")

@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")

@login_required
def customer_detail(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    return render(request,"home/customer-detail.html",{'customer': customer})

@login_required
def Customer(request):
    if request.GET.get('page') == 'edit_customer':
        customer_id = request.GET.get('id')
        customer = Customers.objects.get(pk=customer_id)
        return render(request, 'home/customer.html', {'customer': customer})
    customers = Customers.objects.all()
    return render(request, "home/customer.html", {"customers":customers})

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

@login_required
def add_customer(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        home_owner = request.POST.get('home_owner')
        address = request.POST.get('address')

        customer = Customers.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            home_owner=home_owner,
            address=address
        )

        messages.success(request, 'Customer added successfully!')
        return redirect('app:customer')

    return render(request, 'home/customer.html')

@login_required
def edit_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == 'POST':
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.phone_number = request.POST.get('phone_number')
        customer.email = request.POST.get('email')
        customer.home_owner = request.POST.get('home_owner')
        customer.address = request.POST.get('address')

        customer.save()

        messages.success(request, 'Customer updated successfully!')
        return redirect('app:customer')

    context = {'customer': customer}
    return render(request, 'home/customer.html', context)

@login_required
def remove_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.delete()

    messages.success(request, 'Customer deleted successfully!')
    return redirect('app:customer')


def action_submit(request, customer_id):
    if request.method == 'POST':
        customer = Customers.objects.get(id=customer_id)
        date_str = request.POST.get('date_field')
        time_str = request.POST.get('time_field')
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
        text = request.POST.get('text')
        customer.add_action(date_time, text)

        messages.success(request, 'Action added successfully!')
        return render(request, 'home/customer-detail.html', {'customer': customer})