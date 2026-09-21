import typing

from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer
from apps.strategic.models import MajorResponsibilities, StrategicDirectives


class MajorResponsibilitiesSerializer(UserResourceSerializer[MajorResponsibilities]):
    id = serializers.IntegerField(required=False)
    directive = serializers.PrimaryKeyRelatedField(
        queryset=StrategicDirectives.objects.all(),
        required=False,
    )

    class Meta:
        model = MajorResponsibilities
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
        ]

    @typing.override
    def create(self, validated_data):
        validated_data["directive"] = self.context["directive"]
        return super().create(validated_data)

    @typing.override
    def update(self, instance, validated_data):
        validated_data["directive"] = self.context["directive"]
        return super().update(instance, validated_data)


class StrategicDirectivesSerializer(UserResourceSerializer[StrategicDirectives]):
    major_responsibilities = MajorResponsibilitiesSerializer(many=True)

    class Meta:
        model = StrategicDirectives
        fields = [
            "title",
            "description",
            "cover_image",
            "major_responsibilities",
        ]
        read_only_fields = [
            "created_by",
            "modified_by",
        ]

    @typing.override
    def create(self, validated_data):
        major_responsibilities_data = validated_data.pop("major_responsibilities", [])
        directive = super().create(validated_data)
        for mr_data in major_responsibilities_data:
            serializer = MajorResponsibilitiesSerializer(
                data=mr_data,
                context={
                    **self.context,
                    "directive": directive,
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return directive

    @typing.override
    def update(self, instance, validated_data):
        major_responsibilities_data = validated_data.pop("major_responsibilities", None)
        directive = super().update(instance, validated_data)

        if major_responsibilities_data is None:
            return directive

        mr_qs = MajorResponsibilities.objects.filter(directive=directive)
        for mr_data in major_responsibilities_data:
            mr_id = mr_data.get("id", None)

            mr_instance = None
            if mr_id is not None:
                mr_instance = mr_qs.filter(id=mr_id).first()

            serializer = MajorResponsibilitiesSerializer(
                instance=mr_instance,
                data=mr_data,
                context={
                    **self.context,
                    "directive": directive,
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return directive
