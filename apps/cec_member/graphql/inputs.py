import enum

import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.cec_member.models import CecMember


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.input(CecMember)
class CecMemberCreateInput:
    name: strawberry.auto
    member_type: strawberry.auto
    designation: strawberry.auto
    email: strawberry.auto
    secondary_email: strawberry.auto
    address: strawberry.auto
    contact_number: strawberry.auto
    photo: Upload | None
    is_active: strawberry.auto


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.partial(CecMember)
class CecMemberUpdateInput:
    name: strawberry.auto
    member_type: strawberry.auto
    designation: strawberry.auto
    email: strawberry.auto
    secondary_email: strawberry.auto
    address: strawberry.auto
    contact_number: strawberry.auto
    photo: Upload | None
    is_active: strawberry.auto


@strawberry_django.input(CecMember)
class CecMemberDeleteInput:
    id: strawberry.ID


@strawberry.enum
class CecMemberReorderPosition(enum.Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


@strawberry.input
class CecMemberReorderInput:
    # A single move: place `moved_id` immediately before/after `target_id`.
    # The server owns the full ordering (same approach as FaqReorderInput).
    moved_id: strawberry.ID
    target_id: strawberry.ID
    position: CecMemberReorderPosition
