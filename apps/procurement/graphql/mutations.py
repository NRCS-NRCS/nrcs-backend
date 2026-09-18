import strawberry
import strawberry_django
from strawberry_django.permissions import IsStaff

from apps.procurement.graphql.inputs import ProcurementCreateInput, ProcurementDeleteInput, ProcurementUpdateInput
from apps.procurement.graphql.types import ProcurementType
from apps.procurement.models import Procurement
from apps.procurement.serializers import ProcurementSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_procurement: ProcurementType = strawberry_django.mutations.delete(
        ProcurementDeleteInput,
        key_attr="pk",
        extensions=[IsStaff()],
    )

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def create_procurement(self, info: Info, data: ProcurementCreateInput) -> MutationResponseType[ProcurementType]:
        return await ModelMutation(ProcurementSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def update_procurement(
        self,
        info: Info,
        data: ProcurementUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[ProcurementType]:
        procurement = await Procurement.objects.aget(pk=pk)
        return await ModelMutation(ProcurementSerializer).handle_update_mutation(data, info, procurement)
