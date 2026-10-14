import logging
from types import SimpleNamespace

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .cache import cached_page
from .forms import ContactForm, SubscribeForm
from .models import (
    FAQ, SDG, Video, AboutPage, Certificate, CoreValue, DonationMethod, FocusArea, GalleryImage, HomePage, ImpactStat,
    InvolvementOption, MediaCoverage, Milestone, NewsPost, Objective, PageHeader, Partner, Project,
    Resource, Subscriber, TeamMember, Testimonial,
)

log = logging.getLogger(__name__)

DEFAULT_HEADERS = dict(PageHeader.PAGES)


def page_header(page):
    header = PageHeader.objects.filter(page=page).first()
    if header:
        return header
    label = DEFAULT_HEADERS.get(page, "")
    return SimpleNamespace(page=page, eyebrow="", title=label, subtitle="", image=None, meta_description="",
                           get_page_display=label)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")


def rate_limited(request, scope, limit=5, window=600):
    key = f"wemasa:rate:{scope}:{client_ip(request)}"
    count = cache.get(key, 0)
    if count >= limit:
        return True
    cache.set(key, count + 1, window)
    return False


def published_projects():
    return Project.objects.published().select_related("focus_area").prefetch_related("stats")


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------


@cached_page
def home(request):
    projects = list(published_projects().filter(is_featured=True)[:6])
    news = list(NewsPost.objects.published()[:4])
    return render(request, "website/home.html", {
        "page": HomePage.load(),
        "focus_areas": FocusArea.objects.published().annotate(project_count=Count("projects", filter=Q(projects__is_published=True))),
        "projects": projects,
        "news": news,
        "media": MediaCoverage.objects.published()[:12],
        "testimonials": Testimonial.objects.published().select_related("project")[:6],
        "partners": Partner.objects.published(),
        "values": CoreValue.objects.published()[:4],
        "milestones": Milestone.objects.published(),
        "about": AboutPage.load(),
        "options": InvolvementOption.objects.published()[:3],
        "featured_video": Video.objects.published().filter(is_featured=True).first(),
        "certificates": Certificate.objects.published()[:5],
    })


@cached_page
def about(request):
    return render(request, "website/about.html", {
        "header": page_header("about"),
        "page": AboutPage.load(),
        "objectives": Objective.objects.published(),
        "values": CoreValue.objects.published(),
        "milestones": Milestone.objects.published(),
        "leaders": TeamMember.objects.published().filter(group="founders")[:4],
        "certificates": Certificate.objects.published(),
        "stats": ImpactStat.objects.published()[:4],
    })


@cached_page
def focus_list(request):
    areas = FocusArea.objects.published().prefetch_related(
        Prefetch("projects", queryset=Project.objects.published(), to_attr="live_projects")
    )
    return render(request, "website/focus_list.html", {"header": page_header("focus"), "areas": areas})


@cached_page
def focus_detail(request, slug):
    area = get_object_or_404(FocusArea.objects.published(), slug=slug)
    return render(request, "website/focus_detail.html", {
        "area": area,
        "projects": published_projects().filter(focus_area=area),
        "others": FocusArea.objects.published().exclude(pk=area.pk),
        "photos": GalleryImage.objects.published().filter(project__focus_area=area)[:8],
    })


@cached_page
def project_list(request):
    projects = published_projects()
    focus = request.GET.get("focus", "")
    status = request.GET.get("status", "")
    if focus:
        projects = projects.filter(focus_area__slug=focus)
    if status in dict(Project.STATUS):
        projects = projects.filter(status=status)
    return render(request, "website/project_list.html", {
        "header": page_header("projects"),
        "projects": projects.annotate(photo_count=Count("photos")),
        "focus_areas": FocusArea.objects.published(),
        "statuses": Project.STATUS,
        "active_focus": focus,
        "active_status": status,
    })


@cached_page
def project_detail(request, slug):
    project = get_object_or_404(published_projects().select_related("report"), slug=slug)
    others = published_projects().exclude(pk=project.pk)
    # projects from the same focus area first, then the rest
    related = list(others.filter(focus_area_id=project.focus_area_id)[:3]) if project.focus_area_id else []
    if len(related) < 3:
        related += list(others.exclude(pk__in=[p.pk for p in related])[: 3 - len(related)])
    return render(request, "website/project_detail.html", {
        "project": project,
        "stats": project.stats.all(),
        "photos": project.photos.filter(is_published=True),
        "videos": project.videos.filter(is_published=True),
        "partners": project.partners.filter(is_published=True),
        "testimonials": project.testimonials.filter(is_published=True),
        "news": NewsPost.objects.published().filter(project=project)[:3],
        "related": related,
    })


@cached_page
def impact(request):
    return render(request, "website/impact.html", {
        "header": page_header("impact"),
        "stats": ImpactStat.objects.published(),
        "sdgs": SDG.objects.published(),
        "milestones": Milestone.objects.published(),
        "projects": published_projects().prefetch_related("stats")[:6],
        "testimonials": Testimonial.objects.published()[:6],
    })


