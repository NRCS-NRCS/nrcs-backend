import strawberry
import strawberry_django
from strawberry_django.permissions import IsStaff

from apps.blog.graphql.inputs import BlogCreateInput, BlogDeleteInput, BlogUpdateInput
from apps.blog.graphql.types import BlogType
from apps.blog.models import Blog
from apps.blog.serializers import BlogSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    delete_blog: BlogType = strawberry_django.mutations.delete(
        BlogDeleteInput,
        key_attr="pk",
        extensions=[IsStaff()],
    )

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def create_blog(
        self,
        info: Info,
        data: BlogCreateInput,
    ) -> MutationResponseType[BlogType]:
        return await ModelMutation(BlogSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsStaff()])
    async def update_blog(
        self,
        info: Info,
        data: BlogUpdateInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[BlogType]:
        blog = await Blog.objects.aget(pk=pk)
        return await ModelMutation(BlogSerializer).handle_update_mutation(data, info, blog)
