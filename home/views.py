from django.contrib.auth.decorators import login_required
from user.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customers,Action, Client, Campaign
from datetime import datetime, timedelta
from datetime import date
from django.http import HttpResponseRedirect
import pandas as pd
from django.db.models import Max,Min
import pytz
from user.models import User
from pytz import timezone

utc = pytz.UTC


def home(request):
    return render(request, "home/index.html")


@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")


@login_required
def customer_detail(request, customer_id):
    all_customers = Customers.objects.all()
    customer = Customers.objects.get(pk=customer_id)
    prev = None
    next = None
    if len(all_customers) == 1:
        prev = customer
        next = customer
    else:
        for i in range(len(all_customers)):
            if all_customers[i].id == customer_id:
                if i == 0:
                    prev = all_customers[len(all_customers) - 1]
                    next = all_customers[i + 1]
                elif i == len(all_customers) - 1:
                    prev = all_customers[i - 1]
                    next = all_customers[0]
                else:
                    prev = all_customers[i - 1]
                    next = all_customers[i + 1]

    history = {}
    actions = customer.get_created_at_action_history()
    imported = {}
    london_tz = timezone('Europe/London')

    for i in actions:
        if i.imported:
            if i.added_date_time.replace(tzinfo=london_tz).date() not in imported:
                imported[i.added_date_time.replace(tzinfo=london_tz).date()] = []
        else:
            if i.added_date_time.replace(tzinfo=london_tz).date() not in history:
                history[i.added_date_time.replace(tzinfo=london_tz).date()] = []
    for i in actions:
        if i.imported:
            imported[i.added_date_time.replace(tzinfo=london_tz).date()].append(
            [i.added_date_time.replace(tzinfo=london_tz).time(), i.text, i.agent.first_name, i.agent.last_name, i.imported]
        )
        else:
            history[i.added_date_time.replace(tzinfo=london_tz).date()].append(
            [i.added_date_time.replace(tzinfo=london_tz).time(), i.text, i.agent.first_name, i.agent.last_name, i.imported]
        )
        print(i.imported)


    return render(
        request,
        "home/customer-detail.html",
        {
            "customer": customer,
            "history": history,
            "prev": prev,
            "next": next,
        },
    )


@login_required
def Customer(request):
    if request.GET.get("page") == "edit_customer":
        customer_id = request.GET.get("id")
        customer = Customers.objects.get(pk=customer_id)
        return render(request, "home/customer.html", {"customer": customer})
    # customers = Customers.objects.annotate(num_actions=Count('action')).order_by('-num_actions', 'action__date_time').distinct()
    customers = Customers.objects.annotate(
        earliest_action_date=Max("action__date_time")
    ).order_by("earliest_action_date")
    # for customer in customers:
    #     print(customer.get_action_history())

    return render(request, "home/customer.html", {"customers": customers})


@login_required
def Admin(request):
    if request.GET.get("page") == "edit":
        user_id = request.GET.get("id")
        user = User.objects.get(pk=user_id)
        return render(request, "home/admin.html", {"user": user})
    if request.GET.get("page") == "edit_client":
        client_id = request.GET.get("id")
        client = Client.objects.get(pk=client_id)
        return render(request, "home/admin.html", {"client": client})
    users = User.objects.filter(is_superuser=False).values()
    clients = Client.objects.filter()
    return render(request, "home/admin.html", {"users": users, "clients" : clients})


@login_required
def Finance(request):
    return render(request, "home/finance.html")


@login_required
def HR(request):
    return render(request, "home/hr.html")


@login_required
def add_customer(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        postcode = request.POST.get("postcode")
        address = request.POST.get("address")
        agent = User.objects.get(email=request.user)

        if phone_number[0] == '0':
            phone_number = phone_number[1:]
            phone_number = '+44' + phone_number
        elif phone_number[0] == '+' and (phone_number[1] != '4' or phone_number[2] != '4'):
            phone_number = phone_number[3:]
            phone_number = '+44' + phone_number            
        elif phone_number[0] == '+' and phone_number[1] == '4' and phone_number[1] == '4':
            phone_number = phone_number
        else:
            phone_number = '+44' + phone_number

        customer = Customers.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            postcode=postcode,
            address=address,
            agent = agent,
        )

        messages.success(request, "Customer added successfully!")
        return redirect("app:customer")

    return render(request, "home/customer.html")


