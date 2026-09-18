"""Exercise the 0008 data migration against a real historical schema."""

from datetime import UTC, datetime

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

BEFORE = [("home", "0007_highlight_show_in_popup"), ("news", "0006_move_news_file_to_attachments")]
AFTER = [("home", "0008_delete_highlight_actionlink")]

STATUS_DRAFT = 50
STATUS_PUBLISHED = 60


@pytest.mark.django_db(transaction=True)
def test_highlights_become_news(restore_migration_state):
    executor = MigrationExecutor(connection)
    executor.migrate(BEFORE)
    executor.loader.build_graph()
    old_apps = executor.loader.project_state(BEFORE).apps

    Highlight = old_apps.get_model("home", "Highlight")
    ActionLink = old_apps.get_model("home", "ActionLink")
    HighlightFile = old_apps.get_model("home", "HighlightFile")
    KeyStat = old_apps.get_model("home", "KeyStat")
    User = old_apps.get_model("auth", "User")

    author = User.objects.create(username="migration-user")
    live = Highlight.objects.create(
        heading="Flood response",
        description="Relief under way",
        image="highlights/flood.jpg",
        is_active=True,
        show_in_popup=True,
        created_by=author,
        modified_by=author,
    )
    Highlight.objects.create(
        heading="Draft appeal",
        description="Not published yet",
        image="highlights/appeal.jpg",
        is_active=False,
        show_in_popup=False,
        created_by=author,
        modified_by=author,
    )
    # A second popup highlight must not give news two popup rows.
    Highlight.objects.create(
        heading="Flood response",
        description="Duplicate heading, also asking for the popup",
        image="highlights/flood-2.jpg",
        is_active=True,
        show_in_popup=True,
        created_by=author,
        modified_by=author,
    )
    created_at = datetime(2024, 5, 4, 9, 30, tzinfo=UTC)
    Highlight.objects.filter(pk=live.pk).update(created_at=created_at, modified_at=created_at)

    ActionLink.objects.create(highlight=live, url="https://example.org/donate", label="Donate")
    HighlightFile.objects.create(highlight=live, file="highlights/files/report.pdf", order=1, label="Report")
    KeyStat.objects.create(highlight=live, order=1, title="Families reached", stat=1200, featured=True)
    # Orphans have no highlight to hang off, so they are not carried over.
    ActionLink.objects.create(highlight=None, url="https://example.org/orphan", label="Orphan")

    executor = MigrationExecutor(connection)
    executor.migrate(AFTER)
    new_apps = executor.loader.project_state(AFTER).apps
    News = new_apps.get_model("news", "News")
    NewsActionLink = new_apps.get_model("news", "ActionLink")
    NewsAttachment = new_apps.get_model("news", "NewsAttachment")
    NewsKeyStat = new_apps.get_model("news", "KeyStat")

    assert News.objects.count() == 3
    migrated = News.objects.get(slug="flood-response")
    assert migrated.title == "Flood response"
    assert migrated.content == "Relief under way"
    assert migrated.cover_image == "highlights/flood.jpg"
    assert migrated.status == STATUS_PUBLISHED
    assert migrated.is_highlighted
    assert migrated.show_in_popup
    assert migrated.published_date.isoformat() == "2024-05-04"
    assert migrated.created_at == created_at
    assert migrated.created_by_id == author.pk

    draft = News.objects.get(title="Draft appeal")
    assert draft.status == STATUS_DRAFT
    assert not draft.is_highlighted

    # The duplicate heading gets its own slug and loses the popup race.
    duplicate = News.objects.get(slug="flood-response-2")
    assert not duplicate.show_in_popup
    assert News.objects.filter(show_in_popup=True).count() == 1

    assert list(NewsActionLink.objects.values_list("news_id", "url", "label")) == [
        (migrated.pk, "https://example.org/donate", "Donate"),
    ]
    assert list(NewsAttachment.objects.values_list("news_id", "file", "order", "label")) == [
        (migrated.pk, "highlights/files/report.pdf", 1, "Report"),
    ]
    assert list(NewsKeyStat.objects.values_list("news_id", "title", "stat", "order", "featured")) == [
        (migrated.pk, "Families reached", 1200, 1, True),
    ]


@pytest.mark.django_db(transaction=True)
def test_existing_popup_news_keeps_the_slot(restore_migration_state):
    executor = MigrationExecutor(connection)
    executor.migrate(BEFORE)
    executor.loader.build_graph()
    old_apps = executor.loader.project_state(BEFORE).apps

    Highlight = old_apps.get_model("home", "Highlight")
    News = old_apps.get_model("news", "News")
    User = old_apps.get_model("auth", "User")

    author = User.objects.create(username="migration-user")
    incumbent = News.objects.create(
        title="Already in the popup",
        published_date="2024-01-01",
        slug="already-in-the-popup",
        show_in_popup=True,
        created_by=author,
        modified_by=author,
    )
    Highlight.objects.create(
        heading="Wants the popup",
        description="",
        image="highlights/wants.jpg",
        is_active=True,
        show_in_popup=True,
        created_by=author,
        modified_by=author,
    )

    executor = MigrationExecutor(connection)
    executor.migrate(AFTER)
    News = executor.loader.project_state(AFTER).apps.get_model("news", "News")

    assert list(News.objects.filter(show_in_popup=True).values_list("pk", flat=True)) == [incumbent.pk]
