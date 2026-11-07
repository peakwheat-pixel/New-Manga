"""Versioned schema definitions for the unified SQLite persistence.

v1 (TASK-006, immutable): books/chapters/pages as the minimal FK chain for
artifacts, the artifact revision tables, and the infrastructure metadata
tables. The v1 DDL encodes the TASK-002 §2.1 frozen invariant "the current
pointer must reference a revision of the same artifact" as a composite
foreign key ``media_artifacts(current_revision_id, artifact_id) →
artifact_revisions(artifact_revision_id, artifact_id)`` (DEFERRABLE).

v2 (TASK-029, per the frozen TASK-028 design §3): completes Book/Chapter
columns, adds full Page import columns (NULL-tolerant for v1 structural
placeholder pages), tags/book_tags, and regions/region_revisions with the
same composite deferred FK pattern plus a no-current-clearing trigger.
v3 (TASK-013): adds the durable Pipeline run graph, stage projections and
redacted default snapshot configuration. v1/v2 statements are never edited.
v1 statements are never edited; each version is an additive migration.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

SCHEMA_VERSION_V1 = 1
SCHEMA_VERSION_V2 = 2
SCHEMA_VERSION_V3 = 3
SCHEMA_VERSION_V4 = 4
SCHEMA_VERSION_V5 = 5
#: PLUGIN-RUNTIME-1 (design §4.1–§4.4, D2/D5): additive plugin state + audit.
SCHEMA_VERSION_V6 = 6
#: FEA-09 (C-15 v1.0 frozen DDL): source storage — six Source tables plus
#: pages.source_mode/integrity_status; migration backfills legacy complete set.
SCHEMA_VERSION_V7 = 7
#: FEA-11 (C-17 v1.0 frozen DDL, §2): source sync — plans, durable
#: operations, binding publications (read gates) and revision lineage.
#: Pure additive empty tables; v1–v7 SQL/name/checksum stay byte-identical.
SCHEMA_VERSION_V8 = 8
#: FEA-12-CORE-C04B-INDEX-L4-1 (frozen record §4A `L-4`): the C-04b v1.2
#: artifact membership predicate (``media_artifacts.book_id = ?``) had no
#: supporting index, so every book-scoped artifact query degraded to a full
#: scan whose cost grew with the whole-library artifact count. v9 adds
#: exactly one index; v1–v8 SQL/name/checksum stay byte-identical.
SCHEMA_VERSION_V9 = 9

MIGRATION_V1_NAME = "v1__storage_base"

MIGRATION_V1_SQL = """
CREATE TABLE books (
    book_id TEXT PRIMARY KEY CHECK (length(book_id) > 0),
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE TABLE chapters (
    chapter_id TEXT PRIMARY KEY CHECK (length(chapter_id) > 0),
    book_id TEXT NOT NULL REFERENCES books(book_id),
    title TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);
CREATE INDEX idx_chapters_book_id ON chapters(book_id);

CREATE TABLE pages (
    page_id TEXT PRIMARY KEY CHECK (length(page_id) > 0),
    chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);
CREATE INDEX idx_pages_chapter_sort ON pages(chapter_id, sort_order);

CREATE TABLE media_artifacts (
    artifact_id TEXT PRIMARY KEY CHECK (length(artifact_id) > 0),
    book_id TEXT NOT NULL REFERENCES books(book_id),
    chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    artifact_type TEXT NOT NULL CHECK (artifact_type IN (
        'original', 'thumbnail', 'detection_overlay', 'mask', 'clean',
        'translated', 'render_preview', 'export', 'debug_ocr', 'debug_detection')),
    current_revision_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (page_id) REFERENCES pages(page_id),
    FOREIGN KEY (current_revision_id, artifact_id) REFERENCES
        artifact_revisions(artifact_revision_id, artifact_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX idx_media_artifacts_page ON media_artifacts(page_id, artifact_type);

CREATE TABLE artifact_revisions (
    artifact_revision_id TEXT PRIMARY KEY CHECK (length(artifact_revision_id) > 0),
    artifact_id TEXT NOT NULL REFERENCES media_artifacts(artifact_id),
    revision_no INTEGER NOT NULL CHECK (revision_no >= 1),
    managed_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    integrity_status TEXT NOT NULL DEFAULT 'valid'
        CHECK (integrity_status IN ('unknown', 'valid', 'missing', 'corrupted')),
    last_verified_at TEXT,
    provider_profile_id TEXT,
    model_name TEXT,
    options_json TEXT,
    source_artifact_revision_id TEXT REFERENCES artifact_revisions(artifact_revision_id),
    pipeline_run_id TEXT,
    step_run_id TEXT,
    provenance_json TEXT,
    is_pinned INTEGER NOT NULL DEFAULT 0 CHECK (is_pinned IN (0, 1)),
    created_at TEXT NOT NULL,
    UNIQUE (artifact_id, revision_no),
    UNIQUE (artifact_revision_id, artifact_id)
);
CREATE INDEX idx_artifact_revisions_artifact ON artifact_revisions(artifact_id, revision_no);

CREATE TABLE schema_migrations (
    schema_version INTEGER PRIMARY KEY,
    migration_name TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    checksum TEXT NOT NULL
);

CREATE TABLE application_metadata (
    metadata_key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE backup_records (
    backup_id TEXT PRIMARY KEY CHECK (length(backup_id) > 0),
    backup_type TEXT NOT NULL
        CHECK (backup_type IN ('automatic', 'manual', 'pre_migration', 'pre_restore')),
    managed_path TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    app_version TEXT,
    schema_version INTEGER,
    database_hash TEXT,
    size_bytes INTEGER,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    source_reason TEXT
);

-- TASK-002 §2.1: "失败、冲突或取消不得改变任何 current 指针". The composite
-- deferred FK cannot see the NULL direction (SQLite MATCH SIMPLE), so the
-- database itself enforces that an established current pointer is never
-- cleared back to NULL; the first-version NULL remains legal.
CREATE TRIGGER trg_media_artifacts_current_not_clearable
BEFORE UPDATE ON media_artifacts
FOR EACH ROW
WHEN OLD.current_revision_id IS NOT NULL AND NEW.current_revision_id IS NULL
BEGIN
    SELECT RAISE(ABORT, 'media_artifacts.current_revision_id cannot be cleared once set');
END;
"""


MIGRATION_V2_NAME = "v2__library_region_persistence"

MIGRATION_V2_SQL = """
-- TASK-028 §3.1: complete Book entity columns (v1 rows keep defaults).
ALTER TABLE books ADD COLUMN original_title TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN author TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN publisher TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN series_title TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN description TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN source_language TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN target_language TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN source_url TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN notes TEXT NOT NULL DEFAULT '';
ALTER TABLE books ADD COLUMN default_chapter_type TEXT NOT NULL DEFAULT 'paged'
    CHECK (default_chapter_type IN ('paged', 'webtoon'));
ALTER TABLE books ADD COLUMN default_reading_direction TEXT NOT NULL DEFAULT 'rtl'
    CHECK (default_reading_direction IN ('rtl', 'ltr', 'vertical'));
ALTER TABLE books ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0
    CHECK (is_favorite IN (0, 1));
ALTER TABLE books ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0
    CHECK (is_archived IN (0, 1));
ALTER TABLE books ADD COLUMN last_opened_at TEXT;

-- TASK-028 §3.1: complete Chapter entity columns.
ALTER TABLE chapters ADD COLUMN chapter_number TEXT NOT NULL DEFAULT '';
ALTER TABLE chapters ADD COLUMN subtitle TEXT NOT NULL DEFAULT '';
ALTER TABLE chapters ADD COLUMN import_order INTEGER NOT NULL DEFAULT 0;
ALTER TABLE chapters ADD COLUMN chapter_type TEXT NOT NULL DEFAULT 'paged'
    CHECK (chapter_type IN ('paged', 'webtoon'));
ALTER TABLE chapters ADD COLUMN reading_direction TEXT NOT NULL DEFAULT 'rtl'
    CHECK (reading_direction IN ('rtl', 'ltr', 'vertical'));
ALTER TABLE chapters ADD COLUMN notes TEXT NOT NULL DEFAULT '';

-- TASK-028 §3.1: Page import columns. NULL-tolerant so v1 structural
-- placeholder pages (artifact FK anchors) survive without forged provenance;
-- non-NULL values must satisfy the basic integrity CHECKs.
ALTER TABLE pages ADD COLUMN source_filename TEXT;
ALTER TABLE pages ADD COLUMN source_order INTEGER
    CHECK (source_order IS NULL OR source_order >= 0);
ALTER TABLE pages ADD COLUMN source_hash TEXT
    CHECK (source_hash IS NULL OR length(source_hash) > 0);
ALTER TABLE pages ADD COLUMN source_size_bytes INTEGER
    CHECK (source_size_bytes IS NULL OR source_size_bytes >= 0);
ALTER TABLE pages ADD COLUMN width INTEGER CHECK (width IS NULL OR width > 0);
ALTER TABLE pages ADD COLUMN height INTEGER CHECK (height IS NULL OR height > 0);
ALTER TABLE pages ADD COLUMN managed_original_ref TEXT
    CHECK (managed_original_ref IS NULL OR length(managed_original_ref) > 0);
ALTER TABLE pages ADD COLUMN page_locked INTEGER NOT NULL DEFAULT 0
    CHECK (page_locked IN (0, 1));
ALTER TABLE pages ADD COLUMN review_state TEXT
    CHECK (review_state IS NULL OR review_state IN
        ('unreviewed', 'needs_review', 'confirmed'));
ALTER TABLE pages ADD COLUMN overall_status TEXT
    CHECK (overall_status IS NULL OR overall_status IN
        ('not_started', 'pending', 'running', 'completed', 'stale',
         'failed', 'skipped', 'interrupted', 'cancelled'));
CREATE INDEX idx_pages_chapter_source_order ON pages(chapter_id, source_order);

-- TASK-028 §3.2: free-form user tags. No UNIQUE(name): LibraryService owns
-- duplicate checks via DuplicateTagName (exact match, no normalization).
CREATE TABLE tags (
    tag_id TEXT PRIMARY KEY CHECK (length(tag_id) > 0),
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE book_tags (
    book_id TEXT NOT NULL REFERENCES books(book_id),
    tag_id TEXT NOT NULL REFERENCES tags(tag_id),
    PRIMARY KEY (book_id, tag_id)
);
CREATE INDEX idx_book_tags_tag_id ON book_tags(tag_id);

-- TASK-028 §3.4: region current state (queryable) + immutable history.
CREATE TABLE regions (
    region_id TEXT PRIMARY KEY CHECK (length(region_id) > 0),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    region_type TEXT NOT NULL
        CHECK (region_type IN ('speech', 'narration', 'sfx', 'title', 'note', 'other')),
    reading_order INTEGER NOT NULL DEFAULT 0,
    geometry_json TEXT NOT NULL CHECK (length(geometry_json) > 0),
    text_json TEXT NOT NULL CHECK (length(text_json) > 0),
    style_json TEXT NOT NULL CHECK (length(style_json) > 0),
    sfx_policy TEXT NOT NULL DEFAULT 'skip'
        CHECK (sfx_policy IN ('skip', 'translate', 'manual')),
    region_locked INTEGER NOT NULL DEFAULT 0 CHECK (region_locked IN (0, 1)),
    translation_locked INTEGER NOT NULL DEFAULT 0 CHECK (translation_locked IN (0, 1)),
    inpaint_locked INTEGER NOT NULL DEFAULT 0 CHECK (inpaint_locked IN (0, 1)),
    current_revision_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    -- TASK-002 §2.1 composite deferred FK (same pattern as media_artifacts):
    -- current must reference a revision of the same region; NULL is legal
    -- only until the first revision lands in the same transaction. SQLite
    -- resolves the forward reference to region_revisions at runtime.
    FOREIGN KEY (current_revision_id, region_id) REFERENCES
        region_revisions(region_revision_id, region_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX idx_regions_page_order ON regions(page_id, reading_order);

CREATE TABLE region_revisions (
    region_revision_id TEXT PRIMARY KEY CHECK (length(region_revision_id) > 0),
    region_id TEXT NOT NULL REFERENCES regions(region_id),
    revision_no INTEGER NOT NULL CHECK (revision_no >= 1),
    snapshot_json TEXT NOT NULL CHECK (length(snapshot_json) > 0),
    origin TEXT NOT NULL
        CHECK (origin IN ('machine', 'user', 'imported', 'restored')),
    review_state TEXT NOT NULL
        CHECK (review_state IN ('unreviewed', 'needs_review', 'confirmed')),
    is_pinned INTEGER NOT NULL DEFAULT 0 CHECK (is_pinned IN (0, 1)),
    source_run_id TEXT,
    source_step_run_id TEXT,
    restored_from_revision_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (region_id, revision_no),
    UNIQUE (region_revision_id, region_id),
    -- Restore provenance must reference a revision of the same region.
    FOREIGN KEY (restored_from_revision_id, region_id) REFERENCES
        region_revisions(region_revision_id, region_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX idx_region_revisions_region ON region_revisions(region_id, revision_no);

-- TASK-002 §2.1: an established current pointer is never cleared to NULL
-- (the composite FK cannot see the NULL direction).
CREATE TRIGGER trg_regions_current_not_clearable
BEFORE UPDATE ON regions
FOR EACH ROW
WHEN OLD.current_revision_id IS NOT NULL AND NEW.current_revision_id IS NULL
BEGIN
    SELECT RAISE(ABORT, 'regions.current_revision_id cannot be cleared once set');
END;
"""


MIGRATION_V3_NAME = "v3__production_pipeline_persistence"

MIGRATION_V3_SQL = """
-- TASK-013: the JSON columns preserve the immutable domain snapshot while
-- the child tables keep the execution graph queryable and recoverable.
CREATE TABLE pipeline_runs (
    run_id TEXT PRIMARY KEY CHECK (length(run_id) > 0),
    command_type TEXT NOT NULL,
    scope_type TEXT NOT NULL,
    requested_targets_json TEXT NOT NULL,
    settings_snapshot_json TEXT NOT NULL,
    provider_binding_snapshot_json TEXT NOT NULL,
    constraint_snapshot_ref TEXT,
    context_policy_json TEXT NOT NULL,
    status TEXT NOT NULL,
    planned_step_units INTEGER NOT NULL DEFAULT 0 CHECK (planned_step_units >= 0),
    terminal_step_units INTEGER NOT NULL DEFAULT 0 CHECK (terminal_step_units >= 0),
    pause_requested INTEGER NOT NULL DEFAULT 0 CHECK (pause_requested IN (0, 1)),
    cancel_requested INTEGER NOT NULL DEFAULT 0 CHECK (cancel_requested IN (0, 1)),
    source_run_id TEXT,
    retry_reason TEXT,
    interruption_disposition TEXT,
    termination_reason TEXT,
    fatal_error TEXT,
    run_json TEXT NOT NULL CHECK (length(run_json) > 0),
    updated_at TEXT NOT NULL
);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);

CREATE TABLE pipeline_run_targets (
    run_target_id TEXT PRIMARY KEY CHECK (length(run_target_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('page', 'region')),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    region_id TEXT,
    target_order INTEGER NOT NULL CHECK (target_order >= 0),
    snapshot_json TEXT NOT NULL CHECK (length(snapshot_json) > 0),
    UNIQUE (pipeline_run_id, target_order),
    UNIQUE (pipeline_run_id, target_id)
);
CREATE INDEX idx_pipeline_run_targets_page ON pipeline_run_targets(page_id);

CREATE TABLE pipeline_tasks (
    task_id TEXT PRIMARY KEY CHECK (length(task_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    run_target_id TEXT NOT NULL REFERENCES pipeline_run_targets(run_target_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('page', 'region')),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    region_id TEXT,
    status TEXT NOT NULL,
    units_json TEXT NOT NULL,
    step_run_ids_json TEXT NOT NULL,
    error_code TEXT,
    error_detail TEXT
);
CREATE INDEX idx_pipeline_tasks_run ON pipeline_tasks(pipeline_run_id);

CREATE TABLE step_runs (
    step_run_id TEXT PRIMARY KEY CHECK (length(step_run_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    task_id TEXT NOT NULL REFERENCES pipeline_tasks(task_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    region_id TEXT,
    step_type TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    status TEXT NOT NULL,
    input_refs_json TEXT NOT NULL,
    lock_snapshot_json TEXT NOT NULL,
    retry_no INTEGER NOT NULL DEFAULT 0 CHECK (retry_no >= 0),
    error_code TEXT,
    error_detail TEXT,
    output_json TEXT NOT NULL
);
CREATE INDEX idx_step_runs_run ON step_runs(pipeline_run_id);

CREATE TABLE step_run_input_refs (
    step_run_id TEXT NOT NULL REFERENCES step_runs(step_run_id) ON DELETE CASCADE,
    input_order INTEGER NOT NULL CHECK (input_order >= 0),
    ref_key TEXT NOT NULL,
    revision_id TEXT,
    PRIMARY KEY (step_run_id, input_order)
);

CREATE TABLE step_run_output_refs (
    step_run_id TEXT NOT NULL REFERENCES step_runs(step_run_id) ON DELETE CASCADE,
    output_order INTEGER NOT NULL CHECK (output_order >= 0),
    ref_key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    PRIMARY KEY (step_run_id, output_order)
);

CREATE TABLE step_result_candidates (
    candidate_id TEXT PRIMARY KEY CHECK (length(candidate_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    step_run_id TEXT NOT NULL REFERENCES step_runs(step_run_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    region_id TEXT,
    result_kind TEXT NOT NULL,
    base_revision_id TEXT,
    payload_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX idx_step_result_candidates_run ON step_result_candidates(pipeline_run_id);

CREATE TABLE pipeline_stage_states (
    target_type TEXT NOT NULL CHECK (target_type IN ('page', 'region')),
    target_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (target_type, target_id, stage)
);

CREATE TABLE pipeline_defaults (
    defaults_id INTEGER PRIMARY KEY CHECK (defaults_id = 1),
    settings_json TEXT NOT NULL,
    provider_bindings_json TEXT NOT NULL,
    constraint_snapshot_ref TEXT,
    context_policy_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

MIGRATION_V4_NAME = "v4__reading_export_storage"

MIGRATION_V4_SQL = """
-- T3.1.1: reading progress persistence (D03 §29, AC-READ-002).
-- One row per (book_id, chapter_id, mode); keeps original and translated independent.
CREATE TABLE reading_progress (
    progress_id TEXT PRIMARY KEY CHECK (length(progress_id) > 0),
    book_id TEXT NOT NULL,
    chapter_id TEXT NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('original', 'translated')),
    last_page_id TEXT NOT NULL DEFAULT '',
    scroll_offset_x REAL NOT NULL DEFAULT 0.0,
    scroll_offset_y REAL NOT NULL DEFAULT 0.0,
    progress_percent REAL NOT NULL DEFAULT 0.0,
    last_read_at TEXT NOT NULL DEFAULT '',
    total_read_seconds REAL NOT NULL DEFAULT 0.0,
    updated_at TEXT NOT NULL,
    UNIQUE (book_id, chapter_id, mode)
);
CREATE INDEX idx_reading_progress_book ON reading_progress(book_id);

-- T3.1.1: export history persistence (D03 §31, AC-EXPORT-002).
-- Records terminal export outcomes (completed, skipped, cancelled, failed)
-- with snapshots sufficient to repeat exports with original settings.
CREATE TABLE export_history (
    export_id TEXT PRIMARY KEY CHECK (length(export_id) > 0),
    book_id TEXT NOT NULL,
    chapter_id TEXT NOT NULL,
    pipeline_run_id TEXT,
    export_type TEXT NOT NULL,
    scope_snapshot_json TEXT NOT NULL DEFAULT '{}',
    output_path TEXT NOT NULL DEFAULT '',
    render_profile_snapshot_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL CHECK (status IN ('completed', 'skipped', 'cancelled', 'failed')),
    file_hash TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    completed_at TEXT NOT NULL DEFAULT '',
    detail TEXT NOT NULL DEFAULT ''
);
CREATE INDEX idx_export_history_created_at ON export_history(created_at DESC);
CREATE INDEX idx_export_history_book ON export_history(book_id, chapter_id);
"""

MIGRATION_V5_NAME = "v5__detach_pipeline_history"

MIGRATION_V5_SQL = """
-- P09-AC3-DELETE-1: Detach pipeline history foreign keys from pages so that
-- deleting books/pages retains all pipeline run, task, and step history without FK failure.
CREATE TABLE pipeline_run_targets_v5 (
    run_target_id TEXT PRIMARY KEY CHECK (length(run_target_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('page', 'region')),
    page_id TEXT NOT NULL,
    region_id TEXT,
    target_order INTEGER NOT NULL CHECK (target_order >= 0),
    snapshot_json TEXT NOT NULL CHECK (length(snapshot_json) > 0),
    UNIQUE (pipeline_run_id, target_order),
    UNIQUE (pipeline_run_id, target_id)
);
INSERT INTO pipeline_run_targets_v5 SELECT * FROM pipeline_run_targets;
DROP TABLE pipeline_run_targets;
ALTER TABLE pipeline_run_targets_v5 RENAME TO pipeline_run_targets;
CREATE INDEX idx_pipeline_run_targets_page ON pipeline_run_targets(page_id);

CREATE TABLE pipeline_tasks_v5 (
    task_id TEXT PRIMARY KEY CHECK (length(task_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    run_target_id TEXT NOT NULL REFERENCES pipeline_run_targets(run_target_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('page', 'region')),
    page_id TEXT NOT NULL,
    region_id TEXT,
    status TEXT NOT NULL,
    units_json TEXT NOT NULL,
    step_run_ids_json TEXT NOT NULL,
    error_code TEXT,
    error_detail TEXT
);
INSERT INTO pipeline_tasks_v5 SELECT * FROM pipeline_tasks;
DROP TABLE pipeline_tasks;
ALTER TABLE pipeline_tasks_v5 RENAME TO pipeline_tasks;
CREATE INDEX idx_pipeline_tasks_run ON pipeline_tasks(pipeline_run_id);

CREATE TABLE step_runs_v5 (
    step_run_id TEXT PRIMARY KEY CHECK (length(step_run_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    task_id TEXT NOT NULL REFERENCES pipeline_tasks(task_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    page_id TEXT NOT NULL,
    region_id TEXT,
    step_type TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    status TEXT NOT NULL,
    input_refs_json TEXT NOT NULL,
    lock_snapshot_json TEXT NOT NULL,
    retry_no INTEGER NOT NULL DEFAULT 0 CHECK (retry_no >= 0),
    error_code TEXT,
    error_detail TEXT,
    output_json TEXT NOT NULL
);
INSERT INTO step_runs_v5 SELECT * FROM step_runs;
DROP TABLE step_runs;
ALTER TABLE step_runs_v5 RENAME TO step_runs;
CREATE INDEX idx_step_runs_run ON step_runs(pipeline_run_id);

CREATE TABLE step_result_candidates_v5 (
    candidate_id TEXT PRIMARY KEY CHECK (length(candidate_id) > 0),
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    step_run_id TEXT NOT NULL REFERENCES step_runs(step_run_id) ON DELETE CASCADE,
    target_id TEXT NOT NULL,
    page_id TEXT NOT NULL,
    region_id TEXT,
    result_kind TEXT NOT NULL,
    base_revision_id TEXT,
    payload_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
INSERT INTO step_result_candidates_v5 SELECT * FROM step_result_candidates;
DROP TABLE step_result_candidates;
ALTER TABLE step_result_candidates_v5 RENAME TO step_result_candidates;
CREATE INDEX idx_step_result_candidates_run ON step_result_candidates(pipeline_run_id);

CREATE TABLE book_cleanup_manifests (
    book_id TEXT PRIMARY KEY CHECK (length(book_id) > 0),
    targets_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class Migration:
    schema_version: int
    migration_name: str
    sql: str

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.sql.encode("utf-8")).hexdigest()


MIGRATION_V6_NAME = "v6__plugin_runtime"

MIGRATION_V6_SQL = """
-- PLUGIN-RUNTIME-1 (design §4.1-§4.4; decision D2/D5): local plugin state and
-- an append-only audit ledger. Both tables start empty, so every existing
-- database gains the schema without changing any current behaviour.
-- `plugin_id = '__global__'` carries the global `plugins.enabled` switch (a
-- disabled-by-default kill switch, design §4.3); every other row is one
-- discovered plugin.
CREATE TABLE plugin_state (
    plugin_id TEXT PRIMARY KEY CHECK (length(plugin_id) > 0),
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    manifest_json TEXT,
    installed_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_error TEXT
);

-- One row per load/reject/enable/disable/hook/error event. `detail_json` is
-- a closed, non-sensitive projection (never paths outside the plugin root or
-- user payload bytes).
CREATE TABLE plugin_events (
    event_id TEXT PRIMARY KEY CHECK (length(event_id) > 0),
    plugin_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'load_ok', 'load_rejected', 'enabled', 'disabled',
        'hook_invoked', 'plugin_error'
    )),
    hook_name TEXT,
    detail_json TEXT NOT NULL DEFAULT '{}',
    occurred_at TEXT NOT NULL
);
CREATE INDEX idx_plugin_events_plugin ON plugin_events(plugin_id, occurred_at);
CREATE INDEX idx_plugin_events_type ON plugin_events(event_type, occurred_at);
"""


MIGRATION_V7_NAME = "v7__source_storage"

#: The SQL below is the frozen C-15 v1.0 §2 block, copied verbatim
#: (doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md, extract 口径同 PREREQ-1 r7
#: validate_c15_ddl.extract_v7; comments preserved per C-15 §2).
MIGRATION_V7_SQL = """-- 2.1 pages：source mode + 完整性（新列默认 incomplete；迁移回填旧 complete 集）
ALTER TABLE pages ADD COLUMN source_mode TEXT NOT NULL DEFAULT 'managed'
    CHECK (source_mode IN ('managed', 'referenced'));
ALTER TABLE pages ADD COLUMN integrity_status TEXT NOT NULL DEFAULT 'incomplete'
    CHECK (integrity_status IN ('incomplete', 'complete'));
UPDATE pages SET integrity_status = 'complete'
 WHERE source_hash IS NOT NULL AND managed_original_ref IS NOT NULL
   AND width IS NOT NULL AND width > 0 AND height IS NOT NULL AND height > 0;

-- 2.2 源
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY CHECK (length(source_id) > 0),
    source_kind TEXT NOT NULL CHECK (source_kind IN ('image', 'folder', 'zip', 'cbz', 'pdf')),
    display_name TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

-- 2.3 源位置/授权绑定：不保存绝对路径；同物理身份唯一（I-3）
CREATE TABLE source_locations (
    location_id TEXT PRIMARY KEY CHECK (length(location_id) > 0),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    registry_id TEXT NOT NULL CHECK (length(registry_id) > 0),
    authorization_generation INTEGER NOT NULL CHECK (authorization_generation >= 1),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    volume_serial INTEGER NOT NULL CHECK (volume_serial >= 0),
    file_id INTEGER NOT NULL CHECK (file_id >= 0),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    mtime_hint TEXT,
    observed_at TEXT NOT NULL,
    last_verified_at TEXT,
    is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1)),
    created_at TEXT NOT NULL,
    UNIQUE (source_id, location_id),
    UNIQUE (source_id, content_digest, volume_serial, file_id)
);
CREATE INDEX idx_source_locations_source ON source_locations(source_id, is_current);
CREATE UNIQUE INDEX uq_source_locations_current
    ON source_locations(source_id) WHERE is_current = 1;

-- 2.4 内容版本（content identity；rendition 观察在 entries 行）
CREATE TABLE source_versions (
    version_id TEXT PRIMARY KEY CHECK (length(version_id) > 0),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    location_id TEXT NOT NULL,
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    observed_at TEXT NOT NULL,
    superseded_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (source_id, version_id),
    UNIQUE (source_id, content_digest),
    FOREIGN KEY (source_id, location_id) REFERENCES source_locations(source_id, location_id)
);
CREATE INDEX idx_source_versions_source ON source_versions(source_id, observed_at);

-- 2.5 容器成员/文件条目：行键 (source, version, entry)；稳定排序键版本内唯一
CREATE TABLE source_entries (
    source_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    entry_id TEXT NOT NULL CHECK (length(entry_id) > 0),
    locator TEXT NOT NULL CHECK (length(locator) > 0),
    ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
    stable_sort_key TEXT NOT NULL CHECK (length(stable_sort_key) > 0),
    content_digest_kind TEXT NOT NULL CHECK (content_digest_kind IN ('encoded', 'page-identity')),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    encoded_digest TEXT CHECK (encoded_digest IS NULL OR length(encoded_digest) = 64),
    pixel_digest TEXT CHECK (pixel_digest IS NULL OR length(pixel_digest) = 64),
    pixel_digest_algorithm TEXT CHECK (pixel_digest_algorithm IS NULL
        OR pixel_digest_algorithm = 'pixel-digest/1'),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    mime_type TEXT,
    width INTEGER CHECK (width IS NULL OR width > 0),
    height INTEGER CHECK (height IS NULL OR height > 0),
    orientation INTEGER CHECK (orientation IS NULL OR orientation IN (1, 3, 6, 8)),
    decoder_name TEXT NOT NULL DEFAULT '',
    decoder_version TEXT NOT NULL DEFAULT '',
    decoder_params_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    PRIMARY KEY (source_id, version_id, entry_id),
    UNIQUE (version_id, ordinal),
    UNIQUE (version_id, stable_sort_key),
    FOREIGN KEY (source_id, version_id) REFERENCES source_versions(source_id, version_id)
);
CREATE INDEX idx_source_entries_identity ON source_entries(source_id, entry_id);
CREATE INDEX idx_source_entries_digest ON source_entries(version_id, content_digest);

-- 2.6 页绑定：项目（book）内 entry 当前唯一；每页 current binding 唯一
CREATE TABLE page_bindings (
    binding_id TEXT PRIMARY KEY CHECK (length(binding_id) > 0),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    project_id TEXT NOT NULL REFERENCES books(book_id),
    binding_version INTEGER NOT NULL CHECK (binding_version >= 1),
    source_id TEXT NOT NULL,
    entry_id TEXT NOT NULL,
    accepted_source_version TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('healthy', 'needs_confirmation', 'missing', 'superseded')),
    previous_binding_id TEXT REFERENCES page_bindings(binding_id),
    authorization_generation INTEGER NOT NULL CHECK (authorization_generation >= 1),
    authorized_at TEXT NOT NULL,
    verified_digest TEXT NOT NULL CHECK (length(verified_digest) = 64),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (page_id, binding_version),
    FOREIGN KEY (source_id, accepted_source_version)
        REFERENCES source_versions(source_id, version_id),
    FOREIGN KEY (source_id, accepted_source_version, entry_id)
        REFERENCES source_entries(source_id, version_id, entry_id)
);
CREATE UNIQUE INDEX uq_page_bindings_current
    ON page_bindings(page_id) WHERE status <> 'superseded';
CREATE UNIQUE INDEX uq_page_bindings_project_entry
    ON page_bindings(project_id, entry_id) WHERE status <> 'superseded';
CREATE INDEX idx_page_bindings_source ON page_bindings(source_id, accepted_source_version);

-- 2.7 rendition 缓存元数据（可再生产物；只允许 decoded/re-encoded rendition，禁 raw user-source 字节）
CREATE TABLE rendition_cache (
    cache_key TEXT PRIMARY KEY CHECK (length(cache_key) > 0),
    source_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    entry_id TEXT NOT NULL,
    rendition_kind TEXT NOT NULL
        CHECK (rendition_kind IN ('thumbnail', 'tile', 'pdf_raster', 'archive_page', 'page_preview')),
    decoder_name TEXT NOT NULL,
    decoder_version TEXT NOT NULL,
    params_digest TEXT NOT NULL CHECK (length(params_digest) = 64),
    rel_path TEXT NOT NULL CHECK (length(rel_path) > 0),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    created_at TEXT NOT NULL,
    last_used_at TEXT NOT NULL,
    active_references INTEGER NOT NULL DEFAULT 0 CHECK (active_references >= 0),
    FOREIGN KEY (source_id, version_id, entry_id)
        REFERENCES source_entries(source_id, version_id, entry_id)
);
CREATE INDEX idx_rendition_cache_lru ON rendition_cache(last_used_at);
CREATE INDEX idx_rendition_cache_source ON rendition_cache(source_id, version_id, entry_id);
"""


MIGRATION_V8_NAME = "v8__source_sync"

#: The SQL below is the frozen C-17 v1.0 §2 block, copied verbatim (doc/plan/
#: FEA-C17_SOURCE_SYNC_DRAFT.md §2). No ON DELETE CASCADE (this migration
#: decides no deletion history); JSON TEXT closed-shape/canonical/cross-row
#: guards are application-layer duties (C-17 §2.2), not DDL claims.
MIGRATION_V8_SQL = """CREATE TABLE source_sync_plans (
    plan_id TEXT NOT NULL PRIMARY KEY CHECK (length(plan_id) BETWEEN 1 AND 128),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    kind TEXT NOT NULL CHECK (kind IN ('relink','repoint','resync')),
    state TEXT NOT NULL CHECK (state IN ('draft','previewed','confirmed','applied','stale')),
    plan_digest TEXT NOT NULL CHECK (length(plan_digest)=64 AND plan_digest NOT GLOB '*[^0-9a-f]*'),
    body_json TEXT NOT NULL CHECK (length(body_json)>1),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    previewed_at TEXT,
    confirmed_at TEXT,
    applied_at TEXT,
    stale_reason TEXT CHECK (stale_reason IS NULL OR stale_reason IN
        ('expired','source','binding','authorization','scope','manual','decision','cancelled')),
    CHECK (state NOT IN ('previewed','confirmed','applied') OR previewed_at IS NOT NULL),
    CHECK (state NOT IN ('confirmed','applied') OR confirmed_at IS NOT NULL),
    CHECK ((state='applied')=(applied_at IS NOT NULL)),
    CHECK ((state='stale')=(stale_reason IS NOT NULL)),
    UNIQUE (plan_id,plan_digest,kind)
);
CREATE INDEX idx_source_sync_plans_source_state ON source_sync_plans(source_id,state);
CREATE INDEX idx_source_sync_plans_expiry ON source_sync_plans(state,expires_at);

CREATE TABLE source_operations (
    operation_id TEXT NOT NULL PRIMARY KEY CHECK (length(operation_id) BETWEEN 1 AND 128),
    plan_id TEXT NOT NULL UNIQUE,
    plan_digest TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('relink','repoint','resync')),
    request_digest TEXT NOT NULL CHECK (length(request_digest)=64 AND request_digest NOT GLOB '*[^0-9a-f]*'),
    state TEXT NOT NULL CHECK (state IN
        ('started','host-authorized','core-committed','acknowledged','failed','recovered')),
    authorization_digest TEXT NOT NULL CHECK (length(authorization_digest)=64 AND authorization_digest NOT GLOB '*[^0-9a-f]*'),
    authorization_json TEXT NOT NULL CHECK (length(authorization_json)>1),
    host_receipt_id TEXT NOT NULL CHECK (length(host_receipt_id) BETWEEN 1 AND 128),
    commit_receipt_json TEXT,
    commit_digest TEXT CHECK (commit_digest IS NULL OR
        (length(commit_digest)=64 AND commit_digest NOT GLOB '*[^0-9a-f]*')),
    error_code TEXT,
    retryable INTEGER NOT NULL DEFAULT 0 CHECK (retryable IN (0,1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    committed_at TEXT,
    acknowledged_at TEXT,
    CHECK ((commit_digest IS NULL)=(commit_receipt_json IS NULL)),
    CHECK ((committed_at IS NULL)=(commit_digest IS NULL)),
    CHECK (state NOT IN ('core-committed','acknowledged','recovered') OR committed_at IS NOT NULL),
    CHECK ((state IN ('acknowledged','recovered'))=(acknowledged_at IS NOT NULL)),
    CHECK ((state='failed')=(error_code IS NOT NULL)),
    FOREIGN KEY (plan_id,plan_digest,kind)
        REFERENCES source_sync_plans(plan_id,plan_digest,kind)
);
CREATE INDEX idx_source_operations_state ON source_operations(state,updated_at);

CREATE TABLE source_binding_publications (
    binding_id TEXT NOT NULL PRIMARY KEY REFERENCES page_bindings(binding_id),
    operation_id TEXT NOT NULL REFERENCES source_operations(operation_id),
    previous_binding_id TEXT REFERENCES page_bindings(binding_id),
    relation TEXT NOT NULL CHECK (relation IN ('same_content','changed','repoint','added','missing')),
    read_gate TEXT NOT NULL CHECK (read_gate IN ('pending','open')),
    opened_at TEXT,
    CHECK ((read_gate='open')=(opened_at IS NOT NULL)),
    CHECK ((relation='added')=(previous_binding_id IS NULL)),
    CHECK (binding_id<>previous_binding_id)
);
CREATE INDEX idx_source_binding_publications_operation ON source_binding_publications(operation_id,read_gate);
CREATE INDEX idx_source_binding_publications_previous ON source_binding_publications(previous_binding_id);

CREATE TABLE source_revision_lineage (
    revision_id TEXT NOT NULL PRIMARY KEY REFERENCES region_revisions(region_revision_id),
    region_id TEXT NOT NULL REFERENCES regions(region_id),
    binding_id TEXT REFERENCES page_bindings(binding_id),
    provenance TEXT NOT NULL CHECK (provenance IN ('captured_v7','native','migrated','legacy_unverified')),
    from_revision_id TEXT REFERENCES region_revisions(region_revision_id),
    operation_id TEXT REFERENCES source_operations(operation_id),
    created_at TEXT NOT NULL,
    CHECK ((provenance='legacy_unverified')=(binding_id IS NULL)),
    CHECK ((provenance='migrated')=(from_revision_id IS NOT NULL)),
    CHECK (revision_id<>from_revision_id)
);
CREATE INDEX idx_source_revision_lineage_binding ON source_revision_lineage(binding_id,region_id);
CREATE INDEX idx_source_revision_lineage_origin ON source_revision_lineage(from_revision_id);
"""


MIGRATION_V9_NAME = "v9__media_artifacts_book_index"

#: The C-04b L-4 index. ``(book_id)`` serves the preview/protected-set
#: membership predicate (C-04b v1.2 §0 第 1 条), the delete-inventory COUNT,
#: the artifact revision-id/pinned enumeration and the transaction's
#: ``DELETE FROM media_artifacts WHERE book_id = ?`` (the last two walk the
#: covering index). A bare ``CREATE INDEX`` is deliberate: a pre-existing
#: conflicting index must fail the migration loudly instead of being recorded
#: as applied without the index; the version gate (migrator.py) already
#: provides idempotence, and the statement plus the ``schema_migrations`` row
#: share one transaction, so a failure leaves the database at v8 with no
#: index residue.
MIGRATION_V9_SQL = "CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);"


def default_migrations() -> tuple[Migration, ...]:
    return (
        Migration(SCHEMA_VERSION_V1, MIGRATION_V1_NAME, MIGRATION_V1_SQL),
        Migration(SCHEMA_VERSION_V2, MIGRATION_V2_NAME, MIGRATION_V2_SQL),
        Migration(SCHEMA_VERSION_V3, MIGRATION_V3_NAME, MIGRATION_V3_SQL),
        Migration(SCHEMA_VERSION_V4, MIGRATION_V4_NAME, MIGRATION_V4_SQL),
        Migration(SCHEMA_VERSION_V5, MIGRATION_V5_NAME, MIGRATION_V5_SQL),
        Migration(SCHEMA_VERSION_V6, MIGRATION_V6_NAME, MIGRATION_V6_SQL),
        Migration(SCHEMA_VERSION_V7, MIGRATION_V7_NAME, MIGRATION_V7_SQL),
        Migration(SCHEMA_VERSION_V8, MIGRATION_V8_NAME, MIGRATION_V8_SQL),
        Migration(SCHEMA_VERSION_V9, MIGRATION_V9_NAME, MIGRATION_V9_SQL),
    )
