import strawberry
import strawberry_django

from apps.radio_program.models import RadioProgram, RadioProgramTypeEnum


@strawberry_django.filters.filter(RadioProgram, lookups=True)
class RadioProgramFilter:
    published_date: strawberry.auto
    id: strawberry.ID | None = strawberry.UNSET
    title: str | None = strawberry.UNSET
    type: RadioProgramTypeEnum | None = strawberry.UNSET
