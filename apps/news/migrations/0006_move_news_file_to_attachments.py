from django.db import migrations
from django.db.models import Max


def file_to_attachment(apps, schema_editor):
    """Carry each News.file across as an attachment before the column is dropped."""
    News = apps.get_model("news", "News")
    NewsAttachment = apps.get_model("news", "NewsAttachment")

    for news in News.objects.exclude(file="").exclude(file=None).iterator():
        # Existing attachments keep their order; the migrated file goes last.
        last_order = NewsAttachment.objects.filter(news=news).aggregate(value=Max("order"))["value"]
        NewsAttachment.objects.create(
            news=news,
            file=news.file,
            order=(last_order + 1) if last_order is not None else 1,
            label="",
        )


def attachment_to_file(apps, schema_editor):
    """Put the first attachment back on News.file. Any others are left behind."""
    News = apps.get_model("news", "News")
    NewsAttachment = apps.get_model("news", "NewsAttachment")

    for news in News.objects.iterator():
        first = NewsAttachment.objects.filter(news=news).order_by("order").first()
        if first is not None:
            news.file = first.file
            news.save(update_fields=["file"])


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0005_news_show_in_popup_keystat_newsattachment"),
    ]

    operations = [
        migrations.RunPython(file_to_attachment, attachment_to_file),
        migrations.RemoveField(
            model_name="news",
            name="file",
        ),
    ]
