import strawberry
import strawberry_django
from strawberry_django.permissions import IsStaff

from apps.resources.graphql.inputs import ResourceCreateInput, ResourceDeleteInput, ResourceUpdateInput
from apps.resources.graphql.types import ResourceType
from apps.resources.models import Resource
from apps.resources.serializers import ResourceSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_resource: ResourceType = strawberry_django.mutations.delete(
        ResourceDeleteInput,
        key_attr="pk",
        extensions=[IsStaff()],
    )

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def create_resource(self, info: Info, data: ResourceCreateInput) -> MutationResponseType[ResourceType]:
        return await ModelMutation(ResourceSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def update_resource(
        self,
        info: Info,
        data: ResourceUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[ResourceType]:
        resource = await Resource.objects.aget(pk=pk)
        return await ModelMutation(ResourceSerializer).handle_update_mutation(data, info, resource)
