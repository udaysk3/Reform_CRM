from django.contrib.auth.decorators import login_required
from user.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customers, Client, Campaign, Councils, Route
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
import pandas as pd
import requests
from django.db.models import Max
import pytz
from user.models import User
from pytz import timezone
london_tz = pytz.timezone('Europe/London')
from datetime import datetime
from .tasks import getLA
from .epc import getEPC

def home(request):
    return render(request, "home/index.html")


@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")


@login_required
def customer_detail(request, customer_id):
    all_customers = Customers.objects.all().filter(parent_customer=None)
    customer = Customers.objects.get(pk=customer_id)
    child_customers= Customers.objects.all().filter(parent_customer=customer)
    
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
            if i.created_at.replace(tzinfo=london_tz).date() not in imported:
                imported[i.created_at.replace(tzinfo=london_tz).date()] = []
        else:
            if i.created_at.replace(tzinfo=london_tz).date() not in history:
                history[i.created_at.replace(tzinfo=london_tz).date()] = []
    for i in actions:
        if i.imported:
            imported[i.created_at.replace(tzinfo=london_tz).date()].append(
            [i.created_at.replace(tzinfo=london_tz).time(), i.text, i.agent.first_name, i.agent.last_name, i.imported, i.talked_with]
        )
        else:
            history[i.created_at.replace(tzinfo=london_tz).date()].append(
            [i.created_at.replace(tzinfo=london_tz).time(), i.text, i.agent.first_name, i.agent.last_name, i.imported, i.talked_with]
        )

    # routes = Route.objects.all().filter(customer=customer)


    return render(
        request,
        "home/customer-detail.html",
        {
            "customer": customer,
            "history": history,
            "imported": imported,
            "prev": prev,
            "next": next,
            "child_customers": child_customers,
            # "routes": routes,
        },
    )

@login_required
def council_detail(request, council_id):
    all_councils = Councils.objects.all()
    council = Councils.objects.get(pk=council_id)

    prev = None
    next = None
    if len(all_councils) == 1:
        prev = council
        next = council
    else:
        for i in range(len(all_councils)):
            if all_councils[i].id == council_id:
                if i == 0:
                    prev = all_councils[len(all_councils) - 1]
                    next = all_councils[i + 1]
                elif i == len(all_councils) - 1:
                    prev = all_councils[i - 1]
                    next = all_councils[0]
                else:
                    prev = all_councils[i - 1]
                    next = all_councils[i + 1]

    history = {}
    actions = council.get_created_at_council_action_history()
    london_tz = timezone('Europe/London')

    for i in actions:
        if i.created_at.replace(tzinfo=london_tz).date() not in history:
            history[i.created_at.replace(tzinfo=london_tz).date()] = []

    for i in actions:
        history[i.created_at.replace(tzinfo=london_tz).date()].append(
            [i.created_at.replace(tzinfo=london_tz).time(), i.text, i.agent.first_name, i.agent.last_name, i.imported, i.talked_with]
        )
    # routes = Route.objects.all().filter(funding_route=funding_route)


    return render(
        request,
        "home/council-detail.html",
        {
            "council": council,
            "history": history,
            "prev": prev,
            "next": next,
            # "routes": routes,
        },
    )


@login_required
def Customer(request):
    if request.GET.get("page") == "edit_customer" and request.GET.get("backto") is None:
        customer_id = request.GET.get("id")
        customer = Customers.objects.get(pk=customer_id)
        return render(request, "home/customer.html", {"customer": customer})
    
    # customers = Customers.objects.annotate(num_actions=Count('action')).order_by('-num_actions', 'action__date_time').distinct()
    customers = Customers.objects.annotate(
        earliest_action_date=Max("action__date_time")
    ).filter(parent_customer=None).order_by("earliest_action_date")
    # for customer in customers:
    #     print(customer.get_action_history())
    campaigns = Campaign.objects.all()


    return render(request, "home/customer.html", {"customers": customers, "campaigns": campaigns})


