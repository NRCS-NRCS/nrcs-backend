from apps.blog.models import Blog
from apps.common.serializers import UserResourceSerializer


class BlogSerializer(UserResourceSerializer[Blog]):
    class Meta:
        model = Blog
        fields = [
            "title",
            "published_date",
            "author",
            "content",
            "cover_image",
            "featured",
            "status",
            "department",
            "directive",
        ]
