import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.home.graphql.inputs import (
    HighlightCreateInput,
    HighlightDeleteInput,
    HighlightUpdateInput,
)
from apps.home.graphql.types import HighlightType
from apps.home.models import ActionLink, Highlight
from apps.home.serializers import HighlightSerializer
from main.graphql.context import Info
from utils.graphql.common import DataclassInstance
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import CudInput, MutationResponseType


@strawberry.type
class Mutation:
    # --- Highlight Mutations ---
    delete_highlight: HighlightType = strawberry_django.mutations.delete(
        HighlightDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_highlight(self, info: Info, data: HighlightCreateInput) -> MutationResponseType[HighlightType]:
        return await ModelMutation(HighlightSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_highlight(
        self,
        info: Info,
        data: HighlightUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[HighlightType]:
        highlight = await Highlight.objects.aget(pk=pk)

        def transformer(obj: DataclassInstance):
            if not isinstance(obj, CudInput):
                return (False, obj)

            if obj.delete is not None and obj.delete != strawberry.UNSET:
                return (True, None)

            if obj.create is not None and obj.create != strawberry.UNSET:
                return (True, obj.create)

            if obj.update is not None and obj.update != strawberry.UNSET:
                return (True, obj.update)

            return (False, obj)

        for action_link in data.action_links or []:
            if action_link.delete is not None and action_link.delete != strawberry.UNSET:
                await ActionLink.objects.filter(id=action_link.delete.id).adelete()
                continue

        return await ModelMutation(HighlightSerializer).handle_update_mutation(
            data,
            info,
            highlight,
            None,
            transformer,
        )
