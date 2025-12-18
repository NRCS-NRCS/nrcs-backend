import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.strategic.models import MajorResponsibilities, StrategicDirectives
from utils.graphql.types import CudInput


@strawberry_django.input(MajorResponsibilities)
class MajorResponsibilitiesCreateInput:
    title: strawberry.auto
    description: strawberry.auto


@strawberry_django.partial(MajorResponsibilities)
class MajorResponsibilitiesUpdateInput:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto


@strawberry.input
class MajorResponsibilitiesInput(CudInput[MajorResponsibilitiesCreateInput, MajorResponsibilitiesUpdateInput]): ...


@strawberry_django.input(StrategicDirectives)
class StrategicDirectivesCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET
    major_responsibilities: list[MajorResponsibilitiesCreateInput] | None = strawberry.UNSET


@strawberry_django.partial(StrategicDirectives)
class StrategicDirectivesUpdateInput:
    title: strawberry.auto
    description: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET
    major_responsibilities: list[MajorResponsibilitiesInput] | None = strawberry.UNSET


@strawberry_django.input(StrategicDirectives)
class StrategicDirectivesDeleteInput:
    id: strawberry.ID
