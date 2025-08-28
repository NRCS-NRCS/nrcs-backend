import strawberry
import strawberry_django

from apps.common.models import StatusEnum
from apps.news.models import News
from apps.strategic.graphql.types import StrategicDirectivesType


@strawberry_django.filters.filter(News, lookups=True)
class NewsFilter:
    name: str | None = strawberry.UNSET
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: StrategicDirectivesType | None = strawberry.UNSET
    status: StatusEnum | None = strawberry.UNSET
