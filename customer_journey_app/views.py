from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import (
    Stage,
)
from product_app.models import Product
from funding_route_app.models import Route
from customer_journey_app.models import CJStage
from question_actions_requirements_app.models import Rule_Regulation, Questions
from security_app.models import Role
import pytz
london_tz = pytz.timezone("Europe/London")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def customer_journey(request):
    routes = Route.objects.all().filter(global_archive=False)
    stages = Stage.objects.all().filter(global_archive=False)
    archived_stages = Stage.objects.all().filter(global_archive=True)
    return render(request, "home/customer_journey.html", {"funding_routes": routes, "stages":stages, "archived_stages":archived_stages})

def add_stage(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        stage = Stage.objects.create(
            name=name,
            description=description,
        )
        messages.success(request, "Stage added successfully!")
        return redirect("customer_journey_app:customer_journey")
    return render(request, "home/add_stage.html")

def archive_global_stage(request, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    if stage.global_archive == False:
        stage.global_archive = True
        stage.save()
        messages.success(request, "Archived successfully!")
        return redirect("customer_journey_app:customer_journey")
    else:
        stage.global_archive = False
        stage.save()
        messages.success(request, "Unarchived successfully!")
        return redirect("customer_journey_app:customer_journey")

def cj_route(request, route_id):
    route = Route.objects.get(pk=route_id)
    return render(request, 'home/cj_route.html', {'route':route})

def cj_product(request ,route_id ,product_id):
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stages = Stage.objects.all().filter(global_archive=False)
    roles = Role.objects.all()
    cjstages = CJStage.objects.all().filter(route=route,product=product,client=None)
    
    
    if request.method == 'POST':
        stage = Stage.objects.get(pk=request.POST.get('stage'))
        role = Role.objects.get(pk=request.POST.get('role'))
        CJStage.objects.get_or_create(route=route, product=product,stage=stage, role=role)
        messages.success(request, "Stage added to product successfully!")
        return redirect(f"/cj_product/{route_id}/{product_id}")
    return render(
        request, "home/cj_product.html", {"product": product, "stages": stages, "route":route, "cjstages":cjstages, "roles":roles}
    )


def cj_stage(request, route_id, product_id, stage_id):
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)
    all_questions = Questions.objects.all()
    questions_with_rules = [] 
    questions = []
    
    for rule in Rule_Regulation.objects.all().filter(route=route,product=product,stage=stage,is_client=False):
        questions.append(rule.question)

    for question in questions:
        rule_regulation = (Rule_Regulation.objects.all()
                           .filter(route=route)
                           .filter(product=product)
                           .filter(stage=stage)
                           .filter(question=question)
                           .filter(is_client=False))

        if rule_regulation.exists():
            questions_with_rules.append((question, rule_regulation[0]))
        else:
            questions_with_rules.append((question, None))

    if request.method == 'POST':
        question = Questions.objects.get(pk=request.POST.get('question'))
        stage.question.add(question)
        Rule_Regulation.objects.create(route=route,product=product,stage=stage,question=question)
        cjstages = CJStage.objects.all().filter(route=route,product=product, stage=stage)
        for cjstage in cjstages:
            if cjstage.questions:
                cjstage.questions.append(question.id)
                cjstage.save()
        stage.save()
        messages.success(request, "Question added to stage successfully!")
        return redirect(f"/cj_stage/{route_id}/{product_id}/{stage_id}")

    return render(
        request,
        "home/cj_stage.html",
        {
            "stage": stage,
            "questions": questions_with_rules,
            "route": route,
            "product": product,
            "all_questions": all_questions,
            "json_questions": serialize('json', all_questions),
        },
    )


def add_stage_rule(request, route_id, product_id, stage_id, question_id):
    question = Questions.objects.get(pk=question_id)
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)

    if request.method == "POST":
        dynamicRules = request.POST.getlist("dynamicRule")
        rule_regulation = Rule_Regulation.objects.filter(
            route=route, product=product, stage=stage, question=question
        ).first()

        rule_regulation.rules_regulation = dynamicRules
        rule_regulation.save()

        messages.success(request, "Rules and Regulations added successfully!")
        return redirect(f"/cj_stage/{route_id}/{product_id}/{stage_id}")


def delete_stage(request, stage_id):
    stage = Stage.objects.get(pk=stage_id)
    stage.delete()
    messages.success(request, "Stage deleted successfully!")
    return redirect("customer_journey_app:customer_journey")

def delete_cj_stage(request, route_id ,product_id, stage_id):
    product = Product.objects.get(pk=product_id)
    stage = Stage.objects.get(pk=stage_id)
    route = Route.objects.get(pk=route_id)
    CJStage.objects.filter(route=route, product=product, stage=stage).delete()
    messages.success(request, "Stage deleted successfully!")
    return redirect(f"/cj_product/{route_id}/{product_id}")

def delete_cj_stage_question(request, route_id, product_id, stage_id, question_id):
    stage = Stage.objects.get(pk=stage_id)
    question = Questions.objects.get(pk=question_id)
    route = Route.objects.get(pk=route_id)
    product = Product.objects.get(pk=product_id)
    stage.question.remove(question)
    rule = Rule_Regulation.objects.filter(
            route=route, product=product, stage=stage, question=question
        ).first()
    cjstages = CJStage.objects.all().filter(route=route,product=product, stage=stage)
    for cjstage in cjstages:
        if cjstage.questions and question.id in cjstage.questions:
            print(cjstage.id)
            cjstage.questions.remove(question.id)
            cjstage.save()
    rule.delete()
    question.save()
    stage.save()
    messages.success(request, "Question removed successfully!")
    return redirect(f"/cj_stage/{route_id}/{product_id}/{stage_id}")