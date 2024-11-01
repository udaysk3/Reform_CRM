from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers import serialize
from datetime import datetime
import pytz
from pytz import timezone
from user.models import User
from .models import Role
from django.contrib.auth.hashers import make_password
from client_app.models import Clients

@login_required
def s_employee(request):
    if request.session.get("first_name"):
        delete_customer_session(request)
    employes = User.objects.filter(is_employee=True, is_archive=False)
    return render(request, "home/s_employee.html", {'emps': employes})

@login_required
def s_client(request):
    clients = Clients.objects.all()
    clients_list = Clients.objects.all()
    agents = User.objects.all().filter(is_employee=True)
    return render(request, 'home/s_client.html', {'clients': clients, "agents": serialize('json', agents), "clients_list": serialize('json', clients_list)})

def assign_agents(request):
    if request.method == "POST":
     try:
        agent_ids = [int(id_str.split(' - ')[-1]) for id_str in request.POST.get("agents").split(',')]
        clients = request.POST.get("clients")
        clients = list(clients.split(','))
        if "All Unassigned Clients" in clients or " All Unassigned Clients" in clients:
            if "All Unassigned Clients" in clients:
                clients.remove("All Unassigned Clients")
            else:
                clients.remove(" All Unassigned Clients")
            client_ids = Clients.objects.filter(assigned_to=None).values_list('id', flat=True)
            
            num_clients = len(client_ids)
            num_agents = len(agent_ids)
            clients_per_agent = num_clients // num_agents
            extra_clients = num_clients % num_agents
            
            agent_index = 0
            for agent_id in agent_ids:
                agent = User.objects.get(pk=agent_id)
                
                if extra_clients > 0:
                    num_clients_for_agent = clients_per_agent + 1
                    extra_clients -= 1
                else:
                    num_clients_for_agent = clients_per_agent
                
                assigned_clients = client_ids[:num_clients_for_agent]
                Clients.objects.filter(id__in=assigned_clients).update(assigned_to=agent_id)
                client_ids = client_ids[num_clients_for_agent:]
                
                agent_index += 1
        if clients:
            c_agent_ids = []
            for agent_id in clients:
                c_agent_ids.append(int(agent_id.split(' - ')[-1]))
            client_ids = []
            for agent_id in c_agent_ids:
                client_ids.extend(list(Clients.objects.filter(assigned_to=agent_id).values_list('id', flat=True)))
            num_clients = len(client_ids)
            num_agents = len(agent_ids)
            clients_per_agent = num_clients // num_agents
            extra_clients = num_clients % num_agents

            agent_index = 0
            for agent_id in agent_ids:
                agent = User.objects.get(pk=agent_id)

                if extra_clients > 0:
                    num_clients_for_agent = clients_per_agent + 1
                    extra_clients -= 1
                else:
                    num_clients_for_agent = clients_per_agent

                assigned_clients = client_ids[:num_clients_for_agent]
                Clients.objects.filter(id__in=assigned_clients).update(assigned_to=agent_id)
                client_ids = client_ids[num_clients_for_agent:]

                agent_index += 1
        
        messages.success(request, "Clients Assigned successfully!")
        return redirect("security_app:s_client")
     except Exception as e:
        messages.error(request, f"Error assigning clients: {e}")
        return redirect("security_app:s_client")
    else:
        messages.error(request, "Cannot Assign clients!")
        return redirect("security_app:s_client")


@login_required
def role(request):
    roles = Role.objects.all()
    return render(request, 'home/role.html', {'roles': roles})

