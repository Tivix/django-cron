
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_cron", "0003_cronjoblock"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="cronjoblog",
            new_name="django_cron_code_89ad04_idx",
            old_fields=("code", "is_success", "ran_at_time"),
        ),
        migrations.RenameIndex(
            model_name="cronjoblog",
            new_name="django_cron_code_966ed3_idx",
            old_fields=("code", "start_time"),
        ),
        migrations.RenameIndex(
            model_name="cronjoblog",
            new_name="django_cron_code_21f381_idx",
            old_fields=("code", "start_time", "ran_at_time"),
        ),
    ]
