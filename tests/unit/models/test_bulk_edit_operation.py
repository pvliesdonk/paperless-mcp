"""``BulkEditOperation`` offers exactly the methods Paperless 3.1.3 accepts."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from paperless_mcp.models.common import BulkEditOperation

_OPENAPI = (
    Path(__file__).parents[3]
    / "docs"
    / "design"
    / "reference"
    / "paperless-openapi-3.1.3.json.gz"
)


def test_operations_match_the_openapi_method_enum() -> None:
    spec = json.loads(gzip.decompress(_OPENAPI.read_bytes()))
    methods = set(spec["components"]["schemas"]["MethodEnum"]["enum"])
    assert {op.value for op in BulkEditOperation} == methods
