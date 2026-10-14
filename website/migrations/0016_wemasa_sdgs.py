from django.db import migrations

from website.management.commands.seed_content import SDGS


def set_goals(apps, schema_editor):
    # WEMASA's goals (October 2026): 1, 2, 3, 4, 5, 7, 11, 13, 14, 15 and 17.
    # Goals on the list are added if missing and published, in number order; any other goal is hidden
    # (not deleted, so its text is kept if WEMASA brings it back).
    SDG = apps.get_model("website", "SDG")
    wanted = {number: (title, desc) for number, title, desc in SDGS}
    for order, number in enumerate(sorted(wanted)):
        title, desc = wanted[number]
        goal = SDG.objects.filter(number=number).first()
        if goal is None:
            SDG.objects.create(number=number, title=title, description=desc, order=order, is_published=True)
        else:
            goal.order, goal.is_published = order, True
            goal.save(update_fields=["order", "is_published"])
    SDG.objects.exclude(number__in=wanted).update(is_published=False)


class Migration(migrations.Migration):
    dependencies = [("website", "0015_load_certificates_and_socials")]
    operations = [migrations.RunPython(set_goals, migrations.RunPython.noop)]
