from apps.news.factories import NewsFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestNewsQuery(TestCase):
    class Query:
        NEWS = """
          query news($order: NewsOrder) {
            news(order: $order) {
                results {
                    content
                    id
                    publishedDate
                    title
                    directive {
                        id
                    }
                }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test", is_staff=True)

    def test_news_query(self):
        def _query():
            return self.query_check(
                self.Query.NEWS,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        news_items = [
            NewsFactory.create(
                content="Something",
                published_date="2023-12-31",
                title="News One",
                directive=StrategicDirectivesFactory.create(
                    title="Directive One",
                ),
            ),
            NewsFactory.create(
                content="Something2",
                published_date="2023-12-31",
                title="News Two",
            ),
        ]

        content = _query()
        assert content["data"]["news"]["results"] == [
            dict(
                id=self.gID(news.id),
                title=news.title,
                content=news.content,
                publishedDate=news.published_date,
                directive=(dict(id=self.gID(news.directive.id)) if news.directive else None),
            )
            for news in news_items
        ], content
