import strawberry
import strawberry_django
from django.db.models import Q

from apps.blog.models import Blog
from apps.common.models import StatusEnum


@strawberry_django.filters.filter(Blog, lookups=True)
class BlogFilter:
    id: strawberry.ID | None
    slug: strawberry.auto
    status: StatusEnum
    author: strawberry.auto
    featured: strawberry.auto
    directive: strawberry.ID | None = None
    search: str | None = strawberry.UNSET

    def filter_search(self, queryset, info, value):
        if not value or value is strawberry.UNSET:
            return queryset
        return queryset.filter(Q(title__icontains=value))
