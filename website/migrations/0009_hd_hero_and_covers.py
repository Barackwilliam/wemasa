import hashlib

from django.db import migrations

from website.cache import bump_content_version
from website.management.commands.seed_content import LEAD_PROJECTS, photo, upload

# (project title, new cover, SHA-256 of the cover seed_content first stored)
COVERS = [
    ("World Cleanup Day 2026: Mbezi Beach Cleanup", "cover-world-cleanup-day-hd.webp", "a16b37143364408295b4b08517798369102d61a445431b0d0fd42a9e00ad54d4"),
    ("Waste and Brand Audits (WABA)", "cover-waba-hd.webp", "b5ea310bbda014584e643e0eb82bc1c780d314f8ebd1da79ead4f1a28df6300b"),
    ("Beach & Community Cleanups", "cover-beach-cleanup-hd.webp", "0b53a4319ae643461981b3c4b6e58e38670219164a824c5171b5050f340d9837"),
]
HERO = ("hero-hd.webp", "2c075e3c4565a90ef71615e99c587dae4725c5d09ddcfb56bfa79759234ebbf4")


def _sha(field_file):
    try:
        with field_file.open("rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def _replace(obj, field, filename, old_hash):
    """Swap in an HD photo, only where the stored one is still the photo seed_content put there."""
    current = getattr(obj, field)
    if not current or _sha(current) != old_hash:
        return
    f = photo(filename)
    if f and upload(current, f):
        obj.save(update_fields=[field])


def hd_hero_and_covers(apps, schema_editor):
    # The first home page photos were WhatsApp copies about 1080px wide, stretched across the
    # full screen. These come from the 2560px originals.
    HomePage = apps.get_model("website", "HomePage")
    Project = apps.get_model("website", "Project")
    home = HomePage.objects.filter(pk=1).first()
    if home:
        _replace(home, "hero_image", *HERO)
    for title, filename, old_hash in COVERS:
        project = Project.objects.filter(title=title).first()
        if project:
            _replace(project, "cover", filename, old_hash)
    # The home page slider shows the first three projects: put the latest work, with HD covers, first.
    lead = [p for t in LEAD_PROJECTS for p in Project.objects.filter(title=t)]
    if lead:
        rest = Project.objects.exclude(pk__in=[p.pk for p in lead]).order_by("order", "id")
        for order, project in enumerate(lead + list(rest)):
            if project.order != order:
                project.order = order
                project.save(update_fields=["order"])
    # Changes made here bypass the dashboard's save signals, so refresh the page cache explicitly.
    bump_content_version()


class Migration(migrations.Migration):
    dependencies = [("website", "0008_tidy_partner_logos")]

    operations = [migrations.RunPython(hd_hero_and_covers, migrations.RunPython.noop)]
