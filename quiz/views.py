from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    ExamAnswer,
    ExamSession,
    FavoriteQuestion,
    Question,
    QuizCategory,
    WrongQuestion,
)


EXAM_DURATION_MINUTES = 30


def parse_answer_list(value):
    if not value:
        return []

    return sorted([
        int(item.strip())
        for item in value.split(",")
        if item.strip().isdigit()
    ])


def get_question_correct_answers(question):
    correct_answers = parse_answer_list(question.correct_answers)

    if not correct_answers:
        correct_answers = [question.correct_answer]

    return correct_answers


def random_question(request):
    question = Question.objects.filter(
        is_published=True
    ).order_by("?").first()

    if not question:
        return redirect("/dashboard/")

    return redirect("question_detail", pk=question.pk)


def question_detail(request, pk):
    question = get_object_or_404(
        Question,
        pk=pk,
        is_published=True,
    )

    selected_answer = None
    is_correct = None
    correct_answers_list = get_question_correct_answers(question)

    if request.method == "POST":
        raw_selected_answers = request.POST.getlist("answer")

        selected_answers_list = sorted([
            int(item)
            for item in raw_selected_answers
            if item.isdigit()
        ])

        if selected_answers_list:
            selected_answer = selected_answers_list[0]
            is_correct = selected_answers_list == correct_answers_list

    return render(
        request,
        "quiz/question_detail.html",
        {
            "question": question,
            "selected_answer": selected_answer,
            "is_correct": is_correct,
            "correct_answers_list": correct_answers_list,
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
    mode = request.GET.get("mode")
    category_id = request.GET.get("category_id")

    if request.method == "POST":
        mode = request.POST.get("mode", "test")
        category_id = request.POST.get("category_id")

    if not category_id:
        official_parent = QuizCategory.objects.filter(
            slug="hftd-zmon-sl"
        ).first()

        if official_parent:
            return redirect(
                "category_detail",
                category_id=official_parent.id,
            )

        return redirect("/quiz/categories/")

    if mode not in ["practice", "read", "test"]:
        mode = "test"

    questions = list(
        Question.objects.filter(
            is_published=True,
            category_id=category_id,
        ).order_by("id")
    )

    if not questions:
        return redirect("/quiz/categories/")

    exam = ExamSession.objects.create(
        user=request.user,
        mode=mode,
    )

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

    is_test_mode = exam.mode == "test"
    is_practice_mode = exam.mode == "practice"
    is_read_mode = exam.mode == "read"

    exam_end_time = exam.started_at + timedelta(minutes=EXAM_DURATION_MINUTES)
    remaining_seconds = int((exam_end_time - timezone.now()).total_seconds())

    if is_test_mode and remaining_seconds <= 0:
        return redirect("exam_result", exam_id=exam.id)

    question = get_object_or_404(
        Question,
        id=question_id,
    )

    questions = list(exam.questions.all())

    if question not in questions:
        return redirect(
            "exam_question",
            exam_id=exam.id,
            question_id=questions[0].id,
        )

    current_index = questions.index(question)
    progress_percent = int(((current_index + 1) / len(questions)) * 100)

    selected_answer = None
    selected_answers_list = []
    is_correct = None

    correct_answers_list = get_question_correct_answers(question)

    existing_answer = ExamAnswer.objects.filter(
        exam=exam,
        question=question,
    ).first()

    if existing_answer:
        selected_answer = existing_answer.selected_answer
        selected_answers_list = parse_answer_list(existing_answer.selected_answers)

        if not selected_answers_list and selected_answer:
            selected_answers_list = [selected_answer]

        is_correct = existing_answer.is_correct

    if request.method == "POST" and not is_read_mode:
        raw_selected_answers = request.POST.getlist("answer")

        selected_answers_list = sorted([
            int(item)
            for item in raw_selected_answers
            if item.isdigit()
        ])

        is_correct = selected_answers_list == correct_answers_list

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

        if not is_correct:
            WrongQuestion.objects.get_or_create(
                user=request.user,
                question=question,
            )
        else:
            WrongQuestion.objects.filter(
                user=request.user,
                question=question,
            ).delete()

        if is_test_mode:
            if current_index + 1 < len(questions):
                next_question = questions[current_index + 1]

                return redirect(
                    "exam_question",
                    exam_id=exam.id,
                    question_id=next_question.id,
                )

            exam.is_finished = True
            exam.finished_at = timezone.now()
            exam.save(update_fields=["is_finished", "finished_at"])

            return redirect("exam_result", exam_id=exam.id)

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
            status = "correct" if answer.is_correct else "wrong"

        nav_items.append(
            {
                "question": item,
                "number": index + 1,
                "status": status,
                "is_current": item.id == question.id,
                "section": item.section,
            }
        )

    is_favorite = FavoriteQuestion.objects.filter(
        user=request.user,
        question=question,
    ).exists()

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
            "is_favorite": is_favorite,
            "is_test_mode": is_test_mode,
            "is_practice_mode": is_practice_mode,
            "is_read_mode": is_read_mode,
        },
    )


