import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0004_news_actionlink"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="show_in_popup",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="KeyStat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=255)),
                ("stat", models.IntegerField()),
                ("featured", models.BooleanField(default=False)),
                (
                    "news",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="key_stats",
                        to="news.news",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
                "constraints": [
                    models.UniqueConstraint(fields=("news", "order"), name="unique_key_stat_order_per_news"),
                ],
            },
        ),
        migrations.CreateModel(
            name="NewsFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="news/files/")),
                ("order", models.PositiveIntegerField()),
                ("label", models.CharField(blank=True, max_length=255)),
                (
                    "news",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="files",
                        to="news.news",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
                "constraints": [
                    models.UniqueConstraint(fields=("news", "order"), name="unique_news_file_order_per_news"),
                ],
            },
        ),
    ]
