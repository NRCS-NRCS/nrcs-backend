from apps.project.factories import ProjectFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestprojectQuery(TestCase):
    class Query:
        project = """
          query projects($order: ProjectOrder) {
            projects(order: $order) {
              id
              title
              description
              endDate
              id
              startDate
              title
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

    def test_project_query(self):
        def _query():
            return self.query_check(
                self.Query.project,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        project_items = [
            ProjectFactory.create(
                title="project one",
                description="Something",
                cover_image="project1.jpg",
                start_date="2023-01-01",
                end_date="2023-12-31",
            ),
            ProjectFactory.create(
                title="project two",
                description="Something2",
                cover_image="project2.jpg",
                start_date="2023-01-01",
                end_date="2023-12-31",
            ),
        ]

        content = _query()
        assert content["data"] == {
            "projects": [
                dict(
                    id=self.gID(project.id),
                    title=project.title,
                    coverImage={
                        "url": self.get_media_url(project.cover_image.name),
                    },
                    description=project.description,
                    startDate=project.start_date,
                    endDate=project.end_date,
                )
                for project in project_items
            ],
        }, content
