import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from django.db import transaction
from strawberry_django.permissions import IsStaff

from apps.faq.graphql.inputs import (
    FaqCreateInput,
    FaqDeleteInput,
    FaqReorderInput,
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
    # Client sends the complete ordered list of FAQ ids. The set must match
    # the existing FAQs exactly — reject (updating nothing) on any missing,
    # unknown or duplicate id so a stale client can't silently corrupt order.
    ordered_ids = [str(pk) for pk in data.ordered_ids]

    if len(ordered_ids) != len(set(ordered_ids)):
        return MutationResponseType(
            ok=False,
            errors=_CustomErrorType.generate_message("Duplicate FAQ ids in the provided order."),
        )

    existing_ids = {str(pk) for pk in Faq.objects.values_list("id", flat=True)}
    if set(ordered_ids) != existing_ids:
        return MutationResponseType(
            ok=False,
            errors=_CustomErrorType.generate_message(
                "The provided FAQ ids do not match the existing FAQs. Please refresh and try again.",
            ),
        )

    with transaction.atomic():
        faq_by_id = {str(faq.id): faq for faq in Faq.objects.select_for_update()}
        for index, pk in enumerate(ordered_ids):
            faq_by_id[pk].order_index = index
        Faq.objects.bulk_update(faq_by_id.values(), ["order_index"])
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
