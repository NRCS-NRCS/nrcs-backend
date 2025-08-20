import strawberry
import strawberry_django

from apps.procurement.models import Procurement


@strawberry_django.filters.filter(Procurement, lookups=True)
class ProcurementFilter:
    id: strawberry.ID
    expiry_date: strawberry.auto
    published_date: strawberry.auto
