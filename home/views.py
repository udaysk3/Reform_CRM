from hmac import new
from django.contrib.auth.decorators import login_required
from user.models import User
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cities, Customers, Client, Campaign, Councils, Route, Stage, Document, Cities, Email, Reason, HistoryId, Countys, Countries
import re
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, HttpResponse
import pandas as pd
import requests
import csv
from django.db.models import Max, BooleanField, Case, When
import pytz
from user.models import User
from pytz import timezone
import json
import numpy as np
import os
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
london_tz = pytz.timezone("Europe/London")
from datetime import datetime
from .tasks import getLA
from .epc import getEPC
from simplegmail import Gmail
from simplegmail.query import construct_query
import base64 
import quopri
import requests
import os.path
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def home(request):
    return render(request, "home/index.html")


@login_required
def dashboard(request):
    all_customers = (
        Customers.objects.annotate(earliest_action_date=Max("action__created_at"))
        .filter(parent_customer=None)
        .order_by("earliest_action_date")
    )
    user  = User.objects.get(email=request.user)
    a_customers = (
        Customers.objects.all()
        .filter(assigned_to=user)
        .annotate(earliest_action_date=Max("action__date_time"))
        .filter(parent_customer=None)
        .order_by("earliest_action_date")
    )
    
    customers = (
        Customers.objects.all()
        .filter(assigned_to=user)
        .annotate(earliest_action_date=Max("action__date_time"))
        .filter(parent_customer=None)
        .filter(closed=False)
        .order_by("earliest_action_date")
    )

    customers = list(customers)
    new_customers = []
    for customer in customers:
        actions = customer.get_created_at_action_history()
        flag = False
        for action in actions:
            if action.imported == False:
                new_customers.append(customer)
                break
            
    new_customers.sort(key=lambda x: x.get_created_at_action_history()[0].date_time)
    result = [x for x in customers if x not in new_customers] 
    customers= new_customers + result
    na=[]
    lm=[]
    cb=[]
    sms=[]
    email=[]
    history = {}
    imported = {}
    london_tz = timezone("Europe/London")
    for customer in a_customers:
        user = User.objects.get(email=request.user)
        actions = customer.get_created_at_action_history().filter(agent=user)
        for i in actions:
            if i.action_type == 'NA':
                print(i.action_type == 'NA')
                na.append(i)
            elif i.action_type == 'LM':
                lm.append(i)
            elif i.action_type == 'CB':
                cb.append(i)
            elif i.action_type == 'SMS':
                sms.append(i)
            elif i.action_type == 'EMAIL':
                email.append(i)
            
            
            if i.imported:
                if i.created_at.replace(tzinfo=london_tz).date() not in imported:
                    imported[i.created_at.replace(tzinfo=london_tz).date()] = []
            else:
                if i.created_at.replace(tzinfo=london_tz).date() not in history:
                    history[i.created_at.replace(tzinfo=london_tz).date()] = []
        for i in actions:
            if i.imported:
                imported[i.created_at.replace(tzinfo=london_tz).date()].append(
                    [
                        i.created_at.replace(tzinfo=london_tz).time(),
                        i.text,
                        i.agent.first_name,
                        i.agent.last_name,
                        i.imported,
                        i.talked_with,
                        i.customer.postcode,
                        i.customer.house_name,
                        i.customer.id
                    ]
                )
            else:
                history[i.created_at.replace(tzinfo=london_tz).date()].append(
                    [
                        i.created_at.replace(tzinfo=london_tz).time(),
                        i.customer.postcode,
                        i.customer.house_name,
                        i.agent.first_name,
                        i.agent.last_name,
                        i.action_type,
                        i.date_time,
                        i.talked_with,
                        i.text,
                        i.customer.id,
                    ]
                )

    campaigns = Campaign.objects.all()
    unassigned_customers = Customers.objects.filter(assigned_to=None)
    agents = User.objects.filter(is_superuser=False)
    
    p_customers = Paginator(customers, 50)
    page_number = request.GET.get('page')
    try:
        page_obj = p_customers.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p_customers.page(1)
    except EmptyPage:
        page_obj = p_customers.page(p_customers.num_pages)
        
    
    return render(request, "home/dashboard.html", {"customers": customers, "all_customers": all_customers, "current_date": datetime.now(london_tz).date, "campaigns": campaigns, "history": history, "imported": imported,"agents": serialize('json', agents),'na':len(na), 'lm':len(lm), 'cb':len(cb), 'sms':len(sms), 'email':len(email), 'page_obj':page_obj})


