"""
All website content lives here so it can be edited from the dashboard.

Singletons (SiteSettings, HomePage, AboutPage, ...) hold page copy; the other
models are collections (projects, team, news ...).
"""
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator

from .utils import OptimisedImagesMixin, UploadTo, clean_html, unique_slug

ICON_CHOICES = [
    (name, name.replace("-", " ").title())
    for name in (
        "leaf", "sprout", "tree", "recycle", "trash", "droplet", "wave", "sun", "wind", "flame",
        "globe", "map-pin", "school", "graduation", "book", "megaphone", "mic", "newspaper", "camera",
        "users", "user", "heart", "hand-heart", "handshake", "shield", "scale", "eye", "target",
        "lightbulb", "sparkles", "chart", "award", "briefcase", "clipboard", "database", "peace",
        "child", "home", "phone", "mail", "clock", "calendar", "bank", "wallet", "smartphone", "star",
    )
]


class RichTextField(models.TextField):
    """A TextField edited with the rich-text editor and sanitised on save."""

    def pre_save(self, model_instance, add):
        value = clean_html(getattr(model_instance, self.attname))
        setattr(model_instance, self.attname, value)
        return value


class Singleton(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return None

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Orderable(models.Model):
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")
    is_published = models.BooleanField("Published", default=True, help_text="Untick to hide from the website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


# ==========================================================================
# Singletons
# ==========================================================================


class SiteSettings(OptimisedImagesMixin, Singleton):
    image_sizes = {"og_image": 1200}

    org_name = models.CharField("Organisation name", max_length=150, default="WEMASA Tanzania Organization")
    short_name = models.CharField(max_length=40, default="WEMASA")
    tagline = models.CharField(max_length=200, default="Weka Mazingira Safi — Keep the Environment Clean")
    logo = models.ImageField(
        upload_to=UploadTo("brand"), blank=True,
        help_text="Optional. Leave empty to use the official WEMASA logo.",
    )
    footer_about = models.TextField(blank=True)
    registration_number = models.CharField(max_length=60, blank=True)
    registration_year = models.CharField(max_length=10, blank=True)
    registration_note = models.CharField(max_length=200, blank=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    phone_alt = models.CharField("Alternative phone", max_length=40, blank=True)
    whatsapp = models.CharField(
        "WhatsApp number", max_length=40, blank=True, help_text="International format, e.g. 255787618186",
    )
    address = models.CharField("Postal address", max_length=200, blank=True)
    location = models.CharField("Office location", max_length=200, blank=True)
    office_hours = models.CharField(max_length=120, blank=True)
    map_embed_url = models.URLField(
        "Google Maps embed URL", max_length=1000, blank=True,
        help_text="From Google Maps → Share → Embed a map → copy the src link.",
    )

    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    x_twitter = models.URLField("X (Twitter)", blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)

    announcement = models.CharField(
        "Announcement bar", max_length=200, blank=True, help_text="Short notice shown above the menu. Leave empty to hide.",
    )
    announcement_link = models.CharField(max_length=300, blank=True)
    donate_button_text = models.CharField(max_length=40, default="Donate")
    newsletter_title = models.CharField(max_length=120, default="Stay in the loop")
    newsletter_text = models.CharField(max_length=300, blank=True)

    meta_description = models.CharField(
        "Search engine description", max_length=300, blank=True,
        help_text="Shown by Google and when the site is shared on social media.",
    )
    og_image = models.ImageField("Social sharing image", upload_to=UploadTo("brand"), blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    @property
    def social_links(self):
        links = [
            ("facebook", "Facebook", self.facebook), ("instagram", "Instagram", self.instagram),
            ("x", "X", self.x_twitter), ("linkedin", "LinkedIn", self.linkedin),
            ("youtube", "YouTube", self.youtube), ("tiktok", "TikTok", self.tiktok),
        ]
        return [{"icon": i, "name": n, "url": u} for i, n, u in links if u]


class HomePage(OptimisedImagesMixin, Singleton):
    image_sizes = {"hero_image": 2200, "intro_image": 1400, "intro_image_2": 1000, "story_image": 1800, "cta_image": 2000}

    hero_eyebrow = models.CharField(max_length=120, blank=True)
    hero_title = models.CharField(max_length=160)
    hero_highlight = models.CharField(
        max_length=80, blank=True, help_text="A word or phrase from the title to show in the accent colour.",
    )
    hero_subtitle = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to=UploadTo("home"), blank=True)
    hero_primary_text = models.CharField("Primary button text", max_length=40, blank=True)
    hero_primary_url = models.CharField("Primary button link", max_length=300, blank=True)
    hero_secondary_text = models.CharField("Secondary button text", max_length=40, blank=True)
    hero_secondary_url = models.CharField("Secondary button link", max_length=300, blank=True)

    intro_eyebrow = models.CharField(max_length=80, blank=True)
    intro_title = models.CharField(max_length=200, blank=True)
    intro_text = RichTextField(blank=True)
    intro_points = models.TextField(blank=True, help_text="One highlight per line.")
    intro_image = models.ImageField(upload_to=UploadTo("home"), blank=True)
    intro_image_2 = models.ImageField(upload_to=UploadTo("home"), blank=True)
    intro_badge_value = models.CharField(max_length=20, blank=True)
    intro_badge_label = models.CharField(max_length=60, blank=True)

    focus_eyebrow = models.CharField(max_length=80, blank=True)
    focus_title = models.CharField(max_length=200, blank=True)
    focus_subtitle = models.TextField(blank=True)

    impact_eyebrow = models.CharField(max_length=80, blank=True)
    impact_title = models.CharField(max_length=200, blank=True)
    impact_subtitle = models.TextField(blank=True)

    projects_eyebrow = models.CharField(max_length=80, blank=True)
    projects_title = models.CharField(max_length=200, blank=True)
    projects_subtitle = models.TextField(blank=True)

    story_eyebrow = models.CharField(max_length=80, blank=True)
    story_title = models.CharField(max_length=200, blank=True)
    story_text = models.TextField(blank=True)
    story_image = models.ImageField(upload_to=UploadTo("home"), blank=True)
    story_button_text = models.CharField(max_length=40, blank=True)
    story_button_url = models.CharField(max_length=300, blank=True)

    media_title = models.CharField(max_length=200, blank=True)
    news_eyebrow = models.CharField(max_length=80, blank=True)
    news_title = models.CharField(max_length=200, blank=True)
    testimonials_title = models.CharField(max_length=200, blank=True)
    partners_title = models.CharField(max_length=200, blank=True)
    partners_subtitle = models.TextField(blank=True)

    cta_title = models.CharField(max_length=200, blank=True)
    cta_text = models.TextField(blank=True)
    cta_image = models.ImageField(upload_to=UploadTo("home"), blank=True)
    cta_primary_text = models.CharField(max_length=40, blank=True)
    cta_primary_url = models.CharField(max_length=300, blank=True)
    cta_secondary_text = models.CharField(max_length=40, blank=True)
    cta_secondary_url = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Home page"

    def __str__(self):
        return "Home page"

    @property
    def intro_points_list(self):
        return [line.strip() for line in self.intro_points.splitlines() if line.strip()]


class AboutPage(OptimisedImagesMixin, Singleton):
    image_sizes = {"story_image": 1600, "approach_image": 1600}

    story_eyebrow = models.CharField(max_length=80, blank=True)
    story_title = models.CharField(max_length=200, blank=True)
    story_text = RichTextField(blank=True)
    story_image = models.ImageField(upload_to=UploadTo("about"), blank=True)
    story_quote = models.TextField(blank=True)

    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)

    objectives_title = models.CharField(max_length=200, blank=True)
    objectives_intro = models.TextField(blank=True)
    values_title = models.CharField(max_length=200, blank=True)
    values_intro = models.TextField(blank=True)

    approach_title = models.CharField(max_length=200, blank=True)
    approach_text = RichTextField(blank=True)
    approach_image = models.ImageField(upload_to=UploadTo("about"), blank=True)

    timeline_title = models.CharField(max_length=200, blank=True)
    legal_title = models.CharField(max_length=200, blank=True)
    legal_text = models.TextField(blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "About page"

    def __str__(self):
        return "About page"


class PageHeader(OptimisedImagesMixin, models.Model):
    """The banner at the top of each inner page."""

    image_sizes = {"image": 2200}
    PAGES = [
        ("about", "About"), ("focus", "Our Focus"), ("projects", "Projects"), ("impact", "Impact"),
        ("resources", "Reports & Resources"), ("media", "In the Media"), ("news", "News & Stories"),
        ("gallery", "Gallery"), ("team", "Our Team"), ("partners", "Partners"), ("sdgs", "SDGs"),
        ("involved", "Get Involved"), ("donate", "Donate"), ("contact", "Contact"), ("search", "Search"),
    ]

    page = models.CharField(max_length=20, choices=PAGES, unique=True)
    eyebrow = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=160)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to=UploadTo("headers"), blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["page"]
        verbose_name = "Page header"

    def __str__(self):
        return self.get_page_display()


# ==========================================================================
# About: objectives, values, milestones
# ==========================================================================


class Objective(Orderable):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="target")

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Objective"

    def __str__(self):
        return self.title


class CoreValue(Orderable):
    name = models.CharField(max_length=80)
    local_name = models.CharField("Swahili name", max_length=80, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="star")

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Core value"

    def __str__(self):
        return self.name


class Milestone(Orderable):
    year = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Timeline milestone"

    def __str__(self):
        return f"{self.year} — {self.title}"


# ==========================================================================
# Work: focus areas, projects, gallery
# ==========================================================================


class FocusArea(OptimisedImagesMixin, Orderable):
    image_sizes = {"image": 1600}

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="leaf")
    summary = models.TextField(help_text="One or two sentences shown on cards.")
    description = RichTextField(blank=True)
    image = models.ImageField(upload_to=UploadTo("focus"), blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Focus area"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:focus_detail", args=[self.slug])


