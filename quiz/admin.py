import json
import os
import time

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

import google.generativeai as genai

from .models import (
    ExamAnswer,
    ExamSession,
    FavoriteQuestion,
    Question,
    QuizCategory,
)


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None


def translate_question_with_gemini(question):
    if gemini_model is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    prompt = f"""
Translate the following German driving-theory content into natural Persian.

Return ONLY valid JSON.
Do not use Markdown.
Do not add explanations outside the JSON.

Source content:

{{
  "scenario": {json.dumps(question.scenario or "", ensure_ascii=False)},
  "title": {json.dumps(question.title or "", ensure_ascii=False)},
  "option_1": {json.dumps(question.option_1 or "", ensure_ascii=False)},
  "option_2": {json.dumps(question.option_2 or "", ensure_ascii=False)},
  "option_3": {json.dumps(question.option_3 or "", ensure_ascii=False)},
  "option_4": {json.dumps(question.option_4 or "", ensure_ascii=False)},
  "explanation": {json.dumps(question.explanation or "", ensure_ascii=False)}
}}

Return exactly this structure:

{{
  "scenario_fa": "",
  "title_fa": "",
  "option_1_fa": "",
  "option_2_fa": "",
  "option_3_fa": "",
  "option_4_fa": "",
  "explanation_fa": ""
}}
"""

    response = gemini_model.generate_content(prompt)

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json")
        text = text.removesuffix("```").strip()

    elif text.startswith("```"):
        text = text.removeprefix("```")
        text = text.removesuffix("```").strip()

    return json.loads(text)


@admin.action(description=_("ترجمه سؤال‌های انتخاب‌شده به فارسی با Gemini"))
def translate_selected_questions_with_gemini(
    modeladmin,
    request,
    queryset,
):
    if gemini_model is None:
        messages.error(
            request,
            _("متغیر GEMINI_API_KEY تنظیم نشده است."),
        )
        return

    translated_count = 0
    failed_count = 0

    for question in queryset:
        try:
            data = translate_question_with_gemini(question)

            question.scenario_fa = data.get(
                "scenario_fa",
                question.scenario_fa,
            )

            question.title_fa = data.get(
                "title_fa",
                question.title_fa,
            )

            question.option_1_fa = data.get(
                "option_1_fa",
                question.option_1_fa,
            )

            question.option_2_fa = data.get(
                "option_2_fa",
                question.option_2_fa,
            )

            question.option_3_fa = data.get(
                "option_3_fa",
                question.option_3_fa,
            )

            question.option_4_fa = data.get(
                "option_4_fa",
                question.option_4_fa,
            )

            question.explanation_fa = data.get(
                "explanation_fa",
                question.explanation_fa,
            )

            question.save(
                update_fields=[
                    "scenario_fa",
                    "title_fa",
                    "option_1_fa",
                    "option_2_fa",
                    "option_3_fa",
                    "option_4_fa",
                    "explanation_fa",
                ]
            )

            translated_count += 1

            # جلوگیری از Rate Limit در اجرای گروهی
            time.sleep(15)

        except Exception as error:
            failed_count += 1

            messages.error(
                request,
                _("ترجمه سؤال شماره %(question_id)s ناموفق بود: %(error)s") % {"question_id": question.id, "error": error},
            )

    if translated_count:
        messages.success(
            request,
            _("%(count)s سؤال با موفقیت به فارسی ترجمه شد.") % {"count": translated_count},
        )

    if failed_count:
        messages.warning(
            request,
            _("ترجمه %(count)s سؤال ناموفق بود.") % {"count": failed_count},
        )


# ---------------------------------------------------------
# Proxy models for category management
# ---------------------------------------------------------

class MainCategory(QuizCategory):
    class Meta:
        proxy = True
        verbose_name = _("دسته‌بندی اصلی")
        verbose_name_plural = _("دسته‌بندی‌های اصلی")


class SubCategory(QuizCategory):
    class Meta:
        proxy = True
        verbose_name = _("زیردسته")
        verbose_name_plural = _("زیردسته‌ها")


# ---------------------------------------------------------
# Main categories
# ---------------------------------------------------------

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )

    search_fields = (
        "name",
        "name_fa",
        "name_de",
        "name_en",
        "slug",
    )

    ordering = (
        "name",
    )

    fields = (
        "name_fa",
        "name_de",
        "name_en",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name_en",),
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(parent__isnull=True)
        )

    def save_model(self, request, obj, form, change):
        obj.parent = None
        super().save_model(request, obj, form, change)


# ---------------------------------------------------------
# Subcategories
# ---------------------------------------------------------

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "parent",
        "slug",
    )

    list_filter = (
        "parent",
    )

    search_fields = (
        "name",
        "name_fa",
        "name_de",
        "name_en",
        "slug",
        "parent__name",
        "parent__name_fa",
        "parent__name_de",
        "parent__name_en",
    )

    ordering = (
        "parent__name",
        "name",
    )

    fields = (
        "parent",
        "name_fa",
        "name_de",
        "name_en",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name_en",),
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(parent__isnull=False)
        )


# ---------------------------------------------------------
# Questions
# ---------------------------------------------------------

@admin.register(Question)
class QuestionAdmin(TranslationAdmin):
    actions = [
        translate_selected_questions_with_gemini,
    ]

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
        "created_at",
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
            _("دسته‌بندی"),
            {
                "fields": (
                    "main_category",
                    "sub_category",
                    "category",
                ),
            },
        ),
        (
            _("محتوای سوال"),
            {
                "fields": (
                    "section",
                    "scenario",
                    "title",
                    "image",
                    "video_url",
                    "max_video_replays",
                ),
            },
        ),
        (
            _("گزینه‌های پاسخ"),
            {
                "fields": (
                    "option_1",
                    "option_2",
                    "option_3",
                    "option_4",
                    "correct_answer",
                    "correct_answers",
                ),
            },
        ),
        (
            _("توضیحات و تنظیمات آزمون"),
            {
                "fields": (
                    "points",
                    "explanation",
                    "is_published",
                    "created_at",
                ),
            },
        ),
    )


# ---------------------------------------------------------
# Exam sessions
# ---------------------------------------------------------

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

    filter_horizontal = (
        "questions",
    )


# ---------------------------------------------------------
# Exam answers
# ---------------------------------------------------------

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

    readonly_fields = (
        "answered_at",
    )


# ---------------------------------------------------------
# Favorite questions
# ---------------------------------------------------------

@admin.register(FavoriteQuestion)
class FavoriteQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "question",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "question__title",
    )

    readonly_fields = (
        "created_at",
    )