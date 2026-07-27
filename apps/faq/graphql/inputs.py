import enum

import strawberry
import strawberry_django

from apps.faq.models import Faq


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.input(Faq)
class FaqCreateInput:
    question: strawberry.auto
    answer: strawberry.auto


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.partial(Faq)
class FaqUpdateInput:
    question: strawberry.auto
    answer: strawberry.auto
    order_index: strawberry.auto


@strawberry_django.input(Faq)
class FaqDeleteInput:
    id: strawberry.ID


@strawberry.enum
class FaqReorderPosition(enum.Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


@strawberry.input
class FaqReorderInput:
    # A single move: place `moved_id` immediately before/after `target_id`.
    # The server owns the full ordering, so the client only needs the dragged
    # item and one adjacent anchor from the page it can see — no need to send
    # every id, which is what makes this pagination-safe.
    moved_id: strawberry.ID
    target_id: strawberry.ID
    position: FaqReorderPosition
