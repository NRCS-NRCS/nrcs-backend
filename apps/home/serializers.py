import typing

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer
from apps.home.models import ActionLink, Highlight


class ActionLinkSerializer(UserResourceSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ActionLink
        fields = "__all__"

    @typing.override
    def create(self, validated_data):
        validated_data["highlight"] = self.context["highlight"]
        return super().create(validated_data)

    @typing.override
    def update(self, instance, validated_data):
        validated_data["highlight"] = self.context["highlight"]
        return super().update(instance, validated_data)


class HighlightSerializer(UserResourceSerializer):
    action_links = ActionLinkSerializer(many=True, required=False)

    class Meta:
        model = Highlight
        fields = [
            "heading",
            "description",
            "image",
            "is_active",
            "action_links",
        ]

    @typing.override
    def create(self, validated_data):
        action_links_data = validated_data.pop("action_links", [])
        highlight = super().create(validated_data)
        for action_link_data in action_links_data:
            ActionLink.objects.create(highlight=highlight, **action_link_data)
        return highlight

    @typing.override
    def update(self, instance, validated_data):
        action_links_data = validated_data.pop("action_links", None)
        highlight = super().update(instance, validated_data)

        if action_links_data is None:
            return highlight

        action_links_qs = ActionLink.objects.filter(highlight=highlight)
        for action_link_data in action_links_data:
            action_link_id = action_link_data.get("id")

            action_link_instance = None
            if action_link_id is not None:
                action_link_instance = get_object_or_404(
                    action_links_qs,
                    id=action_link_id,
                )

            serializer = ActionLinkSerializer(
                instance=action_link_instance,
                data=action_link_data,
                context={
                    **self.context,
                    "highlight": highlight,
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return highlight
