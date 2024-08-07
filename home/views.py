from django.contrib.auth.decorators import login_required
from user.models import User
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import ast
from .models import (
    Cities,
    Customers,
    Clients,
    Campaign,
    Councils,
    Route,
    Stage,
    Document,
    Cities,
    Email,
    Reason,
    HistoryId,
    Countys,
    Countries,
    Signature,
    Product,
    CoverageAreas,
    Questions,
    QAction,
    Stage,
)
import re
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, HttpResponse
import pandas as pd
import requests
from django.db.models import Max
import pytz
from user.models import User
from pytz import timezone
import json
import os
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
london_tz = pytz.timezone("Europe/London")
from datetime import datetime
from .tasks import getLA
from .epc import getEPC
import base64 
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
    if request.session.get("first_name"):
        delete_customer_session(request)
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
    date_wise_customers = {}
    brand_new_customers = []
    for i in customers:
        if i.get_created_at_action_history()[0].date_time.date() not in date_wise_customers:
            date_wise_customers[i.get_created_at_action_history()[0].date_time.date()] = []
        date_wise_customers[i.get_created_at_action_history()[0].date_time.date()].append(i)
    for key, values in date_wise_customers.items():
        cb_wise_customers = []
        values = values
        for i in values:
            if i.get_created_at_action_history()[0].action_type == 'CB':
                if cb_wise_customers and cb_wise_customers[0].get_created_at_action_history()[0].action_type == 'CB':
                    cb_wise_customers.insert(1, i) 
                else:
                    cb_wise_customers = [i] + cb_wise_customers
            else:
                cb_wise_customers = cb_wise_customers +[i]
        brand_new_customers += cb_wise_customers
    customers = brand_new_customers

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
                        i.created_at.astimezone(london_tz).time(),
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
                        i.created_at.astimezone(london_tz).time(),
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
    clients = Clients.objects.all()
    campaigns = Campaign.objects.all()
    all_customers = []
    prev = None
    next = None
    domain_name = request.build_absolute_uri("/")[:-1]
    signatures = Signature.objects.all()
    if request.GET.get('previous') == 'dashboard':
        user  = User.objects.get(email=request.user)
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
        all_customers= new_customers + result
        all_customers = all_customers[::-1]
        if len(all_customers) == 1:
            prev = customer
            next = customer
        else:
            for i in range(len(all_customers)):
                if all_customers[i].id == customer_id:
                    if i == 0:
                        prev = all_customers[i]
                        next = all_customers[i + 1]
                    elif i == len(all_customers) - 1:
                        prev = all_customers[i - 1]
                        next = all_customers[i]
                    else:
                        prev = all_customers[i - 1]
                        next = all_customers[i + 1]
        if prev:
            prev = str(prev.id) + '?previous=dashboard'
        else:
            prev = str(customer_id) + '?previous=dashboard'   
        if next:     
            next = str(next.id) + '?previous=dashboard'
        else:
            next = str(customer_id) + '?previous=dashboard'
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
        customers = customers[::-1]
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
    # print(type(prev), next)
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
                    i.created_at.astimezone(london_tz).time(),
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
                    i.created_at.astimezone(london_tz).time(),
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
                    i.created_at.astimezone(london_tz).time(),
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
        council_routes = Route.objects.all().filter(council=council)
        print(Route.objects.all().filter(council=council))
    else:
        council = None
        council_routes = None
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
    routes = Route.objects.all().filter(client=customer.client)
    all_stages = Stage.objects.all()    
    products = Product.objects.all().filter(client=customer.client)
    true_products = [True] * len(products)
    true_routes = [True] * len(routes)
    stages = {}

    for stage in all_stages:
        stages[stage.name] = json.loads(stage.fields)

    if customer.stage_values:
        stage_values = json.loads(customer.stage_values)
        values = {}
        for name, s_fields in stages.items():
            fields = {}
            for field in s_fields:
                fields[field] = [s_fields[field], '']
            values[name] = fields

        for key, fields in values.items():
            if key in stage_values:
                for field in fields:
                    if field in stage_values[key]:
                        fields[field][1] = stage_values[key][field]

        i = 0
        for product in products:
            product_rules = {}
            for key, value in ast.literal_eval(product.rules_regulations).items():
                rule_key = value[0].split(",")[0]
                rule_value = value[1].split(',')[0]
                rule_additional_value = value[2]

                if rule_key not in product_rules:
                    product_rules[rule_key] = {rule_value: [rule_additional_value]}
                else:
                    if rule_value not in product_rules[rule_key]:
                        product_rules[rule_key][rule_value] = [rule_additional_value]
                    else:
                        product_rules[rule_key][rule_value].append(rule_additional_value)

            for stage, rules in product_rules.items():
                if stage in values:
                    for field, rule in rules.items():
                        for key, value in values[stage].items():
                            if ',' in key:
                                key = key.split(',')[0]
                            if field == key:
                                if value[0] in ['time', 'date', 'number', 'month']:
                                    if value[0] == 'date':
                                        if check_date(value[1], rule):
                                            pass
                                        else:
                                            true_products[i] = False
                                    elif value[0] == 'time':
                                        if check_time(value[1], rule):
                                            pass
                                        else:
                                            true_products[i] = False
                                    elif value[0] == 'number':
                                        if check_number(value[1], rule):
                                            pass
                                        else:
                                            true_products[i] = False
                                    elif value[0] == 'month':
                                        if check_month(value[1], rule):
                                            pass
                                        else:
                                            true_products[i] = False
                                else:
                                    if value[1] in rule or value[1] == '':
                                        pass
                                    else:
                                        true_products[i] = False

            i += 1

        j = 0
        for route in routes:
            route_rules = {}
            for key, value in ast.literal_eval(route.rules_regulations).items():
                rule_key = value[0].split(",")[0]
                rule_value = value[1].split(",")[0]
                rule_additional_value = value[2]

                if rule_key not in route_rules:
                    route_rules[rule_key] = {rule_value: [rule_additional_value]}
                else:
                    if rule_value not in route_rules[rule_key]:
                        route_rules[rule_key][rule_value] = [rule_additional_value]
                    else:
                        route_rules[rule_key][rule_value].append(rule_additional_value)

            for stage, rules in route_rules.items():
                if stage in values:
                    for field, rule in rules.items():
                        for key, value in values[stage].items():
                            if "," in key:
                                key = key.split(",")[0]
                            if field == key:
                                if value[0] in ["time", "date", "number", "month"]:
                                    if value[0] == "date":
                                        if check_date(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                    elif value[0] == "time":
                                        if check_time(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                    elif value[0] == "number":
                                        if check_number(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                    elif value[0] == "month":
                                        if check_month(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                else:
                                    if value[1] in rule or value[1] == "":
                                        pass
                                    else:
                                        true_routes[j] = False
                                print("route",true_routes)

            j += 1

        j = 0
        for route in routes:
            route_rules = {}
            if route.sub_rules_regulations == None:
                continue
            for key, value in ast.literal_eval(route.sub_rules_regulations).items():
                rule_key = value[0].split(",")[0]
                rule_value = value[1].split(',')[0]
                rule_additional_value = value[2]

                if rule_key not in route_rules:
                    route_rules[rule_key] = {rule_value: [rule_additional_value]}
                else:
                    if rule_value not in route_rules[rule_key]:
                        route_rules[rule_key][rule_value] = [rule_additional_value]
                    else:
                        route_rules[rule_key][rule_value].append(rule_additional_value)

            for stage, rules in route_rules.items():
                if stage in values:
                    for field, rule in rules.items():
                        for key, value in values[stage].items():
                            if ',' in key:
                                key = key.split(',')[0]
                            if field == key:
                                if value[0] in ['time', 'date', 'number', 'month']:
                                    if value[0] == 'date':
                                        if check_date(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                    elif value[0] == 'time':
                                        if check_time(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                    elif value[0] == 'number':
                                        if check_number(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                    elif value[0] == 'month':
                                        if check_month(value[1], rule):
                                            pass
                                        else:
                                            true_routes[j] = False
                                else:
                                    if value[1] in rule or value[1] == '':
                                        pass
                                    else:
                                        true_routes[j] = False
                                print(true_routes)

            j += 1

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
                    "council_routes": council_routes,
                    "stages": stages,
                    "values": values,
                    "agents": agents,
                    "show_customer": show_customer,
                    "events": events,
                    "reasons": reasons,
                    "templates": templates,
                    "signatures": signatures,
                    "domain_name": domain_name,
                    "products": products,
                    "true_products": true_products,
                    "true_routes": true_routes,
                    "clients": clients,
                    "campaigns": campaigns,
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
            "council_routes":council_routes,
            "stages": stages,
            "agents" : agents,
            "show_customer": show_customer,
            "events": events,
            "reasons": reasons,
            "templates": templates,
            "signatures": signatures,
            "domain_name": domain_name,
            "products": products,
            "clients": clients,
            "campaigns": campaigns,
        },
    )

def check_date(date_to_check, conditions):
    if date_to_check == '':
        return True
    date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
    
    for condition in conditions:
        date_str, comparator = condition.split(',')
        condition_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        if comparator.strip() == 'Less Than' and date_to_check < condition_date:
            return True
        elif comparator.strip() == 'Greater Than' and date_to_check > condition_date:
            return True
        elif comparator.strip() == 'Equal' and date_to_check == condition_date:
            return True
        elif comparator.strip() == '':
            return True
    
    return False

def check_month(month_to_check, conditions):
    if month_to_check == '':
        return True
    month_to_check = datetime.strptime(month_to_check, '%Y-%m')

    for condition in conditions:
        month_str, comparator = condition.split(',')
        condition_month = datetime.strptime(month_str, '%Y-%m')

        if comparator.strip() == 'Less Than' and month_to_check < condition_month:
            return True
        elif comparator.strip() == 'Greater Than' and month_to_check > condition_month:
            return True
        elif comparator.strip() == 'Equal' and month_to_check == condition_month:
            return True
        elif comparator.strip() == "":
            return True

    return False

def check_number(number_to_check, conditions):
    if number_to_check == '':
        return True
    number_to_check = int(number_to_check)

    for condition in conditions:
        number_str, comparator = condition.split(',')
        condition_number = int(number_str)

        if comparator.strip() == 'Less Than' and number_to_check < condition_number:
            return True
        elif comparator.strip() == 'Greater Than' and number_to_check > condition_number:
            return True
        elif comparator.strip() == 'Equal' and number_to_check == condition_number:
            return True
        elif comparator.strip() == "":
            return True

    return False

def check_time(time_to_check, conditions):
    if time_to_check == '':
        return True
    time_to_check = datetime.strptime(time_to_check, '%H:%M')

    for condition in conditions:
        time_str, comparator = condition.split(',')
        condition_time = datetime.strptime(time_str, '%H:%M')

        if comparator.strip() == 'Less Than' and time_to_check < condition_time:
            return True
        elif comparator.strip() == 'Greater Than' and time_to_check > condition_time:
            return True
        elif comparator.strip() == 'Equal' and time_to_check == condition_time:
            return True
        elif comparator.strip() == "":
            return True

    return False


@login_required
def client_detail(request, client_id, s_client_id=None):
    all_clients = []
    prev = None
    next = None
    domain_name = request.build_absolute_uri("/")[:-1]
    signatures = Signature.objects.all()
    coverage_area = CoverageAreas.objects.all().filter(client=Clients.objects.get(pk=client_id)) 
    clients = (
        Clients.objects.annotate(earliest_action_date=Max("action__date_time"))
        .filter(parent_client=None)
        .filter(closed=False)
        .order_by("earliest_action_date")
    )
    clients = list(clients)
    new_clients = []
    for client in clients:
        actions = client.get_created_at_action_history()
        flag = False
        for action in actions:
            if action.imported == False:
                new_clients.append(client)
                break
    new_clients.sort(key=lambda x: x.get_created_at_action_history()[0].date_time)
    result = [x for x in clients if x not in new_clients] 
    clients= new_clients + result
    clients = clients[::-1]
    if len(clients) == 1:
        prev = client
        next = client
    else:
        for i in range(len(clients)):
            if clients[i].id == client_id:
                if i == 0:
                    prev = clients[i]
                    next = clients[i + 1]
                elif i == len(clients) - 1:
                    prev = clients[i - 1]
                    next = clients[i]
                else:
                    prev = clients[i - 1]
                    next = clients[i + 1]
    if prev:
        prev = str(prev.id)
    else:
        prev = str(client_id)   
    if next:     
        next = str(next.id)
    else:
        next = str(client_id)
    # print(type(prev), next)
    client = Clients.objects.get(pk=client_id)
    stages = Stage.objects.all().filter(client=client).order_by('order')
    campaigns = Campaign.objects.all().filter(client=client).filter(archive=False)
    uncampaigns = Campaign.objects.all().filter(client=client).filter(archive=True)
    all_products = Product.objects.all()
    products = Product.objects.all().filter(client=client).filter(archive=False)
    unproducts = Product.objects.all().filter(client=client).filter(archive=True)
    all_routes = Route.objects.all().filter(main_route=True)
    routes = Route.objects.all().filter(client=client).filter(archive=False)
    unroutes = Route.objects.all().filter(client=client).filter(archive=True)
    child_clients = Clients.objects.all().filter(parent_client=client)
    agents = User.objects.filter(is_superuser=False)
    show_client = client
    reasons = Reason.objects.all()
    templates = Email.objects.all()
    if s_client_id:
        show_client = Clients.objects.get(pk=s_client_id)

    history = {}
    actions = client.get_created_at_action_history()
    imported = {}
    london_tz = timezone("Europe/London")
    keyevents = client.get_created_at_action_history().filter(keyevents=True)
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
                    i.created_at.astimezone(london_tz).time(),
                    i.text,
                    i.agent.first_name,
                    i.agent.last_name,
                    i.imported,
                    i.talked_with,
                    i.client.postcode,
                    i.client.house_name,
                ]
            )
        else:
            history[i.created_at.replace(tzinfo=london_tz).date()].append(
                [
                    i.created_at.astimezone(london_tz).time(),
                    i.client.postcode,
                    i.client.house_name,
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
                    i.created_at.astimezone(london_tz).time(),
                    i.client.postcode,
                    i.client.house_name,
                    i.agent.first_name,
                    i.agent.last_name,
                    i.action_type,
                    i.date_time,
                    i.talked_with,
                    i.text
                ]
            )

        return render(
            request,
            "home/client-detail.html",
            {
                "client": client,
                "history": history,
                "imported": imported,
                "prev": prev,
                "next": next,
                "child_clients": child_clients,
                "agents": agents,
                "show_client": show_client,
                "events": events,
                "reasons": reasons,
                "templates": templates,
                "signatures": signatures,
                "domain_name": domain_name,
                "campaigns": campaigns,
                "uncampaigns": uncampaigns,
                "products": products,
                "unproducts": unproducts,
                "coverage_areas": coverage_area,
                "all_products": all_products,
                "all_routes": all_routes,
                "routes":routes,
                "unroutes":unroutes,
                "stages": stages,
                
            },
        )

    return render(
        request,
        "home/client-detail.html",
        {
            "client": client,
            "history": history,
            "imported": imported,
            "prev": prev,
            "next": next,
            "child_clients": child_clients,
            "agents" : agents,
            "show_client": show_client,
            "events": events,
            "reasons": reasons,
            "templates": templates,
            "signatures": signatures,
            "domain_name": domain_name,
            "campaigns": campaigns,
            "uncampaigns": uncampaigns,
            "products":products,
            "unproducts":unproducts,
            "coverage_areas": coverage_area,
            "all_products":all_products,
            "all_routes":all_routes,
            "routes":routes,
            "unroutes":unroutes,
            "stages": stages,
        },
    )


@login_required
def council_detail(request, council_id):
    all_councils = Councils.objects.all()
    council = Councils.objects.get(pk=council_id)
    routes = Route.objects.all().filter(council=council).filter(main_route=True)
    all_routes = Route.objects.all().filter(parent_route=True)
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

    return render(
        request,
        "home/council-detail.html",
        {
            "council": council,
            "prev": prev,
            "next": next,
            "routes": routes,
            "all_routes" : all_routes,
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
    # print(type(customers))
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

    client = Clients.objects.all()    
    if request.session.get("first_name") and request.GET.get("page") != "add_customer":
        delete_customer_session(request)
    return render(
        request, "home/customer.html", {"customers": p_customers, "current_date": datetime.now(london_tz).date, "campaigns": campaigns,"agents": serialize('json', agents), 'page_obj': page_obj, 'clients':client}
    )


@login_required
def Client(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    if request.GET.get("page") == "edit_client" and request.GET.get("backto") is None:
        client_id = request.GET.get("id")
        client = Clients.objects.get(pk=client_id)
        if client.parent_client:
            edit_client = client
            client = Clients.objects.get(pk=client.parent_client.id)
            clients = Clients.objects.all().filter(parent_client=client)
            return render(
                request,
                "home/client.html",
                {
                    "edit_client": edit_client,
                    "client": client,
                    "clients": clients,
                },
            )
        edit_client = client
        clients = Clients.objects.all().filter(parent_client=client)
        return render(
            request,
            "home/client.html",
            {
                "edit_client": edit_client,
                "client": client,
                "clients": clients,
            },
        )

    # clients = Clients.objects.annotate(num_actions=Count('action')).order_by('-num_actions', 'action__date_time').distinct()
    current_time = datetime.now(london_tz)
    user  = User.objects.get(email=request.user)
    clients = (
        Clients.objects.annotate(earliest_action_date=Max("action__date_time"))
        .filter(parent_client=None)
        .filter(closed=False)
        .order_by("earliest_action_date")
    )

    clients = list(clients)
    new_clients = []
    for client in clients:
        actions = client.get_created_at_action_history()
        flag = False
        for action in actions:
            if action.imported == False:
                new_clients.append(client)
                break

    new_clients.sort(key=lambda x: x.get_created_at_action_history()[0].date_time)

    result = [x for x in clients if x not in new_clients] 

    clients= new_clients + result
    # print(type(clients))
    clients = clients[::-1]
    campaigns = Campaign.objects.all()
    agents = User.objects.filter(is_superuser=False)
    p_clients = Paginator(clients, 50)
    page_number = request.GET.get('page')
    try:
        page_obj = p_clients.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p_clients.page(1)
    except EmptyPage:
        page_obj = p_clients.page(p_clients.num_pages)

    return render(
        request, "home/client.html", {"clients": p_clients, "current_date": datetime.now(london_tz).date, "campaigns": campaigns,"agents": serialize('json', agents), 'page_obj': page_obj}
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
    if request.session.get("first_name"):
        delete_customer_session(request)
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
    if request.session.get("first_name"):
        delete_customer_session(request)
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
    if request.GET.get("page") == "edit_signature":
        signature_id = request.GET.get("id")
        signature = Signature.objects.get(pk=signature_id)
        return render(request, "home/admin.html", {"signature": signature})
    if request.session.get("first_name"):
        delete_customer_session(request)
    users = User.objects.filter(is_superuser=False).values()
    emails = Email.objects.all()
    reasons = Reason.objects.all()
    signatures = Signature.objects.all()
    return render(request, "home/admin.html", {"users": users, "emails": emails, "reasons": reasons, "signatures": signatures})


@login_required
def Finance(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    return render(request, "home/finance.html")


@login_required
def HR(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
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
        client = request.POST.get("client")
        agent = User.objects.get(email=request.user)

        if (
            campaign == "nan"
            or city == "nan"
            or county == "nan"
            or country == "nan"
            or client == "nan"
        ):
            messages.error(request, "Select all dropdown fields")
            return redirect("/customer?page=add_customer")

        if phone_number[0] == "0":
            phone_number = phone_number[1:]
            phone_number = "+44" + phone_number
        elif phone_number[0] == "+":
            phone_number = phone_number
        else:
            phone_number = "+44" + phone_number

        if Customers.objects.filter(email=email).filter(client=client).exists():
            messages.error(request, "Email with this Client already exists")
            request.session['first_name'] = first_name,
            request.session['last_name'] = last_name,
            request.session['phone_number'] = phone_number,
            request.session['email'] = email,
            request.session['postcode'] = postcode,
            request.session['street_name'] = street_name,
            request.session['house_name'] = house_name,
            request.session['city'] = city,
            request.session['county'] = county,
            request.session['country'] = country,
            request.session['campaign'] = campaign,
            request.session['client'] = client,

            return redirect("/customer?page=add_customer")

        if (
            Customers.objects.filter(phone_number=phone_number)
            .filter(client=client)
            .exists()
        ):
            messages.error(request, "Phone number already exists")
            request.session["first_name"] = (first_name,)
            request.session["last_name"] = (last_name,)
            request.session["phone_number"] = (phone_number,)
            request.session["email"] = (email,)
            request.session["postcode"] = (postcode,)
            request.session["street_name"] = (street_name,)
            request.session["house_name"] = (house_name,)
            request.session["city"] = (city,)
            request.session["county"] = (county,)
            request.session["country"] = (country,)
            request.session["campaign"] = (campaign,)
            request.session["client"] = (client,)

            return redirect("/customer?page=add_customer")

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
            client=Clients.objects.get(pk=client),
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
                action_type=f"Added  {customer.first_name}  {customer.last_name},  {customer.house_name },  {customer.phone_number},  {customer.email}, {customer.house_name},  {customer.street_name},  {customer.city} {customer.county},  {customer.country}",
                keyevents=True,
        )
        messages.success(request, "Customer added successfully!")
        if request.session.get("first_name"):
            delete_customer_session(request)
        return redirect("app:customer")
    return render(request, "home/customer.html")


@login_required
def edit_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == "POST":
        changed = ''
        if customer.phone_number != request.POST.get("phone_number"):
            changed += f'{request.POST.get("phone_number")}, '
        if customer.email != request.POST.get('email'):
            changed += f'{request.POST.get("email")}, '
        if customer.postcode != request.POST.get("postcode"):
            changed += f'{request.POST.get("postcode")}, '
        if customer.street_name != request.POST.get("street_name"):
            changed += f'{request.POST.get("street_name")}, '
        if customer.city != request.POST.get("city"):
            changed += f'{request.POST.get("city")}, '
        if customer.house_name != request.POST.get("house_name"):
            changed += f'{request.POST.get("house_name")}, '
        if customer.county != request.POST.get("county"):
            changed += f'{request.POST.get("county")}, '
        if customer.country != request.POST.get("country"):
            changed += f'{request.POST.get("country")}, '

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
        # print(request.POST.get("county"),request.POST.get("country"))
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
            action_type=f"Updated {customer.first_name},  {customer.last_name} - " + changed,
            keyevents=True,
        )
        messages.success(request, "Customer updated successfully!")
        if customer.parent_customer:
            customer.parent_customer.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Updated {customer.parent_customer.firt_name},  {customer.parent_customer.last_name} - " + changed,
                keyevents=True,
            )
            return redirect(f"/customer-detail/{customer.parent_customer.id}")

        return redirect(f"/customer-detail/{customer_id}")

    context = {"customer": customer}
    return render(request, "home/customer.html", context)


@login_required
def add_client(request):
    if request.method == "POST":
        acc_number = request.POST.get("acc_number")
        sort_code = request.POST.get("sort_code")
        iban = request.POST.get("iban")
        bic_swift = request.POST.get("bic_swift")
        company_name = request.POST.get("company_name").upper()
        company_phno = request.POST.get("company_phno")
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
        agent = User.objects.get(email=request.user)

        if phone_number[0] == "0":
            phone_number = phone_number[1:]
            phone_number = "+44" + phone_number
        elif phone_number[0] == "+":
            phone_number = phone_number
        else:
            phone_number = "+44" + phone_number

        if Clients.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("/client?page=add_client")

        if Clients.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists")
            return redirect("/client?page=add_client")


        postcode = re.sub(r'\s+', ' ', postcode)
        client = Clients.objects.create(
            acc_number = acc_number,
            sort_code = sort_code,
            iban = iban,
            bic_swift = bic_swift,
            company_name=company_name,
            company_phno=company_phno,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            postcode=postcode,
            street_name=street_name,
            city=city,
            house_name=house_name,
            county=county,
            country=country,
            agent=agent,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            primary_client=True,
        )
        client.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Added {client.first_name}  {client.last_name},  {client.house_name },  {client.phone_number},  {client.email}, {client.house_name},  {client.street_name},  {client.city},  {client.county},  {client.country}",
                keyevents=True,
        )
        messages.success(request, "Client added successfully!")
        return redirect("app:client")
    return render(request, "home/client.html")


@login_required
def edit_client(request, client_id):
    client = Clients.objects.get(pk=client_id)
    if request.method == "POST":
        changed = ''
        if client.acc_number != request.POST.get("acc_number"):
            changed += f'{request.POST.get("acc_number")}'
        if client.sort_code != request.POST.get("sort_code"):
            changed += f'{request.POST.get("sort_code")}'
        if client.iban != request.POST.get("iban"):
            changed += f'{request.POST.get("iban")}'
        if client.bic_swift != request.POST.get("bic_swift"):
            changed += f'{request.POST.get("bic_swift")}'
        if client.company_name != request.POST.get("company_name"):
            changed += f'{request.POST.get("company_name")}'
        if client.company_phno != request.POST.get("company_phno"):
            changed += f'{request.POST.get("company_phno")}'
        if client.phone_number != request.POST.get("phone_number"):
            changed += f'{request.POST.get("phone_number")}'
        if client.email != request.POST.get('email'):
            changed += f'{request.POST.get("email")}'
        if client.postcode != request.POST.get("postcode"):
            changed += f'{request.POST.get("postcode")}'
        if client.street_name != request.POST.get("street_name"):
            changed += f'{request.POST.get("street_name")}'
        if client.city != request.POST.get("city"):
            changed += f'{request.POST.get("city")}'
        if client.house_name != request.POST.get("house_name"):
            changed += f'{request.POST.get("house_name")}'
        if client.county != request.POST.get("county"):
            changed += f'{request.POST.get("county")}'
        if client.country != request.POST.get("country"):
            changed += f'{request.POST.get("country")}'

        client.acc_number = request.POST.get("acc_number")
        client.sort_code = request.POST.get("sort_code")
        client.iban = request.POST.get("iban")
        client.bic_swift = request.POST.get("bic_swift")
        client.company_name = request.POST.get("company_name").upper()
        client.company_phno = request.POST.get("company_phno")
        client.first_name = request.POST.get("first_name")
        client.last_name = request.POST.get("last_name").upper()
        client.phone_number = request.POST.get("phone_number")
        client.email = request.POST.get("email")
        client.postcode = re.sub(r'\s+', ' ', request.POST.get("postcode"))
        client.street_name = request.POST.get("street_name")
        client.city = request.POST.get("city")
        client.house_name = request.POST.get("house_name")
        client.county = request.POST.get("county")
        client.country = request.POST.get("country")
        # print(request.POST.get("county"),request.POST.get("country"))
        if client.city == "nan" or client.county == "nan" or client.country == "nan":
            messages.error(request, "Select all dropdown fields")
            return redirect(f"/client?page=edit_client&id={client_id}")

        client.save()
        client.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=f"Updated {client.first_name},  {client.last_name} - " + changed,
            keyevents=True,
        )
        messages.success(request, "Client updated successfully!")
        if client.parent_client:
            client.parent_client.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Updated {client.parent_client.firt_name},  {client.parent_client.last_name} - " + changed,
                keyevents=True,
            )
            return redirect(f"/client-detail/{client.parent_client.id}")

        return redirect(f"/client-detail/{client_id}")

    context = {"client": client}
    return render(request, "home/client.html", context)


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
def remove_client(request, client_id):
    client = Clients.objects.get(pk=client_id)
    client.delete()

    messages.success(request, "Client deleted successfully!")
    return redirect("app:client")


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

def client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        talked_with = request.POST.get("talked_client")
        date_str = request.POST.get("date_field")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")

        if talked_with == "nan":
            messages.error(request, "Client field should be mapped")
            return redirect(f"/client-detail/{client_id}")

        client.add_action(
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
        return HttpResponseRedirect("/client-detail/" + str(client_id))

def close_client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        talked_with = request.POST.get("talked_client")
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
            
        if client.closed:
            c_text = text
        

        if client.closed:
            action_type = f"Reopened"
            closed = False
            try:
                client = Clients.objects.get(pk=client_id)
                client.assigned_to =  User.objects.get(pk=reason)
                client.save()
                client.add_action(
                    agent=User.objects.get(email=request.user),
                    date_time=datetime.now(pytz.timezone("Europe/London")),
                    created_at=datetime.now(pytz.timezone("Europe/London")),
                    action_type="Assigned to Agent",
                )
            except Exception as e:
                messages.error(request, f"Error assigning client: {e}")
                return HttpResponseRedirect("/client-detail/" + str(client_id))
        else:
            action_type = f"Closed"
            closed = True

        if talked_with == "nan":
            messages.error(request, "Client field should be mapped")
            return redirect(f"/client-detail/{client_id}")

        client.add_action(
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
        return HttpResponseRedirect("/client-detail/" + str(client_id))


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

def na_client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=60)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

        client.add_action(
            date_time=date_time,
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(london_tz),
            action_type="NA",
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/client-detail/" + str(client_id))

def lm_client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=60)
        time_str_updated = time_obj.strftime("%H:%M")
        date_time_str = f"{date_str} {time_str_updated}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

        client.add_action(
            date_time=date_time,
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type="LM",
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/client-detail/" + str(client_id))


def import_customers_view(request):
    excel_columns = []
    expected_columns = ["history"]
    history = {}
    message = []
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        campaign = request.POST.get("campaign")
        client = request.POST.get("client")
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

            if Customers.objects.filter(email=customer_data['email']).exists():
                message.append(f'{customer_data["first_name"]} {customer_data["last_name"]}')
                continue

            elif Customers.objects.filter(
                phone_number=customer_data['phone_number']
            ).exists():
                message.append(
                    f'{customer_data["first_name"]} {customer_data["last_name"]}'
                )
                continue
            
            if campaign == "nan" or client == "nan":
                messages.error(request, "Select all dropdown fields")
                return redirect("/customer?page=add_customer")

            customer = Customers.objects.create(
                **customer_data,
                district=district,
                campaign=Campaign.objects.get(id=campaign),
                client=Clients.objects.get(pk=client),
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
                action_type=f"Added {customer.first_name}  {customer.last_name},  {customer.house_name },  {customer.phone_number},  {customer.email}, {customer.house_name},  {customer.street_name},  {customer.city}, {customer.county},  {customer.country}",
                keyevents=True,
        )
        if message:
            messages.error(request, f"Customer with email or phone number already exists: {', '.join(message)}")
        else:
            messages.success(request, "Customers imported successfully.")
        return redirect("app:customer")

    campaigns = Campaign.objects.all()
    client = Clients.objects.all()    


    return render(
        request,
        "home/import_customers.html",
        {"excel_columns": excel_columns, "campaigns": campaigns, 'clients':client},
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

def bulk_remove_clients(request):
    if request.method == "GET":
        client_ids_str = request.GET.get("ids", "")
        try:
            client_ids = [
                int(id) for id in client_ids_str.split(",") if id.isdigit()
            ]
            if client_ids:
                Clients.objects.filter(id__in=client_ids).delete()
                messages.success(request, "Selected clients deleted successfully.")
            else:
                messages.warning(
                    request, "No valid client IDs provided for deletion."
                )
        except Exception as e:
            messages.error(request, f"Error deleting clients: {e}")
        return redirect("app:client")
    return render(request, "home/client_list.html")


def add_campaign(request, client_id):
    if request.method == "POST":
        description = request.POST.get("description")
        name = request.POST.get("name")
        if Campaign.objects.filter(name=name).exists():
            messages.error(request, "Campaign with this name already exists!")
            return redirect(f"/client-detail/{client_id}")
        name = request.POST.get("name")
        campaign = Campaign.objects.create(
            client_id=client_id,
            name=name,
            description=description,
        )
        messages.success(request, "Campaign added successfully!")
        return redirect(f"/client-detail/{client_id}")
    return render(request, f"/client-detail/{client_id}")


def remove_campaign(request, campaign_id, client_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    campaign.delete()
    messages.success(request, "Campaign deleted successfully!")
    return redirect(f"/client-detail/{client_id}")

def add_product_client(request,client_id):
    if request.method == 'POST':
        product = Product.objects.get(pk=request.POST.get('product_id'))
        client = Clients.objects.get(pk=client_id)
        client.product.add(product)
        product.save()
        messages.success(request, "Product added successfully to a Client!")
        return redirect(f'/client-detail/{client_id}')


@login_required
def product(request):
    products = Product.objects.all()
    return render(request, "home/products.html", {"products": products})

@login_required
def funding_route(request):
    products = Product.objects.all()
    if request.GET.get("page") == "edit":
        route_id = request.GET.get("route_id")
        route = Route.objects.get(pk=route_id)
        
        return render(request, "home/funding_routes.html", {"route": route,"products": products})
    funding_routes = Route.objects.all().filter(parent_route=True)
    return render(request, "home/funding_routes.html", {"funding_routes": funding_routes, "products": products})

@login_required
def add_new_funding_route(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        documents = request.FILES.getlist("document")
        
        route = Route.objects.create(name=name, description=description,parent_route=True)
        for document in documents:
            doc = Document.objects.create(document=document)
            route.documents.add(doc)
        route.save()
        messages.success(request, "Funding Route created successfully!")
        return redirect("app:funding_route")
    return render(request, "home/add_new_funding_routes.html")

@login_required
def edit_new_funding_route(request,route_id):
    route = Route.objects.get(pk=route_id)
    if request.method == "POST":
        route.name = request.POST.get("name")
        route.description = request.POST.get("description")
        documents = request.FILES.getlist("document")
        for document in documents:
            doc = Document.objects.create(document=document)
            route.documents.add(doc)
        route.save()
        print(route.council_route.all())
        for council_route in route.council_route.all():
            council_route.name=route.name
            council_route.description=route.description
            council_route.save()
        messages.success(request, "Funding Route created successfully!")
        return redirect("app:funding_route")
    return render(request, "home/edit_new_funding_routes.html",{"route":route})


@login_required
def edit_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    clients = product.client.all()
    if clients.exists():
        client_id = clients.first().id
    stages = Stage.objects.all().filter(client=Clients.objects.get(pk=client_id))
    fields = {}
    saved_rules_regulations = json.loads(product.rules_regulations)
    if stages.exists():
        for stage in stages:
            fields[stage.name] = json.loads(stage.fields)
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        dynamicStages = request.POST.getlist("dynamicStage")
        dynamicFields = request.POST.getlist("dynamicField")
        dynamicRules = request.POST.getlist("dynamicRule")
        documents = request.FILES.getlist("document")

        rules_regulations = {}
        i=0
        for d_stage, d_field, d_rule in zip(dynamicStages, dynamicFields, dynamicRules):
            rules_regulations[f'{i}'] = [d_stage,d_field, d_rule]
            i+=1
        product.rules_regulations = json.dumps(rules_regulations)
        for document in documents:
            doc = Document.objects.create(document=document)
            product.documents.add(doc)
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect(f"/client-detail/{client_id}")
    return render(
        request, "home/edit_products.html", {"product": product, "fields": fields, 'saved_rules_regulations': saved_rules_regulations}
    )

@login_required
def edit_funding_route(request, funding_route_id):
    funding_route = Route.objects.get(pk=funding_route_id)
    councils = funding_route.council.all()
    if councils.exists():
        council_id = councils.first().id
    stages = Stage.objects.all()
    fields = {}
    saved_rules_regulations = {}
    if funding_route.rules_regulations:
        saved_rules_regulations = json.loads(funding_route.rules_regulations)
    if stages.exists():
        for stage in stages:
            fields[stage.name] = json.loads(stage.fields)
    if request.method == "POST":
        dynamicStages = request.POST.getlist("dynamicStage")
        dynamicFields = request.POST.getlist("dynamicField")
        dynamicRules = request.POST.getlist("dynamicRule")
        documents = request.FILES.getlist("document")

        rules_regulations = {}
        i = 0
        for d_stage, d_field, d_rule in zip(dynamicStages, dynamicFields, dynamicRules):
            rules_regulations[f"{i}"] = [d_stage, d_field, d_rule]
            i += 1
        funding_route.rules_regulations = json.dumps(rules_regulations)
        for document in documents:
            doc = Document.objects.create(document=document)
            funding_route.documents.add(doc)
        funding_route.save()
        for child_route in funding_route.client_route.all():
            child_route.rules_regulations = json.dumps(rules_regulations)
            for document in documents:
                doc = Document.objects.create(document=document)
                child_route.documents.add(doc)
            child_route.save()
        messages.success(request, "Funding Route updated successfully!")
        return redirect(f"/council-detail/{council_id}")
    return render(
        request, "home/edit_funding_routes.html", {"funding_route": funding_route, "fields": fields, 'saved_rules_regulations': saved_rules_regulations}
    )

@login_required
def add_product(request, client_id):
    clients = Clients.objects.all()
    fields = {}
    client = Clients.objects.get(pk=client_id)
    stages = Stage.objects.all().filter(client=client)
    if stages.exists():
        for stage in stages:
            fields[stage.name] =  json.loads(stage.fields)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        dynamicStages = request.POST.getlist("dynamicStage")
        dynamicFields = request.POST.getlist("dynamicField")
        dynamicRules = request.POST.getlist("dynamicRule")
        documents = request.FILES.getlist("document")

        rules_regulations = {}
        i=0
        for d_stage, d_field, d_rule in zip(dynamicStages, dynamicFields, dynamicRules):
            rules_regulations[f'{i}'] = [d_stage,d_field, d_rule]
            i+=1
        rules_regulations = json.dumps(rules_regulations)

        product = Product.objects.create(
            name=name,
            description=description,
            rules_regulations=rules_regulations,
        )
        client.product.add(product)
        for document in documents:
            doc = Document.objects.create(document=document)
            product.documents.add(doc)
        product.save()
        messages.success(request, "Product added successfully!")
        return redirect(f'/client-detail/{client_id}')
    return render(
        request,
        "home/add_products.html",
        {"clients": clients, "stages": stages, "fields": fields, "client_id": client_id},
    )

@login_required
def add_funding_route(request, council_id):
    council = Councils.objects.get(pk=council_id)
    if request.method == "POST":
        if request.POST.get("route") == "nan":
            messages.error(request, "Route should be selected")
            return redirect(f"/council-detail/{council_id}")
        route = Route.objects.get(pk=request.POST.get("route"))
        council_route = Route.objects.create(
            name=route.name,
            description=route.description,
            main_route=True,
        )
        council_route.council.add(council)
        route.council_route.add(council_route)
        council_route.save()
        route.save()
        messages.success(request, "Funding Route added successfully!")
        return redirect('/council-detail/'+str(council_id))

def remove_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect(f"/product")


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
            campaign=Campaign.objects.get(id=parent_customer.campaign.id),  # type: ignore
            client=Campaign.objects.get(id=parent_customer.campaign.id).client,  # type: ignore
            created_at=datetime.now(pytz.timezone("Europe/London")),
            parent_customer=parent_customer,
            primary_customer=True,
        )
        parent_customer.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=f"Added {child_customer.first_name}  {child_customer.last_name}  { child_customer.house_name }  {child_customer.phone_number},  {child_customer.email},  {child_customer.house_name},  {child_customer.street_name},  {child_customer.city},  {child_customer.county},  {child_customer.country}",
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


def add_route_client(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(pk=client_id)
        if request.POST.get("route") == "nan":
            messages.error(request, "Route should be selected")
            return redirect(f"/client-detail/{client_id}")
        main_route = Route.objects.get(pk=request.POST.get("route"))
        funding_route = Route.objects.create(
            name=main_route.name,
            description=main_route.description,
            rules_regulations=main_route.rules_regulations,
        )
        client.route.add(funding_route)
        for council in main_route.council.all():
            funding_route.council.add(council)
        funding_route.save()
        main_route.client_route.add(funding_route)
        main_route.save()
        client.save()
        messages.success(request, "Funding Route added successfully to a Client!")
        return redirect(f"/client-detail/{client_id}")

def add_council_funding_route(request, council_id):
    if request.method == "POST":
        council = Councils.objects.get(pk=council_id)
        route = Route.objects.get(pk=request.POST.get("route"))
        route.council.add(council)
        route.save()
        messages.success(request, "Funding Route added successfully to a Council!")
        return redirect(f"/council-detail/{council_id}")

def add_local_authority(request):
    if request.method == "POST":
        name = request.POST.get("name")
        council = Councils.objects.create(
            name=name,
            created_at=datetime.now(pytz.timezone('Europe/London')),
            agent=User.objects.get(email=request.user),
        )
        messages.success(request, "Local Authority added successfully!")
        return redirect("app:council")
    return render(request, "home/council.html")

def remove_funding_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    route.delete()
    messages.success(request, "Route deleted successfully!")
    return redirect("app:funding_route")


@login_required
def create_stage(request, client_id):
    routes = Route.objects.all()
    client = Clients.objects.get(pk=client_id)
    stages=Stage.objects.all().filter(client=client).order_by("order")
    templateablestages = Stage.objects.all().filter(templateable=True)
    if request.GET.get("page")== 'edit_page':
        stage = Stage.objects.get(pk=request.GET.get("stage_id"))          
        return render(request, 'home/stages.html', {"stage":stage, "fields":json.loads(stage.fields), "templateablestages": templateablestages})

    if request.method == "POST":
        dynamic_types = request.POST.getlist("dynamic_type")
        dynamic_labels = request.POST.getlist("dynamic_label")
        order = request.POST.get('order')
        templateable = request.POST.get('templateable') == 'on'
        description = request.POST.get('description')
        documents = request.FILES.getlist("document")

        if order.isdigit():
            order = int(order)
        else:
            messages.error(request, "Order should be a number")
            return redirect("/client-detail/"+str(client_id))
        if Stage.objects.filter(client=client).filter(order=order).exists():
            messages.error(request, "Stage with this order already exists!")
            return redirect("/client-detail/"+str(client_id))

        dynamic_fields = {}
        for label, field_type in zip(dynamic_labels, dynamic_types):
            dynamic_fields[label] = field_type
        fields = json.dumps(dynamic_fields)
        stage = Stage.objects.create(
            name=request.POST.get("name"),
            fields=fields,
            order=order,
            description=description,
            templateable=templateable,
            client=client,
        )
        for document in documents:
            doc = Document.objects.create(document=document)
            stage.documents.add(doc)
        stage.save()
        return redirect("/client-detail/"+str(client_id))
    return render(request, "home/stages.html", {"routes": routes, "stages": stages, "client_id": client_id, "templateablestages": templateablestages}) 


@login_required
def remove_stage(request, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    stage.delete()
    messages.success(request, "Stage deleted successfully!")
    return redirect("/client-detail/" + str(stage.client.id))

@login_required
def edit_stage(request, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    if request.method == "POST":
        dynamic_types = request.POST.getlist("dynamic_type")
        dynamic_labels = request.POST.getlist("dynamic_label")
        order = request.POST.get("order") 
        templateable = request.POST.get("templateable") == "on"
        description = request.POST.get("description")
        documents = request.FILES.getlist("document")
        dynamic_fields = {}
        if order.isdigit():
            order = int(order)
        else:
            messages.error(request, "Order should be a number")
            return redirect("/client-detail/" + str(stage.client.id))
        for label, field_type in zip(dynamic_labels, dynamic_types):
            dynamic_fields[label] = field_type
        fields = json.dumps(dynamic_fields)
        stage.name = request.POST.get("name")
        stage.fields = fields
        stage.order = order
        stage.description = description
        stage.templateable = templateable
        for document in documents:
            doc = Document.objects.create(document=document)
            stage.documents.add(doc)
        stage.save()
        messages.success(request, "Stage updated successfully!")
        return redirect("/client-detail/"+str(stage.client.id))


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

def remove_customer_route(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.route = None
    customer.save()
    messages.success(request, "Route removed successfully!")
    return redirect(f"/customer-detail/{customer_id}")

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
    domain_name = request.build_absolute_uri("/")[:-1]
    date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    body = ""
    subject = ""
    text = ""

    if request.POST.get("signature") == "nan":
        messages.error(request, "Signature field should be mapped")
        return redirect(f"/customer-detail/{customer_id}")

    signature = Signature.objects.get(pk=request.POST.get("signature"))

    if email_id != "nan":
        email = Email.objects.get(pk=email_id)
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
        subject = request.POST.get("subject")

    # body = re.sub(r"\r?\n", "\n", body)
    # signature.signature = re.sub(r"\r?\n", "\n", signature.signature)

    context = {
        "body": body,
        "signature": signature,
        "domain_name": domain_name,
    }
    template_name = "../templates/home/email.html"
    convert_to_html_content = render_to_string(
        template_name=template_name, context=context
    )
    plain_message = strip_tags(convert_to_html_content)
    print(convert_to_html_content)
    email = send_mail(
        subject=subject,
        message=plain_message,
        from_email="support@reform-group.uk",
        recipient_list=[customer.email],
        html_message=convert_to_html_content,
    ) 

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


def send_client_email(request, cclient_id):
    cclient = Cclients.objects.get(pk=cclient_id)
    email_id = request.POST.get("template")
    date_str = request.POST.get("date_field")
    time_str = request.POST.get("time_field")
    date_time_str = f"{date_str} {time_str}"
    domain_name = request.build_absolute_uri("/")[:-1]
    date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    body = ""
    subject = ""
    text = ""

    if request.POST.get("signature") == "nan":
        messages.error(request, "Signature field should be mapped")
        return redirect(f"/cclient-detail/{cclient_id}")

    signature = Signature.objects.get(pk=request.POST.get("signature"))

    if email_id != "nan":
        email = Email.objects.get(pk=email_id)
        text = email.name
        body = email.body
        if cclient.first_name:
            body = body.replace("{{first_name}}", cclient.first_name)
        if cclient.last_name:
            body = body.replace("{{last_name}}", cclient.last_name)
        if cclient.phone_number:
            body = body.replace("{{phone_number}}", cclient.phone_number)
        if cclient.email:
            body = body.replace("{{email}}", cclient.email)
        if cclient.house_name:
            body = body.replace("{{house_name}}", cclient.house_name)
        if cclient.street_name:
            body = body.replace("{{street_name}}", cclient.street_name)
        if cclient.city:
            body = body.replace("{{city}}", cclient.city)
        if cclient.county:
            body = body.replace("{{county}}", cclient.county)
        if cclient.country:
            body = body.replace("{{country}}", cclient.country)
        if cclient.postcode:
            body = body.replace("{{postcode}}", cclient.postcode)
        subject = email.subject
    else:
        body = request.POST.get("text")
        text = request.POST.get("text")
        subject = request.POST.get("subject")

    # Replace newline characters with <br> tags
    body = re.sub(r"\r?\n", "<br>", body)
    signature_content = re.sub(r"\r?\n", "<br>", signature.signature)

    print(body)
    print(signature_content)

    context = {
        "body": body,
        "signature": signature_content,
        "domain_name": domain_name,
    }

    template_name = "../templates/home/email.html"
    convert_to_html_content = render_to_string(
        template_name=template_name, context=context
    )
    plain_message = strip_tags(convert_to_html_content)

    email = send_mail(
        subject=subject,
        message=plain_message,
        from_email="support@reform-group.uk",
        recipient_list=[cclient.email],
        html_message=convert_to_html_content,
    )

    if text == "":
        cclient.add_action(
            agent=User.objects.get(email=request.user),
            closed=False,
            imported=False,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type="Email Sent",
            date_time=datetime.now(pytz.timezone("Europe/London")),
        )
    else:
        cclient.add_action(
            agent=User.objects.get(email=request.user),
            closed=False,
            imported=False,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type="Email Sent",
            date_time=date_time,
            text=text,
        )

    messages.success(request, "Email sent successfully!")
    return HttpResponseRedirect("/cclient-detail/" + str(cclient_id))


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


def add_signature(request):
    if request.method == "POST":
        signature = request.POST.get("signature")
        signature_img = request.FILES.get("signature_img")
        template = Signature.objects.create(
            signature=signature,
            signature_img=signature_img,
        )
        messages.success(request, "Signature added successfully!")
        return redirect("app:admin")
    return render(request, "home/admin.html")


def edit_signature(request, signature_id):
    signature = Signature.objects.get(pk=signature_id)
    if request.method == "POST":
        signature.signature = request.POST.get("signature")
        signature.signature_img = request.FILES.get("signature_img")
        signature.save()
        messages.success(request, "Signature updated successfully!")
        return redirect("app:admin")
    return redirect("app:admin")

def remove_signature(request, signature_id):
    signature = Signature.objects.get(pk=signature_id)
    signature.delete()
    messages.success(request, "Signature deleted successfully!")
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
            # print('response', response)
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
        get_message(historyId, userId)
    return HttpResponse(200)

def add_coverage_areas(request, client_id):
    if request.method == "POST":

        client = Clients.objects.get(pk=client_id)
        coverage_area = CoverageAreas.objects.create(
            client=client,
            postcode=re.sub(r"\s+", " ", request.POST.get("postcode")),
        )
        
        messages.success(request, "Postcode Added Successfully")
        return redirect(r"/client-detail/" + str(client_id))
    return render(request, "home/admin.html")

def archive_campaign(request,client_id, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    if campaign.archive == False:
        campaign.archive = True
        campaign.save()
        messages.success(request, "Archived successfully!")
        return redirect(r"/client-detail/" + str(client_id))
    else:
        campaign.archive = False
        campaign.save()
        messages.success(request, "Unarchived successfully!")
        return redirect(r"/client-detail/" + str(client_id))

def get_campaign(request, client_id):
    client = Clients.objects.get(pk=client_id)
    campaigns = Campaign.objects.all().filter(client=client)
    return JsonResponse([{"campaign_id": campaign.id,"campaign_name":campaign.name} for campaign in campaigns], safe=False)

def archive_product(request,client_id, product_id):
    product = Product.objects.get(pk=product_id)
    if product.archive == False:
        product.archive = True
        product.save()
        messages.success(request, "Archived successfully!")
        return redirect(r"/client-detail/" + str(client_id))
    else:
        product.archive = False
        product.save()
        messages.success(request, "Unarchived successfully!")
        return redirect(r"/client-detail/" + str(client_id))

def archive_route(request,client_id, route_id):
    route = Route.objects.get(pk=route_id)
    if route.archive == False:
        route.archive = True
        route.save()
        messages.success(request, "Archived successfully!")
        return redirect(r"/client-detail/" + str(client_id))
    else:
        route.archive = False
        route.save()
        messages.success(request, "Unarchived successfully!")
        return redirect(r"/client-detail/" + str(client_id))

def change_customer_client(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == "POST":
        client = Clients.objects.get(pk=request.POST.get("client"))
        campaign = Campaign.objects.get(pk=request.POST.get("campaign"))
        if (
            Customers.objects.filter(email=customer.email)
            .filter(phone_number=customer.phone_number)
            .filter(client=client)
            .exists()
        ):
            messages.success(request, "Customer with this Client already exist!")
            return redirect(r"/customer-detail/" + str(customer_id))
        new_customer = Customers.objects.create(
            first_name=customer.first_name,
            last_name=customer.last_name,
            phone_number=customer.phone_number,
            email=customer.email,
            postcode=customer.postcode,
            street_name=customer.street_name,
            city=customer.city,
            house_name=customer.house_name,
            address=customer.address,
            county=customer.county,
            country=customer.country,
            agent=customer.agent,
            district=customer.district,
            constituency=customer.constituency,
            campaign=campaign,
            client=client,
            created_at=datetime.now(pytz.timezone("Europe/London")),
            primary_customer=True,
            energy_rating=customer.energy_rating,
            energy_certificate_link=customer.energy_certificate_link,
            recommendations=customer.recommendations,
        )
        new_customer.add_action(
            agent=User.objects.get(email=request.user),
            date_time=datetime.now(pytz.timezone("Europe/London")),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=f"Added  {new_customer.first_name}  {new_customer.last_name},  {new_customer.house_name },  {new_customer.phone_number},  {new_customer.email}, {new_customer.house_name},  {new_customer.street_name},  {new_customer.city} {new_customer.county},  {new_customer.country}",
            keyevents=True,
        )
        messages.success(request, "New Customer added successfully!")
        return redirect(r"/customer-detail/" + str(customer_id))
    return render(request, "home/admin.html")

def delete_customer_session(request):
    del request.session['first_name']
    del request.session['last_name']
    del request.session['phone_number']
    del request.session['email']
    del request.session['postcode']
    del request.session['street_name']
    del request.session['house_name']
    del request.session['city']
    del request.session['county']
    del request.session['country']
    del request.session['campaign']
    del request.session['client']

def stage_template(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        if request.POST.get("template") == "nan":
            messages.error(request, "Select a template")
            return redirect(f"/client-detail/{client_id}")
        template_id = request.POST.get('template')
        template = Stage.objects.get(pk=template_id)
        templateablestages = Stage.objects.all().filter(templateable=True)
        messages.success(request, "Template copied successfully!")
        return render(request, 'home/add_stage_template.html', {"stage":template, "templateablestages":templateablestages,"fields":json.loads(template.fields), "client_id": client_id})


@login_required
def edit_local_funding_route(request, funding_route_id):
    funding_route = Route.objects.get(pk=funding_route_id)
    clients = funding_route.client.all()
    if clients.exists():
        client_id = clients.first().id
    stages = Stage.objects.all().filter(client=Clients.objects.get(pk=client_id))
    fields = {}
    saved_rules_regulations = {}
    if funding_route.rules_regulations:
        saved_rules_regulations = json.loads(funding_route.rules_regulations)
    if stages.exists():
        for stage in stages:
            fields[stage.name] = json.loads(stage.fields)
    if funding_route.sub_rules_regulations:
        sub_rules_regulations = json.loads(funding_route.sub_rules_regulations)
    else:
        sub_rules_regulations = None
    if stages.exists():
        for stage in stages:
            fields[stage.name] = json.loads(stage.fields)
    if request.method == "POST":
        dynamicStages = request.POST.getlist("subDynamicStage")
        dynamicFields = request.POST.getlist("subDynamicField")
        dynamicRules = request.POST.getlist("subDynamicRule")
        
        rules_regulations = {}
        i = 0
        for d_stage, d_field, d_rule in zip(dynamicStages, dynamicFields, dynamicRules):
            rules_regulations[f"{i}"] = [d_stage, d_field, d_rule]
            i += 1
        funding_route.sub_rules_regulations = json.dumps(rules_regulations)
        funding_route.save()
        messages.success(request, "Funding Route updated successfully!")
        return redirect(f"/client-detail/{client_id}")
    return render(
        request,
        "home/edit_local_funding_routes.html",
        {
            "funding_route": funding_route,
            "fields": fields,
            "saved_rules_regulations": saved_rules_regulations,
            "sub_rules_regulations": sub_rules_regulations,
        },
    )

def make_template_stage(request,stage_id):
    stage = Stage.objects.get(pk=stage_id)
    stage.templateable = not stage.templateable
    stage.save()
    if stage.templateable:
        messages.success(request, "Stage is now made template!")
    else:
        messages.success(request, "Stage is not a template!")
    return redirect(f"/client-detail/{stage.client.id}")

def remove_doc(request,doc_id):
    pass

def questions(request):
    questions = Questions.objects.all()
    actions = QAction.objects.all()
    return render(request, 'home/question_actions.html', {'questions':questions,'actions':actions})

def add_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        type = request.POST.get('type')
        new_question = Questions.objects.create(
            question=question,
            type=type,
        )
    messages.success(request, "Question is created successfully!")
    return redirect("/questions")


def add_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        type = request.POST.get('type')
        new_action = QAction.objects.create(
            action=action,
            script=type,
        )
    messages.success(request, "Action is created successfully!")
    return redirect("/questions")

def edit_question(request, question_id):
    if request.method == 'POST':
        qquestion = Questions.objects.get(pk=question_id)
        question = request.POST.get('question')
        type = request.POST.get('type')
        qquestion.question=question
        qquestion.type=type
        qquestion.save()
    messages.success(request, "Question is edited successfully!")
    return redirect("/questions")


def edit_action(request, action_id):
    if request.method == "POST":
        qaction = QAction.objects.get(pk=action_id)
        action = request.POST.get("action")
        script = request.POST.get("script")
        qaction.action = action
        qaction.script = script
        qaction.save()
    messages.success(request, "Action is edited successfully!")
    return redirect("/questions")


def delete_question(request, question_id):
    qquestion = Questions.objects.get(pk=question_id)
    qquestion.delete()
    messages.success(request, "Question is deleted successfully!")
    return redirect("/questions")

def delete_action(request, action_id):
    qaction = QAction.objects.get(pk=action_id)
    qaction.delete()
    messages.success(request, "Action is deleted successfully!")
    return redirect("/questions")

def add_new_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        documents = request.FILES.getlist('document')
        product = Product.objects.create(
            name=name,
            description=description,
        )
        for document in documents:
            doc = Document.objects.create(document=document)
            product.documents.add(doc)
        product.save()
        messages.success(request, "Product added successfully!")
        return redirect("app:product")
    return render(request, 'home/add_new_product.html')

def edit_new_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        product.name = name
        product.description = description
        documents = request.FILES.getlist('document')
        for document in documents:
            doc = Document.objects.create(document=document)
            product.documents.add(doc)

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("app:product")
    return render(request, 'home/edit_new_product.html', {'product':product})


def delete_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("app:product")


def delete_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    route.delete()
    messages.success(request, "Route deleted successfully!")
    return redirect("app:funding_route")

def edit_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    products = Product.objects.all()
    if request.method == "POST":
        route.name = request.POST.get("name")
        route.description = request.POST.get("description")
        documents = request.FILES.getlist("document")
        for document in documents:
            doc = Document.objects.create(document=document)
            route.documents.add(doc)

        for product in products:
            if request.POST.get(product.name) == 'true':
                route.product.add(product)
            else:
                route.product.remove(product)
        route.save()
        messages.success(request, "Route updated successfully!")
        return redirect("app:funding_route")
    return redirect("app:funding_route")

def customer_journey(request):
    routes = Route.objects.all()
    stages = Stage.objects.all()
    return render(request, "home/customer_journey.html", {"funding_routes": routes, "stages":stages})

def add_stage(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        stage = Stage.objects.create(
            name=name,
            description=description,
        )
        messages.success(request, "Stage added successfully!")
        return redirect("app:customer_journey")
    return render(request, "home/add_stage.html")

def cj_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    return render(request, 'home/cj_route.html', {'route':route})

def cj_product(request ,route_id ,product_id):
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stages = Stage.objects.all()
    if request.method == 'POST':
        stage = Stage.objects.get(pk=request.POST.get('stage'))
        product.stage.add(stage)
        product.save()
        messages.success(request, "Stage added to product successfully!")
        return redirect(f"/cj_product/{route_id}/{product_id}")
    return render(
        request, "home/cj_product.html", {"product": product, "stages": stages, "route":route}
    )


def cj_stage(request, route_id, product_id, stage_id):
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)
    questions = Questions.objects.all()
    if request.method == 'POST':
        question = Questions.objects.get(pk=request.POST.get('question'))
        stage.question.add(question)
        stage.save()
        messages.success(request, "Question added to stage successfully!")
        return redirect(f"/cj_stage/{route_id}/{product_id}/{stage_id}")
    return render(request, 'home/cj_stage.html', {'stage':stage, 'questions':questions, 'route':route, 'product':product})


def add_stage_rule(request, route_id, product_id, stage_id,question_id):
    question = Questions.objects.get(pk=question_id)
    if request.method == 'POST':
        dynamicRules = request.POST.getlist('dynamicRule')
        question.rules_regulations = dynamicRules
        question.save()
        messages.success(request, "Rules and Regulations added successfully!")
        return redirect(f"/cj_stage/{route_id}/{product_id}/{stage_id}")

def delete_stage(request, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    stage.delete()
    messages.success(request, "Stage deleted successfully!")
    return redirect("app:customer_journey")

def delete_cj_stage(request, route_id ,product_id, stage_id):
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)
    product.stage.remove(stage)
    product.save()
    messages.success(request, "Stage deleted successfully!")
    return redirect(f"/cj_product/{route_id}/{product_id}")

def delete_cj_stage_question(request, route_id, product_id, stage_id, question_id):
    stage = Stage.objects.get(pk=stage_id)
    question = Questions.objects.get(pk=question_id)
    stage.question.remove(question)
    question.rules_regulations = ''
    question.save()
    stage.save()
    messages.success(request, "Question removed successfully!")
    return redirect(f"/cj_stage/{route_id}/{product_id}/{stage_id}")
