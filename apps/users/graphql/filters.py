import strawberry
import strawberry_django
from django.contrib.auth.models import User
from django.db.models import Q


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    id: strawberry.ID | None
    is_active: strawberry.auto
    is_staff: strawberry.auto

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(email__icontains=value)
