import strawberry
import strawberry_django

from apps.radio_program.models import RadioProgram


@strawberry_django.filters.filter(RadioProgram, lookups=True)
class RadioProgramFilter:
    title: str | None = strawberry.UNSET
    published_date: str | None = strawberry.UNSET
