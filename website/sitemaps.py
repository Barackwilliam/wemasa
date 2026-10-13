from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import FocusArea, NewsPost, Project


class BaseSitemap(Sitemap):
    # Google should see https:// addresses on the live site.
    protocol = None if settings.DEBUG else "https"


class StaticSitemap(BaseSitemap):
    changefreq = "weekly"

    def items(self):
        return ["home", "about", "focus_list", "project_list", "impact", "sdgs", "resources", "media",
                "news_list", "gallery", "videos", "team", "partners", "get_involved", "donate", "contact"]

    def location(self, item):
        return reverse(f"website:{item}")

    def priority(self, item):
        if item == "home":
            return 1.0
        return 0.9 if item in ("about", "project_list", "focus_list", "news_list") else 0.7


class FocusSitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return FocusArea.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(FocusSitemap):
    priority = 0.8

    def items(self):
        return Project.objects.published()


class NewsSitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return NewsPost.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {"pages": StaticSitemap, "focus": FocusSitemap, "projects": ProjectSitemap, "news": NewsSitemap}
