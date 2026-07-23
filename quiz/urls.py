from django.urls import path

from . import views

urlpatterns = [
    # Main quiz entry
    path("", views.random_question, name="random_question"),

    # Question detail
    path("question/<int:pk>/", views.question_detail, name="question_detail"),

    # Exam flow
    path("exam/", views.exam_player, name="exam_player"),
    path("exam/start/", views.start_exam, name="start_exam"),
    path(
        "exam/<int:exam_id>/<int:question_id>/",
        views.exam_question,
        name="exam_question",
    ),
    path("exam/<int:exam_id>/result/", views.exam_result, name="exam_result"),
    path("exam/<int:exam_id>/review/", views.exam_review, name="exam_review"),

    # Mistakes
    path("my-mistakes/", views.my_mistakes, name="my_mistakes"),
    path("practice-mistakes/", views.practice_mistakes, name="practice_mistakes"),

    # Favorites
    path("favorite/<int:question_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites, name="favorites"),
    path("practice-favorites/", views.practice_favorites, name="practice_favorites"),

    # History
    path("history/", views.exam_history, name="exam_history"),

    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:category_id>/", views.category_detail, name="category_detail"),

    # Category modes
    path("category/<int:category_id>/read/", views.category_read, name="category_read"),
    path(
        "category/<int:category_id>/practice/",
        views.practice_category,
        name="category_practice",
    ),
    path(
        "category/<int:category_id>/exam/",
        views.start_category_exam,
        name="category_exam",
    ),

    # Official exams
    path("official-exams/", views.official_exams, name="official_exams"),

    # Category practice result
    path(
        "category-practice/<int:exam_id>/result/",
        views.category_practice_result,
        name="category_practice_result",
    ),
]