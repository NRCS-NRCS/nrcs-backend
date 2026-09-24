from django.db.models import Max

from apps.cec_member.models import CecMember
from apps.common.serializers import UserResourceSerializer


class CecMemberSerializer(UserResourceSerializer[CecMember]):
    class Meta:
        model = CecMember
        fields = [
            "name",
            "member_type",
            "designation",
            "email",
            "secondary_email",
            "address",
            "contact_number",
            "photo",
            "is_active",
        ]

    # Optional text columns are blank-but-not-null; the CMS sends null for cleared inputs
    OPTIONAL_TEXT_FIELDS = (
        "designation",
        "email",
        "secondary_email",
        "address",
        "contact_number",
    )

    def to_internal_value(self, data):
        data = {key: ("" if key in self.OPTIONAL_TEXT_FIELDS and value is None else value) for key, value in data.items()}
        return super().to_internal_value(data)

    def create(self, validated_data):
        # New members go to the end of the list; ordering is owned by the reorder mutation.
        last_index = CecMember.objects.aggregate(value=Max("order_index"))["value"]
        validated_data["order_index"] = (last_index + 1) if last_index is not None else 0
        return super().create(validated_data)
