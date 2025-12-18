import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.strategic.factories import MajorResponsibilitiesFactory, StrategicDirectivesFactory, UserFactory
from apps.strategic.models import MajorResponsibilities
from main.tests.base_test import TestCase


def generate_test_image_file():
    image = Image.new("RGB", (10, 10))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    return SimpleUploadedFile(
        "test.jpg",
        buffer.read(),
        content_type="image/jpeg",
    )


def strategic_image_mutation(
    *,
    query_check_func,
    query: str,
    data: dict,
    **kwargs,
) -> dict:
    variables = {"data": data}
    if pk := kwargs.pop("pk", None):
        variables["pk"] = pk

    with generate_test_image_file() as file:
        return query_check_func(
            query,
            variables=variables,
            files={
                "coverImage": file,
            },
            map={
                "coverImage": ["variables.data.coverImage"],
            },
            **kwargs,
        )


class TestStrategicDirectivesMutation(TestCase):
    class Mutation:
        CREATE_STRATEGIC_DIRECTIVES = """
          mutation createStrategicDirectives($data: StrategicDirectivesCreateInput!) {
              createStrategicDirectives(data: $data) {
                  ... on StrategicDirectivesTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          description
                          coverImage {
                              url
                          }
                          majorResponsibilities {
                            id
                            title
                            description
                          }
                       }
                  }
              }
          }
        """

        UPDATE_STRATEGIC_DIRECTIVES = """
            mutation updateStrategicDirectives($pk: ID!, $data: StrategicDirectivesUpdateInput!) {
                updateStrategicDirectives(data: $data, pk: $pk) {
                    ... on StrategicDirectivesTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         description
                         coverImage {
                             url
                         }
                         majorResponsibilities {
                             id
                             title
                             description
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

    def test_create_strategic_directives(self):
        data = {
            "title": "New Strategic Directive",
            "description": "Strategic Directive Description",
            "majorResponsibilities": [
                {
                    "title": "Responsibility 1",
                    "description": "Description 1",
                },
                {
                    "title": "Responsibility 2",
                    "description": "Description 2",
                },
            ],
        }

        self.force_login(self.user)
        content = strategic_image_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.CREATE_STRATEGIC_DIRECTIVES,
            data=data,
        )
        resp_data = content["data"]["createStrategicDirectives"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                description=data["description"],
                coverImage=dict(
                    url=resp_data["result"]["coverImage"]["url"],
                ),
                majorResponsibilities=[
                    dict(
                        id=resp_data["result"]["majorResponsibilities"][0]["id"],
                        title="Responsibility 1",
                        description="Description 1",
                    ),
                    dict(
                        id=resp_data["result"]["majorResponsibilities"][1]["id"],
                        title="Responsibility 2",
                        description="Description 2",
                    ),
                ],
            ),
        )

    def test_update_strategic_directives(self):
        strategic = StrategicDirectivesFactory.create(
            title="Original Title",
            description="Original Description",
        )
        major_resp_1 = MajorResponsibilitiesFactory.create(
            title="Old Responsibility 1",
            description="Old Description 1",
            directive=strategic,
        )
        major_resp_2 = MajorResponsibilitiesFactory.create(
            title="Old Responsibility 2",
            description="Old Description 2",
            directive=strategic,
        )

        data = {
            "title": "Updated Strategic Directive",
            "description": "Updated Description",
            "majorResponsibilities": [
                {
                    "update": {
                        "id": self.gID(major_resp_1.id),
                        "title": "New Responsibility",
                        "description": "New Description",
                    },
                },
                {
                    "create": {
                        "title": "Another Responsibility",
                        "description": "Another Description",
                    },
                },
                {
                    "delete": {
                        "id": self.gID(major_resp_2.id),
                    },
                },
            ],
        }

        self.force_login(self.user)
        content = strategic_image_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_STRATEGIC_DIRECTIVES,
            pk=self.gID(strategic.id),
            data=data,
        )
        resp_data = content["data"]["updateStrategicDirectives"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(strategic.id),
                title=data["title"],
                description=data["description"],
                coverImage=dict(
                    url=resp_data["result"]["coverImage"]["url"],
                ),
                majorResponsibilities=[
                    dict(
                        id=self.gID(major_resp_1.id),
                        title=data["majorResponsibilities"][0]["update"]["title"],
                        description=data["majorResponsibilities"][0]["update"]["description"],
                    ),
                    dict(
                        id=resp_data["result"]["majorResponsibilities"][1]["id"],
                        title="Another Responsibility",
                        description="Another Description",
                    ),
                ],
            ),
        )

        # check that major_resp_2 is deleted
        assert not MajorResponsibilities.objects.filter(id=major_resp_2.id).exists()
