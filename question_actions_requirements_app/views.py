from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Questions, Rule_Regulation



def questions(request):
    questions = Questions.objects.all().filter(is_archive=False)
    archive_questions = Questions.objects.all().filter(is_archive=True)
    rule_regulations = Rule_Regulation.objects.all()

    return render(request, 'home/question_actions.html', {'questions':questions, 'rule_regulations':rule_regulations, 'archive_questions':archive_questions})

def add_question(request):
    if request.method == 'POST':
        print(request.POST.get("parameter"))
        question = request.POST.get('question')
        type = request.POST.get('type')
        parameter = request.POST.get("parameter")
        new_question = Questions.objects.create(
            question=question,
            type=type,
            parameter=parameter,
        )
        messages.success(request, "Question is created successfully!")
        return redirect("/questions")
    return render(request, 'home/add_question.html')


def edit_question(request, question_id):
    qquestion = Questions.objects.get(pk=question_id)

    if request.method == "POST":
        question = request.POST.get("question")
        parameter = request.POST.get("parameter")
        new_type = request.POST.get("type")

        if qquestion.type != new_type:
            for rule in qquestion.rules_regulation.all():
                rule.delete()  

        qquestion.question = question
        qquestion.type = new_type
        qquestion.parameter = parameter
        qquestion.save()

        messages.success(request, "Question is edited successfully!")
        return redirect("/questions")

    return render(request, "home/edit_question.html", {"question": qquestion})


def archive_question(request, question_id):
    qquestion = Questions.objects.get(pk=question_id)
    if qquestion.is_archive:
        qquestion.is_archive = False
    else:
        qquestion.is_archive = True
    qquestion.save()
    if qquestion.is_archive:
        messages.success(request, "Question is archived successfully!")
    else:
        messages.success(request, "Question is unarchived successfully!")
    return redirect("/questions")

def client_archive_question(request, question_id, client_id):
    qquestion = Questions.objects.get(pk=question_id)
    if qquestion.is_client_archive:
        qquestion.is_client_archive = False
    else:
        qquestion.is_client_archive = True
    qquestion.save()
    if qquestion.is_client_archive:
        messages.success(request, "Question is archived successfully!")
    else:
        messages.success(request, "Question is unarchived successfully!")
    return redirect("/client-detail/"+str(client_id))
