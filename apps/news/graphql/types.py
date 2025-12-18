import strawberry
import strawberry_django

from apps.news.models import News
from utils.graphql.types import DjangoFileType


@strawberry_django.type(News)
class NewsType:
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType | None
    content: str
    published_date: strawberry.auto
    directive: strawberry.auto
    slug: strawberry.auto
    cover_image: DjangoFileType | None
    is_notice: strawberry.auto
