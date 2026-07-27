from apps.common.serializers import UserResourceSerializer
from apps.partner.models import Partner


class PartnerSerializer(UserResourceSerializer[Partner]):
    class Meta:
        model = Partner
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
        ]
