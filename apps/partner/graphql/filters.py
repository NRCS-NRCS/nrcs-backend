import strawberry
import strawberry_django
from django.db.models import Q

from apps.partner.models import Partner


@strawberry_django.filters.filter(Partner, lookups=True)
class PartnerFilter:
    scope: strawberry.auto

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
