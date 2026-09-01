import typing

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer
from apps.news.models import ActionLink, KeyStat, News, NewsAttachment


class NewsChildSerializer(UserResourceSerializer):
    """Base for rows owned by a single News; the parent comes from the context."""

    id = serializers.IntegerField(required=False)

    @typing.override
    def create(self, validated_data):
        validated_data["news"] = self.context["news"]
        return super().create(validated_data)

    @typing.override
    def update(self, instance, validated_data):
        validated_data["news"] = self.context["news"]
        return super().update(instance, validated_data)


class ActionLinkSerializer(NewsChildSerializer):
    class Meta:
        model = ActionLink
        fields = "__all__"


class KeyStatSerializer(NewsChildSerializer):
    class Meta:
        model = KeyStat
        fields = ["id", "order", "title", "stat", "featured"]


class NewsAttachmentSerializer(NewsChildSerializer):
    class Meta:
        model = NewsAttachment
        fields = ["id", "order", "label", "file"]


class NewsSerializer(UserResourceSerializer[News]):
    action_links = ActionLinkSerializer(many=True, required=False)
    key_stats = KeyStatSerializer(many=True, required=False)
    attachments = NewsAttachmentSerializer(many=True, required=False)

    # field name -> (model, serializer) for the three child collections.
    CHILDREN = {
        "action_links": (ActionLink, ActionLinkSerializer),
        "key_stats": (KeyStat, KeyStatSerializer),
        "attachments": (NewsAttachment, NewsAttachmentSerializer),
    }

    class Meta:
        model = News
        fields = [
            "title",
            "content",
            "status",
            "published_date",
            "directive",
            "slug",
            "cover_image",
            "is_highlighted",
            "show_in_popup",
            "action_links",
            "key_stats",
            "attachments",
        ]

    def _untouched_count(self, model, children_data, **filters):
        """Count existing rows this payload does not address.

        Deletions are applied before the serializer runs (see the news mutation),
        so what is left in the database is already the post-delete state.
        """
        if self.instance is None:
            return 0
        touched_ids = {datum["id"] for datum in children_data if datum.get("id") is not None}
        return model.objects.filter(news=self.instance, **filters).exclude(id__in=touched_ids).count()

    @typing.override
    def validate(self, attrs):
        attrs = super().validate(attrs)

        for field in self.CHILDREN:
            children_data = attrs.get(field)
            if not children_data:
                continue
            orders = [datum["order"] for datum in children_data if datum.get("order") is not None]
            if len(orders) != len(set(orders)):
                raise serializers.ValidationError({field: "Each row must have a distinct order."})

        key_stats_data = attrs.get("key_stats")
        if key_stats_data is not None:
            featured = sum(1 for datum in key_stats_data if datum.get("featured"))
            featured += self._untouched_count(KeyStat, key_stats_data, featured=True)
            if featured > KeyStat.MAX_FEATURED_PER_NEWS:
                raise serializers.ValidationError(
                    {"key_stats": f"A news item can have at most {KeyStat.MAX_FEATURED_PER_NEWS} featured key stats."},
                )

        attachments_data = attrs.get("attachments")
        if attachments_data is not None:
            count = len(attachments_data) + self._untouched_count(NewsAttachment, attachments_data)
            if count > NewsAttachment.MAX_ATTACHMENTS_PER_NEWS:
                raise serializers.ValidationError(
                    {
                        "attachments": (
                            f"A news item can have at most "
                            f"{NewsAttachment.MAX_ATTACHMENTS_PER_NEWS} attachments."
                        ),
                    },
                )

        return attrs

    def _save_children(self, news, field, children_data):
        """Create or update the rows in ``children_data`` against ``news``."""
        model, serializer_class = self.CHILDREN[field]
        existing_qs = model.objects.filter(news=news)

        for datum in children_data:
            child_id = datum.get("id")
            instance = get_object_or_404(existing_qs, id=child_id) if child_id is not None else None
            serializer = serializer_class(
                instance=instance,
                data=datum,
                # The GraphQL update input is partial, so an untouched column
                # simply stays absent from the payload.
                partial=instance is not None,
                context={**self.context, "news": news},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

    @typing.override
    def create(self, validated_data):
        children_data = {field: validated_data.pop(field, []) for field in self.CHILDREN}
        news = super().create(validated_data)
        for field, data in children_data.items():
            self._save_children(news, field, data)
        return news

    @typing.override
    def update(self, instance, validated_data):
        # None means "not sent" — leave that collection alone.
        children_data = {field: validated_data.pop(field, None) for field in self.CHILDREN}
        news = super().update(instance, validated_data)
        for field, data in children_data.items():
            if data is not None:
                self._save_children(news, field, data)
        return news
