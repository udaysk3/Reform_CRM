from django.contrib.auth.decorators import login_required
from user.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
import pytz, json, os
from pytz import timezone
from .models import (
    Cities,
    Campaign,
    Stage,
    Cities,
    HistoryId,
    Countys,
    Countries,
    Stage,
    Suggestion,
    Document,
    Sub_suggestions,
)
from django.db.models import Q
from django.http import HttpResponseRedirect
from customer_app.models import Customers
from client_app.models import Clients
from region_app.models import Councils
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
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

@login_required
def suggestion(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    if request.GET.get("page") == "In Review" or request.GET.get("page") == None:
        suggestions = Suggestion.objects.filter(Q(status="In Review")).order_by("order")
    else:
        suggestions = Suggestion.objects.all().filter(status=request.GET.get("page")).order_by("order")
    current_date_time = datetime.now(pytz.timezone("Europe/London")).date()
    yesterday = current_date_time + timedelta(days=1)
    agents = User.objects.all().filter(is_staff=True)

    return render(request, "home/suggestion.html", {"suggestions": suggestions, "agents": agents, "current_date_time": current_date_time, "yesterday": yesterday})

def assign_agents(request):
    if request.method == "POST":
     try:
        agent_id = request.POST.get("agent_id")
        suggestion_ids = request.POST.get("suggestions").split(",")
        agent = User.objects.get(pk=agent_id)
        for suggestion_id in suggestion_ids:
            suggestion = Suggestion.objects.get(pk=suggestion_id)
            suggestion.assigned_to =  agent
            suggestion.save()
            suggestion.add_suggestion_action(
                agent=User.objects.get(email=request.user),
                date_time=datetime.now(pytz.timezone("Europe/London")),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type="Assigned to Agent",
            )
        messages.success(request, "Suggestion Assigned successfully!")
        return redirect("app:suggestion")
     except Exception as e:
        messages.error(request, f"Error assigning suggestion: {e}")
        return redirect("app:suggestion")
    else:
        messages.error(request, "Cannot Assign suggestion!")
        return redirect("app:suggestion")


def assign_agent(request):
    suggestion_id = request.POST.get("suggestion_id")
    agent_id = request.POST.get("agent_id")
    agent = User.objects.get(pk=agent_id)
    try:
        suggestion = Suggestion.objects.get(pk=suggestion_id)
        suggestion.assigned_to =  User.objects.get(pk=agent_id)
        suggestion.save()
        suggestion.add_suggestion_action(
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            text=f"Assigned to Agent {agent.first_name} {agent.last_name}",
        )
        messages.success(request, "Agent Assigned successfully!")
        return HttpResponseRedirect("/detail_suggestion/" + str(suggestion_id))
    except Exception as e:
        messages.error(request, f"Error assigning suggestion: {e}")
        return HttpResponseRedirect("/detail_suggestion/" + str(suggestion_id))

@login_required
def detail_suggestion(request, suggestion_id):
    suggestion = Suggestion.objects.get(pk=suggestion_id)
    sub_suggestions = Sub_suggestions.objects.all().filter(suggestion=suggestion).order_by("created_at")
    completed_sub_suggestions = Sub_suggestions.objects.all().filter(suggestion=suggestion, status="Completed")
    length_sub_suggestions = len(sub_suggestions)
    length_completed_sub_suggestions = len(completed_sub_suggestions)
    if len(sub_suggestions) == 0:
        if suggestion.status == "Complete":
            length_completed_sub_suggestions = 1
            length_sub_suggestions = 1
        else:
            length_sub_suggestions = 1
            length_completed_sub_suggestions = 0

    merge_suggestions = Suggestion.objects.filter(Q(status="In Progress") | Q(status="Not Started"))
    if suggestion.expected_completion_date:
        formatted_date = suggestion.expected_completion_date.strftime("%Y-%m-%d")
    else:
        formatted_date = ""
    london_tz = timezone("Europe/London")
    keyevents = suggestion.get_created_at_action_history()
    events = {}
    for i in keyevents:
        if i.created_at.replace(tzinfo=london_tz).date() not in events:
            events[i.created_at.replace(tzinfo=london_tz).date()] = []
    for i in keyevents:
        events[i.created_at.replace(tzinfo=london_tz).date()].append(
                [
                    i.created_at.astimezone(london_tz).time(),
                    i.agent.first_name,
                    i.agent.last_name,
                    i.text
                ]
            )
    agents = User.objects.all().filter(is_staff=True)
    return render(request, "home/detail_suggestion.html", {"suggestion": suggestion, "sub_suggestions": sub_suggestions, "formatted_date": formatted_date, "events": events, "agents": agents, "merge_suggestions": merge_suggestions, "length_sub_suggestions": length_sub_suggestions, "length_completed_sub_suggestions": length_completed_sub_suggestions})

def add_sub_suggestion(request, suggestion_id):
    if request.method == "POST":
        suggestion = Suggestion.objects.get(pk=suggestion_id)
        descriptions = request.POST.getlist("suggestion")
        suggestion = Suggestion.objects.get(pk=suggestion_id)
        for description in descriptions:
            Sub_suggestions.objects.create(
                description=description,
                suggestion=suggestion,
                created_at=datetime.now(pytz.timezone("Europe/London")),
                status="In Review",
                assigned_to=suggestion.assigned_to,
            )
            suggestion.add_suggestion_action(
                agent=User.objects.get(email=request.user),
                created_at=datetime.now(pytz.timezone("Europe/London")),
                text=f"Added sub suggestion: {description}",
            )
        messages.success(request, "Sub suggestion added successfully!")
        return HttpResponseRedirect(f"/detail_suggestion/{suggestion_id}")
    
def delete_sub_suggestion(request, sub_suggestion_id):
    sub_suggestion = Sub_suggestions.objects.get(pk=sub_suggestion_id)
    suggestion = sub_suggestion.suggestion
    suggestion.add_suggestion_action(
        agent=User.objects.get(email=request.user),
        created_at=datetime.now(pytz.timezone("Europe/London")),
        text=f"Deleted sub suggestion: {sub_suggestion.description}",
    )
    sub_suggestion.delete()
    return HttpResponse(200)

def change_sub_suggestion_status(request, sub_suggestion_id):
    sub_suggestion = Sub_suggestions.objects.get(pk=sub_suggestion_id)
    suggestion = sub_suggestion.suggestion
    status = request.POST.get("status")
    sub_suggestion.status = status
    sub_suggestion.save()
    suggestion.add_suggestion_action(
        agent=User.objects.get(email=request.user),
        created_at=datetime.now(pytz.timezone("Europe/London")),
        text=f"Changed sub suggestion status to {status}",
    )
    return redirect(f"/detail_suggestion/{suggestion.id}")

def change_sub_suggestion_agent(request, sub_suggestion_id):
    sub_suggestion = Sub_suggestions.objects.get(pk=sub_suggestion_id)
    suggestion = sub_suggestion.suggestion
    agent_id = request.POST.get("agent")
    agent = User.objects.get(pk=agent_id)
    sub_suggestion.assigned_to = agent
    sub_suggestion.save()
    suggestion.add_suggestion_action(
        agent=User.objects.get(email=request.user),
        created_at=datetime.now(pytz.timezone("Europe/London")),
        text=f"Assigned sub suggestion to {agent.first_name} {agent.last_name}",
    )
    return redirect(f"/detail_suggestion/{suggestion.id}")

def suggestion_order(request):
    if request.method == 'POST':
        body = request.body
        response = json.loads(body)
        order_suggestions = response["order_suggestions"]
        for suggestion in order_suggestions:
            suggestion_obj = Suggestion.objects.get(pk=suggestion["suggestion"])
            suggestion_obj.order = suggestion["order"]
            suggestion_obj.save()
        return HttpResponse(200)

def add_suggestion(request):
    if request.method == "POST":
        description = request.POST.get("description")
        type = request.POST.get("type")
        agent = request.user
        location = request.POST.get("location")
        files = request.FILES.getlist("file")
        suggestion = Suggestion.objects.create(
            description=description,
            type=type,
            agent=agent,
            status="In Review",
            location=location,
            created_at=datetime.now(pytz.timezone("Europe/London")),

        )
        
        for file in files:
            doc = Document.objects.create(document=file)
            suggestion.files.add(doc)
        suggestions = Suggestion.objects.all().filter(status="In Review")
        length = len(suggestions)
        suggestion.order = length
        suggestion.save()

        suggestion.add_suggestion_action(
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            text=f"Added suggestion {description} of type {type} at location {location}",
        )
        
        
        messages.success(request, "Suggestion added successfully!")
        return HttpResponseRedirect(location)
    
def merge_suggestions(request, suggestion_id):
    if request.method == "POST":
        suggestion = Suggestion.objects.get(pk=suggestion_id)
        merge_suggestion_id = request.POST.get("merge_suggestion")
        merge_suggestion = Suggestion.objects.get(pk=merge_suggestion_id)

        for requester in suggestion.aditional_requesters.all():
            merge_suggestion.aditional_requesters.add(requester)
        merge_suggestion.aditional_requesters.add(suggestion.agent)    
        sub_suggestion_data = ''
        for sub_suggestion in suggestion.sub_suggestions.all():
            if sub_suggestion.assigned_to:
                sub_suggestion_data += f"Description - {sub_suggestion.description} Status - {sub_suggestion.status} Assigned To - {sub_suggestion.assigned_to.first_name} {sub_suggestion.assigned_to.last_name} \n"
            else:
                sub_suggestion_data += f"Description - {sub_suggestion.description} Status - {sub_suggestion.status} Assigned To - None \n"
            sub_suggestion.delete()

        aditional_requesters = ''
        for requester in suggestion.aditional_requesters.all():
            aditional_requesters += f"{requester.first_name} {requester.last_name}, "

        files = ''
        for file in suggestion.files.all():
            files += f"{file.document}, "
            file.delete()

        assigned_to = 'None'
        if suggestion.assigned_to:
            assigned_to = f"{suggestion.assigned_to.first_name} {suggestion.assigned_to.last_name}"

        merge_suggestion.add_suggestion_action(
            agent=User.objects.get(email=request.user),
            created_at= datetime.now(pytz.timezone("Europe/London")),
            text=f"A suggestion was merged into this \n Suggestion - {suggestion.description} \n Type - {suggestion.type} \n Date - {suggestion.created_at} \n Location - {suggestion.location} \n Status - {suggestion.status} \n Expected Completion Date - {suggestion.expected_completion_date} \n Assigned to - {assigned_to} \n Additional Requesters - {aditional_requesters} \n Files - {files} \n Sub Suggestions - {sub_suggestion_data} \n",
        )

        suggestion.delete()
        merge_suggestion.save()
        messages.success(request, "Suggestion merged successfully!")
        return HttpResponseRedirect(f"/suggestion?page=In Review")

    
def add_comment(request, suggestion_id):
    if request.method == "POST":
        suggestion = Suggestion.objects.get(pk=suggestion_id)
        comment = request.POST.get("comment")
        suggestion.add_suggestion_action(
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            text=f"{comment}",
        )
        messages.success(request, "Comment added successfully!")
        return HttpResponseRedirect(f"/detail_suggestion/{suggestion_id}")

def edit_suggestion(request, suggestion_id):
    if request.method == "POST":
        description = request.POST.get("description")
        type = request.POST.get("type")
        location = request.POST.get("location")
        files = request.FILES.getlist("files")
        expected_completion_date = request.POST.get("expected_completion_date")
        status = request.POST.get("status")
        suggestion = Suggestion.objects.get(pk=suggestion_id)
        if suggestion.status != status:
            suggestions = Suggestion.objects.all().filter(status=status)
            length = len(suggestions)
            suggestion.order = length + 1
            if request.POST.get("status") == "Complete":
                Sub_suggestions.objects.filter(suggestion=suggestion).update(status="Completed")
            elif request.POST.get("status") == "Test":
                Sub_suggestions.objects.filter(suggestion=suggestion).update(status="Test")

        text = "Changed "
        if suggestion.description != description:
            text += f"description to {description}"
        if suggestion.type != type:
            text += f"type to {type}"
        if suggestion.location != location:
            text += f"location to {location}"
        if suggestion.expected_completion_date != expected_completion_date:
            text += f"expected completion date to {expected_completion_date}"
        if suggestion.status != status:
            text += f"status to {status}"
        suggestion.add_suggestion_action(
            agent=User.objects.get(email=request.user),
            created_at=datetime.now(pytz.timezone("Europe/London")),
            text=text,
        )
        suggestion.description = description
        suggestion.type = type
        suggestion.location = location
        if files:
            for file in files:
                doc = Document.objects.create(document=file)
                suggestion.files.add(doc)

        if expected_completion_date:
            suggestion.expected_completion_date = expected_completion_date
        else:
            suggestion.expected_completion_date = None
        suggestion.status = status
        suggestion.save()
        messages.success(request, "Suggestion edited successfully!")
        return redirect(f"/detail_suggestion/{suggestion_id}")

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
