import strawberry
import strawberry_django

from apps.resources.models import Resource


@strawberry_django.order_type(Resource)
class ResourceOrder:
    id: strawberry.auto