@login_required
def customer_detail(request, customer_id, s_customer_id=None):
    all_customers = []
    prev = None
    next = None
    if request.GET.get('previous') == 'dashboard':
        all_customers = Customers.objects.all().filter(parent_customer=None).filter(assigned_to= User.objects.get(email=request.user))
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
        prev = str(prev.id) + '?previous=dashboard'
        next = str(next.id) + '?previous=dashboard'
    else:
        customers = (
            Customers.objects.annotate(earliest_action_date=Max("action__date_time"))
            .filter(parent_customer=None)
            .filter(closed=False)
            .order_by("earliest_action_date")
        )

        customers = list(customers)
        new_customers = []
        for customer in customers:
            actions = customer.get_created_at_action_history()
            flag = False
            for action in actions:
                if action.imported == False:
                    new_customers.append(customer)
                    break
                
        new_customers.sort(key=lambda x: x.get_created_at_action_history()[0].date_time)


        result = [x for x in customers if x not in new_customers] 

        customers= new_customers + result
        if len(customers) == 1:
            prev = customer
            next = customer
        else:
            for i in range(len(customers)):
                if customers[i].id == customer_id:
                    if i == 0:
                        prev = customers[i]
                        next = customers[i + 1]
                    elif i == len(customers) - 1:
                        prev = customers[i - 1]
                        next = customers[i]
                    else:
                        prev = customers[i - 1]
                        next = customers[i + 1]
        if prev:
            prev = str(prev.id)
        else:
            prev = str(customer_id)   
        if next:     
            next = str(next.id)
        else:
            next = str(customer_id)
    print(type(prev), next)
    customer = Customers.objects.get(pk=customer_id)
    child_customers = Customers.objects.all().filter(parent_customer=customer)
    agents = User.objects.filter(is_superuser=False)
    show_customer = customer
    reasons = Reason.objects.all()
    templates = Email.objects.all()
    if s_customer_id:
        show_customer = Customers.objects.get(pk=s_customer_id)

    history = {}
    actions = customer.get_created_at_action_history()
    imported = {}
    london_tz = timezone("Europe/London")
    keyevents = customer.get_created_at_action_history().filter(keyevents=True)
    events = {}

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
                [
                    i.created_at.replace(tzinfo=london_tz).time(),
                    i.text,
                    i.agent.first_name,
                    i.agent.last_name,
                    i.imported,
                    i.talked_with,
                    i.customer.postcode,
                    i.customer.house_name,
                ]
            )
        else:
            history[i.created_at.replace(tzinfo=london_tz).date()].append(
                [
                    i.created_at.replace(tzinfo=london_tz).time(),
                    i.customer.postcode,
                    i.customer.house_name,
                    i.agent.first_name,
                    i.agent.last_name,
                    i.action_type,
                    i.date_time,
                    i.talked_with,
                    i.text,
                ]
            )

    for i in keyevents:
        if i.created_at.replace(tzinfo=london_tz).date() not in events:
            events[i.created_at.replace(tzinfo=london_tz).date()] = []
    for i in keyevents:
        events[i.created_at.replace(tzinfo=london_tz).date()].append(
                [
                    i.created_at.replace(tzinfo=london_tz).time(),
                    i.customer.postcode,
                    i.customer.house_name,
                    i.agent.first_name,
                    i.agent.last_name,
                    i.action_type,
                    i.date_time,
                    i.talked_with,
                    i.text
                ]
            )


    if customer.district:
        council= Councils.objects.get_or_create(name=customer.district)[0]
    else:
        council = None
    routes = Route.objects.all().filter(council=council)
    recommendations_list = []
    if customer.recommendations:
        recommendations_list = [
            item.strip() for item in customer.recommendations.split("<br>")
        ]
    processed_recommendations = []
    for recommendation in recommendations_list:
        improvement, indicative_cost = recommendation.split(", £(")
        processed_recommendations.append(
            {"improvement": improvement, "indicative_cost": indicative_cost[:-1]}
        )
    if customer.route:
        all_stages = customer.route.stage.all()
        stages = {}
        for stage in all_stages:
            stages[stage.name] = json.loads(stage.fields)
        if customer.stage_values:
            stage_values = json.loads(customer.stage_values)
            values = {}
            for name,s_fields in stages.items():
                fields = {}
                for field in s_fields:
                    fields[field] = [s_fields[field], '']
                values[name] = fields
            
            for key, fields in values.items():
                if key in stage_values:
                    for field in fields:
                        if field in stage_values[key]:
                            fields[field][1] = stage_values[key][field]

            
            # print(stage_values, values)
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
            "recommendations_list": processed_recommendations,
            "routes": routes,
            "stages": stages,
            "values": values,
            "agents": agents,
            "show_customer": show_customer,
            "events": events,
            "reasons": reasons,
            "templates": templates,
        },
    )
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
            "recommendations_list": processed_recommendations,
            "routes": routes,
            "stages": stages,
            "agents" : agents,
            "show_customer": show_customer,
            "events": events,
            "reasons": reasons,
            "templates": templates,
        },
    )

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
            "recommendations_list": processed_recommendations,
            "routes": routes,
            "agents" : agents,
            "show_customer": show_customer,
            "events": events,
            "reasons": reasons,
            "templates": templates,
        },
    )


@login_required
def council_detail(request, council_id):
    all_councils = Councils.objects.all()
    council = Councils.objects.get(pk=council_id)
    routes = Route.objects.all()
    c_routes = Route.objects.all().filter(council=council)    
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
    london_tz = timezone("Europe/London")

    for i in actions:
        if i.created_at.replace(tzinfo=london_tz).date() not in history:
            history[i.created_at.replace(tzinfo=london_tz).date()] = []

    for i in actions:
        history[i.created_at.replace(tzinfo=london_tz).date()].append(
            [
                i.created_at.replace(tzinfo=london_tz).time(),
                i.text,
                i.agent.first_name,
                i.agent.last_name,
                i.imported,
                i.talked_with,
                i.customer.postcode,
                i.customer.house_name,
            ]
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
            "routes": routes,
            "c_routes" : c_routes,
        },
    )


