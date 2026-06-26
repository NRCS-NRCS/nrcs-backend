from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_remove_highlight_expiry_date_highlight_is_active"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ActionLink",
        ),
        migrations.DeleteModel(
            name="Highlight",
        ),
    ]
