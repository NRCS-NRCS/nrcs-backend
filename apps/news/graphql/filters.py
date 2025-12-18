import strawberry
import strawberry_django

from apps.common.models import StatusEnum
from apps.news.models import News


@strawberry_django.filters.filter(News, lookups=True)
class NewsFilter:
    name: str | None = strawberry.UNSET
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: strawberry.ID | None = None
    status: StatusEnum | None = strawberry.UNSET
    is_notice: bool | None = strawberry.UNSET
