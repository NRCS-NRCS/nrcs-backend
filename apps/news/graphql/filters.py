import strawberry
import strawberry_django

from apps.news.models import News


@strawberry_django.filters.filter(News, lookups=True)
class NewsFilter:
    name: str | None = strawberry.UNSET
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: int | None = strawberry.UNSET
    status: int | None = strawberry.UNSET
