import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_news_is_highlighted"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActionLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField()),
                ("label", models.CharField(max_length=255)),
                (
                    "news",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="action_links",
                        to="news.news",
                    ),
                ),
            ],
        ),
    ]
