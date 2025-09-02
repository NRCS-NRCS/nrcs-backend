from apps.blog.factories import BlogFactory
from apps.common.models import StatusEnum
from apps.department.factories import DepartmentFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestBlogQuery(TestCase):
    class Query:
        BLOG = """
          query blogs($order: BlogOrder) {
            blogs(order: $order) {
            author
            content
            coverImage {
              name
              size
              url
            }
            department {
              pk
            }
            directive {
              pk
            }
            featured
            id
            publishedDate
            slug
            status
            title
          }
        }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_blog_query(self):
        def _query():
            return self.query_check(
                self.Query.BLOG,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        blog_items = [
            BlogFactory.create(
                title="Blog",
                content="Something",
                author="Author",
                featured=True,
                status=StatusEnum.PUBLISHED,
                slug="blog",
                department=DepartmentFactory.create(
                    title="Department",
                ),
                published_date="2023-01-01",
                directive=None,
                cover_image=None,
            ),
            BlogFactory.create(
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
                directive=None,
                cover_image=None,
            ),
        ]

        content = _query()
        assert content["data"] == {
            "blogs": [
                dict(
                    id=self.gID(blog.id),
                    title=blog.title,
                    slug=blog.slug,
                    department={
                        "pk": self.gID(blog.department.id),
                    },
                    publishedDate=blog.published_date,
                    status=self.genum(blog.status),
                    featured=blog.featured,
                    author=blog.author,
                    content=blog.content,
                    directive=None,
                    coverImage=None,
                )
                for blog in blog_items
            ],
        }, content
