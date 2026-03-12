import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.partner.models import Partner


@strawberry_django.input(Partner)
class PartnerCreateInput:
    title: strawberry.auto
    scope: strawberry.auto
    image: Upload | None


@strawberry_django.partial(Partner)
class PartnerUpdateInput:
    title: strawberry.auto
    scope: strawberry.auto
    image: Upload | None


@strawberry_django.input(Partner)
class PartnerDeleteInput:
    id: strawberry.ID
