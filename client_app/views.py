import json
import os
import os.path
import re
from datetime import datetime, timedelta

import pytz
from pytz import timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.cache import cache_page
from django.views.generic import ListView

from admin_app.models import Email, Reason, Signature
from client_app.models import ClientArchive, Clients, CoverageAreas
from customer_app.epc import getEPC
from customer_app.task import getLA
from customer_journey_app.models import CJStage
from funding_route_app.models import Route
from home.models import Campaign, Client_Council_Route, Stage
from product_app.models import Product
from question_actions_requirements_app.models import Questions, Rule_Regulation
from region_app.models import Councils, RegionArchive
from user.models import User

london_tz = pytz.timezone("Europe/London")

@login_required
@cache_page(60 * 20)
def client_detail(request, client_id, selected_client_id=None):
    domain_name = request.build_absolute_uri("/")[:-1]
    london_tz = timezone('Europe/London')

    client = get_object_or_404(Clients, pk=client_id)

    signatures = Signature.objects.all()
    coverage_areas = CoverageAreas.objects.filter(client=client)
    regions = Councils.objects.all()

    coverage_postcodes = set(ca.postcode for ca in coverage_areas)
    display_regions = {}
    for region in regions:
        region_postcodes = set(region.postcodes.split(','))
        covered_postcodes = coverage_postcodes & region_postcodes
        if covered_postcodes == region_postcodes:
            display_regions[region] = 'All'
        elif covered_postcodes:
            display_regions[region] = 'Partial'
        else:
            display_regions[region] = 'None'

    clients = (Clients.objects
               .annotate(earliest_action_date=Max('action__date_time'))
               .filter(parent_client=None, closed=False)
               .order_by('earliest_action_date'))

    clients_list = list(clients)
    new_clients = [c for c in clients_list if any(not action.imported for action in c.get_created_at_action_history())]
    old_clients = [c for c in clients_list if c not in new_clients]
    clients_ordered = (new_clients + old_clients)[::-1]

    client_ids = [c.id for c in clients_ordered]
    try:
        index = client_ids.index(client.id)
    except ValueError:
        index = 0

    prev_client = clients_ordered[index - 1] if index > 0 else clients_ordered[0]
    next_client = clients_ordered[index + 1] if index < len(clients_ordered) - 1 else clients_ordered[-1]

    prev_client_id = str(prev_client.id)
    next_client_id = str(next_client.id)

    campaigns = Campaign.objects.filter(client=client, archive=False)
    uncampaigns = Campaign.objects.filter(client=client, archive=True)
    all_products = Product.objects.filter(global_archive=False)
    products = Product.objects.filter(client=client, global_archive=False)
    unproducts = products.filter(client_archive__client=client).distinct()
    products = products.exclude(id__in=unproducts.values_list('id', flat=True))

    councils = Councils.objects.all()
    coverage_area_postcodes = set(ca.postcode for ca in coverage_areas)
    council_coverage_area = [
        council for council in councils
        if coverage_area_postcodes & set(council.postcodes.split(','))
    ]

    all_routes = {}
    for council in council_coverage_area:
        routes = council.routes.filter(global_archive=False)
        if routes.exists():
            all_routes[council] = list(routes)

    client_council_routes = Client_Council_Route.objects.filter(client=client)
    routes = {}
    unroutes = {}
    for route_obj in client_council_routes:
        council = route_obj.council
        route = route_obj.route
        is_archived = ClientArchive.objects.filter(client=client, route=route, councils=council).exists()
        is_region_archived = RegionArchive.objects.filter(council=council, route=route).exists()
        if is_archived or is_region_archived or route.global_archive:
            unroutes.setdefault(council, []).append(route)
        else:
            routes.setdefault(council, []).append(route)

    stages = []
    for council, council_routes in routes.items():
        for route in council_routes:
            for product in products:
                cjstages = CJStage.objects.filter(route=route, product=product)
                for cjstage in cjstages:
                    questions = Rule_Regulation.objects.filter(
                        route=route, product=product, stage=cjstage.stage, is_client=False
                    ).values_list('question', flat=True).distinct()

                    questions_with_rules = []
                    for question in questions:
                        rule_regulation = Rule_Regulation.objects.filter(
                            route=route, product=product, stage=cjstage.stage,
                            question=question, is_client=True
                        ).first()
                        questions_with_rules.append(
                            (question, rule_regulation, route, product, cjstage.stage)
                        )

                    stages.append({
                        'route': route,
                        'product': product,
                        'stage': cjstage.stage,
                        'order': cjstage.order,
                        'questions': questions_with_rules
                    })

    stages.sort(key=lambda x: x['order'] if x['order'] is not None else float('inf'))

    display_stages = {}
    for stage_info in stages:
        key = f"{stage_info['route'].name} - {stage_info['product'].name}"
        display_stages.setdefault(key, []).append([stage_info['stage'], stage_info['questions']])

    child_clients = Clients.objects.filter(parent_client=client)
    agents = User.objects.filter(is_superuser=False)
    show_client = get_object_or_404(Clients, pk=selected_client_id) if selected_client_id else client
    reasons = Reason.objects.all()
    templates = Email.objects.all()

    actions = client.get_created_at_action_history()
    key_events = actions.filter(keyevents=True)
    history = {}
    imported = {}
    events = {}

    for action in actions:
        action_date = action.created_at.astimezone(london_tz).date()
        action_time = action.created_at.astimezone(london_tz).time()
        action_data = [
            action_time,
            action.text,
            action.agent.first_name,
            action.agent.last_name,
            action.imported,
            action.talked_with,
            action.client.postcode,
            action.client.house_name,
        ]

        if action.imported:
            imported.setdefault(action_date, []).append(action_data)
        else:
            history.setdefault(action_date, []).append(action_data)

    for event in key_events:
        event_date = event.created_at.astimezone(london_tz).date()
        event_time = event.created_at.astimezone(london_tz).time()
        event_data = [
            event_time,
            event.client.postcode,
            event.client.house_name,
            event.agent.first_name,
            event.agent.last_name,
            event.action_type,
            event.date_time,
            event.talked_with,
            event.text,
        ]
        events.setdefault(event_date, []).append(event_data)

    context = {
        'councils': councils,
        'client': client,
        'history': history,
        'imported': imported,
        'prev': prev_client_id,
        'next': next_client_id,
        'child_clients': child_clients,
        'agents': agents,
        'show_client': show_client,
        'events': events,
        'reasons': reasons,
        'templates': templates,
        'signatures': signatures,
        'domain_name': domain_name,
        'campaigns': campaigns,
        'uncampaigns': uncampaigns,
        'products': products,
        'unproducts': unproducts,
        'coverage_areas': coverage_areas,
        'all_products': all_products,
        'all_routes': all_routes,
        'routes': routes,
        'unroutes': unroutes,
        'stages': stages,
        'display_regions': display_regions,
        'display_stages': display_stages,
    }

    return render(request, 'home/client-detail.html', context)


class ClientListView(ListView):
    model = Clients
    template_name = 'home/client.html'
    context_object_name = 'clients'
    paginate_by = 50

    def get_queryset(self):
        return (
            Clients.objects
            .filter(parent_client=None, closed=False)
            .annotate(
                earliest_action_date=Max('action__date_time'),
                has_nonimported_action=Exists(
                    Action.objects.filter(client=OuterRef('pk'), imported=False)
                )
            )
            .order_by('-has_nonimported_action', '-earliest_action_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().date()
        context['campaigns'] = Campaign.objects.all()
        context['agents'] = serialize('json', User.objects.filter(is_superuser=False))
        return context


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

def client_note_submit(request, client_id):
    if request.method == "POST":
        client = Clients.objects.get(id=client_id)
        talked_with = request.POST.get("talked_client")
        date_str = request.POST.get("date_field")
        date_time_str = f"{date_str} 00:00"
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
            action_type="Note",
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

def send_client_email(request, cclient_id):
    cclient = Clients.objects.get(pk=cclient_id)
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

    body = re.sub(r"\r?\n", "<br>", body)
    signature_content = re.sub(r"\r?\n", "<br>", signature.signature)
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