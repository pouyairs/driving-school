from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("نام"), max_length=100)
    slug = models.SlugField(_("نامک"), unique=True)

    class Meta:
        verbose_name = _("دسته‌بندی ویدیو")
        verbose_name_plural = _("دسته‌بندی‌های ویدیو")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Video(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="videos",
        null=True,
        blank=True,
        verbose_name=_("دسته‌بندی"),
    )
    title = models.CharField(_("عنوان"), max_length=200)
    description = models.TextField(_("توضیحات"), blank=True)
    youtube_url = models.URLField(_("نشانی یوتیوب"))
    order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)
    is_published = models.BooleanField(_("منتشر شده"), default=True)
    created_at = models.DateTimeField(_("زمان ایجاد"), auto_now_add=True)

    class Meta:
        verbose_name = _("ویدیو")
        verbose_name_plural = _("ویدیوها")
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def youtube_video_id(self):
        parsed_url = urlparse(self.youtube_url)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed_url.query).get("v", [""])[0]
        if parsed_url.hostname == "youtu.be":
            return parsed_url.path.lstrip("/")
        return ""

    def youtube_thumbnail(self):
        video_id = self.youtube_video_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return ""

    def youtube_embed_url(self):
        video_id = self.youtube_video_id()
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return ""


class WatchedVideo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watched_videos",
        verbose_name=_("کاربر"),
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="watched_by",
        verbose_name=_("ویدیو"),
    )
    watched_at = models.DateTimeField(_("زمان مشاهده"), auto_now_add=True)

    class Meta:
        verbose_name = _("ویدیوی مشاهده‌شده")
        verbose_name_plural = _("ویدیوهای مشاهده‌شده")
        unique_together = ("user", "video")
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"
