import strawberry
import strawberry_django
from django.db.models import Q

from apps.project.models import Project
from apps.strategic.graphql.filters import StrategicDirectivesFilter


@strawberry_django.filters.filter(Project, lookups=True)
class ProjectFilter:
    id: strawberry.ID | None = None
    department__strategic_directive: StrategicDirectivesFilter | None = None

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
