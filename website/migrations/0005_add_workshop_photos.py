from django.db import migrations
from django.db.models import Max

from website.management.commands.seed_content import WORKSHOP_PHOTOS, photo, upload

PROJECT = "1st Workshop for Young Girls and Women Environment Journalists"
ALBUM = "Women journalists workshop"


def add_workshop_photos(apps, schema_editor):
    # seed_content only adds photos to projects it creates, so sites that already have the
    # workshop project get its new photos here, once. New sites get them from seed_content.
    Project = apps.get_model("website", "Project")
    GalleryImage = apps.get_model("website", "GalleryImage")
    project = Project.objects.filter(title=PROJECT).first()
    if not project:
        return
    order = (GalleryImage.objects.filter(project=project).aggregate(Max("order"))["order__max"] or 0) + 1
    for i, (name, caption) in enumerate(WORKSHOP_PHOTOS):
        f = photo(name)
        if not f:
            continue
        img = GalleryImage(project=project, album=ALBUM, caption=caption, order=order + i)
        if upload(img.image, f):
            img.save()


class Migration(migrations.Migration):
    dependencies = [("website", "0004_create_cache_table")]

    operations = [migrations.RunPython(add_workshop_photos, migrations.RunPython.noop)]
