from django.contrib import admin

from .models import Question, QuizCategory


@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "correct_answer", "is_published", "created_at")
    list_filter = ("category", "is_published")
    search_fields = ("title", "explanation")