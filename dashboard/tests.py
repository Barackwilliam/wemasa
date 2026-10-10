import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from website.models import ContactMessage, GalleryImage, HomePage, Project, Subscriber

from .registry import SECTIONS

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
TEST_CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(STORAGES=TEST_STORAGES, CACHES=TEST_CACHES, PAGE_CACHE_ENABLED=False)
class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", verbosity=0)
        User = get_user_model()
        cls.staff = User.objects.create_user("editor", email="editor@wemasa.org", password="Strong-pass-2026", is_staff=True)
        cls.visitor = User.objects.create_user("visitor", password="Strong-pass-2026")

    def setUp(self):
        self.client.force_login(self.staff)

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, reverse("dashboard:login") + "?next=/dashboard/")

    def test_non_staff_are_refused(self):
        self.client.force_login(self.visitor)
        self.assertEqual(self.client.get(reverse("dashboard:home")).status_code, 403)

    def test_login_with_email(self):
        self.client.logout()
        response = self.client.post(reverse("dashboard:login"), {"username": "editor@wemasa.org", "password": "Strong-pass-2026"})
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_every_section_list_and_form_renders(self):
        self.assertEqual(self.client.get(reverse("dashboard:home")).status_code, 200)
        for section in SECTIONS:
            with self.subTest(section=section.slug):
                if section.singleton:
                    self.assertEqual(self.client.get(reverse("dashboard:singleton", args=[section.slug])).status_code, 200)
                    continue
                self.assertEqual(self.client.get(reverse("dashboard:list", args=[section.slug]) + "?q=a").status_code, 200)
                if section.can_add:
                    self.assertEqual(self.client.get(reverse("dashboard:create", args=[section.slug])).status_code, 200)
                obj = section.model.objects.first()
                if obj and section.slug != "messages":
                    self.assertEqual(self.client.get(reverse("dashboard:update", args=[section.slug, obj.pk])).status_code, 200)

    def test_edit_home_page_updates_site(self):
        page = HomePage.load()
        url = reverse("dashboard:singleton", args=["home-page"])
        form = self.client.get(url).context["form"]
        data = {k: ("" if v is None else v) for k, v in form.initial.items() if not hasattr(v, "url")}
        data["hero_title"] = "A brand new headline"
        data = {k: v for k, v in data.items() if k in form.fields and not k.endswith("image") and not k.endswith("image_2")}
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        page.refresh_from_db()
        self.assertEqual(page.hero_title, "A brand new headline")
        self.assertContains(self.client.get("/"), "A brand new headline")

    def test_create_project_with_figures(self):
        response = self.client.post(reverse("dashboard:create", args=["projects"]), {
            "title": "Mangrove Restoration", "slug": "", "status": "planned", "summary": "Restoring mangroves.",
            "description": "<p>Details</p>", "location": "Kigamboni", "period": "2027", "beneficiaries": "Fishers",
            "outcomes": "", "is_featured": "on", "is_published": "on", "order": "1",
            "stats-TOTAL_FORMS": "1", "stats-INITIAL_FORMS": "0", "stats-MIN_NUM_FORMS": "0", "stats-MAX_NUM_FORMS": "1000",
            "stats-0-value": "500", "stats-0-label": "Mangroves planted", "stats-0-order": "0",
        })
        self.assertRedirects(response, reverse("dashboard:list", args=["projects"]))
        project = Project.objects.get(title="Mangrove Restoration")
        self.assertEqual(project.slug, "mangrove-restoration")
        self.assertEqual(project.stats.get().label, "Mangroves planted")

    def test_toggle_and_delete(self):
        project = Project.objects.first()
        self.client.post(reverse("dashboard:toggle", args=["projects", project.pk]))
        project.refresh_from_db()
        self.assertFalse(project.is_published)
        self.client.post(reverse("dashboard:delete", args=["projects", project.pk]))
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_bulk_photo_upload(self):
        def img(name):
            buf = io.BytesIO()
            Image.new("RGB", (800, 600), "green").save(buf, "PNG")
            return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")

        project = Project.objects.first()
        before = GalleryImage.objects.count()
        response = self.client.post(reverse("dashboard:bulk_upload"), {
            "photos": [img("a.png"), img("b.png")], "project": project.pk, "album": "", "caption": "Field day",
        })
        self.assertRedirects(response, reverse("dashboard:list", args=["gallery"]))
        self.assertEqual(GalleryImage.objects.count(), before + 2)
        self.assertEqual(project.photos.filter(caption="Field day").count(), 2)

    def test_messages_and_subscribers(self):
        msg = ContactMessage.objects.create(name="Juma", email="j@example.com", message="Hello")
        self.client.get(reverse("dashboard:message", args=[msg.pk]))
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)
        Subscriber.objects.create(email="reader@example.com")
        response = self.client.get(reverse("dashboard:export_subscribers"))
        self.assertIn(b"reader@example.com", response.content)
