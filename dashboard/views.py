import csv
from datetime import datetime
from functools import wraps

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from website.cache import bump_content_version
from website.models import ContactMessage, GalleryImage, HomePage, NewsPost, Project, Subscriber, TeamMember

from .forms import INLINE_FORMSETS, INLINE_TITLES, BulkPhotoForm, fieldsets_for, form_for
from .registry import BY_SLUG, SECTIONS, grouped


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


def get_section(slug):
    section = BY_SLUG.get(slug)
    if not section:
        raise Http404("Unknown section")
    return section


def base_context(request, section=None, **extra):
    return {
        "nav_groups": grouped(),
        "section": section,
        "unread_count": ContactMessage.objects.filter(is_read=False).count(),
        **extra,
    }


def cell(obj, name):
    value = getattr(obj, f"get_{name}_display", None)
    value = value() if callable(value) else getattr(obj, name, "")
    if isinstance(value, bool):
        return {"bool": value}
    if hasattr(value, "strftime"):
        return {"text": value.strftime("%d %b %Y")}
    return {"text": "" if value is None else str(value)}


def monthly(qs, months=6):
    """Counts per calendar month for the last `months` months, oldest first."""
    today = timezone.localdate()
    starts = []
    y, mth = today.year, today.month
    for _ in range(months):
        starts.append((y, mth))
        y, mth = (y, mth - 1) if mth > 1 else (y - 1, 12)
    starts.reverse()
    first = timezone.make_aware(datetime(starts[0][0], starts[0][1], 1))
    tally = {}
    for dt in qs.filter(created_at__gte=first).values_list("created_at", flat=True):
        dt = timezone.localtime(dt)
        tally[(dt.year, dt.month)] = tally.get((dt.year, dt.month), 0) + 1
    rows = [{"label": datetime(yy, mm, 1).strftime("%b"), "full": datetime(yy, mm, 1).strftime("%B %Y"),
             "value": tally.get((yy, mm), 0)} for yy, mm in starts]
    top = max([r["value"] for r in rows] + [1])
    for r in rows:
        r["pct"] = round(r["value"] / top * 100)
    return {"rows": rows, "total": sum(r["value"] for r in rows), "top": top}


def greeting():
    hour = timezone.localtime().hour
    if hour < 12:
        return "Habari za asubuhi"
    if hour < 16:
        return "Habari za mchana"
    return "Habari za jioni"


class LoginView(auth_views.LoginView):
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Django adds the request's "site"; drop it so the site settings from the context processor show through.
        context.pop("site", None)
        home = HomePage.objects.filter(pk=1).only("hero_image").first()
        context["backdrop"] = home.hero_image if home and home.hero_image else None
        return context


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "dashboard/password.html"
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **base_context(self.request)}


# ---------------------------------------------------------------------------


@staff_required
def home(request):
    counts = []
    for s in SECTIONS:
        if s.singleton or s.group in ("Inbox",):
            continue
        counts.append({"section": s, "count": s.model.objects.count()})
    return render(request, "dashboard/home.html", base_context(
        request,
        counts=counts,
        latest_messages=ContactMessage.objects.all()[:6],
        subscriber_count=Subscriber.objects.filter(is_active=True).count(),
        totals={
            "projects": Project.objects.filter(is_published=True).count(),
            "photos": GalleryImage.objects.count(),
            "news": NewsPost.objects.filter(is_published=True).count(),
            "team": TeamMember.objects.filter(is_published=True).count(),
        },
        message_trend=monthly(ContactMessage.objects.all()),
        subscriber_trend=monthly(Subscriber.objects.all()),
        recent_news=NewsPost.objects.order_by("-published_at")[:4],
        recent_photos=GalleryImage.objects.order_by("-pk")[:8],
        hero=HomePage.load(),
        greeting=greeting(),
        now=timezone.now(),
    ))


@staff_required
def object_list(request, slug):
    section = get_section(slug)
    if section.singleton:
        return redirect("dashboard:singleton", slug=slug)
    qs = section.model.objects.all()
    q = request.GET.get("q", "").strip()
    if q and section.search_fields:
        cond = Q()
        for f in section.search_fields:
            cond |= Q(**{f"{f}__icontains": q})
        qs = qs.filter(cond)
    filter_choices, active_filter = [], request.GET.get("filter", "")
    if section.filter_field:
        field = section.model._meta.get_field(section.filter_field)
        if field.is_relation:
            filter_choices = [(str(o.pk), str(o)) for o in field.related_model.objects.all()]
            if active_filter:
                qs = qs.filter(**{f"{section.filter_field}_id": active_filter})
        else:
            filter_choices = list(field.choices or [])
            if active_filter:
                qs = qs.filter(**{section.filter_field: active_filter})
    if any(f.name == "project" or f.name == "focus_area" for f in section.model._meta.fields):
        qs = qs.select_related(*[f.name for f in section.model._meta.fields if f.name in ("project", "focus_area")])
    page = Paginator(qs, 30).get_page(request.GET.get("page"))
    columns = [section.model._meta.get_field(n).verbose_name for n in section.list_display]
    rows = [{"obj": o, "cells": [{**cell(o, n), "label": label} for n, label in zip(section.list_display, columns)],
             "thumb": getattr(o, section.thumb, None) if section.thumb else None,
             "toggle": hasattr(o, "is_published")} for o in page]
    return render(request, "dashboard/list.html", base_context(
        request, section, page_obj=page, rows=rows, columns=columns, q=q,
        filter_choices=filter_choices, active_filter=active_filter,
    ))


