from django.contrib.auth.decorators import login_required
from user.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import (
    Campaign,
)
from admin_app.models import Signature, Reason, Email
from client_app.models import Clients
from django.http import  JsonResponse

@login_required
def Admin(request):
    if request.GET.get("page") == "edit":
        user_id = request.GET.get("id")
        user = User.objects.get(pk=user_id)
        return render(request, "home/admin.html", {"user": user})
    if request.GET.get("page") == "edit_client":
        client_id = request.GET.get("id")
        client = Clients.objects.get(pk=client_id)
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
        return redirect("admin_app:admin")
    return render(request, "home/admin.html")

def edit_template(request, template_id):
    template = Email.objects.get(pk=template_id)
    if request.method == "POST":
        template.name = request.POST.get("name")
        template.subject = request.POST.get("subject")
        template.body = request.POST.get("body")
        template.save()
        messages.success(request, "Template updated successfully!")
        return redirect("admin_app:admin")
    return redirect("admin_app:admin")

def remove_template(request, template_id):
    template = Email.objects.get(pk=template_id)
    template.delete()
    messages.success(request, "Template deleted successfully!")
    return redirect("admin_app:admin")

def add_reason(request):
    if request.method == "POST":
        name = request.POST.get("name")
        reason = request.POST.get("reason")
        template = Reason.objects.create(
            name=name,
            reason=reason,
        )
        messages.success(request, "Reason added successfully!")
        return redirect("admin_app:admin")
    return render(request, "home/admin.html")

def edit_reason(request, reason_id):
    reason = Reason.objects.get(pk=reason_id)
    if request.method == "POST":
        reason.name = request.POST.get("name")
        reason.reason = request.POST.get("reason")
        reason.save()
        messages.success(request, "Reason updated successfully!")
        return redirect("admin_app:admin")
    return redirect("admin_app:admin")

def remove_reason(request, reason_id):
    reason = Reason.objects.get(pk=reason_id)
    reason.delete()
    messages.success(request, "Reason deleted successfully!")
    return redirect("admin_app:admin")


def add_signature(request):
    if request.method == "POST":
        signature = request.POST.get("signature")
        signature_img = request.FILES.get("signature_img")
        template = Signature.objects.create(
            signature=signature,
            signature_img=signature_img,
        )
        messages.success(request, "Signature added successfully!")
        return redirect("admin_app:admin")
    return render(request, "home/admin.html")


def edit_signature(request, signature_id):
    signature = Signature.objects.get(pk=signature_id)
    if request.method == "POST":
        signature.signature = request.POST.get("signature")
        signature.signature_img = request.FILES.get("signature_img")
        signature.save()
        messages.success(request, "Signature updated successfully!")
        return redirect("admin_app:admin")
    return redirect("admin_app:admin")

def remove_signature(request, signature_id):
    signature = Signature.objects.get(pk=signature_id)
    signature.delete()
    messages.success(request, "Signature deleted successfully!")
    return redirect("admin_app:admin")

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
