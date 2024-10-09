from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Questions 


def questions(request):
    questions = Questions.objects.all()
    return render(request, 'home/question_actions.html', {'questions':questions})

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


def delete_question(request, question_id):
    qquestion = Questions.objects.get(pk=question_id)
    qquestion.delete()
    messages.success(request, "Question is deleted successfully!")
    return redirect("/questions")
