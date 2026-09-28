"""Field types shared by the create and patch models, with their descriptions.

These models are tool arguments, so each description reaches the model as the
property description of that argument's schema.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

Match = Annotated[
    str | None,
    Field(
        description=(
            "Text Paperless looks for in new documents to assign this "
            "automatically, read according to matching_algorithm."
        )
    ),
]
MatchingAlgorithm = Annotated[
    int | None,
    Field(
        ge=0,
        le=6,
        description=(
            "How match is applied to new documents: 0 never, 1 any word, 2 all "
            "words, 3 the exact text, 4 a regular expression, 5 fuzzy, "
            "6 learned automatically from existing assignments."
        ),
    ),
]
IsInsensitive = Annotated[
    bool | None, Field(description="Match without regard to case.")
]
