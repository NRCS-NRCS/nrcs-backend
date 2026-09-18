import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.project.graphql.inputs import ProjectCreateInput, ProjectDeleteInput, ProjectUpdateInput
from apps.project.graphql.types import ProjectType
from apps.project.models import Project
from apps.project.serializers import ProjectSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_project: ProjectType = strawberry_django.mutations.delete(
        ProjectDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_project(self, info: Info, data: ProjectCreateInput) -> MutationResponseType[ProjectType]:
        return await ModelMutation(ProjectSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_project(
        self,
        info: Info,
        data: ProjectUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[ProjectType]:
        project = await Project.objects.aget(pk=pk)
        return await ModelMutation(ProjectSerializer).handle_update_mutation(data, info, project)
