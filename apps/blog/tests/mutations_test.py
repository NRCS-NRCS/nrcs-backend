from apps.blog.factories import BlogFactory
from apps.blog.models import Blog
from apps.common.models import StatusEnum
from apps.department.factories import DepartmentFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestBlogMutation(TestCase):
    class Mutation:
        CREATE_BLOG = """
          mutation createBlog($data: BlogCreateInput!) {
            createBlog(data: $data) {
                ... on OperationInfo {
                  __typename
                  messages {
                    code
                    field
                    kind
                    message
                  }
                }
                ... on BlogTypeMutationResponseType {
                   errors
                   ok
                   result {
                     id
                     title
                     content
                     author
                     featured
                     status
                     slug
                     department {
                       id
                     }
                     directive {
                       id
                     }
                   }
                }
            }
          }
        """

        UPDATE_BLOG = """
            mutation updateBlog($pk: ID!, $data: BlogUpdateInput!) {
                updateBlog(data: $data, pk: $pk) {
                    ... on OperationInfo {
                      __typename
                      messages {
                        code
                        field
                        kind
                        message
                      }
                    }
                    ... on BlogTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         content
                         author
                         featured
                         status
                         slug
                         department {
                           id
                         }
                         directive {
                           id
                         }
                       }
                    }
                }
            }
        """

        DELETE_BLOG = """
            mutation deleteBlog($data: BlogDeleteInput!) {
                deleteBlog(data: $data) {
                    ... on OperationInfo {
                        __typename
                        messages {
                          code
                          field
                          kind
                          message
                        }
                    }
                    ... on BlogType{
                         id
                    }
                }
            }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_create_blog(self):
        strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
        )
        department = DepartmentFactory.create(
            title="Department One",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
            strategic_directive=strategic_directive,
        )

        data = {
            "title": "Blog Title",
            "publishedDate": "2024-01-01",
            "author": "Jane Smith",
            "content": "This is the content of the blog.",
            "featured": True,
            "status": self.genum(StatusEnum.PUBLISHED),
            "department": str(department.id),
            "directive": str(strategic_directive.id),
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_BLOG,
            variables={
                "data": data,
            },
        )
        resp_data = content["data"]["createBlog"]
        assert resp_data["errors"] is None, content

        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                content=data["content"],
                author=data["author"],
                featured=data["featured"],
                status=data["status"],
                slug=resp_data["result"]["slug"],
                department=dict(
                    id=self.gID(department.id),
                ),
                directive=dict(
                    id=self.gID(strategic_directive.id),
                ),
            ),
        ), content

        strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
        )
        department = DepartmentFactory.create(
            title="Department One",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
            strategic_directive=strategic_directive,
        )
        blog = BlogFactory.create(
            title="Original Blog Title",
            published_date="2024-01-01",
            author="Jane Smith",
            content="This is the original content of the blog.",
            featured=False,
            status=StatusEnum.DRAFT,
            department=department,
            directive=strategic_directive,
        )
        data = {
            "title": "Updated Blog Title",
            "publishedDate": "2024-02-01",
            "author": "John Doe",
            "content": "This is the updated content of the blog.",
            "featured": True,
            "status": self.genum(StatusEnum.PUBLISHED),
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_BLOG,
            variables={
                "pk": str(blog.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateBlog"]
        assert resp_data["errors"] is None, content

        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(blog.id),
                title=data["title"],
                content=data["content"],
                author=data["author"],
                featured=data["featured"],
                status=data["status"],
                slug=blog.slug,
                department=dict(
                    id=self.gID(department.id),
                ),
                directive=dict(
                    id=self.gID(strategic_directive.id),
                ),
            ),
        ), content

    def test_delete_blog(self):
        blog = BlogFactory.create(
            title="Blog One",
            content="Something",
            author="Author",
            featured=True,
            status=StatusEnum.DRAFT,
            slug="blog-one",
            department=DepartmentFactory.create(
                title="Department One",
            ),
            published_date="2023-01-01",
        )
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.DELETE_BLOG,
            variables={
                "data": {
                    "id": str(blog.id),
                },
            },
        )
        resp_data = content["data"]["deleteBlog"]
        assert resp_data["id"] == self.gID(blog.id), content
        assert not Blog.objects.filter(id=blog.id).exists(), content
