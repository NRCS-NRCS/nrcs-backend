import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.news.models import News
from apps.strategic.graphql.types import StrategicDirectivesType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(News)
class NewsType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType | None
    content: str
    status: strawberry.auto
    published_date: strawberry.auto
    directive_id: strawberry.auto
    directive: StrategicDirectivesType | None
    slug: strawberry.auto
    cover_image: DjangoFileType | None
