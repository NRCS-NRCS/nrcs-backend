import strawberry
import strawberry_django

from apps.home.models import ActionLink, Highlight, KeyStat
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Highlight)
class HighlightType:
    id: strawberry.ID
    heading: strawberry.auto
    description: str
    image: DjangoFileType | None
    action_links: list["ActionLinkType"] = strawberry_django.field()
    key_stats: list["KeyStatType"] = strawberry_django.field()
    is_active: strawberry.auto


@strawberry_django.type(ActionLink)
class ActionLinkType:
    label: strawberry.auto
    url: strawberry.auto


@strawberry_django.type(KeyStat)
class KeyStatType:
    order: strawberry.auto
    title: strawberry.auto
    stat: strawberry.auto
    featured: strawberry.auto
