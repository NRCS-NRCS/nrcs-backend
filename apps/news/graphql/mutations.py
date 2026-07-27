import strawberry
import strawberry_django
from strawberry_django.permissions import IsStaff

from apps.news.graphql.inputs import NewsCreateInput, NewsDeleteInput, NewsUpdateInput
from apps.news.graphql.types import NewsType
from apps.news.models import ActionLink, News
from apps.news.serializers import NewsSerializer
from main.graphql.context import Info
from utils.graphql.common import DataclassInstance
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import CudInput, MutationResponseType


@strawberry.type
class Mutation:
    delete_news: NewsType = strawberry_django.mutations.delete(
        NewsDeleteInput,
        key_attr="pk",
        extensions=[IsStaff()],
    )

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def create_news(
        self,
        info: Info,
        data: NewsCreateInput,
    ) -> MutationResponseType[NewsType]:
        return await ModelMutation(NewsSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def update_news(
        self,
        info: Info,
        data: NewsUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[NewsType]:
        news = await News.objects.aget(pk=pk)

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

        for action_link in data.action_links or []:
            if action_link.delete is not None and action_link.delete != strawberry.UNSET:
                await ActionLink.objects.filter(id=action_link.delete.id).adelete()
                continue

        return await ModelMutation(NewsSerializer).handle_update_mutation(
            data,
            info,
            news,
            None,
            transformer,
        )
