"""Infrastructure adapters (SQLite, filesystem).

RC2 (F-05): importing ``infrastructure`` must stay cheap and side-effect
free, so the resource-channel sidecar entry does not drag in unrelated
adapters. The subpackages are therefore imported lazily (PEP 562): direct
``from infrastructure import sqlite`` keeps working for product call sites,
while ``import infrastructure.resource_channel.host_bridge`` loads neither
``filesystem`` nor ``sqlite``. Isolation evidence: the pre-fix module dump is
preserved in ``verification/M2-RC2/raw/sidecar-import-before-fix.log`` (the
sidecar transitively loaded ``infrastructure.filesystem``,
``infrastructure.sqlite``, ``infrastructure.sqlite.reading_export`` and
``domain.books.entities``); the post-fix gate lives in
``tests/m2_resource_channel/test_sidecar_isolation.py``.
"""

__all__ = ["filesystem", "sqlite"]


def __getattr__(name: str):
    if name == "filesystem":
        import infrastructure.filesystem as module
    elif name == "sqlite":
        import infrastructure.sqlite as module
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = module
    return module
