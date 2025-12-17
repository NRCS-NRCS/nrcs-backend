import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.strategic.graphql.inputs import (
    StrategicDirectivesCreateInput,
    StrategicDirectivesDeleteInput,
    StrategicDirectivesUpdateInput,
)
from apps.strategic.graphql.types import StrategicDirectivesType
from apps.strategic.models import StrategicDirectives
from apps.strategic.serializers import StrategicDirectivesSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


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
        return await ModelMutation(StrategicDirectivesSerializer).handle_update_mutation(data, info, strategic_directives)
