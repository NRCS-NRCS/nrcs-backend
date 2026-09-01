from django.core.files.uploadedfile import SimpleUploadedFile

from apps.common.models import StatusEnum
from apps.news.factories import KeyStatFactory, NewsFactory
from apps.news.models import KeyStat, NewsAttachment
from apps.news.serializers import NewsSerializer
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase

CREATE_NEWS = """
  mutation createNews($data: NewsCreateInput!) {
    createNews(data: $data) {
        ... on NewsTypeMutationResponseType {
            errors
            ok
            result {
                id
                keyStats { id order title stat featured }
            }
        }
    }
  }
"""

UPDATE_NEWS = """
  mutation updateNews($pk: ID!, $data: NewsUpdateInput!) {
    updateNews(data: $data, pk: $pk) {
        ... on NewsTypeMutationResponseType {
            errors
            ok
            result {
                id
                keyStats { id order title stat featured }
            }
        }
    }
  }
"""


class TestNewsKeyStatMutation(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-keystat-mutation", is_staff=True)

    def _update_base(self, news):
        """NewsUpdateInput still marks content and directive as required."""
        return {"content": news.content, "directive": str(news.directive_id)}

    def _base_data(self):
        return {
            "title": "News with stats",
            "content": "Body",
            "publishedDate": "2024-10-01",
            "directive": str(StrategicDirectivesFactory.create(title="Directive").id),
            "status": self.genum(StatusEnum.DRAFT),
        }

    def test_create_with_key_stats(self):
        self.force_login(self.user)
        data = {
            **self._base_data(),
            "keyStats": [
                {"order": 1, "title": "Volunteers", "stat": 100, "featured": True},
                {"order": 2, "title": "Districts", "stat": 77, "featured": False},
            ],
        }
        content = self.query_check(CREATE_NEWS, variables={"data": data})
        resp = content["data"]["createNews"]
        assert resp["errors"] is None, content
        assert [
            {"order": item["order"], "title": item["title"], "featured": item["featured"]}
            for item in resp["result"]["keyStats"]
        ] == [
            {"order": 1, "title": "Volunteers", "featured": True},
            {"order": 2, "title": "Districts", "featured": False},
        ], content

    def test_create_rejects_more_than_four_featured(self):
        self.force_login(self.user)
        data = {
            **self._base_data(),
            "keyStats": [
                {"order": index, "title": f"Stat {index}", "stat": index, "featured": True}
                for index in range(1, 6)
            ],
        }
        content = self.query_check(CREATE_NEWS, variables={"data": data})
        resp = content["data"]["createNews"]
        assert resp["ok"] is False, content
        assert "at most 4 featured" in str(resp["errors"]), content
        assert KeyStat.objects.count() == 0, "the whole mutation should roll back"

    def test_create_rejects_duplicate_order(self):
        self.force_login(self.user)
        data = {
            **self._base_data(),
            "keyStats": [
                {"order": 1, "title": "One", "stat": 1},
                {"order": 1, "title": "Two", "stat": 2},
            ],
        }
        content = self.query_check(CREATE_NEWS, variables={"data": data})
        resp = content["data"]["createNews"]
        assert resp["ok"] is False, content
        assert "distinct order" in str(resp["errors"]), content

    def test_update_creates_updates_and_deletes(self):
        news = NewsFactory.create(
            title="Existing",
            content="Body",
            published_date="2024-05-01",
            status=StatusEnum.DRAFT,
            directive=StrategicDirectivesFactory.create(title="Directive"),
        )
        kept = KeyStatFactory.create(news=news, order=1, title="Kept", stat=10)
        removed = KeyStatFactory.create(news=news, order=2, title="Removed", stat=20)

        self.force_login(self.user)
        data = {
            **self._update_base(news),
            "keyStats": [
                {"update": {"id": str(kept.id), "order": 1, "title": "Renamed", "stat": 11, "featured": True}},
                {"delete": {"id": str(removed.id)}},
                {"create": {"order": 2, "title": "Fresh", "stat": 30, "featured": False}},
            ],
        }
        content = self.query_check(UPDATE_NEWS, variables={"pk": str(news.id), "data": data})
        resp = content["data"]["updateNews"]
        assert resp["errors"] is None, content
        assert [
            {"order": item["order"], "title": item["title"], "featured": item["featured"]}
            for item in resp["result"]["keyStats"]
        ] == [
            {"order": 1, "title": "Renamed", "featured": True},
            {"order": 2, "title": "Fresh", "featured": False},
        ], content
        assert not KeyStat.objects.filter(id=removed.id).exists()

    def test_update_counts_untouched_rows_against_the_featured_limit(self):
        news = NewsFactory.create(
            title="Existing",
            content="Body",
            published_date="2024-05-01",
            status=StatusEnum.DRAFT,
            directive=StrategicDirectivesFactory.create(title="Directive"),
        )
        for index in range(1, 5):
            KeyStatFactory.create(news=news, order=index, title=f"Stat {index}", stat=index, featured=True)

        self.force_login(self.user)
        # A fifth featured stat, with the existing four left untouched.
        data = {
            **self._update_base(news),
            "keyStats": [{"create": {"order": 5, "title": "Fifth", "stat": 5, "featured": True}}],
        }
        content = self.query_check(UPDATE_NEWS, variables={"pk": str(news.id), "data": data})
        resp = content["data"]["updateNews"]
        assert resp["ok"] is False, content
        assert "at most 4 featured" in str(resp["errors"]), content
        assert KeyStat.objects.filter(news=news).count() == 4

    def test_update_can_swap_two_orders(self):
        """The unique (news, order) constraint is deferred, so a swap is one payload."""
        news = NewsFactory.create(
            title="Existing",
            content="Body",
            published_date="2024-05-01",
            status=StatusEnum.DRAFT,
            directive=StrategicDirectivesFactory.create(title="Directive"),
        )
        first = KeyStatFactory.create(news=news, order=1, title="First", stat=1)
        second = KeyStatFactory.create(news=news, order=2, title="Second", stat=2)

        self.force_login(self.user)
        data = {
            **self._update_base(news),
            "keyStats": [
                {"update": {"id": str(first.id), "order": 2}},
                {"update": {"id": str(second.id), "order": 1}},
            ],
        }
        content = self.query_check(UPDATE_NEWS, variables={"pk": str(news.id), "data": data})
        resp = content["data"]["updateNews"]
        assert resp["errors"] is None, content
        assert [(item["title"], item["order"]) for item in resp["result"]["keyStats"]] == [
            ("Second", 1),
            ("First", 2),
        ], content

    def test_key_stats_left_alone_when_not_sent(self):
        news = NewsFactory.create(
            title="Existing",
            content="Body",
            published_date="2024-05-01",
            status=StatusEnum.DRAFT,
            directive=StrategicDirectivesFactory.create(title="Directive"),
        )
        KeyStatFactory.create(news=news, order=1, title="Kept", stat=10)

        self.force_login(self.user)
        content = self.query_check(
            UPDATE_NEWS,
            variables={"pk": str(news.id), "data": {**self._update_base(news), "title": "Retitled"}},
        )
        resp = content["data"]["updateNews"]
        assert resp["errors"] is None, content
        assert len(resp["result"]["keyStats"]) == 1, content


class TestNewsAttachmentLimit(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-attachment-mutation", is_staff=True)

    def _news_at_attachment_cap(self):
        news = NewsFactory.create(
            title="Existing",
            content="Body",
            published_date="2024-05-01",
            status=StatusEnum.DRAFT,
            directive=StrategicDirectivesFactory.create(title="Directive"),
        )
        for index in range(NewsAttachment.MAX_ATTACHMENTS_PER_NEWS):
            NewsAttachment.objects.create(news=news, order=index + 1, file=f"news/attachments/{index}.pdf")
        return news

    def test_one_attachment_over_the_cap_is_rejected(self):
        news = self._news_at_attachment_cap()
        serializer = NewsSerializer(
            instance=news,
            data={
                "attachments": [
                    {
                        "order": NewsAttachment.MAX_ATTACHMENTS_PER_NEWS + 1,
                        "file": SimpleUploadedFile("extra.pdf", b"x", content_type="application/pdf"),
                    },
                ],
            },
            partial=True,
        )
        assert not serializer.is_valid()
        assert "at most 50 attachments" in str(serializer.errors["attachments"])

    def test_replacing_an_existing_row_stays_within_the_cap(self):
        news = self._news_at_attachment_cap()
        first = NewsAttachment.objects.filter(news=news).first()
        serializer = NewsSerializer(
            instance=news,
            data={"attachments": [{"id": first.id, "order": first.order, "label": "Renamed"}]},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors


class TestNewsAttachmentUpload(TestCase):
    """The CMS sends attachments nested inside the CUD list, so the multipart
    map targets a path like ``variables.data.attachments.0.create.file``."""

    CREATE_WITH_FILES = """
      mutation createNews($data: NewsCreateInput!) {
        createNews(data: $data) {
            ... on NewsTypeMutationResponseType {
                errors
                ok
                result {
                    id
                    attachments { id order label file { name url } }
                }
            }
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-attachment-upload", is_staff=True)

    def test_nested_file_uploads_are_stored(self):
        self.force_login(self.user)
        directive = StrategicDirectivesFactory.create(title="Directive")
        data = {
            "title": "News with attachments",
            "content": "Body",
            "publishedDate": "2024-10-01",
            "directive": str(directive.id),
            "status": self.genum(StatusEnum.DRAFT),
            "attachments": [
                {"order": 1, "label": "First", "file": None},
                {"order": 2, "label": "Second", "file": None},
            ],
        }
        first = SimpleUploadedFile("first.pdf", b"first", content_type="application/pdf")
        second = SimpleUploadedFile("second.pdf", b"second", content_type="application/pdf")

        content = self.query_check(
            self.CREATE_WITH_FILES,
            variables={"data": data},
            files={"file0": first, "file1": second},
            map={
                "file0": ["variables.data.attachments.0.file"],
                "file1": ["variables.data.attachments.1.file"],
            },
        )
        resp = content["data"]["createNews"]
        assert resp["errors"] is None, content
        assert [(row["order"], row["label"]) for row in resp["result"]["attachments"]] == [
            (1, "First"),
            (2, "Second"),
        ], content
        assert NewsAttachment.objects.count() == 2
