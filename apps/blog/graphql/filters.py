import strawberry
import strawberry_django
from django.db.models import Q

from apps.blog.models import Blog
from apps.common.models import StatusEnum


@strawberry_django.filters.filter(Blog, lookups=True)
class BlogFilter:
    id: strawberry.ID | None
    slug: strawberry.auto
    author: strawberry.auto
    featured: strawberry.auto
    status: StatusEnum | None = strawberry.UNSET
    directive: strawberry.ID | None = None

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
