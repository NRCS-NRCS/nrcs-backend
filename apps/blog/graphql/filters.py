import strawberry
import strawberry_django

from apps.blog.models import Blog
from apps.common.models import StatusEnum


@strawberry_django.filters.filter(Blog, lookups=True)
class BlogFilter:
    id: strawberry.ID
    slug: strawberry.auto
    status: StatusEnum
    author: strawberry.auto
    featured: strawberry.auto
