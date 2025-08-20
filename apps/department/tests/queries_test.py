from apps.department.factories import DepartmentFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestStrategicDirectivesQuery(TestCase):
    class Query:
        DEPARTMENT = """
          query departments($order: DepartmentOrder) {
            departments(order: $order) {
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
        assert content["data"] == {
            "departments": [
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
        }, content