def add_role(request):
    if request.method == 'POST':
        name = request.POST.get('role')
        dashboard = request.POST.get('dashboard') == 'on'
        mcustomer = request.POST.get('mcustomer') == 'on'
        customer = request.POST.get('customer') == 'on'
        client = request.POST.get('client') == 'on'
        council = request.POST.get('council') == 'on'
        admin = request.POST.get('admin') == 'on'
        archive = request.POST.get('archive') == 'on'
        product = request.POST.get('product') == 'on'
        globals = request.POST.get('global') == 'on'
        finance = request.POST.get('finance') == 'on'
        hr = request.POST.get('hr') == 'on'
        security = request.POST.get('security') == 'on'
        funding_route = request.POST.get('funding_route') == 'on'
        CJ = request.POST.get('CJ') == 'on'
        QA = request.POST.get('QA') == 'on'
        h_dashboard = request.POST.get('h_dashboard') == 'on'
        h_employee = request.POST.get('h_employee') == 'on'
        h_application = request.POST.get('h_application') == 'on'
        h_onboarding = request.POST.get('h_onboarding') == 'on'
        h_timesheet = request.POST.get('h_timesheet') == 'on'
        h_emp_action = request.POST.get('h_emp_action') == 'on'
        h_emp_notify = request.POST.get('h_emp_notify') == 'on'
        h_offboarding = request.POST.get('h_offboarding') == 'on'
        h_org_chart = request.POST.get('h_org_chart') == 'on'
        knowledge_base = request.POST.get('knowledge_base') == 'on'
        s_employee = request.POST.get('s_employee') == 'on'
        s_role = request.POST.get('s_role') == 'on'
        s_client = request.POST.get('s_client') == 'on'

        Role.objects.create(
            name=name,
            dashboard=dashboard,
            mcustomer=mcustomer,
            client=client,
            council=council,
            archive=archive,
            admin=admin,
            product=product,
            globals=globals,
            finance=finance,
            hr=hr,
            security=security,
            funding_route=funding_route,
            CJ=CJ,
            QA=QA,
            customer=customer,
            h_dashboard=h_dashboard,
            h_employee=h_employee,
            h_application=h_application,
            h_onboarding=h_onboarding,
            h_timesheet=h_timesheet,
            h_emp_action=h_emp_action,
            h_emp_notify=h_emp_notify,
            h_offboarding=h_offboarding,
            h_org_chart=h_org_chart,
            knowledge_base=knowledge_base,
            s_employee=s_employee,
            s_role=s_role,
            s_client=s_client
        )
        messages.success(request, "Role added successfully!")
        return redirect('security_app:role')
    return render(request, 'home/add_role.html')

