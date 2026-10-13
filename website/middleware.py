from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Send every visitor (and Google) to one address, e.g. https://www.wemasatanzania.org.

    Without this the same pages are reachable on wemasa.onrender.com and on the bare domain,
    and search engines treat them as duplicate copies. Set CANONICAL_HOST (e.g. www.wemasatanzania.org)
    to turn it on; it does nothing when CANONICAL_HOST is empty or in DEBUG.
    """

    EXEMPT_PATHS = ("/health/",)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = settings.CANONICAL_HOST
        if host and not settings.DEBUG and not request.path.startswith(self.EXEMPT_PATHS):
            if request.get_host().lower() != host:
                return HttpResponsePermanentRedirect(f"https://{host}{request.get_full_path()}")
        return self.get_response(request)
