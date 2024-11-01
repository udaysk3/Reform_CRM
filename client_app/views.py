import json
import os
import os.path
import re
from datetime import datetime, timedelta

from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db.models import Max, Exists, OuterRef
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.cache import cache_page

from admin_app.models import Email, Reason, Signature
from client_app.models import ClientArchive, Clients, CoverageAreas
from customer_app.models import Action
from customer_app.epc import getEPC
from customer_app.task import getLA
from customer_journey_app.models import CJStage
from funding_route_app.models import Route
from home.models import Campaign, Client_Council_Route, Stage
from product_app.models import Product
from question_actions_requirements_app.models import Questions, Rule_Regulation
from region_app.models import Councils, RegionArchive
from user.models import User

import pytz
london_tz = pytz.timezone("Europe/London")

@login_required
def client_detail(request, client_id, s_client_id=None):
    prev = None
    next = None
    domain_name = request.build_absolute_uri("/")[:-1]
    signatures = Signature.objects.all()
    coverage_areas = CoverageAreas.objects.all().filter(
        client=Clients.objects.get(pk=client_id)
    )

    regions = Councils.objects.all()
    display_regions = {}

    for region in regions:
        region_postcodes = region.postcodes.split(',')
        covered_postcodes = []

        for coverage_area in coverage_areas:
            if coverage_area.postcode in region_postcodes:
                covered_postcodes.append(coverage_area.postcode)

        if len(covered_postcodes) == len(region_postcodes):
            display_regions[region] = 'All'
        elif len(covered_postcodes) > 0:
            display_regions[region] = 'Partial'
        else:
            display_regions[region] = 'None'

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
    client = Clients.objects.get(pk=client_id)
    campaigns = Campaign.objects.all().filter(client=client).filter(archive=False)
    uncampaigns = Campaign.objects.all().filter(client=client).filter(archive=True)
    all_products = Product.objects.all().filter(global_archive=False)
    products = list(Product.objects.all().filter(client=client).filter(global_archive=False))
    unproducts = []
    for prod in products[:]: 
        if ClientArchive.objects.all().filter(client=client).filter(product=prod).exists():
            unproducts.append(prod)
            products.remove(prod)

    councils = Councils.objects.all()
    coverage_area_client = CoverageAreas.objects.filter(client=client)
    council_coverage_area = []
    for coun in councils:
        for ca in coverage_area_client:
            if ca.postcode in coun.postcodes.split(',') and coun not in council_coverage_area:
                council_coverage_area.append(coun)
    all_routes = {}
    for council in council_coverage_area:
        for route in council.routes.all():
            if all_routes.get(council) and route.global_archive == False:
                all_routes[council].append(route)
            else:
                if route.global_archive == False:
                    all_routes[council] = [route]

    d_routes = {}
    d_unroutes = {}

    for route_obj in Client_Council_Route.objects.filter(client=client):
        council = route_obj.council
        route = route_obj.route

        if (
            ClientArchive.objects.filter(
                client=client, route=route, councils=council
            ).exists()
            and route.global_archive == False
        ):
            if council not in d_unroutes:
                d_unroutes[council] = []
            d_unroutes[council].append(route)
        else:
            if route.global_archive == False:
                if council not in d_routes:
                    d_routes[council] = []
                d_routes[council].append(route)
            else:
                if council not in d_unroutes:
                    d_unroutes[council] = []
                d_unroutes[council].append(route)

    routes = {}
    unroutes = d_unroutes

    for council, routes_list in d_routes.items():
        for route in routes_list:
            if (
                RegionArchive.objects.filter(council=council, route=route).exists()
            ):
                if council not in unroutes:
                    unroutes[council] = []
                unroutes[council].append(route)
            else:
                if council not in routes:
                    routes[council] = []
                routes[council].append(route)
    stages = []
    for council, council_routes in routes.items():
        for route in council_routes:
            for product in products:
                cjstages = CJStage.objects.filter(route=route, product=product)
                for cjstage in cjstages:
                    questions = []
                    questions_with_rules = []
                    added_questions = set()
                    
                    for rule in Rule_Regulation.objects.filter(route=route, product=product, stage=cjstage.stage,is_client=False):
                        questions.append(rule.question)
                        
                    
                    for question in questions:
                        rule_regulation = (Rule_Regulation.objects
                                           .filter(route=route)
                                           .filter(product=product)
                                           .filter(stage=cjstage.stage)
                                           .filter(question=question)
                                           .filter(is_client=True))
                       
                        if question not in added_questions:
                            if rule_regulation.exists():
                                questions_with_rules.append((question, rule_regulation[0], route, product, cjstage.stage))
                            else:
                                questions_with_rules.append((question, None, route, product, cjstage.stage))
                            
                            added_questions.add(question)
                    
                    stages.append({
                        'route': route,
                        'product': product,
                        'stage': cjstage.stage, 
                        'order': cjstage.order, 
                        'questions': questions_with_rules
                    })
    
    stages = sorted(stages, key=lambda x: x['order'] if x['order'] is not None else float('inf'))
    
    display_stages = {}
    for stage in stages:
        key = f"{stage['route'].name} - {stage['product'].name}"
    
        if key in display_stages:
            display_stages[key].append([stage['stage'], stage['questions']])
        else:
            display_stages[key] = [[stage['stage'], stage['questions']]]


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
                "councils": councils,
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
                "coverage_areas": coverage_area_client,
                "all_products": all_products,
                "all_routes": all_routes,
                "routes": routes,
                "unroutes": unroutes,
                "stages": stages,
                "display_regions": display_regions,
                "display_stages":display_stages,
            },
        )

    return render(
        request,
        "home/client-detail.html",
        {
            "councils": councils,
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
            "coverage_areas": coverage_area_client,
            "all_products": all_products,
            "all_routes": all_routes,
            "routes": routes,
            "unroutes": unroutes,
            "stages": stages,
            "display_regions": display_regions,
            "display_stages":display_stages,
        },
    ) 

