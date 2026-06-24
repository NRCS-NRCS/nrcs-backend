import strawberry
import strawberry_django
from django.db.models import Q

from apps.vacancy.models import JobVacancy


@strawberry_django.filters.filter(JobVacancy, lookups=True)
class JobVacancyFilter:
    expiry_date: strawberry.auto
    is_archived: bool | None = strawberry.UNSET
    search: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value) | Q(position__icontains=value)