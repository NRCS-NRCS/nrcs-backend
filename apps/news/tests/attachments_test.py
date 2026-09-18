import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.forms.models import inlineformset_factory
from django.utils.datastructures import MultiValueDict

from apps.news.admin import NewsAttachmentInlineFormSet
from apps.news.factories import NewsAttachmentFactory, NewsFactory
from apps.news.models import News, NewsAttachment
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase
from utils.common import MAX_NEWS_ATTACHMENT_SIZE


class TestNewsAttachmentsQuery(TestCase):
    QUERY = """
      query news {
        news {
            results {
                id
                attachments {
                    order
                    label
                    file {
                        url
                    }
                }
            }
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-attachments-test")

    def test_attachments_returned_ordered(self):
        news = NewsFactory.create(title="With attachments", content="x", published_date="2023-12-31")
        # Created out of order to confirm the response is ordered by `order`.
        NewsAttachmentFactory.create(news=news, order=2, label="Second", file="news/attachments/b.pdf")
        NewsAttachmentFactory.create(news=news, order=1, label="", file="news/attachments/a.pdf")

        content = self.query_check(self.QUERY)
        assert content["data"]["news"]["results"] == [
            {
                "id": self.gID(news.id),
                "attachments": [
                    {"order": 1, "label": "", "file": {"url": self.get_media_url("news/attachments/a.pdf")}},
                    {"order": 2, "label": "Second", "file": {"url": self.get_media_url("news/attachments/b.pdf")}},
                ],
            },
        ], content


class TestNewsAttachmentSizeLimit(TestCase):
    def test_oversized_file_rejected(self):
        over = (MAX_NEWS_ATTACHMENT_SIZE * 1024 * 1024) + 1
        big = SimpleUploadedFile("big.pdf", b"0" * over, content_type="application/pdf")
        with pytest.raises(ValidationError):
            NewsAttachment(order=1, file=big).clean()

    def test_within_limit_allowed(self):
        small = SimpleUploadedFile("ok.pdf", b"0" * 1024, content_type="application/pdf")
        NewsAttachment(order=1, file=small).clean()  # should not raise


class TestNewsAttachmentCountLimit(TestCase):
    FormSet = inlineformset_factory(
        News,
        NewsAttachment,
        formset=NewsAttachmentInlineFormSet,
        fields=["order", "label", "file"],
        extra=0,
        can_delete=True,
    )

    def _build(self, count):
        data = {
            "attachments-TOTAL_FORMS": str(count),
            "attachments-INITIAL_FORMS": "0",
            "attachments-MIN_NUM_FORMS": "0",
            "attachments-MAX_NUM_FORMS": "1000",
        }
        files: MultiValueDict[str, UploadedFile] = MultiValueDict()
        for i in range(count):
            data[f"attachments-{i}-order"] = str(i + 1)
            data[f"attachments-{i}-label"] = f"File {i}"
            files[f"attachments-{i}-file"] = SimpleUploadedFile(f"f{i}.pdf", b"0" * 16, content_type="application/pdf")
        formset = self.FormSet(data=data, files=files, instance=News())
        formset.is_valid()
        return formset.non_form_errors()

    def test_max_attachments_allowed(self):
        assert self._build(NewsAttachment.MAX_ATTACHMENTS_PER_NEWS) == []

    def test_over_max_attachments_rejected(self):
        errors = self._build(NewsAttachment.MAX_ATTACHMENTS_PER_NEWS + 1)
        assert errors
        assert "at most 50 attachments" in errors[0]
