import strawberry
import strawberry_django

from apps.radio_program.models import RadioProgram


@strawberry_django.filters.filter(RadioProgram, lookups=True)
class RadioProgramFilter:
    id: strawberry.ID
    title: str
    published_date: strawberry.auto
