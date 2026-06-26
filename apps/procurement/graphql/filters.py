import strawberry
import strawberry_django
from django.db.models import Q

from apps.procurement.models import Procurement


@strawberry_django.filters.filter(Procurement, lookups=True)
class ProcurementFilter:
    expiry_date: strawberry.auto
    published_date: strawberry.auto
    id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
