import strawberry
import strawberry_django

from apps.vacancy.models import JobVacancy


@strawberry_django.ordering.order(JobVacancy)
class JobVacancyOrder:
    id: strawberry.auto
