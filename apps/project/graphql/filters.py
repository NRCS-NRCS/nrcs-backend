import strawberry
import strawberry_django

from apps.project.models import Project
from apps.strategic.graphql.filters import StrategicDirectivesFilter


@strawberry_django.filters.filter(Project, lookups=True)
class ProjectFilter:
    id: strawberry.ID | None = None
    department__strategic_directive: StrategicDirectivesFilter | None = None
