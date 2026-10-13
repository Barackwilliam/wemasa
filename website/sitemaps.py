from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import FocusArea, NewsPost, Project


class StaticSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return ["home", "about", "focus_list", "project_list", "impact", "sdgs", "resources", "media",
                "news_list", "gallery", "videos", "team", "partners", "get_involved", "donate", "contact"]

    def location(self, item):
        return reverse(f"website:{item}")

    def priority(self, item):
        return 1.0 if item == "home" else 0.7


class FocusSitemap(Sitemap):
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


class NewsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return NewsPost.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {"pages": StaticSitemap, "focus": FocusSitemap, "projects": ProjectSitemap, "news": NewsSitemap}
