from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from website.sitemaps import SITEMAPS

admin.site.site_header = "WEMASA — System Administration"
admin.site.site_title = "WEMASA Admin"

urlpatterns = [
    path("system-admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("", include("website.urls")),
]

if settings.SERVE_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "website.views.page_not_found"
handler500 = "website.views.server_error"
