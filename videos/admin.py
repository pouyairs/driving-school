from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from .models import Category, Video, WatchedVideo


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Video)
class VideoAdmin(TranslationAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "order",
        "is_published",
        "created_at",
    )

    list_filter = (
        "category",
        "is_published",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "youtube_url",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        (
            _("محتوای ویدیو"),
            {
                "fields": (
                    "title",
                    "description",
                ),
            },
        ),
        (
            _("دسته‌بندی و ویدیو"),
            {
                "fields": (
                    "category",
                    "youtube_url",
                ),
            },
        ),
        (
            _("تنظیمات انتشار"),
            {
                "fields": (
                    "order",
                    "is_published",
                    "created_at",
                ),
            },
        ),
    )


@admin.register(WatchedVideo)
class WatchedVideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "video",
        "watched_at",
    )

    list_filter = (
        "watched_at",
    )

    search_fields = (
        "user__username",
        "video__title",
    )

    readonly_fields = (
        "user",
        "video",
        "watched_at",
    )