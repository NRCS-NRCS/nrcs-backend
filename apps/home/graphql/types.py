import strawberry
import strawberry_django

from apps.home.models import ActionLink, Highlight
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Highlight)
class HighlightType:
    id: strawberry.ID
    heading: strawberry.auto
    description: strawberry.auto
    image: DjangoFileType | None
    action_links: list["ActionLinkType"] = strawberry_django.field()
    is_active: strawberry.auto


@strawberry_django.type(ActionLink)
class ActionLinkType:
    label: strawberry.auto
    url: strawberry.auto
