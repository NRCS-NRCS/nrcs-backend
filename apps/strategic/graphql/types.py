import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.strategic.models import MajorResponsibilities, StrategicDirectives
from utils.graphql.types import DjangoFileType


@strawberry_django.type(MajorResponsibilities)
class MajorResponsibilitiesType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    directive: strawberry.auto
    slug: strawberry.auto


@strawberry_django.type(StrategicDirectives)
class StrategicDirectivesType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType | None
    slug: strawberry.auto
    major_responsibilities: list[MajorResponsibilitiesType]