class Project(OptimisedImagesMixin, Orderable):
    image_sizes = {"cover": 2000}
    STATUS = [("ongoing", "Ongoing"), ("completed", "Completed"), ("planned", "Planned")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    focus_area = models.ForeignKey(FocusArea, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    status = models.CharField(max_length=20, choices=STATUS, default="completed")
    summary = models.TextField(help_text="Short description for cards (1–3 sentences).")
    description = RichTextField(blank=True)
    cover = models.ImageField("Cover photo", upload_to=UploadTo("projects"), blank=True)
    location = models.CharField(max_length=200, blank=True)
    period = models.CharField(max_length=80, blank=True, help_text="e.g. 2025, or March 2026, or 2024 – 2026")
    beneficiaries = models.CharField("Target group", max_length=200, blank=True)
    partners = models.ManyToManyField("Partner", blank=True, related_name="projects")
    outcomes = models.TextField("Key results", blank=True, help_text="One result per line.")
    report = models.ForeignKey(
        "Resource", on_delete=models.SET_NULL, null=True, blank=True, related_name="projects",
        help_text="Optional report to download from the project page.",
    )
    is_featured = models.BooleanField("Show on home page", default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Project"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:project_detail", args=[self.slug])

    @property
    def outcomes_list(self):
        return [line.strip() for line in self.outcomes.splitlines() if line.strip()]


class ProjectStat(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stats")
    value = models.CharField(max_length=30, help_text="e.g. 3,700 or 8")
    label = models.CharField(max_length=120, help_text="e.g. Students reached")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Project figure"

    def __str__(self):
        return f"{self.value} {self.label}"


class GalleryImage(OptimisedImagesMixin, Orderable):
    image_sizes = {"image": 1800}

    image = models.ImageField(upload_to=UploadTo("gallery"))
    caption = models.CharField(max_length=250, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    album = models.CharField(
        max_length=80, blank=True, help_text="Used to group photos on the gallery page (defaults to the project name).",
    )

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Photo"

    def __str__(self):
        return self.caption or f"Photo {self.pk}"

    @property
    def album_name(self):
        return self.album or (self.project.title if self.project_id else "General")


# ==========================================================================
# Impact
# ==========================================================================


class ImpactStat(Orderable):
    value = models.PositiveIntegerField()
    prefix = models.CharField(max_length=5, blank=True)
    suffix = models.CharField(max_length=10, blank=True, help_text="e.g. + or %")
    label = models.CharField(max_length=120)
    description = models.CharField(max_length=250, blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="chart")
    show_on_home = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Impact figure"

    def __str__(self):
        return f"{self.prefix}{self.value:,}{self.suffix} {self.label}"


class SDG(Orderable):
    COLOURS = {
        1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21", 6: "#26BDE2",
        7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367", 11: "#FD9D24", 12: "#BF8B2E",
        13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B", 16: "#00689D", 17: "#19486A",
    }

    number = models.PositiveSmallIntegerField(choices=[(n, f"SDG {n}") for n in range(1, 18)])
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "SDG"
        verbose_name_plural = "SDGs"

    def __str__(self):
        return f"SDG {self.number}: {self.title}"

    @property
    def colour(self):
        return self.COLOURS.get(self.number, "#27963C")


# ==========================================================================
# People and partners
# ==========================================================================


class TeamMember(OptimisedImagesMixin, Orderable):
    image_sizes = {"photo": 900}
    GROUPS = [("founders", "Founders & Leadership"), ("board", "Board"), ("staff", "Team"), ("advisors", "Advisors")]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    role = models.CharField(max_length=150)
    group = models.CharField(max_length=20, choices=GROUPS, default="staff")
    photo = models.ImageField(upload_to=UploadTo("team"), blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Team member"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    @property
    def initials(self):
        return "".join(part[0] for part in self.name.split()[:2]).upper()


class Partner(OptimisedImagesMixin, Orderable):
    image_sizes = {"logo": 600}
    CATEGORIES = [
        ("funding", "Funding partner"), ("international", "International organisation"), ("government", "Government"),
        ("corporate", "Corporate partner"),
        ("ngo", "Civil society"), ("community", "Community partner"), ("media", "Media partner"),
    ]

    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to=UploadTo("partners"), blank=True)
    website = models.URLField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default="corporate")
    description = models.TextField(blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Partner"

    def __str__(self):
        return self.name

    @property
    def initials(self):
        words = [w for w in self.name.replace(".", " ").split() if w[:1].isalpha()]
        return "".join(w[0] for w in words[:3]).upper()


class Testimonial(OptimisedImagesMixin, Orderable):
    image_sizes = {"photo": 400}

    quote = models.TextField()
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to=UploadTo("testimonials"), blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="testimonials")

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Testimonial"

    def __str__(self):
        return f"{self.name}: {Truncator(self.quote).chars(50)}"


# ==========================================================================
# News, media coverage and documents
# ==========================================================================


class NewsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class NewsPost(OptimisedImagesMixin, models.Model):
    image_sizes = {"cover": 1800}
    CATEGORIES = [("news", "News"), ("story", "Impact story"), ("event", "Event"), ("announcement", "Announcement")]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default="news")
    excerpt = models.TextField(blank=True, help_text="Short summary for cards. Leave empty to use the start of the article.")
    body = RichTextField()
    cover = models.ImageField("Cover photo", upload_to=UploadTo("news"), blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="news")
    author = models.CharField(max_length=120, blank=True, default="WEMASA Communications")
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField("Published", default=True)
    is_featured = models.BooleanField("Featured", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-id"]
        verbose_name = "News post"

    objects = NewsQuerySet.as_manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:news_detail", args=[self.slug])

    @property
    def summary(self):
        return self.excerpt or Truncator(strip_tags(self.body)).words(32)

    @property
    def reading_minutes(self):
        return max(1, round(len(strip_tags(self.body).split()) / 220))


class MediaCoverage(OptimisedImagesMixin, Orderable):
    image_sizes = {"image": 1200}
    TYPES = [("newspaper", "Newspaper"), ("tv", "Television"), ("online", "Online"), ("radio", "Radio")]

    outlet = models.CharField(max_length=120)
    headline = models.CharField(max_length=250)
    media_type = models.CharField(max_length=20, choices=TYPES, default="online")
    url = models.URLField("Link to the story", max_length=500, blank=True)
    published_on = models.DateField(null=True, blank=True)
    reporter = models.CharField(max_length=120, blank=True)
    excerpt = models.TextField(blank=True)
    image = models.ImageField(upload_to=UploadTo("media"), blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-published_on", "id"]
        verbose_name = "Media coverage"
        verbose_name_plural = "Media coverage"

    def __str__(self):
        return f"{self.outlet}: {self.headline}"


class Resource(OptimisedImagesMixin, models.Model):
    image_sizes = {"cover": 900}
    CATEGORIES = [
        ("annual", "Annual report"), ("financial", "Financial report"), ("project", "Project report"),
        ("strategic", "Strategic plan"), ("research", "Research & publication"), ("policy", "Policy & governance"),
        ("other", "Other document"),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default="project")
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=UploadTo("documents"),
        validators=[FileExtensionValidator(["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "zip"])],
    )
    cover = models.ImageField("Cover image", upload_to=UploadTo("documents"), blank=True)
    published_on = models.DateField(default=timezone.localdate)
    is_published = models.BooleanField("Published", default=True)
    is_featured = models.BooleanField("Featured", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_on", "-id"]
        verbose_name = "Report / document"

    objects = PublishedQuerySet.as_manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    @property
    def extension(self):
        return self.file.name.rsplit(".", 1)[-1].upper() if self.file else ""


# ==========================================================================
# Giving and getting involved
# ==========================================================================


class DonationMethod(Orderable):
    KINDS = [("bank", "Bank transfer"), ("mobile", "Mobile money"), ("other", "Other")]

    kind = models.CharField(max_length=20, choices=KINDS, default="bank")
    title = models.CharField(max_length=120, help_text="e.g. CRDB Bank, M-Pesa, Airtel Money")
    account_name = models.CharField(max_length=150, blank=True)
    account_number = models.CharField("Account / till / phone number", max_length=80, blank=True)
    branch = models.CharField(max_length=120, blank=True)
    branch_code = models.CharField(max_length=30, blank=True)
    swift_code = models.CharField("SWIFT code", max_length=30, blank=True)
    currency = models.CharField(max_length=20, blank=True)
    instructions = models.TextField(blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Donation method"

    def __str__(self):
        return self.title


class InvolvementOption(Orderable):
    title = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="hand-heart")
    button_text = models.CharField(max_length=40, blank=True)
    button_url = models.CharField(max_length=300, blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "Way to get involved"

    def __str__(self):
        return self.title


class FAQ(Orderable):
    question = models.CharField(max_length=250)
    answer = models.TextField()

    objects = PublishedQuerySet.as_manager()

    class Meta(Orderable.Meta):
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


# ==========================================================================
# Inbox
# ==========================================================================


class ContactMessage(models.Model):
    TOPICS = [
        ("general", "General enquiry"), ("partnership", "Partnership"), ("volunteer", "Volunteering"),
        ("donation", "Donation"), ("media", "Media & press"), ("other", "Other"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    organisation = models.CharField(max_length=150, blank=True)
    topic = models.CharField(max_length=20, choices=TOPICS, default="general")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message"

    def __str__(self):
        return f"{self.name} — {self.get_topic_display()}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Newsletter subscriber"

    def __str__(self):
        return self.email
