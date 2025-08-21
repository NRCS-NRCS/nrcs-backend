import strawberry
import strawberry_django

from apps.partner.models import Partner


@strawberry_django.filters.filter(Partner, lookups=True)
class PartnerFilter:
    scope: strawberry.auto
