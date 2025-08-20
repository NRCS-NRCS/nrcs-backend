import strawberry
import strawberry_django

from apps.department.graphql.orders import DepartmentOrder

from .filters import DepartmentFilter
from .types import DepartmentType


@strawberry.type
class Query:
    # all departments (no pagination)
    departments: list[DepartmentType] = strawberry_django.field(
        order=DepartmentOrder,
        filters=DepartmentFilter,
    )

    # single department (by pk by default)
    department: DepartmentType = strawberry_django.field()

    @staticmethod
    def departments_get_queryset(queryset, info):
        return queryset.prefetch_related("strategic_directive")

    @staticmethod
    def department_get_queryset(queryset, info):
        return queryset.select_related("strategic_directive")
