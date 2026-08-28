import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from main.tests.base_test import TestCase

_MEDIA_ROOT = tempfile.mkdtemp(prefix="mdeditor-upload-test-")

# A minimal valid 1x1 PNG.
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c636000000200010005fe02fea7d0e0b40000000049454e44ae426082",
)

UPLOAD_URL = "/mdeditor/uploads/"


@override_settings(MEDIA_ROOT=_MEDIA_ROOT)
class TestMDEditorImageUpload(TestCase):
    def test_valid_image_uploaded_via_default_storage(self):
        image = SimpleUploadedFile("photo.png", PNG_BYTES, content_type="image/png")
        response = self.client.post(UPLOAD_URL, {"editormd-image-file": image})
        content = response.json()
        assert content["success"] == 1, content
        # Saved under the configured editor folder and served via storage URL.
        assert "editor/" in content["url"], content
        assert content["url"].endswith(".png"), content
        # Must be framable same-origin so editor.md's upload iframe can read it,
        # despite the site-wide X_FRAME_OPTIONS = "DENY".
        assert response.headers.get("X-Frame-Options") == "SAMEORIGIN", dict(response.headers)

    def test_unsupported_format_rejected(self):
        bad = SimpleUploadedFile("evil.exe", b"MZ", content_type="application/octet-stream")
        content = self.client.post(UPLOAD_URL, {"editormd-image-file": bad}).json()
        assert content["success"] == 0, content
        assert content["url"] == ""

    def test_oversized_image_rejected(self):
        # 3 MB exceeds the 2 MB mdeditor upload limit.
        big = SimpleUploadedFile("big.png", PNG_BYTES + b"0" * (3 * 1024 * 1024), content_type="image/png")
        content = self.client.post(UPLOAD_URL, {"editormd-image-file": big}).json()
        assert content["success"] == 0, content
        assert "too large" in content["message"].lower()
        assert "2 MB" in content["message"], content

    def test_missing_image_rejected(self):
        content = self.client.post(UPLOAD_URL, {}).json()
        assert content["success"] == 0, content
