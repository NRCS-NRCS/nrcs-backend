import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.faq.models import Faq


@strawberry_django.type(Faq)
class FaqType(UserResourceTypeMixin):
    id: strawberry.ID
    question: strawberry.auto
    answer: strawberry.auto
    order_index: strawberry.auto
