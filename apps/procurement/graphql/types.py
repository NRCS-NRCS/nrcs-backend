import strawberry
import strawberry_django

from apps.procurement.models import Procurement
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Procurement)
class ProcurementType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    file: DjangoFileType
    published_date: strawberry.auto
    expiry_date: strawberry.auto
