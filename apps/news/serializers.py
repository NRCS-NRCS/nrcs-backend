import typing

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer
from apps.news.models import ActionLink, News


class ActionLinkSerializer(UserResourceSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ActionLink
        fields = "__all__"

    @typing.override
    def create(self, validated_data):
        validated_data["news"] = self.context["news"]
        return super().create(validated_data)

    @typing.override
    def update(self, instance, validated_data):
        validated_data["news"] = self.context["news"]
        return super().update(instance, validated_data)


class NewsSerializer(UserResourceSerializer[News]):
    action_links = ActionLinkSerializer(many=True, required=False)

    class Meta:
        model = News
        fields = [
            "title",
            "file",
            "content",
            "status",
            "published_date",
            "directive",
            "slug",
            "cover_image",
            "is_highlighted",
            "action_links",
        ]

    @typing.override
    def create(self, validated_data):
        action_links_data = validated_data.pop("action_links", [])
        news = super().create(validated_data)
        for action_link_data in action_links_data:
            ActionLink.objects.create(news=news, **action_link_data)
        return news

    @typing.override
    def update(self, instance, validated_data):
        action_links_data = validated_data.pop("action_links", None)
        news = super().update(instance, validated_data)

        if action_links_data is None:
            return news

        action_links_qs = ActionLink.objects.filter(news=news)
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
                    "news": news,
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return news
