import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.forms.models import inlineformset_factory
from django.utils.datastructures import MultiValueDict

from apps.home.admin import HighlightFileInlineFormSet
from apps.home.factories import HighlightFactory, HighlightFileFactory
from apps.home.models import Highlight, HighlightFile
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase
from utils.common import MAX_HIGHLIGHT_FILE_SIZE


class TestHighlightFilesQuery(TestCase):
    QUERY = """
      query highlights {
        highlights {
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
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-files-test")

    def test_files_returned_ordered(self):
        highlight = HighlightFactory.create(heading="With files", description="x", image="test.jpg")
        # Created out of order to confirm the response is ordered by `order`.
        HighlightFileFactory.create(highlight=highlight, order=2, label="Second", file="highlights/files/b.pdf")
        HighlightFileFactory.create(highlight=highlight, order=1, label="", file="highlights/files/a.pdf")

        content = self.query_check(self.QUERY)
        assert content["data"]["highlights"] == [
            {
                "id": self.gID(highlight.id),
                "files": [
                    {"order": 1, "label": "", "file": {"url": self.get_media_url("highlights/files/a.pdf")}},
                    {"order": 2, "label": "Second", "file": {"url": self.get_media_url("highlights/files/b.pdf")}},
                ],
            },
        ], content


class TestHighlightFileSizeLimit(TestCase):
    def test_oversized_file_rejected(self):
        over = (MAX_HIGHLIGHT_FILE_SIZE * 1024 * 1024) + 1
        big = SimpleUploadedFile("big.pdf", b"0" * over, content_type="application/pdf")
        with pytest.raises(ValidationError):
            HighlightFile(order=1, file=big).clean()

    def test_within_limit_allowed(self):
        small = SimpleUploadedFile("ok.pdf", b"0" * 1024, content_type="application/pdf")
        HighlightFile(order=1, file=small).clean()  # should not raise


class TestHighlightFileCountLimit(TestCase):
    FormSet = inlineformset_factory(
        Highlight,
        HighlightFile,
        formset=HighlightFileInlineFormSet,
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
        formset = self.FormSet(data=data, files=files, instance=Highlight())
        formset.is_valid()
        return formset.non_form_errors()

    def test_max_files_allowed(self):
        assert self._build(HighlightFile.MAX_FILES_PER_HIGHLIGHT) == []

    def test_over_max_files_rejected(self):
        errors = self._build(HighlightFile.MAX_FILES_PER_HIGHLIGHT + 1)
        assert errors
        assert "at most 50 files" in errors[0]
