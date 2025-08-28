from apps.home.factories import ActionLinkFactory, HighlightFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestHighlightQuery(TestCase):
    class Query:
        HIGHLIGHT = """
          query highlights($order: HighlightOrder) {
            highlights(order: $order) {
                id
                heading
                description

                actionLinks {
                    url
                    label
                }
                image {
                    url
                }
                expiryDate
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_highlight_query(self):
        def _query():
            return self.query_check(
                self.Query.HIGHLIGHT,
                variables={
                    "order": {"heading": "ASC"},
                },
            )

        highlights_items = [
            HighlightFactory.create(
                heading="Highlight One",
                description="Something",
                image="test.jpg",
                expiry_date="2023-01-01",
            ),
            HighlightFactory.create(
                heading="Highlight Two",
                description="Something2",
                image="test.jpg",
                expiry_date="2023-01-01",
            ),
        ]
        ActionLinkFactory.create(
            url="https://www.nrcs.gov.bd/",
            label="Action Link One",
            highlight=highlights_items[0],
        )
        ActionLinkFactory.create(
            url="https://www.nrcs.gov.bd/",
            label="Action Link Two",
            highlight=highlights_items[1],
        )

        content = _query()
        assert content["data"] == {
            "highlights": [
                dict(
                    id=self.gID(highlight.id),
                    heading=highlight.heading,
                    description=highlight.description,
                    image=dict(url=self.get_media_url(highlight.image.name)),
                    expiryDate=highlight.expiry_date,
                    actionLinks=[
                        dict(
                            url=action_link.url,
                            label=action_link.label,
                        )
                        for action_link in highlight.action_links.all()
                    ],
                )
                for highlight in highlights_items
            ],
        }, content
