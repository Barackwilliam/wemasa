from django.conf import settings

from .models import FocusArea, SiteSettings


def site(request):
    if request.path.startswith(("/dashboard", "/system-admin")):
        return {"site": SiteSettings.load()}
    return {
        "site": SiteSettings.load(),
        "nav_focus_areas": list(FocusArea.objects.published().only("title", "slug", "icon")[:8]),
        "site_url": settings.SITE_URL or request.build_absolute_uri("/").rstrip("/"),
    }