@login_required
def Customer(request):
    if request.GET.get("page") == "edit_customer" and request.GET.get("backto") is None:
        customer_id = request.GET.get("id")
        customer = Customers.objects.get(pk=customer_id)
        if customer.parent_customer:
            edit_customer = customer
            customer = Customers.objects.get(pk=customer.parent_customer.id)
            customers = Customers.objects.all().filter(parent_customer=customer)
            return render(
                request,
                "home/customer.html",
                {
                    "edit_customer": edit_customer,
                    "customer": customer,
                    "customers": customers,
                },
            )
        edit_customer = customer
        customers = Customers.objects.all().filter(parent_customer=customer)
        return render(
            request,
            "home/customer.html",
            {
                "edit_customer": edit_customer,
                "customer": customer,
                "customers": customers,
            },
        )
    

    # customers = Customers.objects.annotate(num_actions=Count('action')).order_by('-num_actions', 'action__date_time').distinct()
    current_time = datetime.now(london_tz)
    user  = User.objects.get(email=request.user)
    customers = (
        Customers.objects.annotate(earliest_action_date=Max("action__date_time"))
        .filter(parent_customer=None)
        .filter(closed=False)
        .order_by("earliest_action_date")
    )

    customers = list(customers)
    new_customers = []
    for customer in customers:
        actions = customer.get_created_at_action_history()
        flag = False
        for action in actions:
            if action.imported == False:
                new_customers.append(customer)
                break
            
    new_customers.sort(key=lambda x: x.get_created_at_action_history()[0].date_time)


    result = [x for x in customers if x not in new_customers] 

    customers= new_customers + result
    print(type(customers))
    customers = customers[::-1]
    campaigns = Campaign.objects.all()
    unassigned_customers = Customers.objects.filter(assigned_to=None)
    agents = User.objects.filter(is_superuser=False)
    p_customers = Paginator(customers, 50)
    page_number = request.GET.get('page')
    try:
        page_obj = p_customers.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p_customers.page(1)
    except EmptyPage:
        page_obj = p_customers.page(p_customers.num_pages)
        
    return render(
        request, "home/customer.html", {"customers": p_customers, "current_date": datetime.now(london_tz).date, "campaigns": campaigns,"agents": serialize('json', agents), 'page_obj': page_obj}
    )

@login_required
def archive(request):
    customers = (
        Customers.objects.annotate(earliest_action_date=Max("action__date_time"))
        .filter(parent_customer=None)
        .filter(closed=True)
        .order_by("earliest_action_date")
    )

    customers = list(customers)
    new_customers = []
    for customer in customers:
        actions = customer.get_created_at_action_history()
        flag = False
        for action in actions:
            if action.imported == False:
                new_customers.append(customer)
                break
            
    new_customers.sort(key=lambda x: x.get_created_at_action_history()[0].date_time)


    result = [x for x in customers if x not in new_customers] 


    # for customer in customers:
    #     print(customer.get_action_history())
    customers= new_customers + result
    campaigns = Campaign.objects.all()
    unassigned_customers = Customers.objects.filter(assigned_to=None)
    agents = User.objects.filter(is_superuser=False)
    return render(
        request, "home/archive.html", {"customers": customers, "current_date": datetime.now(london_tz).date, "campaigns": campaigns,"agents": serialize('json', agents)}
    )



@login_required
def council(request):
    if request.GET.get("page") == "edit_council" and request.GET.get("backto") is None:
        council_id = request.GET.get("id")
        council = Councils.objects.get(pk=council_id)
        return render(request, "home/council.html", {"council": council})

    # councils = Councils.objects.annotate(
    #     earliest_action_date=Max("action__date_time")
    # ).order_by("earliest_action_date")

    councils = Councils.objects.all().order_by("name")

    campaigns = Campaign.objects.all()

    # for i in councils:
    # print(i)
    return render(
        request, "home/council.html", {"councils": councils, "campaigns": campaigns}
    )


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
    if request.GET.get("page") == "edit_template":
        email_id = request.GET.get("id")
        email = Email.objects.get(pk=email_id)
        return render(request, "home/admin.html", {"email": email})
    if request.GET.get("page") == "edit_reason":
        reason_id = request.GET.get("id")
        reason = Reason.objects.get(pk=reason_id)
        return render(request, "home/admin.html", {"reason": reason})
    users = User.objects.filter(is_superuser=False).values()
    clients = Client.objects.filter()
    emails = Email.objects.all()
    reasons = Reason.objects.all()
    return render(request, "home/admin.html", {"users": users, "clients": clients, "emails": emails, "reasons": reasons})


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
        street_name = request.POST.get("street_name")
        house_name = request.POST.get("house_name")
        city = request.POST.get("city")
        county = request.POST.get("county")
        country = request.POST.get("country")
        campaign = request.POST.get("campaign")
        agent = User.objects.get(email=request.user)

        if campaign == "nan" or city == "nan" or county == "nan" or country == "nan":
            messages.error(request, "Select all dropdown fields")
            return redirect("/customer?page=add_customer")

        if phone_number[0] == "0":
            phone_number = phone_number[1:]
            phone_number = "+44" + phone_number
        elif phone_number[0] == "+":
            phone_number = phone_number
        else:
            phone_number = "+44" + phone_number
        postcode = re.sub(r'\s+', ' ', postcode)
        district = getLA(postcode)
        if district and not Councils.objects.filter(name=district).exists():
            Councils.objects.create(name=district)
        obj = getEPC(postcode, house_name, street_name)
        energy_rating = None
        energy_certificate_link = None
        address = house_name + " " + street_name
        constituency = None
        if obj is not None:
            energy_rating = obj["energy_rating"]
            energy_certificate_link = obj["energy_certificate_link"]
            county = obj["county"] if obj["county"] else county
            district = obj["local_authority"] if obj["local_authority"] else district
            city = obj["town"] if obj["town"] else city
            constituency = obj["constituency"] if obj["constituency"] else None
            address = (
                obj["address"] if obj["address"] else house_name + " " + street_name
            )
            recommendations = obj["recommendations"] if obj["recommendations"] else None
        customer = Customers.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            postcode=postcode,
            street_name=street_name,
            city=city,
            house_name=house_name,
            address=address,
            county=county,
            country=country,
            agent=agent,
            district=district,
            constituency=constituency,
            campaign=Campaign.objects.get(id=campaign),
            client=Campaign.objects.get(id=campaign).client,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            primary_customer=True,
            energy_rating=energy_rating,
            energy_certificate_link=energy_certificate_link,
            recommendations=recommendations,
        )
        customer.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Added {customer.first_name} {customer.last_name}  {customer.house_name } {customer.phone_number} {customer.email} {customer.house_name} {customer.street_name} {customer.city} {customer.county} {customer.country}",
                keyevents=True,
        )
        messages.success(request, "Customer added successfully!")
        return redirect("app:customer")
    return render(request, "home/customer.html")


