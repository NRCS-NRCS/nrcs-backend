import strawberry
import strawberry_django
from django.db.models import Q

from apps.faq.models import Faq


@strawberry_django.filters.filter(Faq, lookups=True)
class FaqFilter:
    id: strawberry.ID
    order_index: strawberry.auto
    search: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(question__icontains=value)
