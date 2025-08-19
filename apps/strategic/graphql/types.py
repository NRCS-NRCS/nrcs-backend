import strawberry
import strawberry_django

from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@strawberry_django.type(StrategicDirectives)
class StrategicDirectivesType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    slug: strawberry.auto


@strawberry_django.type(MajorResponsibilities)
class MajorResponsibilitiesType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    directive: strawberry.auto
    slug: strawberry.auto
