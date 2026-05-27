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
]