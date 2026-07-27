import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.home.models import ActionLink, Highlight
from utils.graphql.types import DjangoFileType


@strawberry_django.type(ActionLink)
class ActionLinkType:
    id: strawberry.ID
    label: strawberry.auto
    url: strawberry.auto


@strawberry_django.type(Highlight)
class HighlightType(UserResourceTypeMixin):
    id: strawberry.ID
    heading: strawberry.auto
    description: strawberry.auto
    image: DjangoFileType | None
    is_active: strawberry.auto
    action_links: list[ActionLinkType] | None
