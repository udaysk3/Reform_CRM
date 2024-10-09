from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import (
    Stage,
    Document,
    Stage,
)
from product_app.models import Product
from client_app.models import Clients
import json


@login_required
def product(request):
    products = Product.objects.all().filter(global_archive=False)
    archived_products = Product.objects.all().filter(global_archive=True)
    return render(request, "home/products.html", {"products": products, "archived_products": archived_products})

def archive_global_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    if product.global_archive == False:
        product.global_archive = True
    else:
        product.global_archive = False
        
    product.save()
    if product.global_archive == True:
        messages.success(request, "Product archived successfully!")
    else:
        messages.success(request, "Product unarchived successfully!")
    return redirect("product_app:product")

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

def remove_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect(f"/product")




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
            doc = Document.objects.create(document=document, is_product=True)
            product.documents.add(doc)
        product.save()
        messages.success(request, "Product added successfully!")
        return redirect("product_app:product")
    return render(request, 'home/add_new_product.html')

def edit_new_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    docs = []
    for doc in product.documents.all():
        if doc.is_client == False and doc.is_route == False:
            docs.append(doc)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        product.name = name
        product.description = description
        documents = request.FILES.getlist('document')
        for document in documents:
            docu = Document.objects.create(document=document)
            product.documents.add(docu)

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("product_app:product")
    return render(request, 'home/edit_new_product.html', {'product':product, "docs":docs})


def delete_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("product_app:product")