@login_required
def edit_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == "POST":
        changed = ''
        if customer.phone_number != request.POST.get("phone_number"):
            changed += f'{request.POST.get("phone_number")}'
        if customer.email != request.POST.get('email'):
            changed += f'{request.POST.get("email")}'
        if customer.postcode != request.POST.get("postcode"):
            changed += f'{request.POST.get("postcode")}'
        if customer.street_name != request.POST.get("street_name"):
            changed += f'{request.POST.get("street_name")}'
        if customer.city != request.POST.get("city"):
            changed += f'{request.POST.get("city")}'
        if customer.house_name != request.POST.get("house_name"):
            changed += f'{request.POST.get("house_name")}'
        if customer.county != request.POST.get("county"):
            changed += f'{request.POST.get("county")}'
        if customer.country != request.POST.get("country"):
            changed += f'{request.POST.get("country")}'

        customer.first_name = request.POST.get("first_name")
        customer.last_name = request.POST.get("last_name").upper()
        customer.phone_number = request.POST.get("phone_number")
        customer.email = request.POST.get("email")
        customer.postcode = re.sub(r'\s+', ' ', request.POST.get("postcode"))
        customer.street_name = request.POST.get("street_name")
        customer.city = request.POST.get("city")
        customer.house_name = request.POST.get("house_name")
        customer.county = request.POST.get("county")
        customer.country = request.POST.get("country")
        print(request.POST.get("county"),request.POST.get("country"))
        if customer.campaign == "nan" or customer.city == "nan" or customer.county == "nan" or customer.country == "nan":
            messages.error(request, "Select all dropdown fields")
            return redirect(f"/customer?page=edit_customer&id={customer_id}")
        
        district = getLA(customer.postcode)
        if district and not Councils.objects.filter(name=district).exists():
            Councils.objects.create(name=district)
        obj = getEPC(customer.postcode, customer.house_name, customer.street_name)
        energy_rating = None
        energy_certificate_link = None
        address = customer.house_name + " " + customer.street_name
        constituency = None
        if obj is not None:
            energy_rating = obj["energy_rating"]
            energy_certificate_link = obj["energy_certificate_link"]
            county = obj["county"] if obj["county"] else customer.county
            district = obj["local_authority"] if obj["local_authority"] else customer.district
            city = obj["town"] if obj["town"] else customer.city
            constituency = obj["constituency"] if obj["constituency"] else None
            address = (
                obj["address"] if obj["address"] else customer.house_name + " " + customer.street_name
            )
            recommendations = obj["recommendations"] if obj["recommendations"] else None
        customer.energy_rating = energy_rating
        customer.energy_certificate_link = energy_certificate_link
        customer.address = address
        customer.constituency = constituency
        customer.recommendations = recommendations
        if district:
            customer.district = district
        customer.save()
        customer.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=f"Updated {customer.first_name} {customer.last_name} - " + changed,
            keyevents=True,
        )
        messages.success(request, "Customer updated successfully!")
        if customer.parent_customer:
            customer.parent_customer.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Updated {customer.parent_customer.firt_name} {customer.parent_customer.last_name} - " + changed,
                keyevents=True,
            )
            return redirect(f"/customer-detail/{customer.parent_customer.id}")

        return redirect(f"/customer-detail/{customer_id}")

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
        # council.street_name = request.POST.get("street_name")

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
        talked_with = request.POST.get("talked_customer")
        date_str = request.POST.get("date_field")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")

        if talked_with == "nan":
            messages.error(request, "Customer field should be mapped")
            return redirect(f"/customer-detail/{customer_id}")

        customer.add_action(
            text=text,
            agent=User.objects.get(email=request.user),
            closed=False,
            imported=False,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            talked_with=talked_with,
            date_time=date_time,
            action_type="CB",
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))

def close_action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        talked_with = request.POST.get("talked_customer")
        reason = request.POST.get("reason")
        text = request.POST.get("text")
        action_type = ''
        c_text = ''
        closed = False
        
        c_text = f'{reason} - {text}'

        if reason == 'nan':
            c_text = text
        
        if text == '':
            c_text = reason
            
        if customer.closed:
            c_text = text
        

        if customer.closed:
            action_type = f"Reopened"
            closed = False
            try:
                customer = Customers.objects.get(pk=customer_id)
                customer.assigned_to =  User.objects.get(pk=reason)
                customer.save()
                customer.add_action(
                    agent=User.objects.get(email=request.user),
                    date_time=datetime.now(pytz.timezone("Europe/London")),
                    created_at=datetime.now(pytz.timezone("Europe/London")),
                    action_type="Assigned to Agent",
                )
            except Exception as e:
                messages.error(request, f"Error assigning customer: {e}")
                return HttpResponseRedirect("/customer-detail/" + str(customer_id))
        else:
            action_type = f"Closed"
            closed = True

        if talked_with == "nan":
            messages.error(request, "Customer field should be mapped")
            return redirect(f"/customer-detail/{customer_id}")

        customer.add_action(
            text=c_text,
            closed=closed,
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            imported=False,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            talked_with=talked_with,
            action_type=action_type,
            keyevents=True,
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

        if talked_with == "nan":
            messages.error(request, "council field should be mapped")
            return redirect(f"/council-detail/{council_id}")

        council.add_council_action(
            text=text,
            agent=User.objects.get(email=request.user),
            imported=False,
            created_at=datetime.now(pytz.timezone("Europe/London")),
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
        time_obj += timedelta(minutes=60)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = "NA"

        council.add_council_action(
            date_time=date_time,
            text=text,
            agent=User.objects.get(email=request.user),
            imported=False,
            created_at=datetime.now(pytz.timezone("Europe/London")),
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/council-detail/" + str(council_id))


def na_action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=60)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

        customer.add_action(
            date_time=date_time,
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type="NA",
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))

def lm_action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=60)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

        customer.add_action(
            date_time=date_time,
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type="LM",
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))