@login_required
def client(request):
    """
    View function to display the list of clients.
    """
    if request.session.get("first_name"):
        delete_customer_session(request)

    # Handle editing a client
    if request.GET.get("page") == "edit_client" and request.GET.get("backto") is None:
        client_id = request.GET.get("id")
        client = get_object_or_404(Clients, pk=client_id)
        edit_client = client
        if client.parent_client:
            client = client.parent_client
        clients = Clients.objects.filter(parent_client=client)
        context = {
            "edit_client": edit_client,
            "client": client,
            "clients": clients,
        }
        return render(request, "home/client.html", context)

    clients = (
        Clients.objects
        .filter(parent_client=None, closed=False)
        .annotate(
            earliest_action_date=Max("action__date_time"),
            has_nonimported_action=Exists(
                Action.objects.filter(client=OuterRef('pk'), imported=False)
            ),
        )
        .order_by("-has_nonimported_action", "-earliest_action_date")
    )

    campaigns = Campaign.objects.all()
    agents = User.objects.filter(is_superuser=False)
    paginator = Paginator(clients, 50)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        "clients": page_obj,
        "current_date": timezone.now().date(),
        "campaigns": campaigns,
        "agents": serialize('json', agents),
        "page_obj": page_obj,
    }
    return render(request, "home/client.html", context)

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
        postcode = request.POST.get("postcode").upper()
        street_name = request.POST.get("street_name")
        house_name = request.POST.get("house_name")
        city = request.POST.get("city")
        county = request.POST.get("county")
        country = request.POST.get("country")
        agent = User.objects.get(email=request.user)
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(request.POST.get("password")),
            is_client=True,
        )

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

        if " " not in postcode:
            postcode = postcode[:-3] + " " + postcode[-3:]
        uk = Councils.objects.get(name="UK")
        if postcode[:-3] not in uk.postcodes.split(","):
            uk_postcodes = os.path.join(
                os.path.dirname(__file__), "./uk_postcodes.txt"
            )
            
            with open(uk_postcodes, "a") as f:
                f.write("," + postcode[:-3].strip())
            uk.postcodes += "," + postcode[:-3].strip()
            uk.save()
        postcode = re.sub(r'\s+', ' ', postcode)
        district = getLA(postcode)
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

        client = Clients.objects.create(
            acc_number=acc_number,
            sort_code=sort_code,
            iban=iban,
            bic_swift=bic_swift,
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
            energy_rating=energy_rating,
            energy_certificate_link=energy_certificate_link,
            recommendations=recommendations,
            address=address,
            district=district,
            constituency=constituency,
            user=user,
        )
        client.add_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type=f"Added {client.first_name}  {client.last_name},  {client.house_name },  {client.phone_number},  {client.email}, {client.house_name},  {client.street_name},  {client.city},  {client.county},  {client.country}",
                keyevents=True,
        )
        messages.success(request, "Client added successfully!")
        return redirect("client_app:client")
    return redirect("/client")


