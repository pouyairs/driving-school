from django.contrib import admin

from .models import ExamAnswer, ExamSession, Question, QuizCategory


@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "section",
        "points",
        "correct_answer",
        "is_published",
        "created_at",
    )

    list_filter = (
        "category",
        "section",
        "is_published",
        "points",
    )

    search_fields = (
        "title",
        "option_1",
        "option_2",
        "option_3",
        "option_4",
        "explanation",
    )

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Question Info",
            {
                "fields": (
                    "category",
                    "section",
                    "title",
                    "image",
                    "video_url",
                    "max_video_replays",
                )
            },
        ),
        (
            "Answers",
            {
                "fields": (
                    "option_1",
                    "option_2",
                    "option_3",
                    "option_4",
                    "correct_answer",
                )
            },
        ),
        (
            "Exam Settings",
            {
                "fields": (
                    "points",
                    "explanation",
                    "is_published",
                    "created_at",
                )
            },
        ),
    )


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "started_at",
        "finished_at",
        "is_finished",
    )

    list_filter = (
        "is_finished",
        "started_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "started_at",
        "finished_at",
    )

    filter_horizontal = ("questions",)


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exam",
        "question",
        "selected_answer",
        "is_correct",
        "answered_at",
    )

    list_filter = (
        "is_correct",
        "answered_at",
    )

    search_fields = (
        "question__title",
        "exam__user__username",
    )

    readonly_fields = ("answered_at",)