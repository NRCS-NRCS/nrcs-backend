import strawberry
import strawberry_django
from django.contrib.auth.models import User


@strawberry_django.ordering.order(User)
class UserOrder:
    id: strawberry.auto
    email: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto
