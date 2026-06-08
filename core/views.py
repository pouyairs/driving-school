from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from quiz.models import ExamAnswer, ExamSession, Question, QuizCategory, WrongQuestion
from videos.models import Category, Video, WatchedVideo


def home(request):
    User = get_user_model()

    return render(
        request,
        "core/home.html",
        {
            "videos_count": Video.objects.filter(is_published=True).count(),
            "courses_count": Category.objects.count(),
            "students_count": User.objects.count(),
            "blog_count": 3,
        },
    )


@login_required
def dashboard(request):
    categories = Category.objects.prefetch_related("videos").all()

    total_videos = Video.objects.filter(is_published=True).count()

    watched_video_ids = list(
        WatchedVideo.objects.filter(
            user=request.user
        ).values_list("video_id", flat=True)
    )

    watched_count = len(watched_video_ids)

    progress_percent = 0
    if total_videos > 0:
        progress_percent = int((watched_count / total_videos) * 100)

    next_video = (
        Video.objects.filter(is_published=True)
        .exclude(id__in=watched_video_ids)
        .order_by("order", "-created_at")
        .first()
    )

    total_exams = ExamSession.objects.filter(user=request.user).count()

    passed_exams = 0

    for exam in ExamSession.objects.filter(user=request.user):
        if exam.total_error_points() <= 10:
            passed_exams += 1

    failed_exams = total_exams - passed_exams

    mistakes_count = WrongQuestion.objects.filter(user=request.user).count()

    pass_rate = 0
    if total_exams > 0:
        pass_rate = round((passed_exams / total_exams) * 100)

    category_stats = []

    learning_categories = (
        QuizCategory.objects
        .filter(parent__isnull=False)
        .exclude(parent__slug="hftd-zmon-sl")
        .order_by("id")
        )

    for category in learning_categories:
        question_ids = Question.objects.filter(
            category=category
        ).values_list("id", flat=True)

        total_answers = ExamAnswer.objects.filter(
            exam__user=request.user,
            question_id__in=question_ids,
        ).count()

        correct_answers = ExamAnswer.objects.filter(
            exam__user=request.user,
            question_id__in=question_ids,
            is_correct=True,
        ).count()

        success_rate = 0

        if total_answers > 0:
            success_rate = round((correct_answers / total_answers) * 100)

        if total_answers > 0:
            category_stats.append(
                {
                    "category": category,
                    "success_rate": success_rate,
                    "total_answers": total_answers,
                }
            )

    return render(
        request,
        "core/dashboard.html",
        {
            "categories": categories,
            "total_videos": total_videos,
            "watched_count": watched_count,
            "progress_percent": progress_percent,
            "watched_video_ids": watched_video_ids,
            "next_video": next_video,
            "total_exams": total_exams,
            "passed_exams": passed_exams,
            "failed_exams": failed_exams,
            "mistakes_count": mistakes_count,
            "pass_rate": pass_rate,
            "category_stats": category_stats,
        },
    )


@staff_member_required
def admin_reports(request):
    User = get_user_model()

    total_users = User.objects.count()
    total_videos = Video.objects.filter(is_published=True).count()
    total_watched_videos = WatchedVideo.objects.count()
    total_exams = ExamSession.objects.count()

    passed_exams = 0
    failed_exams = 0
    total_error_points_sum = 0

    exams = ExamSession.objects.all()

    for exam in exams:
        error_points = exam.total_error_points()
        total_error_points_sum += error_points

        if error_points <= 10:
            passed_exams += 1
        else:
            failed_exams += 1

    pass_rate = 0
    fail_rate = 0
    average_error_points = 0

    if total_exams > 0:
        pass_rate = int((passed_exams / total_exams) * 100)
        fail_rate = int((failed_exams / total_exams) * 100)
        average_error_points = round(total_error_points_sum / total_exams, 1)

    most_wrong_questions = (
        ExamAnswer.objects.filter(is_correct=False)
        .values(
            "question__id",
            "question__title",
            "question__category__name",
            "question__section",
        )
        .annotate(wrong_count=Count("id"))
        .order_by("-wrong_count")[:10]
    )

    hardest_categories = (
        ExamAnswer.objects.filter(is_correct=False)
        .exclude(question__category__slug="hftd-zmon-sl")
        .exclude(question__category__parent__slug="hftd-zmon-sl")
        .values(
            "question__category__name",
        )
        .annotate(wrong_count=Count("id"))
        .order_by("-wrong_count")[:10]
    )

    most_active_users = (
        ExamSession.objects.values(
            "user__username",
            "user__email",
        )
        .annotate(exam_count=Count("id"))
        .order_by("-exam_count")[:10]
    )

    most_watched_videos = (
        WatchedVideo.objects.values(
            "video__title",
            "video__category__name",
        )
        .annotate(watched_count=Count("id"))
        .order_by("-watched_count")[:10]
    )

    return render(
        request,
        "core/admin_reports.html",
        {
            "total_users": total_users,
            "total_videos": total_videos,
            "total_watched_videos": total_watched_videos,
            "total_exams": total_exams,
            "passed_exams": passed_exams,
            "failed_exams": failed_exams,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
            "average_error_points": average_error_points,
            "most_wrong_questions": most_wrong_questions,
            "hardest_categories": hardest_categories,
            "most_active_users": most_active_users,
            "most_watched_videos": most_watched_videos,
            "total_payments": 0,
            "total_revenue": 0,
        },
    )
def coming_soon(request):
    return render(request, "core/coming_soon.html")
