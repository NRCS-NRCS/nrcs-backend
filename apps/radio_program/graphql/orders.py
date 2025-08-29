import strawberry
import strawberry_django

from apps.radio_program.models import RadioProgram


@strawberry_django.ordering.order(RadioProgram)
class RadioProgramOrder:
    id: strawberry.auto
    title: strawberry.auto
    published_date: strawberry.auto
