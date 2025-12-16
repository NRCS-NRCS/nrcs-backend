import strawberry
import strawberry_django

from apps.news.models import News
from strawberry.file_uploads import Upload


@strawberry_django.input(News)
class NewsCreateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    slug: strawberry.auto
    status: strawberry.auto
    directive: strawberry.ID
    file: Upload | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET


@strawberry_django.partial(News)
class NewsUpdateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    status: strawberry.auto
    slug: strawberry.auto
    directive: strawberry.ID
    file: Upload | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET


@strawberry_django.input(News)
class NewsDeleteInput:
    id: strawberry.ID
