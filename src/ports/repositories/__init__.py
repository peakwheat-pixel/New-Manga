"""Repository and storage ports for persistence consumers.

TASK-006 scope: the first slice only needs artifact persistence, managed file
storage, schema migration and database backup contracts. The ports stay free
of sqlite3/PySide6 imports so domain and application layers can depend on
them without violating the TASK-005 architecture guards.
"""

from ports.repositories import artifacts, database, storage

__all__ = ["artifacts", "database", "storage"]
