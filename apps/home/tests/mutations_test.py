from django.core.files.uploadedfile import SimpleUploadedFile

from apps.home.factories import HighlightFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


def generate_test_image_file():
    return SimpleUploadedFile(
        name="test_image.jpq",
        content=b"Fake Image binary content",
        content_type="image/jpeg",
    )


def highlight_mutation_with_image(
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
                     isActive
                     actionLinks {
                        label
                        url
                     }
                     image {
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
                         isActive
                         actionLinks {
                             id
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
            "isActive": False,
            "actionLinks": [
                {
                    "label": "Learn More",
                    "url": "https://example.com/learn-more",
                },
                {
                    "label": "Get Started",
                    "url": "https://example.com/get-started",
                },
            ],
        }

        self.force_login(self.user)
        content = highlight_mutation_with_image(
            query_check_func=self.query_check,
            query=self.Mutation.CREATE_HIGHLIGHT,
            resource_data=data,
        )

        resp_data = content["data"]["createHighlight"]
        assert resp_data["errors"] is None, content
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=resp_data["result"]["id"],
                heading=data["heading"],
                description=data["description"],
                isActive=data["isActive"],
                image=dict(
                    url=resp_data["result"]["image"]["url"],
                ),
                actionLinks=data["actionLinks"],
            ),
        ), content

    def test_update_highlight(self):
        highlight = HighlightFactory.create(
            heading="Old Highlight",
            description="This is an old highlight.",
            is_active=False,
        )
        data = {
            "heading": "Updated Highlight",
            "description": "This is an updated highlight.",
            "isActive": True,
            "actionLinks": [
                {
                    "create": {
                        "label": "Updated Link",
                        "url": "https://example.com/updated-link",
                    },
                },
                {
                    "create": {
                        "label": "Another Link",
                        "url": "https://example.com/another-link",
                    },
                },
            ],
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
            result=dict(
                id=self.gID(highlight.id),
                heading=data["heading"],
                description=data["description"],
                isActive=data["isActive"],
                actionLinks=[
                    dict(
                        id=resp_data["result"]["actionLinks"][0]["id"],
                        label="Updated Link",
                        url="https://example.com/updated-link",
                    ),
                    dict(
                        id=resp_data["result"]["actionLinks"][1]["id"],
                        label="Another Link",
                        url="https://example.com/another-link",
                    ),
                ],
            ),
        ), content

        data = {
            "heading": "Updated Highlight with Image",
            "description": "This is an updated highlight with image.",
            "isActive": True,
            "actionLinks": [
                {
                    "create": {
                        "label": "Updated Link",
                        "url": "https://example.com/updated-link",
                    },
                },
                {
                    "update": {
                        "id": resp_data["result"]["actionLinks"][1]["id"],
                        "label": "Another Link",
                        "url": "https://example.com/another-link",
                    },
                },
                {
                    "delete": {
                        "id": resp_data["result"]["actionLinks"][0]["id"],
                    },
                },
            ],
        }

        # Update with image
        content = highlight_mutation_with_image(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_HIGHLIGHT,
            pk=self.gID(highlight.id),
            resource_data=data,
        )
        update_resp_data = content["data"]["updateHighlight"]
        assert update_resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(highlight.id),
                heading=data["heading"],
                description=data["description"],
                isActive=data["isActive"],
                actionLinks=[
                    dict(
                        id=update_resp_data["result"]["actionLinks"][0]["id"],
                        label=data["actionLinks"][1]["update"]["label"],
                        url=data["actionLinks"][1]["update"]["url"],
                    ),
                    dict(
                        id=update_resp_data["result"]["actionLinks"][1]["id"],
                        label=data["actionLinks"][0]["create"]["label"],
                        url=data["actionLinks"][0]["create"]["url"],
                    ),
                ],
            ),
        ), content

        # Check if deleted or not
        highlight.refresh_from_db()
        action_link_ids = [str(link.id) for link in highlight.action_links.all()]
        assert data["actionLinks"][2]["delete"]["id"] not in action_link_ids, "Action link should be deleted"
