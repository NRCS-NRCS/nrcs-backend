import strawberry
import strawberry_django

from apps.partner.models import Partner
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Partner)
class PartnerType:
    id: strawberry.ID
    title: strawberry.auto
    scope: strawberry.auto
    image: DjangoFileType
