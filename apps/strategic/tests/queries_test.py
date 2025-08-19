from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestStrategicDirectivesQuery(TestCase):
    class Query:
        STRATEGIC_DIRECTIVES = """
          query strategicDirectives($pagination: OffsetPaginationInput, $order: StrategicDirectivesOrder) {
            strategicDirectives(pagination: $pagination, order: $order) {
              totalCount
              results {
                id
                title
                description
                contactPersonName
                contactPersonEmail
              }
              pageInfo {
                limit
                offset
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
                    "pagination": {"limit": 10, "offset": 0},
                    "order": {"id": "ASC"},
                },
            )

        strategic_directives_items = [
            StrategicDirectivesFactory.create(
                title="Strategic Directive One",
                description="Something",
                contact_person_name="John Doe",
                contact_person_email="johndoe@example.com",
            ),
            StrategicDirectivesFactory.create(
                title="Strategic Directive Two",
                description="Something2",
                contact_person_name="Test 2",
                contact_person_email="test@xyz.com",
            ),
        ]

        content = _query()
        assert content["data"]["strategicDirectives"] == {
            **self.g_pagination(
                offset=0,
                limit=10,
                total_count=2,
                results=[
                    dict(
                        id=self.gID(strategic.id),
                        title=strategic.title,
                        description=strategic.description,
                        contactPersonName=strategic.contact_person_name,
                        contactPersonEmail=strategic.contact_person_email,
                    )
                    for strategic in strategic_directives_items
                ],
            ),
        }, content
