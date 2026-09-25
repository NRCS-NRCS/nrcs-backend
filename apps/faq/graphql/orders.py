import strawberry
import strawberry_django

from apps.faq.models import Faq


@strawberry_django.order_type(Faq)
class FaqOrder:
    id: strawberry.auto
    order_index: strawberry.auto
