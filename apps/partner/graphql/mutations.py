import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.partner.graphql.inputs import PartnerCreateInput, PartnerDeleteInput, PartnerUpdateInput
from apps.partner.graphql.types import PartnerType
from apps.partner.models import Partner
from apps.partner.serializers import PartnerSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_partner: PartnerType = strawberry_django.mutations.delete(
        PartnerDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_partner(self, info: Info, data: PartnerCreateInput) -> MutationResponseType[PartnerType]:
        return await ModelMutation(PartnerSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_partner(
        self,
        info: Info,
        data: PartnerUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[PartnerType]:
        partner = await Partner.objects.aget(pk=pk)
        return await ModelMutation(PartnerSerializer).handle_update_mutation(data, info, partner)
