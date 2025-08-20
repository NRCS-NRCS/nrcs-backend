from apps.department.factories import DepartmentFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestStrategicDirectivesQuery(TestCase):
    class Query:
        DEPARTMENT = """
          query department($pagination: OffsetPaginationInput, $order: DepartmentOrder) {
            department(pagination: $pagination, order: $order) {
              totalCount
              results {
                id
                title
                description
                contactPersonName
                contactPersonEmail
                slug
                strategicDirective {
                  id
                  slug
                  title
                  description
                  contactPersonName
                  contactPersonEmail
                }
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

    def test_department_query(self):
        def _query():
            return self.query_check(
                self.Query.DEPARTMENT,
                variables={
                    "pagination": {"limit": 10, "offset": 0},
                    "order": {"id": "ASC"},
                },
            )

        department_items = [
            DepartmentFactory.create(
                title="Department",
                description="Something",
                contact_person_name="John Doe",
                contact_person_email="johndoe@example.com",
                strategic_directive=StrategicDirectivesFactory.create(
                    title="Strategic Directive",
                    description="Something",
                    contact_person_name="John Doe",
                    contact_person_email="johndoe@example.com",
                ),
            ),
            DepartmentFactory.create(
                title="Department One",
                description="Something",
                contact_person_name="John Doe",
                contact_person_email="johndoe@example.com",
                strategic_directive=StrategicDirectivesFactory.create(
                    title="Strategic Directive One",
                    description="Something",
                    contact_person_name="John Doe",
                    contact_person_email="johndoe@example.com",
                ),
            ),
        ]

        content = _query()
        assert content["data"]["department"] == {
            **self.g_pagination(
                offset=0,
                limit=10,
                total_count=2,
                results=[
                    dict(
                        id=self.gID(department.id),
                        title=department.title,
                        description=department.description,
                        contactPersonName=department.contact_person_name,
                        contactPersonEmail=department.contact_person_email,
                        slug=department.slug,
                        strategicDirective={
                            "id": self.gID(department.strategic_directive.id),
                            "slug": department.strategic_directive.slug,
                            "title": department.strategic_directive.title,
                            "description": department.strategic_directive.description,
                            "contactPersonName": department.strategic_directive.contact_person_name,
                            "contactPersonEmail": department.strategic_directive.contact_person_email,
                        },
                    )
                    for department in department_items
                ],
            ),
        }, content
