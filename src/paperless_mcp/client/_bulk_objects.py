"""Request body for ``/api/bulk_edit_objects/``, shared by the object clients.

Paperless reads ``owner``, ``permissions`` and ``merge`` from the top level of
this request and ignores anything nested; it also accepts ``all`` and
``filters``, which select objects beyond the given ids. So only the three
permission fields are forwarded, and the fixed keys are written last where a
caller's dict cannot replace them. The claims are sourced in
``docs/design/reference/paperless-bulk-edit-indexing.md``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

OBJECT_BULK_PARAMETERS = ("owner", "permissions", "merge")


def object_bulk_payload(
    object_type: str,
    ids: Sequence[int],
    operation: str,
    parameters: Mapping[str, object] | None,
) -> dict[str, object]:
    """Build the request body for one object bulk edit.

    Args:
        object_type: Paperless's name for the kind of object, e.g. ``tags``.
        ids: Ids of the objects to change.
        operation: ``set_permissions`` or ``delete``.
        parameters: ``owner``, ``permissions`` and ``merge`` for
            ``set_permissions``; nothing else.

    Returns:
        The JSON body to post.

    Raises:
        ValueError: If *parameters* names a key other than the three above.
    """
    extra = sorted(set(parameters or {}) - set(OBJECT_BULK_PARAMETERS))
    if extra:
        msg = f"unsupported object bulk-edit parameters: {', '.join(extra)}"
        raise ValueError(msg)
    return {
        **(parameters or {}),
        "object_type": object_type,
        "objects": list(ids),
        "operation": operation,
    }
