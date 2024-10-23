from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import User


@login_required
def employee(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.all().filter(is_employee=True).filter(is_archive=False)
    return render(request, "home/employee.html", {'emps':employes})

@login_required
def off_boarding(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.all().filter(is_employee=True).filter(is_archive=True)
    return render(request, "home/off_boarding.html", {'emps':employes})

def add_employee(request):
    return render(request, 'home/add_employee.html')

def edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    if emp.dob:
        emp_dob_formatted = emp.dob.strftime('%Y-%m-%d')
    else:
        emp_dob_formatted = ''

    return render(request, 'home/edit_employee.html', {'emp':emp, 'emp_dob':emp_dob_formatted})


def bulk_archive_employes(request):
    if request.method == "GET":
        emp_ids_str = request.GET.get("ids", "")
        try:
            emp_ids = [
                int(id) for id in emp_ids_str.split(",") if id.isdigit()
            ]
            if emp_ids:
                emps = User.objects.filter(id__in=emp_ids)
                for emp in emps:
                    print(emp)
                    if emp.is_archive == True:
                        emp.is_archive = False
                    else:
                        emp.is_archive = True
                    emp.save()

                messages.success(request, "Selected employes archived successfully.")
            else:
                messages.warning(
                    request, "No valid employes IDs provided for deletion."
                )
        except Exception as e:
            messages.error(request, f"Error deleting employes: {e}")
        return redirect("hr_app:employee")

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
