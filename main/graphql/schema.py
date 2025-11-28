import strawberry
from django.core.files.uploadedfile import UploadedFile
from strawberry.django.views import AsyncGraphQLView
from strawberry.file_uploads import Upload
from strawberry_django.optimizer import DjangoOptimizerExtension

from apps.blog.graphql import queries as blog_queries
from apps.department.graphql import queries as department_queries
from apps.faq.graphql import queries as faq_queries
from apps.home.graphql import queries as home_queries
from apps.news.graphql import queries as news_queries
from apps.partner.graphql import queries as partner_queries
from apps.procurement.graphql import queries as procurement_queries
from apps.project.graphql import queries as project_queries
from apps.radio_program.graphql import queries as radio_program_queries
from apps.resources.graphql import queries as resources_queries
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
class Mutation: ...


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
    scalar_overrides={
        UploadedFile: Upload,
    },
)
