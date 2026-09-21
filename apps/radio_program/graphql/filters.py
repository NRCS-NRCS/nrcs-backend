import strawberry
import strawberry_django
from django.db.models import Q

from apps.radio_program.models import RadioProgram, RadioProgramTypeEnum


@strawberry_django.filters.filter(RadioProgram, lookups=True)
class RadioProgramFilter:
    published_date: strawberry.auto
    id: strawberry.ID | None = strawberry.UNSET
    title: str | None = strawberry.UNSET
    type: RadioProgramTypeEnum | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
