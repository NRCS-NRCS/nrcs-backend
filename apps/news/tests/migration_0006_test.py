"""Exercise the 0006 data migration against a real historical schema."""
import pytest
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

BEFORE = [("news", "0005_news_show_in_popup_keystat_newsattachment")]
AFTER = [("news", "0006_move_news_file_to_attachments")]


@pytest.mark.django_db(transaction=True)
def test_news_file_becomes_an_attachment():
    executor = MigrationExecutor(connection)
    executor.migrate(BEFORE)
    executor.loader.build_graph()
    old_apps = executor.loader.project_state(BEFORE).apps

    News = old_apps.get_model("news", "News")
    NewsAttachment = old_apps.get_model("news", "NewsAttachment")
    User = old_apps.get_model("auth", "User")

    author = User.objects.create(username="migration-user")
    with_file = News.objects.create(
        title="Has file", published_date="2024-01-01", slug="has-file", file="news/report.pdf",
        created_by=author, modified_by=author,
    )
    without = News.objects.create(
        title="No file", published_date="2024-01-01", slug="no-file", file="",
        created_by=author, modified_by=author,
    )
    # An existing attachment must keep order 1; the migrated file goes after it.
    NewsAttachment.objects.create(news=with_file, file="news/attachments/existing.pdf", order=1, label="Existing")

    executor = MigrationExecutor(connection)
    executor.migrate(AFTER)
    new_apps = executor.loader.project_state(AFTER).apps
    NewsAttachment = new_apps.get_model("news", "NewsAttachment")

    rows = list(NewsAttachment.objects.filter(news_id=with_file.pk).order_by("order").values_list("order", "file"))
    assert rows == [(1, "news/attachments/existing.pdf"), (2, "news/report.pdf")], rows
    assert NewsAttachment.objects.filter(news_id=without.pk).count() == 0
    assert not hasattr(new_apps.get_model("news", "News"), "file")
