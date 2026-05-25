from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from videos.models import Video


def home(request):
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    videos = Video.objects.filter(is_published=True)

    return render(
        request,
        "core/dashboard.html",
        {
            "videos": videos,
        },
    )