import io

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import ContactMessage, FocusArea, GalleryImage, NewsPost, Project, SiteSettings, Subscriber

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
TEST_CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


def jpeg_upload(name="photo.jpg", size=(2600, 1400)):
    buf = io.BytesIO()
    Image.new("RGB", size, (39, 150, 60)).save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


@override_settings(STORAGES=TEST_STORAGES, CACHES=TEST_CACHES, PAGE_CACHE_ENABLED=False)
class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", verbosity=0)

    def test_every_public_page_renders(self):
        project = Project.objects.first()
        area = FocusArea.objects.first()
        post = NewsPost.objects.first()
        urls = [
            reverse("website:home"), reverse("website:about"), reverse("website:focus_list"),
            area.get_absolute_url(), reverse("website:project_list"), project.get_absolute_url(),
            reverse("website:impact"), reverse("website:sdgs"), reverse("website:resources"),
            reverse("website:media"), reverse("website:news_list"), post.get_absolute_url(),
            reverse("website:gallery"), reverse("website:team"), reverse("website:partners"),
            reverse("website:get_involved"), reverse("website:donate"), reverse("website:contact"),
            reverse("website:search") + "?q=school", reverse("website:robots"), reverse("sitemap"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_seeded_content_appears_on_home_page(self):
        html = self.client.get(reverse("website:home")).content.decode()
        self.assertIn("WEMASA", html)
        self.assertIn("ooNGO/R/2395", html)
        self.assertIn("Students reached", html)

    def test_seed_is_idempotent(self):
        before = Project.objects.count(), GalleryImage.objects.count()
        call_command("seed_content", verbosity=0)
        self.assertEqual(before, (Project.objects.count(), GalleryImage.objects.count()))

    def test_project_filters(self):
        response = self.client.get(reverse("website:project_list") + "?status=ongoing")
        self.assertContains(response, "School Tree Planting Programme")
        self.assertNotContains(response, "Food Vendors Cooking Energy Mapping")

    def test_unpublished_items_are_hidden(self):
        project = Project.objects.get(title__startswith="Food Vendors")
        project.is_published = False
        project.save()
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.assertNotContains(self.client.get(reverse("website:project_list")), project.title)

    def test_unknown_page_returns_404(self):
        self.assertEqual(self.client.get("/does-not-exist/").status_code, 404)


@override_settings(STORAGES=TEST_STORAGES, CACHES=TEST_CACHES, PAGE_CACHE_ENABLED=False)
class FormsTests(TestCase):
    def setUp(self):
        cache.clear()  # rate-limit counters live in the cache

    def test_contact_form_saves_message(self):
        response = self.client.post(reverse("website:contact"), {
            "name": "Asha", "email": "asha@example.com", "topic": "partnership", "message": "Let us work together.",
        })
        self.assertRedirects(response, reverse("website:contact") + "?sent=1#message", fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.get().name, "Asha")

    def test_contact_honeypot_drops_spam(self):
        self.client.post(reverse("website:contact"), {
            "name": "Bot", "email": "bot@example.com", "topic": "general", "message": "spam", "website": "http://spam",
        })
        self.assertFalse(ContactMessage.objects.exists())

    def test_contact_form_shows_errors(self):
        response = self.client.post(reverse("website:contact"), {"name": "", "email": "nope", "message": ""})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ContactMessage.objects.exists())

    def test_contact_rate_limit(self):
        data = {"name": "A", "email": "a@example.com", "topic": "general", "message": "Hi"}
        for _ in range(5):
            self.client.post(reverse("website:contact"), data)
        response = self.client.post(reverse("website:contact"), data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ContactMessage.objects.count(), 5)

    def test_subscribe(self):
        response = self.client.post(reverse("website:subscribe"), {"email": "Reader@Example.com", "next": "/about/"})
        self.assertRedirects(response, "/about/?subscribed=ok#newsletter", fetch_redirect_response=False)
        self.assertTrue(Subscriber.objects.filter(email="reader@example.com").exists())

    def test_subscribe_ajax_and_open_redirect(self):
        response = self.client.post(reverse("website:subscribe"), {"email": "x@example.com"}, HTTP_X_REQUESTED_WITH="fetch")
        self.assertEqual(response.content, b"ok")
        response = self.client.post(reverse("website:subscribe"), {"email": "y@example.com", "next": "//evil.com"})
        self.assertTrue(response["Location"].startswith("/?subscribed"))


@override_settings(STORAGES=TEST_STORAGES, CACHES=TEST_CACHES, PAGE_CACHE_ENABLED=True)
class PageCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        SiteSettings.objects.create(pk=1, org_name="WEMASA", tagline="Original tagline")

    def test_pages_are_cached_and_refreshed_after_edits(self):
        url = reverse("website:about")
        self.client.get(url)  # the first visit creates the About page singleton, which itself refreshes the cache
        cache.clear()
        first = self.client.get(url)
        self.assertEqual(first["X-Page-Cache"], "miss")
        self.assertEqual(self.client.get(url)["X-Page-Cache"], "hit")
        settings_obj = SiteSettings.load()
        settings_obj.footer_about = "Fresh footer text"
        settings_obj.save()
        refreshed = self.client.get(url)
        self.assertEqual(refreshed["X-Page-Cache"], "miss")
        self.assertContains(refreshed, "Fresh footer text")

    def test_logged_in_staff_bypass_cache(self):
        user = get_user_model().objects.create_user("staff", password="x-Strong-pass-1", is_staff=True)
        self.client.force_login(user)
        self.assertNotIn("X-Page-Cache", self.client.get(reverse("website:about")))


@override_settings(STORAGES=TEST_STORAGES, CACHES=TEST_CACHES)
class ImageOptimisationTests(TestCase):
    def test_uploads_are_resized_and_converted_to_webp(self):
        photo = GalleryImage.objects.create(image=jpeg_upload())
        self.assertTrue(photo.image.name.endswith(".webp"))
        with photo.image.open("rb") as fh:
            image = Image.open(fh)
            self.assertEqual(image.format, "WEBP")
            self.assertLessEqual(max(image.size), 1800)

    def test_rich_text_is_sanitised(self):
        post = NewsPost.objects.create(title="Safe", body='<p onclick="x()">Hi<script>alert(1)</script></p>')
        self.assertNotIn("script", post.body)
        self.assertNotIn("onclick", post.body)
        self.assertTrue(post.slug)
