from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def HR(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    return render(request, "home/hr.html")

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