@cached_page
def sdgs(request):
    return render(request, "website/sdgs.html", {"header": page_header("sdgs"), "sdgs": SDG.objects.published()})


@cached_page
def resources(request):
    items = Resource.objects.published().prefetch_related("projects")
    category = request.GET.get("type", "")
    if category in dict(Resource.CATEGORIES):
        items = items.filter(category=category)
    used = set(Resource.objects.published().values_list("category", flat=True))
    return render(request, "website/resources.html", {
        "header": page_header("resources"),
        "resources": items,
        "categories": [c for c in Resource.CATEGORIES if c[0] in used],
        "active": category,
    })


@cached_page
def media_coverage(request):
    items = MediaCoverage.objects.published()
    kind = request.GET.get("type", "")
    if kind in dict(MediaCoverage.TYPES):
        items = items.filter(media_type=kind)
    used = set(MediaCoverage.objects.published().values_list("media_type", flat=True))
    return render(request, "website/media.html", {
        "header": page_header("media"),
        "items": items,
        "outlets": MediaCoverage.objects.published().values_list("outlet", flat=True).distinct(),
        "types": [t for t in MediaCoverage.TYPES if t[0] in used],
        "active": kind,
        "total": MediaCoverage.objects.published().count(),
    })


@cached_page
def news_list(request):
    posts = NewsPost.objects.published()
    category = request.GET.get("category", "")
    featured = None
    if category in dict(NewsPost.CATEGORIES):
        posts = posts.filter(category=category)
    else:
        # The featured story sits in its own banner, so it is left out of the grid below.
        featured = posts.filter(is_featured=True).first()
        if featured:
            posts = posts.exclude(pk=featured.pk)
    page = Paginator(posts, 9).get_page(request.GET.get("page"))
    used = set(NewsPost.objects.published().values_list("category", flat=True))
    return render(request, "website/news_list.html", {
        "header": page_header("news"),
        "page_obj": page,
        "featured": featured if page.number == 1 else None,
        "categories": [c for c in NewsPost.CATEGORIES if c[0] in used],
        "active": category,
    })


@cached_page
def news_detail(request, slug):
    post = get_object_or_404(NewsPost.objects.published().select_related("project"), slug=slug)
    return render(request, "website/news_detail.html", {
        "post": post,
        "more": NewsPost.objects.published().exclude(pk=post.pk)[:3],
    })


@cached_page
def gallery(request):
    photos = GalleryImage.objects.published().select_related("project")
    album = request.GET.get("album", "")
    albums = sorted({p.album_name for p in photos})
    if album:
        photos = [p for p in photos if p.album_name == album]
    return render(request, "website/gallery.html", {
        "header": page_header("gallery"), "photos": photos, "albums": albums, "active": album,
    })


@cached_page
def team(request):
    members = TeamMember.objects.published()
    groups = []
    for key, label in TeamMember.GROUPS:
        people = [m for m in members if m.group == key]
        if people:
            groups.append({"key": key, "label": label, "members": people})
    return render(request, "website/team.html", {"header": page_header("team"), "groups": groups})


@cached_page
def partners(request):
    items = list(Partner.objects.published())
    titles = {
        "funding": "Funding partners", "international": "International partners", "government": "Government partners", "corporate": "Corporate partners",
        "ngo": "Civil society partners", "community": "Community partners", "media": "Media partners",
    }
    groups = []
    for key, label in Partner.CATEGORIES:
        members = [p for p in items if p.category == key]
        if members:
            groups.append({"key": key, "label": titles.get(key, label), "partners": members})
    return render(request, "website/partners.html", {
        "header": page_header("partners"),
        "groups": groups,
        "count": len(items),
        "options": InvolvementOption.objects.published()[:3],
    })


@cached_page
def videos(request):
    items = list(Video.objects.published().select_related("project"))
    featured = next((v for v in items if v.is_featured), items[0] if items else None)
    return render(request, "website/videos.html", {
        "header": page_header("videos"),
        "featured": featured,
        "videos": [v for v in items if v is not featured],
    })


# Gallery albums whose first photo illustrates an involvement option (matched on a word in its title).
INVOLVEMENT_PHOTOS = [
    ("volunteer", "Beach cleanups"), ("partner", "World Cleanup Day 2026"), ("school", "School tree planting"),
    ("media", "Women journalists workshop"),
]


@cached_page
def get_involved(request):
    options = list(InvolvementOption.objects.published())
    photos = GalleryImage.objects.published().order_by("order", "id")
    for o in options:
        album = next((a for word, a in INVOLVEMENT_PHOTOS if word in o.title.lower()), None)
        o.photo = photos.filter(album=album).first() if album else None
    return render(request, "website/get_involved.html", {
        "header": page_header("involved"),
        "options": options,
        "stats": ImpactStat.objects.published().filter(show_on_home=True)[:4],
        "faqs": FAQ.objects.published(),
        "form": ContactForm(initial={"topic": "volunteer"}),
    })


