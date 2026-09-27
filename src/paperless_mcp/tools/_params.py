"""Parameter types shared by several tools, each carrying its model-facing text.

A parameter's description is what the model reads when it fills that one
argument (the ``writing-model-facing-text`` skill), so a parameter that recurs
across tools is described once here rather than in every docstring.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

Page = Annotated[int, Field(ge=1, description="Page number, starting at 1.")]
PageSize = Annotated[
    int, Field(ge=1, le=100, description="Results per page, up to 100.")
]
Ordering = Annotated[
    str | None,
    Field(
        description=(
            "Field to sort by, such as name; prefix it with - to sort "
            "descending (-name). Omit for Paperless's default order."
        )
    ),
]
DocumentOrdering = Annotated[
    str | None,
    Field(
        description=(
            "Field to sort by: created, added, modified, title, "
            "archive_serial_number, correspondent__name, document_type__name "
            "or page_count; prefix it with - to sort descending (-created). "
            "Omit for Paperless's default order."
        )
    ),
]
CorrespondentOrdering = Annotated[
    str | None,
    Field(
        description=(
            "Field to sort by: name, document_count or last_correspondence; "
            "prefix it with - to sort descending (-last_correspondence). Omit "
            "for Paperless's default order."
        )
    ),
]
NameContains = Annotated[
    str | None,
    Field(description="Keep only names that contain this text, ignoring case."),
]
DocumentId = Annotated[int, Field(description="Paperless document id.")]
BulkIds = Annotated[list[int], Field(description="Ids of the objects to change.")]
ObjectBulkParameters = Annotated[
    dict[str, object] | None,
    Field(
        description=(
            "For set_permissions: owner (a user id or null), permissions "
            '({"view": {"users": [ids], "groups": [ids]}, "change": {...}}) and '
            "merge (true adds to the current permissions instead of replacing "
            "them). Omit for delete."
        )
    ),
]
