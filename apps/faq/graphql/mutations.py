import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from django.db import transaction
from strawberry_django.permissions import IsStaff

from apps.faq.graphql.inputs import (
    FaqCreateInput,
    FaqDeleteInput,
    FaqReorderInput,
    FaqReorderPosition,
    FaqUpdateInput,
)
from apps.faq.graphql.types import FaqType
from apps.faq.models import Faq
from apps.faq.serializers import FAQSerializer
from main.graphql.context import Info
from utils.graphql.drf import _CustomErrorType
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@sync_to_async
def _reorder_faq(data: FaqReorderInput) -> MutationResponseType[list[FaqType]]:
    # Move-based reorder: the client sends only the dragged FAQ (`moved_id`) and
    # one adjacent anchor (`target_id`) plus whether it lands before/after it.
    # The server owns the full ordering, loads every FAQ itself and renumbers,
    # so this works regardless of how the client is paginated — it never needs
    # the complete id list.
    moved_id = str(data.moved_id)
    target_id = str(data.target_id)

    if moved_id == target_id:
        return MutationResponseType(
            ok=False,
            errors=_CustomErrorType.generate_message("An FAQ cannot be reordered relative to itself."),
        )

    with transaction.atomic():
        faqs = list(Faq.objects.select_for_update().order_by("order_index", "id"))
        ids = {str(faq.id) for faq in faqs}
        if moved_id not in ids or target_id not in ids:
            return MutationResponseType(
                ok=False,
                errors=_CustomErrorType.generate_message(
                    "The provided FAQ ids do not match the existing FAQs. Please refresh and try again.",
                ),
            )

        moved = next(faq for faq in faqs if str(faq.id) == moved_id)
        remaining = [faq for faq in faqs if str(faq.id) != moved_id]
        target_index = next(index for index, faq in enumerate(remaining) if str(faq.id) == target_id)
        insert_at = target_index + 1 if data.position == FaqReorderPosition.AFTER else target_index
        remaining.insert(insert_at, moved)

        for index, faq in enumerate(remaining):
            faq.order_index = index
        Faq.objects.bulk_update(remaining, ["order_index"])
        result = list(Faq.objects.order_by("order_index", "id"))

    return MutationResponseType(result=result)  # type: ignore[reportReturnType]


@strawberry.type
class Mutation:
    delete_faq: FaqType = strawberry_django.mutations.delete(
        FaqDeleteInput,
        key_attr="pk",
        extensions=[IsStaff()],
    )

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def create_faq(self, info: Info, data: FaqCreateInput) -> MutationResponseType[FaqType]:
        return await ModelMutation(FAQSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def update_faq(
        self,
        info: Info,
        data: FaqUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[FaqType]:
        faq = await Faq.objects.aget(pk=pk)
        return await ModelMutation(FAQSerializer).handle_update_mutation(data, info, faq)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def reorder_faq(
        self,
        info: Info,
        data: FaqReorderInput,
    ) -> MutationResponseType[list[FaqType]]:
        return await _reorder_faq(data)
