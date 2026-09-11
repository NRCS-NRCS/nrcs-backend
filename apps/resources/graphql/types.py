import strawberry
import strawberry_django
from strawberry.types import Info

from apps.common.graphql.types import UserResourceTypeMixin
from apps.resources.models import Resource
from apps.strategic.graphql.types import StrategicDirectivesType
from utils.graphql.types import DjangoFileType, markdown_with_absolute_media


@strawberry_django.type(Resource)
class ResourceType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType
    published_date: strawberry.auto
    directive_id: strawberry.ID
    directive: StrategicDirectivesType
    slug: strawberry.auto
    cover_image: DjangoFileType | None
    type: strawberry.auto

    @strawberry_django.field(only=["content"])
    def content(self, info: Info, root: strawberry.Parent[Resource]) -> str:
        return markdown_with_absolute_media(root.content, info)
