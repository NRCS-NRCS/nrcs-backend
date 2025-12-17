import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.procurement.models import Procurement
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Procurement)
class ProcurementType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    file: DjangoFileType | None
    published_date: strawberry.auto
    expiry_date: strawberry.auto
