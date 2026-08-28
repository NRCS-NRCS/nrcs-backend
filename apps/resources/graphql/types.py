import strawberry
import strawberry_django
from strawberry.types import Info

from apps.resources.models import Resource
from utils.graphql.types import DjangoFileType, markdown_with_absolute_media


@strawberry_django.type(Resource)
class ResourceType:
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType
    published_date: strawberry.auto
    directive: strawberry.auto
    slug: strawberry.auto
    cover_image: DjangoFileType | None
    type: strawberry.auto

    @strawberry_django.field(only=["content"])
    def content(self, info: Info, root: strawberry.Parent[Resource]) -> str:
        return markdown_with_absolute_media(root.content, info)
