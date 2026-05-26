from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from videos.models import Category, Video, WatchedVideo


def home(request):
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    categories = Category.objects.prefetch_related("videos").all()

    total_videos = Video.objects.filter(is_published=True).count()

    watched_video_ids = list(
        WatchedVideo.objects.filter(user=request.user).values_list("video_id", flat=True)
    )

    watched_count = len(watched_video_ids)

    progress_percent = 0
    if total_videos > 0:
        progress_percent = int((watched_count / total_videos) * 100)

    next_video = (
        Video.objects.filter(is_published=True)
        .exclude(id__in=watched_video_ids)
        .order_by("order", "-created_at")
        .first()
    )

    return render(
        request,
        "core/dashboard.html",
        {
            "categories": categories,
            "total_videos": total_videos,
            "watched_count": watched_count,
            "progress_percent": progress_percent,
            "watched_video_ids": watched_video_ids,
            "next_video": next_video,
        },
    )