@cached_page
def donate(request):
    methods = DonationMethod.objects.published()
    return render(request, "website/donate.html", {
        "header": page_header("donate"),
        "bank": [m for m in methods if m.kind == "bank"],
        "mobile": [m for m in methods if m.kind == "mobile"],
        "other": [m for m in methods if m.kind == "other"],
        "stats": ImpactStat.objects.published()[:4],
        "faqs": FAQ.objects.published(),
    })


@csrf_exempt  # pages are cached, so the form cannot carry a per-visitor token; a honeypot and rate limit protect it
@cached_page
def contact(request):
    form = ContactForm(request.POST or None, initial={"topic": request.GET.get("topic", "general")})
    if request.method == "POST":
        if rate_limited(request, "contact"):
            form.add_error(None, "You have sent several messages in a short time. Please try again in a few minutes.")
        elif form.is_valid():
            if not form.is_spam():
                message = form.save()
                notify_team(message)
            return redirect(f"{reverse('website:contact')}?sent=1#message")
    return render(request, "website/contact.html", {
        "header": page_header("contact"),
        "form": form,
        "sent": request.GET.get("sent") == "1",
    }, status=400 if request.method == "POST" else 200)


def notify_team(message):
    recipients = settings.CONTACT_NOTIFY_EMAILS
    if not recipients:
        from .models import SiteSettings

        email = SiteSettings.load().email
        recipients = [email] if email else []
    if not recipients:
        return
    try:
        send_mail(
            subject=f"[WEMASA website] {message.get_topic_display()} from {message.name}",
            message=(
                f"Name: {message.name}\nEmail: {message.email}\nPhone: {message.phone}\n"
                f"Organisation: {message.organisation}\nTopic: {message.get_topic_display()}\n\n{message.message}"
            ),
            from_email=None,
            recipient_list=recipients,
            fail_silently=True,
        )
    except Exception:  # email problems must never break the form
        log.exception("Could not send contact notification")


@csrf_exempt
@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    back = request.POST.get("next") or "/"
    if not back.startswith("/") or back.startswith("//"):
        back = "/"
    if rate_limited(request, "subscribe", limit=8):
        status = "limit"
    elif form.is_valid():
        if not form.is_spam():
            sub, created = Subscriber.objects.get_or_create(email=form.cleaned_data["email"].lower())
            if not sub.is_active:
                sub.is_active = True
                sub.save(update_fields=["is_active"])
        status = "ok"
    else:
        status = "invalid"
    if request.headers.get("x-requested-with") == "fetch":
        return HttpResponse(status, content_type="text/plain", status=200 if status == "ok" else 400)
    sep = "&" if "?" in back else "?"
    return redirect(f"{back.split('#')[0]}{sep}subscribed={status}#newsletter")


def search(request):
    q = (request.GET.get("q") or "").strip()[:100]
    results = {}
    if len(q) >= 2:
        media_url, team_url, docs_url = reverse("website:media"), reverse("website:team"), reverse("website:resources")
        groups = {
            "Projects": [(p.title, p.summary, p.get_absolute_url()) for p in published_projects().filter(
                Q(title__icontains=q) | Q(summary__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))[:10]],
            "Focus areas": [(a.title, a.summary, a.get_absolute_url()) for a in FocusArea.objects.published().filter(
                Q(title__icontains=q) | Q(summary__icontains=q))[:10]],
            "News & stories": [(n.title, n.summary, n.get_absolute_url()) for n in NewsPost.objects.published().filter(
                Q(title__icontains=q) | Q(body__icontains=q))[:10]],
            "Reports": [(r.title, r.description, docs_url) for r in Resource.objects.published().filter(
                Q(title__icontains=q) | Q(description__icontains=q))[:10]],
            "In the media": [(c.headline, c.outlet, media_url) for c in MediaCoverage.objects.published().filter(
                Q(headline__icontains=q) | Q(outlet__icontains=q))[:10]],
            "Videos": [(v.title, v.description, reverse("website:videos")) for v in Video.objects.published().filter(
                Q(title__icontains=q) | Q(description__icontains=q))[:10]],
            "Team": [(t.name, t.role, team_url) for t in TeamMember.objects.published().filter(
                Q(name__icontains=q) | Q(role__icontains=q))[:10]],
        }
        results = {k: [{"title": t, "text": x, "url": u} for t, x, u in v] for k, v in groups.items() if v}
    return render(request, "website/search.html", {
        "header": page_header("search"), "q": q, "results": results,
        "total": sum(len(v) for v in results.values()),
    })


def health(request):
    """Light endpoint for uptime monitors (e.g. UptimeRobot): keeps the free Render service awake."""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return HttpResponse("database unavailable", content_type="text/plain", status=503)
    response = HttpResponse("ok", content_type="text/plain")
    response["Cache-Control"] = "no-store"
    return response


def robots_txt(request):
    lines = ["User-agent: *", "Disallow: /dashboard/", "Disallow: /system-admin/", "Disallow: /search/",
             f"Sitemap: {(settings.SITE_URL or request.build_absolute_uri('/').rstrip('/'))}{reverse('sitemap')}"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    from django.template import loader

    return HttpResponse(loader.get_template("500.html").render(), status=500)
