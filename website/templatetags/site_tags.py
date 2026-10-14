import hashlib
from urllib.parse import urlencode

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()

SOCIAL_ICONS = {"x": "x-logo"}
_asset_versions = {}


@register.simple_tag
def asset(path):
    """Static URL ending in a fingerprint of the file, so browsers fetch a changed CSS or JS file at once.

    Static files are cached by browsers for 30 days; without DEBUG=False (hashed file names) a
    changed stylesheet would otherwise keep its old URL and visitors would keep the old version.
    """
    if path not in _asset_versions:
        found = finders.find(path)
        try:
            with open(found, "rb") as f:
                _asset_versions[path] = hashlib.md5(f.read()).hexdigest()[:10]
        except (OSError, TypeError):
            _asset_versions[path] = ""
    url = static(path)
    return f"{url}?v={_asset_versions[path]}" if _asset_versions[path] else url


@register.simple_tag
def icon(name, size=None, cls=""):
    name = SOCIAL_ICONS.get(name, name) or "leaf"
    style = f' style="width:{int(size)}px;height:{int(size)}px"' if size else ""
    return mark_safe(f'<svg class="icon {escape(cls)}"{style} aria-hidden="true"><use href="#i-{escape(name)}"/></svg>')


@register.filter
def highlight(title, phrase):
    """Wrap `phrase` inside `title` with an accent span."""
    title = escape(title or "")
    phrase = escape(phrase or "")
    if phrase and phrase in title:
        return mark_safe(title.replace(phrase, f'<span class="accent">{phrase}</span>', 1))
    return mark_safe(title)


@register.filter
def img_url(field, fallback=""):
    """URL of an uploaded image, or a static fallback image when empty."""
    try:
        if field and field.name:
            return field.url
    except ValueError:
        pass
    return static(fallback) if fallback else ""


@register.simple_tag(takes_context=True)
def query(context, **kwargs):
    """Build a query string keeping current GET params, overriding the ones given."""
    params = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            params.pop(key, None)
        else:
            params[key] = value
    if "page" not in kwargs:  # changing a filter always goes back to page 1
        params.pop("page", None)
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "?"


@register.filter
def split_lines(value):
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


@register.filter
def whatsapp_link(number):
    digits = "".join(ch for ch in (number or "") if ch.isdigit())
    if digits.startswith("0"):
        digits = "255" + digits[1:]
    return f"https://wa.me/{digits}" if digits else ""


@register.filter
def tel_link(number):
    cleaned = "".join(ch for ch in (number or "") if ch.isdigit() or ch == "+")
    return f"tel:{cleaned}"


@register.simple_tag
def share_links(url, title):
    data = {
        "WhatsApp": ("whatsapp", f"https://wa.me/?{urlencode({'text': f'{title} {url}'})}"),
        "Facebook": ("facebook", f"https://www.facebook.com/sharer/sharer.php?{urlencode({'u': url})}"),
        "X": ("x", f"https://twitter.com/intent/tweet?{urlencode({'url': url, 'text': title})}"),
        "LinkedIn": ("linkedin", f"https://www.linkedin.com/sharing/share-offsite/?{urlencode({'url': url})}"),
        "Threads": ("threads", f"https://www.threads.net/intent/post?{urlencode({'text': f'{title} {url}'})}"),
    }
    links = [{"name": k, "icon": v[0], "url": v[1]} for k, v in data.items()]
    # Instagram has no web share link: the button opens the phone's share sheet (which lists Instagram),
    # or copies the link on a computer so it can be pasted into Instagram.
    links.append({"name": "Instagram", "icon": "instagram", "url": url, "native": True, "title": title})
    return links


@register.inclusion_tag("partials/section_head.html")
def section_head(eyebrow="", title="", subtitle="", align="center", light=False):
    return {"eyebrow": eyebrow, "title": title, "subtitle": subtitle, "align": align, "light": light}


@register.simple_tag
def first_of(*values):
    for value in values:
        if value:
            return value
    return ""


@register.filter
def initials(value):
    return "".join(part[0] for part in str(value).split()[:2]).upper()


@register.simple_tag
def bg_image(field, fallback=""):
    url = img_url(field, fallback)
    return format_html('style="--bg:url(\'{}\')"', url) if url else ""


ACCENTS = ["#27963C", "#0096D6", "#E58A12", "#7B4FC2", "#D9483B", "#13867A"]


@register.filter
def accent(index):
    """A colour for each focus area, so cards and links can be colour-coded."""
    try:
        return ACCENTS[int(index) % len(ACCENTS)]
    except (TypeError, ValueError):
        return ACCENTS[0]
