"""CORS_URLS_REGEX is opt-in per path, so a new browser-facing endpoint is
easy to add and then find blocked. These pin the paths the CMS calls."""

from main.tests.base_test import TestCase

ORIGIN = "http://localhost:3055"


class TestCorsAllowedPaths(TestCase):
    def _preflight(self, path):
        return self.client.options(
            path,
            HTTP_ORIGIN=ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-csrftoken",
        )

    def test_markdown_image_upload_is_cors_enabled(self):
        response = self._preflight("/mdeditor/uploads/")
        assert response.headers.get("access-control-allow-origin") == ORIGIN, dict(response.headers)
        assert response.headers.get("access-control-allow-credentials") == "true", dict(response.headers)
        assert "x-csrftoken" in response.headers.get("access-control-allow-headers", "")

    def test_graphql_is_cors_enabled(self):
        response = self._preflight("/graphql/")
        assert response.headers.get("access-control-allow-origin") == ORIGIN, dict(response.headers)

    def test_unlisted_path_is_not_cors_enabled(self):
        response = self._preflight("/admin/")
        assert response.headers.get("access-control-allow-origin") is None, dict(response.headers)
