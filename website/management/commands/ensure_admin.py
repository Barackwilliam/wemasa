import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the first dashboard administrator from ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD (only if missing)."

    def handle(self, *args, **options):
        email = os.getenv("ADMIN_EMAIL", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "")
        username = os.getenv("ADMIN_USERNAME", "admin").strip() or "admin"
        if not password:
            self.stdout.write("ADMIN_PASSWORD not set — skipping administrator creation.")
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Administrator '{username}' already exists.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created administrator '{username}'."))
