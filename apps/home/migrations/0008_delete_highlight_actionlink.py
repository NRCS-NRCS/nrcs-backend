from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_highlight_show_in_popup"),
    ]

    operations = [
        # Constraints reference the highlight FK, so drop them before the models.
        migrations.RemoveConstraint(
            model_name="keystat",
            name="unique_key_stat_order_per_highlight",
        ),
        migrations.RemoveConstraint(
            model_name="highlightfile",
            name="unique_highlight_file_order_per_highlight",
        ),
        migrations.DeleteModel(
            name="KeyStat",
        ),
        migrations.DeleteModel(
            name="HighlightFile",
        ),
        migrations.DeleteModel(
            name="ActionLink",
        ),
        migrations.DeleteModel(
            name="Highlight",
        ),
    ]
