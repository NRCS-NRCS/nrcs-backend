import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import JobVacancyFilter
from .orders import JobVacancyOrder
from .types import JobVacancyType


@strawberry.type
class Query:
    # --- Paginated
    job_vacancies: OffsetPaginated[JobVacancyType] = strawberry_django.offset_paginated(
        order=JobVacancyOrder,
        filters=JobVacancyFilter,
    )
    job_vacancy: JobVacancyType = strawberry_django.field()
