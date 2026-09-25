import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from django.db import transaction
from strawberry_django.permissions import IsStaff

from apps.cec_member.graphql.inputs import (
    CecMemberCreateInput,
    CecMemberDeleteInput,
    CecMemberReorderInput,
    CecMemberReorderPosition,
    CecMemberUpdateInput,
)
from apps.cec_member.graphql.types import CecMemberType
from apps.cec_member.models import CecMember
from apps.cec_member.serializers import CecMemberSerializer
from main.graphql.context import Info
from utils.graphql.drf import _CustomErrorType
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@sync_to_async
def _reorder_cec_member(data: CecMemberReorderInput) -> MutationResponseType[list[CecMemberType]]:
    # Move-based reorder, see _reorder_faq for the rationale.
    moved_id = str(data.moved_id)
    target_id = str(data.target_id)

    if moved_id == target_id:
        return MutationResponseType(
            ok=False,
            errors=_CustomErrorType.generate_message("A member cannot be reordered relative to itself."),
        )

    with transaction.atomic():
        members = list(CecMember.objects.select_for_update().order_by("order_index", "id"))
        ids = {str(member.id) for member in members}
        if moved_id not in ids or target_id not in ids:
            return MutationResponseType(
                ok=False,
                errors=_CustomErrorType.generate_message(
                    "The provided member ids do not match the existing members. Please refresh and try again.",
                ),
            )

        moved = next(member for member in members if str(member.id) == moved_id)
        remaining = [member for member in members if str(member.id) != moved_id]
        target_index = next(index for index, member in enumerate(remaining) if str(member.id) == target_id)
        insert_at = target_index + 1 if data.position == CecMemberReorderPosition.AFTER else target_index
        remaining.insert(insert_at, moved)

        for index, member in enumerate(remaining):
            member.order_index = index
        CecMember.objects.bulk_update(remaining, ["order_index"])
        result = list(CecMember.objects.order_by("order_index", "id"))

    return MutationResponseType(result=result)  # type: ignore[reportReturnType]


@strawberry.type
class Mutation:
    delete_cec_member: CecMemberType = strawberry_django.mutations.delete(
        CecMemberDeleteInput,
        key_attr="pk",
        extensions=[IsStaff()],
    )

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def create_cec_member(self, info: Info, data: CecMemberCreateInput) -> MutationResponseType[CecMemberType]:
        return await ModelMutation(CecMemberSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def update_cec_member(
        self,
        info: Info,
        data: CecMemberUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[CecMemberType]:
        member = await CecMember.objects.aget(pk=pk)
        return await ModelMutation(CecMemberSerializer).handle_update_mutation(data, info, member)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def reorder_cec_member(
        self,
        info: Info,
        data: CecMemberReorderInput,
    ) -> MutationResponseType[list[CecMemberType]]:
        return await _reorder_cec_member(data)
