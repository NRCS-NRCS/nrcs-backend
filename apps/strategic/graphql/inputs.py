import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@strawberry_django.input(StrategicDirectives)
class StrategicDirectivesCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET


@strawberry_django.partial(StrategicDirectives)
class StrategicDirectivesUpdateInput:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET


@strawberry_django.input(StrategicDirectives)
class StrategicDirectivesDeleteInput:
    id: strawberry.ID


@strawberry_django.input(MajorResponsibilities)
class MajorResponsibilitiesCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    directive: strawberry.ID


@strawberry_django.partial(MajorResponsibilities)
class MajorResponsibilitiesUpdateInput:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    directive: strawberry.ID


@strawberry_django.input(MajorResponsibilities)
class MajorResponsibilitiesDeleteInput:
    id: strawberry.ID
