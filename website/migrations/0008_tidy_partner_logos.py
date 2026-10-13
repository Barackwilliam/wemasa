import hashlib

from django.db import migrations

from website.management.commands.seed_content import photo, upload

# (partner, new logo in seed/images/partners/, SHA-256 of every earlier seed version of that logo)
LOGOS = [
    ('Global Fund for Women', "global-fund-for-women.png", {
        "11d4565b1fd42799c78b99b51476e81dee65710e335d29d97c55c6cee5f3875b",
        "5f3c1cc5d7d637f6382d9461921d7c587caefd87da7f914f86753370165f3433",
    }),
    ('Lake Group', "lake-group.png", {
        "1057ecab6d14e679e74bdbb677e7189106609ad82156c5b28af745b59e7473bb",
    }),
    ('Mazingira Konekti', "mazingira-konekti.png", {
        "4eba22d2407c352aa1b26ac60da38e2e6dc6de63a2dfb8d400196e418ee350ef",
    }),
    ('Nabaki Afrika', "nabaki-afrika.png", {
        "fa677e553ad148e7afc7a1533285e10cdc73fe0e90e7195fb21c30ecf34b8aa3",
    }),
    ('National Environment Management Council (NEMC)', "nemc.png", {
        "0f7529805ada4a90ed8f84229d5a268449a8cc4f0d608b0bbdade818b3f14e94",
        "5f300313f348463105fd5e271b6f07805625f2bc30f22ab0b391413bcc361dbf",
    }),
    ('SB Plastics EPZ Ltd', "sb-plastics.png", {
        "7c5cc10370c1330e3f7e4c084bab9e047d89db30d940b76d5f7bee12537f62be",
        "c21f6ac6eee87d50001345145604feadabb78fbfacc2ef2dfff7bc3da704c34a",
    }),
    ('Taifa Gas', "taifa-gas.png", {
        "27556001a73e275fa2994995f46841317e2f61a706c27bbae7ce2c9e2ec4c401",
    }),
    ('Government of the United Republic of Tanzania', "tanzania-government.png", {
        "76aaedb24b95035315cc1f64aa025bd881745e160b21b9634dbfd9cc6fca3ab0",
        "99bb32a244021c549d9a7cc436013ccb0d2456744ce6aebc8b34b8acf8e6e968",
    }),
    ('UNESCO Tanzania', "unesco.png", {
        "665005a9e2fff04bbe76bf975a926768ed8dc8c2c72ad8c47a011f7e2f9d63c6",
        "f8522d6a47f17ea8581d7888c486bffc12f0f98c884aef9c95bd9672e3d5bff0",
    }),
    ('UTT AMIS', "utt-amis.png", {
        "f569b1420cbed4e0e875fd4cb13fa65bd45459a4ad20046cff213bc0d8163938",
    }),
]


def tidy_partner_logos(apps, schema_editor):
    """Swap in the trimmed partner logos, but only where the stored logo is one seed_content put there.

    The new files are the same logos with their empty margins removed, so they all appear at a
    similar size. A logo someone uploaded through the dashboard matches none of the hashes and is
    left alone.
    """
    Partner = apps.get_model("website", "Partner")
    for name, filename, old_hashes in LOGOS:
        partner = Partner.objects.filter(name=name).exclude(logo="").first()
        if not partner:
            continue
        try:
            with partner.logo.open("rb") as stored:
                current = hashlib.sha256(stored.read()).hexdigest()
        except Exception:
            continue
        if current not in old_hashes:
            continue
        f = photo(f"partners/{filename}")
        if f and upload(partner.logo, f):
            partner.save(update_fields=["logo"])


class Migration(migrations.Migration):
    dependencies = [("website", "0007_donation_branch_code")]

    operations = [migrations.RunPython(tidy_partner_logos, migrations.RunPython.noop)]
