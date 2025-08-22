import strawberry
import strawberry_django

from apps.blog.models import Blog
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Blog)
class BlogType:
    id: strawberry.ID
    title: strawberry.auto
    published_date: strawberry.auto
    author: strawberry.auto
    content: str
    cover_image: DjangoFileType | None
    featured: strawberry.auto
    status: strawberry.auto
    slug: strawberry.auto
    department: strawberry.auto
    directive: strawberry.auto
    work: strawberry.auto
