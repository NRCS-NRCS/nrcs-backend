from apps.resources.factories import ResourceFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestResourcesQuery(TestCase):
    class Query:
        RESOURCES = """
          query resources($order: ResourceOrder) {
            resources(order: $order) {
                content
                file {
                    url
                }
                id
                publishedDate
                title
                directive {
                    id
                }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_resources_query(self):
        def _query():
            return self.query_check(
                self.Query.RESOURCES,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        resources_items = [
            ResourceFactory.create(
                content="Something",
                published_date="2023-12-31",
                title="Resource One",
                file="resource1.pdf",
                directive=StrategicDirectivesFactory.create(
                    title="Directive One",
                ),
            ),
            ResourceFactory.create(
                content="Something2",
                published_date="2023-12-31",
                title="Resource Two",
                file="resource2.pdf",
                directive=StrategicDirectivesFactory.create(
                    title="Directive One",
                ),
            ),
        ]

        content = _query()
        assert content["data"] == {
            "resources": [
                dict(
                    id=self.gID(resource.id),
                    title=resource.title,
                    content=resource.content,
                    file=dict(
                        url=self.get_media_url(resource.file.name),
                    ),
                    publishedDate=resource.published_date,
                    directive=(dict(id=self.gID(resource.directive.id)) if resource.directive else None),
                )
                for resource in resources_items
            ],
        }, content
