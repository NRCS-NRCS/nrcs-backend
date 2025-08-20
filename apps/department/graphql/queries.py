import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import DepartmentFilter
from .orders import DepartmentOrder
from .types import DepartmentType


@strawberry.type
class Query:
    department: OffsetPaginated[DepartmentType] = strawberry_django.offset_paginated(
        order=DepartmentOrder,
        filters=DepartmentFilter,
        extensions=[],
    )
