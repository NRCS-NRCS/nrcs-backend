import strawberry
import strawberry_django

from apps.home.models import ActionLink, Highlight
from strawberry.file_uploads import Upload

from utils.graphql.types import CudInput

# NOTE: Make sure this matches with the serializers ../serializers.py


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


@strawberry_django.input(Highlight)
class HighlightCreateInput:
    heading: strawberry.auto
    description: strawberry.auto
    is_active: strawberry.auto
    action_links: list[ActionLinkCreateInput] | None = strawberry.UNSET
    image: Upload | None = strawberry.UNSET


@strawberry_django.partial(Highlight)
class HighlightUpdateInput:
    heading: strawberry.auto
    description: strawberry.auto
    is_active: strawberry.auto
    image: Upload | None = strawberry.UNSET
    action_links: list[ActionLinkInput] | None = strawberry.UNSET


@strawberry_django.input(Highlight)
class HighlightDeleteInput:
    id: strawberry.ID
