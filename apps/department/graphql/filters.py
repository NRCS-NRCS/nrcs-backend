import strawberry
import strawberry_django

from apps.department.models import Department


@strawberry_django.filters.filter(Department, lookups=True)
class DepartmentFilter:
    id: strawberry.ID
    slug: strawberry.auto
