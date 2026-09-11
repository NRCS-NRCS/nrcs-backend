from apps.news.factories import NewsFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestNewsContentMediaUrls(TestCase):
    QUERY = """
      query news {
        news {
            results {
                content
            }
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-desc-media-test")

    def test_relative_media_urls_are_absolutized(self):
        # An editor-uploaded image lands in the markdown as a root-relative path.
        NewsFactory.create(
            title="With image",
            content="Intro\n\n![alt](/media/editor/photo.png)\n\nOutro",
            published_date="2023-12-31",
        )
        content = self.query_check(self.QUERY)
        news_content = content["data"]["news"]["results"][0]["content"]
        # On filesystem storage (test env) the path is made absolute against the host.
        assert self.get_media_url("editor/photo.png") in news_content, news_content
        assert "](/media/editor/photo.png)" not in news_content, news_content

    def test_plain_content_unchanged(self):
        NewsFactory.create(title="Plain", content="Just text, no media.", published_date="2023-12-31")
        content = self.query_check(self.QUERY)
        assert content["data"]["news"]["results"][0]["content"] == "Just text, no media."
