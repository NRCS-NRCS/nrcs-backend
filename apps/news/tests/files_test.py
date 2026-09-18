import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.forms.models import inlineformset_factory
from django.utils.datastructures import MultiValueDict

from apps.news.admin import NewsFileInlineFormSet
from apps.news.factories import NewsFactory, NewsFileFactory
from apps.news.models import News, NewsFile
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase
from utils.common import MAX_NEWS_FILE_SIZE


class TestNewsFilesQuery(TestCase):
    QUERY = """
      query news {
        news {
            results {
                id
                files {
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
        cls.user = UserFactory.create(username="nrcs-files-test")

    def test_files_returned_ordered(self):
        news = NewsFactory.create(title="With files", content="x", published_date="2023-12-31")
        # Created out of order to confirm the response is ordered by `order`.
        NewsFileFactory.create(news=news, order=2, label="Second", file="news/files/b.pdf")
        NewsFileFactory.create(news=news, order=1, label="", file="news/files/a.pdf")

        content = self.query_check(self.QUERY)
        assert content["data"]["news"]["results"] == [
            {
                "id": self.gID(news.id),
                "files": [
                    {"order": 1, "label": "", "file": {"url": self.get_media_url("news/files/a.pdf")}},
                    {"order": 2, "label": "Second", "file": {"url": self.get_media_url("news/files/b.pdf")}},
                ],
            },
        ], content


class TestNewsFileSizeLimit(TestCase):
    def test_oversized_file_rejected(self):
        over = (MAX_NEWS_FILE_SIZE * 1024 * 1024) + 1
        big = SimpleUploadedFile("big.pdf", b"0" * over, content_type="application/pdf")
        with pytest.raises(ValidationError):
            NewsFile(order=1, file=big).clean()

    def test_within_limit_allowed(self):
        small = SimpleUploadedFile("ok.pdf", b"0" * 1024, content_type="application/pdf")
        NewsFile(order=1, file=small).clean()  # should not raise


class TestNewsFileCountLimit(TestCase):
    FormSet = inlineformset_factory(
        News,
        NewsFile,
        formset=NewsFileInlineFormSet,
        fields=["order", "label", "file"],
        extra=0,
        can_delete=True,
    )

    def _build(self, count):
        data = {
            "files-TOTAL_FORMS": str(count),
            "files-INITIAL_FORMS": "0",
            "files-MIN_NUM_FORMS": "0",
            "files-MAX_NUM_FORMS": "1000",
        }
        files: MultiValueDict[str, UploadedFile] = MultiValueDict()
        for i in range(count):
            data[f"files-{i}-order"] = str(i + 1)
            data[f"files-{i}-label"] = f"File {i}"
            files[f"files-{i}-file"] = SimpleUploadedFile(f"f{i}.pdf", b"0" * 16, content_type="application/pdf")
        formset = self.FormSet(data=data, files=files, instance=News())
        formset.is_valid()
        return formset.non_form_errors()

    def test_max_files_allowed(self):
        assert self._build(NewsFile.MAX_FILES_PER_NEWS) == []

    def test_over_max_files_rejected(self):
        errors = self._build(NewsFile.MAX_FILES_PER_NEWS + 1)
        assert errors
        assert "at most 50 files" in errors[0]
