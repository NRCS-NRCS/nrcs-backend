import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.department.graphql.inputs import DepartmentCreateInput, DepartmentDeleteInput, DepartmentUpdateInput
from apps.department.graphql.types import DepartmentType
from apps.department.models import Department
from apps.department.serializers import DepartmentSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_department: DepartmentType = strawberry_django.mutations.delete(
        DepartmentDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_department(self, info: Info, data: DepartmentCreateInput) -> MutationResponseType[DepartmentType]:
        return await ModelMutation(DepartmentSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_department(
        self,
        info: Info,
        data: DepartmentUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[DepartmentType]:
        department = await Department.objects.aget(pk=pk)
        return await ModelMutation(DepartmentSerializer).handle_update_mutation(data, info, department)
