import strawberry
import strawberry_django

from apps.procurement.models import Procurement


@strawberry_django.ordering.order(Procurement)
class ProcurementOrder:
    id: strawberry.auto
