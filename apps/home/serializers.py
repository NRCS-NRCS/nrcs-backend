import typing

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer
from apps.home.models import ActionLink, Highlight


class ActionLinkSerializer(UserResourceSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ActionLink
        fields = "__all__"


class HighlightSerializer(UserResourceSerializer):
    action_links = ActionLinkSerializer(many=True, required=False)

    class Meta:
        model = Highlight
        fields = [
            "heading",
            "description",
            # "image",
            "action_links",
            "expiry_date",
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
        action_links_data = validated_data.pop("action_links", [])
        highlight = super().update(instance, validated_data)

        action_links_qs = ActionLink.objects.filter(highlight=highlight)

        for action_link_data in action_links_data:
            action_link_id = action_link_data.get("id", None)
            action_link_instance = None
            if action_link_id is not None:
                action_link_instance = get_object_or_404(action_links_qs, id=action_link_id)

            action_link_serializer = ActionLinkSerializer(
                data=action_link_data,
                instance=action_link_instance,
                context={
                    **self.context,
                    "highlight": highlight,
                },
            )
            action_link_serializer.is_valid(raise_exception=True)
            action_link_serializer.save()
        return highlight
