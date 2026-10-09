import io
import os
import uuid

import nh3
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image, ImageOps

# --------------------------------------------------------------------------
# Upload paths
# --------------------------------------------------------------------------


class UploadTo:
    """Store every upload under `<folder>/<yyyy>/<random>.<ext>` so names never clash."""

    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        from django.utils import timezone

        ext = os.path.splitext(filename)[1].lower() or ".bin"
        return f"{self.folder}/{timezone.now():%Y}/{uuid.uuid4().hex[:16]}{ext}"

    def deconstruct(self):
        return ("website.utils.UploadTo", (self.folder,), {})


# --------------------------------------------------------------------------
# Image optimisation: every uploaded photo is resized and converted to WebP
# --------------------------------------------------------------------------

def optimise_image(field_file, max_size=1920, quality=82):
    """Resize a freshly uploaded image and re-encode it as WebP (in place, not yet saved)."""
    if not field_file or getattr(field_file, "_committed", True):
        return
    name = os.path.basename(field_file.name)
    if name.lower().endswith(".svg"):
        return
    try:
        field_file.file.seek(0)
        image = Image.open(field_file.file)
        source_format = image.format
        image = ImageOps.exif_transpose(image)
    except Exception:  # not an image Pillow understands: keep the original
        return
    if source_format == "WEBP" and max(image.size) <= max_size:
        field_file.file.seek(0)
        return  # already optimised
    has_alpha = image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
    image = image.convert("RGBA" if has_alpha else "RGB")
    image.thumbnail((max_size, max_size), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, "WEBP", quality=quality, method=5)
    new_name = f"{os.path.splitext(name)[0]}.webp"
    field_file.save(new_name, ContentFile(buffer.getvalue()), save=False)


class OptimisedImagesMixin:
    """Models list `image_sizes = {"field_name": max_px}` and get WebP conversion on save."""

    image_sizes = {}

    def save(self, *args, **kwargs):
        for field_name, max_size in self.image_sizes.items():
            optimise_image(getattr(self, field_name), max_size)
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------
# Rich text
# --------------------------------------------------------------------------

ALLOWED_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "s", "a", "ul", "ol", "li", "blockquote",
    "h2", "h3", "h4", "div", "span", "pre", "code", "hr", "figure", "figcaption", "del",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title", "target"}}


def clean_html(value):
    if not value:
        return ""
    return nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
        url_schemes={"http", "https", "mailto", "tel"},
    )


def unique_slug(instance, value, field="slug", max_length=200):
    """Return a slug for `value` that no other row of the same model uses."""
    base = slugify(value)[: max_length - 6] or "item"
    slug, n = base, 2
    model = type(instance)
    while model.objects.filter(**{field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug
