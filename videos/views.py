from django.shortcuts import get_object_or_404, render

from .models import Video


def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk, is_published=True)
    all_videos = Video.objects.filter(is_published=True)

    return render(
        request,
        "videos/video_detail.html",
        {
            "video": video,
            "all_videos": all_videos,
        },
    )