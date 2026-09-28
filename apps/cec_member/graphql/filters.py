import strawberry
import strawberry_django
from django.db.models import Q

from apps.cec_member.models import CecMember


@strawberry_django.filter_type(CecMember, lookups=True)
class CecMemberFilter:
    member_type: strawberry.auto
    is_active: strawberry.auto

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(name__icontains=value) | Q(designation__icontains=value)
