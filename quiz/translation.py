from modeltranslation.translator import TranslationOptions, register

from .models import Question, QuizCategory


@register(QuizCategory)
class QuizCategoryTranslationOptions(TranslationOptions):
    fields = (
        "name",
    )


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = (
        "scenario",
        "title",
        "option_1",
        "option_2",
        "option_3",
        "option_4",
        "explanation",
    )