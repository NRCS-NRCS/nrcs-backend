from apps.home.factories import HighlightFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestHighlightDescriptionMediaUrls(TestCase):
    QUERY = """
      query highlights {
        highlights {
            description
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-desc-media-test")

    def test_relative_media_urls_are_absolutized(self):
        # An editor-uploaded image lands in the markdown as a root-relative path.
        HighlightFactory.create(
            heading="With image",
            description="Intro\n\n![alt](/media/editor/photo.png)\n\nOutro",
            image="test.jpg",
        )
        content = self.query_check(self.QUERY)
        description = content["data"]["highlights"][0]["description"]
        # On filesystem storage (test env) the path is made absolute against the host.
        assert self.get_media_url("editor/photo.png") in description, description
        assert "](/media/editor/photo.png)" not in description, description

    def test_plain_description_unchanged(self):
        HighlightFactory.create(heading="Plain", description="Just text, no media.", image="test.jpg")
        content = self.query_check(self.QUERY)
        assert content["data"]["highlights"][0]["description"] == "Just text, no media."