def import_customers_view(request):
    excel_columns = []
    expected_columns = ["history"]
    history = {}
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        campaign = request.POST.get("campaign")
        if campaign == "nan":
            messages.error(request, "Select a Campaign")
            return redirect("app:import_customers")
        df = pd.read_excel(excel_file)
        excel_columns = df.columns.tolist()
        column_mappings = []
        for i, column in enumerate(excel_columns):
            # Retrieve user's selection for each column
            attribute = request.POST.get(f"column{i}", "")
            column_mappings.append(attribute)

        if (
            "email"
            and "first_name"
            and "last_name"
            and "phone_number" not in column_mappings
        ):
            messages.error(
                request,
                "First Name, Last Name, Phone Number and  Email fields should be mapped",
            )
            return redirect("app:import_customers")

        for index, row in df.iterrows():
            district = None
            customer_data = {}
            for i, column in enumerate(excel_columns):
                history[excel_columns[i]] = str(row[i])
                if column_mappings[i] == "history":
                    history[excel_columns[i]] = str(row[i])
                elif column_mappings[i] == "last_name":
                    customer_data[column_mappings[i]] = str(row[i]).upper()
                elif column_mappings[i] == "phone_number":
                    phone_number = str(row[i])
                    if phone_number[0] == "0":
                        phone_number = phone_number[1:]
                        phone_number = "+44" + phone_number
                    elif phone_number[0] == "+":
                        phone_number = phone_number
                    else:
                        phone_number = "+44" + phone_number
                    customer_data[column_mappings[i]] = phone_number
                elif column_mappings[i] == "postcode":
                    postcode = str(row[i])


                    url = "https://api.postcodes.io/postcodes/" + postcode.strip()
                    try:
                        response = requests.get(
                            url, headers={"muteHttpExceptions": "true"}
                        )

                        if response.status_code == 200:
                            json_data = response.json()
                            status = json_data.get("status")
                            if status == 200:
                                district = json_data["result"]["admin_district"]
                            else:
                                district = "Invalid postcode or not found"
                        else:
                            district = "Error fetching data"
                    except requests.exceptions.RequestException as e:
                        district = f"Request Error"
                    customer_data[column_mappings[i]] = re.sub(r'\s+', ' ', postcode)
                else:
                    customer_data[column_mappings[i]] = str(row[i])

            customer = Customers.objects.create(
                **customer_data,
                district=district,
                campaign=Campaign.objects.get(id=campaign),
                client=Campaign.objects.get(id=campaign).client,
                agent=User.objects.get(email=request.user),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                imported=True,
            )
            customer.primary_customer = True

            customer.save()
            for i in history:
                customer.add_action(
                    text=f"{i} : {history[i]}",
                    date_time=datetime.now(pytz.timezone("Europe/London")),
                    agent=User.objects.get(email=request.user),
                    closed=False,
                    imported=True,
                    created_at=datetime.now(pytz.timezone("Europe/London")),
                )
            customer.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Added {customer.first_name} {customer.last_name}  {customer.house_name } {customer.phone_number} {customer.email} {customer.house_name} {customer.street_name} {customer.city} {customer.county} {customer.country}",
                keyevents=True,
        )
        messages.success(request, "Customers imported successfully.")
        return redirect("app:customer")

    campaigns = Campaign.objects.all()

    return render(
        request,
        "home/import_customers.html",
        {"excel_columns": excel_columns, "campaigns": campaigns},
    )


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
    if request.method == "POST":
        # email = request.POST.get('email')
        # if Client.objects.filter(email=email).exists():
        #     messages.error(request, 'Client with this email already exists!')
        # return redirect('app:client')
        name = request.POST.get("name")
        telephone = request.POST.get("telephone")
        main_contact = request.POST.get("main_contact")
        email = request.POST.get("email")
        client = Client.objects.create(
            name=name,
            main_contact=main_contact,
            email=email,
            telephone=telephone,
        )
        messages.success(request, "Client added successfully!")
        return redirect("app:admin")
    return render(request, "admin.html")


def add_campaign(request):
    if request.method == "POST":
        name = request.POST.get("name")
        client_id = request.POST.get("client_id")
        if Campaign.objects.filter(name=name).exists():
            messages.error(request, "Campaign with this name already exists!")
            return redirect("app:admin")
        name = request.POST.get("name")
        campaign = Campaign.objects.create(
            client_id=client_id,
            name=name,
        )
        messages.success(request, "Campaign added successfully!")
        return redirect("app:admin")
    return render(request, "admin.html")


def edit_client(request, client_id):
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        client.name = request.POST.get("name")
        client.main_contact = request.POST.get("main_contact")
        client.telephone = request.POST.get("telephone")
        client.email = request.POST.get("email")
        client.save()
        messages.success(request, "Client updated successfully!")
        return redirect("app:admin")
    context = {"client": client}
    return redirect("app:adminview")


def remove_client(request, client_id):
    client = Client.objects.get(pk=client_id)
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to do this!")
        return redirect("app:admin")
    client.delete()
    messages.success(request, "Client deleted successfully!")
    return redirect("app:admin")


def remove_campaign(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    campaign.delete()
    messages.success(request, "Campaign deleted successfully!")
    return redirect("app:admin")


def add_child_customer(request, customer_id):
    if request.method == "POST":
        parent_customer = Customers.objects.get(pk=customer_id)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name").upper()
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
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
            street_name=parent_customer.street_name,
            city=parent_customer.city,
            county=parent_customer.county,
            country=parent_customer.country,
            agent=parent_customer.agent,
            district=parent_customer.district,
            campaign=Campaign.objects.get(id=parent_customer.campaign.id),
            client=Campaign.objects.get(id=parent_customer.campaign.id).client,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            parent_customer=parent_customer,
            primary_customer=True,
        )
        parent_customer.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=f"Added {child_customer.first_name} {child_customer.last_name} { child_customer.house_name } {child_customer.phone_number} {child_customer.email} {child_customer.house_name} {child_customer.street_name} {child_customer.city} {child_customer.county} {child_customer.country}",
            keyevents=True
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
    if parent_customer == child_customer:
        parent_customer.primary_customer = True
        parent_customer.save() 
    parent_customer.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=f"Made {child_customer.first_name} {child_customer.last_name} as Primary Contact",
        )    
    messages.success(request, "Customer made primary successfully!")
    return redirect(f"/customer-detail/{parent_customer_id}")


