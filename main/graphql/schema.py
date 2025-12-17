import strawberry
from django.core.files.uploadedfile import UploadedFile
from strawberry.django.views import AsyncGraphQLView
from strawberry.file_uploads import Upload
from strawberry_django.optimizer import DjangoOptimizerExtension

from apps.blog.graphql import mutations as blog_mutations
from apps.blog.graphql import queries as blog_queries
from apps.common.graphql import mutations as common_mutation
from apps.department.graphql import mutations as department_mutations
from apps.department.graphql import queries as department_queries
from apps.faq.graphql import mutations as faq_mutation
from apps.faq.graphql import queries as faq_queries
from apps.home.graphql import mutations as home_mutations
from apps.home.graphql import queries as home_queries
from apps.news.graphql import mutations as news_mutations
from apps.news.graphql import queries as news_queries
from apps.partner.graphql import mutations as partner_mutations
from apps.partner.graphql import queries as partner_queries
from apps.procurement.graphql import mutations as procurement_mutations
from apps.procurement.graphql import queries as procurement_queries
from apps.project.graphql import mutations as project_mutation
from apps.project.graphql import queries as project_queries
from apps.radio_program.graphql import mutations as radio_program_mutations
from apps.radio_program.graphql import queries as radio_program_queries
from apps.resources.graphql import mutations as resources_mutations
from apps.resources.graphql import queries as resources_queries
from apps.strategic.graphql import mutations as strategic_mutations
from apps.strategic.graphql import queries as strategic_queries
from apps.vacancy.graphql import queries as vacancy_queries

from .context import GraphQLContext
from .dataloaders import GlobalDataLoader
from .enums import AppEnumCollection, AppEnumCollectionData


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, *args, **kwargs) -> GraphQLContext:  # type: ignore[reportIncompatibleMethodOverride]
        return GraphQLContext(
            *args,
            **kwargs,
            dl=GlobalDataLoader(),
        )


@strawberry.type
class Query(
    strategic_queries.Query,
    department_queries.Query,
    procurement_queries.Query,
    vacancy_queries.Query,
    project_queries.Query,
    faq_queries.Query,
    resources_queries.Query,
    partner_queries.Query,
    blog_queries.Query,
    news_queries.Query,
    home_queries.Query,
    radio_program_queries.Query,
):
    enums: AppEnumCollection = strawberry.field(  # type: ignore[reportGeneralTypeIssues]
        resolver=lambda: AppEnumCollectionData(),
    )


# NOTE: for now we are not using mutation
@strawberry.type
class Mutation(
    department_mutations.Mutation,
    common_mutation.Mutation,
    faq_mutation.Mutation,
    project_mutation.Mutation,
    blog_mutations.Mutation,
    home_mutations.Mutation,
    news_mutations.Mutation,
    partner_mutations.Mutation,
    procurement_mutations.Mutation,
    radio_program_mutations.Mutation,
    resources_mutations.Mutation,
    strategic_mutations.Mutation,
): ...


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ],
    scalar_overrides={
        UploadedFile: Upload,
    },
)
