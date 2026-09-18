import strawberry
import strawberry_django
from strawberry.types import Info

from apps.common.graphql.types import UserResourceTypeMixin
from apps.home.models import ActionLink, Highlight, HighlightFile, KeyStat
from utils.graphql.types import DjangoFileType, markdown_with_absolute_media


@strawberry_django.type(ActionLink)
class ActionLinkType:
    id: strawberry.ID
    label: strawberry.auto
    url: strawberry.auto


@strawberry_django.type(Highlight)
class HighlightType(UserResourceTypeMixin):
    id: strawberry.ID
    heading: strawberry.auto
    image: DjangoFileType | None
    key_stats: list["KeyStatType"] = strawberry_django.field()
    files: list["HighlightFileType"] = strawberry_django.field()
    is_active: strawberry.auto
    show_in_popup: strawberry.auto
    action_links: list[ActionLinkType] | None

    @strawberry_django.field(only=["description"])
    def description(self, info: Info, root: strawberry.Parent[Highlight]) -> str:
        return markdown_with_absolute_media(root.description, info)


@strawberry_django.type(KeyStat)
class KeyStatType:
    order: strawberry.auto
    title: strawberry.auto
    stat: strawberry.auto
    featured: strawberry.auto


@strawberry_django.type(HighlightFile)
class HighlightFileType:
    file: DjangoFileType
    order: strawberry.auto
    label: strawberry.auto
