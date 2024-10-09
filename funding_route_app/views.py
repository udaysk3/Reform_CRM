from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import (
    Stage,
    Document,
    Stage,
)
from product_app.models import Product
from region_app.models import Councils
from funding_route_app.models import Route
import pytz
import json
london_tz = pytz.timezone("Europe/London")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

@login_required
def funding_route(request):
    products = Product.objects.all().filter(global_archive=False)
    if request.GET.get("page") == "edit":
        route_id = request.GET.get("route_id")
        route = Route.objects.get(pk=route_id)
        documents = []
        for doc in route.documents.all():
            if doc.is_client == False and doc.is_council == False:
                documents.append(doc)
        
        return render(request, "home/funding_routes.html", {"route": route,"products": products, "documents":documents})
    funding_routes = Route.objects.all().filter(global_archive=False)
    archived_funding_routes = Route.objects.all().filter(global_archive=True)
    return render(request, "home/funding_routes.html", {"funding_routes": funding_routes, "products": products, "archived_funding_routes": archived_funding_routes})

def archive_global_funding_route(request, funding_route_id):
    funding_route = Route.objects.get(pk=funding_route_id)
    if funding_route.global_archive == False:
        funding_route.global_archive = True
    else:
        funding_route.global_archive = False
    
    funding_route.save()
    if funding_route.global_archive == True:
        messages.success(request, "Funding Route archived successfully!")
    else:
        messages.success(request, "Funding Route unarchived successfully!")
    return redirect("funding_route_app:funding_route")

@login_required
def add_new_funding_route(request):
    products = Product.objects.all().filter(global_archive=False)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        documents = request.FILES.getlist("document")

        route = Route.objects.create(name=name, description=description)
        for document in documents:
            doc = Document.objects.create(document=document,is_route=True)
            route.documents.add(doc)
        for product in products:
            if request.POST.get(product.name) == "true":
                route.product.add(product)
            else:
                route.product.remove(product)
        route.save()
        messages.success(request, "Funding Route created successfully!")
        return redirect("funding_route_app:funding_route")
    return render(request, "home/add_new_funding_routes.html",{'products':products})

@login_required
def edit_new_funding_route(request,route_id):
    route = Route.objects.get(pk=route_id)
    if request.method == "POST":
        route.name = request.POST.get("name")
        route.description = request.POST.get("description")
        documents = request.FILES.getlist("document")
        for document in documents:
            doc = Document.objects.create(document=document,is_route=True)
            route.documents.add(doc)
        route.save()
        messages.success(request, "Funding Route created successfully!")
        return redirect("funding_route_app:funding_route")
    return render(request, "home/edit_new_funding_routes.html",{"route":route})


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
            if stage.fields is not None:
                fields[stage.name] = json.loads(stage.fields)
            else:
                # Handle the None case if needed
                fields[stage.name] = {}
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
def add_funding_route(request, council_id):
    council = Councils.objects.get(pk=council_id)
    if request.method == "POST":
        if request.POST.get("route") == "nan":
            messages.error(request, "Route should be selected")
            return redirect(f"/council-detail/{council_id}")
        route = Route.objects.get(pk=request.POST.get("route"))
        route.council.add(council)
        route.save()
        messages.success(request, "Funding Route added successfully!")
        return redirect('/council-detail/'+str(council_id))

def add_council_funding_route(request, council_id):
    if request.method == "POST":
        council = Councils.objects.get(pk=council_id)
        route = Route.objects.get(pk=request.POST.get("route"))
        route.council.add(council)
        route.save()
        messages.success(request, "Funding Route added successfully to a Council!")
        return redirect(f"/council-detail/{council_id}")

def remove_funding_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    route.delete()
    messages.success(request, "Route deleted successfully!")
    return redirect("funding_route_app:funding_route")


@login_required
def edit_local_funding_route(request, funding_route_id):
    funding_route = Route.objects.get(pk=funding_route_id)
    clients = funding_route.client.all()
    if clients.exists():
        client_id = clients.first().id
    # stages = Stage.objects.all().filter(client=Clients.objects.get(pk=client_id))
    # fields = {}
    # saved_rules_regulations = {}
    # if funding_route.rules_regulations:
    #     saved_rules_regulations = json.loads(funding_route.rules_regulations)
    # if stages.exists():
    #     for stage in stages:
    #         fields[stage.name] = json.loads(stage.fields)
    # if funding_route.sub_rules_regulations:
    #     sub_rules_regulations = json.loads(funding_route.sub_rules_regulations)
    # else:
    #     sub_rules_regulations = None
    # if stages.exists():
    #     for stage in stages:
    #         fields[stage.name] = json.loads(stage.fields)
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
            # "fields": fields,
            # "saved_rules_regulations": saved_rules_regulations,
            # "sub_rules_regulations": sub_rules_regulations,
        },
    )


def delete_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    route.delete()
    messages.success(request, "Route deleted successfully!")
    return redirect("funding_route_app:funding_route")

def edit_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    products = Product.objects.all()
    if request.method == "POST":
        route.name = request.POST.get("name")
        route.description = request.POST.get("description")
        documents = request.FILES.getlist("document")
        for document in documents:
            doc = Document.objects.create(document=document,is_route=True)
            route.documents.add(doc)
        for product in products:
            if request.POST.get(product.name) == 'true':
                route.product.add(product)
            else:
                route.product.remove(product)
        route.save()
        messages.success(request, "Route updated successfully!")
        return redirect("funding_route_app:funding_route")
    return redirect("funding_route_app:funding_route")

