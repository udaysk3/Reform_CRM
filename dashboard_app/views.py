from django.contrib.auth.decorators import login_required
from user.models import User
from django.core.serializers import serialize
from django.shortcuts import render
from home.models import (
    Campaign,
)
from customer_app.models import Customers
from datetime import datetime
from django.db.models import Max
import pytz
from user.models import User
from pytz import timezone
london_tz = pytz.timezone("Europe/London")
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

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
