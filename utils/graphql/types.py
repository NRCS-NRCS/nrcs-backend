import re
import typing

import strawberry
import strawberry_django
from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.db.models.fields import files
from django.db.models.fields.files import FileField, ImageField
from strawberry.types import Info
from strawberry_django.fields.types import field_type_map

ResultTypeVar = typing.TypeVar("ResultTypeVar")


def markdown_with_absolute_media(content: str | None, info: Info) -> str:
    """Return markdown ``content`` with root-relative media URLs made absolute.

    Mirrors :class:`DjangoFileType`: the stored markdown keeps storage-relative
    ``/media/...`` references (portable across domains), which are absolutized
    against the request host at read time when using filesystem storage. Remote
    storage (e.g. S3) already yields absolute URLs via ``default_storage.url()``,
    so the content is returned unchanged.
    """
    if not content:
        return content or ""
    if not isinstance(default_storage, FileSystemStorage):
        return content
    absolute_prefix = info.context.request.build_absolute_uri(settings.MEDIA_URL)
    # Match a media URL only where it starts a markdown/HTML target: after "](",
    # or a single/double quote. Keeps the preceding delimiter, swaps the prefix.
    return re.sub(
        r"([(\"'])" + re.escape(settings.MEDIA_URL),
        lambda match: match.group(1) + absolute_prefix,
        content,
    )


# generalize all the CustomErrorType
CustomErrorType = strawberry.scalar(
    typing.NewType("CustomErrorType", object),
    description="A generic type to return error messages",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry.type
class MutationResponseType(typing.Generic[ResultTypeVar]):
    ok: bool = True
    errors: CustomErrorType | None = None
    result: ResultTypeVar | None = None


# Replaces strawberry_django.fields.types.DjangoFileType
@strawberry.type
class DjangoFileType:
    name: str
    size: int

    @strawberry_django.field
    def url(
        self,
        info: Info,
        file: strawberry.Parent[files.FieldFile],
    ) -> str:
        if isinstance(default_storage, FileSystemStorage):
            return info.context.request.build_absolute_uri(file.url)
        return file.url


field_type_map.update(
    {
        FileField: DjangoFileType,
        ImageField: DjangoFileType,
    },
)
