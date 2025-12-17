import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.vacancy.graphql.inputs import JobVacancyCreateInput, JobVacancyDeleteInput, JobVacancyUpdateInput
from apps.vacancy.graphql.types import JobVacancyType
from apps.vacancy.models import JobVacancy
from apps.vacancy.serializers import JobVacancySerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_job_vacancy: JobVacancyType = strawberry_django.mutations.delete(
        JobVacancyDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_job_vacancy(self, info: Info, data: JobVacancyCreateInput) -> MutationResponseType[JobVacancyType]:
        return await ModelMutation(JobVacancySerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_job_vacancy(
        self,
        info: Info,
        data: JobVacancyUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[JobVacancyType]:
        vacancy = await JobVacancy.objects.aget(pk=pk)
        return await ModelMutation(JobVacancySerializer).handle_update_mutation(data, info, vacancy)
