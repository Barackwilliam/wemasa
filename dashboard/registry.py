"""
What the dashboard can edit, and how each section looks.

Every entry describes one content type: its menu label and icon, which columns
show in the list, which fields can be searched, and how the edit form is
grouped. Adding a new content type to the dashboard is one entry here.
"""
from dataclasses import dataclass, field

from website import models as m


@dataclass
class Section:
    slug: str
    model: type
    label: str
    icon: str
    group: str
    singular: str = ""
    help: str = ""
    singleton: bool = False
    list_display: list = field(default_factory=list)
    search_fields: list = field(default_factory=list)
    filter_field: str = ""
    thumb: str = ""
    fieldsets: list = field(default_factory=list)
    exclude: list = field(default_factory=list)
    inlines: list = field(default_factory=list)
    can_add: bool = True
    view_url: str = ""

    @property
    def name(self):
        return self.singular or self.model._meta.verbose_name.title()


SECTIONS = [
    # ------------------------------------------------------------------ Pages
    Section(
        "site-settings", m.SiteSettings, "Site settings", "home", "Website", singleton=True,
        help="Organisation details, contacts, social media and search-engine text used across the whole website.",
        fieldsets=[
            ("Organisation", ["org_name", "short_name", "tagline", "logo", "footer_about"]),
            ("Registration", ["registration_number", "registration_year", "registration_note"]),
            ("Contact details", ["email", "phone", "phone_alt", "whatsapp", "location", "address", "office_hours", "map_embed_url"]),
            ("Social media", ["facebook", "instagram", "threads", "x_twitter", "linkedin", "youtube", "tiktok"]),
            ("Announcement bar", ["announcement", "announcement_link"]),
            ("Buttons & newsletter", ["donate_button_text", "newsletter_title", "newsletter_text"]),
            ("Search engines & sharing", ["meta_description", "og_image", "google_site_verification"]),
        ],
    ),
    Section(
        "home-page", m.HomePage, "Home page", "star", "Website", singleton=True, view_url="/",
        help="Every heading, paragraph, button and image on the home page.",
        fieldsets=[
            ("Hero banner", ["hero_eyebrow", "hero_title", "hero_highlight", "hero_subtitle", "hero_image",
                             "hero_primary_text", "hero_primary_url", "hero_secondary_text", "hero_secondary_url"]),
            ("Who we are", ["intro_eyebrow", "intro_title", "intro_text", "intro_points", "intro_image", "intro_image_2",
                            "intro_badge_value", "intro_badge_label"]),
            ("Focus areas section", ["focus_eyebrow", "focus_title", "focus_subtitle"]),
            ("Impact section", ["impact_eyebrow", "impact_title", "impact_subtitle"]),
            ("Projects section", ["projects_eyebrow", "projects_title", "projects_subtitle"]),
            ("Our story band", ["story_eyebrow", "story_title", "story_text", "story_image", "story_button_text", "story_button_url"]),
            ("Other section titles", ["media_title", "news_eyebrow", "news_title", "testimonials_title", "partners_title", "partners_subtitle"]),
            ("Closing call to action", ["cta_title", "cta_text", "cta_image", "cta_primary_text", "cta_primary_url",
                                        "cta_secondary_text", "cta_secondary_url"]),
        ],
    ),
    Section(
        "about-page", m.AboutPage, "About page", "leaf", "Website", singleton=True, view_url="/about/",
        help="Your story, vision, mission and the introductions to each About section.",
        fieldsets=[
            ("Our story", ["story_eyebrow", "story_title", "story_text", "story_image", "story_quote"]),
            ("Vision & mission", ["vision", "mission"]),
            ("Section introductions", ["objectives_title", "objectives_intro", "values_title", "values_intro", "timeline_title"]),
            ("How we work", ["approach_title", "approach_text", "approach_image"]),
            ("Registration & governance", ["legal_title", "legal_text"]),
        ],
    ),
    Section(
        "page-headers", m.PageHeader, "Page banners", "image", "Website", singular="Page banner",
        help="The title, introduction and background photo at the top of each inner page.",
        list_display=["page", "title"], search_fields=["title", "subtitle"], thumb="image",
    ),
    # --------------------------------------------------------------- Our work
    Section(
        "focus-areas", m.FocusArea, "Focus areas", "target", "Our work",
        list_display=["title", "order", "is_published"], search_fields=["title", "summary"], thumb="image",
    ),
    Section(
        "projects", m.Project, "Projects", "layers", "Our work",
        list_display=["title", "focus_area", "status", "location", "is_featured", "is_published"],
        search_fields=["title", "summary", "location"], filter_field="status", thumb="cover",
        fieldsets=[
            ("Project", ["title", "slug", "focus_area", "status", "summary", "description", "cover"]),
            ("Details", ["location", "period", "beneficiaries", "partners", "outcomes", "report"]),
            ("Display", ["is_featured", "is_published", "order"]),
        ],
        inlines=["stats"],
    ),
    Section(
        "gallery", m.GalleryImage, "Photo gallery", "camera", "Our work", singular="Photo",
        list_display=["caption", "project", "album", "is_published"], search_fields=["caption", "album"],
        filter_field="project", thumb="image",
    ),
    Section(
        "videos", m.Video, "Videos", "play", "Our work", singular="Video",
        help="Paste a YouTube link (best for long videos), or upload a short MP4 of up to 50 MB.",
        list_display=["title", "project", "is_featured", "order", "is_published"], search_fields=["title", "description"],
        filter_field="project", thumb="poster",
        fieldsets=[
            ("Video", ["title", "youtube_url", "video_file", "poster"]),
            ("Details", ["description", "project", "recorded_on"]),
            ("Display", ["is_featured", "is_published", "order"]),
        ],
    ),
    Section(
        "impact", m.ImpactStat, "Impact figures", "chart", "Our work", singular="Impact figure",
        list_display=["label", "value", "suffix", "show_on_home", "order", "is_published"], search_fields=["label"],
    ),
    Section("milestones", m.Milestone, "Timeline", "calendar", "Our work", singular="Milestone",
            list_display=["year", "title", "order", "is_published"], search_fields=["title", "year"]),
    Section("sdgs", m.SDG, "SDGs", "globe", "Our work", singular="SDG",
            list_display=["number", "title", "order", "is_published"], search_fields=["title"]),
    # ----------------------------------------------------------- Organisation
    Section(
        "team", m.TeamMember, "Team", "users", "Organisation", singular="Team member",
        list_display=["name", "role", "group", "order", "is_published"], search_fields=["name", "role"],
        filter_field="group", thumb="photo",
    ),
    Section(
        "partners", m.Partner, "Partners", "handshake", "Organisation",
        list_display=["name", "category", "order", "is_published"], search_fields=["name"],
        filter_field="category", thumb="logo",
    ),
    Section("values", m.CoreValue, "Core values", "heart", "Organisation", singular="Core value",
            list_display=["name", "local_name", "order", "is_published"], search_fields=["name"]),
    Section("objectives", m.Objective, "Objectives", "clipboard", "Organisation",
            list_display=["title", "order", "is_published"], search_fields=["title"]),
    Section("testimonials", m.Testimonial, "Testimonials", "quote", "Organisation",
            list_display=["name", "role", "project", "is_published"], search_fields=["name", "quote"], thumb="photo"),
    # ----------------------------------------------------------- Publications
    Section(
        "news", m.NewsPost, "News & stories", "newspaper", "Publications", singular="Article",
        list_display=["title", "category", "published_at", "is_featured", "is_published"],
        search_fields=["title", "body"], filter_field="category", thumb="cover",
        fieldsets=[
            ("Article", ["title", "slug", "category", "excerpt", "body", "cover"]),
            ("Publishing", ["author", "project", "published_at", "is_featured", "is_published"]),
        ],
    ),
    Section(
        "media", m.MediaCoverage, "Media coverage", "mic", "Publications", singular="Media item",
        list_display=["outlet", "headline", "media_type", "published_on", "is_published"],
        search_fields=["outlet", "headline"], filter_field="media_type", thumb="image",
    ),
    Section(
        "resources", m.Resource, "Reports & documents", "file", "Publications", singular="Document",
        list_display=["title", "category", "published_on", "is_published"], search_fields=["title", "description"],
        filter_field="category", thumb="cover",
    ),
    # ------------------------------------------------------------- Engagement
    Section("donation-methods", m.DonationMethod, "Donation methods", "wallet", "Engagement", singular="Donation method",
            list_display=["title", "kind", "account_number", "is_published"], search_fields=["title", "account_number"]),
    Section("involvement", m.InvolvementOption, "Ways to get involved", "hand-heart", "Engagement", singular="Option",
            list_display=["title", "order", "is_published"], search_fields=["title"]),
    Section("faqs", m.FAQ, "FAQs", "lightbulb", "Engagement", singular="FAQ",
            list_display=["question", "order", "is_published"], search_fields=["question", "answer"]),
    # ------------------------------------------------------------------ Inbox
    Section("messages", m.ContactMessage, "Messages", "mail", "Inbox", singular="Message", can_add=False,
            list_display=["name", "email", "topic", "created_at", "is_read"], search_fields=["name", "email", "message"],
            filter_field="topic"),
    Section("subscribers", m.Subscriber, "Subscribers", "send", "Inbox", singular="Subscriber",
            list_display=["email", "is_active", "created_at"], search_fields=["email"]),
]

BY_SLUG = {s.slug: s for s in SECTIONS}


def grouped():
    groups = {}
    for s in SECTIONS:
        groups.setdefault(s.group, []).append(s)
    return groups.items()
