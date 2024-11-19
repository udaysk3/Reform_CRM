from django.contrib.auth.decorators import login_required
from user.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
import pytz
from .models import (
    Cities,
    Campaign,
    Stage,
    Cities,
    HistoryId,
    Countys,
    Countries,
    Stage,
)
from customer_app.models import Customers
from client_app.models import Clients
from region_app.models import Councils
from datetime import datetime
from django.http import HttpResponse, JsonResponse
import json
import os
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import base64 
import os.path
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def home(request):
    return render(request, "home/index.html")

@login_required
def Finance(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    return render(request, "home/finance.html")

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
                        agent=User.objects.get(email='systems@reform-group.uk'),
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
                        agent=User.objects.get(email='systems@reform-group.uk'),
                        keyevents=True,
                    )
                    customer.add_action(
                        date_time=datetime.now(pytz.timezone("Europe/London")),
                        created_at=datetime.now(pytz.timezone("Europe/London")),
                        action_type="Email Received",
                        agent=User.objects.get(email='systems@reform-group.uk'),
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

def get_campaign(request, client_id):
    client = Clients.objects.get(pk=client_id)
    campaigns = Campaign.objects.all().filter(client=client)
    return JsonResponse([{"campaign_id": campaign.id,"campaign_name":campaign.name} for campaign in campaigns], safe=False)

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

def get_postcodes(request, region):
    council = Councils.objects.get(name=region)
    if council.postcodes:
        postcodes = council.postcodes.split(",")
        return JsonResponse({"postcodes": postcodes}, safe=False)
    return JsonResponse({"postcodes": []}, safe=False)
