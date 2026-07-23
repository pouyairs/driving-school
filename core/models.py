from django.db import models
from django.utils.translation import gettext_lazy as _


class HeroSlide(models.Model):
    COLOR_CHOICES = [
        ("red", _("قرمز")),
        ("blue", _("آبی")),
        ("green", _("سبز")),
        ("purple", _("بنفش")),
    ]

    title = models.CharField(_("عنوان"), max_length=120)
    highlighted_text = models.CharField(_("متن رنگی داخل عنوان"), max_length=80, blank=True)
    subtitle = models.TextField(_("توضیح کوتاه"), blank=True)

    image = models.ImageField(_("عکس بنر"), upload_to="hero_slides/", blank=True, null=True)

    badge_text = models.CharField(_("متن Badge"), max_length=80, default="Driving Theory MVP")
    badge_icon = models.CharField(_("آیکون Badge"), max_length=10, default="🚗")

    primary_button_text = models.CharField(_("متن دکمه اصلی"), max_length=60, default="شروع")
    primary_button_link = models.CharField(_("لینک دکمه اصلی"), max_length=255, default="/")

    secondary_button_text = models.CharField(_("متن دکمه دوم"), max_length=60, blank=True)
    secondary_button_link = models.CharField(_("لینک دکمه دوم"), max_length=255, blank=True)

    preview_icon = models.CharField(_("آیکون کارت سمت چپ"), max_length=10, default="🚗")
    preview_title = models.CharField(_("عنوان کارت سمت چپ"), max_length=100, blank=True)
    preview_text = models.CharField(_("متن کارت سمت چپ"), max_length=180, blank=True)

    color = models.CharField(_("رنگ اسلاید"), max_length=20, choices=COLOR_CHOICES, default="red")
    order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)
    is_active = models.BooleanField(_("فعال باشد؟"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("اسلاید صفحه اصلی")
        verbose_name_plural = _("اسلایدهای صفحه اصلی")
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title
