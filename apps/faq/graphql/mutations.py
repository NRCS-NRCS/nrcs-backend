import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.faq.graphql.inputs import FaqCreateInput, FaqDeleteInput, FaqUpdateInput
from apps.faq.graphql.types import FaqType
from apps.faq.models import Faq
from apps.faq.serializers import FAQSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_faq: FaqType = strawberry_django.mutations.delete(
        FaqDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_faq(self, info: Info, data: FaqCreateInput) -> MutationResponseType[FaqType]:
        return await ModelMutation(FAQSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_faq(
        self,
        info: Info,
        data: FaqUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[FaqType]:
        faq = await Faq.objects.aget(pk=pk)
        return await ModelMutation(FAQSerializer).handle_update_mutation(data, info, faq)
