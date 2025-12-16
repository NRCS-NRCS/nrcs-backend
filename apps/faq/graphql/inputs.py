import strawberry
import strawberry_django

from apps.faq.models import Faq


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.input(Faq)
class FaqCreateInput:
    question: strawberry.auto
    answer: strawberry.auto
    order_index: strawberry.auto


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.partial(Faq)
class FaqUpdateInput:
    question: strawberry.auto
    answer: strawberry.auto
    order_index: strawberry.auto


@strawberry_django.input(Faq)
class FaqDeleteInput:
    id: strawberry.ID
