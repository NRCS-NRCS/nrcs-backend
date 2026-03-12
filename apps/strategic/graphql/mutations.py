import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.strategic.graphql.inputs import (
    StrategicDirectivesCreateInput,
    StrategicDirectivesDeleteInput,
    StrategicDirectivesUpdateInput,
)
from apps.strategic.graphql.types import StrategicDirectivesType
from apps.strategic.models import MajorResponsibilities, StrategicDirectives
from apps.strategic.serializers import StrategicDirectivesSerializer
from main.graphql.context import Info
from utils.graphql.common import DataclassInstance
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import CudInput, MutationResponseType


@strawberry.type
class Mutation:
    delete_strategic_directives: StrategicDirectivesType = strawberry_django.mutations.delete(
        StrategicDirectivesDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_strategic_directives(
        self,
        info: Info,
        data: StrategicDirectivesCreateInput,
    ) -> MutationResponseType[StrategicDirectivesType]:
        return await ModelMutation(StrategicDirectivesSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_strategic_directives(
        self,
        info: Info,
        data: StrategicDirectivesUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[StrategicDirectivesType]:
        strategic_directives = await StrategicDirectives.objects.aget(pk=pk)

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

        for major_responsibility in data.major_responsibilities or []:
            if major_responsibility.delete is not None and major_responsibility.delete != strawberry.UNSET:
                await MajorResponsibilities.objects.filter(id=major_responsibility.delete.id).adelete()
                continue

        return await ModelMutation(StrategicDirectivesSerializer).handle_update_mutation(
            data,
            info,
            strategic_directives,
            None,
            transformer,
        )
