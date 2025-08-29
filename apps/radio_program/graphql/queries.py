import strawberry
import strawberry_django

from .filters import RadioProgramFilter
from .orders import RadioProgramOrder
from .types import RadioProgramType


@strawberry.type
class Query:
    radio_program: list[RadioProgramType] = strawberry_django.field(
        order=RadioProgramOrder,
        filters=RadioProgramFilter,
    )
