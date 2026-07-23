from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from .models import HeroSlide


@admin.register(HeroSlide)
class HeroSlideAdmin(TranslationAdmin):
    list_display = (
        "title",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = (
        "title",
        "subtitle",
        "badge_text",
    )

    fieldsets = (
        (
            _("محتوای اسلاید"),
            {
                "fields": (
                    "title",
                    "highlighted_text",
                    "subtitle",
                    "badge_text",
                )
            },
        ),
        (
            _("دکمه‌ها"),
            {
                "fields": (
                    "primary_button_text",
                    "primary_button_link",
                    "secondary_button_text",
                    "secondary_button_link",
                )
            },
        ),
        (
            _("بخش پیش‌نمایش"),
            {
                "fields": (
                    "preview_icon",
                    "preview_title",
                    "preview_text",
                )
            },
        ),
        (
            _("تصویر و ظاهر"),
            {
                "fields": (
                    "image",
                    "badge_icon",
                    "color",
                )
            },
        ),
        (
            _("تنظیمات انتشار"),
            {
                "fields": (
                    "order",
                    "is_active",
                )
            },
        ),
    )