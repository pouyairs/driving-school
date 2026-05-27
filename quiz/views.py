from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ExamAnswer, ExamSession, Question


def random_question(request):
    question = (
        Question.objects.filter(
            is_published=True
        )
        .order_by("?")
        .first()
    )

    if not question:
        return redirect("/dashboard/")

    return redirect(
        "question_detail",
        pk=question.pk,
    )


def question_detail(request, pk):
    question = get_object_or_404(
        Question,
        pk=pk,
        is_published=True,
    )

    selected_answer = None
    is_correct = None

    if request.method == "POST":

        selected_answer = int(
            request.POST.get("answer")
        )

        is_correct = (
            selected_answer == question.correct_answer
        )

    return render(
        request,
        "quiz/question_detail.html",
        {
            "question": question,
            "selected_answer": selected_answer,
            "is_correct": is_correct,
        },
    )


def exam_player(request):
    basic_questions = Question.objects.filter(
        is_published=True,
        section=Question.SECTION_BASIC,
    )[:20]

    class_b_questions = Question.objects.filter(
        is_published=True,
        section=Question.SECTION_CLASS_B,
    )[:10]

    current_question = (
        basic_questions.first()
        or class_b_questions.first()
    )

    return render(
        request,
        "quiz/exam_player.html",
        {
            "basic_questions": basic_questions,
            "class_b_questions": class_b_questions,
            "current_question": current_question,
        },
    )


@login_required
def start_exam(request):

    exam = ExamSession.objects.create(
        user=request.user,
    )

    basic_questions = list(
        Question.objects.filter(
            is_published=True,
            section=Question.SECTION_BASIC,
        ).order_by("?")[:20]
    )

    class_b_questions = list(
        Question.objects.filter(
            is_published=True,
            section=Question.SECTION_CLASS_B,
        ).order_by("?")[:10]
    )

    questions = basic_questions + class_b_questions

    exam.questions.set(questions)

    first_question = questions[0]

    return redirect(
        "exam_question",
        exam_id=exam.id,
        question_id=first_question.id,
    )


@login_required
def exam_question(request, exam_id, question_id):

    exam = get_object_or_404(
        ExamSession,
        id=exam_id,
        user=request.user,
    )

    question = get_object_or_404(
        Question,
        id=question_id,
    )

    questions = list(exam.questions.all())

    current_index = questions.index(question)

    selected_answer = None
    is_correct = None

    existing_answer = ExamAnswer.objects.filter(
        exam=exam,
        question=question,
    ).first()

    if existing_answer:
        selected_answer = existing_answer.selected_answer
        is_correct = existing_answer.is_correct

    if request.method == "POST":

        selected_answer = int(
            request.POST.get("answer")
        )

        is_correct = (
            selected_answer == question.correct_answer
        )

        ExamAnswer.objects.update_or_create(
            exam=exam,
            question=question,
            defaults={
                "selected_answer": selected_answer,
                "is_correct": is_correct,
            },
        )

    next_question = None

    if current_index + 1 < len(questions):
        next_question = questions[current_index + 1]

    return render(
        request,
        "quiz/exam_question.html",
        {
            "exam": exam,
            "question": question,
            "questions": questions,
            "current_index": current_index,
            "selected_answer": selected_answer,
            "is_correct": is_correct,
            "next_question": next_question,
        },
    )
@login_required
def exam_result(request, exam_id):
    exam = get_object_or_404(
        ExamSession,
        id=exam_id,
        user=request.user,
    )

    total_questions = exam.questions.count()
    answered_count = exam.answers.count()
    correct_count = exam.answers.filter(is_correct=True).count()
    wrong_count = exam.answers.filter(is_correct=False).count()
    total_error_points = exam.total_error_points()

    is_passed = total_error_points <= 10

    return render(
        request,
        "quiz/exam_result.html",
        {
            "exam": exam,
            "total_questions": total_questions,
            "answered_count": answered_count,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "total_error_points": total_error_points,
            "is_passed": is_passed,
        },
    )