@login_required
def exam_result(request, exam_id):
    exam = get_object_or_404(
        ExamSession,
        id=exam_id,
        user=request.user,
    )

    if not exam.is_finished:
        exam.is_finished = True
        exam.finished_at = timezone.now()
        exam.save(update_fields=["is_finished", "finished_at"])

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
        correct_answers = get_question_correct_answers(answer.question)
        selected_answers = parse_answer_list(answer.selected_answers)

        if not selected_answers and answer.selected_answer:
            selected_answers = [answer.selected_answer]

        wrong_answer_items.append(
            {
                "answer": answer,
                "correct_answers": correct_answers,
                "selected_answers": selected_answers,
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
        correct_answers = get_question_correct_answers(answer.question)
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


@login_required
def my_mistakes(request):
    mistakes = (
        WrongQuestion.objects.filter(user=request.user)
        .select_related("question", "question__category")
        .order_by("-created_at")
    )

    return render(
        request,
        "quiz/my_mistakes.html",
        {
            "mistakes": mistakes,
        },
    )


@login_required
def practice_mistakes(request):
    first_mistake = (
        WrongQuestion.objects.filter(user=request.user)
        .select_related("question")
        .order_by("created_at")
        .first()
    )

    if not first_mistake:
        return redirect("my_mistakes")

    return redirect(
        "question_detail",
        pk=first_mistake.question.id,
    )


@login_required
def toggle_favorite(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    favorite, created = FavoriteQuestion.objects.get_or_create(
        user=request.user,
        question=question,
    )

    if not created:
        favorite.delete()

    return redirect(request.META.get("HTTP_REFERER", "/dashboard/"))


@login_required
def favorites(request):
    favorites = (
        FavoriteQuestion.objects.filter(user=request.user)
        .select_related("question")
        .order_by("-created_at")
    )

    return render(
        request,
        "quiz/favorites.html",
        {
            "favorites": favorites,
        },
    )


@login_required
def practice_favorites(request):
    first_favorite = (
        FavoriteQuestion.objects.filter(user=request.user)
        .select_related("question")
        .order_by("created_at")
        .first()
    )

    if not first_favorite:
        return redirect("favorites")

    return redirect(
        "question_detail",
        pk=first_favorite.question.id,
    )


@login_required
def exam_history(request):
    exams = (
        ExamSession.objects.filter(user=request.user)
        .order_by("-started_at")
    )

    history_items = []

    for exam in exams:
        error_points = exam.total_error_points()
        is_passed = error_points <= 10

        history_items.append(
            {
                "exam": exam,
                "error_points": error_points,
                "is_passed": is_passed,
                "answered_count": exam.answers.count(),
                "total_questions": exam.questions.count(),
            }
        )

    return render(
        request,
        "quiz/exam_history.html",
        {
            "history_items": history_items,
        },
    )


@login_required
def category_list(request):
    categories = (
        QuizCategory.objects.filter(
            parent__isnull=True
        )
        .exclude(slug="hftd-zmon-sl")
        .order_by("id")
    )

    for category in categories:
        direct_count = Question.objects.filter(
            category=category,
            is_published=True,
        ).count()

        children_count = Question.objects.filter(
            category__parent=category,
            is_published=True,
        ).count()

        category.total_questions_count = direct_count + children_count

    return render(
        request,
        "quiz/category_list.html",
        {
            "categories": categories,
        },
    )
    categories = (
        QuizCategory.objects.filter(
            parent__isnull=True
        )
        .exclude(slug="hftd-zmon-sl")
        .order_by("id")
    )

    return render(
        request,
        "quiz/category_list.html",
        {
            "categories": categories,
        },
    )


@login_required
def category_detail(request, category_id):
    parent_category = get_object_or_404(
        QuizCategory,
        id=category_id,
    )

    child_categories = QuizCategory.objects.filter(
        parent=parent_category
    ).order_by("id")

    for category in child_categories:
        direct_count = Question.objects.filter(
            category=category,
            is_published=True,
        ).count()

        children_count = Question.objects.filter(
            category__parent=category,
            is_published=True,
        ).count()

        category.total_questions_count = direct_count + children_count

    if not child_categories.exists():
        return redirect(
            "category_practice",
            category_id=parent_category.id,
        )

    return render(
        request,
        "quiz/category_detail.html",
        {
            "parent_category": parent_category,
            "child_categories": child_categories,
        },
    )
    parent_category = get_object_or_404(
        QuizCategory,
        id=category_id,
    )

    child_categories = QuizCategory.objects.filter(
        parent=parent_category
    ).order_by("id")

    if not child_categories.exists():
        return redirect(
            "category_practice",
            category_id=parent_category.id,
        )

    return render(
        request,
        "quiz/category_detail.html",
        {
            "parent_category": parent_category,
            "child_categories": child_categories,
        },
    )


@login_required
def practice_category(request, category_id):
    category = get_object_or_404(
        QuizCategory,
        id=category_id,
    )

    questions = list(
        Question.objects.filter(
            category=category,
            is_published=True,
        ).order_by("id")
    )

    if not questions:
        return redirect("category_list")

    exam = ExamSession.objects.create(
        user=request.user,
        mode="practice",
    )

    exam.questions.set(questions)

    return redirect(
        "exam_question",
        exam_id=exam.id,
        question_id=questions[0].id,
    )


category_practice = practice_category


@login_required
def start_category_exam(request, category_id):
    category = get_object_or_404(
        QuizCategory,
        id=category_id,
    )

    questions = list(
        Question.objects.filter(
            category=category,
            is_published=True,
        ).order_by("id")
    )

    if not questions:
        return redirect("category_list")

    exam = ExamSession.objects.create(
        user=request.user,
        mode="test",
    )

    exam.questions.set(questions)

    return redirect(
        "exam_question",
        exam_id=exam.id,
        question_id=questions[0].id,
    )


@login_required
def category_read(request, category_id):
    category = get_object_or_404(
        QuizCategory,
        id=category_id,
    )

    questions = list(
        Question.objects.filter(
            category=category,
            is_published=True,
        ).order_by("id")
    )

    if not questions:
        return redirect("/quiz/categories/")

    exam = ExamSession.objects.create(
        user=request.user,
        mode="read",
    )

    exam.questions.set(questions)

    return redirect(
        "exam_question",
        exam_id=exam.id,
        question_id=questions[0].id,
    )


@login_required
def official_exams(request):
    parent = get_object_or_404(
        QuizCategory,
        slug="hftd-zmon-sl",
    )

    exams = QuizCategory.objects.filter(
        parent=parent
    ).order_by("id")

    return render(
        request,
        "quiz/official_exams.html",
        {
            "exams": exams,
        },
    )
@login_required
def category_practice_result(request, exam_id):
    exam = get_object_or_404(
        ExamSession,
        id=exam_id,
        user=request.user,
    )

    total_questions = exam.questions.count()
    answered_count = exam.answers.count()
    correct_count = exam.answers.filter(is_correct=True).count()
    wrong_count = exam.answers.filter(is_correct=False).count()

    wrong_answers = (
        exam.answers.filter(is_correct=False)
        .select_related("question", "question__category")
        .order_by("answered_at")
    )

    wrong_items = []

    for answer in wrong_answers:
        correct_answers = get_question_correct_answers(answer.question)
        selected_answers = parse_answer_list(answer.selected_answers)

        if not selected_answers and answer.selected_answer:
            selected_answers = [answer.selected_answer]

        wrong_items.append(
            {
                "answer": answer,
                "question": answer.question,
                "correct_answers": correct_answers,
                "selected_answers": selected_answers,
            }
        )

    return render(
        request,
        "quiz/category_practice_result.html",
        {
            "exam": exam,
            "total_questions": total_questions,
            "answered_count": answered_count,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "wrong_items": wrong_items,
        },
    )