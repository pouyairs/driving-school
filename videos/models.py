from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
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
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    youtube_url = models.URLField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
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
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="watched_by",
    )
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "video")
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"