import strawberry
import strawberry_django

from apps.vacancy.models import JobVacancy


@strawberry_django.order_type(JobVacancy)
class JobVacancyOrder:
    id: strawberry.auto
