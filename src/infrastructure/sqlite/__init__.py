"""SQLite persistence adapters."""

from infrastructure.sqlite.reading_export import (
    LegacyCorruptJsonError,
    LegacyImportError,
    LegacyInvalidRecordError,
    LegacyInvalidStructureError,
    SqliteExportHistoryStore,
    SqliteHistoryDocumentStore,
    SqliteProgressDocumentStore,
    SqliteReadingProgressStore,
    import_legacy_export_history,
    import_legacy_reading_progress,
)

__all__ = [
    "LegacyCorruptJsonError",
    "LegacyImportError",
    "LegacyInvalidRecordError",
    "LegacyInvalidStructureError",
    "SqliteExportHistoryStore",
    "SqliteHistoryDocumentStore",
    "SqliteProgressDocumentStore",
    "SqliteReadingProgressStore",
    "import_legacy_export_history",
    "import_legacy_reading_progress",
]
