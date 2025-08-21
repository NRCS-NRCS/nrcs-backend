import strawberry
import strawberry_django

from apps.work.models import Work


@strawberry_django.ordering.order(Work)
class WorkOrder:
    id: strawberry.auto
