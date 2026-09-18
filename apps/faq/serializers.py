from django.db.models import Max

from apps.common.serializers import UserResourceSerializer
from apps.faq.models import Faq


class FAQSerializer(UserResourceSerializer[Faq]):
    class Meta:
        model = Faq
        fields = [
            "question",
            "answer",
            "order_index",
        ]

    def create(self, validated_data):
        # New FAQs go to the end of the list. order_index is never accepted from
        # the client on create (see FaqCreateInput); ordering is owned by the
        # reorder mutation, which keeps indices contiguous.
        last_index = Faq.objects.aggregate(value=Max("order_index"))["value"]
        validated_data["order_index"] = (last_index + 1) if last_index is not None else 0
        return super().create(validated_data)
