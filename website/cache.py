"""
Whole-page caching for the public website.

Every page is rendered once and then served from the cache. Any change saved
in the dashboard bumps a "content version" number, which makes every cached
page stale at once, so visitors always see the latest content.

Cached pages are also tied to the deploy's static files: each deploy gives the
stylesheet and scripts new hashed names, so a page cached by an earlier deploy
would point at files that no longer exist and show up unstyled.
"""
import hashlib
from functools import wraps
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

VERSION_KEY = "wemasa:content-version"


def _static_build():
    """A fingerprint of this deploy's collected static files (changes whenever a CSS/JS file does)."""
    try:
        manifest = Path(settings.STATIC_ROOT) / "staticfiles.json"
        return hashlib.md5(manifest.read_bytes()).hexdigest()[:10]
    except (OSError, TypeError):
        return "dev"


STATIC_BUILD = _static_build()


def content_version():
    version = cache.get(VERSION_KEY)
    if version is None:
        version = 1
        cache.set(VERSION_KEY, version, None)
    return version


def bump_content_version(**kwargs):
    try:
        cache.incr(VERSION_KEY)
    except ValueError:
        cache.set(VERSION_KEY, 2, None)


def cached_page(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if (
            not settings.PAGE_CACHE_ENABLED
            or request.method != "GET"
            or request.user.is_authenticated
        ):
            return view(request, *args, **kwargs)
        digest = hashlib.md5(request.get_full_path().encode()).hexdigest()
        key = f"wemasa:page:{STATIC_BUILD}:{content_version()}:{digest}"
        cached = cache.get(key)
        if cached is not None:
            content, content_type = cached
            response = HttpResponse(content, content_type=content_type)
            response["X-Page-Cache"] = "hit"
            return response
        response = view(request, *args, **kwargs)
        if hasattr(response, "render") and callable(response.render):
            response = response.render()
        if response.status_code == 200 and not response.streaming:
            cache.set(key, (response.content, response["Content-Type"]))
            response["X-Page-Cache"] = "miss"
        return response

    return wrapper
