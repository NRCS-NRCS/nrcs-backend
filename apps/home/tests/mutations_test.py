from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase

from apps.home.factories import HighlightFactory

# TODO: Add tests for action links and image uploads


class TestHighlightMutation(TestCase):
    class Mutation:
        CREATE_HIGHLIGHT = """
          mutation createHighlight($data: HighlightCreateInput!) {
            createHighlight(data: $data) {
                ... on OperationInfo {
                  __typename
                    messages {
                        code
                        field
                        kind
                        message
                    }
                }
                ... on HighlightTypeMutationResponseType {
                   errors
                   ok
                   result {
                     id
                     heading
                     description
                     expiryDate
                     actionLinks {
                        label
                        url
                     }
                   }
                }
            }
          }
        """
        UPDATE_HIGHLIGHT = """
        mutation updateHighlight($pk: ID!, $data: HighlightUpdateInput!) {
            updateHighlight(data: $data, pk: $pk) {
                ... on OperationInfo {
                    __typename
                    messages {
                        code
                        field
                        kind
                        message
                    }
                }
                ... on HighlightTypeMutationResponseType {
                    errors
                    ok
                    result {
                         id
                         heading
                         description
                         expiryDate
                         actionLinks {
                            label
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

    def test_create_highlight(self):
        data = {
            "heading": "New Highlight",
            "description": "This is a new highlight.",
            "expiryDate": "2024-12-31",
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_HIGHLIGHT,
            variables={
                "data": data,
            },
        )
        resp_data = content["data"]["createHighlight"]
        assert resp_data["errors"] is None, content
        assert resp_data == self.g_mutation_response(
            ok=True,
            result={
                "id": resp_data["result"]["id"],
                "heading": data["heading"],
                "description": data["description"],
                "expiryDate": data["expiryDate"],
                "actionLinks": [],
            },
        ), content

    def test_update_highlight(self):
        highlight = HighlightFactory.create(
            heading="Old Highlight",
            description="This is an old highlight.",
            expiry_date="2024-06-30",
        )
        data = {
            "heading": "Updated Highlight",
            "description": "This is an updated highlight.",
            "expiryDate": "2025-01-31",
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_HIGHLIGHT,
            variables={
                "pk": str(highlight.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateHighlight"]
        assert resp_data["errors"] is None, content
        assert resp_data == self.g_mutation_response(
            ok=True,
            result={
                "id": str(highlight.id),
                "heading": data["heading"],
                "description": data["description"],
                "expiryDate": data["expiryDate"],
                "actionLinks": [],
            },
        ), content
