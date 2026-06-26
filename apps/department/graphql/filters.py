import strawberry
import strawberry_django
from django.db.models import Q

from apps.department.models import Department


@strawberry_django.filters.filter(Department, lookups=True)
class DepartmentFilter:
    id: strawberry.ID | None = strawberry.UNSET
    slug: strawberry.auto = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
