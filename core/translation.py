from modeltranslation.translator import TranslationOptions, register

from .models import HeroSlide


@register(HeroSlide)
class HeroSlideTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "highlighted_text",
        "subtitle",
        "badge_text",
        "primary_button_text",
        "secondary_button_text",
        "preview_title",
        "preview_text",
    )