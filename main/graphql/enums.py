import dataclasses
from enum import Enum

import strawberry

@strawberry.enum
class DummyEnum(Enum):
    VALUE_1 = "Value 1"
    VALUE_2 = "Value 2"


ENUM_TO_STRAWBERRY_ENUMS: list[type] = [
    DummyEnum,
]


class AppEnumData:
    def __init__(self, enum):
        self.enum = enum

    @property
    def key(self):
        return self.enum

    @property
    def label(self):
        return str(self.enum.label)


def generate_app_enum_collection_data(name):
    return type(
        name,
        (),
        {
            enum.__name__: [AppEnumData(e) for e in enum]  # type: ignore[reportGeneralTypeIssues]
            for enum in ENUM_TO_STRAWBERRY_ENUMS
        },
    )


AppEnumCollectionData = generate_app_enum_collection_data("AppEnumCollectionData")


def generate_type_for_enum(name, Enum):
    return strawberry.type(
        dataclasses.make_dataclass(
            f"AppEnumCollection{name}",
            [
                ("key", Enum),
                ("label", str),
            ],
        ),
    )


def _enum_type(name, Enum):
    EnumType = generate_type_for_enum(name, Enum)

    @strawberry.field
    def _field() -> list[EnumType]:  # type: ignore[reportGeneralTypeIssues]
        return [
            EnumType(
                key=e,
                label=e.label,
            )
            for e in Enum
        ]

    return list[EnumType], _field


def generate_type_for_enums():
    enum_fields = [
        (
            enum.__name__,
            *_enum_type(enum.__name__, enum),
        )
        for enum in ENUM_TO_STRAWBERRY_ENUMS
    ]
    return strawberry.type(
        dataclasses.make_dataclass(
            "AppEnumCollection",
            enum_fields,
        ),
    )


AppEnumCollection = generate_type_for_enums()
