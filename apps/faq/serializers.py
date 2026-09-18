from apps.common.serializers import UserResourceSerializer
from apps.faq.models import Faq


class FAQSerializer(UserResourceSerializer[Faq]):
    class Meta:
        model = Faq
        fields = [
            "question",
            "answer",
        ]
