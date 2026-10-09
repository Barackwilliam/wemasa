from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password/", views.PasswordChangeView.as_view(), name="password"),
    path("refresh-cache/", views.clear_cache, name="clear_cache"),
    path("gallery/upload/", views.bulk_upload, name="bulk_upload"),
    path("messages/<int:pk>/view/", views.message_detail, name="message"),
    path("subscribers/export/", views.export_subscribers, name="export_subscribers"),
    path("edit/<slug:slug>/", views.singleton, name="singleton"),
    path("<slug:slug>/", views.object_list, name="list"),
    path("<slug:slug>/new/", views.create, name="create"),
    path("<slug:slug>/<int:pk>/", views.update, name="update"),
    path("<slug:slug>/<int:pk>/delete/", views.delete, name="delete"),
    path("<slug:slug>/<int:pk>/toggle/", views.toggle, name="toggle"),
]
