import strawberry
import strawberry_django

from apps.partner.models import Partner


@strawberry_django.ordering.order(Partner)
class PartnerOrder:
    id: strawberry.auto
    scope: strawberry.auto
