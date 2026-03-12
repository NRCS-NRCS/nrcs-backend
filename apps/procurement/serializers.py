from apps.common.serializers import UserResourceSerializer
from apps.procurement.models import Procurement


class ProcurementSerializer(UserResourceSerializer[Procurement]):
    class Meta:
        model = Procurement
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
        ]
