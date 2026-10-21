from django.db import migrations

from website.management.commands.seed_content import HERO_DIR, HERO_PHOTOS, photo, upload


def load(apps, schema_editor):
    # The live site does not always run seed_content on deploy, so the photos are added here, once.
    HeroPhoto = apps.get_model("website", "HeroPhoto")
    for order, (caption, image) in enumerate(HERO_PHOTOS):
        if HeroPhoto.objects.filter(caption=caption).exists():
            continue
        f = photo(image, HERO_DIR)
        if not f:
            continue
        hp = HeroPhoto(caption=caption, order=order)
        if upload(hp.image, f):
            hp.save()


class Migration(migrations.Migration):
    dependencies = [("website", "0017_hero_photos")]

    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
