from apps.common.serializers import UserResourceSerializer
from apps.strategic.models import MajorResponsibilities, StrategicDirectives


class StrategicDirectivesSerializer(UserResourceSerializer[StrategicDirectives]):
    class Meta:
        model = StrategicDirectives
        fields = [
            "title",
            "description",
            "contact_person_name",
            "contact_person_email",
            "cover_image",
            "slug",
        ]
        read_only_fields = [
            "created_by",
            "modified_by",
        ]


class MajorResponsibilitiesSerializer(UserResourceSerializer[MajorResponsibilities]):
    class Meta:
        model = MajorResponsibilities
        fields = [
            "title",
            "description",
            "directive",
            "slug",
        ]
        read_only_fields = [
            "created_by",
            "modified_by",
        ]
