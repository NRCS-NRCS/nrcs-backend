from apps.strategic.factories import UserFactory
from apps.vacancy.factories import JobVacancyFactory
from main.tests.base_test import TestCase


class TestJobVacancyQuery(TestCase):
    class Query:
        JOB_VACANCIES = """
          query jobVacancies($order: JobVacancyOrder) {
            jobVacancies(order: $order) {
                id
                title
                file {
                    url
                }
                description
                numberOfVacancies
                expiryDate
                isArchived
                position
                publishedAt
              }

          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_job_vacancies_query(self):
        def _query():
            return self.query_check(
                self.Query.JOB_VACANCIES,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        job_vacancies_items = [
            JobVacancyFactory.create(
                title="Job Vacancy One",
                description="Something",
                position="Software Engineer",
                file="job1.pdf",
                number_of_vacancies=1,
                expiry_date="2023-12-31",
                is_archived=False,
                published_at="2023-12-31",
            ),
            JobVacancyFactory.create(
                title="Job Vacancy Two",
                description="Something2",
                position="Software Engineer",
                file="job2.pdf",
                number_of_vacancies=1,
                expiry_date="2023-12-31",
                is_archived=True,
                published_at="2023-12-31",
            ),
        ]

        content = _query()
        assert content["data"] == {
            "jobVacancies": [
                dict(
                    id=self.gID(job.id),
                    title=job.title,
                    file=dict(
                        url=self.get_media_url(job.file.name),
                    ),
                    description=job.description,
                    position=job.position,
                    numberOfVacancies=job.number_of_vacancies,
                    expiryDate=job.expiry_date,
                    isArchived=job.is_archived,
                    publishedAt=job.published_at,
                )
                for job in job_vacancies_items
            ],
        }, content
