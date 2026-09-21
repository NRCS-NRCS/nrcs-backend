import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import MajorResponsibilitiesFilter, StrategicDirectivesFilter
from .orders import MajorResponsibilitiesOrder, StrategicDirectivesOrder
from .types import MajorResponsibilitiesType, StrategicDirectivesType


@strawberry.type
class Query:
    # --- Paginated
    strategic_directives: OffsetPaginated[StrategicDirectivesType] = strawberry_django.offset_paginated(
        order=StrategicDirectivesOrder,
        filters=StrategicDirectivesFilter,
    )
    strategic_directive: StrategicDirectivesType = strawberry_django.field()

    # --- Paginated
    major_responsibilities: OffsetPaginated[MajorResponsibilitiesType] = strawberry_django.offset_paginated(
        order=MajorResponsibilitiesOrder,
        filters=MajorResponsibilitiesFilter,
    )
    major_responsibility: MajorResponsibilitiesType = strawberry_django.field()
