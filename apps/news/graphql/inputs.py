import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.news.models import ActionLink, News
from utils.graphql.types import CudInput


@strawberry_django.input(ActionLink)
class ActionLinkCreateInput:
    url: strawberry.auto
    label: strawberry.auto


@strawberry_django.partial(ActionLink)
class ActionLinkUpdateInput:
    id: strawberry.ID
    url: strawberry.auto
    label: strawberry.auto


@strawberry.input
class ActionLinkInput(CudInput[ActionLinkCreateInput, ActionLinkUpdateInput]): ...


@strawberry_django.input(News)
class NewsCreateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    slug: strawberry.auto
    status: strawberry.auto
    directive: strawberry.ID
    is_highlighted: strawberry.auto
    file: Upload | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    action_links: list[ActionLinkCreateInput] | None = strawberry.UNSET


@strawberry_django.partial(News)
class NewsUpdateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    status: strawberry.auto
    slug: strawberry.auto
    directive: strawberry.ID
    is_highlighted: strawberry.auto
    file: Upload | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    action_links: list[ActionLinkInput] | None = strawberry.UNSET


@strawberry_django.input(News)
class NewsDeleteInput:
    id: strawberry.ID
