from apps.common.serializers import UserResourceSerializer
from apps.news.models import News


class NewsSerializer(UserResourceSerializer[News]):
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
        ]
