import strawberry
import strawberry_django

from apps.resources.models import Resource


@strawberry_django.ordering.order(Resource)
class ResourceOrder:
    id: strawberry.auto
