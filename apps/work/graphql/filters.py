import strawberry
import strawberry_django

from apps.work.models import Work


@strawberry_django.filters.filter(Work, lookups=True)
class WorkFilter:
    strategic_directive: strawberry.ID