@login_required
def edit_client(request, client_id):
    client = Clients.objects.get(pk=client_id)
    user = client.user
    user.first_name = request.POST.get("first_name")
    user.last_name = request.POST.get("last_name")
    user.email = request.POST.get("email")
    user.password = make_password(request.POST.get("password"))
    user.save()
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
        client.postcode = re.sub(r'\s+', ' ', request.POST.get("postcode").upper())
        client.street_name = request.POST.get("street_name")
        client.city = request.POST.get("city")
        client.house_name = request.POST.get("house_name")
        client.county = request.POST.get("county")
        client.country = request.POST.get("country")
        if client.city == "nan" or client.county == "nan" or client.country == "nan":
            messages.error(request, "Select all dropdown fields")
            return redirect(f"/client?page=edit_client&id={client_id}")
        if " " not in client.postcode:
            client.postcode = client.postcode[:-3] + " " + client.postcode[-3:]
        uk = Councils.objects.get(name="UK")
        if client.postcode[:-3] not in uk.postcodes.split(","):
            uk_postcodes = os.path.join(
                os.path.dirname(__file__), "./uk_postcodes.txt"
            )
            with open(uk_postcodes, "a") as f:
                f.write("," + client.postcode[:-3].strip())
            uk.postcodes += "," + client.postcode[:-3].strip()
            uk.save()
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
    return redirect('client_app:client', context)

@login_required
def remove_client(request, client_id):
    client = Clients.objects.get(pk=client_id)
    client.delete()

    messages.success(request, "Client deleted successfully!")
    return redirect("client_app:client")


def add_client_action(
    client,
    agent,
    action_type,
    date_time=None,
    text='',
    talked_with=None,
    closed=False,
    imported=False,
    keyevents=False,
    created_at=None
):
    """
    Helper function to add an action to a client.
    """
    if not created_at:
        created_at = datetime.now(london_tz)
    client.add_action(
        text=text,
        agent=agent,
        closed=closed,
        imported=imported,
        created_at=created_at,
        talked_with=talked_with,
        date_time=date_time,
        action_type=action_type,
        keyevents=keyevents,
    )

def get_future_datetime(minutes_ahead=60):
    """
    Helper function to get a future datetime object.
    """
    now = datetime.now(london_tz)
    future_time = now + timedelta(minutes=minutes_ahead)
    return future_time

def replace_placeholders(body, client):
    """
    Helper function to replace placeholders in the email body with client data.
    """
    placeholders = {
        "{{first_name}}": client.first_name or '',
        "{{last_name}}": client.last_name or '',
        "{{phone_number}}": client.phone_number or '',
        "{{email}}": client.email or '',
        "{{house_name}}": client.house_name or '',
        "{{street_name}}": client.street_name or '',
        "{{city}}": client.city or '',
        "{{county}}": client.county or '',
        "{{country}}": client.country or '',
        "{{postcode}}": client.postcode or '',
    }
    for placeholder, value in placeholders.items():
        body = body.replace(placeholder, value)
    return body

