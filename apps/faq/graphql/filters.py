import strawberry
import strawberry_django

from apps.faq.models import Faq


@strawberry_django.filters.filter(Faq, lookups=True)
class FaqFilter:
    id: strawberry.ID
    order_index: strawberry.auto
