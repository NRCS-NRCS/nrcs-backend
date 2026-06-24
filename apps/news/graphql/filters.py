import strawberry
import strawberry_django
from django.db.models import Q

from apps.common.models import StatusEnum
from apps.news.models import News


@strawberry_django.filters.filter(News, lookups=True)
class NewsFilter:
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: strawberry.ID | None = None
    status: StatusEnum | None = strawberry.UNSET
    is_highlighted: bool | None = strawberry.UNSET
    search: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
