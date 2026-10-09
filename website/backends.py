from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Dashboard users can sign in with their username or their email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username and "@" in username:
            user = get_user_model().objects.filter(email__iexact=username.strip()).first()
            if user:
                username = user.get_username()
        return super().authenticate(request, username=username, password=password, **kwargs)
