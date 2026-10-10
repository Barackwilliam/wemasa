from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    # The page cache lives in the database (settings.CACHES). Creating its table here means
    # `python manage.py migrate` is enough; no separate `createcachetable` step to forget.
    call_command("createcachetable", database=schema_editor.connection.alias, verbosity=0)


class Migration(migrations.Migration):
    dependencies = [("website", "0003_restore_original_fields")]

    operations = [migrations.RunPython(create_cache_table, migrations.RunPython.noop)]
