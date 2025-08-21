from apps.department.factories import DepartmentFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from apps.work.factories import WorkFactory
from main.tests.base_test import TestCase


class TestWorkQuery(TestCase):
    class Query:
        WORK = """
          query works($order: WorkOrder) {
            works(order: $order) {
              id
              title
              description
              endDate
              id
              startDate
              strategicDirective {
                id
                title
              }
              title
              coverImage {
                url
              }
              department {
                id
                title
              }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_work_query(self):
        def _query():
            return self.query_check(
                self.Query.WORK,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        work_items = [
            WorkFactory.create(
                title="work one",
                description="Something",
                cover_image="work1.jpg",
                department=DepartmentFactory.create(
                    title="department one",
                ),
                strategic_directive=StrategicDirectivesFactory.create(
                    title="strategic directive one",
                ),
                start_date="2023-01-01",
                end_date="2023-12-31",
            ),
            WorkFactory.create(
                title="work two",
                description="Something2",
                cover_image="work2.jpg",
                department=DepartmentFactory.create(
                    title="department two",
                ),
                strategic_directive=StrategicDirectivesFactory.create(
                    title="strategic directive two",
                ),
                start_date="2023-01-01",
                end_date="2023-12-31",
            ),
        ]

        content = _query()
        assert content["data"] == {
            "works": [
                dict(
                    id=self.gID(work.id),
                    title=work.title,
                    coverImage={
                        "url": self.get_media_url(work.cover_image.name),
                    },
                    description=work.description,
                    department={
                        "id": self.gID(work.department.id),
                        "title": work.department.title,
                    },
                    strategicDirective={
                        "id": self.gID(work.strategic_directive.id),
                        "title": work.strategic_directive.title,
                    },
                    startDate=work.start_date,
                    endDate=work.end_date,
                )
                for work in work_items
            ],
        }, content
