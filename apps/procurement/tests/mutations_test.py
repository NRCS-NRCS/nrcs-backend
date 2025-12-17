from apps.procurement.factories import ProcurementFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestProcurementMutation(TestCase):
    class Mutation:
        CREATE_PARTNER = """
          mutation createProcurement($data: ProcurementCreateInput!) {
              createProcurement(data: $data) {
                  ... on ProcurementTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          description
                          publishedDate
                          expiryDate
                          createdBy {
                            id
                          }
                       }
                  }
              }
          }
        """

        UPDATE_PARTNER = """
            mutation updateProcurement($pk: ID!, $data: ProcurementUpdateInput!) {
                updateProcurement(data: $data, pk: $pk) {
                    ... on ProcurementTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         description
                         publishedDate
                         expiryDate
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
            "title": "New Procurement",
            "description": "This is a new procurement description.",
            "publishedDate": "2024-07-01",
            "expiryDate": "2024-12-31",
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_PARTNER,
            variables={
                "data": data,
            },
        )
        resp_data = content["data"]["createProcurement"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            errors=None,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                description=data["description"],
                publishedDate=data["publishedDate"],
                expiryDate=data["expiryDate"],
                createdBy=dict(
                    id=self.gID(self.user.id),
                ),
            ),
        ), content

    def test_update_partner(self):
        partner = ProcurementFactory.create(
            title="Initial Title",
            description="Initial Description",
            published_date="2024-01-01",
            expiry_date="2024-06-30",
        )

        data = {
            "title": "Updated Procurement Title",
            "description": "Updated Description",
            "publishedDate": "2024-08-01",
            "expiryDate": "2025-01-31",
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_PARTNER,
            variables={
                "pk": self.gID(partner.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateProcurement"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(partner.id),
                title=data["title"],
                description=data["description"],
                publishedDate=data["publishedDate"],
                expiryDate=data["expiryDate"],
            ),
        ), content
