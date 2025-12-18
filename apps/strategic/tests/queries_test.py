from apps.strategic.factories import MajorResponsibilitiesFactory, StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestStrategicDirectivesQuery(TestCase):
    class Query:
        STRATEGIC_DIRECTIVES = """
          query strategicDirectives($order: StrategicDirectivesOrder) {
            strategicDirectives(order: $order) {
                id
                title
                description
                majorResponsibilities {
                    description
                    id
                    slug
                    title
                }
                coverImage {
                    url
                }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_strategic_directives_query(self):
        def _query():
            return self.query_check(
                self.Query.STRATEGIC_DIRECTIVES,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        strategic_directives_items = [
            StrategicDirectivesFactory.create(
                title="Strategic Directive One",
                description="Something",
                cover_image="test.jpg",
            ),
            StrategicDirectivesFactory.create(
                title="Strategic Directive Two",
                description="Something2",
                cover_image="test.jpg",
            ),
        ]
        MajorResponsibilitiesFactory.create(
            title="Major Responsibility One",
            description="Something",
            directive=strategic_directives_items[0],
        )
        MajorResponsibilitiesFactory.create(
            title="Major Responsibility Two",
            description="Something2",
            directive=strategic_directives_items[1],
        )

        content = _query()
        assert content["data"] == {
            "strategicDirectives": [
                dict(
                    id=self.gID(strategic.id),
                    title=strategic.title,
                    description=strategic.description,
                    coverImage=dict(url=self.get_media_url(strategic.cover_image.name)),
                    majorResponsibilities=[
                        dict(
                            id=self.gID(major.id),
                            title=major.title,
                            description=major.description,
                            slug=major.slug,
                        )
                        for major in strategic.major_responsibilities.all()
                    ],
                )
                for strategic in strategic_directives_items
            ],
        }, content
