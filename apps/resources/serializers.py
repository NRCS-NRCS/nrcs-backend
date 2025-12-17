from apps.common.serializers import UserResourceSerializer
from apps.resources.models import Resource


class ResourceSerializer(UserResourceSerializer[Resource]):
    class Meta:
        model = Resource
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
        ]
