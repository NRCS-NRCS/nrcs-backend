import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.partner.factories import PartnerFactory
from apps.partner.models import PartnerScopeEnum
from apps.strategic.factories import UserFactory
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
                "image": file,
            },
            map={
                "image": ["variables.data.image"],
            },
            **kwargs,
        )


class TestPartnerMutation(TestCase):
    class Mutation:
        CREATE_PARTNER = """
          mutation createPartner($data: PartnerCreateInput!) {
              createPartner(data: $data) {
                  ... on PartnerTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          scope
                          createdBy {
                            id
                          }
                          image {
                            url
                          }
                       }
                  }
              }
          }
        """

        UPDATE_PARTNER = """
            mutation updatePartner($pk: ID!, $data: PartnerUpdateInput!) {
                updatePartner(data: $data, pk: $pk) {
                    ... on PartnerTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         scope
                         image {
                           url
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

    def test_create_partner(self):
        data = {
            "title": "New Partner",
            "scope": self.genum(PartnerScopeEnum.LOCAL),
        }

        self.force_login(self.user)
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.CREATE_PARTNER,
            resource_data=data,
        )

        resp_data = content["data"]["createPartner"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            errors=None,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                scope=data["scope"],
                createdBy=dict(
                    id=self.gID(self.user.id),
                ),
                image=dict(
                    url=resp_data["result"]["image"]["url"],
                ),
            ),
        ), content

    def test_update_partner(self):
        partner = PartnerFactory.create(
            title="Initial Title",
            scope=PartnerScopeEnum.LOCAL,
        )

        data = {
            "title": "Updated Partner Title",
            "scope": self.genum(PartnerScopeEnum.GLOBAL),
        }

        self.force_login(self.user)
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_PARTNER,
            pk=self.gID(partner.id),
            resource_data=data,
        )
        resp_data = content["data"]["updatePartner"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(partner.id),
                title=data["title"],
                scope=data["scope"],
                image=dict(
                    url=resp_data["result"]["image"]["url"],
                ),
            ),
        ), content

        # Update with image
        data_with_image = {
            "title": "Updated Partner With Image",
            "scope": self.genum(PartnerScopeEnum.GLOBAL),
        }
        content = graphql_file_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_PARTNER,
            pk=self.gID(partner.id),
            resource_data=data_with_image,
        )
        resp_data = content["data"]["updatePartner"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(partner.id),
                title=data_with_image["title"],
                scope=data_with_image["scope"],
                image=dict(
                    url=resp_data["result"]["image"]["url"],
                ),
            ),
        ), content
