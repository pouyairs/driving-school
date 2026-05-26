from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Video, WatchedVideo


def video_list(request):
    categories = Category.objects.prefetch_related("videos").all()

    return render(
        request,
        "videos/video_list.html",
        {
            "categories": categories,
        },
    )


def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk, is_published=True)
    categories = Category.objects.prefetch_related("videos").all()

    watched_video_ids = []

    if request.user.is_authenticated:
        watched_video_ids = list(
            WatchedVideo.objects.filter(user=request.user).values_list("video_id", flat=True)
        )

    next_videos = (
        Video.objects.filter(is_published=True)
        .exclude(id__in=watched_video_ids)
        .exclude(id=video.id)
        .order_by("order", "-created_at")[:2]
    )

    return render(
        request,
        "videos/video_detail.html",
        {
            "video": video,
            "categories": categories,
            "watched_video_ids": watched_video_ids,
            "next_videos": next_videos,
        },
    )


@login_required
def mark_video_watched(request, pk):
    video = get_object_or_404(Video, pk=pk, is_published=True)

    watched_video, created = WatchedVideo.objects.get_or_create(
        user=request.user,
        video=video,
    )

    if not created:
        watched_video.delete()

    return redirect("video_detail", pk=video.pk)