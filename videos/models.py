from urllib.parse import parse_qs, urlparse

from django.db import models


class Video(models.Model):
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