from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("our-focus/", views.focus_list, name="focus_list"),
    path("our-focus/<slug:slug>/", views.focus_detail, name="focus_detail"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("impact/", views.impact, name="impact"),
    path("sdgs/", views.sdgs, name="sdgs"),
    path("resources/", views.resources, name="resources"),
    path("in-the-media/", views.media_coverage, name="media"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("videos/", views.videos, name="videos"),
    path("team/", views.team, name="team"),
    path("partners/", views.partners, name="partners"),
    path("get-involved/", views.get_involved, name="get_involved"),
    path("donate/", views.donate, name="donate"),
    path("contact/", views.contact, name="contact"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("search/", views.search, name="search"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("health/", views.health, name="health"),
]
