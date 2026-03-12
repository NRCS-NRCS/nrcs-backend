import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.news.graphql.inputs import NewsCreateInput, NewsDeleteInput, NewsUpdateInput
from apps.news.graphql.types import NewsType
from apps.news.models import News
from apps.news.serializers import NewsSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_news: NewsType = strawberry_django.mutations.delete(
        NewsDeleteInput,
        key_attr="pk",
        extensions=[IsAuthenticated()],
    )

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_news(
        self,
        info: Info,
        data: NewsCreateInput,
    ) -> MutationResponseType[NewsType]:
        return await ModelMutation(NewsSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_news(
        self,
        info: Info,
        data: NewsUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[NewsType]:
        news = await News.objects.aget(pk=pk)
        return await ModelMutation(NewsSerializer).handle_update_mutation(data, info, news)
