from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import ExamAnswer, ExamSession, Question


EXAM_DURATION_MINUTES = 30


def parse_answer_list(value):
    if not value:
        return []

    return sorted([
        int(item.strip())
        for item in value.split(",")
        if item.strip().isdigit()
    ])


def random_question(request):
    question = Question.objects.filter(is_published=True).order_by("?").first()

    if not question:
        return redirect("/dashboard/")

    return redirect("question_detail", pk=question.pk)


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk, is_published=True)

    selected_answer = None
    is_correct = None

    if request.method == "POST":
        selected_answer = int(request.POST.get("answer"))
        is_correct = selected_answer == question.correct_answer

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

    current_question = basic_questions.first() or class_b_questions.first()

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
    exam = ExamSession.objects.create(user=request.user)

    basic_questions = list(
        Question.objects.filter(
            is_published=True,
            section=Question.SECTION_BASIC,
        ).order_by("id")[:20]
    )

    class_b_questions = list(
        Question.objects.filter(
            is_published=True,
            section=Question.SECTION_CLASS_B,
        ).order_by("id")[:10]
    )

    questions = basic_questions + class_b_questions

    if not questions:
        return redirect("/dashboard/")

    exam.questions.set(questions)

    return redirect(
        "exam_question",
        exam_id=exam.id,
        question_id=questions[0].id,
    )


@login_required
def exam_question(request, exam_id, question_id):
    exam = get_object_or_404(
        ExamSession,
        id=exam_id,
        user=request.user,
    )

    exam_end_time = exam.started_at + timedelta(minutes=EXAM_DURATION_MINUTES)
    remaining_seconds = int((exam_end_time - timezone.now()).total_seconds())

    if remaining_seconds <= 0:
        return redirect("exam_result", exam_id=exam.id)

    question = get_object_or_404(
        Question,
        id=question_id,
    )

    questions = list(exam.questions.all())
    current_index = questions.index(question)
    progress_percent = int(((current_index + 1) / len(questions)) * 100)

    selected_answer = None
    selected_answers_list = []
    selected_answers_text = ""
    is_correct = None

    existing_answer = ExamAnswer.objects.filter(
        exam=exam,
        question=question,
    ).first()

    if existing_answer:
        selected_answer = existing_answer.selected_answer
        selected_answers_text = existing_answer.selected_answers
        selected_answers_list = parse_answer_list(existing_answer.selected_answers)

        if not selected_answers_list and selected_answer:
            selected_answers_list = [selected_answer]

        is_correct = existing_answer.is_correct

    if request.method == "POST":
        raw_selected_answers = request.POST.getlist("answer")

        selected_answers_list = sorted([
            int(item)
            for item in raw_selected_answers
            if item.isdigit()
        ])

        correct_answers = parse_answer_list(question.correct_answers)

        if not correct_answers:
            correct_answers = [question.correct_answer]

        is_correct = selected_answers_list == correct_answers

        selected_answer = (
            selected_answers_list[0]
            if selected_answers_list
            else question.correct_answer
        )

        selected_answers_text = ",".join(
            str(item)
            for item in selected_answers_list
        )

        ExamAnswer.objects.update_or_create(
            exam=exam,
            question=question,
            defaults={
                "selected_answer": selected_answer,
                "selected_answers": selected_answers_text,
                "is_correct": is_correct,
            },
        )

    next_question = None

    if current_index + 1 < len(questions):
        next_question = questions[current_index + 1]

    answers = {
        answer.question_id: answer
        for answer in exam.answers.all()
    }

    nav_items = []

    for index, item in enumerate(questions):
        answer = answers.get(item.id)

        status = "empty"

        if answer:
            if answer.is_correct:
                status = "correct"
            else:
                status = "wrong"

        nav_items.append(
            {
                "question": item,
                "number": index + 1,
                "status": status,
                "is_current": item.id == question.id,
                "section": "basic" if index < 20 else "class_b",
            }
        )
        
    correct_answers_list = parse_answer_list(question.correct_answers)
    if not correct_answers_list:
         correct_answers_list = [question.correct_answer]

    return render(
        request,
        "quiz/exam_question.html",
        {
            "exam": exam,
            "question": question,
            "questions": questions,
            "current_index": current_index,
            "progress_percent": progress_percent,
            "selected_answer": selected_answer,
            "selected_answers_list": selected_answers_list,
            "correct_answers_list": correct_answers_list,
            "is_correct": is_correct,
            "next_question": next_question,
            "remaining_seconds": remaining_seconds,
            "nav_items": nav_items,
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

    wrong_answers = (
        exam.answers.filter(is_correct=False)
        .select_related("question")
        .order_by("answered_at")
    )
    wrong_answer_items = []

    for answer in wrong_answers:

        correct_answers = parse_answer_list(
        answer.question.correct_answers
    )

    if not correct_answers:
        correct_answers = [answer.question.correct_answer]

    wrong_answer_items.append(
        {
            "answer": answer,
            "correct_answers": correct_answers,
        }
    )

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
            "wrong_answer_items": wrong_answer_items,
            "is_passed": is_passed,
        },
    )


@login_required
def exam_review(request, exam_id):
    exam = get_object_or_404(
        ExamSession,
        id=exam_id,
        user=request.user,
    )

    answers = (
        ExamAnswer.objects.filter(exam=exam)
        .select_related("question", "question__category")
        .order_by("answered_at")
    )

    review_items = []

    for answer in answers:
        correct_answers = parse_answer_list(answer.question.correct_answers)

        if not correct_answers:
            correct_answers = [answer.question.correct_answer]

        selected_answers = parse_answer_list(answer.selected_answers)

        if not selected_answers and answer.selected_answer:
            selected_answers = [answer.selected_answer]

        review_items.append(
            {
                "answer": answer,
                "question": answer.question,
                "correct_answers": correct_answers,
                "selected_answers": selected_answers,
            }
        )

    return render(
        request,
        "quiz/exam_review.html",
        {
            "exam": exam,
            "review_items": review_items,
        },
    )