@login_required
def council(request):
    if request.GET.get("page") == "edit_council" and request.GET.get("backto") is None:
        council_id = request.GET.get("id")
        council = Councils.objects.get(pk=council_id)
        return render(request, "home/council.html", {"council": council})

    # councils = Councils.objects.annotate(
    #     earliest_action_date=Max("action__date_time")
    # ).order_by("earliest_action_date")

    councils = Councils.objects.all().order_by('name')

    campaigns = Campaign.objects.all()

    # for i in councils:
        # print(i)
    return render(request, "home/council.html", {"councils": councils, "campaigns": campaigns})


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
        last_name = request.POST.get("last_name").upper()
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        postcode = request.POST.get("postcode")
        address = request.POST.get("address")
        house_name = request.POST.get("house_name")
        city = request.POST.get("city")
        county = request.POST.get("county")
        country = request.POST.get("country")
        campaign = request.POST.get("campaign")
        agent = User.objects.get(email=request.user)

        if campaign == 'nan':
            messages.error(request, "Select a Campaign")
            return redirect("app:customer")

        if phone_number[0] == '0':
            phone_number = phone_number[1:]
            phone_number = '+44' + phone_number          
        elif phone_number[0] == '+':
            phone_number = phone_number
        else:
            phone_number = '+44' + phone_number
        # url = "https://api.postcodes.io/postcodes/" + postcode.strip()
        # try:
        #     response = requests.get(url, headers={'muteHttpExceptions': 'true'})

        #     if response.status_code == 200:
        #         json_data = response.json()
        #         status = json_data.get('status')
        #         if status == 200:
        #             district = json_data['result']['admin_district']
        #         else:
        #             district = "Invalid postcode or not found"
        #     else:
        #         district = "Error fetching data"
        # except requests.exceptions.RequestException as e:
        #     district = f"Request Error"
        district = getLA(postcode)
        if not Councils.objects.filter(name=district).exists():
            Councils.objects.create(name=district)
        obj = getEPC(postcode, house_name) 
        energy_rating = None 
        energy_certificate_link = None
        if obj is not None:
            energy_rating = obj['energy_rating']
            energy_certificate_link = obj['energy_certificate_link']
        customer = Customers.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            postcode=postcode,
            address=address,
            city=city,
            house_name=house_name,
            county=county,
            country=country,
            agent = agent,
            district=district,
            campaign = Campaign.objects.get(id=campaign),
            client = Campaign.objects.get(id=campaign).client,
            created_at = datetime.now(pytz.timezone('Europe/London')),
            primary_customer= True,
            energy_rating=energy_rating,
            energy_certificate_link=energy_certificate_link
        )
        messages.success(request, "Customer added successfully!")
        return redirect("app:customer")
    return render(request, "home/customer.html")


# def add_funding_route(request):
#     try:
#         response = requests.get("https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/georef-united-kingdom-local-authority-district/records?select=lad_name&limit=-1")
#         if response.status_code == 200:
#             json_data = response.json()
#             for data in json_data['results']:
#                 name = data['lad_name'][0]
#                 funding_route = FundingRoutes.objects.create(name=name)
#         else:
#             district = "Error fetching data"
#     except requests.exceptions.RequestException as e:
#         district = f"Request Error"
#     messages.success(request, "funding_routes added successfully!")
#     return redirect("app:funding_route")


@login_required
def edit_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == "POST":
        customer.first_name = request.POST.get("first_name")
        customer.last_name = request.POST.get("last_name").upper()
        customer.phone_number = request.POST.get("phone_number")
        customer.email = request.POST.get("email")
        customer.postcode = request.POST.get("postcode")
        customer.address = request.POST.get("address")
        customer.city = request.POST.get("city")
        customer.house_name = request.POST.get("house_name")
        customer.county = request.POST.get("county")
        customer.country = request.POST.get("country")
        customer.save()

        messages.success(request, "Customer updated successfully!")
        return redirect("app:customer")

    context = {"customer": customer}
    return render(request, "home/customer.html", context)


@login_required
def edit_council(request, council_id):
    council = Councils.objects.get(pk=council_id)
    if request.method == "POST":
        council.name = request.POST.get("name")
        # council.phone_number = request.POST.get("phone_number")
        # council.email = request.POST.get("email")
        # council.postcode = request.POST.get("postcode")
        # council.address = request.POST.get("address")


        council.save()

        messages.success(request, "Council updated successfully!")
        return redirect("app:council")

    context = {"council": council}
    return render(request, "home/council.html", context)


