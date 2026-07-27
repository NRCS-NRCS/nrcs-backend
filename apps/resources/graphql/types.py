import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.resources.models import Resource
from apps.strategic.graphql.types import StrategicDirectivesType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Resource)
class ResourceType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType
    content: str
    published_date: strawberry.auto
    directive_id: strawberry.ID
    directive: StrategicDirectivesType
    slug: strawberry.auto
    cover_image: DjangoFileType | None
    type: strawberry.auto
