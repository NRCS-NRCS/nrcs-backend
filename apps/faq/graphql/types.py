import strawberry
import strawberry_django

from apps.faq.models import Faq


@strawberry_django.type(Faq)
class FaqType:
    id: strawberry.ID
    question: strawberry.auto
    answer: strawberry.auto
    order_index: strawberry.auto
