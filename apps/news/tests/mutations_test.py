from apps.common.models import StatusEnum
from apps.news.factories import NewsFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestNewsMutation(TestCase):
    class Mutation:
        CREATE_NEWS = """
          mutation createNews($data: NewsCreateInput!) {
            createNews(data: $data) {
                ... on OperationInfo {
                  __typename
                    messages {
                        code
                        field
                        kind
                        message
                    }
                }
                ... on NewsTypeMutationResponseType {
                   errors
                   ok
                   result {
                     id
                     title
                     content
                     publishedDate
                     slug
                     status
                     directive {
                        id
                     }
                   }
                }
            }
          }
        """
        UPDATE_NEWS = """
        mutation updateNews($pk: ID!, $data: NewsUpdateInput!) {
            updateNews(data: $data, pk: $pk) {
                ... on OperationInfo {
                    __typename
                    messages {
                        code
                        field
                        kind
                        message
                    }
                }
                ... on NewsTypeMutationResponseType {
                    errors
                    ok
                    result {
                         id
                         title
                         content
                         publishedDate
                         slug
                         status
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
        cls.user = UserFactory.create(username="nrcs-test", is_staff=True)

    def test_create_news(self):
        strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive",
            description="Something",
        )
        data = {
            "title": "New News Title",
            "content": "This is the content of the news.",
            "publishedDate": "2024-10-01",
            "directive": str(strategic_directive.id),
            "status": self.genum(StatusEnum.DRAFT),
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_NEWS,
            variables={"data": data},
        )

        resp_data = content["data"]["createNews"]
        assert resp_data["errors"] is None, content

        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                content=data["content"],
                publishedDate=data["publishedDate"],
                slug=resp_data["result"]["slug"],
                status=data["status"],
                directive=dict(
                    id=str(strategic_directive.id),
                ),
            ),
        ), content

    def test_create_news_without_directive(self):
        # directive is nullable on the model, so it can be left out entirely.
        data = {
            "title": "News Without A Directive",
            "content": "This is the content of the news.",
            "publishedDate": "2024-10-01",
            "status": self.genum(StatusEnum.DRAFT),
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_NEWS,
            variables={"data": data},
        )

        resp_data = content["data"]["createNews"]
        assert resp_data["errors"] is None, content
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                content=data["content"],
                publishedDate=data["publishedDate"],
                slug=resp_data["result"]["slug"],
                status=data["status"],
                directive=None,
            ),
        ), content

    def test_update_news(self):
        news_instance = NewsFactory.create(
            title="Old News Title",
            content="This is the old content of the news.",
            published_date="2024-05-01",
            status=StatusEnum.DRAFT,
            directive=StrategicDirectivesFactory.create(
                title="Old Directive",
                description="Old Description",
            ),
        )
        new_strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive",
            description="Something",
        )
        data = {
            "title": "Updated News Title",
            "content": "This is the updated content of the news.",
            "publishedDate": "2024-11-01",
            "status": self.genum(StatusEnum.PUBLISHED),
            "directive": str(new_strategic_directive.id),
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_NEWS,
            variables={
                "pk": str(news_instance.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateNews"]
        assert resp_data["errors"] is None, content
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(news_instance.id),
                title=data["title"],
                content=data["content"],
                publishedDate=data["publishedDate"],
                slug=news_instance.slug,
                status=data["status"],
                directive=dict(
                    id=str(new_strategic_directive.id),
                ),
            ),
        ), content
