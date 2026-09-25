import strawberry
import strawberry_django

from apps.cec_member.models import CecMember
from apps.common.graphql.types import UserResourceTypeMixin
from utils.graphql.types import DjangoFileType


@strawberry_django.type(CecMember)
class CecMemberType(UserResourceTypeMixin):
    id: strawberry.ID
    name: strawberry.auto
    member_type: strawberry.auto
    designation: strawberry.auto
    email: strawberry.auto
    secondary_email: strawberry.auto
    address: strawberry.auto
    contact_number: strawberry.auto
    photo: DjangoFileType | None
    order_index: strawberry.auto
    is_active: strawberry.auto
