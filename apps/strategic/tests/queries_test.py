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
                contactPersonName
                contactPersonEmail
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
                contact_person_name="John Doe",
                contact_person_email="johndoe@example.com",
                cover_image="test.jpg",
            ),
            StrategicDirectivesFactory.create(
                title="Strategic Directive Two",
                description="Something2",
                contact_person_name="Test 2",
                contact_person_email="test@xyz.com",
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
                    contactPersonName=strategic.contact_person_name,
                    contactPersonEmail=strategic.contact_person_email,
                    coverImage=dict(url=strategic.cover_image.url),
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
