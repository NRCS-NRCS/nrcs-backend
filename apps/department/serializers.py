from apps.common.serializers import UserResourceSerializer
from apps.department.models import Department


class DepartmentSerializer(UserResourceSerializer[Department]):
    class Meta:
        model = Department
        fields = [
            "title",
            "description",
            "contact_person_name",
            "contact_person_email",
            "slug",
            "strategic_directive",
        ]
