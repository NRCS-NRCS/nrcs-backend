import strawberry
import strawberry_django

from .filters import JobVacancyFilter
from .orders import JobVacancyOrder
from .types import JobVacancyType


@strawberry.type
class Query:
    job_vacancies: list[JobVacancyType] = strawberry_django.field(
        order=JobVacancyOrder,
        filters=JobVacancyFilter,
    )
    job_vacancy: JobVacancyType = strawberry_django.field()
