from apps.common.serializers import UserResourceSerializer
from apps.project.models import Project


class ProjectSerializer(UserResourceSerializer[Project]):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "cover_image",
            "department",
        ]
