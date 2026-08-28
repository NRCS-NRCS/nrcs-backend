import strawberry
import strawberry_django
from strawberry.types import Info

from apps.blog.models import Blog
from utils.graphql.types import DjangoFileType, markdown_with_absolute_media


@strawberry_django.type(Blog)
class BlogType:
    id: strawberry.ID
    title: strawberry.auto
    published_date: strawberry.auto
    author: strawberry.auto
    cover_image: DjangoFileType | None
    featured: strawberry.auto
    status: strawberry.auto
    slug: strawberry.auto
    department: strawberry.auto
    directive: strawberry.auto

    @strawberry_django.field(only=["content"])
    def content(self, info: Info, root: strawberry.Parent[Blog]) -> str:
        return markdown_with_absolute_media(root.content, info)
