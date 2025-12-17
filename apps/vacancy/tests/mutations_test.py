from django.core.files.uploadedfile import SimpleUploadedFile

from apps.department.factories import DepartmentFactory
from apps.strategic.factories import UserFactory
from apps.vacancy.factories import JobVacancyFactory
from apps.vacancy.models import JobVacancy
from main.tests.base_test import TestCase


def generate_vacancy_test_file():
    return SimpleUploadedFile(
        name="vancancy_file.pdf",
        content=b"Fake Image binary content",
        content_type="application/pdf",
    )


def graphql_file_mutation(
    *,
    query_check_func,
    query: str,
    resource_data: dict,
    **kwargs,
) -> dict:
    variables = {"data": resource_data}
    if pk := kwargs.pop("pk", None):
        variables["pk"] = pk

    with generate_vacancy_test_file() as file:
        return query_check_func(
            query,
            variables=variables,
            files={
                "file": file,
            },
            map={
                "file": ["variables.data.file"],
            },
            **kwargs,
        )


class TestJobVacancyMutation(TestCase):
    class Mutation:
        CREATE_JOB_VACANCY = """
          mutation createJobVacancy($data: JobVacancyCreateInput!) {
              createJobVacancy(data: $data) {
                  ... on JobVacancyTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          description
                          file {
                             url
                          }
                          position
                          isArchived
                          publishedAt
                          numberOfVacancies
                          department {
                              id
                          }
                          createdBy {
                             id
                          }
                       }
                  }
              }
          }
        """

        UPDATE_JOB_VACANCY = """
            mutation updateJobVacancy($pk: ID!, $data: JobVacancyUpdateInput!) {
                updateJobVacancy(data: $data, pk: $pk) {
                    ... on JobVacancyTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          description
                          file {
                             url
                          }
                          position
                          expiryDate
                          isArchived
                          publishedAt
                          numberOfVacancies
                          department {
                              id
                          }
                       }
                    }
                }
            }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_create_job_vacancy(self):
        department = DepartmentFactory.create(
            title="Department One",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
        )
        data = {
            "title": "New JobVacancy",
            "description": "JobVacancy Description",
            "publishedAt": "2024-01-01",
            "department": str(department.pk),
            "position": "Software Engineer",
            "isArchived": False,
            "expiryDate": "2024-12-31",
            "numberOfVacancies": 5,
        }

        self.force_login(self.user)
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.CREATE_JOB_VACANCY,
            resource_data=data,
        )

        resp_data = content["data"]["createJobVacancy"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            errors=None,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                description=data["description"],
                publishedAt=data["publishedAt"],
                department=dict(
                    id=self.gID(department.id),
                ),
                position=data["position"],
                isArchived=data["isArchived"],
                numberOfVacancies=data["numberOfVacancies"],
                createdBy=dict(
                    id=self.gID(self.user.id),
                ),
                file=dict(
                    url=resp_data["result"]["file"]["url"],
                ),
            ),
        ), content

        # Check the image file is saved correctly
        resource_id = resp_data["result"]["id"]
        resource = JobVacancy.objects.get(id=self.gID(resource_id))
        assert resource.file, "File should be saved and not empty"

    def test_update_job_vacancy(self):
        vacancy = JobVacancyFactory.create(
            title="Initial Title",
            position="Software Engineer",
            description="Initial Description",
            number_of_vacancies=3,
            expiry_date="2024-12-31",
            published_at="2024-01-01",
            department=DepartmentFactory.create(
                title="Department Old",
                description="Something Old",
                contact_person_name="Old Contact",
                contact_person_email="old@gmail.com",
            ),
            file=generate_vacancy_test_file(),
        )
        new_department = DepartmentFactory.create(
            title="Department New",
            description="Something New",
            contact_person_name="New employee",
            contact_person_email="new@gmail.com",
        )

        data = {
            "title": "Updated JobVacancy Title",
            "description": "Updated Description",
            "position": "Senior Software Engineer",
            "numberOfVacancies": 4,
            "expiryDate": "2024-11-30",
            "department": new_department.pk,
            "publishedAt": "2024-06-01",
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_JOB_VACANCY,
            variables={
                "pk": self.gID(vacancy.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateJobVacancy"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(vacancy.id),
                title=data["title"],
                description=data["description"],
                position=data["position"],
                isArchived=vacancy.is_archived,
                numberOfVacancies=data["numberOfVacancies"],
                expiryDate=data["expiryDate"],
                publishedAt=data["publishedAt"],
                department=dict(
                    id=self.gID(new_department.id),
                ),
                file=dict(
                    url=resp_data["result"]["file"]["url"],
                ),
            ),
        ), content

        # Update with new file
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_JOB_VACANCY,
            pk=self.gID(vacancy.id),
            resource_data=data,
        )
        resp_data = content["data"]["updateJobVacancy"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(vacancy.id),
                title=data["title"],
                description=data["description"],
                position=data["position"],
                isArchived=vacancy.is_archived,
                numberOfVacancies=data["numberOfVacancies"],
                expiryDate=data["expiryDate"],
                publishedAt=data["publishedAt"],
                department=dict(
                    id=self.gID(new_department.id),
                ),
                file=dict(
                    url=resp_data["result"]["file"]["url"],
                ),
            ),
        ), content

        # Check THE file should not be empty
        vacancy.refresh_from_db()
        assert vacancy.file, "File should be updated and not empty"
