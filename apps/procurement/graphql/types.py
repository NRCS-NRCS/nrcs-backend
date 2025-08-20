import strawberry
import strawberry_django

from apps.procurement.models import Procurement


@strawberry_django.type(Procurement)
class ProcurementType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    file: strawberry.auto
    published_date: strawberry.auto
    expiry_date: strawberry.auto