@login_required
def remove_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.delete()

    messages.success(request, "Customer deleted successfully!")
    return redirect("app:customer")


@login_required
def remove_council(request, council_id):
    council = Councils.objects.get(pk=council_id)
    council.delete()

    messages.success(request, "council deleted successfully!")
    return redirect("app:council")


def action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = request.POST.get("date_field")
        talked_with = request.POST.get("talked_customer")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")

        if talked_with == 'nan':
            messages.error(request, 'Customer field should be mapped')
            return redirect(f"/customer-detail/{customer_id}")

        customer.add_action(
            text,
            User.objects.get(email=request.user),
            date_time,
            False,
            datetime.now(pytz.timezone('Europe/London')),
            talked_with=talked_with,
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))

def council_action_submit(request, council_id):
    if request.method == "POST":
        council = Councils.objects.get(id=council_id)
        date_str = request.POST.get("date_field")
        talked_with = request.POST.get("talked_customer")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")

        if talked_with == 'nan':
            messages.error(request, 'council field should be mapped')
            return redirect(f"/council-detail/{council_id}")

        council.add_council_action(
            text,
            User.objects.get(email=request.user),
            date_time,
            False,
            datetime.now(pytz.timezone('Europe/London')),
            talked_with=talked_with,
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/council-detail/" + str(council_id))


def na_council_action_submit(request, council_id):
    if request.method == "POST":
        council = Councils.objects.get(id=council_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=20)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = "NA"

        council.add_council_action(
            text,
            User.objects.get(email=request.user),
            date_time,
            created_at=datetime.now(pytz.timezone('Europe/London')),
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/council-detail/" + str(council_id))

def na_action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
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
            created_at=datetime.now(pytz.timezone('Europe/London')),
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
        campaign = request.POST.get("campaign")
        if campaign == 'nan':
            messages.error(request, "Select a Campaign")
            return redirect("app:import_customers")
        df = pd.read_excel(excel_file)
        excel_columns = df.columns.tolist()
        column_mappings = []
        for i, column in enumerate(excel_columns):
            # Retrieve user's selection for each column
            attribute = request.POST.get(f"column{i}", "")
            column_mappings.append(attribute)

        if 'email' and 'first_name' and 'last_name' and 'phone_number'  not in column_mappings:
            messages.error(request, 'First Name, Last Name, Phone Number and  Email fields should be mapped')
            return redirect("app:import_customers")
            

        for index, row in df.iterrows():
            district = None
            customer_data = {}
            for i, column in enumerate(excel_columns):
                if column_mappings[i]== 'history':
                    history[excel_columns[i]] = str(row[i])
                elif column_mappings[i]== 'last_name':
                    customer_data[column_mappings[i]] = str(row[i]).upper()
                elif column_mappings[i]== 'phone_number':
                    phone_number = str(row[i])
                    if phone_number[0] == '0':
                        phone_number = phone_number[1:]
                        phone_number = '+44' + phone_number
                    elif phone_number[0] == '+':
                        phone_number = phone_number
                    else:
                        phone_number = '+44' + phone_number
                    customer_data[column_mappings[i]] = phone_number
                elif column_mappings[i] == 'postcode':
                    postcode = str(row[i])
                    url = "https://api.postcodes.io/postcodes/" + postcode.strip()
                    try:
                        response = requests.get(url, headers={'muteHttpExceptions': 'true'})

                        if response.status_code == 200:
                            json_data = response.json()
                            status = json_data.get('status')
                            if status == 200:
                                district = json_data['result']['admin_district']
                            else:
                                district = "Invalid postcode or not found"
                        else:
                            district = "Error fetching data"
                    except requests.exceptions.RequestException as e:
                        district = f"Request Error"
                    customer_data[column_mappings[i]] = postcode
                else :
                    customer_data[column_mappings[i]] = str(row[i])
            
            customer = Customers.objects.create(**customer_data,district=district,campaign = Campaign.objects.get(id=campaign), client = Campaign.objects.get(id=campaign).client, agent=User.objects.get(email=request.user),created_at=datetime.now(pytz.timezone('Europe/London')))
            customer.primary_customer = True

            customer.save()
            for i in history:
                customer.add_action(f'{i} : {history[i]}', User.objects.get(email=request.user), imported=True, created_at=datetime.now(pytz.timezone('Europe/London')))
        messages.success(request, "Customers imported successfully.")
        return redirect("app:customer")
    
    campaigns = Campaign.objects.all()

    return render(request, "home/import_customers.html", {"excel_columns": excel_columns ,"campaigns": campaigns})


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
        name = request.POST.get('name')
        telephone = request.POST.get('telephone')
        main_contact = request.POST.get('main_contact')
        email = request.POST.get('email')
        client = Client.objects.create(
            name=name,
            main_contact=main_contact,
            email=email,
            telephone=telephone,
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
        client.name = request.POST.get('name')
        client.main_contact= request.POST.get('main_contact')
        client.telephone= request.POST.get('telephone')
        client.email= request.POST.get('email')
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

def add_child_customer(request, customer_id):
    if request.method == 'POST':
        parent_customer = Customers.objects.get(pk=customer_id)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name').upper()
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        if parent_customer.primary_customer:
            parent_customer.primary_customer = False
            parent_customer.save()
        else:
            primaryc = Customers.objects.all().filter(parent_customer=parent_customer)
            for i in primaryc:
                if i.primary_customer:
                    i.primary_customer = False
                    i.save()
        child_customer = Customers.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            postcode=parent_customer.postcode,
            house_name=parent_customer.house_name,
            address=parent_customer.address,
            city=parent_customer.city,
            county=parent_customer.county,
            country=parent_customer.country,
            agent = parent_customer.agent,
            district=parent_customer.district,
            campaign = Campaign.objects.get(id=parent_customer.campaign.id),
            client = Campaign.objects.get(id=parent_customer.campaign.id).client,
            created_at = datetime.now(pytz.timezone('Europe/London')),
            parent_customer= parent_customer,
            primary_customer = True,
        )
        messages.success(request, "Customer added successfully!")
        return redirect(f"/customer-detail/{customer_id}")

def make_primary(request, parent_customer_id, child_customer_id):
    parent_customer = Customers.objects.get(pk=parent_customer_id)
    child_customer = Customers.objects.get(pk=child_customer_id)
    if parent_customer.primary_customer:
       parent_customer.primary_customer = False
       parent_customer.save()
    else:
       primaryc = Customers.objects.all().filter(parent_customer=parent_customer)
       for i in primaryc:
           if i.primary_customer:
               i.primary_customer = False
               i.save()
    child_customer.primary_customer = True
    child_customer.save()
    messages.success(request, "Customer made primary successfully!")
    return redirect(f"/customer-detail/{parent_customer_id}")

# def add_funding_route(request,customer_id):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         telephone = request.POST.get('telephone')
#         main_contact = request.POST.get('main_contact')
#         email = request.POST.get('email')
#         another_contact = request.POST.get('another_contact')
#         customer = Customers.objects.get(pk=customer_id)
#         route = Route.objects.create(
#             name=name,
#             telephone=telephone,
#             main_contact=main_contact,
#             email=email,
#             another_contact=another_contact,
#             customer=customer,
#         )
#         messages.success(request, 'Funding Route added successfully!')
#         return redirect(f'/customer-detail/{customer_id}')  
#     return render(request, 'admin.html')


def add_funding_route(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        telephone = request.POST.get('telephone')
        main_contact = request.POST.get('main_contact')
        email = request.POST.get('email')
        another_contact = request.POST.get('another_contact')
        council = Councils.objects.get(name=request.POST.get('council'))
        route = Route.objects.create(
            name=name,
            telephone=telephone,
            main_contact=main_contact,
            email=email,
            another_contact=another_contact,
        )
        messages.success(request, 'Funding Route added successfully!')
        return redirect(f'/councils')  
    return render(request, 'admin.html')

