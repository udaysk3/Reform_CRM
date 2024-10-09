from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import (
    Campaign,
)
from customer_app.models import Customers
from .models import Councils, RegionArchive
from funding_route_app.models import Route
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
import pytz
from user.models import User
import os
london_tz = pytz.timezone("Europe/London")
from datetime import datetime
import os.path

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

@login_required
def council_detail(request, council_id):
    all_councils = Councils.objects.all()
    council = Councils.objects.get(pk=council_id)
    routes = []
    unroutes = []

    for route in Route.objects.all().filter(council=council):


        if (
            RegionArchive.objects.filter(council=council, route=route).exists()
        ) or route.global_archive == True:
            unroutes.append(route)
        else:
            if route.global_archive == False:
                routes.append(route)
    all_routes = Route.objects.all().filter(global_archive=False)
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
            "unroutes":unroutes,
            "all_routes" : all_routes,
        },
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

def delete_council(request, council_id):
    council = Councils.objects.get(pk=council_id)
    council.delete()
    return redirect("/council")




@login_required
def remove_council(request, council_id):
    council = Councils.objects.get(pk=council_id)
    council.delete()

    messages.success(request, "council deleted successfully!")
    return redirect("region_app:council")


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
        postcodes = request.POST.get("postcodes")
        main_postcodes = ''
        for postcode in request.POST.get("postcodes").split(","):
            postcode = postcode.strip()  # Trim any leading/trailing whitespace
            if len(postcode) < 2 or len(postcode) > 4:  # Adjust this range as needed
                messages.error(request, f"Postcode {postcode} is not valid")
            else:
                uk_council = Councils.objects.get(name='UK')
                if postcode not in uk_council.postcodes:
                    uk_council.postcodes += ',' + postcode
                    uk_council.save()
                    uk_postcodes = os.path.join(os.path.dirname(__file__), '../uk_postcodes.txt')
                    with open(uk_postcodes, 'a') as f:
                        f.write(',' + postcode)
                if main_postcodes == '':
                    main_postcodes += postcode
                else:
                    main_postcodes += ',' + postcode
                print(uk_council.postcodes)

        council = Councils.objects.create(
            name=name,
            postcodes=main_postcodes,
            created_at=datetime.now(pytz.timezone('Europe/London')),
        )

        messages.success(request, "Region added successfully!")
        return redirect("region_app:council")
    return render(request, "home/council.html")


def edit_council(request, council_id):
    council = Councils.objects.get(pk=council_id)
    if request.method == "POST":
        main_postcodes = ""
        for postcode in request.POST.get("postcodes").split(","):
            postcode = postcode.strip()  # Trim any leading/trailing whitespace
            if len(postcode) < 2 or len(postcode) > 4:  # Adjust this range as needed
                messages.error(request, f"Postcode {postcode} is not valid")
            else:
                uk_council = Councils.objects.get(name="UK")
                if postcode not in uk_council.postcodes:
                    uk_council.postcodes += "," + postcode
                    uk_council.save()
                    uk_postcodes = os.path.join(os.path.dirname(__file__), '../uk_postcodes.txt')
                    with open(uk_postcodes, 'a') as f:
                        f.write(',' + postcode)
                if main_postcodes == "":
                    main_postcodes += postcode
                else:
                    main_postcodes += "," + postcode
        council.name = request.POST.get('name')
        council.postcodes = main_postcodes
        council.save()
        messages.success(request, "Region updated successfully!")
        return redirect(f"/council-detail/{council_id}")
    return render(request, "home/edit_council.html", {"council": council})


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

def region_archive(request, council_id, route_id):
    council = Councils.objects.get(pk=council_id)
    route = Route.objects.get(pk=route_id)
    if RegionArchive.objects.all().filter(council=council).filter(route=route).exists():
        RegionArchive.objects.all().filter(council=council).filter(route=route).first().delete()
    else:
        RegionArchive.objects.create(council=council,route=route)
    messages.success(request, "Archive successfully!")
    return redirect("/council-detail/"+ str(council_id))
