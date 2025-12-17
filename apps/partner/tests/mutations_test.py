from apps.partner.factories import PartnerFactory
from apps.partner.models import PartnerScopeEnum
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


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
        content = self.query_check(
            self.Mutation.CREATE_PARTNER,
            variables={
                "data": data,
            },
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
        content = self.query_check(
            self.Mutation.UPDATE_PARTNER,
            variables={
                "pk": self.gID(partner.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updatePartner"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(partner.id),
                title=data["title"],
                scope=data["scope"],
            ),
        ), content
