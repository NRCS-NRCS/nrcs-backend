import strawberry
import strawberry_django

from apps.vacancy.models import JobVacancy


@strawberry_django.filters.filter(JobVacancy, lookups=True)
class JobVacancyFilter:
    expiry_date: strawberry.auto
    is_archived: bool | None = strawberry.UNSET
