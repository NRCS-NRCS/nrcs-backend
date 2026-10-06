import typing

from apps.common.serializers import UserResourceSerializer
from apps.procurement.models import Procurement
from utils.common import validate_expiry_date


class ProcurementSerializer(UserResourceSerializer[Procurement]):
    class Meta:
        model = Procurement
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
        ]

    @typing.override
    def validate(self, attrs):
        attrs = super().validate(attrs)
        validate_expiry_date(attrs, self.instance, "published_date")
        return attrs
