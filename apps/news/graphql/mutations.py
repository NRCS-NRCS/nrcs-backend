import strawberry
import strawberry_django
from strawberry_django.permissions import IsStaff

from apps.news.graphql.inputs import NewsCreateInput, NewsDeleteInput, NewsUpdateInput
from apps.news.graphql.types import NewsType
from apps.news.models import ActionLink, KeyStat, News, NewsAttachment
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

        # Deletions are applied up front so the serializer only ever sees
        # creates and updates, and so limit checks run against the final state.
        for collection, model in (
            (data.action_links, ActionLink),
            (data.key_stats, KeyStat),
            (data.attachments, NewsAttachment),
        ):
            if collection == strawberry.UNSET or collection is None:
                continue
            delete_ids = [
                item.delete.id
                for item in collection
                if item.delete is not None and item.delete != strawberry.UNSET
            ]
            if delete_ids:
                await model.objects.filter(news=news, id__in=delete_ids).adelete()

        return await ModelMutation(NewsSerializer).handle_update_mutation(
            data,
            info,
            news,
            None,
            transformer,
        )
