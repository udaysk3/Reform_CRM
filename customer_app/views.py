from django.contrib.auth.decorators import login_required
from user.models import User
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Customers, Answer
from home.models import Campaign, Stage, Client_Council_Route
from admin_app.models import Email, Reason,Signature
from client_app.models import Clients, ClientArchive
from product_app.models import Product
from region_app.models import Councils
from funding_route_app.models import Route
from customer_journey_app.models import CJStage
from question_actions_requirements_app.models import Rule_Regulation, Questions
import re
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import pandas as pd
import requests
from django.db.models import Max
import pytz
from user.models import User
from pytz import timezone
from .task import getLA
from .epc import getEPC
import os, json
from django.core.mail import send_mail
london_tz = pytz.timezone("Europe/London")
from datetime import datetime
import requests
import os.path
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

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
    customer = Customers.objects.get(pk=customer_id)
    display_regions =[]
    regions = Councils.objects.all()
    for region in regions:
        if customer.postcode:
            if customer.postcode.split(' ')[0] in region.postcodes:
                display_regions.append(region)
    child_customers = Customers.objects.all().filter(parent_customer=customer)
    agents = User.objects.filter(is_superuser=False).filter(is_client=False)
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
    client_routes = []
    routes = []
    for route_obj in Client_Council_Route.objects.filter(client=customer.client):
        council = route_obj.council
        route = route_obj.route

        if (
            ClientArchive.objects.filter(
                client=customer.client, route=route, councils=council
            ).exists()
            and route.global_archive == False
        ):
            pass
        else:
            if route.global_archive == False:
                client_routes.append([council , route])

    for region in display_regions:
        council_routes_in_region = region.routes.filter(global_archive=False)
        for council_route in council_routes_in_region:
            if [region, council_route] in client_routes:
                if not ClientArchive.objects.filter(
                    client=customer.client, route=council_route, councils=region
                ).exists():
                    routes.append(council_route)
    products = Product.objects.all().filter(client=customer.client)
    stages = []

    for route in routes:
        for product in products:
            if CJStage.objects.filter(route=route, product=product, client=customer.client).exists():
                cjstages = CJStage.objects.filter(route=route, product=product, client=customer.client)
            else:
                cjstages = CJStage.objects.filter(route=route, product=product, client=None)
            for cjstage in cjstages:
                user = request.user
                if user.is_employee:
                    if cjstage.role:
                        if user.role != cjstage.role.name:
                            continue
                all_answered = True
            
                questions = []
                questions_with_ans = []
                added_ans = set()

                if cjstage.questions:
                    for question in cjstage.questions:
                        qus = Questions.objects.get(pk=question)
                        if qus.is_archive == False:
                            if qus.is_client_archive == False:
                                questions.append(qus)
                else: 
                    for rule in Rule_Regulation.objects.filter(route=route, product=product, stage=cjstage. stage):
                        if rule.question.is_archive == False:
                            if rule.question.is_client_archive == False:
                                questions.append(rule.question)
                
                
                for question in questions:
                    ans = (Answer.objects.filter(route=route)
                                         .filter(product=product)
                                         .filter(stage=cjstage.stage)
                                         .filter(question=question)
                                         .filter(customer=customer))

                    if question not in added_ans:
                        if ans.exists():
                            questions_with_ans.append([question, ans[0], route, product, cjstage.stage])
                            
                        else:
                            questions_with_ans.append([question, None, route, product, cjstage.stage])
                            all_answered = False
                        added_ans.add(question)

                stages.append({
                    'route': route,
                    'product': product,
                    'stage': cjstage.stage,
                    'order': cjstage.order,
                    'questions': questions_with_ans,
                    'all_answered': all_answered
                })

    stages = sorted(stages, key=lambda x: x['order'] if x['order'] is not None else float('inf'))
    previous_all_answered = True
    for i, stage in enumerate(stages):
        stage['all_answered'], previous_all_answered = previous_all_answered, stage['all_answered']
        

    display_stages = {}
    for stage in stages:
        key = f'{stage["route"].name} - {stage["product"].name}'
        if key in display_stages:
            display_stages[key].append([stage['stage'], stage['questions'], stage['all_answered']])
        else:
            display_stages[key] = [[stage['stage'], stage['questions'], stage['all_answered']]]

    for route_product, stages in display_stages.items():
        for i, (stage, question_ans, all_ans) in enumerate(stages):
            route = route_product.split(' - ')[0]
            product = route_product.split(' - ')[1]
            correct_stage = True
            new_question_ans = []
            for question, ans, route, product, stage in question_ans:
                correct_ans = True
                if ans == None:
                    correct_ans = False
                elif ans.submit == True:
                    correct_ans = True
                elif ans.question.type == 'file':
                    if ans.file != '':
                        correct_ans = True
                elif ans.answer == [''] or ans.answer == '' or ans.answer == []:
                    correct_ans = False
                else:
                    rule_requirements = Rule_Regulation.objects.filter(route=route, product=product, stage=stage, question=question, is_client=False)
                    if rule_requirements:
                        if rule_requirements[0].rules_regulation:
                            rule = rule_requirements[0]
                            
                            type = question.type.split(',')
                            if len(type) > 1:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    rule_values = rule.rules_regulation[0].split(',')
                                    correct_ans = False
                                    if 'all_value' in rule.rules_regulation:
                                        arr = ans.answer[0].split(',')
                                        correct_ans = arr == rule_values
                                    else:
                                        for el in ans.answer[0].split(','):
                                            if el in rule_values:
                                                correct_ans = True
                                                break
                            if type[0] in ['text', 'email', 'password', 'phone']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                    print(ans.answer, rule.rules_regulation)
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            if type[0] == 'checkbox':
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            
                            if type[0] in ['date', 'month', 'time', 'number']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    if type[0] == 'date' or type[0] == 'month':
                                        answer_date = datetime.strptime(ans.answer[0], '%Y-%m-%d')
                                        rule_date = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%Y-%m-%d')
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date < rule_date
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date > rule_date
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_date == rule_date

                                    elif type[0] == 'time':
                                        answer_time = datetime.strptime(ans.answer[0], '%H:%M:%S').time()
                                        rule_time = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%H:%M:%S').time()
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time < rule_time
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time > rule_time
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_time == rule_time

                                    elif type[0] == 'number':
                                        answer_number = int(ans.answer[0])
                                        rule_number = int(rule.rules_regulation[0].split(',')[0])

                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number < rule_number
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number > rule_number
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_number == rule_number
                    else:
                        correct_ans = True
                
                correct_stage =  correct_stage and correct_ans
                new_question_ans.append((question, ans, route, product, stage, correct_ans))

            stages[i] = (stage, new_question_ans, correct_stage)
    

    
    for route_product, stages in display_stages.items():
        for i, (stage, question_ans, all_ans) in enumerate(stages):
            route = route_product.split(' - ')[0]
            product = route_product.split(' - ')[1]
            correct_stage = True
            new_question_ans = []
            for question, ans, route, product, stage, is_correct in question_ans:
                correct_ans = True
                if ans == None:
                    correct_ans = False
                elif ans.submit == True:
                    correct_ans = True
                elif ans.question.type == 'file':
                    if ans.file != '':
                        correct_ans = True
                elif ans.answer == [''] or ans.answer == '' or ans.answer == []:
                    correct_ans = False
                else:
                    rule_requirements = Rule_Regulation.objects.filter(route=route, product=product, stage=stage, question=question, is_client=True)
                    if rule_requirements:
                        if rule_requirements[0].rules_regulation:
                            rule = rule_requirements[0]
                            type = question.type.split(',')
                            if len(type) > 1:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    rule_values = rule.rules_regulation[0].split(',')
                                    correct_ans = False
                                    if 'all_value' in rule.rules_regulation:
                                        arr = ans.answer[0].split(',')
                                        correct_ans = arr == rule_values
                                    else:
                                        for el in ans.answer[0].split(','):
                                            if el in rule_values:
                                                correct_ans = True
                                                break
                            if type[0] in ['text', 'email', 'password', 'phone']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            if type[0] == 'checkbox':
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            if type[0] in ['date', 'month', 'time', 'number']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    if type[0] == 'date' or type[0] == 'month':
                                        answer_date = datetime.strptime(ans.answer[0], '%Y-%m-%d')
                                        rule_date = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%Y-%m-%d')
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date < rule_date
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date > rule_date
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_date == rule_date
                                    elif type[0] == 'time':
                                        answer_time = datetime.strptime(ans.answer[0], '%H:%M:%S').time()
                                        rule_time = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%H:%M:%S').time()
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time < rule_time
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time > rule_time
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_time == rule_time
                                    elif type[0] == 'number':
                                        answer_number = int(ans.answer[0])
                                        rule_number = int(rule.rules_regulation[0].split(',')[0])
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number < rule_number
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number > rule_number
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_number == rule_number
                    else:
                        correct_ans = True
                correct_stage =  correct_stage and correct_ans
                
                new_question_ans.append((question, ans, route, product, stage, correct_ans))
            stages[i] = (stage, new_question_ans, correct_stage)

    current_route_product = None
    last_route_product = None
    current_nums =0
    total_nums = 0
    for route_product, stages in display_stages.items():
        all_true_for_product = True  

        for i, (stage, question_ans, all_ans) in enumerate(stages):
            if not all_ans:
                current_route_product = [stages, 100 / len(stages), route_product]
                all_true_for_product = False
                break

        if all_true_for_product:
            last_route_product = [stages, 100 / len(stages), route_product]
        else:
            break

    if current_route_product is None:
        current_route_product = last_route_product


    for route_product, stages in display_stages.items():
        if current_route_product[2] == route_product:
            for i, (stage, question_ans, all_ans) in enumerate(stages):
                current_nums += 1
                if not all_ans:
                    total_nums = len(stages)
                    break

    

    current_stage = None
    for route_product, stages in display_stages.items():
        for i, (stage, question_ans, all_ans) in enumerate(stages):
            if all_ans == False:
                current_stage = question_ans
                break
        if current_stage != None:

            break
    
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
            "epc_data": customer.epc_data,
            "routes": routes,
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
            "display_regions":display_regions,
            "display_stages":display_stages,
            "current_route_product":current_route_product,
            "current_stage": current_stage,
            "current_nums": current_nums,
            "total_nums": total_nums,
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
    search_query = request.GET.get("search", "").strip()
    current_time = datetime.now(london_tz)
    user  = request.user
    if user.is_employee:
        clients_with_customers = Clients.objects.filter(assigned_to=user).prefetch_related('customers')
        customers_list = []
        for client in clients_with_customers:
            customers_list.extend(client.customers.all())
        customers = customers_list
    else:
        customers = (
            Customers.objects
            .annotate(earliest_action_date=Max("action__date_time"))
            .filter(parent_customer=None)
            .filter(closed=False)
            .order_by("earliest_action_date")
        )

    if search_query:
        # Filter by first name, last name, or postcode
        customers = Customers.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(postcode__icontains=search_query)
        )
    else:
        # Sort and prepare customers as usual
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
        customers = new_customers + result
        customers = customers[::-1]
    campaigns = Campaign.objects.all()
    unassigned_customers = Customers.objects.filter(assigned_to=None)
    agents = User.objects.filter(is_employee=True)
    p_customers = Paginator(customers, 15)
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
        request, "home/customer.html", {"customers": p_customers, "current_date": datetime.now(london_tz).date, "campaigns": campaigns, "agents": agents, 'page_obj': page_obj, 'clients':client,  "search_query": search_query}
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

    customers= new_customers + result
    campaigns = Campaign.objects.all()
    unassigned_customers = Customers.objects.filter(assigned_to=None)
    agents = User.objects.filter(is_superuser=False).filter(is_client=False).filter(is_employee=False)
    if request.session.get("first_name"):
        delete_customer_session(request)
    return render(
        request, "home/archive.html", {"customers": customers, "current_date": datetime.now(london_tz).date, "campaigns": campaigns,"agents": serialize('json', agents)}
    )

