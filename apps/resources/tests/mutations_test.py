from django.core.files.uploadedfile import SimpleUploadedFile

from apps.resources.factories import ResourceFactory
from apps.resources.models import Resource, ResourceTypeEnum
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


def generate_test_image_file():
    return SimpleUploadedFile(
        name="test_image.jpq",
        content=b"Fake Image binary content",
        content_type="image/jpeg",
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

    with generate_test_image_file() as file:
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


class TestResourceMutation(TestCase):
    class Mutation:
        CREATE_RESOURCE = """
          mutation createResource($data: ResourceCreateInput!) {
              createResource(data: $data) {
                  ... on ResourceTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          content
                          publishedDate
                          slug
                          type
                          directive {
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

        UPDATE_RESOURCE = """
            mutation updateResource($pk: ID!, $data: ResourceUpdateInput!) {
                updateResource(data: $data, pk: $pk) {
                    ... on ResourceTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          content
                          publishedDate
                          slug
                          type
                          directive {
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

    def test_create_resource(self):
        new_strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive Two",
            description="Something New",
        )
        data = {
            "title": "New Resource",
            "content": "This is the content of the new resource.",
            "publishedDate": "2024-01-01",
            "type": self.genum(ResourceTypeEnum.REPORT),
            "directive": str(new_strategic_directive.pk),
        }

        self.force_login(self.user)
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.CREATE_RESOURCE,
            resource_data=data,
        )

        resp_data = content["data"]["createResource"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            errors=None,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                content=data["content"],
                publishedDate=data["publishedDate"],
                slug=resp_data["result"]["slug"],
                type=data["type"],
                directive=dict(
                    id=self.gID(new_strategic_directive.id),
                ),
                createdBy=dict(
                    id=self.gID(self.user.id),
                ),
            ),
        ), content

        # Check the image file is saved correctly
        resource_id = resp_data["result"]["id"]
        resource = Resource.objects.get(id=self.gID(resource_id))
        assert resource.file, "File should be saved and not empty"

    def test_update_resource(self):
        resource = ResourceFactory.create(
            title="Initial Title",
            published_date="2024-01-01",
            content="Initial Content",
            directive=StrategicDirectivesFactory.create(
                title="Strategic Directive",
                description="Something New",
            ),
        )
        new_strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive Two",
            description="Something New",
        )

        data = {
            "title": "Updated Resource Title",
            "publishedDate": "2024-02-01",
            "content": "Updated content of the resource.",
            "type": self.genum(ResourceTypeEnum.REPORT),
            "directive": str(new_strategic_directive.pk),
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_RESOURCE,
            variables={
                "pk": self.gID(resource.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateResource"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(resource.id),
                title=data["title"],
                slug=resp_data["result"]["slug"],
                directive=dict(
                    id=self.gID(new_strategic_directive.id),
                ),
                content=data["content"],
                type=data["type"],
                publishedDate=data["publishedDate"],
            ),
        ), content

        # Update with new file
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_RESOURCE,
            pk=self.gID(resource.id),
            resource_data=data,
        )
        resp_data = content["data"]["updateResource"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(resource.id),
                title=data["title"],
                content=data["content"],
                slug=resp_data["result"]["slug"],
                type=data["type"],
                publishedDate=data["publishedDate"],
                directive=dict(
                    id=self.gID(new_strategic_directive.id),
                ),
            ),
        ), content

        # Check THE file should not be empty
        resource.refresh_from_db()
        assert resource.file, "File should be updated and not empty"