def add_funding_route(request):
    if request.method == "POST":
        name = request.POST.get("name")
        # managed_by = request.POST.get("managed_by")
        # main_contact = request.POST.get("main_contact")
        # email = request.POST.get("email")
        # telephone = request.POST.get("telephone")
        description = request.POST.get("description") 
        route = Route.objects.create(
            name=name,
            # managed_by=managed_by,
            # telephone=telephone,
            # main_contact=main_contact,
            # email=email,
            description=description,
        )
        documents = request.FILES.getlist("document")
        for document in documents:
            doc = Document.objects.create(document=document)
            route.documents.add(doc)
        route.save()
        messages.success(request, "Funding Route added successfully!")
        return redirect(f"/funding_route")
    return render(request, "admin.html")


def add_council_funding_route(request, council_id):
    if request.method == "POST":
        council = Councils.objects.get(pk=council_id)
        route = Route.objects.get(pk=request.POST.get("route"))
        route.council.add(council)
        route.save()
        messages.success(request, "Funding Route added successfully to a Council!")
        return redirect(f"/council-detail/{council_id}")


def edit_funding_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    if request.method == "POST":
        route.name = request.POST.get("name")
        # route.managed_by = request.POST.get("managed_by")
        # route.main_contact = request.POST.get("main_contact")
        # route.email = request.POST.get("email")
        # route.telephone = request.POST.get("telephone")
        route.description = request.POST.get("description")
        route.document = request.FILE.get("document")
        route.save()
        messages.success(request, "Route updated successfully!")
        return redirect("app:funding_route")

def remove_funding_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    route.delete()
    messages.success(request, "Route deleted successfully!")
    return redirect("app:funding_route")


@login_required
def create_stage(request, route_id):
    route = Route.objects.get(pk=route_id)
    stages=Stage.objects.all().filter(route=route)
    if request.GET.get("page")== 'edit_page':
        stage = Stage.objects.get(pk=request.GET.get("stage_id"))          
        return render(request, 'home/stages.html', {"route": route,"stage":stage, "fields":json.loads(stage.fields)})

    if request.method == "POST":
        dynamic_types = request.POST.getlist("dynamic_type")
        dynamic_labels = request.POST.getlist("dynamic_label")

        dynamic_fields = {}
        for label, field_type in zip(dynamic_labels, dynamic_types):
            dynamic_fields[label] = field_type
        fields = json.dumps(dynamic_fields)
        stage = Stage.objects.create(
            name=request.POST.get("name"),
            route=route,
            fields=fields,
        )
        return redirect(f"/{route_id}/stages") 
    return render(request, "home/stages.html", {"route": route, "stages": stages}) 

