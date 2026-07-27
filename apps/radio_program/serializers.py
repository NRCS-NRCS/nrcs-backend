from apps.common.serializers import UserResourceSerializer
from apps.radio_program.models import RadioProgram


class RadioProgramSerializer(UserResourceSerializer[RadioProgram]):
    class Meta:
        model = RadioProgram
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
        ]
