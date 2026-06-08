import json
import os
import time

from django.contrib import admin, messages
import google.generativeai as genai
from django.urls import path
from django.shortcuts import redirect

from .models import (
    ExamAnswer,
    ExamSession,
    FavoriteQuestion,
    Question,
    QuizCategory,
)


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash")


def translate_question_with_gemini(question):
    prompt = f"""
Translate this driving theory question content into natural Persian.

Return ONLY valid JSON.
No markdown.
No explanation.

{{
  "scenario": "{question.scenario}",
  "title": "{question.title}",
  "option_1": "{question.option_1}",
  "option_2": "{question.option_2}",
  "option_3": "{question.option_3}",
  "option_4": "{question.option_4}"
}}

Return this JSON format:
{{
  "scenario_translation": "",
  "title_translation": "",
  "option_1_translation": "",
  "option_2_translation": "",
  "option_3_translation": "",
  "option_4_translation": ""
}}
"""

    response = gemini_model.generate_content(prompt)
    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)


@admin.action(description="Translate selected questions with Gemini")
def translate_selected_questions_with_gemini(modeladmin, request, queryset):
    translated_count = 0

    for question in queryset:
        try:
            data = translate_question_with_gemini(question)

            question.scenario_translation = data.get(
                "scenario_translation",
                question.scenario_translation,
            )
            question.title_translation = data.get(
                "title_translation",
                question.title_translation,
            )
            question.option_1_translation = data.get(
                "option_1_translation",
                question.option_1_translation,
            )
            question.option_2_translation = data.get(
                "option_2_translation",
                question.option_2_translation,
            )
            question.option_3_translation = data.get(
                "option_3_translation",
                question.option_3_translation,
            )
            question.option_4_translation = data.get(
                "option_4_translation",
                question.option_4_translation,
            )

            question.save()
            translated_count += 1

            # Free Gemini tier is rate-limited. Keep this for batch actions.
            time.sleep(15)

        except Exception as error:
            messages.error(
                request,
                f"Question #{question.id} translation failed: {error}",
            )

    messages.success(
        request,
        f"{translated_count} question(s) translated with Gemini.",
    )


class MainCategory(QuizCategory):
    class Meta:
        proxy = True
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"


class SubCategory(QuizCategory):
    class Meta:
        proxy = True
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)

    fields = (
        "name",
        "slug",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            parent__isnull=True,
        )

    def save_model(self, request, obj, form, change):
        obj.parent = None
        super().save_model(request, obj, form, change)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "slug")
    list_filter = ("parent",)
    search_fields = ("name", "slug", "parent__name")
    ordering = ("parent__name", "name")

    fields = (
        "parent",
        "name",
        "slug",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            parent__isnull=False,
        )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    actions = [translate_selected_questions_with_gemini]

    list_display = (
        "id",
        "title",
        "main_category",
        "sub_category",
        "category",
        "section",
        "points",
        "correct_answer",
        "is_published",
        "created_at",
    )

    list_filter = (
        "main_category",
        "sub_category",
        "section",
        "is_published",
        "points",
    )

    search_fields = (
        "title",
        "scenario",
        "option_1",
        "option_2",
        "option_3",
        "option_4",
        "explanation",
        "main_category__name",
        "sub_category__name",
    )

    readonly_fields = (
        "category",
        "created_at",
    )

    fieldsets = (
        (
            "Category",
            {
                "fields": (
                    "main_category",
                    "sub_category",
                    "category",
                )
            },
        ),
        (
            "Question Info",
            {
                "fields": (
                    "section",
                    "scenario",
                    "scenario_translation",
                    "title",
                    "title_translation",
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
                    "option_1_translation",
                    "option_2",
                    "option_2_translation",
                    "option_3",
                    "option_3_translation",
                    "option_4",
                    "option_4_translation",
                    "correct_answer",
                    "correct_answers",
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
        "mode",
        "started_at",
        "finished_at",
        "is_finished",
    )

    list_filter = (
        "mode",
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


@admin.register(FavoriteQuestion)
class FavoriteQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "question",
        "created_at",
    )

    search_fields = (
        "user__username",
        "question__title",
    )