@login_required
def add_customer(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name").upper()
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email").lower()
        postcode = request.POST.get("postcode").upper()
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
        elif phone_number[0] == "4" and phone_number[1] == "4":
            phone_number = "+" + phone_number
        elif phone_number[0] != "+":
            phone_number = "+44" + phone_number
        if phone_number[-2:] == ".0":
            phone_number = phone_number[:-2]

        if Customers.objects.filter(email__iexact=email).filter(client=client).exists():
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
        if ' ' not in postcode:
            postcode = postcode[:-3] + " " + postcode[-3:]
        uk = Councils.objects.get(name='UK')
        if postcode[:-3] not in uk.postcodes.split(','):
            uk_postcodes = os.path.join(os.path.dirname(__file__), './uk_postcodes.txt')
            with open(uk_postcodes, 'a') as f:
                f.write(',' + postcode[:-3].strip())
            uk.postcodes += ',' + postcode[:-3].strip()
            uk.save()
            
        district = getLA(postcode)
        obj = getEPC(postcode, house_name, street_name)
        energy_rating = None
        energy_certificate_link = None
        address = house_name + " " + street_name
        constituency = None
        epc_data = None
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
            processed_epc_data = dict()
            if obj["epc_data"]:
                for key, value in obj["epc_data"].items():
                    key_formatted = key.replace("_", " ").replace("-"," ").title()
                    if value == "":
                        processed_epc_data[key_formatted] = "Not Available"
                    else:
                        processed_epc_data[key_formatted] = value
        customer = Customers.objects.create(
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
            address=address,
            council=Councils.objects.get(name='UK'),
            district=district,
            constituency=constituency,
            campaign=Campaign.objects.get(id=campaign),
            client=Clients.objects.get(pk=client),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            primary_customer=True,
            energy_rating=energy_rating,
            energy_certificate_link=energy_certificate_link,
            recommendations=recommendations,
            epc_data=processed_epc_data,
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
        return redirect("customer_app:customer")
    return render(request, "home/customer.html")


@login_required
def edit_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    if request.method == "POST":
        changed = ''
        if customer.phone_number != request.POST.get("phone_number"):
            changed += f'{request.POST.get("phone_number")}, '
        if customer.email != request.POST.get('email').lower():
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
        phone_number = request.POST.get("phone_number")
        if phone_number[0] == "0":
            phone_number = phone_number[1:]
            phone_number = "+44" + phone_number
        elif phone_number[0] == "4" and phone_number[1] == "4":
            phone_number = "+" + phone_number
        elif phone_number[0] != "+":
            phone_number = "+44" + phone_number
        if phone_number[-2:] == ".0":
            phone_number = phone_number[:-2]
        customer.phone_number = phone_number
        email = request.POST.get("email").lower()
        if Customers.objects.filter(email__iexact=email).filter(client=customer.client).exists():
            messages.error(request, "Email with this Client already exists")
            return redirect(f"/customer?page=edit_customer&id={customer_id}")
        customer.email = email
        postcode = re.sub(r'\s+', ' ', request.POST.get("postcode").upper())
        customer.street_name = request.POST.get("street_name")
        customer.city = request.POST.get("city")
        customer.house_name = request.POST.get("house_name")
        customer.county = request.POST.get("county")
        customer.country = request.POST.get("country")
        if customer.campaign == "nan" or customer.city == "nan" or customer.county == "nan" or customer.country == "nan":
            messages.error(request, "Select all dropdown fields")
            return redirect(f"/customer?page=edit_customer&id={customer_id}")
        if " " not in postcode:
            postcode = postcode[:-3] + " " + postcode[-3:]
        uk = Councils.objects.get(name='UK')
        if postcode[:-3] not in uk.postcodes.split(','):
            uk_postcodes = os.path.join(os.path.dirname(__file__), './uk_postcodes.txt')
            with open(uk_postcodes, 'a') as f:
                f.write(',' + postcode[:-3].strip())
            uk.postcodes += ',' + postcode[:-3].strip()
            uk.save()
        district = getLA(customer.postcode)
        obj = getEPC(customer.postcode, customer.house_name, customer.street_name)
        energy_rating = None
        energy_certificate_link = None
        address = customer.house_name + " " + customer.street_name
        constituency = None
        epc_data = None
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
            processed_epc_data = dict()
            if obj["epc_data"]:
                for key, value in obj["epc_data"].items():
                    key_formatted = key.replace("_", " ").replace("-"," ").title()
                    if value == "":
                        processed_epc_data[key_formatted] = "Not Available"
                    else:
                        processed_epc_data[key_formatted] = value
        customer.postcode = postcode
        customer.energy_rating = energy_rating
        customer.energy_certificate_link = energy_certificate_link
        customer.address = address
        customer.constituency = constituency
        customer.recommendations = recommendations
        customer.epc_data = processed_epc_data
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
def remove_customer(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.delete()

    messages.success(request, "Customer deleted successfully!")
    return redirect("customer_app:customer")



def note_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        talked_with = request.POST.get("talked_customer")
        date_str = request.POST.get("date_field")
        date_time_str = f"{date_str} 00:00"
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
            action_type="Note",
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect("/customer-detail/" + str(customer_id))


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

def na_action_submit(request, customer_id):
    if request.method == "POST":
        customer = Customers.objects.get(id=customer_id)
        date_str = datetime.now(london_tz).strftime("%Y-%m-%d")
        time_str = datetime.now(london_tz).strftime("%H:%M")
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=180)
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
        time_obj += timedelta(minutes=180)
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
    message = []
    
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        campaign = request.POST.get("campaign")
        client = request.POST.get("client")
        
        if campaign == "nan":
            messages.error(request, "Select a Campaign")
            return redirect("customer_app:import_customers")
        
        df = pd.read_excel(excel_file)
        excel_columns = df.columns.tolist()
        column_mappings = []
        
        # Retrieve column mappings
        for i, column in enumerate(excel_columns):
            attribute = request.POST.get(f"column{i}", "")
            column_mappings.append(attribute)

        # Check if mandatory columns are mapped
        if not all(field in column_mappings for field in ["email", "first_name", "last_name", "phone_number"]):
            messages.error(
                request,
                "First Name, Last Name, Phone Number, and Email fields should be mapped.",
            )
            return redirect("customer_app:import_customers")

        for index, row in df.iterrows():
            district = None
            customer_data = {}
            missing_mandatory_field = False  # Flag to check if any mandatory field is missing

            for i, column in enumerate(excel_columns):
                value = str(row[i]).strip()
                
                # Check if mandatory fields are empty
                if column_mappings[i] in ["email", "first_name", "last_name", "phone_number"] and (
                    not value or value.lower() in ["nan", "nat", "none"]
                ):
                    missing_mandatory_field = True
                    break
            
                if column_mappings[i] == "history":
                    history[excel_columns[i]] = value
                elif column_mappings[i] == "last_name":
                    customer_data[column_mappings[i]] = value.upper()
                elif column_mappings[i] == "phone_number":
                    phone_number = value
                    if phone_number[0] == "0":
                        phone_number = "+44" + phone_number[1:]
                    elif phone_number[0] == "4" and phone_number[1] == "4":
                        phone_number = "+" + phone_number
                    elif phone_number[0] != "+":
                        phone_number = "+44" + phone_number
                    if phone_number[-2:] == ".0":
                        phone_number = phone_number[:-2]
                    customer_data[column_mappings[i]] = phone_number
                elif column_mappings[i] == "postcode":
                    postcode = value
                    url = "https://api.postcodes.io/postcodes/" + postcode.strip()
                    try:
                        response = requests.get(url, headers={"muteHttpExceptions": "true"})
                        if response.status_code == 200:
                            json_data = response.json()
                            status = json_data.get("status")
                            if status == 200:
                                district = json_data["result"]["admin_district"]
                            else:
                                district = "Invalid postcode or not found"
                        else:
                            district = "Error fetching data"
                    except requests.exceptions.RequestException:
                        district = "Request Error"
                    customer_data[column_mappings[i]] = re.sub(r'\s+', ' ', postcode)
                else:
                    customer_data[column_mappings[i]] = value

            # Skip creating customer if any mandatory field is missing
            if missing_mandatory_field:
                continue

            # Check for existing customer by email or phone number
            if Customers.objects.filter(email=customer_data['email']).exists() or \
               Customers.objects.filter(phone_number=customer_data['phone_number']).exists():
                message.append(f'{customer_data["first_name"]} {customer_data["last_name"]}')
                continue

            # Ensure campaign and client are selected
            if campaign == "nan" or client == "nan":
                messages.error(request, "Select all dropdown fields")
                return redirect("/customer?page=add_customer")

            # Create and save customer
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
            
            # Add action history for customer
            for key, value in history.items():
                customer.add_action(
                    text=f"{key} : {value}",
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
                action_type=f"Added {customer.first_name} {customer.last_name}, {customer.phone_number}, {customer.email}",
                keyevents=True,
            )
        
        # Show success or error messages
        if message:
            messages.error(request, f"Customer(s) with duplicate email or phone number: {', '.join(message)}")
        else:
            messages.success(request, "Customers imported successfully.")
        
        return redirect("customer_app:customer")

    campaigns = Campaign.objects.all()
    clients = Clients.objects.all()
    
    return render(
        request,
        "home/import_customers.html",
        {"excel_columns": excel_columns, "campaigns": campaigns, "clients": clients},
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
        return redirect("customer_app:customer")
    return render(request, "home/customer_list.html")


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


@login_required
def set_customer_route(request, customer_id, route_id):
    customer = Customers.objects.get(pk=customer_id)
    route = Route.objects.get(pk=route_id)
    customer.route = route
    customer.save()
    messages.success(request, "Route set successfully!")
    return redirect(f"/customer-detail/{customer_id}")

def remove_customer_route(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    customer.route = None
    customer.save()
    messages.success(request, "Route removed successfully!")
    return redirect(f"/customer-detail/{customer_id}")


def assign_agents(request):
    if request.method == "POST":
     try:
        agent_id = request.POST.get("agent_id")
        customer_ids = request.POST.get("customers").split(",")
        agent = User.objects.get(pk=agent_id)
        clients_with_customers = Clients.objects.filter(assigned_to=agent).prefetch_related('customers')
        customers_list = []
        for client in clients_with_customers:
            customers_list.extend(client.customers.all())
        for customer_id in customer_ids:
            print(customer_ids, customers_list)
            customer = Customers.objects.get(pk=customer_id)
            if customer not in customers_list:
                messages.error(request,f"Customer {customer.first_name} {customer.last_name} can not be assigned to the {agent.first_name} {agent.last_name}")
            else:
                customer.assigned_to =  agent
                customer.save()
                customer.add_action(
                    agent=User.objects.get(email=request.user),
                    date_time=datetime.now(pytz.timezone("Europe/London")),
                    created_at=datetime.now(pytz.timezone("Europe/London")),
                    action_type="Assigned to Agent",
                )
        messages.success(request, "Customers Assigned successfully!")
        return redirect("customer_app:customer")
     except Exception as e:
        messages.error(request, f"Error assigning customers: {e}")
        return redirect("customer_app:customer")
    else:
        messages.error(request, "Cannot Assign customers!")
        return redirect("customer_app:customer")

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



def add_stage_ans(request, route_id, product_id, stage_id, question_id, customer_id):
    question = Questions.objects.get(pk=question_id)
    customer = Customers.objects.get(pk=customer_id)

    if request.method == "POST":
        dynamicAns = request.POST.getlist("dynamicRule")
        
        rules = Rule_Regulation.objects.filter(question=question, is_client=False)
        
        for rule in rules:
            answer = Answer.objects.filter(
                route=rule.route, product=rule.product, stage=rule.stage, question=question, customer=customer
            ).first()

            if answer:
                answer.answer = dynamicAns
                answer.save()
            else:
                answer = Answer.objects.create(
                    route=rule.route,
                    product=rule.product,
                    stage=rule.stage,
                    question=question,
                    customer=customer,
                    answer=dynamicAns,
                )

            if 'dynamicRule' in request.FILES:
                uploaded_file = request.FILES['dynamicRule']
                answer.file = uploaded_file
                answer.save()

    return JsonResponse({'status': 'success'}, status=200)

def check_stage_ans(request, route_id, product_id, stage_id, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    main_stage = Stage.objects.get(pk=stage_id)
    stages = []

    if CJStage.objects.filter(route=route, product=product, client=customer.client).exists():
        cjstages = CJStage.objects.filter(route=route, product=product, client=customer.client)
    else:
        cjstages = CJStage.objects.filter(route=route, product=product, client=None)
    for cjstage in cjstages:
        user = request.user
        if user.is_employee:
            if cjstage.role:
                if user.role != cjstage.role.name:
                    continue
        all_answered = True
    
        questions = []
        questions_with_ans = []
        added_ans = set()
        if cjstage.questions:
            for question in cjstage.questions:
                qus = Questions.objects.get(pk=question)
                if qus.is_archive == False:
                    if qus.is_client_archive == False:
                        questions.append(qus)
        else: 
            for rule in Rule_Regulation.objects.filter(route=route, product=product, stage=cjstage. stage):
                if rule.question.is_archive == False:
                    if rule.question.is_client_archive == False:
                        questions.append(rule.question)
        
        
        for question in questions:
            ans = (Answer.objects.filter(route=route)
                                 .filter(product=product)
                                 .filter(stage=cjstage.stage)
                                 .filter(question=question)
                                 .filter(customer=customer))
            if question not in added_ans:
                if ans.exists():
                    questions_with_ans.append([question, ans[0], route, product, cjstage.stage])
                    
                else:
                    questions_with_ans.append([question, None, route, product, cjstage.stage])
                    all_answered = False
                added_ans.add(question)
        stages.append({
            'route': route,
            'product': product,
            'stage': cjstage.stage,
            'order': cjstage.order,
            'questions': questions_with_ans,
            'all_answered': all_answered
        })

    stages = sorted(stages, key=lambda x: x['order'] if x['order'] is not None else float('inf'))
    previous_all_answered = True
    for i, stage in enumerate(stages):
        stage['all_answered'], previous_all_answered = previous_all_answered, stage['all_answered']
        

    display_stages = {}
    for stage in stages:
        key = f'{stage["route"].name} - {stage["product"].name}'
        if key in display_stages:
            display_stages[key].append([stage['stage'], stage['questions'], stage['all_answered']])
        else:
            display_stages[key] = [[stage['stage'], stage['questions'], stage['all_answered']]]

    for route_product, stages in display_stages.items():
        for i, (stage, question_ans, all_ans) in enumerate(stages):
            route = route_product.split(' - ')[0]
            product = route_product.split(' - ')[1]
            correct_stage = True
            new_question_ans = []
            for question, ans, route, product, stage in question_ans:
                correct_ans = True
                if ans == None:
                    correct_ans = False
                elif ans.submit == True:
                    correct_ans = True
                elif ans.question.type == 'file':
                    if ans.file != '':
                        correct_ans = True
                elif ans.answer == [''] or ans.answer == '' or ans.answer == []:
                    correct_ans = False
                else:
                    rule_requirements = Rule_Regulation.objects.filter(route=route, product=product, stage=stage, question=question, is_client=False)
                    if rule_requirements:
                        if rule_requirements[0].rules_regulation:
                            rule = rule_requirements[0]
                            
                            type = question.type.split(',')
                            if len(type) > 1:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    rule_values = rule.rules_regulation[0].split(',')
                                    correct_ans = False
                                    if 'all_value' in rule.rules_regulation:
                                        arr = ans.answer[0].split(',')
                                        correct_ans = arr == rule_values
                                    else:
                                        for el in ans.answer[0].split(','):
                                            if el in rule_values:
                                                correct_ans = True
                                                break
                            if type[0] in ['text', 'email', 'password', 'phone']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                    print(ans.answer, rule.rules_regulation)
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            if type[0] == 'checkbox':
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            
                            if type[0] in ['date', 'month', 'time', 'number']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    if type[0] == 'date' or type[0] == 'month':
                                        answer_date = datetime.strptime(ans.answer[0], '%Y-%m-%d')
                                        rule_date = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%Y-%m-%d')
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date < rule_date
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date > rule_date
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_date == rule_date

                                    elif type[0] == 'time':
                                        answer_time = datetime.strptime(ans.answer[0], '%H:%M:%S').time()
                                        rule_time = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%H:%M:%S').time()
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time < rule_time
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time > rule_time
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_time == rule_time

                                    elif type[0] == 'number':
                                        answer_number = int(ans.answer[0])
                                        rule_number = int(rule.rules_regulation[0].split(',')[0])

                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number < rule_number
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number > rule_number
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_number == rule_number
                    else:
                        correct_ans = True
                
                correct_stage =  correct_stage and correct_ans
                new_question_ans.append((question, ans, route, product, stage, correct_ans))

            stages[i] = (stage, new_question_ans, correct_stage)
    

    
    for route_product, stages in display_stages.items():
        for i, (stage, question_ans, all_ans) in enumerate(stages):
            route = route_product.split(' - ')[0]
            product = route_product.split(' - ')[1]
            correct_stage = True
            new_question_ans = []
            for question, ans, route, product, stage, is_correct in question_ans:
                correct_ans = True
                if ans == None:
                    correct_ans = False
                elif ans.submit == True:
                    correct_ans = True
                elif ans.question.type == 'file':
                    if ans.file != '':
                        correct_ans = True
                elif ans.answer == [''] or ans.answer == '' or ans.answer == []:
                    correct_ans = False
                else:
                    rule_requirements = Rule_Regulation.objects.filter(route=route, product=product, stage=stage, question=question, is_client=True)
                    if rule_requirements:
                        if rule_requirements[0].rules_regulation:
                            rule = rule_requirements[0]
                            type = question.type.split(',')
                            if len(type) > 1:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    rule_values = rule.rules_regulation[0].split(',')
                                    correct_ans = False
                                    if 'all_value' in rule.rules_regulation:
                                        arr = ans.answer[0].split(',')
                                        correct_ans = arr == rule_values
                                    else:
                                        for el in ans.answer[0].split(','):
                                            if el in rule_values:
                                                correct_ans = True
                                                break
                            if type[0] in ['text', 'email', 'password', 'phone']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            if type[0] == 'checkbox':
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    correct_ans = ans.answer == rule.rules_regulation
                            if type[0] in ['date', 'month', 'time', 'number']:
                                if ans.answer == [''] or ans.answer[0] == '':
                                    correct_ans = False
                                else:
                                    if type[0] == 'date' or type[0] == 'month':
                                        answer_date = datetime.strptime(ans.answer[0], '%Y-%m-%d')
                                        rule_date = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%Y-%m-%d')
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date < rule_date
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_date > rule_date
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_date == rule_date
                                    elif type[0] == 'time':
                                        answer_time = datetime.strptime(ans.answer[0], '%H:%M:%S').time()
                                        rule_time = datetime.strptime(rule.rules_regulation[0].split(',')[0], '%H:%M:%S').time()
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time < rule_time
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_time > rule_time
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_time == rule_time
                                    elif type[0] == 'number':
                                        answer_number = int(ans.answer[0])
                                        rule_number = int(rule.rules_regulation[0].split(',')[0])
                                        if 'Less Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number < rule_number
                                        elif 'Greater Than' in rule.rules_regulation[0]:
                                            correct_ans = answer_number > rule_number
                                        elif 'Equal' in rule.rules_regulation[0]:
                                            correct_ans = answer_number == rule_number
                    else:
                        correct_ans = True
                correct_stage =  correct_stage and correct_ans
                
                new_question_ans.append((question, ans, route, product, stage, correct_ans))
            stages[i] = (stage, new_question_ans, correct_stage)

    all_correct = True
    for route_product, stages in display_stages.items():
        for i, (stage, question_ans, all_ans) in enumerate(stages):
            if main_stage == stage:
                if all_ans == False:
                    all_correct = False
                    break
    
    return JsonResponse({'status': 'success', 'all_correct': all_correct}, status=200)


def add_submit_stage_ans(request, route_id, product_id, stage_id, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)

    if request.method == "POST":
        rules = Rule_Regulation.objects.filter(route=route, product=product, is_client=False)
        for rule in rules:
            if Answer.objects.filter(route=route, product=product, stage=rule.stage, customer=customer, question=rule.question).exists():
                answer = Answer.objects.get(route=route, product=product, stage=rule.stage, customer=customer, question=rule.question)
                answer.submit = True
                answer.save()
            else:
                Answer.objects.create(route=route, product=product, stage=rule.stage, customer=customer, question=rule.question, submit=True)
    return JsonResponse({'status': 'success'}, status=200)

def get_agent_customers(request, agent_id):
    agent = User.objects.get(pk=agent_id)
    clients_with_customers = Clients.objects.filter(assigned_to=agent).prefetch_related('customers')
    customers_list = []
    for client in clients_with_customers:
        customers_list.extend(client.customers.all())
    return JsonResponse([{"customer_id": customer.id, "customer_first_name":customer.first_name, "customer_last_name":customer.last_name} for customer in customers_list], safe=False)

def refresh_epc(request, customer_id):
    customer = Customers.objects.get(pk=customer_id)
    obj = getEPC(customer.postcode, customer.house_name, customer.street_name)
    energy_rating = None
    energy_certificate_link = None
    constituency = None
    epc_data = None
    if obj is not None:
        energy_rating = obj["energy_rating"]
        energy_certificate_link = obj["energy_certificate_link"]
        constituency = obj["constituency"] if obj["constituency"] else None
        recommendations = obj["recommendations"] if obj["recommendations"] else None
        processed_epc_data = dict()
        if obj["epc_data"]:
            for key, value in obj["epc_data"].items():
                key_formatted = key.replace("_", " ").replace("-"," ").title()
                if value == "":
                    processed_epc_data[key_formatted] = "Not Available"
                else:
                    processed_epc_data[key_formatted] = value
    customer.energy_rating = energy_rating
    customer.energy_certificate_link = energy_certificate_link
    customer.constituency = constituency
    customer.recommendations = recommendations
    customer.epc_data = processed_epc_data
    customer.save()
    messages.success(request, "EPC refreshed successfully!")
    return redirect(f"/customer-detail/{customer_id}")
