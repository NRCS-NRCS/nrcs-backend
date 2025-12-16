# --- Move this to a common app later? --- #

import strawberry
import strawberry_django
from django.contrib.auth.models import User


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    first_name: strawberry.auto
    last_name: strawberry.auto


@strawberry_django.type(User)
class UserMeType(UserType):
    email: strawberry.auto
