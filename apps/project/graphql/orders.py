import strawberry
import strawberry_django

from apps.project.models import Project


@strawberry_django.order_type(Project)
class ProjectOrder:
    id: strawberry.auto
