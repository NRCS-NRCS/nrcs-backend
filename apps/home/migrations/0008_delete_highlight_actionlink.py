"""Move the highlight tree into news, then drop the home models."""

from django.db import migrations
from django.utils.text import slugify

# Historical models carry no enum, so News.status values are spelled out here.
# Mirrors apps.common.models.StatusEnum.
STATUS_DRAFT = 50
STATUS_PUBLISHED = 60

SLUG_MAX_LENGTH = 250


def _unique_slug(News, heading):
    """Build a slug News does not use yet; historical models lack the save() that does this."""
    base = slugify(heading)[:SLUG_MAX_LENGTH] or "highlight"
    slug = base
    suffix = 2
    while News.objects.filter(slug=slug).exists():
        tail = f"-{suffix}"
        slug = f"{base[: SLUG_MAX_LENGTH - len(tail)]}{tail}"
        suffix += 1
    return slug


def highlights_to_news(apps, schema_editor):
    """Carry every highlight, with its links, files and key stats, across to news."""
    Highlight = apps.get_model("home", "Highlight")
    News = apps.get_model("news", "News")
    NewsActionLink = apps.get_model("news", "ActionLink")
    NewsAttachment = apps.get_model("news", "NewsAttachment")
    NewsKeyStat = apps.get_model("news", "KeyStat")

    # Only one news item may sit in the homepage popup, so an existing one keeps
    # the slot and at most one highlight can claim a free one.
    popup_taken = News.objects.filter(show_in_popup=True).exists()

    for highlight in Highlight.objects.order_by("pk").iterator():
        news = News.objects.create(
            title=highlight.heading,
            content=highlight.description,
            # Highlights had no publish date of their own.
            published_date=highlight.created_at.date(),
            slug=_unique_slug(News, highlight.heading),
            # The image keeps its stored "highlights/" path; upload_to only
            # decides where new uploads land, so the file stays reachable.
            cover_image=highlight.image,
            status=STATUS_PUBLISHED if highlight.is_active else STATUS_DRAFT,
            is_highlighted=highlight.is_active,
            show_in_popup=highlight.show_in_popup and not popup_taken,
            created_by_id=highlight.created_by_id,
            modified_by_id=highlight.modified_by_id,
        )
        popup_taken = popup_taken or news.show_in_popup

        # created_at/modified_at are auto fields, so create() stamped them with
        # now; put the highlight's own timestamps back.
        News.objects.filter(pk=news.pk).update(
            created_at=highlight.created_at,
            modified_at=highlight.modified_at,
        )

        NewsActionLink.objects.bulk_create(
            [NewsActionLink(news=news, url=link.url, label=link.label) for link in highlight.action_links.order_by("pk")]
        )
        NewsAttachment.objects.bulk_create(
            [
                NewsAttachment(news=news, file=highlight_file.file, order=highlight_file.order, label=highlight_file.label)
                for highlight_file in highlight.files.order_by("order")
            ]
        )
        NewsKeyStat.objects.bulk_create(
            [
                NewsKeyStat(
                    news=news, order=key_stat.order, title=key_stat.title, stat=key_stat.stat, featured=key_stat.featured
                )
                for key_stat in highlight.key_stats.order_by("order")
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_highlight_show_in_popup"),
        # The news side must already have attachments and key stats to copy into.
        ("news", "0006_move_news_file_to_attachments"),
    ]

    operations = [
        # Copy the data out before the tables holding it go away. Reversing only
        # recreates empty home tables: the migrated news rows are indistinguishable
        # from ones authored later, so unwinding the copy is left to hand.
        migrations.RunPython(highlights_to_news, migrations.RunPython.noop),
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