def edit_object(request, section, instance=None):
    Form = form_for(section)
    form = Form(request.POST or None, request.FILES or None, instance=instance)
    formsets = []
    for key in section.inlines:
        FS = INLINE_FORMSETS[key]
        title, help_text = INLINE_TITLES.get(key, (key.title(), ""))
        formsets.append({"fs": FS(request.POST or None, instance=instance or section.model(), prefix=key),
                         "title": title, "help": help_text})
    if request.method == "POST" and form.is_valid() and all(f["fs"].is_valid() for f in formsets):
        with transaction.atomic():
            obj = form.save()
            for f in formsets:
                f["fs"].instance = obj
                f["fs"].save()
        if request.POST.get("_action") == "add_another":
            messages.success(request, f"“{obj}” saved. Add the next one below.")
            return redirect("dashboard:create", slug=section.slug)
        messages.success(request, f"“{obj}” saved. The website has been updated.")
        if section.singleton or request.POST.get("_action") == "continue":
            return redirect(request.path)
        return redirect("dashboard:list", slug=section.slug)
    if request.method == "POST":
        messages.error(request, "Please correct the highlighted fields.")
    view_url = section.view_url
    if instance is not None and hasattr(instance, "get_absolute_url") and getattr(instance, "pk", None):
        try:
            view_url = instance.get_absolute_url()
        except Exception:
            pass
    return render(request, "dashboard/form.html", base_context(
        request, section, form=form, fieldsets=fieldsets_for(section, form), formsets=formsets,
        object=instance, view_url=view_url,
    ))


@staff_required
def create(request, slug):
    section = get_section(slug)
    if section.singleton or not section.can_add:
        raise Http404
    return edit_object(request, section)


@staff_required
def update(request, slug, pk):
    section = get_section(slug)
    if section.slug == "messages":
        return redirect("dashboard:message", pk=pk)
    return edit_object(request, section, get_object_or_404(section.model, pk=pk))


@staff_required
def singleton(request, slug):
    section = get_section(slug)
    if not section.singleton:
        raise Http404
    return edit_object(request, section, section.model.load())


@staff_required
def delete(request, slug, pk):
    section = get_section(slug)
    if section.singleton:
        raise Http404
    obj = get_object_or_404(section.model, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        messages.success(request, f"“{name}” was deleted.")
        return redirect("dashboard:list", slug=slug)
    return render(request, "dashboard/confirm_delete.html", base_context(request, section, object=obj))


@staff_required
def toggle(request, slug, pk):
    """Quick publish / unpublish from the list."""
    section = get_section(slug)
    obj = get_object_or_404(section.model, pk=pk)
    if request.method == "POST" and hasattr(obj, "is_published"):
        obj.is_published = not obj.is_published
        obj.save(update_fields=["is_published", "updated_at"] if hasattr(obj, "updated_at") else ["is_published"])
        bump_content_version()
        messages.success(request, f"“{obj}” is now {'published' if obj.is_published else 'hidden'}.")
    return redirect(request.POST.get("next") or reverse("dashboard:list", args=[slug]))


@staff_required
def bulk_upload(request):
    form = BulkPhotoForm(request.POST or None, request.FILES or None, initial={"project": request.GET.get("project")})
    if request.method == "POST" and form.is_valid():
        photos = form.save()
        messages.success(request, f"{len(photos)} photo{'s' if len(photos) != 1 else ''} uploaded.")
        return redirect("dashboard:list", slug="gallery")
    return render(request, "dashboard/bulk_upload.html", base_context(request, BY_SLUG["gallery"], form=form))


@staff_required
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST" and request.POST.get("_action") == "unread":
        msg.is_read = False
        msg.save(update_fields=["is_read"])
        return redirect("dashboard:list", slug="messages")
    if not msg.is_read:
        msg.is_read = True
        msg.save(update_fields=["is_read"])
    return render(request, "dashboard/message.html", base_context(request, BY_SLUG["messages"], msg=msg))


@staff_required
def export_subscribers(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="wemasa-subscribers-{timezone.localdate()}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Email", "Active", "Subscribed on"])
    for s in Subscriber.objects.all():
        writer.writerow([s.email, "yes" if s.is_active else "no", s.created_at.strftime("%Y-%m-%d")])
    return response


@staff_required
def clear_cache(request):
    if request.method == "POST":
        bump_content_version()
        messages.success(request, "The website cache was refreshed.")
    return redirect("dashboard:home")
