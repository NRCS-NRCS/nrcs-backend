import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.procurement.models import Procurement


@strawberry_django.input(Procurement)
class ProcurementCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    published_date: strawberry.auto
    expiry_date: strawberry.auto
    file: Upload | None


@strawberry_django.partial(Procurement)
class ProcurementUpdateInput:
    title: strawberry.auto
    description: strawberry.auto
    published_date: strawberry.auto
    expiry_date: strawberry.auto
    file: Upload | None


@strawberry_django.input(Procurement)
class ProcurementDeleteInput:
    id: strawberry.ID