@login_required
def s_edit_employee(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    history = {}
    actions = emp.employee_user.get_created_at_emp_action_history()
    london_tz = timezone("Europe/London")

    for i in actions:
        if i.created_at.replace(tzinfo=london_tz).date() not in history:
            history[i.created_at.replace(tzinfo=london_tz).date()] = []

    for i in actions:
        history[i.created_at.replace(tzinfo=london_tz).date()].append(
            [
                i.created_at.astimezone(london_tz).time(),
                i.agent.first_name,
                i.agent.last_name,
                i.action_type,
                i.text,
            ]
        )
        
    if request.method == 'POST':
        if request.POST.get('password'):
            emp.password = make_password(request.POST.get('password'))
        emp.status = request.POST.get('status') == 'on'
        emp.save()
        action_type = ''
        if request.POST.get('status') == 'on':
            action_type = 'Employee activated'
        else:
            action_type = 'Employee deactivated'
        emp.employee_user.add_emp_action(
            created_at=datetime.now(pytz.timezone("Europe/London")),
            action_type=action_type,
            agent=request.user,
        )
        messages.success(request, 'Employee activated successfully!')
        return redirect('/s_edit_employee/' + str(emp_id))
    return render(request, 'home/s_edit_employee.html', {'emp': emp, "history": history})

def approve_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'approve'
    role = Role.objects.get(name=emp.role)
    emp.dashboard = role.dashboard
    emp.mcustomer = role.mcustomer
    emp.customer = role.customer
    emp.archive = role.archive
    emp.client = role.client
    emp.council = role.council
    emp.admin = role.admin
    emp.product = role.product
    emp.globals = role.globals
    emp.finance = role.finance
    emp.hr = role.hr
    emp.security = role.security
    emp.funding_route = role.funding_route
    emp.CJ = role.CJ
    emp.QA = role.QA
    emp.h_dashboard = role.h_dashboard
    emp.h_employee = role.h_employee
    emp.h_application = role.h_application
    emp.h_onboarding = role.h_onboarding
    emp.h_timesheet = role.h_timesheet
    emp.h_emp_action = role.h_emp_action
    emp.h_emp_notify = role.h_emp_notify
    emp.h_offboarding = role.h_offboarding
    emp.h_org_chart = role.h_org_chart
    emp.knowledge_base = role.knowledge_base
    emp.s_employee = role.s_employee
    emp.s_role = role.s_role
    emp.s_client = role.s_client
    emp.save()
    emp.employee_user.add_emp_action(
        created_at=datetime.now(pytz.timezone("Europe/London")),
        action_type="Role approved",
        agent=request.user,
    )
    messages.success(request, 'Role approved successfully!')
    return redirect('/s_edit_employee/' + str(emp_id))

def deny_role(request, emp_id):
    emp = User.objects.get(pk=emp_id)
    emp.approved = 'deny'
    emp.save()
    emp.employee_user.add_emp_action(
        created_at=datetime.now(pytz.timezone("Europe/London")),
        action_type="Role denied",
        agent=request.user,
    )

    messages.success(request, 'Role denied successfully!')
    return redirect('/s_edit_employee/' + str(emp_id))

def change_otp_mail(request, emp_id):
    emp = get_object_or_404(User, pk=emp_id)
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            if User.objects.filter(email=new_email).exists():
                messages.error(request, 'This email is already in use!')
                return redirect('/s_edit_employee/' + str(emp_id))
            emp.email = new_email
            emp.save()
            messages.success(request, 'OTP mail changed successfully!')
            emp.employee_user.add_emp_action(
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type="Email updated to " + new_email,
                agent=request.user,
            )

        else:
            messages.error(request, 'Email cannot be empty.')
    return redirect('/s_edit_employee/' + str(emp_id))

def edit_role(request, role_id):
    role = Role.objects.get(pk=role_id)
    if request.method == 'POST':
        role.name = request.POST.get('role')
        role.dashboard = request.POST.get('dashboard') == 'on'
        role.mcustomer = request.POST.get('mcustomer') == 'on'
        role.customer = request.POST.get('customer') == 'on'
        role.client = request.POST.get('client') == 'on'
        role.council = request.POST.get('council') == 'on'
        role.admin = request.POST.get('admin') == 'on'
        role.archive = request.POST.get('archive') == 'on'
        role.product = request.POST.get('product') == 'on'
        role.globals = request.POST.get('global') == 'on'
        role.finance = request.POST.get('finance') == 'on'
        role.hr = request.POST.get('hr') == 'on'
        role.security = request.POST.get('security') == 'on'
        role.funding_route = request.POST.get('funding_route') == 'on'
        role.CJ = request.POST.get('CJ') == 'on'
        role.QA = request.POST.get('QA') == 'on'
        role.h_dashboard = request.POST.get('h_dashboard') == 'on'
        role.h_employee = request.POST.get('h_employee') == 'on'
        role.h_application = request.POST.get('h_application') == 'on'
        role.h_onboarding = request.POST.get('h_onboarding') == 'on'
        role.h_timesheet = request.POST.get('h_timesheet') == 'on'
        role.h_emp_action = request.POST.get('h_emp_action') == 'on'
        role.h_emp_notify = request.POST.get('h_emp_notify') == 'on'
        role.h_offboarding = request.POST.get('h_offboarding') == 'on'
        role.h_org_chart = request.POST.get('h_org_chart') == 'on'
        role.knowledge_base = request.POST.get('knowledge_base') == 'on'
        role.s_employee = request.POST.get('s_employee') == 'on'
        role.s_role = request.POST.get('s_role') == 'on'
        role.s_client = request.POST.get('s_client') == 'on'
        role.save()
        messages.success(request, 'Role updated successfully!')
        return redirect('security_app:role')
    return render(request, 'home/edit_role.html', {'role': role})

def bulk_delete_roles(request):
    if request.method == "GET":
        role_ids_str = request.GET.get("ids", "")
        try:
            role_ids = [int(id) for id in role_ids_str.split(",") if id.isdigit()]
            if role_ids:
                Role.objects.filter(id__in=role_ids).delete()
                messages.success(request, "Selected roles deleted successfully.")
            else:
                messages.warning(request, "No valid role IDs provided for deletion.")
        except Exception as e:
            messages.error(request, f"Error deleting roles: {e}")
        return redirect("security_app:role")

def delete_customer_session(request):
    keys_to_delete = [
        'first_name', 'last_name', 'phone_number', 'email', 'postcode',
        'street_name', 'house_name', 'city', 'county', 'country',
        'campaign', 'client'
    ]
    for key in keys_to_delete:
        request.session.pop(key, None)

def reset_password(request, emp_id):
    if request.method == 'POST':
        password = request.POST.get('password')
        conform_password = request.POST.get('conform_password')
        if password != conform_password:
            messages.error(request, 'Password and conform password does not match!')
            return redirect('/s_edit_employee/' + str(emp_id))
        emp = User.objects.get(pk=emp_id)
        emp.password = make_password(password)
        emp.save()
        emp.employee_user.add_emp_action(
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type="Updated Password",
                agent=request.user,
            )
    messages.success(request, 'Password reset successfully!')
    return redirect('/s_edit_employee/' + str(emp_id))

def upload_profile(request, emp_id):
    if request.method == 'POST':
        emp = User.objects.get(pk=emp_id)

        emp.employee_user.employee_image = request.FILES['profile']
        emp.employee_user.save()
        emp.employee_user.add_emp_action(
                created_at=datetime.now(pytz.timezone("Europe/London")),
                action_type="Profile picture updated",
                agent=request.user,
            )
    messages.success(request, 'Profile picture updated successfully!')
    return redirect('/s_edit_employee/' + str(emp_id))