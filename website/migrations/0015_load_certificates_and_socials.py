from django.db import migrations

from website.management.commands.seed_content import CERT_DIR, CERTIFICATES, DONATION_METHODS, SITE, photo, upload

SOCIAL_FIELDS = ("facebook", "instagram", "threads", "x_twitter", "linkedin", "tiktok")


def load(apps, schema_editor):
    # The live site does not always run seed_content on deploy, so content that must reach it
    # is added here, once, and only where it is missing.
    Certificate = apps.get_model("website", "Certificate")
    for order, (title, issuer, kind, issued, text, image) in enumerate(CERTIFICATES):
        if Certificate.objects.filter(title=title).exists():
            continue
        f = photo(image, CERT_DIR)
        if not f:
            continue
        cert = Certificate(title=title, issuer=issuer, kind=kind, issued_on=issued, description=text, order=order)
        if upload(cert.image, f):
            cert.save()

    SiteSettings = apps.get_model("website", "SiteSettings")
    site = SiteSettings.objects.filter(pk=1).first()
    if site:
        changed = [f for f in SOCIAL_FIELDS if not getattr(site, f) and SITE.get(f)]
        for f in changed:
            setattr(site, f, SITE[f])
        if changed:
            site.save(update_fields=changed)

    DonationMethod = apps.get_model("website", "DonationMethod")
    if not DonationMethod.objects.filter(kind="bank").exists():
        for order, (k, t, n, no, b, bc, sw, c, i) in enumerate(DONATION_METHODS):
            DonationMethod.objects.create(kind=k, title=t, account_name=n, account_number=no, branch=b, branch_code=bc,
                                          swift_code=sw, currency=c, instructions=i, order=order)
    else:
        # A bank account that exists but was hidden would leave the Donate page without bank details.
        DonationMethod.objects.filter(kind="bank", title="Equity Bank", is_published=False).update(is_published=True)


class Migration(migrations.Migration):
    dependencies = [("website", "0014_certificates")]

    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