@login_required
def remove_stage(request, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    route_id = stage.route.id
    stage.delete()
    messages.success(request, "Stage deleted successfully!")
    return redirect(f"/{route_id}/stages")

@login_required
def edit_stage(request, route_id, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    if request.method == "POST":
        dynamic_types = request.POST.getlist("dynamic_type")
        dynamic_labels = request.POST.getlist("dynamic_label")
        dynamic_fields = {}
        for label, field_type in zip(dynamic_labels, dynamic_types):
            dynamic_fields[label] = field_type
        fields = json.dumps(dynamic_fields)
        stage.name = request.POST.get("name")
        stage.fields = fields
        stage.save()
        messages.success(request, "Stage updated successfully!")
        return redirect(f"/{route_id}/stages")

@login_required
def set_customer_route(request, customer_id, route_id):
    customer = Customers.objects.get(pk=customer_id)
    route = Route.objects.get(pk=route_id)
    customer.route = route
    customer.save()
    messages.success(request, "Route set successfully!")
    return redirect(f"/customer-detail/{customer_id}")

@login_required
def set_stage_values(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == 'POST':
        name = request.POST.get("name")
        dynamic_labels = request.POST.getlist("dynamic_label")
        dynamic_input = request.POST.getlist("dynamic_input")
        dynamic_fields = {}
        for label, field_type in zip(dynamic_labels, dynamic_input):
            dynamic_fields[label] = field_type
        values = {}
        if customer.stage_values:
            values = json.loads(customer.stage_values)
            values[name] = dynamic_fields
        else:
            values = {name:dynamic_fields}
        stage_values = json.dumps(values)
        customer.stage_values = stage_values
        customer.save()
        messages.success(request, f"{name} is set successfully!")
        return redirect(f"/customer-detail/{customer_id}")
    
@login_required
def funding_route(request):
    routes = Route.objects.all()
    return render(request, 'home/funding-route.html', {"routes": routes})

def remove_customer_route(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.route = None
    customer.save()
    messages.success(request, "Route removed successfully!")
    return redirect(f"/customer-detail/{customer_id}")

@login_required
def funding_route_detail(request, route_id):
    route = Route.objects.get(pk=route_id)
    documents = []
    for doc in route.documents.all():
        documents.append(doc.document)
    # print(documents)
    return render(request, 'home/funding-route_detail.html', {"route": route, "documents": documents})

from django.http import JsonResponse
from .models import Customers
from user.models import User
from googleapiclient.discovery import build

def assign_agents(request):
    if request.method == "POST":
     try:
        # Parse customers and agents from the POST request
        agent_ids = [int(id_str.split(' - ')[-1]) for id_str in request.POST.get("agents").split(',')]
        customers = request.POST.get("customers")
        customers = list(customers.split(','))
        if "All Unassigned Customers" in customers or " All Unassigned Customers" in customers:
            if "All Unassigned Customers" in customers:
                customers.remove("All Unassigned Customers")
            else:
                customers.remove(" All Unassigned Customers")
            customer_ids = Customers.objects.filter(assigned_to=None).values_list('id', flat=True)
            
            num_customers = len(customer_ids)
            num_agents = len(agent_ids)
            customers_per_agent = num_customers // num_agents
            extra_customers = num_customers % num_agents
            
            # Assign customers to agents
            agent_index = 0
            for agent_id in agent_ids:
                agent = User.objects.get(pk=agent_id)
                
                # Determine the number of customers to assign to this agent
                if extra_customers > 0:
                    num_customers_for_agent = customers_per_agent + 1
                    extra_customers -= 1
                else:
                    num_customers_for_agent = customers_per_agent
                
                # Assign customers to this agent
                assigned_customers = customer_ids[:num_customers_for_agent]
                Customers.objects.filter(id__in=assigned_customers).update(assigned_to=agent_id)
                customer_ids = customer_ids[num_customers_for_agent:]
                
                agent_index += 1
        if customers:
            c_agent_ids = []
            for agent_id in customers:
                c_agent_ids.append(int(agent_id.split(' - ')[-1]))
            customer_ids = []
            for agent_id in c_agent_ids:
                customer_ids.extend(list(Customers.objects.filter(assigned_to=agent_id).values_list('id', flat=True)))
            num_customers = len(customer_ids)
            num_agents = len(agent_ids)
            customers_per_agent = num_customers // num_agents
            extra_customers = num_customers % num_agents

            # Assign customers to agents
            agent_index = 0
            for agent_id in agent_ids:
                agent = User.objects.get(pk=agent_id)

                # Determine the number of customers to assign to this agent
                if extra_customers > 0:
                    num_customers_for_agent = customers_per_agent + 1
                    extra_customers -= 1
                else:
                    num_customers_for_agent = customers_per_agent

                # Assign customers to this agent
                assigned_customers = customer_ids[:num_customers_for_agent]
                Customers.objects.filter(id__in=assigned_customers).update(assigned_to=agent_id)
                customer_ids = customer_ids[num_customers_for_agent:]

                agent_index += 1


        
        messages.success(request, "Customers Assigned successfully!")
        return redirect("app:customer")
     except Exception as e:
        messages.error(request, f"Error assigning customers: {e}")
        return redirect("app:customer")
    else:
        messages.error(request, "Cannot Assign customers!")
        return redirect("app:customer")

def assign_agent(request):
    customer_id = request.POST.get("customer_id")
    agent_id = request.POST.get("agent_id")
    try:
        customer = Customers.objects.get(pk=customer_id)
        customer.assigned_to =  User.objects.get(pk=agent_id)
        customer.save()
        customer.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type="Assigned to Agent",
        )
        messages.success(request, "Agent Assigned successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))
    except Exception as e:
        messages.error(request, f"Error assigning customer: {e}")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))
    

def send_email(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    email_id = request.POST.get("template")
    date_str = request.POST.get("date_field")
    time_str = request.POST.get("time_field")
    date_time_str = f"{date_str} {time_str}"
    date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    body = ''
    subject = ''
    text = ''
    if email_id != 'nan':
        email  = Email.objects.get(pk=email_id)
        text = email.name
        body = email.body
        if customer.first_name:
            body = body.replace("{{first_name}}", customer.first_name)
        if customer.last_name:    
            body = body.replace("{{last_name}}", customer.last_name)
        if customer.phone_number:
            body = body.replace("{{phone_number}}", customer.phone_number)
        if customer.email:
            body = body.replace("{{email}}", customer.email)
        if customer.house_name:    
            body = body.replace("{{house_name}}", customer.house_name)
        if customer.street_name:
            body = body.replace("{{street_name}}", customer.street_name)
        if customer.city:
            body = body.replace("{{city}}", customer.city)
        if customer.county:
            body = body.replace("{{county}}", customer.county)
        if customer.country:
            body = body.replace("{{country}}", customer.country)
        if customer.postcode:
            body = body.replace("{{postcode}}", customer.postcode)
        subject = email.subject
    else:
        body = request.POST.get("text")
        text = request.POST.get("text")

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email='support@reform-group.uk',
        to=[customer.email],
    )

    email.send()
    if text == '':
        customer.add_action(
                agent=User.objects.get(email=request.user),
                closed=False,
                imported=False,
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type="Email Sent",
                date_time=datetime.now(pytz.timezone("Europe/London")),
            )
    else:
        customer.add_action(
                agent=User.objects.get(email=request.user),
                closed=False,
                imported=False,
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type="Email Sent",
                date_time=date_time,
                text= text,
            )

    messages.success(request, "Email sent successfully!")
    return HttpResponseRedirect("/customer-detail/" + str(customer_id))

def query_city(request, q):
    cities = Cities.objects.all()
    filters = []
    q = q.lower()
    for city in cities:
        if (q in city.name.lower()):
            filters.append(city)
    return JsonResponse([{'city':city.name} for city in filters], safe=False)

def query_county(request, q):
    countys = Countys.objects.all()
    filters = []
    q = q.lower()
    for county in countys:
        if (q in county.name.lower()):
            filters.append(county)
    return JsonResponse([{'county':county.name} for county in filters], safe=False)

def query_country(request, q):
    countries = Countries.objects.all()
    filters = []
    q = q.lower()
    for country in countries:
        if (q in country.name.lower()):
            filters.append(country)
    return JsonResponse([{'country':country.name} for country in filters], safe=False)

def add_template(request):
    if request.method == "POST":
        name = request.POST.get("name")
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        template = Email.objects.create(
            name=name,
            subject=subject,
            body=body,
        )
        messages.success(request, "Template added successfully!")
        return redirect("app:admin")
    return render(request, "home/admin.html")

def edit_template(request, template_id):
    template = Email.objects.get(pk=template_id)
    if request.method == "POST":
        template.name = request.POST.get("name")
        template.subject = request.POST.get("subject")
        template.body = request.POST.get("body")
        template.save()
        messages.success(request, "Template updated successfully!")
        return redirect("app:admin")
    return redirect("app:admin")

def remove_template(request, template_id):
    template = Email.objects.get(pk=template_id)
    template.delete()
    messages.success(request, "Template deleted successfully!")
    return redirect("app:admin")

def add_reason(request):
    if request.method == "POST":
        name = request.POST.get("name")
        reason = request.POST.get("reason")
        template = Reason.objects.create(
            name=name,
            reason=reason,
        )
        messages.success(request, "Reason added successfully!")
        return redirect("app:admin")
    return render(request, "home/admin.html")

def edit_reason(request, reason_id):
    reason = Reason.objects.get(pk=reason_id)
    if request.method == "POST":
        reason.name = request.POST.get("name")
        reason.reason = request.POST.get("reason")
        reason.save()
        messages.success(request, "Reason updated successfully!")
        return redirect("app:admin")
    return redirect("app:admin")

def remove_reason(request, reason_id):
    reason = Reason.objects.get(pk=reason_id)
    reason.delete()
    messages.success(request, "Reason deleted successfully!")
    return redirect("app:admin")

def get_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return part['body']['data']
            elif part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain':
                        return subpart['body']['data']
    else:
        if payload['mimeType'] == 'text/plain':
            return payload['body']['data']
    return None

def get_message(historyId,userId):
    historys = HistoryId.objects.all().order_by('-created_at')
    if historys:
        if os.path.exists("static/token.json"):
            creds = Credentials.from_authorized_user_file("static/token.json", SCOPES)
        if not creds or not creds.valid:
          if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
          else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "static/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=3000)
          with open("static/token.json", "w") as token:
            token.write(creds.to_json())

        try:
            messageids = {
                "ids": [],
            }
            historyId1 = historys[0].history_id
            gmail = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
            response = gmail.users().history().list(userId='me', startHistoryId=historyId1,historyTypes="messageAdded", labelId="UNREAD").execute()
            print('response', response)
            if 'history' in response:
                for history in response['history']:
                    if 'messagesAdded' in history:
                        for ids in history['messagesAdded']:
                            messageids["ids"].append(ids['message']['id'])
            
            messageids["ids"] = list(set(messageids["ids"]))
            for messageid in messageids["ids"]:
                
                message = gmail.users().messages().get(userId='me', id=messageid).execute()
                payload = message['payload']
                headers = payload['headers']
                from_header=''
                subject_header=''
                body=''
                for header in headers:
                    if header['name'] == 'From':
                        from_header = header['value']
                    if header['name'] == 'Subject':
                        subject_header = header['value']
                raw_body = get_body(message['payload']) if 'payload' in message else None
                if raw_body:
                    try:
                        body = base64.urlsafe_b64decode(raw_body).decode('utf-8')
                    except Exception as e:
                        body = f"Error decoding body: {e}"
                else:
                    body = "No body found"
                print(from_header, subject_header, body)
                if '<' in from_header:
                    from_header = from_header.split('<')[1].split('>')[0]
                customers = Customers.objects.all()
                customer = None
                for c_customer in customers:
                    if c_customer.email == from_header:
                        customer = c_customer
                        continue
                if customer:
                    actions = customer.get_created_at_action_history()
                    for action in actions:
                        if action.text == f'Subject: {subject_header} \n Body: {body}':
                            return HttpResponse(200)
                    customer.add_action(
                        date_time=datetime.now(pytz.timezone("Europe/London")),
                        created_at=datetime.now(pytz.timezone("Europe/London")),
                        action_type="Email Received",
                        agent=User.objects.get(email='admin@gmail.com'),
                        text=f'Subject: {subject_header} \n Body: {body}',
                    )
                else:
                    customer = Customers.objects.create(
                        first_name=from_header.split('@')[0],
                        email=from_header,
                    )
                    customer.add_action(
                        date_time=datetime.now(pytz.timezone("Europe/London")),
                        created_at=datetime.now(pytz.timezone("Europe/London")),
                        action_type=f"Added {customer.email}",
                        agent=User.objects.get(email='admin@gmail.com'),
                        keyevents=True,
                    )
                    customer.add_action(
                        date_time=datetime.now(pytz.timezone("Europe/London")),
                        created_at=datetime.now(pytz.timezone("Europe/London")),
                        action_type="Email Received",
                        agent=User.objects.get(email='admin@gmail.com'),
                        text=f'Subject: {subject_header} \n Body: {body}',
                    )
            
            
            history = HistoryId.objects.create(history_id=historyId, created_at=datetime.now(pytz.timezone("Europe/London")))
            
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")
        return HttpResponse(200)
    
    else:
        historys = HistoryId.objects.create(history_id=historyId, created_at=datetime.now(pytz.timezone("Europe/London")))
    return HttpResponse(200)
        
@csrf_exempt
def get_notifications(request):
    if request.method == "POST":
        base64_string =json.loads(request.body)["message"]["data"]
        base64_bytes = base64_string.encode("ascii") 
        sample_string_bytes = base64.b64decode(base64_bytes) 
        sample_string = sample_string_bytes.decode("ascii")
        print(sample_string, type(sample_string))
        history_data = json.loads(sample_string)
        historyId = history_data["historyId"]
        userId = history_data["emailAddress"]
        # print(request.body, historyId)
        get_message(historyId, userId)
    return HttpResponse(200)