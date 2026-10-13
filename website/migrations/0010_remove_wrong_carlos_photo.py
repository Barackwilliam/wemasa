import hashlib

from django.db import migrations

from website.cache import bump_content_version

# The photo first seeded for Carlos Mdemu is actually Frednand Nseso (confirmed by a captioned
# photo from WEMASA). Remove it until Carlos's own photo is supplied.
WRONG_PHOTO = "d8d102b28d8e979aedd57ceff5656d562de38c4197af10625a96c973aecf859b"


def remove_wrong_photo(apps, schema_editor):
    TeamMember = apps.get_model("website", "TeamMember")
    member = TeamMember.objects.filter(name="Carlos Mdemu").exclude(photo="").first()
    if not member:
        return
    try:
        with member.photo.open("rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != WRONG_PHOTO:
                return  # a photo uploaded through the dashboard: keep it
    except Exception:
        return
    member.photo = ""
    member.save(update_fields=["photo"])
    bump_content_version()


class Migration(migrations.Migration):
    dependencies = [("website", "0009_hd_hero_and_covers")]

    operations = [migrations.RunPython(remove_wrong_photo, migrations.RunPython.noop)]
