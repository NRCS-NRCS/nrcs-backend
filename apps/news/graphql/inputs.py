import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.news.models import ActionLink, KeyStat, News, NewsAttachment
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


@strawberry_django.input(KeyStat)
class KeyStatCreateInput:
    order: strawberry.auto
    title: strawberry.auto
    stat: strawberry.auto
    featured: strawberry.auto


@strawberry_django.partial(KeyStat)
class KeyStatUpdateInput:
    id: strawberry.ID
    order: strawberry.auto
    title: strawberry.auto
    stat: strawberry.auto
    featured: strawberry.auto


@strawberry.input
class KeyStatInput(CudInput[KeyStatCreateInput, KeyStatUpdateInput]): ...


@strawberry_django.input(NewsAttachment)
class NewsAttachmentCreateInput:
    order: strawberry.auto
    label: strawberry.auto
    file: Upload


@strawberry_django.partial(NewsAttachment)
class NewsAttachmentUpdateInput:
    id: strawberry.ID
    order: strawberry.auto
    label: strawberry.auto
    # Omit to keep the stored file and only change its order or label.
    file: Upload | None = strawberry.UNSET


@strawberry.input
class NewsAttachmentInput(CudInput[NewsAttachmentCreateInput, NewsAttachmentUpdateInput]): ...


@strawberry_django.input(News)
class NewsCreateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    slug: strawberry.auto
    status: strawberry.auto
    directive: strawberry.ID | None = strawberry.UNSET
    is_highlighted: strawberry.auto = strawberry.UNSET
    show_in_popup: strawberry.auto = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    action_links: list[ActionLinkCreateInput] | None = strawberry.UNSET
    key_stats: list[KeyStatCreateInput] | None = strawberry.UNSET
    attachments: list[NewsAttachmentCreateInput] | None = strawberry.UNSET


@strawberry_django.partial(News)
class NewsUpdateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    status: strawberry.auto
    slug: strawberry.auto
    directive: strawberry.ID | None = strawberry.UNSET
    is_highlighted: strawberry.auto = strawberry.UNSET
    show_in_popup: strawberry.auto = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    action_links: list[ActionLinkInput] | None = strawberry.UNSET
    key_stats: list[KeyStatInput] | None = strawberry.UNSET
    attachments: list[NewsAttachmentInput] | None = strawberry.UNSET


@strawberry_django.input(News)
class NewsDeleteInput:
    id: strawberry.ID
