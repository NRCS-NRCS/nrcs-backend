import strawberry
import strawberry_django

from apps.faq.models import Faq


@strawberry_django.ordering.order(Faq)
class FaqOrder:
    id: strawberry.auto
    order_index: strawberry.auto
