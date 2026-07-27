import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.radio_program.graphql.inputs import RadioProgramCreateInput, RadioProgramDeleteInput, RadioProgramUpdateInput
from apps.radio_program.graphql.types import RadioProgramType
from apps.radio_program.models import RadioProgram
from apps.radio_program.serializers import RadioProgramSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_radio_program: RadioProgramType = strawberry_django.mutations.delete(
        RadioProgramDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_radio_program(
        self,
        info: Info,
        data: RadioProgramCreateInput,
    ) -> MutationResponseType[RadioProgramType]:
        return await ModelMutation(RadioProgramSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_radio_program(
        self,
        info: Info,
        data: RadioProgramUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[RadioProgramType]:
        radio_program = await RadioProgram.objects.aget(pk=pk)
        return await ModelMutation(RadioProgramSerializer).handle_update_mutation(data, info, radio_program)
