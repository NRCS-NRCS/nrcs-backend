import strawberry
import strawberry_django
from strawberry.types import Info

from apps.common.graphql.types import UserResourceTypeMixin
from apps.news.models import ActionLink, News
from apps.strategic.graphql.types import StrategicDirectivesType
from utils.graphql.types import DjangoFileType, markdown_with_absolute_media


@strawberry_django.type(ActionLink)
class ActionLinkType:
    id: strawberry.ID
    label: strawberry.auto
    url: strawberry.auto


@strawberry_django.type(News)
class NewsType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType | None
    status: strawberry.auto
    published_date: strawberry.auto
    directive_id: strawberry.auto
    directive: StrategicDirectivesType | None
    slug: strawberry.auto
    cover_image: DjangoFileType | None
    is_highlighted: strawberry.auto
    action_links: list[ActionLinkType] | None

    @strawberry_django.field(only=["content"])
    def content(self, info: Info, root: strawberry.Parent[News]) -> str:
        return markdown_with_absolute_media(root.content, info)
