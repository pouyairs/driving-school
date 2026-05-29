from django.contrib import admin

from .models import Category, Video, WatchedVideo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
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
class VideoAdmin(admin.ModelAdmin):
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
    )

    search_fields = (
        "title",
        "description",
        "youtube_url",
    )

    readonly_fields = (
        "created_at",
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