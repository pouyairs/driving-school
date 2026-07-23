from modeltranslation.translator import TranslationOptions, register

from .models import Category, Video


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = (
        "name",
    )


@register(Video)
class VideoTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "description",
    )