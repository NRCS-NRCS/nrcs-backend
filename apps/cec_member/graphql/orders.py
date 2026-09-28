import strawberry
import strawberry_django

from apps.cec_member.models import CecMember


@strawberry_django.order_type(CecMember)
class CecMemberOrder:
    id: strawberry.auto
    order_index: strawberry.auto
