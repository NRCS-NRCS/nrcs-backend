import strawberry
import strawberry_django

from apps.strategic.models import MajorResponsibilities, StrategicDirectives
from utils.graphql.types import DjangoFileType


@strawberry_django.type(StrategicDirectives)
class StrategicDirectivesType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    cover_image: DjangoFileType | None
    slug: strawberry.auto
    major_responsibilities: list["MajorResponsibilitiesType"] = strawberry_django.field()


@strawberry_django.type(MajorResponsibilities)
class MajorResponsibilitiesType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    directive: strawberry.auto
    slug: strawberry.auto
