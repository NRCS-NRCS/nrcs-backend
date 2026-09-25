import strawberry
import strawberry_django

from apps.procurement.models import Procurement


@strawberry_django.order_type(Procurement)
class ProcurementOrder:
    id: strawberry.auto
