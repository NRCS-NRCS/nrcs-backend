import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.partner.models import Partner
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Partner)
class PartnerType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    scope: strawberry.auto
    image: DjangoFileType | None
