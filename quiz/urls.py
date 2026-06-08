from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.random_question,
        name="random_question",
    ),

    path(
        "exam/start/",
        views.start_exam,
        name="start_exam",
    ),

    path(
        "exam/<int:exam_id>/<int:question_id>/",
        views.exam_question,
        name="exam_question",
    ),

    path(
        "exam/",
        views.exam_player,
        name="exam_player",
    ),

    path(
        "<int:pk>/",
        views.question_detail,
        name="question_detail",
    ),
    path("exam/<int:exam_id>/result/", views.exam_result, name="exam_result"),
    
    
    path("exam/<int:exam_id>/review/", views.exam_review, name="exam_review"),
    path("my-mistakes/", views.my_mistakes, name="my_mistakes"),
    path("practice-mistakes/", views.practice_mistakes, name="practice_mistakes"),
    path("favorite/<int:question_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites, name="favorites"),
    path(
    "practice-favorites/",
    views.practice_favorites,
    name="practice_favorites",
),
    path("history/", views.exam_history, name="exam_history"),
    path(
    "categories/",
    views.category_list,
    name="category_list",
),
        path(
    "categories/<int:category_id>/",
    views.category_detail,
    name="category_detail",
),
        path(
    "category/<int:category_id>/read/",
    views.category_read,
    name="category_read",
),
    path(
    "category/<int:category_id>/practice/",
    views.practice_category,
    name="practice_category",
),
    path(
    "category/<int:category_id>/exam/",
    views.start_category_exam,
    name="start_category_exam",
),
    path(
    "official-exams/",
    views.official_exams,
    name="official_exams",
),
path(
    "category-practice/<int:exam_id>/result/",
    views.category_practice_result,
    name="category_practice_result",
),
]