@login_required
def edit_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == "POST":
        customer.first_name = request.POST.get("first_name")
        customer.last_name = request.POST.get("last_name")
        customer.phone_number = request.POST.get("phone_number")
        customer.email = request.POST.get("email")
        customer.postcode = request.POST.get("postcode")
        customer.address = request.POST.get("address")

        customer.save()

        messages.success(request, "Customer updated successfully!")
        return redirect("app:customer")

    context = {"customer": customer}
    return render(request, "home/customer.html", context)


@login_required
def remove_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.delete()

    messages.success(request, "Customer deleted successfully!")
    return redirect("app:customer")


def action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = request.POST.get("date_field")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")
        customer.add_action(
            text,
            User.objects.get(email=request.user),
            date_time,
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))


def na_action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=20)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = "NA"
        customer.add_action(
            text,
            User.objects.get(email=request.user),
            date_time,
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))


def import_customers_view(request):
    excel_columns = []
    expected_columns = [
        'history'
    ]
    history = {}
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        df = pd.read_excel(excel_file)
        excel_columns = df.columns.tolist()
        column_mappings = []
        for i, column in enumerate(excel_columns):
            # Retrieve user's selection for each column
            attribute = request.POST.get(f"column{i}", "")
            column_mappings.append(attribute)
        print(column_mappings)

        if 'email' and 'first_name' not in column_mappings:
            messages.error(request, 'First Name and Email fields should be mapped')
            return redirect("app:import_customers")
            

        for index, row in df.iterrows():
            customer_data = {}
            for i, column in enumerate(excel_columns):
                if column_mappings[i]== 'history':
                    history[excel_columns[i]] = row[i]
                else :
                    customer_data[column_mappings[i]] = row[i]
            
            customer = Customers.objects.create(**customer_data, agent=User.objects.get(email=request.user))
            for i in history:
                customer.add_action(f'{i} : {history[i]}', User.objects.get(email=request.user), imported=True)
        messages.success(request, "Customers imported successfully.")
        return redirect("app:customer")

    return render(request, "home/import_customers.html", {"excel_columns": excel_columns})


def bulk_remove_customers(request):
    if request.method == "GET":
        customer_ids_str = request.GET.get("ids", "")
        try:
            customer_ids = [
                int(id) for id in customer_ids_str.split(",") if id.isdigit()
            ]
            if customer_ids:
                Customers.objects.filter(id__in=customer_ids).delete()
                messages.success(request, "Selected customers deleted successfully.")
            else:
                messages.warning(
                    request, "No valid customer IDs provided for deletion."
                )
        except Exception as e:
            messages.error(request, f"Error deleting customers: {e}")
        return redirect("app:customer")
    return render(request, "home/customer_list.html")


def add_client(request):
    if request.method == 'POST':
        # email = request.POST.get('email')
        # if Client.objects.filter(email=email).exists():
        #     messages.error(request, 'Client with this email already exists!')
            # return redirect('app:client') 
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        client = Client.objects.create(
            first_name=first_name,
            last_name=last_name,
        )
        messages.success(request, 'Client added successfully!')
        return redirect('app:admin')  
    return render(request, 'admin.html')

def add_campaign(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        client_id = request.POST.get('client_id')
        if Campaign.objects.filter(name=name).exists():
            messages.error(request, 'Campaign with this name already exists!')
            return redirect('app:admin') 
        name = request.POST.get('name')
        campaign = Campaign.objects.create(
            client_id = client_id,
            name=name,
        )
        messages.success(request, 'Campaign added successfully!')
        return redirect('app:admin')  
    return render(request, 'admin.html')

def edit_client(request, client_id):
    client = Client.objects.get(pk=client_id)
    if request.method == 'POST':
        print(request.POST)
        client.first_name = request.POST.get('first_name')
        client.last_name = request.POST.get('last_name')
        client.save()
        messages.success(request, 'Client updated successfully!')
        return redirect('app:admin')  
    context = {'client': client}
    return redirect('app:adminview')

def remove_client(request, client_id):
    client = Client.objects.get(pk=client_id)
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to do this!")
        return redirect('app:admin')
    client.delete()
    messages.success(request, 'Client deleted successfully!')
    return redirect('app:admin')

def remove_campaign(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    campaign.delete()
    messages.success(request, 'Campaign deleted successfully!')
    return redirect('app:admin')