def client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        talked_with = request.POST.get("talked_client")
        if talked_with == "nan":
            messages.error(request, "Client field should be mapped")
            return redirect(f"/client-detail/{client_id}")

        date_str = request.POST.get("date_field")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")
        agent = User.objects.get(email=request.user)

        add_client_action(
            client=client,
            agent=agent,
            action_type="CB",
            date_time=date_time,
            text=text,
            talked_with=talked_with
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect(f"/client-detail/{client_id}")

def client_note_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        talked_with = request.POST.get("talked_client")
        if talked_with == "nan":
            messages.error(request, "Client field should be mapped")
            return redirect(f"/client-detail/{client_id}")

        date_str = request.POST.get("date_field")
        date_time_str = f"{date_str} 00:00"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        text = request.POST.get("text")
        agent = User.objects.get(email=request.user)

        add_client_action(
            client=client,
            agent=agent,
            action_type="Note",
            date_time=date_time,
            text=text,
            talked_with=talked_with
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect(f"/client-detail/{client_id}")

def close_client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        talked_with = request.POST.get("talked_client")
        if talked_with == "nan":
            messages.error(request, "Client field should be mapped")
            return redirect(f"/client-detail/{client_id}")

        reason = request.POST.get("reason")
        text = request.POST.get("text")
        c_text = f'{reason} - {text}' if reason != 'nan' else text or reason

        if client.closed:
            c_text = text

        agent = User.objects.get(email=request.user)
        date_time = datetime.now(london_tz)

        if client.closed:
            action_type = "Reopened"
            closed = False
            try:
                client.assigned_to = User.objects.get(pk=reason)
                client.save()
                add_client_action(
                    client=client,
                    agent=agent,
                    action_type="Assigned to Agent",
                    date_time=date_time
                )
            except Exception as e:
                messages.error(request, f"Error assigning client: {e}")
                return HttpResponseRedirect(f"/client-detail/{client_id}")
        else:
            action_type = "Closed"
            closed = True

        add_client_action(
            client=client,
            agent=agent,
            action_type=action_type,
            date_time=date_time,
            text=c_text,
            talked_with=talked_with,
            closed=closed,
            keyevents=True
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect(f"/client-detail/{client_id}")

def na_client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        date_time = get_future_datetime()
        agent = User.objects.get(email=request.user)
        add_client_action(
            client=client,
            agent=agent,
            action_type="NA",
            date_time=date_time
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect(f"/client-detail/{client_id}")

def lm_client_action_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        date_time = get_future_datetime()
        agent = User.objects.get(email=request.user)
        add_client_action(
            client=client,
            agent=agent,
            action_type="LM",
            date_time=date_time
        )
        messages.success(request, "Action added successfully!")
        return HttpResponseRedirect(f"/client-detail/{client_id}")

def send_client_email(request, cclient_id):
    if request.method == "POST":
        cclient = Clients.objects.get(pk=cclient_id)
        email_id = request.POST.get("template")
        date_str = request.POST.get("date_field")
        time_str = request.POST.get("time_field")
        date_time_str = f"{date_str} {time_str}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        domain_name = request.build_absolute_uri("/")[:-1]

        if request.POST.get("signature") == "nan":
            messages.error(request, "Signature field should be mapped")
            return redirect(f"/cclient-detail/{cclient_id}")

        signature = Signature.objects.get(pk=request.POST.get("signature"))

        if email_id != "nan":
            email_template = Email.objects.get(pk=email_id)
            body = replace_placeholders(email_template.body, cclient)
            subject = email_template.subject
            text = email_template.name
        else:
            body = request.POST.get("text")
            text = body
            subject = request.POST.get("subject")

        # Replace newline characters with <br> tags
        body = re.sub(r"\r?\n", "<br>", body)
        signature_content = re.sub(r"\r?\n", "<br>", signature.signature)
        context = {
            "body": body,
            "signature": signature_content,
            "domain_name": domain_name,
        }

        template_name = "../templates/home/email.html"
        html_content = render_to_string(template_name=template_name, context=context)
        plain_message = strip_tags(html_content)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email="support@reform-group.uk",
            recipient_list=[cclient.email],
            html_message=html_content,
        )

        agent = User.objects.get(email=request.user)
        created_at = datetime.now(london_tz)

        cclient.add_action(
            agent=agent,
            closed=False,
            imported=False,
            created_at=created_at,
            action_type="Email Sent",
            date_time=date_time,
            text=text or "Email Sent",
        )

        messages.success(request, "Email sent successfully!")
        return HttpResponseRedirect(f"/client-detail/{cclient_id}")


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
    return redirect(f"/client-detail/{client_id}")


def remove_campaign(request, campaign_id, client_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    campaign.delete()
    messages.success(request, "Campaign deleted successfully!")
    return redirect(f"/client-detail/{client_id}")



def add_route_client(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(pk=client_id)
        if request.POST.get("route") == "nan":
            messages.error(request, "Route should be selected")
            return redirect(f"/client-detail/{client_id}")
        route_council_id = request.POST.get("route").split('-')
        route = Route.objects.get(pk=route_council_id[0])
        council = Councils.objects.get(pk=route_council_id[1])
        Client_Council_Route.objects.create(
            client=client,
            route=route,
            council=council,
        )
        messages.success(request, "Funding Route added successfully to a Client!")
        return redirect(f"/client-detail/{client_id}")
    

def add_product_client(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(pk=client_id)
        if request.POST.get("product") == "nan":
            messages.error(request, "Product should be selected")
            return redirect(f"/client-detail/{client_id}")
        main_product = Product.objects.get(pk=request.POST.get("product"))
        client.product.add(main_product)
        client.save()
        messages.success(request, "Product added successfully to a Client!")
        return redirect(f"/client-detail/{client_id}")



def add_coverage_areas(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(pk=client_id)
        postcodes = request.POST.get("postcodes").split(",")
        region = Councils.objects.get(name='UK')
        
        for postcode in postcodes:
            if postcode not in region.postcodes.split(','):
                region.postcodes += ',' + postcode
                uk_postcodes = os.path.join(os.path.dirname(__file__), '../uk_postcodes.txt')
                with open(uk_postcodes, 'a') as f:
                    f.write(',' + postcode)
                region.save()    
            CoverageAreas.objects.create(
                client=client,
                postcode=postcode,
            )
            messages.success(request, "Coverage Area added successfully!")
                    
        return redirect(r"/client-detail/" + str(client_id))

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
    client = Clients.objects.get(pk=client_id)
    if ClientArchive.objects.filter(client=client).filter(product=product).exists():
        ClientArchive.objects.filter(client=client).filter(product=product).first().delete()
        messages.success(request, "Unarchive Successfully")
        return redirect(r"/client-detail/" + str(client_id))
    else:
        ClientArchive.objects.create(
            client=client,
            product=product
        )
        messages.success(request, "Archive Successfully")
        return redirect(r"/client-detail/" + str(client_id))

def archive_route(request,client_id, route_id, council_id):
    route = Route.objects.get(pk=route_id)
    client = Clients.objects.get(pk=client_id)
    council = Councils.objects.get(pk=council_id)
    archive = ClientArchive.objects.filter(
        client=client, councils=council, route=route
    ).first()
    if archive:
        archive.delete()
        messages.success(request, "Unarchived Successfully")
    else:
        ClientArchive.objects.create(client=client, route=route, councils=council)
        messages.success(request, "Archived Successfully")

    return redirect(f"/client-detail/{client_id}")

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

def add_priority(request, stage_id, client_id):
    stage = Stage.objects.get(pk=stage_id)
    if request.method == 'POST':
        order = request.POST.get('order')
        stage.order = order
        stage.save()
        messages.success(request, "Priority added successfully!")
        return redirect("/client-detail/"+ str(client_id))

def add_route_priority(request, route_id, client_id):
    route = Route.objects.get(pk=route_id)
    if request.method == 'POST':
        order = request.POST.get('order')
        route.order = order
        route.save()
        messages.success(request, "Priority added successfully!")
        return redirect("/client-detail/"+ str(client_id))


def customer_jr_order(request,client_id):
    client = Clients.objects.get(pk=client_id)
    if request.method == 'POST':
        body = request.body
        response = json.loads(body)
        cjstages = response['cjstages']
        for i in cjstages:
            print(i['route'],i['product'],i['stage'])
            cjstage = CJStage.objects.all().filter(route=Route.objects.get(name=i['route'])).filter(product=Product.objects.get(name=i['product'])).filter(stage=Stage.objects.get(name=i['stage'])).first()
            cjstage.order = i['order']
            cjstage.save()
    return HttpResponse(200)

def add_client_stage_rule(request, route_id, product_id, stage_id, question_id, client_id):
    question = Questions.objects.get(pk=question_id)
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)

    if request.method == "POST":
        dynamicRules = request.POST.getlist("dynamicRule")
        
        rule_regulation = Rule_Regulation.objects.filter(
            route=route, product=product, stage=stage, question=question, is_client=True
        ).first()
        
        if rule_regulation:
            rule_regulation.rules_regulation = dynamicRules
            rule_regulation.save()
        else:
            rule_regulation = Rule_Regulation.objects.create(
                route=route,
                product=product,
                stage=stage,
                question=question,
                rules_regulation=dynamicRules,
                is_client=True,
            )

    messages.success(request, "Rule added successfully!")
    return redirect("/client-detail/"+ str(client_id))