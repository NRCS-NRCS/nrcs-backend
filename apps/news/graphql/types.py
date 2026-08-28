import strawberry
import strawberry_django
from strawberry.types import Info

from apps.news.models import News
from utils.graphql.types import DjangoFileType, markdown_with_absolute_media


@strawberry_django.type(News)
class NewsType:
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType | None
    published_date: strawberry.auto
    directive: strawberry.auto
    slug: strawberry.auto
    cover_image: DjangoFileType | None

    @strawberry_django.field(only=["content"])
    def content(self, info: Info, root: strawberry.Parent[News]) -> str:
        return markdown_with_absolute_media(root.content, info)
