// M2-RG1 AC2 (GUI console policy, release builds only): the packaged app is a
// GUI-subsystem binary — no console window may appear for the app itself.
// Dev builds (debug_assertions) keep the console on purpose: probe evidence
// includes startup stderr (comment below, dev behavior unchanged).
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

//! M2-RC1/M2-RC2 — Contract-Aligned Large-Media Resource Channel Runtime.
//!
//! Vertical slice: Python Core (reference + catalog authority) ⇄ Tauri/Rust
//! host (`m2res` custom protocol over a stdio control bridge) ⇄ React/WebView
//! (opaque protocol URLs only). Bytes stay outside the JSON/Base64 IPC plane
//! (Contract 1.1 §10); the WebView never sees an OS path (T5.1).
//!
//! RC2 (F-03) command-surface hardening: the WebView-facing invoke surface is
//! the allowlist in [`command_allowlist`] — three resource-channel commands,
//! no catalog registration (`register_catalog` is gone entirely; the catalog
//! is Core/SQLite authority), no TTL override on the production issue shape,
//! and the probe commands exist only in probe mode (host env sets
//! `M2RC1_PROBE_OUT`). `capabilities/m2rc1-commands.json` + the inlined
//! `m2rc1-commands` plugin put every command behind the Tauri ACL for the
//! main window; the hardened CSP replaces the RC1 `csp: null`.
//! M2-IPC1 later added the production-only `core_ping`/`library_list_books`
//! pair, M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3) the
//! production-only `settings_get`/`settings_update_section` pair,
//! SETTINGS-OPEN-B-2 (design §4.3) the production-only
//! `cleanup_preview`/`cleanup_run`/`cleanup_retry_pending` trio, and
//! M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4) the production-only
//! `set_region_type`/`list_regions` and the RC-4 history/restore/render
//! commands — probe/AC1 surfaces remain frozen while production widens.

// console note (updated M2-RG1 r1 rework, P3-1): dev builds keep the console
// on purpose — probe evidence includes startup stderr. Release builds are
// GUI-subsystem (windows_subsystem attribute above); the sidecar spawn points
// carry CREATE_NO_WINDOW, so on Windows the packaged app and its sidecars
// surface no console window while stdio (pipe) semantics stay unchanged.

mod ac1_bridge;
mod core_bridge;
mod credential_manager;
mod host_issuer;
mod library_bridge;
#[cfg(test)]
#[path = "packaged_sidecar_tests.rs"]
mod packaged_sidecar_tests;
mod resource_protocol;
mod settings_bridge;

use ac1_bridge::Ac1Channel;
use core_bridge::{CoreChannel, CoreError, StdioCoreChannel};
use library_bridge::{
    BookSummary, ChapterNavSummary, ExportHistoryResponseView, ExportProgressSnapshotView,
    LibraryChannel, LibraryError, LibrarySpawnConfig, P15CredentialTarget, P15SettingsCommand,
    PermanentlyDeleteBookErrorView, PermanentlyDeleteBookPayload, PermanentlyDeleteBookResult,
    PermanentlyDeleteBooksErrorView, PermanentlyDeleteBooksPayload, PermanentlyDeleteBooksResult,
    PingResult, ResilientLibraryChannel, StdioLibraryChannel, P15_HOST_ONLY_COMMANDS,
};
use resource_protocol::ScopeRoots;
use serde::{Deserialize, Serialize};
use settings_bridge::*;
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use tauri::Manager;
use tauri_plugin_dialog::DialogExt;
use tauri_plugin_opener::OpenerExt;

/// Commands every mode exposes: the product WebView surface. No path-shaped
/// parameter, no TTL parameter, no probe capability.
pub const PRODUCTION_COMMANDS: &[&str] = &[
    "issue_resource_url",
    "revoke_ref",
    "revoke_resource_refs",
    "core_ping",
    "library_list_books",
    // AC1 (R-007): the recycle bin read face.
    "library_list_recycle_bin_books",
    "library_create_book",
    "create_chapter",
    // M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): the settings read/
    // write pair, production-only like the IPC1 commands below.
    "settings_get",
    "settings_update_section",
    // SETTINGS-OPEN-B-2 (design §4.3): the cache/Revision maintenance face
    // (preview / run / retry over the rebuildable webtoon tile cache),
    // production-only like the settings pair above.
    "cleanup_preview",
    "cleanup_run",
    "cleanup_retry_pending",
    // SETTINGS-OPEN-C-2-BACKUP (design §3.4): the .nmbak backup package face
    // (create / list / restore / delete), production-only like the cleanup
    // trio above.
    "backup_create",
    "backup_list",
    "backup_restore",
    "backup_delete",
    // P15-C1 rev 2.7 G21/G22/G23/G24 settings surface (19 commands); production-only.
    "settings_provider_profiles_list",
    "settings_provider_profiles_create",
    "settings_provider_profiles_update",
    "settings_provider_profiles_delete",
    "settings_provider_bindings_set",
    "settings_provider_bindings_clear",
    "settings_provider_bindings_resolve",
    "settings_provider_run_snapshot_get",
    "settings_network_profiles_list",
    "settings_network_profiles_create",
    "settings_network_profiles_update",
    "settings_network_profiles_delete",
    "settings_network_profiles_test",
    "settings_network_profile_default_set",
    "settings_network_profile_default_clear",
    "settings_network_profile_resolve",
    "settings_resolve_overrides",
    // G22 credentials are triggered by the WebView without a Secret; the
    // Host collects through native Windows CredUI and binds over trusted stdio.
    "credential_put",
    "credential_clear",
    // M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): the region retype
    // write/read pair, production-only like the settings pair above.
    "set_region_type",
    "list_regions",
    "list_region_revisions",
    "restore_region_revision",
    "rerender_page",
    // M2-PAGE-RESOURCE-RESOLVE-1 (contract rev 1.7 section 5): the page display
    // image resolve, production-only like the RC-4 trio above.
    "resolve_page_resource",
    // M2-PAGE-NAV-PROJECTION-1 (contract rev 1.8 section 5): the read-only
    // page navigation projections, production-only like the resolve above.
    "list_chapters",
    "list_chapter_pages",
    // READER-IPC-1 (contract rev 2.1 §5): opaque Reader projection and
    // progress transport, production-only like the navigation projections.
    "library_get_reader_projection",
    "library_save_reading_progress",
    // HOST-ISSUER-1: user actions use native pickers; refs and paths stay in Rust.
    "library_import_file",
    "library_import_folder",
    "library_start_export",
    // RUN-IPC-1: host transport for the P13-C1 §5.5 Run command surface.
    "library_start_run",
    "library_control_run",
    "library_resume_blocked_run",
    "library_get_run_snapshot",
    "library_get_task_projection",
    "library_retry_failed_targets",
    // EXPORT-REVEAL-1: never accepts a path; Rust resolves this in current Core history.
    "library_reveal_export_folder",
    // EXPORT-IPC-1: host transport for the export control/query surface.
    "library_cancel_export",
    "library_get_export_snapshot",
    "library_get_export_history",
    // P09-AC3-DELETE-1: production-only project-level permanent deletion commands
    "library_delete_book_permanently",
    "library_delete_books_permanently",
];

/// Commands that exist ONLY in probe mode (`M2RC1_PROBE_OUT` set by the
/// evidence runner). In production mode they are not registered, so a
/// WebView invoke fails with "command not found" before any logic runs.
pub const PROBE_ONLY_COMMANDS: &[&str] = &[
    "probe_config",
    "probe_write_results",
    "probe_exit",
    "probe_issue_url",
];

/// Commands removed outright by RC2 (F-03). They must never reappear on any
/// surface: catalog state is Core/SQLite authority (F-03) and cannot be
/// written or fabricated from the host/WebView side.
pub const REMOVED_COMMANDS: &[&str] = &["register_catalog"];

/// M2-AC1 acceptance commands: they exist ONLY in the explicit test startup
/// configuration (`M2AC1_TEST_MODE=1`), never in production or probe mode.
/// The WebView drives the deterministic acceptance loop through them; the
/// production surface stays exactly `PRODUCTION_COMMANDS`.
pub const AC1_TEST_COMMANDS: &[&str] = &["ac1_request", "ac1_write_results", "ac1_exit"];

/// The single source of truth for the WebView-facing command surface.
/// `main` feeds this into the conditional `invoke_handler` registration; the
/// unit tests gate its content (allow/deny matrix, RC2-AC1).
/// Production-only commands added by M2-IPC1 (integration ruling on DSH r2
/// P2-1, option B): they exist solely on the production surface. The frozen
/// RC2/AC1 test-mode surfaces keep their historical 7/6-command shape, so
/// the announcement and the `generate_handler!` registration stay identical
/// in every mode and the runner expectations stay pinned.
pub const IPC1_PRODUCTION_ONLY_COMMANDS: &[&str] = &["core_ping", "library_list_books"];

/// M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): the settings commands
/// are production-only too — the frozen RC2 probe / AC1 test-mode surfaces
/// never gain them (option-B precedent of M2-IPC1).
pub const SETTINGS_PRODUCTION_ONLY_COMMANDS: &[&str] = &["settings_get", "settings_update_section"];

/// SETTINGS-OPEN-B-2 (design §4.3): the cache/Revision maintenance face is
/// production-only too (the option-B precedent): the frozen RC2 probe / AC1
/// test-mode surfaces keep their historical 7/6-command shape and never
/// gain the three cleanup commands.
pub const CLEANUP_PRODUCTION_ONLY_COMMANDS: &[&str] =
    &["cleanup_preview", "cleanup_run", "cleanup_retry_pending"];

/// SETTINGS-OPEN-C-2-BACKUP (design §3.4): the ``.nmbak`` package face is
/// production-only too (the option-B precedent): the frozen RC2 probe / AC1
/// test-mode surfaces keep their historical 7/6-command shape and never gain
/// the four backup commands.
pub const BACKUP_PRODUCTION_ONLY_COMMANDS: &[&str] =
    &["backup_create", "backup_list", "backup_restore", "backup_delete"];

pub const P15_SETTINGS_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "settings_provider_profiles_list",
    "settings_provider_profiles_create",
    "settings_provider_profiles_update",
    "settings_provider_profiles_delete",
    "settings_provider_bindings_set",
    "settings_provider_bindings_clear",
    "settings_provider_bindings_resolve",
    "settings_provider_run_snapshot_get",
    "settings_network_profiles_list",
    "settings_network_profiles_create",
    "settings_network_profiles_update",
    "settings_network_profiles_delete",
    "settings_network_profiles_test",
    "settings_network_profile_default_set",
    "settings_network_profile_default_clear",
    "settings_network_profile_resolve",
    "settings_resolve_overrides",
    "credential_put",
    "credential_clear",
];

/// M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): the region retype pair is
/// production-only as well (same option-B precedent — the frozen test-mode
/// surfaces keep their historical shape).
pub const RETYPE_PRODUCTION_ONLY_COMMANDS: &[&str] = &["set_region_type", "list_regions"];

/// RC-4 commands stay production-only; probe and AC1 surfaces retain their
/// historical shape.
pub const RC4_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "list_region_revisions",
    "restore_region_revision",
    "rerender_page",
];

/// M2-PAGE-RESOURCE-RESOLVE-1: the page display image resolve stays
/// production-only; probe and AC1 surfaces retain their historical shape.
pub const PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS: &[&str] = &["resolve_page_resource"];

/// M2-PAGE-NAV-PROJECTION-1 (contract rev 1.8 §5): the read-only page
/// navigation projections stay production-only; probe and AC1 surfaces
/// retain their historical shape.
pub const PAGE_NAV_PRODUCTION_ONLY_COMMANDS: &[&str] = &["list_chapters", "list_chapter_pages"];

/// READER-IPC-1 (contract rev 2.1 §5): reader commands stay production-only;
/// probe and AC1 surfaces retain their historical shape.
pub const READER_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "library_get_reader_projection",
    "library_save_reading_progress",
];

pub const HOST_ISSUER_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "library_import_file",
    "library_import_folder",
    "library_start_export",
];

/// RUN-IPC-1: P13-C1 (contract rev 2.0 §5.5) froze the Run command surface in
/// the Core but no host outlet existed, so the Workbench (P14) could not start
/// or inspect a Run at all. These six commands are the host transport for that
/// frozen surface and stay production-only, so the probe/AC1 surfaces keep
/// their historical shape (option-B precedent).
pub const RUN_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "library_start_run",
    "library_control_run",
    "library_resume_blocked_run",
    "library_get_run_snapshot",
    "library_get_task_projection",
    "library_retry_failed_targets",
];
/// EXPORT-REVEAL-1 adds this Tauri action to production only; probe and AC1
/// keep their frozen command surfaces.
pub const EXPORT_REVEAL_PRODUCTION_ONLY_COMMANDS: &[&str] = &["library_reveal_export_folder"];

/// EXPORT-IPC-1 (contract rev 2.5 §5.8): Export control/query commands.
/// Production-only transport for the frozen Core export control and query surface.
pub const EXPORT_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "library_cancel_export",
    "library_get_export_snapshot",
    "library_get_export_history",
];

/// AC1 (R-007): the recycle-bin read face is production-only; probe and AC1
/// keep their frozen historical command surfaces.
pub const RECYCLE_BIN_PRODUCTION_ONLY_COMMANDS: &[&str] = &["library_list_recycle_bin_books"];

pub const CREATE_PRODUCTION_ONLY_COMMANDS: &[&str] = &["library_create_book", "create_chapter"];

pub const DELETE_PRODUCTION_ONLY_COMMANDS: &[&str] = &[
    "library_delete_book_permanently",
    "library_delete_books_permanently",
];

pub fn command_allowlist(probe_mode: bool, ac1_mode: bool) -> Vec<&'static str> {
    let mut commands: Vec<&'static str> = if probe_mode || ac1_mode {
        PRODUCTION_COMMANDS
            .iter()
            .copied()
            .filter(|command| {
                !IPC1_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !SETTINGS_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !CLEANUP_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !P15_SETTINGS_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !RETYPE_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !RC4_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !PAGE_NAV_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !READER_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !HOST_ISSUER_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !RUN_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !EXPORT_REVEAL_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !EXPORT_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !CREATE_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !DELETE_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !RECYCLE_BIN_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !BACKUP_PRODUCTION_ONLY_COMMANDS.contains(command)
            })
            .collect()
    } else {
        PRODUCTION_COMMANDS.to_vec()
    };
    if probe_mode {
        commands.extend_from_slice(PROBE_ONLY_COMMANDS);
    }
    if ac1_mode {
        commands.extend_from_slice(AC1_TEST_COMMANDS);
    }
    commands
}

struct AppState {
    channel: Box<dyn CoreChannel>,
    roots: ScopeRoots,
    fixture_shas: serde_json::Value,
    /// Present only in the M2-AC1 explicit test startup configuration.
    ac1: Option<Ac1Channel>,
    /// Present only in production mode; probe and ac1 modes do not spawn library sidecar.
    library: Option<Box<dyn LibraryChannel>>,
    /// Serializes one-shot credential input/store/bind and clear operations.
    credential_operations: Mutex<()>,
    /// Current preview catalog id by page. Keep one global lock for the
    /// short rerender/revoke/swap sequence so concurrent pages cannot
    /// interleave opaque-resource cleanup; split only if throughput evidence
    /// justifies the extra machinery.
    render_preview_resources: Mutex<HashMap<String, String>>,
}

#[derive(Serialize)]
struct IssuedUrl {
    url: String,
    size: u64,
    opaque_id: String,
}

fn into_issued(issued: core_bridge::IssuedRef) -> Result<IssuedUrl, CoreError> {
    // the issue response already carries the presentation size; a resolve
    // here would renew the sliding TTL before any real consumption happens
    Ok(IssuedUrl {
        url: resource_protocol::build_url(&issued.opaque_id),
        size: issued.size,
        opaque_id: issued.opaque_id,
    })
}

#[tauri::command]
fn core_ping(state: tauri::State<'_, AppState>) -> Result<PingResult, String> {
    // Defensive only (M2-IPC1 ruling on DSH r2 P2-1): in probe/ac1 modes
    // these commands are not registered at all, so the `None` arm is
    // unreachable today; it keeps the `Option` state honest if the spawn
    // gating ever changes.
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .ping()
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_list_books(state: tauri::State<'_, AppState>) -> Result<Vec<BookSummary>, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .list_books()
        .map_err(|error| error.code)
}

/// AC1 (R-007): the recycle bin read face.
///
/// Registered on the production surface so the frontend command actually has a
/// handler. A channel that cannot answer yields its typed error, never an empty
/// list - the two must stay distinguishable all the way to the UI.
#[tauri::command]
fn library_list_recycle_bin_books(
    state: tauri::State<'_, AppState>,
) -> Result<Vec<BookSummary>, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .list_recycle_bin_books()
        .map_err(|error| error.code)
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CreateBookPayload {
    title: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CreateChapterPayload {
    book_id: String,
    title: String,
    #[serde(default, deserialize_with = "deserialize_non_null_string")]
    chapter_number: Option<String>,
}

fn deserialize_non_null_string<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    String::deserialize(deserializer).map(Some)
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum LibrarySurfaceCategory {
    Validation,
    NotFound,
    Unavailable,
    Internal,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum LibrarySurfacePhase {
    RequestValidation,
    BookLookup,
    Persistence,
    CoreChannel,
    Unknown,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum LibrarySurfaceAction {
    EditInput,
    SelectBook,
    RetryAfterRefresh,
    ContactSupport,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
enum LibrarySurfaceMessageKey {
    #[serde(rename = "LIBRARY_INVALID_INPUT")]
    InvalidInput,
    #[serde(rename = "LIBRARY_BOOK_NOT_FOUND")]
    BookNotFound,
    #[serde(rename = "LIBRARY_WRITE_FAILED")]
    WriteFailed,
    #[serde(rename = "LIBRARY_UNAVAILABLE")]
    Unavailable,
    #[serde(rename = "LIBRARY_OPERATION_FAILED")]
    OperationFailed,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
struct LibrarySurfaceError {
    category: LibrarySurfaceCategory,
    phase: LibrarySurfacePhase,
    action: LibrarySurfaceAction,
    message_key: LibrarySurfaceMessageKey,
}

impl LibrarySurfaceError {
    fn invalid_input() -> Self {
        Self {
            category: LibrarySurfaceCategory::Validation,
            phase: LibrarySurfacePhase::RequestValidation,
            action: LibrarySurfaceAction::EditInput,
            message_key: LibrarySurfaceMessageKey::InvalidInput,
        }
    }

    fn unavailable() -> Self {
        Self {
            category: LibrarySurfaceCategory::Unavailable,
            phase: LibrarySurfacePhase::CoreChannel,
            action: LibrarySurfaceAction::RetryAfterRefresh,
            message_key: LibrarySurfaceMessageKey::Unavailable,
        }
    }

    fn from_core(error: LibraryError) -> Self {
        match error.code.as_str() {
            "INVALID_REQUEST" | "PROTOCOL_VERSION_UNSUPPORTED" => Self::invalid_input(),
            "TARGET_NOT_FOUND" => Self {
                category: LibrarySurfaceCategory::NotFound,
                phase: LibrarySurfacePhase::BookLookup,
                action: LibrarySurfaceAction::SelectBook,
                message_key: LibrarySurfaceMessageKey::BookNotFound,
            },
            "LIBRARY_WRITE_FAILED" => Self {
                category: LibrarySurfaceCategory::Internal,
                phase: LibrarySurfacePhase::Persistence,
                action: LibrarySurfaceAction::RetryAfterRefresh,
                message_key: LibrarySurfaceMessageKey::WriteFailed,
            },
            _ if error.category == "unavailable" => Self::unavailable(),
            _ => Self {
                category: LibrarySurfaceCategory::Internal,
                phase: LibrarySurfacePhase::Unknown,
                action: LibrarySurfaceAction::ContactSupport,
                message_key: LibrarySurfaceMessageKey::OperationFailed,
            },
        }
    }
}

fn parse_create_book_payload(
    value: Option<serde_json::Value>,
) -> Result<CreateBookPayload, LibrarySurfaceError> {
    serde_json::from_value(value.ok_or_else(LibrarySurfaceError::invalid_input)?)
        .map_err(|_| LibrarySurfaceError::invalid_input())
}

fn parse_create_chapter_payload(
    value: Option<serde_json::Value>,
) -> Result<CreateChapterPayload, LibrarySurfaceError> {
    serde_json::from_value(value.ok_or_else(LibrarySurfaceError::invalid_input)?)
        .map_err(|_| LibrarySurfaceError::invalid_input())
}

#[tauri::command]
fn library_create_book(
    state: tauri::State<'_, AppState>,
    payload: Option<serde_json::Value>,
) -> Result<BookSummary, LibrarySurfaceError> {
    let payload = parse_create_book_payload(payload)?;
    state
        .library
        .as_ref()
        .ok_or_else(LibrarySurfaceError::unavailable)?
        .create_book(&payload.title)
        .map_err(LibrarySurfaceError::from_core)
}

#[tauri::command]
fn create_chapter(
    state: tauri::State<'_, AppState>,
    payload: Option<serde_json::Value>,
) -> Result<ChapterNavSummary, LibrarySurfaceError> {
    let payload = parse_create_chapter_payload(payload)?;
    state
        .library
        .as_ref()
        .ok_or_else(LibrarySurfaceError::unavailable)?
        .create_chapter(
            &payload.book_id,
            &payload.title,
            payload.chapter_number.as_deref(),
        )
        .map_err(LibrarySurfaceError::from_core)
}

/// M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): read the pipeline
/// settings projection. No `section` argument = the full projection;
/// `section` present = that one section (JSON `null` when unset). The host
/// is a pass-through: it never interprets or filters keys — the value-domain
/// authority is the Python Core (write-side validation lives there, BEFORE
/// persistence).
#[tauri::command]
fn settings_get(
    state: tauri::State<'_, AppState>,
    section: Option<String>,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .get_settings(section.as_deref())
        .map_err(|error| error.code)
}

/// M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): upsert one settings
/// section through the Core's `settings.update_section` (which runs the
/// typed write-side validation — sfx.policy three-value gate — BEFORE any
/// persistence, per the M2-SFX-ENTRY r1 R4 lesson). The typed rejection
/// (`INVALID_REQUEST`) propagates verbatim; the result is the full updated
/// projection so one round trip re-syncs the caller.
#[tauri::command]
fn settings_update_section(
    state: tauri::State<'_, AppState>,
    section: String,
    values: serde_json::Value,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .update_settings_section(&section, &values)
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-B-2 (design §4.3): read-only pre-flight of the controlled
/// cache cleanup -- which rebuildable cache files would be removed, how many
/// bytes they occupy, and how many failed removals are still pending. The
/// host is a pass-through: path authority and the never-clean predicate live
/// in the Python Core (`CleanupService`); this command never accepts a path
/// and never guesses at the cache population.
#[tauri::command]
fn cleanup_preview(state: tauri::State<'_, AppState>) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .cleanup_preview()
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-B-2 (design §4.3): run the controlled cleanup now. The
/// result is the Core's structured outcome (per-target ok/failed/skipped plus
/// the three counts); failed removals stay persisted in the Core's
/// `pending_cleanups` ledger, so the retry face below can settle them. No user
/// source file, current/pinned Revision or business row is addressable.
#[tauri::command]
fn cleanup_run(state: tauri::State<'_, AppState>) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .cleanup_run()
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-B-2 (design §4.3): retry the persisted pending removals.
/// Same outcome projection as `cleanup_run`; the Core re-checks the never-clean
/// predicate on every pending entry and only settled entries leave the ledger.
#[tauri::command]
fn cleanup_retry_pending(state: tauri::State<'_, AppState>) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .cleanup_retry_pending()
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-C-2-BACKUP (design §3.4): create one ``manual`` ``.nmbak``
/// package. The Core owns the package format, the fixed backup root and the
/// read-back verification; the host never builds a path and the WebView never
/// picks a directory (export is a separate host-only surface).
#[tauri::command]
fn backup_create(
    state: tauri::State<'_, AppState>,
    backup_type: Option<String>,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .backup_create(backup_type.as_deref().unwrap_or("manual"))
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-C-2-BACKUP (design §3.4): list the packages found in the
/// Core's backup root. A package whose manifest cannot be read is still
/// listed (``verified=false``) — hiding it would look like a lost backup.
#[tauri::command]
fn backup_list(state: tauri::State<'_, AppState>) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .backup_list()
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-C-2-BACKUP (design §3.3): overwrite-restore from one
/// verified package. ``confirm_restore`` is the explicit second confirmation
/// the Core also re-checks; the Core refuses while a Run is active
/// (``BACKUP_RESTORE_BUSY``) and always writes a ``pre_restore`` package
/// first, so a failed restore keeps its rollback point.
#[tauri::command]
fn backup_restore(
    state: tauri::State<'_, AppState>,
    backup_id: String,
    confirm_restore: bool,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .backup_restore(&backup_id, confirm_restore)
        .map_err(|error| error.code)
}

/// SETTINGS-OPEN-C-2-BACKUP (design §3.4): delete one package. Idempotent
/// from the caller's point of view: a second delete answers
/// ``BACKUP_NOT_FOUND`` (not_found, non-retryable) instead of failing
/// mysteriously.
#[tauri::command]
fn backup_delete(
    state: tauri::State<'_, AppState>,
    backup_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .backup_delete(&backup_id)
        .map_err(|error| error.code)
}

/// M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): retype one region through
/// the Core's `set_region_type` (ONE new revision via the existing commit
/// seam, origin=user, EV-8 policy re-snapshot — all decided Core-side). The
/// host is a pass-through: value-domain authority (the RegionType six-value
/// closed set) and the optimistic guard live in the Python Core BEFORE any
/// persistence; the typed rejection propagates verbatim and the result is
/// the post-retype effective state (one round trip, no second query).
#[tauri::command]
fn set_region_type(
    state: tauri::State<'_, AppState>,
    region_id: String,
    new_region_type: String,
    expected_revision: Option<i64>,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .set_region_type(&region_id, &new_region_type, expected_revision)
        .map_err(|error| error.code)
}

/// M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): the RegionListSummary
/// read channel — the minimal five-field DTO per live region in
/// reading_order. A page with no rows reads as `{"regions": []}` (NOT an
/// error, footnote a); the host never interprets the summaries.
#[tauri::command]
fn list_regions(
    state: tauri::State<'_, AppState>,
    page_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .list_regions(&page_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn list_region_revisions(
    state: tauri::State<'_, AppState>,
    region_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .list_region_revisions(&region_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn restore_region_revision(
    state: tauri::State<'_, AppState>,
    region_id: String,
    revision_no: i64,
    expected_revision: i64,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .restore_region_revision(&region_id, revision_no, expected_revision)
        .map_err(|error| error.code)
}

#[tauri::command]
fn rerender_page(
    state: tauri::State<'_, AppState>,
    page_id: String,
) -> Result<serde_json::Value, String> {
    rerender_page_from_core(&state, &page_id)
}

fn rerender_page_from_core(state: &AppState, page_id: &str) -> Result<serde_json::Value, String> {
    // Acquire before Core commits and hold through revocation/swap. Otherwise
    // concurrent calls could commit in order but publish their preview map in
    // reverse response order, leaving the stale resource live.
    let mut current = state
        .render_preview_resources
        .lock()
        .map_err(|_| "CORE_UNAVAILABLE".to_string())?;
    let result = state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .rerender_page(page_id)
        .map_err(|error| error.code)?;
    rotate_render_preview(state.channel.as_ref(), page_id, result, &mut current)
}

/// M2-PAGE-RESOURCE-RESOLVE-1: the resolved key is a STABLE catalog entry
/// (the managed original is immutable) -- deliberately NOT routed through
/// the preview rotation, which revokes the previous render per page and
/// would delete a still-authoritative original reference.
#[tauri::command]
fn resolve_page_resource(
    state: tauri::State<'_, AppState>,
    page_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .resolve_page_resource(&page_id)
        .map_err(|error| error.code)
}

/// M2-PAGE-NAV-PROJECTION-1: read-only navigation projections. No channel
/// or rotation state is touched -- the summaries are pure Core reads.
#[tauri::command]
fn list_chapters(
    state: tauri::State<'_, AppState>,
    book_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .list_chapters(&book_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn list_chapter_pages(
    state: tauri::State<'_, AppState>,
    chapter_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .list_chapter_pages(&chapter_id)
        .map_err(|error| error.code)
}

/// READER-IPC-1: return the Core's ReaderProjection unchanged. Resource refs
/// remain opaque and continue through the existing resolve_page_resource path.
#[tauri::command]
fn library_get_reader_projection(
    state: tauri::State<'_, AppState>,
    chapter_id: String,
    mode: String,
    start_position: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .get_reader_projection(&chapter_id, &mode, &start_position)
        .map_err(|error| error.code)
}

/// READER-IPC-1: the host forwards only progress coordinates and optional
/// elapsed time; Core owns validation and persistence.
#[tauri::command]
fn library_save_reading_progress(
    state: tauri::State<'_, AppState>,
    chapter_id: String,
    mode: String,
    page_id: String,
    scroll_offset_y: Option<f64>,
    elapsed_seconds_delta: Option<f64>,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .save_reading_progress(
            &chapter_id,
            &mode,
            &page_id,
            scroll_offset_y,
            elapsed_seconds_delta,
        )
        .map_err(|error| error.code)
}

// RUN-IPC-1: P13-C1 (contract rev 2.0 §5.5) froze the Run command surface in
// the Core, but no host outlet existed, so the Workbench (P14) had no way to
// start or inspect a Run. These six commands are pure transport: every domain
// rule (PipelineCommand closed set, PipelineScope resolution, idempotency
// semantics, the control-action state matrix, DTO shapes) is decided Core-side
// before persistence, and the typed code propagates verbatim. They are
// production-only (probe/AC1 keep their frozen shapes).
#[tauri::command]
fn library_start_run(
    state: tauri::State<'_, AppState>,
    command: String,
    scope: serde_json::Value,
    overrides: Option<serde_json::Value>,
    idempotency_key: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .start_run(&command, &scope, overrides.as_ref(), &idempotency_key)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_control_run(
    state: tauri::State<'_, AppState>,
    run_id: String,
    action: String,
    idempotency_key: Option<String>,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .control_run(&run_id, &action, idempotency_key.as_deref())
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_resume_blocked_run(
    state: tauri::State<'_, AppState>,
    run_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .resume_blocked_run(&run_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_get_run_snapshot(
    state: tauri::State<'_, AppState>,
    run_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .get_run_snapshot(&run_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_get_task_projection(
    state: tauri::State<'_, AppState>,
    run_id: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .get_task_projection(&run_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_retry_failed_targets(
    state: tauri::State<'_, AppState>,
    run_id: String,
    idempotency_key: String,
) -> Result<serde_json::Value, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .retry_failed_targets(&run_id, &idempotency_key)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_cancel_export(
    state: tauri::State<'_, AppState>,
    export_id: String,
) -> Result<ExportProgressSnapshotView, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .cancel_export(&export_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_get_export_snapshot(
    state: tauri::State<'_, AppState>,
    export_id: String,
) -> Result<ExportProgressSnapshotView, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .get_export_snapshot(&export_id)
        .map_err(|error| error.code)
}

#[tauri::command]
fn library_get_export_history(
    state: tauri::State<'_, AppState>,
) -> Result<ExportHistoryResponseView, String> {
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .get_export_history()
        .map_err(|error| error.code)
}

fn parse_delete_book_payload(
    value: Option<serde_json::Value>,
) -> Result<PermanentlyDeleteBookPayload, PermanentlyDeleteBookErrorView> {
    serde_json::from_value(value.ok_or_else(PermanentlyDeleteBookErrorView::invalid_request)?)
        .map_err(|_| PermanentlyDeleteBookErrorView::invalid_request())
}

fn parse_delete_books_payload(
    value: Option<serde_json::Value>,
) -> Result<PermanentlyDeleteBooksPayload, PermanentlyDeleteBooksErrorView> {
    serde_json::from_value(value.ok_or_else(PermanentlyDeleteBooksErrorView::invalid_request)?)
        .map_err(|_| PermanentlyDeleteBooksErrorView::invalid_request())
}

#[tauri::command]
fn library_delete_book_permanently(
    state: tauri::State<'_, AppState>,
    payload: Option<serde_json::Value>,
) -> Result<PermanentlyDeleteBookResult, PermanentlyDeleteBookErrorView> {
    let payload = parse_delete_book_payload(payload)?;
    state
        .library
        .as_ref()
        .ok_or_else(PermanentlyDeleteBookErrorView::unavailable)?
        .permanently_delete_book(payload)
        .map_err(PermanentlyDeleteBookErrorView::from_core)
}

#[tauri::command]
fn library_delete_books_permanently(
    state: tauri::State<'_, AppState>,
    payload: Option<serde_json::Value>,
) -> Result<PermanentlyDeleteBooksResult, PermanentlyDeleteBooksErrorView> {
    let payload = parse_delete_books_payload(payload)?;
    state
        .library
        .as_ref()
        .ok_or_else(PermanentlyDeleteBooksErrorView::unavailable)?
        .permanently_delete_books(payload)
        .map_err(PermanentlyDeleteBooksErrorView::from_core)
}

#[tauri::command]
async fn library_import_file(
    app: tauri::AppHandle,
    state: tauri::State<'_, AppState>,
    chapter_id: String,
    duplicate_policy: Option<String>,
) -> Result<host_issuer::ImportSummary, String> {
    let selected = app
        .dialog()
        .file()
        .add_filter(
            "Images and PDF",
            &["png", "jpg", "jpeg", "webp", "gif", "bmp", "pdf"],
        )
        .blocking_pick_files();
    let Some(selected) = selected.filter(|paths| !paths.is_empty()) else {
        return Ok(host_issuer::ImportSummary::cancelled(chapter_id));
    };
    let paths = selected
        .into_iter()
        .map(|path| path.into_path().map_err(|_| "INVALID_REQUEST".to_string()))
        .collect::<Result<Vec<_>, _>>()?;
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .import_from_paths(&paths, "file", &chapter_id, duplicate_policy.as_deref())
        .map_err(|error| error.code)
}

#[tauri::command]
async fn library_import_folder(
    app: tauri::AppHandle,
    state: tauri::State<'_, AppState>,
    chapter_id: String,
    duplicate_policy: Option<String>,
) -> Result<host_issuer::ImportSummary, String> {
    let selected = app.dialog().file().blocking_pick_folder();
    let Some(selected) = selected else {
        return Ok(host_issuer::ImportSummary::cancelled(chapter_id));
    };
    let path = selected
        .into_path()
        .map_err(|_| "INVALID_REQUEST".to_string())?;
    state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .import_from_path(&path, "directory", &chapter_id, duplicate_policy.as_deref())
        .map_err(|error| error.code)
}

#[tauri::command]
async fn library_start_export(
    app: tauri::AppHandle,
    state: tauri::State<'_, AppState>,
    request: serde_json::Value,
) -> Result<Option<host_issuer::ExportSummary>, String> {
    let (_, extension) =
        host_issuer::validate_export_request(&request).map_err(|error| error.0.to_string())?;
    let selected = app
        .dialog()
        .file()
        .add_filter("Export target", &[extension])
        .blocking_save_file();
    let Some(selected) = selected else {
        return Ok(None);
    };
    let mut path = selected
        .into_path()
        .map_err(|_| "INVALID_REQUEST".to_string())?;
    match path.extension().and_then(|ext| ext.to_str()) {
        None => {
            path.set_extension(extension);
        }
        Some(actual) if actual.eq_ignore_ascii_case(extension) => {}
        Some(_) => return Err("INVALID_REQUEST".to_string()),
    }
    let result = state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?
        .start_export_to_path(&path, request)
        .map_err(|error| error.code)?;
    Ok(Some(result))
}

fn reveal_export_folder_with(
    export_id: &str,
    resolve_directory: impl FnOnce(&str) -> Result<PathBuf, String>,
    open_directory: impl FnOnce(&std::path::Path) -> Result<(), String>,
) -> Result<(), String> {
    let directory = resolve_directory(export_id)?;
    open_directory(&directory)
}

#[tauri::command]
async fn library_reveal_export_folder(
    app: tauri::AppHandle,
    state: tauri::State<'_, AppState>,
    export_id: String,
) -> Result<(), String> {
    let library = state
        .library
        .as_ref()
        .ok_or_else(|| "CORE_UNAVAILABLE".to_string())?;
    reveal_export_folder_with(
        &export_id,
        |id| {
            library
                .export_output_directory(id)
                .map_err(|error| error.code)
        },
        |directory| {
            app.opener()
                .open_path(
                    directory
                        .to_str()
                        .ok_or_else(|| "EXPORT_PATH_UNAVAILABLE".to_string())?,
                    None::<&str>,
                )
                .map_err(|_| "EXPORT_REVEAL_FAILED".to_string())
        },
    )
}

fn rotate_render_preview(
    channel: &dyn CoreChannel,
    page_id: &str,
    mut result: serde_json::Value,
    current: &mut HashMap<String, String>,
) -> Result<serde_json::Value, String> {
    let previous = current.get(page_id).cloned();
    let next = result
        .get("preview")
        .and_then(|preview| preview.get("resource_id"))
        .and_then(serde_json::Value::as_str)
        .filter(|resource_id| !resource_id.is_empty())
        .map(str::to_owned);

    if let Some(previous_id) = previous.as_deref() {
        // RC4-11: revoke-previous-first rotates across distinct catalog
        // keys. If the new preview re-uses the previous key, revoking it
        // first would silently invalidate the preview we are about to
        // serve -- the equal-key case skips the revoke.
        let same_key = next.as_deref() == Some(previous_id);
        // M2-DERIVED-GC-2: the successful previous-key revoke carries the
        // internal retire bit so the channel can mark the cataloged preview
        // retired AFTER its own revoke succeeded. The equal-key case and
        // the fail-closed new-key revoke below stay PLAIN revokes (no
        // retire bit): same-key rotation must not retire the live key, and
        // a failed rotation must not mark anything reclaimable.
        if !same_key
            && channel
                .revoke_resource_retiring_preview(previous_id)
                .is_err()
        {
            if let Some(next_id) = next.as_deref() {
                let _ = channel.revoke_resource(next_id);
            }
            result["preview"] = serde_json::Value::Null;
            result["preview_error"] = serde_json::json!("PREVIEW_UNAVAILABLE");
            return Ok(result);
        }
    }

    match next {
        Some(resource_id) => {
            current.insert(page_id.to_string(), resource_id);
        }
        None => {
            current.remove(page_id);
        }
    }
    if !result["preview_error"].is_null() {
        result["preview_error"] = serde_json::json!("PREVIEW_UNAVAILABLE");
    }
    Ok(result)
}

/// Production issue shape: catalog entry name + revision only. There is no
/// TTL parameter on this command (RC2-AC1) — reference lifetimes are Core
/// policy (ruled 300 s sliding default), never caller input.
#[tauri::command]
fn issue_resource_url(
    state: tauri::State<'_, AppState>,
    resource_id: String,
    revision: String,
) -> Result<IssuedUrl, String> {
    let issued = state
        .channel
        .issue(&resource_id, &revision)
        .map_err(|error| error.code)?;
    into_issued(issued).map_err(|error| error.code)
}

#[tauri::command]
fn revoke_ref(state: tauri::State<'_, AppState>, opaque_id: String) -> Result<(), String> {
    state.channel.revoke(&opaque_id).map_err(|error| error.code)
}

#[tauri::command]
fn revoke_resource_refs(
    state: tauri::State<'_, AppState>,
    resource_id: String,
) -> Result<u32, String> {
    state
        .channel
        .revoke_resource(&resource_id)
        .map_err(|error| error.code)
}

// ---- probe-mode-only command surface (evidence runner) --------------------
// These #[tauri::command] fns are registered only when `M2RC1_PROBE_OUT` is
// set; in production mode they are absent from the invoke handler entirely.

#[tauri::command]
fn probe_config(state: tauri::State<'_, AppState>) -> serde_json::Value {
    serde_json::json!({
        "probe_auto": true,
        "scheme_host": resource_protocol::SCHEME_HOST,
        "chunk_size": resource_protocol::CHUNK_SIZE,
        "fixture_shas": state.fixture_shas,
    })
}

#[tauri::command]
fn probe_write_results(payload: String) -> Result<String, String> {
    let out = std::env::var("M2RC1_PROBE_OUT").unwrap_or_else(|_| {
        std::env::temp_dir()
            .join("m2rc1-probe-results.json")
            .to_string_lossy()
            .into_owned()
    });
    std::fs::write(&out, payload).map_err(|error| error.to_string())?;
    Ok(out)
}

#[tauri::command]
fn probe_exit(app: tauri::AppHandle, code: i32) {
    app.exit(code);
}

/// Probe-only issue with an explicit TTL override (lifecycle scenarios such
/// as the E-05 expiry case). Deliberately NOT on the production surface: the
/// WebView can never extend (or set) a product reference lifetime.
#[tauri::command]
fn probe_issue_url(
    state: tauri::State<'_, AppState>,
    resource_id: String,
    revision: String,
    ttl_seconds: f64,
) -> Result<IssuedUrl, String> {
    let issued = state
        .channel
        .issue_probe(&resource_id, &revision, ttl_seconds)
        .map_err(|error| error.code)?;
    into_issued(issued).map_err(|error| error.code)
}

// ---- M2-AC1 acceptance-mode-only command surface ---------------------------
// Registered only when `M2AC1_TEST_MODE=1`; production and probe mode never
// see these commands. `ac1_request` forwards a method call to the acceptance
// Core sidecar (bootstrap.acceptance_bridge); `ac1_write_results` writes the
// run evidence file named by `M2AC1_RESULTS_OUT`; `ac1_exit` terminates the
// desktop process so the runner can relaunch it for the restart phase.

#[tauri::command]
fn ac1_request(
    state: tauri::State<'_, AppState>,
    method: String,
    params: serde_json::Value,
) -> Result<serde_json::Value, String> {
    state
        .ac1
        .as_ref()
        .ok_or_else(|| "AC1_BRIDGE_DOWN".to_string())?
        .round_trip(&method, params)
        .map_err(|error| error.code)
}

#[tauri::command]
fn ac1_write_results(payload: String) -> Result<String, String> {
    let out = std::env::var("M2AC1_RESULTS_OUT").unwrap_or_else(|_| {
        std::env::temp_dir()
            .join("m2ac1-results.json")
            .to_string_lossy()
            .into_owned()
    });
    std::fs::write(&out, payload).map_err(|error| error.to_string())?;
    Ok(out)
}

#[tauri::command]
fn ac1_exit(app: tauri::AppHandle, code: i32) {
    app.exit(code);
}

fn env_path(name: &str) -> Option<PathBuf> {
    std::env::var(name).ok().map(PathBuf::from)
}

// ---- M2-AC5 packaged-mode resolution ---------------------------------------
//
// The packaged app carries a self-contained PyInstaller sidecar directory at
// `<install>/resources/core-sidecar/` (declared in tauri.conf.json
// `bundle.resources`; exe names pinned by packaging/m2ac5/core_sidecar.spec:
// host_bridge / core_service / acceptance_bridge / catalog_loader).
//
// Packaged mode is entered when EITHER:
//   a) `M2RC1_PACKAGED=1` is set explicitly (the unambiguous switch), or
//   b) `M2RC1_SRC_ROOT` is absent AND the install-relative sidecar dir
//      exists (an installed app launched bare).
// Dev mode (M2RC1_* present, no installed layout) keeps the frozen env
// contract byte-for-byte; existing tests and runners all hit that path.
//
// Fail-closed (AC2): in packaged mode a missing sidecar exe surfaces as the
// typed `CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING` at spawn time; there is
// deliberately NO fallback to a system `python`.

/// The sidecar directory relative to the running exe's directory.
fn sidecar_dir_for(exe_dir: Option<&std::path::Path>) -> Option<PathBuf> {
    exe_dir.map(|dir| dir.join("resources").join("core-sidecar"))
}

/// Pure decision core of packaged-mode resolution (unit-tested): explicit
/// flag wins, then the src-root-less bare-launch heuristic gated on the
/// sidecar exe actually existing. `exe_dir = None` (no current exe) never
/// resolves packaged.
fn resolve_packaged_sidecar_dir(
    explicit_packaged: Option<&str>,
    src_root: Option<&str>,
    exe_dir: Option<&std::path::Path>,
) -> Option<PathBuf> {
    if explicit_packaged == Some("1") {
        return sidecar_dir_for(exe_dir);
    }
    if src_root.is_none() {
        if let Some(dir) = sidecar_dir_for(exe_dir) {
            if dir.join("host_bridge.exe").is_file() {
                return Some(dir);
            }
        }
    }
    None
}

/// Packaged default user-data root (AC4): `%APPDATA%/<identifier>` — data
/// and derived/managed/catalog live in the user profile, never in the
/// install directory. Explicit `M2RC1_*` env still wins over these defaults
/// (evidence runners pin lab dirs through the same env contract as dev).
fn packaged_user_root() -> Option<PathBuf> {
    std::env::var("APPDATA")
        .ok()
        .map(|appdata| PathBuf::from(appdata).join("com.newmanga.m2rc1.desktop"))
}

fn fixture_shas() -> serde_json::Value {
    let path = env_path("M2RC1_FIXTURES").unwrap_or_default();
    let text = match std::fs::read_to_string(&path) {
        Ok(text) => text,
        Err(_) => return serde_json::Value::Null,
    };
    let parsed: serde_json::Value = match serde_json::from_str(&text) {
        Ok(value) => value,
        Err(_) => return serde_json::Value::Null,
    };
    // manifest shape: {"fixtures": {"<name>": {"sha256": "...", ...}, ...}}
    let mut map = serde_json::Map::new();
    if let Some(fixtures) = parsed.get("fixtures").and_then(|f| f.as_object()) {
        for (name, entry) in fixtures {
            if let Some(sha) = entry.get("sha256") {
                map.insert(name.clone(), sha.clone());
            }
        }
    }
    serde_json::Value::Object(map)
}

fn main() {
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|dir| dir.to_path_buf()));
    let packaged_dir = resolve_packaged_sidecar_dir(
        std::env::var("M2RC1_PACKAGED").ok().as_deref(),
        std::env::var("M2RC1_SRC_ROOT").ok().as_deref(),
        exe_dir.as_deref(),
    );

    // DEV spawn inputs: exactly the pre-M2-AC5 contract, consumed only on the
    // dev path. Packaged mode spawns the frozen sidecar exes instead.
    let (python_exe, src_root) = match &packaged_dir {
        None => (
            std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".to_string()),
            env_path("M2RC1_SRC_ROOT").expect("M2RC1_SRC_ROOT must point at the repo src dir"),
        ),
        Some(_) => (String::new(), PathBuf::new()),
    };

    // Data roots (M2-AC5): dev keeps the `expect` contract; packaged mode
    // defaults under %APPDATA%/<identifier> (created on first launch) and
    // still honours explicit env so runners can pin a lab dir.
    let user_root = match &packaged_dir {
        Some(_) => packaged_user_root(),
        None => None,
    };
    let ensure_dir = |path: &std::path::Path| {
        let _ = std::fs::create_dir_all(path);
    };
    let derived_root = match &user_root {
        Some(root) => env_path("M2RC1_DERIVED_ROOT").unwrap_or_else(|| {
            let path = root.join("derived");
            ensure_dir(&path);
            path
        }),
        None => env_path("M2RC1_DERIVED_ROOT").expect("M2RC1_DERIVED_ROOT required"),
    };
    let managed_root = match &user_root {
        Some(root) => env_path("M2RC1_MANAGED_ROOT").unwrap_or_else(|| {
            let path = root.join("managed");
            ensure_dir(&path);
            path
        }),
        None => env_path("M2RC1_MANAGED_ROOT").expect("M2RC1_MANAGED_ROOT required"),
    };
    // RC2 (F-03): the app refuses to run without its catalog authority. The
    // launcher seeds the Core/SQLite store (catalog_loader in packaged form)
    // and passes the path; without it every issue would fail closed anyway.
    let catalog_db = match &user_root {
        Some(root) => env_path("M2RC2_CATALOG_DB").unwrap_or_else(|| {
            let path = root.join("catalog").join("catalog.sqlite");
            ensure_dir(path.parent().unwrap_or(root));
            path
        }),
        None => env_path("M2RC2_CATALOG_DB")
            .expect("M2RC2_CATALOG_DB required (Core/SQLite catalog authority)"),
    };
    // the embedded page URL has no query string, so the probe mode switch is
    // the presence of M2RC1_PROBE_OUT (set only by the evidence runner)
    let probe_mode = std::env::var("M2RC1_PROBE_OUT").is_ok();
    // M2-AC1: the acceptance mode is its own explicit test startup
    // configuration — never combined with the RC1 probe mode.
    let ac1_mode = !probe_mode && std::env::var("M2AC1_TEST_MODE").as_deref() == Ok("1");

    // M2-DERIVED-GC-2 production startup order (design §2.3): the
    // production Core is spawned FIRST and must answer its startup ping
    // (30 s deadline) before the channel sidecar starts -- the Core only
    // answers after it holds the preview namespace protection and its
    // startup GC window is done. Probe/AC1 keep the historical channel-only
    // startup and never run this GC (probe/ac1 paths never spawn a
    // production library).
    let is_production = !probe_mode && !ac1_mode;
    let data_root = match &user_root {
        Some(root) => Some(env_path("NEWMANGA_DATA_ROOT").unwrap_or_else(|| {
            let path = root.join("data");
            ensure_dir(&path);
            path
        })),
        None => env_path("NEWMANGA_DATA_ROOT"),
    };
    let library: Option<Box<dyn LibraryChannel>> = if is_production {
        let (sidecar_path, working_dir) = match &packaged_dir {
            Some(dir) => (dir.join("core_service.exe").to_string_lossy().to_string(), dir.clone()),
            None => (python_exe.clone(), src_root.clone()),
        };
        let config = LibrarySpawnConfig::new(
            sidecar_path.clone(),
            working_dir.clone(),
            data_root.clone(),
            Some(derived_root.clone()),
            Some(catalog_db.clone()),
        );
        let init_spawn_res = StdioLibraryChannel::spawn_with_startup_ping(
            &sidecar_path,
            &working_dir,
            data_root.as_deref(),
            Some(&derived_root),
            Some(&catalog_db),
            std::time::Duration::from_secs(30),
        )
        .and_then(|chan| {
            chan.open_host_session()?;
            Ok(chan)
        });

        let (initial_chan, initial_failed) = match init_spawn_res {
            Ok(chan) => (Some(chan), false),
            Err(e) => {
                eprintln!("[startup] WARNING: initial core_service startup failed ({e}); supervisor will recover");
                (None, true)
            }
        };

        let resilient = ResilientLibraryChannel::new(config, initial_chan);
        if initial_failed {
            resilient.record_initial_failure();
        }
        resilient.start_heartbeat();
        Some(Box::new(resilient))
    } else {
        None
    };
    let channel = match &packaged_dir {
        Some(dir) => StdioCoreChannel::spawn_packaged(
            &dir.join("host_bridge.exe"),
            &derived_root,
            &managed_root,
            &catalog_db,
        ),
        None => StdioCoreChannel::spawn(
            &python_exe,
            &src_root,
            &derived_root,
            &managed_root,
            &catalog_db,
        ),
    }
    .expect("python core sidecar failed to start");
    let ac1 = if ac1_mode {
        Some(
            match &packaged_dir {
                Some(dir) => {
                    Ac1Channel::spawn(&dir.join("acceptance_bridge.exe").to_string_lossy(), dir)
                }
                None => Ac1Channel::spawn(&python_exe, &src_root),
            }
            .expect("acceptance core sidecar failed to start"),
        )
    } else {
        None
    };

    let state = AppState {
        channel: Box::new(channel),
        roots: ScopeRoots {
            derived: derived_root,
            managed: managed_root,
        },
        fixture_shas: fixture_shas(),
        ac1,
        library,
        credential_operations: Mutex::new(()),
        render_preview_resources: Mutex::new(HashMap::new()),
    };

    let builder = tauri::Builder::default();
    let builder = if is_production {
        builder
            .plugin(tauri_plugin_dialog::init())
            .plugin(tauri_plugin_opener::init())
    } else {
        builder
    };
    let builder = builder
        .manage(state)
        .setup(|app| {
            // progress channel: mirror the page's window title to stderr so
            // the runner can observe probe progress without the invoke bridge
            let handle = app.handle().clone();
            let title_handle = handle.clone();
            std::thread::spawn(move || {
                for _ in 0..90 {
                    std::thread::sleep(std::time::Duration::from_secs(2));
                    for window in title_handle.webview_windows().values() {
                        let title = window.title().unwrap_or_default();
                        eprintln!("[m2rc1-title] {title}");
                    }
                }
            });

            // EVENTS-FWD-1 (rev 2.4 §6.4): Register the event sink to forward
            // projected Core events into the Tauri WebView event bus.
            let app_state = app.state::<AppState>();
            if let Some(library) = &app_state.library {
                let emit_handle = handle.clone();
                library.set_event_sink(Arc::new(
                    move |event_name: &str, payload: serde_json::Value| {
                        use tauri::Emitter;
                        if let Err(err) = emit_handle.emit(event_name, &payload) {
                            eprintln!("[events-fwd] failed to emit {event_name}: {err}");
                        }
                    },
                ));
                let status_handle = handle.clone();
                library.set_status_emitter(Arc::new(
                    move |status: &str, message: &str| {
                        use tauri::Emitter;
                        let payload = serde_json::json!({
                            "status": status,
                            "message": message,
                        });
                        if let Err(err) = status_handle.emit("core:lifecycle_status", &payload) {
                            eprintln!("[status-fwd] failed to emit core:lifecycle_status: {err}");
                        }
                    },
                ));

                // R-002: If initial startup failed early, supervisor triggers self-healing
                // now that status_emitter is hooked to the Tauri event bus.
                if library.is_unhealthy() {
                    library.trigger_restart();
                }
            }

            Ok(())
        })
        .register_uri_scheme_protocol("m2res", |ctx, request| {
            let state = ctx.app_handle().state::<AppState>();
            let uri = request.uri().to_string();
            let response =
                resource_protocol::handle_m2res_request(&uri, state.channel.as_ref(), &state.roots);
            let mut response_builder = tauri::http::Response::builder()
                .status(response.status)
                .header("Content-Type", response.content_type)
                .header("Cache-Control", response.cache_control)
                .header("Access-Control-Allow-Origin", "*");
            if response.status == 206 || !response.body.is_empty() {
                response_builder = response_builder.header("X-M2RC1-Served", "chunk");
            }
            response_builder.body(response.body).unwrap()
        });

    // RC2-AC1: the conditional allowlist. The probe surface physically does
    // not exist in production mode; `register_catalog` exists in no mode.
    // M2-AC1: the acceptance commands exist only in the explicit test mode.
    // R2-04: the announcements below are emitted from the `command_allowlist`
    // CONSTANT ARRAY, which is one of THREE hand-maintained views of the
    // same surface (constants / generate_handler! literal list below /
    // build.rs app-manifest list) -- there is no compile-time binding
    // between them. The unit tests pin the constants, the runner pins the
    // announcement per mode, and tauri-build validates the capability
    // against the manifest; keep all three in sync in the same commit.
    let builder = if probe_mode {
        eprintln!(
            "[m2rc2-allowlist] probe:{}",
            command_allowlist(true, false).join(",")
        );
        builder.invoke_handler(tauri::generate_handler![
            issue_resource_url,
            revoke_ref,
            revoke_resource_refs,
            probe_config,
            probe_write_results,
            probe_exit,
            probe_issue_url
        ])
    } else if ac1_mode {
        eprintln!(
            "[m2ac1-allowlist] ac1:{}",
            command_allowlist(false, true).join(",")
        );
        builder.invoke_handler(tauri::generate_handler![
            issue_resource_url,
            revoke_ref,
            revoke_resource_refs,
            ac1_request,
            ac1_write_results,
            ac1_exit
        ])
    } else {
        eprintln!(
            "[m2rc2-allowlist] production:{}",
            command_allowlist(false, false).join(",")
        );
        builder.invoke_handler(tauri::generate_handler![
            issue_resource_url,
            revoke_ref,
            revoke_resource_refs,
            core_ping,
            library_list_books,
            library_list_recycle_bin_books,
            library_create_book,
            create_chapter,
            settings_get,
            settings_update_section,
            cleanup_preview,
            cleanup_run,
            cleanup_retry_pending,
            backup_create,
            backup_list,
            backup_restore,
            backup_delete,
            settings_provider_profiles_list,
            settings_provider_profiles_create,
            settings_provider_profiles_update,
            settings_provider_profiles_delete,
            settings_provider_bindings_set,
            settings_provider_bindings_clear,
            settings_provider_bindings_resolve,
            settings_provider_run_snapshot_get,
            settings_network_profiles_list,
            settings_network_profiles_create,
            settings_network_profiles_update,
            settings_network_profiles_delete,
            settings_network_profiles_test,
            settings_network_profile_default_set,
            settings_network_profile_default_clear,
            settings_network_profile_resolve,
            settings_resolve_overrides,
            credential_put,
            credential_clear,
            set_region_type,
            list_regions,
            list_region_revisions,
            restore_region_revision,
            rerender_page,
            resolve_page_resource,
            list_chapters,
            list_chapter_pages,
            library_get_reader_projection,
            library_save_reading_progress,
            library_import_file,
            library_import_folder,
            library_start_export,
            library_start_run,
            library_control_run,
            library_resume_blocked_run,
            library_get_run_snapshot,
            library_get_task_projection,
            library_retry_failed_targets,
            library_reveal_export_folder,
            library_cancel_export,
            library_get_export_snapshot,
            library_get_export_history,
            library_delete_book_permanently,
            library_delete_books_permanently
        ])
    };

    builder
        .run(tauri::generate_context!())
        .expect("error while running M2-RC2 desktop runtime");
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core_bridge::{build_issue_params, MockCoreChannel};
    use crate::library_bridge::{LibraryError, MockLibraryChannel};
    use crate::resource_protocol::{build_url, handle_m2res_request, ScopeRoots, ID_LENGTH};
    use std::io::Write;

    struct TestEnv {
        /// Owns the tempdir so every fixture directory is cleaned up on drop
        /// (M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF: replaces the former
        /// `mem::forget` that leaked ~50 tempdirs per stability-loop run).
        _dir: tempfile::TempDir,
        roots: ScopeRoots,
        channel: MockCoreChannel,
    }

    fn write_resource(root: &std::path::Path, rel: &str, payload: &[u8]) -> String {
        let target = root.join(rel);
        std::fs::create_dir_all(target.parent().unwrap()).unwrap();
        std::fs::write(&target, payload).unwrap();
        sha_hex(payload)
    }

    fn sha_hex(payload: &[u8]) -> String {
        use crate::resource_protocol::hex;
        use sha2::{Digest as _, Sha256};
        let mut hasher = Sha256::new();
        hasher.update(payload);
        hex(hasher.finalize())
    }

    fn env_with_fixture(payload: &[u8]) -> (TestEnv, String) {
        let dir = tempfile::tempdir().unwrap();
        let derived = dir.path().join("scope").join("derived");
        let managed = dir.path().join("scope").join("managed");
        std::fs::create_dir_all(&managed).unwrap();
        let sha = write_resource(&derived, "asset.png", payload);
        let env = TestEnv {
            _dir: dir,
            roots: ScopeRoots { derived, managed },
            channel: MockCoreChannel::new(),
        };
        (env, sha)
    }

    fn url_for(id: &str, chunk: Option<u64>) -> String {
        let base = build_url(id);
        match chunk {
            Some(n) => format!("{base}?chunk={n}"),
            None => base,
        }
    }

    fn registered(env: &TestEnv, resource_id: &str, rel: &str, payload: &[u8]) -> String {
        let sha = write_resource(&env.roots.derived, rel, payload);
        // seed the mock catalog (the stand-in for the Core-side SQLite store)
        env.channel.register(resource_id, rel).unwrap();
        let issued = env.channel.issue(resource_id, "rev-1").unwrap();
        // make the mock grant match the real file so handle verification passes
        let opaque = issued.opaque_id.clone();
        let mut table = env.channel.table.lock().unwrap();
        let entry = table.get_mut(&opaque).unwrap();
        entry.grant.size = payload.len() as u64;
        entry.grant.sha256 = sha;
        let metadata = std::fs::metadata(env.roots.derived.join(rel)).unwrap();
        // capture real identity via the same helper the product uses
        drop(table);
        let (volume, index, _size, _mtime) =
            resource_protocol::capture_facts_for_tests(&env.roots.derived.join(rel))
                .expect("issue-time facts from fixture handle");
        let mut table = env.channel.table.lock().unwrap();
        let entry = table.get_mut(&opaque).unwrap();
        entry.grant.volume_serial = volume;
        entry.grant.file_index = index;
        let _ = metadata;
        opaque
    }

    // ---- RC2-AC1: WebView-facing command surface allow/deny matrix --------

    /// R2-01(a): the ACL must be enforced for BARE app commands, which only
    /// happens when the generated acl-manifests.json carries the
    /// `__app-acl__` application manifest (an inlined-plugin declaration is
    /// keyed `plugin:<name>|<cmd>` and never matches bare invocations -- the
    /// ACL layer silently skipped them, DSH R2-01). This pins the build
    /// artifact: the app manifest declares exactly the live commands
    /// (fifty-seven production -- resource-channel, IPC1, settings, cleanup,
    /// retype, RC-4, page resolve/navigation, HOST-ISSUER-1, Run, export
    /// reveal and Reader actions -- plus
    /// four probe-only and three M2-AC1 acceptance commands; R2-06),
    /// and no plugin-shaped surface remains.
    #[test]
    fn app_acl_manifest_is_generated_and_enforced() {
        let manifest: serde_json::Value =
            serde_json::from_str(include_str!("../gen/schemas/acl-manifests.json"))
                .expect("acl-manifests.json must be present and valid");
        let app = manifest
            .get("__app-acl__")
            .expect("acl-manifests.json must carry __app-acl__ (R2-01a)");
        let permissions = app
            .get("permissions")
            .and_then(|p| p.as_object())
            .expect("__app-acl__ permissions object");
        // F-003 (DSH r1): the ACL existence check covers the ac1 test-mode
        // commands too — a capability/manifest typo for an ac1 command must
        // fail here, not only surface as an E2E ACL denial.
        // M2-REGION-RETYPE-CORE r1 P3-2: the production surface joins the
        // sweep, so the existence check covers all 64 commands across the
        // three surfaces (61 production + 4 probe-only + 3 ac1) — a missing
        // capability/manifest entry for a production-only command (e.g. the
        // retype pair or the SETTINGS-OPEN-B-2 cleanup trio) fails this
        // test, not just a live invoke.
        for command in command_allowlist(true, false)
            .into_iter()
            .chain(command_allowlist(false, true))
            .chain(command_allowlist(false, false))
        {
            let allow = format!("allow-{}", command.replace('_', "-"));
            assert!(
                permissions.contains_key(&allow),
                "app ACL must define {allow} (from {command})"
            );
        }
        // the deleted catalog surface must not be declared anywhere either
        assert!(
            !serde_json::to_string(&manifest)
                .unwrap()
                .contains("register_catalog"),
            "register_catalog must not re-enter any ACL surface"
        );
    }

    #[test]
    fn production_surface_includes_export_reveal() {
        // 61 production commands: the previously pinned 57-command surface plus
        // the four SETTINGS-OPEN-C-2-BACKUP package commands.
        assert_eq!(
            command_allowlist(false, false),
            vec![
                "issue_resource_url",
                "revoke_ref",
                "revoke_resource_refs",
                "core_ping",
                "library_list_books",
                "library_list_recycle_bin_books",
                "library_create_book",
                "create_chapter",
                "settings_get",
                "settings_update_section",
                "cleanup_preview",
                "cleanup_run",
                "cleanup_retry_pending",
                "backup_create",
                "backup_list",
                "backup_restore",
                "backup_delete",
                "settings_provider_profiles_list",
                "settings_provider_profiles_create",
                "settings_provider_profiles_update",
                "settings_provider_profiles_delete",
                "settings_provider_bindings_set",
                "settings_provider_bindings_clear",
                "settings_provider_bindings_resolve",
                "settings_provider_run_snapshot_get",
                "settings_network_profiles_list",
                "settings_network_profiles_create",
                "settings_network_profiles_update",
                "settings_network_profiles_delete",
                "settings_network_profiles_test",
                "settings_network_profile_default_set",
                "settings_network_profile_default_clear",
                "settings_network_profile_resolve",
                "settings_resolve_overrides",
                "credential_put",
                "credential_clear",
                "set_region_type",
                "list_regions",
                "list_region_revisions",
                "restore_region_revision",
                "rerender_page",
                "resolve_page_resource",
                "list_chapters",
                "list_chapter_pages",
                "library_get_reader_projection",
                "library_save_reading_progress",
                "library_import_file",
                "library_import_folder",
                "library_start_export",
                "library_start_run",
                "library_control_run",
                "library_resume_blocked_run",
                "library_get_run_snapshot",
                "library_get_task_projection",
                "library_retry_failed_targets",
                "library_reveal_export_folder",
                "library_cancel_export",
                "library_get_export_snapshot",
                "library_get_export_history",
                "library_delete_book_permanently",
                "library_delete_books_permanently",
            ]
        );
    }

    #[test]
    fn p15_settings_commands_are_exact_and_production_only() {
        assert_eq!(P15_SETTINGS_PRODUCTION_ONLY_COMMANDS.len(), 19);
        assert_eq!(PRODUCTION_COMMANDS.len(), 61);
        assert_eq!(command_allowlist(true, false).len(), 7);
        assert_eq!(command_allowlist(false, true).len(), 6);
        for command in P15_SETTINGS_PRODUCTION_ONLY_COMMANDS {
            assert!(command_allowlist(false, false).contains(command));
            assert!(!command_allowlist(true, false).contains(command));
            assert!(!command_allowlist(false, true).contains(command));
        }
    }

    #[test]
    fn create_commands_are_exact_and_production_only() {
        assert_eq!(
            CREATE_PRODUCTION_ONLY_COMMANDS,
            &["library_create_book", "create_chapter"]
        );
        assert_eq!(PRODUCTION_COMMANDS.len(), 61);
        assert_eq!(command_allowlist(true, false).len(), 7);
        assert_eq!(command_allowlist(false, true).len(), 6);
        for command in CREATE_PRODUCTION_ONLY_COMMANDS {
            assert!(command_allowlist(false, false).contains(command));
            assert!(!command_allowlist(true, false).contains(command));
            assert!(!command_allowlist(false, true).contains(command));
            assert!(include_str!("../build.rs").contains(command));
            assert!(include_str!("../capabilities/m2rc1-commands.json")
                .contains(&format!("allow-{}", command.replace('_', "-"))));
        }
        let production_handler = include_str!("main.rs")
            .split("builder.invoke_handler(tauri::generate_handler![")
            .nth(3)
            .unwrap()
            .split("])")
            .next()
            .unwrap();
        for command in CREATE_PRODUCTION_ONLY_COMMANDS {
            assert!(production_handler.contains(command));
        }
    }

    #[test]
    fn create_payloads_and_errors_are_closed_projections() {
        let private = serde_json::json!("C:/private/shelf.db secret-marker");
        assert!(parse_create_book_payload(Some(serde_json::json!({
            "title": "Book",
            "path": private.clone(),
            "secret": "secret-marker"
        })))
        .is_err());
        assert!(parse_create_chapter_payload(Some(serde_json::json!({
            "book_id": "book-1",
            "title": "Chapter",
            "chapter_number": null
        })))
        .is_err());
        assert!(parse_create_chapter_payload(Some(serde_json::json!({
            "book_id": "book-1",
            "title": "Chapter",
            "chapter_number": "1",
            "path": private.clone()
        })))
        .is_err());
        let omitted_number = parse_create_chapter_payload(Some(serde_json::json!({
            "book_id": "book-1",
            "title": "Chapter"
        })))
        .unwrap();
        assert_eq!(omitted_number.chapter_number, None);
        assert!(parse_create_book_payload(None).is_err());

        let cases = [
            (
                LibraryError::new(
                    "INVALID_REQUEST",
                    "validation",
                    false,
                    Some("secret-marker"),
                ),
                serde_json::json!({
                    "category":"validation", "phase":"request_validation",
                    "action":"edit_input", "message_key":"LIBRARY_INVALID_INPUT"
                }),
            ),
            (
                LibraryError::new(
                    "PROTOCOL_VERSION_UNSUPPORTED",
                    "validation",
                    false,
                    Some("version details"),
                ),
                serde_json::json!({
                    "category":"validation", "phase":"request_validation",
                    "action":"edit_input", "message_key":"LIBRARY_INVALID_INPUT"
                }),
            ),
            (
                LibraryError::new("TARGET_NOT_FOUND", "not_found", false, Some("C:/private")),
                serde_json::json!({
                    "category":"not_found", "phase":"book_lookup",
                    "action":"select_book", "message_key":"LIBRARY_BOOK_NOT_FOUND"
                }),
            ),
            (
                LibraryError::new(
                    "LIBRARY_WRITE_FAILED",
                    "internal",
                    false,
                    Some("secret-marker"),
                ),
                serde_json::json!({
                    "category":"internal", "phase":"persistence",
                    "action":"retry_after_refresh", "message_key":"LIBRARY_WRITE_FAILED"
                }),
            ),
            (
                LibraryError::unavailable("C:/private secret-marker"),
                serde_json::json!({
                    "category":"unavailable", "phase":"core_channel",
                    "action":"retry_after_refresh", "message_key":"LIBRARY_UNAVAILABLE"
                }),
            ),
            (
                LibraryError::new(
                    "UNKNOWN",
                    "unknown",
                    false,
                    Some("raw traceback secret-marker"),
                ),
                serde_json::json!({
                    "category":"internal", "phase":"unknown",
                    "action":"contact_support", "message_key":"LIBRARY_OPERATION_FAILED"
                }),
            ),
        ];
        for (error, expected) in cases {
            let projected = serde_json::to_value(LibrarySurfaceError::from_core(error)).unwrap();
            assert_eq!(projected, expected);
            assert!(!projected.to_string().contains("secret-marker"));
            assert!(!projected.to_string().contains("C:/private"));
        }
        let mut detailed_error = LibraryError::new("INVALID_REQUEST", "validation", false, None);
        detailed_error.details = Some(serde_json::json!({
            "path": "C:/private/shelf.db",
            "secret": "secret-marker",
            "traceback": "raw exception"
        }));
        let projected =
            serde_json::to_value(LibrarySurfaceError::from_core(detailed_error)).unwrap();
        assert_eq!(projected["message_key"], "LIBRARY_INVALID_INPUT");
        assert!(!projected.to_string().contains("private"));
        assert!(!projected.to_string().contains("secret-marker"));
        assert!(!projected.to_string().contains("traceback"));
        let invalid = serde_json::to_value(LibrarySurfaceError::invalid_input()).unwrap();
        assert_eq!(invalid.as_object().unwrap().len(), 4);
        assert!(!invalid.to_string().contains("path"));
    }

    #[test]
    fn p15_core_credential_commands_are_host_only() {
        for command in P15_HOST_ONLY_COMMANDS {
            assert!(!PRODUCTION_COMMANDS.contains(&command));
            assert!(!command_allowlist(false, false).contains(&command));
            assert!(!command_allowlist(true, false).contains(&command));
            assert!(!command_allowlist(false, true).contains(&command));
            assert!(!include_str!("main.rs").contains(command));
            assert!(!include_str!("../build.rs").contains(command));
            assert!(!include_str!("../capabilities/m2rc1-commands.json").contains(command));
        }
    }

    #[test]
    fn export_reveal_command_is_production_only() {
        assert_eq!(
            EXPORT_REVEAL_PRODUCTION_ONLY_COMMANDS,
            &["library_reveal_export_folder"]
        );
        assert!(command_allowlist(false, false).contains(&"library_reveal_export_folder"));
        assert!(!command_allowlist(true, false).contains(&"library_reveal_export_folder"));
        assert!(!command_allowlist(false, true).contains(&"library_reveal_export_folder"));
    }

    #[test]
    fn reveal_rejections_do_not_call_the_opener() {
        for (export_id, code) in [
            ("C:/private/export.pdf", "EXPORT_NOT_FOUND"),
            ("unknown-export", "EXPORT_NOT_FOUND"),
            ("older-core-export", "EXPORT_NOT_FOUND"),
            ("current-pending-export", "EXPORT_OUTPUT_NOT_READY"),
            ("current-missing-path", "EXPORT_PATH_UNAVAILABLE"),
        ] {
            let mut opened = false;
            let result = reveal_export_folder_with(
                export_id,
                |_| Err(code.to_string()),
                |_| {
                    opened = true;
                    Ok(())
                },
            );
            assert_eq!(result.unwrap_err(), code);
            assert!(!opened, "{code} must not reach the opener");
        }
    }

    #[test]
    fn reveal_opens_only_the_resolved_directory() {
        let expected = std::env::temp_dir().canonicalize().unwrap();
        let mut opened = false;
        let result = reveal_export_folder_with(
            "opaque-export-id",
            |_| Ok(expected.clone()),
            |directory| {
                assert_eq!(directory, expected);
                opened = true;
                Ok(())
            },
        );
        assert!(result.is_ok());
        assert!(opened);
    }

    #[test]
    fn probe_surface_adds_exactly_the_four_probe_commands() {
        let probe = command_allowlist(true, false);
        for command in PROBE_ONLY_COMMANDS {
            assert!(
                probe.contains(command),
                "{command} missing from probe surface"
            );
        }
        // M2-IPC1 ruling (DSH r2 P2-1 option B): test modes keep the frozen
        // RC2 surface — the production-only IPC1 commands are absent.
        for command in IPC1_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        // M2-SETTINGS-IPC-CHANNEL: the settings pair is production-only too
        for command in SETTINGS_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        // SETTINGS-OPEN-B-2: the cleanup trio is production-only too.
        for command in CLEANUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        // M2-REGION-RETYPE-CORE: the retype pair is production-only too
        for command in RETYPE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in RC4_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in PAGE_NAV_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in READER_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in HOST_ISSUER_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        // RUN-IPC-1: the Run transport commands are production-only as well.
        for command in RUN_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in EXPORT_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in DELETE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !probe.contains(command),
                "{command} must stay production-only"
            );
        }
        assert_eq!(
            probe.len(),
            PRODUCTION_COMMANDS.len()
                - IPC1_PRODUCTION_ONLY_COMMANDS.len()
                - SETTINGS_PRODUCTION_ONLY_COMMANDS.len()
                - CLEANUP_PRODUCTION_ONLY_COMMANDS.len()
                - BACKUP_PRODUCTION_ONLY_COMMANDS.len()
                - P15_SETTINGS_PRODUCTION_ONLY_COMMANDS.len()
                - RETYPE_PRODUCTION_ONLY_COMMANDS.len()
                - RC4_PRODUCTION_ONLY_COMMANDS.len()
                - PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS.len()
                - PAGE_NAV_PRODUCTION_ONLY_COMMANDS.len()
                - READER_PRODUCTION_ONLY_COMMANDS.len()
                - HOST_ISSUER_PRODUCTION_ONLY_COMMANDS.len()
                - RUN_PRODUCTION_ONLY_COMMANDS.len()
                - EXPORT_REVEAL_PRODUCTION_ONLY_COMMANDS.len()
                - EXPORT_PRODUCTION_ONLY_COMMANDS.len()
                - CREATE_PRODUCTION_ONLY_COMMANDS.len()
                - DELETE_PRODUCTION_ONLY_COMMANDS.len()
                - RECYCLE_BIN_PRODUCTION_ONLY_COMMANDS.len()
                + PROBE_ONLY_COMMANDS.len()
        );
    }

    // ---- M2-AC1: the acceptance surface is test-mode-only -----------------

    #[test]
    fn ac1_surface_adds_exactly_the_three_acceptance_commands() {
        let ac1 = command_allowlist(false, true);
        for command in AC1_TEST_COMMANDS {
            assert!(ac1.contains(command), "{command} missing from ac1 surface");
        }
        // M2-IPC1 ruling (DSH r2 P2-1 option B): test modes keep the frozen
        // AC1 surface — the production-only IPC1 commands are absent.
        for command in IPC1_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        // M2-SETTINGS-IPC-CHANNEL: the settings pair is production-only too
        for command in SETTINGS_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        // SETTINGS-OPEN-B-2: the cleanup trio is production-only too.
        for command in CLEANUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        // SETTINGS-OPEN-C-2-BACKUP: the .nmbak package face is production-only too.
        for command in BACKUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        // M2-REGION-RETYPE-CORE: the retype pair is production-only too
        for command in RETYPE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in RC4_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in PAGE_NAV_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in READER_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in HOST_ISSUER_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        // RUN-IPC-1: the Run transport commands are production-only as well.
        for command in RUN_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in EXPORT_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        for command in DELETE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                !ac1.contains(command),
                "{command} must stay production-only"
            );
        }
        assert_eq!(
            ac1.len(),
            PRODUCTION_COMMANDS.len()
                - IPC1_PRODUCTION_ONLY_COMMANDS.len()
                - SETTINGS_PRODUCTION_ONLY_COMMANDS.len()
                - CLEANUP_PRODUCTION_ONLY_COMMANDS.len()
                - BACKUP_PRODUCTION_ONLY_COMMANDS.len()
                - P15_SETTINGS_PRODUCTION_ONLY_COMMANDS.len()
                - RETYPE_PRODUCTION_ONLY_COMMANDS.len()
                - RC4_PRODUCTION_ONLY_COMMANDS.len()
                - PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS.len()
                - PAGE_NAV_PRODUCTION_ONLY_COMMANDS.len()
                - READER_PRODUCTION_ONLY_COMMANDS.len()
                - HOST_ISSUER_PRODUCTION_ONLY_COMMANDS.len()
                - RUN_PRODUCTION_ONLY_COMMANDS.len()
                - EXPORT_REVEAL_PRODUCTION_ONLY_COMMANDS.len()
                - EXPORT_PRODUCTION_ONLY_COMMANDS.len()
                - CREATE_PRODUCTION_ONLY_COMMANDS.len()
                - DELETE_PRODUCTION_ONLY_COMMANDS.len()
                - RECYCLE_BIN_PRODUCTION_ONLY_COMMANDS.len()
                + AC1_TEST_COMMANDS.len()
        );
    }

    #[test]
    fn production_only_commands_stay_off_both_frozen_test_surfaces() {
        // Keep every production-only family off the frozen 7/6-command surfaces.
        for command in IPC1_PRODUCTION_ONLY_COMMANDS
            .iter()
            .chain(SETTINGS_PRODUCTION_ONLY_COMMANDS)
            .chain(CLEANUP_PRODUCTION_ONLY_COMMANDS)
            .chain(P15_SETTINGS_PRODUCTION_ONLY_COMMANDS)
            .chain(RETYPE_PRODUCTION_ONLY_COMMANDS)
            .chain(RC4_PRODUCTION_ONLY_COMMANDS)
            .chain(PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS)
            .chain(PAGE_NAV_PRODUCTION_ONLY_COMMANDS)
            .chain(READER_PRODUCTION_ONLY_COMMANDS)
            .chain(HOST_ISSUER_PRODUCTION_ONLY_COMMANDS)
            .chain(RUN_PRODUCTION_ONLY_COMMANDS)
            .chain(EXPORT_REVEAL_PRODUCTION_ONLY_COMMANDS)
            .chain(EXPORT_PRODUCTION_ONLY_COMMANDS)
            .chain(CREATE_PRODUCTION_ONLY_COMMANDS)
            .chain(DELETE_PRODUCTION_ONLY_COMMANDS)
            .chain(RECYCLE_BIN_PRODUCTION_ONLY_COMMANDS)
        {
            assert!(
                !command_allowlist(true, false).contains(command),
                "{command} must stay production-only (probe surface)"
            );
            assert!(
                !command_allowlist(false, true).contains(command),
                "{command} must stay production-only (ac1 surface)"
            );
        }
        assert_eq!(command_allowlist(true, false).len(), 7);
        assert_eq!(command_allowlist(false, true).len(), 6);
    }

    /// SETTINGS-OPEN-B-2 (design §4.3): literal exact assertions for the
    /// cache/Revision cleanup trio. The three names are pinned with a fixed
    /// literal expectation (never derived from the constant itself), the
    /// group must sit on the production surface and on NEITHER frozen test
    /// surface, and the R2-04 three-view sync is checked: the build.rs app
    /// manifest declares every command, the capability file allows it, and
    /// the production `generate_handler!` literal list registers it.
    #[test]
    fn cleanup_commands_are_exact_and_production_only() {
        assert_eq!(
            CLEANUP_PRODUCTION_ONLY_COMMANDS,
            &["cleanup_preview", "cleanup_run", "cleanup_retry_pending"]
        );
        assert_eq!(PRODUCTION_COMMANDS.len(), 61);

        let production = command_allowlist(false, false);
        let probe = command_allowlist(true, false);
        let ac1 = command_allowlist(false, true);

        for command in CLEANUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production.contains(command),
                "{command} must be on the production surface"
            );
            assert!(
                !probe.contains(command),
                "{command} must not appear in probe surface"
            );
            assert!(
                !ac1.contains(command),
                "{command} must not appear in ac1 surface"
            );
            // view 2: the build.rs application ACL manifest
            assert!(include_str!("../build.rs").contains(command));
            // view 3: the capability allow list
            assert!(include_str!("../capabilities/m2rc1-commands.json")
                .contains(&format!("allow-{}", command.replace('_', "-"))));
        }

        // view 1: the production `generate_handler!` literal list. The
        // production arm is the third `generate_handler!` in main.rs (probe,
        // ac1, production); pin it the same way the create family does.
        let production_handler = include_str!("main.rs")
            .split("builder.invoke_handler(tauri::generate_handler![")
            .nth(3)
            .unwrap()
            .split("])")
            .next()
            .unwrap();
        for command in CLEANUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production_handler.contains(command),
                "{command} missing from the production generate_handler! list"
            );
        }
    }

    /// SETTINGS-OPEN-C-2-BACKUP (design §3.4): the four `.nmbak` commands are
    /// exact, production-only, and synchronized across the R2-04 three views
    /// (build.rs ACL manifest, capability allow list, generate_handler).
    #[test]
    fn backup_commands_are_exact_and_production_only() {
        assert_eq!(
            BACKUP_PRODUCTION_ONLY_COMMANDS,
            &["backup_create", "backup_list", "backup_restore", "backup_delete"]
        );

        let production = command_allowlist(false, false);
        let probe = command_allowlist(true, false);
        let ac1 = command_allowlist(false, true);

        for command in BACKUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production.contains(command),
                "{command} must be on the production surface"
            );
            assert!(
                !probe.contains(command),
                "{command} must not appear in probe surface"
            );
            assert!(
                !ac1.contains(command),
                "{command} must not appear in ac1 surface"
            );
            assert!(include_str!("../build.rs").contains(command));
            assert!(include_str!("../capabilities/m2rc1-commands.json")
                .contains(&format!("allow-{}", command.replace('_', "-"))));
        }

        let production_handler = include_str!("main.rs")
            .split("builder.invoke_handler(tauri::generate_handler![")
            .nth(3)
            .unwrap()
            .split("])")
            .next()
            .unwrap();
        for command in BACKUP_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production_handler.contains(command),
                "{command} missing from the production generate_handler! list"
            );
        }
    }

    /// RUN-IPC-1: literal exact assertions for the Run transport family. The
    /// six names are pinned with a fixed literal expectation (never derived
    /// from the constant itself), the group must sit on the production surface
    /// and on NEITHER frozen test surface, and the production count stays pinned.
    #[test]
    fn run_transport_commands_are_exact_and_production_only() {
        assert_eq!(
            RUN_PRODUCTION_ONLY_COMMANDS,
            &[
                "library_start_run",
                "library_control_run",
                "library_resume_blocked_run",
                "library_get_run_snapshot",
                "library_get_task_projection",
                "library_retry_failed_targets",
            ]
        );
        // 61 production commands: the previous 54 plus the SETTINGS-OPEN-B-2
        // cleanup trio (PRODUCTION_COMMANDS, main.rs).
        assert_eq!(PRODUCTION_COMMANDS.len(), 61);

        let production = command_allowlist(false, false);
        let probe = command_allowlist(true, false);
        let ac1 = command_allowlist(false, true);

        for command in RUN_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production.contains(command),
                "{command} must be on the production surface"
            );
            assert!(
                !probe.contains(command),
                "{command} must not appear in probe surface"
            );
            assert!(
                !ac1.contains(command),
                "{command} must not appear in ac1 surface"
            );
        }
    }

    /// EXPORT-IPC-1: literal exact assertions for the export control/query family.
    #[test]
    fn export_query_commands_are_exact_and_production_only() {
        assert_eq!(
            EXPORT_PRODUCTION_ONLY_COMMANDS,
            &[
                "library_cancel_export",
                "library_get_export_snapshot",
                "library_get_export_history",
            ]
        );
        assert_eq!(PRODUCTION_COMMANDS.len(), 61);

        let production = command_allowlist(false, false);
        let probe = command_allowlist(true, false);
        let ac1 = command_allowlist(false, true);

        for command in EXPORT_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production.contains(command),
                "{command} must be on the production surface"
            );
            assert!(
                !probe.contains(command),
                "{command} must not appear in probe surface"
            );
            assert!(
                !ac1.contains(command),
                "{command} must not appear in ac1 surface"
            );
        }
    }

    /// P09-AC3-DELETE-1: literal exact assertions for the permanent delete family.
    #[test]
    fn delete_commands_are_exact_and_production_only() {
        assert_eq!(
            DELETE_PRODUCTION_ONLY_COMMANDS,
            &[
                "library_delete_book_permanently",
                "library_delete_books_permanently",
            ]
        );
        assert_eq!(PRODUCTION_COMMANDS.len(), 61);

        let production = command_allowlist(false, false);
        let probe = command_allowlist(true, false);
        let ac1 = command_allowlist(false, true);

        for command in DELETE_PRODUCTION_ONLY_COMMANDS {
            assert!(
                production.contains(command),
                "{command} must be on the production surface"
            );
            assert!(
                !probe.contains(command),
                "{command} must not appear in probe surface"
            );
            assert!(
                !ac1.contains(command),
                "{command} must not appear in ac1 surface"
            );
        }
    }

    /// RUN-IPC-1: a channel that does NOT override the Run methods must fail
    /// closed rather than pretend to succeed -- so a missing override is loud
    /// (CORE_UNAVAILABLE) instead of silently making the Workbench unusable.
    #[test]
    fn run_channel_defaults_are_fail_closed() {
        struct BareChannel;
        impl LibraryChannel for BareChannel {
            fn ping(&self) -> Result<PingResult, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn get_settings(
                &self,
                _section: Option<&str>,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn update_settings_section(
                &self,
                _section: &str,
                _values: &serde_json::Value,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn set_region_type(
                &self,
                _region_id: &str,
                _new_region_type: &str,
                _expected_revision: Option<i64>,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_regions(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_region_revisions(
                &self,
                _region_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn restore_region_revision(
                &self,
                _region_id: &str,
                _revision_no: i64,
                _expected_revision: i64,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn rerender_page(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn resolve_page_resource(
                &self,
                _page_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_chapters(&self, _book_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_chapter_pages(
                &self,
                _chapter_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
        }

        let bare = BareChannel;
        assert_eq!(
            bare.start_run("detect", &serde_json::json!({}), None, "key-1")
                .unwrap_err()
                .code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.control_run("run-1", "pause", None).unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.resume_blocked_run("run-1").unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.get_run_snapshot("run-1").unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.get_task_projection("run-1").unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.retry_failed_targets("run-1", "key-2")
                .unwrap_err()
                .code,
            "CORE_UNAVAILABLE"
        );
    }

    #[test]
    fn export_channel_defaults_are_fail_closed() {
        struct BareChannel;
        impl LibraryChannel for BareChannel {
            fn ping(&self) -> Result<PingResult, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn get_settings(
                &self,
                _section: Option<&str>,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn update_settings_section(
                &self,
                _section: &str,
                _values: &serde_json::Value,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn set_region_type(
                &self,
                _region_id: &str,
                _new_region_type: &str,
                _expected_revision: Option<i64>,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_regions(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_region_revisions(
                &self,
                _region_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn restore_region_revision(
                &self,
                _region_id: &str,
                _revision_no: i64,
                _expected_revision: i64,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn rerender_page(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn resolve_page_resource(
                &self,
                _page_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_chapters(&self, _book_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_chapter_pages(
                &self,
                _chapter_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
        }

        let bare = BareChannel;
        assert_eq!(
            bare.cancel_export("exp-1").unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.get_export_snapshot("exp-1").unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.get_export_history().unwrap_err().code,
            "CORE_UNAVAILABLE"
        );
    }

    #[test]
    fn delete_channel_defaults_are_fail_closed() {
        struct BareChannel;
        impl LibraryChannel for BareChannel {
            fn ping(&self) -> Result<PingResult, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn get_settings(
                &self,
                _section: Option<&str>,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn update_settings_section(
                &self,
                _section: &str,
                _values: &serde_json::Value,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn set_region_type(
                &self,
                _region_id: &str,
                _new_region_type: &str,
                _expected_revision: Option<i64>,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_regions(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_region_revisions(
                &self,
                _region_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn restore_region_revision(
                &self,
                _region_id: &str,
                _revision_no: i64,
                _expected_revision: i64,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn rerender_page(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn resolve_page_resource(
                &self,
                _page_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_chapters(&self, _book_id: &str) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
            fn list_chapter_pages(
                &self,
                _chapter_id: &str,
            ) -> Result<serde_json::Value, LibraryError> {
                unimplemented!("not exercised by this test")
            }
        }

        let bare = BareChannel;
        assert_eq!(
            bare.permanently_delete_book(PermanentlyDeleteBookPayload {
                book_id: "book-1".to_string(),
                confirm_permanent_delete: true,
            })
            .unwrap_err()
            .code,
            "CORE_UNAVAILABLE"
        );
        assert_eq!(
            bare.permanently_delete_books(PermanentlyDeleteBooksPayload {
                book_ids: vec!["book-1".to_string()],
                confirmed_book_ids: vec!["book-1".to_string()],
                confirm_count: 1,
                confirm_permanent_delete: true,
            })
            .unwrap_err()
            .code,
            "CORE_UNAVAILABLE"
        );
    }

    /// P04 AC1: Literal exact assertions for PAGE_NAV_PRODUCTION_ONLY_COMMANDS.
    /// Pin exact members with a fixed literal expectation (not derived from the constant
    /// itself) and verify that the group stays on the production surface while absent
    /// from probe and M2-AC1 surfaces.
    #[test]
    fn page_nav_production_only_commands_are_exact() {
        assert_eq!(
            PAGE_NAV_PRODUCTION_ONLY_COMMANDS,
            &["list_chapters", "list_chapter_pages"]
        );

        let production = command_allowlist(false, false);
        let probe = command_allowlist(true, false);
        let ac1 = command_allowlist(false, true);

        const EXPECTED_PAGE_NAV_COMMANDS: &[&str] = &["list_chapters", "list_chapter_pages"];
        for command in EXPECTED_PAGE_NAV_COMMANDS {
            assert!(
                production.contains(command),
                "{command} must stay in production surface"
            );
            assert!(
                !probe.contains(command),
                "{command} must not appear in probe surface"
            );
            assert!(
                !ac1.contains(command),
                "{command} must not appear in ac1 surface"
            );
        }
    }

    #[test]
    fn production_and_probe_surfaces_never_gain_ac1_commands() {
        for command in AC1_TEST_COMMANDS {
            assert!(!command_allowlist(false, false).contains(command));
            assert!(!command_allowlist(true, false).contains(command));
        }
    }

    #[test]
    fn ac1_commands_never_reappear_on_the_removed_surface() {
        for command in REMOVED_COMMANDS {
            assert!(!command_allowlist(false, true).contains(command));
        }
    }

    #[test]
    fn register_catalog_exists_on_no_surface() {
        for command in REMOVED_COMMANDS {
            assert!(!command_allowlist(false, false).contains(command));
            assert!(!command_allowlist(true, false).contains(command));
        }
        // the removed surface must stay removed even if someone re-adds to
        // the probe list: gate the exact constants, not just membership
        assert_eq!(REMOVED_COMMANDS, &["register_catalog"]);
    }

    #[test]
    fn no_surface_command_carries_a_ttl_parameter_shape() {
        // the production issue command fn signature has no TTL parameter
        // (compile-time); this pins the wire/request level: the issued probe
        // override lives behind `probe_issue_url` only.
        assert!(!PRODUCTION_COMMANDS.contains(&"probe_issue_url"));
    }

    #[test]
    fn host_control_operations_are_never_webview_commands() {
        const HOST_CONTROL: &[&str] = &[
            "OpenHostSession",
            "RegisterImportSource",
            "RevokeImportSource",
            "RegisterExportTarget",
            "RevokeExportTarget",
            "CloseHostSession",
        ];
        for command in HOST_CONTROL {
            assert!(!PRODUCTION_COMMANDS.contains(command));
            assert!(!command_allowlist(false, false).contains(command));
            assert!(!command_allowlist(true, false).contains(command));
            assert!(!command_allowlist(false, true).contains(command));
        }
        assert_eq!(HOST_ISSUER_PRODUCTION_ONLY_COMMANDS.len(), 3);
    }

    #[test]
    fn issue_wire_never_carries_path_or_ttl() {
        let params = build_issue_params("res-001", "rev-1", None);
        let text = serde_json::to_string(&params).unwrap();
        assert!(text.contains("\"resource_id\""));
        assert!(text.contains("\"revision_fingerprint\""));
        assert!(!text.contains("rel_path"));
        assert!(!text.contains("scope_class"));
        assert!(!text.contains("ttl"));
        let probe_params = build_issue_params("res-001", "rev-1", Some(0.3));
        let probe_text = serde_json::to_string(&probe_params).unwrap();
        assert!(probe_text.contains("\"ttl_seconds\":0.3"));
        assert!(!probe_text.contains("rel_path"));
    }

    #[test]
    fn mock_issue_without_catalog_entry_fails_closed() {
        let channel = MockCoreChannel::new();
        let error = channel.issue("res-never", "rev-1").unwrap_err();
        assert_eq!(error.code, "RESOURCE_NOT_CATALOGED");
        assert!(
            channel
                .issue_probe("res-never", "rev-1", 5.0)
                .unwrap_err()
                .code
                == "RESOURCE_NOT_CATALOGED"
        );
    }

    #[test]
    fn url_builder_is_opaque_only() {
        let url = build_url(&"a".repeat(ID_LENGTH));
        assert!(url.starts_with("http://m2res.localhost/m2id/"));
        assert!(!url.contains('\\') && !url.contains("C:"));
        assert_eq!(url.rsplit('/').next().unwrap().len(), ID_LENGTH);
    }

    #[test]
    fn malformed_ids_rejected_before_lookup() {
        let (env, _sha) = env_with_fixture(b"payload");
        for bad in ["not-an-id", "", &"x".repeat(ID_LENGTH + 1), "../escape"] {
            let response = handle_m2res_request(&url_for(bad, Some(0)), &env.channel, &env.roots);
            assert_eq!(response.status, 400, "id {bad:?}");
            assert_eq!(
                std::str::from_utf8(&response.body).unwrap(),
                "{\"code\":\"REF_MALFORMED\"}"
            );
        }
    }

    #[test]
    fn unknown_well_formed_id_typed_404() {
        let (env, _sha) = env_with_fixture(b"payload");
        let well_formed = "A".repeat(ID_LENGTH).replace('A', "a");
        let response =
            handle_m2res_request(&url_for(&well_formed, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.status, 404);
        assert_eq!(
            std::str::from_utf8(&response.body).unwrap(),
            "{\"code\":\"REF_UNKNOWN_ID\"}"
        );
    }

    #[test]
    fn chunk_offset_beyond_size_rejected() {
        let (env, _sha) = env_with_fixture(b"tiny payload");
        let opaque = registered(&env, "res-001", "asset.png", b"tiny payload");
        let response = handle_m2res_request(&url_for(&opaque, Some(1)), &env.channel, &env.roots);
        assert_eq!(response.status, 400);
        let body = std::str::from_utf8(&response.body).unwrap();
        assert!(
            body.contains("REF_MALFORMED") || body.contains("REF_UNKNOWN_ID"),
            "{body}"
        );
    }

    #[test]
    fn responses_carry_no_store() {
        let (env, _sha) = env_with_fixture(b"payload");
        let well_formed = "b".repeat(ID_LENGTH).replace('b', "c");
        let response =
            handle_m2res_request(&url_for(&well_formed, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.cache_control, "no-store");
    }

    #[test]
    fn revoked_id_propagates_typed_410() {
        let (env, _sha) = env_with_fixture(b"payload");
        let opaque = registered(&env, "res-001", "asset.png", b"payload");
        env.channel.revoke(&opaque).unwrap();
        let response = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.status, 410);
        assert_eq!(
            std::str::from_utf8(&response.body).unwrap(),
            "{\"code\":\"REF_REVOKED\"}"
        );
    }

    #[test]
    fn full_chunk_serving_matches_bytes_and_digest_check() {
        let payload: Vec<u8> = (0..64_000u32).map(|i| (i % 251) as u8).collect();
        let (env, sha) = env_with_fixture(&payload);
        let opaque = registered(&env, "res-001", "asset.png", &payload);
        assert_eq!(sha.len(), 64);
        let response = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.status, 200);
        assert_eq!(response.body.len(), payload.len());
        assert_eq!(&response.body[..], &payload[..]);
        assert_eq!(response.cache_control, "no-store");
    }

    /// Renamed from `identity_change_invalidates_cache_entry`
    /// (M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF): with the write-only GrantCache
    /// removed there is no cache entry to invalidate. What the test actually
    /// pins is the per-request file-identity check: a file replaced by a NEW
    /// inode (different NTFS file index) is refused with the typed
    /// FILE_IDENTITY_CHANGED on the very next request.
    #[test]
    fn identity_change_rejected_by_per_request_verification() {
        let payload = b"payload-v1".to_vec();
        let (env, _sha) = env_with_fixture(&payload);
        let opaque = registered(&env, "res-001", "asset.png", &payload);
        // first request verifies and serves
        let first = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.roots);
        assert_eq!(first.status, 200);
        // replace with a *new* file (unlink first: an in-place overwrite keeps
        // the same NTFS file index, the M2-S2 lesson)
        let replaced = b"payload-v2-with-different-length!!";
        let target = env.roots.derived.join("asset.png");
        std::fs::remove_file(&target).unwrap();
        std::fs::write(&target, replaced).unwrap();
        let second = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.roots);
        assert_eq!(second.status, 400);
        assert_eq!(
            std::str::from_utf8(&second.body).unwrap(),
            "{\"code\":\"FILE_IDENTITY_CHANGED\"}"
        );
    }

    // ---- M2-RC1-FIX regression tests (DSH F-01/F-02) ----------------------
    // These MUST fail against the pre-fix cache (grant served from cache
    // without consulting the Core) and pass after the repair.

    #[test]
    fn f01_fetch_then_revoke_then_fetch_must_be_typed() {
        let payload = b"cached-then-revoked";
        let (env, _sha) = env_with_fixture(payload);
        let opaque = registered(&env, "res-001", "asset.png", payload);
        let url = url_for(&opaque, Some(0));

        // first fetch establishes the grant cache
        let first = handle_m2res_request(&url, &env.channel, &env.roots);
        assert_eq!(first.status, 200, "first fetch must serve");

        // Core-side revocation AFTER the cache is warm
        env.channel.revoke(&opaque).unwrap();

        // the next request must consult the Core and reject
        let second = handle_m2res_request(&url, &env.channel, &env.roots);
        assert_eq!(
            second.status, 410,
            "revoked URL must not be served from cache"
        );
        assert_eq!(
            std::str::from_utf8(&second.body).unwrap(),
            "{\"code\":\"REF_REVOKED\"}"
        );
    }

    #[test]
    fn f01_ttl_expiry_invalidates_cached_grant() {
        let payload = b"cached-then-expired";
        let (env, _sha) = env_with_fixture(payload);
        // probe-only short TTL through the probe issue path
        env.channel.register("res-001", "asset.png").unwrap();
        let issued = env.channel.issue_probe("res-001", "rev-1", 0.3).unwrap();
        // align mock facts like registered() does
        {
            let mut table = env.channel.table.lock().unwrap();
            let entry = table.get_mut(&issued.opaque_id).unwrap();
            entry.grant.size = payload.len() as u64;
            entry.grant.sha256 = sha_hex(payload);
        }
        let facts =
            resource_protocol::capture_facts_for_tests(&env.roots.derived.join("asset.png"))
                .expect("fixture facts");
        {
            let mut table = env.channel.table.lock().unwrap();
            let entry = table.get_mut(&issued.opaque_id).unwrap();
            entry.grant.volume_serial = facts.0;
            entry.grant.file_index = facts.1;
        }
        let url = url_for(&issued.opaque_id, Some(0));

        let first = handle_m2res_request(&url, &env.channel, &env.roots);
        assert_eq!(first.status, 200, "first fetch must serve within TTL");

        std::thread::sleep(std::time::Duration::from_millis(500));

        let second = handle_m2res_request(&url, &env.channel, &env.roots);
        assert_eq!(
            second.status, 410,
            "expired URL must not be served from cache"
        );
        assert_eq!(
            std::str::from_utf8(&second.body).unwrap(),
            "{\"code\":\"REF_EXPIRED\"}"
        );
    }

    #[test]
    fn f02_equal_size_rewrite_after_first_verify_rejected() {
        let payload = b"equal-size-rewrite-payload";
        let (env, _sha) = env_with_fixture(payload);
        let opaque = registered(&env, "res-001", "asset.png", payload);
        let url = url_for(&opaque, Some(0));

        let first = handle_m2res_request(&url, &env.channel, &env.roots);
        assert_eq!(first.status, 200, "first fetch verifies and caches");

        // equal-size IN-PLACE rewrite: same path, same length, same file index
        // (NTFS keeps the index on overwrite), different bytes + new mtime
        let flipped: Vec<u8> = payload.iter().map(|b| b ^ 0x5A).collect();
        let target = env.roots.derived.join("asset.png");
        let existing = std::fs::OpenOptions::new()
            .write(true)
            .open(&target)
            .unwrap();
        {
            use std::io::{Seek, SeekFrom, Write};
            let mut existing = existing;
            existing.seek(SeekFrom::Start(0)).unwrap();
            existing.write_all(&flipped).unwrap();
        }

        let second = handle_m2res_request(&url, &env.channel, &env.roots);
        assert_eq!(second.status, 400, "rewritten content must not be served");
        assert_eq!(
            std::str::from_utf8(&second.body).unwrap(),
            "{\"code\":\"CONTENT_DIGEST_MISMATCH\"}"
        );
    }

    /// F-02 fix stability loop (M2-FIX-F02 AC3): replays the exact f02
    /// scenario (first fetch verifies, equal-size in-place rewrite, second
    /// fetch) for 50 independent rounds under the default harness and
    /// requires the typed rejection EVERY round. The AC1 diagnostic probe
    /// reproduced the pre-fix flake 3/3 runs (rounds 5/0/2, stat mtime
    /// identical across the rewrite, delta=0), so 50 green rounds here is
    /// the directed stability evidence for the always-reverify fix.
    #[test]
    fn f02_equal_size_rewrite_stability_loop() {
        let payload = b"equal-size-rewrite-payload";
        for round in 0..50u32 {
            let (env, _sha) = env_with_fixture(payload);
            let opaque = registered(&env, "res-001", "asset.png", payload);
            let url = url_for(&opaque, Some(0));

            let first = handle_m2res_request(&url, &env.channel, &env.roots);
            assert_eq!(first.status, 200, "round {round}: first fetch must serve");

            let flipped: Vec<u8> = payload.iter().map(|b| b ^ 0x5A).collect();
            let target = env.roots.derived.join("asset.png");
            let existing = std::fs::OpenOptions::new()
                .write(true)
                .open(&target)
                .unwrap();
            {
                use std::io::{Seek, SeekFrom};
                let mut existing = existing;
                existing.seek(SeekFrom::Start(0)).unwrap();
                existing.write_all(&flipped).unwrap();
            }

            let second = handle_m2res_request(&url, &env.channel, &env.roots);
            assert_eq!(
                second.status, 400,
                "round {round}: rewritten content must not be served"
            );
            assert_eq!(
                std::str::from_utf8(&second.body).unwrap(),
                "{\"code\":\"CONTENT_DIGEST_MISMATCH\"}",
                "round {round}: typed rejection required"
            );
        }
    }

    // ---- AC2 chunk-request cost probe (M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF)
    // `#[ignore]`d: measured explicitly, never in the default suite. Run with
    // `cargo test --bin m2rc1-desktop perf_chunk_request_digest_cost -- --ignored --nocapture`
    // (same command under `--release` for the release-profile column). Warm
    // request first, then N timed identical requests; the average is the
    // per-request figure recorded in the task's comparison table.
    #[test]
    #[ignore]
    fn perf_chunk_request_digest_cost() {
        let cases: &[(&str, usize, u64, u32)] = &[
            // (label, payload_bytes, chunk_index, timed rounds)
            ("1MiB-chunk0", 1024 * 1024, 0, 20),
            ("16MiB-chunk0", 16 * 1024 * 1024, 0, 10),
            ("32MiB-chunk1", 32 * 1024 * 1024, 1, 5),
        ];
        for (label, size, chunk, rounds) in cases {
            let payload: Vec<u8> = (0..*size as u64).map(|i| (i % 251) as u8).collect();
            let (env, _sha) = env_with_fixture(&payload);
            let opaque = registered(&env, "res-001", "asset.png", &payload);
            let url = url_for(&opaque, Some(*chunk));
            let want = std::cmp::min(
                *size as u64 - chunk * resource_protocol::CHUNK_SIZE,
                resource_protocol::CHUNK_SIZE,
            ) as usize;
            // untimed warm-up: OS file cache + allocator reach steady state
            let warm = handle_m2res_request(&url, &env.channel, &env.roots);
            assert_eq!(warm.status, 200, "{label}: warm-up request must serve");
            assert_eq!(warm.body.len(), want, "{label}: warm-up body size");
            let start = std::time::Instant::now();
            for _ in 0..*rounds {
                let response = handle_m2res_request(&url, &env.channel, &env.roots);
                assert_eq!(response.status, 200, "{label}: timed request must serve");
                assert_eq!(response.body.len(), want, "{label}: timed body size");
                assert_eq!(response.cache_control, "no-store");
            }
            let elapsed = start.elapsed();
            println!(
                "PERF {label}: rounds={} total={elapsed:?} avg={:?}/request",
                rounds,
                elapsed / *rounds
            );
        }
    }

    /// Integration with the real Python Core sidecar: exercises the stdio
    /// JSON-lines bridge end to end (catalog seed -> issue -> resolve ->
    /// grant facts), including the RC2 catalog-authority denial (an
    /// uncataloged id must fail closed).
    #[test]
    fn real_core_sidecar_round_trip() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .or_else(|_| {
                // default: resolve ../../../../src relative to this manifest
                let manifest = env!("CARGO_MANIFEST_DIR");
                let mut path = PathBuf::from(manifest);
                for _ in 0..3 {
                    path.pop();
                }
                Ok::<PathBuf, std::env::VarError>(path.join("src"))
            })
            .unwrap();
        let dir = tempfile::tempdir().unwrap();
        let derived = dir.path().join("scope").join("derived");
        std::fs::create_dir_all(&derived).unwrap();
        std::fs::write(derived.join("asset.png"), b"sidecar-payload").unwrap();

        // seed the Core/SQLite catalog through the real loader entry point
        let catalog_db = dir.path().join("catalog.sqlite");
        // M2-DERIVED-GC-2 (R4-A1): the seed creates a brand-new catalog, so
        // the trusted first-bind flag runs against THIS loader's own derived
        // root before the rows are written; an unbound catalog would be
        // refused by the store.
        let seed = std::process::Command::new(&python)
            .arg("-m")
            .arg("infrastructure.resource_channel.catalog_loader")
            .current_dir(&src_root)
            .arg("--db")
            .arg(&catalog_db)
            .arg("--initialize-preview-namespace")
            .arg(&derived)
            .arg("--set")
            .arg("res-sidecar=asset.png")
            .env("PYTHONPATH", &src_root)
            .output()
            .expect("catalog loader spawn");
        assert!(
            seed.status.success(),
            "catalog loader failed: {}",
            String::from_utf8_lossy(&seed.stderr)
        );

        let channel = StdioCoreChannel::spawn(
            &python,
            &src_root,
            &derived,
            &dir.path().join("scope").join("managed"),
            &catalog_db,
        )
        .expect("sidecar spawn");
        let issued = channel.issue("res-sidecar", "rev-1").expect("issue");
        assert!(issued.opaque_id.starts_with("m2id.v1."));
        let grant = channel.resolve(&issued.opaque_id).expect("resolve");
        assert_eq!(grant.rel_path, "asset.png");
        assert_eq!(grant.size, 15);
        assert_eq!(grant.sha256.len(), 64);
        channel.revoke(&issued.opaque_id).unwrap();
        let error = channel.resolve(&issued.opaque_id).unwrap_err();
        assert_eq!(error.code, "REF_REVOKED");
    }

    /// RC2 (F-03) denial through the REAL bridge: an uncataloged resource id
    /// fails closed, and a ttl_seconds above the Core default is refused.
    #[test]
    fn real_core_sidecar_denies_uncataloged_and_extended_ttl() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                for _ in 0..3 {
                    path.pop();
                }
                path.join("src")
            });
        let dir = tempfile::tempdir().unwrap();
        let derived = dir.path().join("scope").join("derived");
        std::fs::create_dir_all(&derived).unwrap();
        std::fs::write(derived.join("asset.png"), b"sidecar-payload").unwrap();
        let catalog_db = dir.path().join("catalog.sqlite");
        // M2-DERIVED-GC-2 (R4-A1): the seed creates a brand-new catalog, so
        // the trusted first-bind flag runs against THIS loader's own derived
        // root before the rows are written; an unbound catalog would be
        // refused by the store.
        let seed = std::process::Command::new(&python)
            .arg("-m")
            .arg("infrastructure.resource_channel.catalog_loader")
            .current_dir(&src_root)
            .arg("--db")
            .arg(&catalog_db)
            .arg("--initialize-preview-namespace")
            .arg(&derived)
            .arg("--set")
            .arg("res-sidecar=asset.png")
            .env("PYTHONPATH", &src_root)
            .output()
            .expect("catalog loader spawn");
        assert!(seed.status.success());

        let channel = StdioCoreChannel::spawn(
            &python,
            &src_root,
            &derived,
            &dir.path().join("scope").join("managed"),
            &catalog_db,
        )
        .expect("sidecar spawn");

        // uncataloged id -> typed fail-closed
        let error = channel.issue("res-never-cataloged", "rev-1").unwrap_err();
        assert_eq!(error.code, "RESOURCE_NOT_CATALOGED");

        // ttl extension above the ruled default -> typed refusal
        let error = channel
            .issue_probe("res-sidecar", "rev-1", 999_999.0)
            .unwrap_err();
        assert_eq!(error.code, "REF_MALFORMED");
    }

    #[test]
    fn mock_library_channel_integration() {
        use crate::library_bridge::MockLibraryChannel;

        let channel = MockLibraryChannel::new();
        let ping = channel.ping().unwrap();
        assert_eq!(ping.status, "ready");
        assert_eq!(ping.protocol_version.major, 1);
        assert_eq!(ping.protocol_version.minor, 0);
        assert!(ping
            .capabilities
            .contains(&"library.list_books".to_string()));

        let books = channel.list_books().unwrap();
        assert!(books.is_empty());
    }

    #[test]
    fn real_library_sidecar_round_trip_and_eof() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                for _ in 0..3 {
                    path.pop();
                }
                path.join("src")
            });
        let dir = tempfile::tempdir().unwrap();
        let data_root = dir.path().join("data_root");
        std::fs::create_dir_all(&data_root).unwrap();

        let channel = StdioLibraryChannel::spawn(&python, &src_root, Some(&data_root))
            .expect("library sidecar spawn");

        // 1. Ping round-trip succeeds
        let ping = channel.ping().expect("ping");
        assert_eq!(ping.status, "ready");
        assert_eq!(ping.protocol_version.major, 2);
        assert_eq!(ping.protocol_version.minor, 3);
        assert!(ping
            .capabilities
            .contains(&"library.list_books".to_string()));

        // 2. List books succeeds on empty store
        let books = channel.list_books().expect("list_books");
        assert!(books.is_empty());

        // 3. Kill child to simulate EOF / process exit
        channel.kill_for_test();

        // 4. Subsequent call maps to CORE_UNAVAILABLE
        let err = channel.ping().unwrap_err();
        assert_eq!(err.code, "CORE_UNAVAILABLE");
        assert!(err.retryable);
    }

    #[test]
    fn real_core_sidecar_create_commands_use_minor_8_and_existing_reads() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                for _ in 0..3 {
                    path.pop();
                }
                path.join("src")
            });
        let dir = tempfile::tempdir().unwrap();
        let data_root = dir.path().join("data_root");
        std::fs::create_dir_all(&data_root).unwrap();
        let channel = StdioLibraryChannel::spawn(&python, &src_root, Some(&data_root))
            .expect("Core 2.8 sidecar spawn");

        let book = channel.create_book("FEAT-CREATE-3 book").unwrap();
        assert_eq!(book.title, "FEAT-CREATE-3 book");
        assert!(book.page_count.is_none());
        let chapter = channel
            .create_chapter(&book.book_id, "First chapter", None)
            .unwrap();
        assert_eq!(chapter.title, "First chapter");
        assert_eq!(chapter.chapter_number, "");

        assert_eq!(channel.list_books().unwrap().len(), 1);
        let chapters = channel.list_chapters(&book.book_id).unwrap();
        assert_eq!(chapters["chapters"].as_array().unwrap().len(), 1);
        assert_eq!(chapters["chapters"][0]["chapter_id"], chapter.chapter_id);
    }

    /// M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): the settings pair
    /// end to end over the REAL production Core sidecar — write-side
    /// validation persists a legal sfx.policy and reads it back, while an
    /// illegal value is typed-rejected (INVALID_REQUEST) BEFORE persistence
    /// (the M2-SFX-ENTRY r1 R4 lesson: the store must keep its previous
    /// state so the next assembly can never hit a startup block).
    #[test]
    fn real_core_sidecar_settings_round_trip_and_typed_rejection() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                for _ in 0..3 {
                    path.pop();
                }
                path.join("src")
            });
        let dir = tempfile::tempdir().unwrap();
        let data_root = dir.path().join("data_root");
        std::fs::create_dir_all(&data_root).unwrap();

        let channel = StdioLibraryChannel::spawn(&python, &src_root, Some(&data_root))
            .expect("library sidecar spawn");

        // 1. full projection read on a fresh install
        let full = channel.get_settings(None).expect("full settings read");
        assert!(
            full.get("settings").is_some(),
            "projection envelope: {full}"
        );

        // 2. unset sfx section reads as JSON null (frozen None channel)
        let unset = channel.get_settings(Some("sfx")).expect("section read");
        assert_eq!(unset["settings"]["sfx"], serde_json::Value::Null);

        // 3. legal write persists and the result carries the new value
        let updated = channel
            .update_settings_section("sfx", &serde_json::json!({ "policy": "translate" }))
            .expect("legal update");
        assert_eq!(updated["settings"]["sfx"]["policy"], "translate");
        let readback = channel.get_settings(Some("sfx")).expect("readback");
        assert_eq!(readback["settings"]["sfx"]["policy"], "translate");

        // 4. illegal value: typed INVALID_REQUEST, and the store still holds
        //    the previous legal value (write rejected BEFORE persistence)
        let error = channel
            .update_settings_section("sfx", &serde_json::json!({ "policy": "bogus" }))
            .unwrap_err();
        assert_eq!(error.code, "INVALID_REQUEST");
        assert_eq!(error.category, "validation");
        let still = channel
            .get_settings(Some("sfx"))
            .expect("read after reject");
        assert_eq!(still["settings"]["sfx"]["policy"], "translate");

        let profiles = channel
            .p15_settings(
                P15SettingsCommand::ProviderProfilesList,
                serde_json::json!({}),
            )
            .expect("Core 2.7 Provider profile list");
        assert!(profiles["profiles"].is_array());

        let target = P15CredentialTarget::ProviderApi {
            profile_id: "missing-profile".into(),
        };
        let bind_error = channel
            .bind_profile_credential(target.clone(), "unused-private-reference")
            .unwrap_err();
        assert_eq!(bind_error.code, "TARGET_NOT_FOUND");
        let clear_error = channel.clear_profile_credential(target).unwrap_err();
        assert_eq!(clear_error.code, "TARGET_NOT_FOUND");
    }

    /// M2-REGION-RETYPE-CORE r1 P3-4: the retype read/write pair end to end
    /// over the REAL production Core sidecar — the full
    /// Rust→stdio→Core→SQLite→Rust chain with the typed mapping intact:
    /// an unknown page_id reads as an EMPTY regions array (contract rev 1.4
    /// §5.4 footnote a — NOT an error), and an unknown region_id is typed
    /// TARGET_NOT_FOUND/not_found (no raw traceback on the error surface).
    #[test]
    fn real_core_sidecar_retype_pair_empty_page_and_typed_rejection() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                for _ in 0..3 {
                    path.pop();
                }
                path.join("src")
            });
        let dir = tempfile::tempdir().unwrap();
        let data_root = dir.path().join("data_root");
        std::fs::create_dir_all(&data_root).unwrap();

        let channel = StdioLibraryChannel::spawn(&python, &src_root, Some(&data_root))
            .expect("library sidecar spawn");

        // 1. footnote a: unknown page -> {"regions": []}, a successful read
        let empty = channel
            .list_regions("no-such-page")
            .expect("unknown page is an empty read, not an error");
        assert_eq!(empty["regions"], serde_json::json!([]));

        // 2. unknown region -> typed TARGET_NOT_FOUND (not_found category)
        let error = channel
            .set_region_type("no-such-region", "sfx", None)
            .unwrap_err();
        assert_eq!(error.code, "TARGET_NOT_FOUND");
        assert_eq!(error.category, "not_found");
    }

    #[test]
    fn real_core_sidecar_rc4_commands_round_trip_typed_errors() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let src_root = std::env::var("M2RC1_SRC_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                for _ in 0..3 {
                    path.pop();
                }
                path.join("src")
            });
        let dir = tempfile::tempdir().unwrap();
        let data_root = dir.path().join("data_root");
        std::fs::create_dir_all(&data_root).unwrap();
        let channel = StdioLibraryChannel::spawn(&python, &src_root, Some(&data_root))
            .expect("library sidecar spawn");

        assert_eq!(
            channel
                .list_region_revisions("no-such-region")
                .unwrap_err()
                .code,
            "TARGET_NOT_FOUND"
        );
        assert_eq!(
            channel
                .restore_region_revision("no-such-region", 1, 1)
                .unwrap_err()
                .code,
            "TARGET_NOT_FOUND"
        );
        assert_eq!(
            channel.rerender_page("no-such-page").unwrap_err().code,
            "TARGET_NOT_FOUND"
        );
    }

    struct SequencedRerenderLibrary {
        inner: MockLibraryChannel,
        calls: std::sync::atomic::AtomicUsize,
        active: std::sync::atomic::AtomicUsize,
        max_active: Mutex<usize>,
        first_entered: Mutex<std::sync::mpsc::Sender<()>>,
        release_first: Mutex<std::sync::mpsc::Receiver<()>>,
        second_entered: Mutex<std::sync::mpsc::Sender<()>>,
    }

    impl LibraryChannel for SequencedRerenderLibrary {
        fn ping(&self) -> Result<PingResult, LibraryError> {
            self.inner.ping()
        }
        fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
            self.inner.list_books()
        }
        fn get_settings(&self, section: Option<&str>) -> Result<serde_json::Value, LibraryError> {
            self.inner.get_settings(section)
        }
        fn update_settings_section(
            &self,
            section: &str,
            values: &serde_json::Value,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner.update_settings_section(section, values)
        }
        fn set_region_type(
            &self,
            region_id: &str,
            new_region_type: &str,
            expected_revision: Option<i64>,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner
                .set_region_type(region_id, new_region_type, expected_revision)
        }
        fn list_regions(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.list_regions(page_id)
        }
        fn list_region_revisions(
            &self,
            region_id: &str,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner.list_region_revisions(region_id)
        }
        fn restore_region_revision(
            &self,
            region_id: &str,
            revision_no: i64,
            expected_revision: i64,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner
                .restore_region_revision(region_id, revision_no, expected_revision)
        }
        fn rerender_page(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
            let ordinal = self.calls.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            let active = self
                .active
                .fetch_add(1, std::sync::atomic::Ordering::SeqCst)
                + 1;
            {
                let mut max_active = self.max_active.lock().unwrap();
                *max_active = (*max_active).max(active);
            }
            if ordinal == 0 {
                self.first_entered.lock().unwrap().send(()).unwrap();
                self.release_first.lock().unwrap().recv().unwrap();
            } else {
                self.second_entered.lock().unwrap().send(()).unwrap();
            }
            self.active
                .fetch_sub(1, std::sync::atomic::Ordering::SeqCst);
            Ok(serde_json::json!({
                "page_id": page_id,
                "artifact_id": "artifact",
                "revision_no": ordinal + 1,
                "reports": [],
                "preview": {"resource_id": format!("render-{}", ordinal + 1), "revision": format!("rev-{}", ordinal + 1)},
                "preview_error": null,
            }))
        }
        fn resolve_page_resource(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.resolve_page_resource(page_id)
        }
        fn list_chapters(&self, book_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.list_chapters(book_id)
        }
        fn list_chapter_pages(&self, chapter_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.list_chapter_pages(chapter_id)
        }

        // RUN-IPC-1: the Run family needs no rerender sequencing -- forward
        // straight through to the inner channel.
        fn start_run(
            &self,
            command: &str,
            scope: &serde_json::Value,
            overrides: Option<&serde_json::Value>,
            idempotency_key: &str,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner
                .start_run(command, scope, overrides, idempotency_key)
        }

        fn control_run(
            &self,
            run_id: &str,
            action: &str,
            idempotency_key: Option<&str>,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner.control_run(run_id, action, idempotency_key)
        }

        fn resume_blocked_run(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.resume_blocked_run(run_id)
        }

        fn get_run_snapshot(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.get_run_snapshot(run_id)
        }

        fn get_task_projection(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
            self.inner.get_task_projection(run_id)
        }

        fn retry_failed_targets(
            &self,
            run_id: &str,
            idempotency_key: &str,
        ) -> Result<serde_json::Value, LibraryError> {
            self.inner.retry_failed_targets(run_id, idempotency_key)
        }

        fn cancel_export(
            &self,
            export_id: &str,
        ) -> Result<ExportProgressSnapshotView, LibraryError> {
            self.inner.cancel_export(export_id)
        }

        fn get_export_snapshot(
            &self,
            export_id: &str,
        ) -> Result<ExportProgressSnapshotView, LibraryError> {
            self.inner.get_export_snapshot(export_id)
        }

        fn get_export_history(&self) -> Result<ExportHistoryResponseView, LibraryError> {
            self.inner.get_export_history()
        }
    }

    /// The shared Arc handle forwards to the library so the test can keep
    /// atomic/counter handles for assertions while AppState owns a boxed
    /// channel.
    impl LibraryChannel for Arc<SequencedRerenderLibrary> {
        fn ping(&self) -> Result<PingResult, LibraryError> {
            (**self).ping()
        }
        fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
            (**self).list_books()
        }
        fn get_settings(&self, section: Option<&str>) -> Result<serde_json::Value, LibraryError> {
            (**self).get_settings(section)
        }
        fn update_settings_section(
            &self,
            section: &str,
            values: &serde_json::Value,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).update_settings_section(section, values)
        }
        fn set_region_type(
            &self,
            region_id: &str,
            new_region_type: &str,
            expected_revision: Option<i64>,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).set_region_type(region_id, new_region_type, expected_revision)
        }
        fn list_regions(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).list_regions(page_id)
        }
        fn list_region_revisions(
            &self,
            region_id: &str,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).list_region_revisions(region_id)
        }
        fn restore_region_revision(
            &self,
            region_id: &str,
            revision_no: i64,
            expected_revision: i64,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).restore_region_revision(region_id, revision_no, expected_revision)
        }
        fn rerender_page(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).rerender_page(page_id)
        }
        fn resolve_page_resource(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).resolve_page_resource(page_id)
        }
        fn list_chapters(&self, book_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).list_chapters(book_id)
        }
        fn list_chapter_pages(&self, chapter_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).list_chapter_pages(chapter_id)
        }

        // RUN-IPC-1: forward the Run family through the shared Arc handle.
        fn start_run(
            &self,
            command: &str,
            scope: &serde_json::Value,
            overrides: Option<&serde_json::Value>,
            idempotency_key: &str,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).start_run(command, scope, overrides, idempotency_key)
        }

        fn control_run(
            &self,
            run_id: &str,
            action: &str,
            idempotency_key: Option<&str>,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).control_run(run_id, action, idempotency_key)
        }

        fn resume_blocked_run(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).resume_blocked_run(run_id)
        }

        fn get_run_snapshot(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).get_run_snapshot(run_id)
        }

        fn get_task_projection(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
            (**self).get_task_projection(run_id)
        }

        fn retry_failed_targets(
            &self,
            run_id: &str,
            idempotency_key: &str,
        ) -> Result<serde_json::Value, LibraryError> {
            (**self).retry_failed_targets(run_id, idempotency_key)
        }

        fn cancel_export(
            &self,
            export_id: &str,
        ) -> Result<ExportProgressSnapshotView, LibraryError> {
            (**self).cancel_export(export_id)
        }

        fn get_export_snapshot(
            &self,
            export_id: &str,
        ) -> Result<ExportProgressSnapshotView, LibraryError> {
            (**self).get_export_snapshot(export_id)
        }

        fn get_export_history(&self) -> Result<ExportHistoryResponseView, LibraryError> {
            (**self).get_export_history()
        }
    }

    #[test]
    fn rerenders_hold_one_global_lock_through_core_and_preview_swap() {
        use std::sync::atomic::AtomicUsize;
        use std::sync::mpsc;
        use std::sync::Arc;
        use std::time::Duration;

        let (first_entered_tx, first_entered_rx) = mpsc::channel();
        let (release_first_tx, release_first_rx) = mpsc::channel();
        let (second_entered_tx, second_entered_rx) = mpsc::channel();
        let library = Arc::new(SequencedRerenderLibrary {
            inner: MockLibraryChannel::new(),
            calls: AtomicUsize::new(0),
            active: AtomicUsize::new(0),
            max_active: Mutex::new(0),
            first_entered: Mutex::new(first_entered_tx),
            release_first: Mutex::new(release_first_rx),
            second_entered: Mutex::new(second_entered_tx),
        });
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.register("render-1", "derived/render-1.png").unwrap();
        core.register("render-2", "derived/render-2.png").unwrap();
        let old_ref = core.issue("render-0", "rev-0").unwrap();
        let first_ref = core.issue("render-1", "rev-1").unwrap();
        let dir = tempfile::tempdir().unwrap();
        let state = Arc::new(AppState {
            channel: Box::new(core),
            roots: ScopeRoots {
                derived: dir.path().join("derived"),
                managed: dir.path().join("managed"),
            },
            fixture_shas: serde_json::json!({}),
            ac1: None,
            library: Some(Box::new(library.clone())),
            credential_operations: Mutex::new(()),
            render_preview_resources: Mutex::new(HashMap::from([(
                "page".to_string(),
                "render-0".to_string(),
            )])),
        });

        let first_state = state.clone();
        let first = std::thread::spawn(move || rerender_page_from_core(&first_state, "page"));
        first_entered_rx
            .recv_timeout(Duration::from_secs(2))
            .unwrap();

        let second_state = state.clone();
        let (second_started_tx, second_started_rx) = mpsc::channel();
        let second = std::thread::spawn(move || {
            second_started_tx.send(()).unwrap();
            rerender_page_from_core(&second_state, "page")
        });
        second_started_rx
            .recv_timeout(Duration::from_secs(2))
            .unwrap();
        assert!(second_entered_rx
            .recv_timeout(Duration::from_millis(100))
            .is_err());
        assert_eq!(library.calls.load(std::sync::atomic::Ordering::SeqCst), 1);

        release_first_tx.send(()).unwrap();
        first.join().unwrap().unwrap();
        second.join().unwrap().unwrap();
        assert_eq!(*library.max_active.lock().unwrap(), 1);
        assert_eq!(
            state.render_preview_resources.lock().unwrap().get("page"),
            Some(&"render-2".to_string())
        );
        assert_eq!(
            state.channel.resolve(&old_ref.opaque_id).unwrap_err().code,
            "REF_REVOKED"
        );
        assert_eq!(
            state
                .channel
                .resolve(&first_ref.opaque_id)
                .unwrap_err()
                .code,
            "REF_REVOKED"
        );
    }

    #[test]
    fn rerender_fails_closed_when_previous_revoke_fails() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.register("render-1", "derived/render-1.png").unwrap();
        let old_ref = core.issue("render-0", "rev-0").unwrap();
        let next_ref = core.issue("render-1", "rev-1").unwrap();
        core.fail_revoke_for
            .lock()
            .unwrap()
            .replace("render-0".to_string());

        let mut current = HashMap::from([("page".to_string(), "render-0".to_string())]);
        let result = serde_json::json!({
            "page_id": "page",
            "artifact_id": "artifact",
            "revision_no": 2,
            "reports": [],
            "preview": {"resource_id": "render-1", "revision": "rev-1"},
            "preview_error": null,
        });

        let out = rotate_render_preview(&core, "page", result, &mut current).unwrap();

        // Contract §3: a failed revoke keeps the committed artifact but
        // fail-closes the new preview, keeps the old key retryable, and
        // rolls back the just-issued new grant.
        assert_eq!(out["preview"], serde_json::Value::Null);
        assert_eq!(
            out["preview_error"],
            serde_json::json!("PREVIEW_UNAVAILABLE")
        );
        assert_eq!(current.get("page"), Some(&"render-0".to_string()));
        assert_eq!(
            core.resolve(&old_ref.opaque_id).unwrap().resource_id,
            "render-0"
        );
        assert_eq!(
            core.resolve(&next_ref.opaque_id).unwrap_err().code,
            "REF_REVOKED"
        );
    }

    #[test]
    fn preview_rotation_short_circuits_equal_catalog_key() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        let old_ref = core.issue("render-0", "rev-0").unwrap();
        core.fail_revoke_for
            .lock()
            .unwrap()
            .replace("render-0".to_string());

        let mut current = HashMap::from([("page".to_string(), "render-0".to_string())]);
        let result = serde_json::json!({
            "page_id": "page",
            "artifact_id": "artifact",
            "revision_no": 2,
            "reports": [],
            "preview": {"resource_id": "render-0", "revision": "rev-1"},
            "preview_error": null,
        });

        let out = rotate_render_preview(&core, "page", result, &mut current).unwrap();

        // RC4-11: an equal-key rotation must not revoke the key it is about
        // to serve -- even a failing revoke stays unreached and the preview
        // stays intact.
        assert_eq!(out["preview_error"], serde_json::Value::Null);
        assert_eq!(current.get("page"), Some(&"render-0".to_string()));
        assert!(core.resolve(&old_ref.opaque_id).is_ok());
    }

    // ---- M2-DERIVED-GC-2: the rotation retire bit (design §2.2) ----------

    /// A successful rotation carries the retire bit for the PREVIOUS key
    /// only; the live new key is never marked.
    #[test]
    fn successful_rotation_retires_previous_key_only() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.register("render-1", "derived/render-1.png").unwrap();
        core.issue("render-0", "rev-0").unwrap();

        let mut current = HashMap::from([("page".to_string(), "render-0".to_string())]);
        let result = serde_json::json!({
            "page_id": "page",
            "artifact_id": "artifact",
            "revision_no": 2,
            "reports": [],
            "preview": {"resource_id": "render-1", "revision": "rev-1"},
            "preview_error": null,
        });

        let out = rotate_render_preview(&core, "page", result, &mut current).unwrap();
        assert_eq!(out["preview_error"], serde_json::Value::Null);
        assert_eq!(
            core.retire_calls.lock().unwrap().clone(),
            vec!["render-0".to_string()],
            "exactly the previous key rides the retire path"
        );
        assert_eq!(current.get("page"), Some(&"render-1".to_string()));
    }

    /// Same-key rotation: no revoke at all and therefore no retire mark.
    #[test]
    fn same_key_rotation_carries_no_retire_bit() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.issue("render-0", "rev-0").unwrap();

        let mut current = HashMap::from([("page".to_string(), "render-0".to_string())]);
        let result = serde_json::json!({
            "page_id": "page",
            "artifact_id": "artifact",
            "revision_no": 2,
            "reports": [],
            "preview": {"resource_id": "render-0", "revision": "rev-1"},
            "preview_error": null,
        });

        rotate_render_preview(&core, "page", result, &mut current).unwrap();
        assert!(
            core.retire_calls.lock().unwrap().is_empty(),
            "the live key must never be marked retired"
        );
    }

    /// Failed rotation: the fail-closed new-key revoke is a PLAIN revoke
    /// (no retire bit) and the previous key is not marked either.
    #[test]
    fn failed_rotation_marks_nothing() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.register("render-1", "derived/render-1.png").unwrap();
        core.issue("render-0", "rev-0").unwrap();
        core.fail_revoke_for
            .lock()
            .unwrap()
            .replace("render-0".to_string());

        let mut current = HashMap::from([("page".to_string(), "render-0".to_string())]);
        let result = serde_json::json!({
            "page_id": "page",
            "artifact_id": "artifact",
            "revision_no": 2,
            "reports": [],
            "preview": {"resource_id": "render-1", "revision": "rev-1"},
            "preview_error": null,
        });

        let out = rotate_render_preview(&core, "page", result, &mut current).unwrap();
        assert_eq!(
            out["preview_error"],
            serde_json::json!("PREVIEW_UNAVAILABLE")
        );
        assert!(
            core.retire_calls.lock().unwrap().is_empty(),
            "a failed rotation must not mark anything reclaimable"
        );
    }

    /// None-preview rotation: the previous key still gets its successful
    /// revoke (with the retire bit) before the map entry is dropped.
    #[test]
    fn none_preview_rotation_still_retires_previous_key() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.issue("render-0", "rev-0").unwrap();

        let mut current = HashMap::from([("page".to_string(), "render-0".to_string())]);
        let result = serde_json::json!({
            "page_id": "page",
            "artifact_id": "artifact",
            "revision_no": 2,
            "reports": [],
            "preview": serde_json::Value::Null,
            "preview_error": serde_json::json!("PREVIEW_UNAVAILABLE"),
        });

        let _out = rotate_render_preview(&core, "page", result, &mut current).unwrap();
        assert_eq!(current.get("page"), None);
        assert_eq!(
            core.retire_calls.lock().unwrap().clone(),
            vec!["render-0".to_string()],
            "the None-preview branch retires the dropped previous key"
        );
    }

    /// The WebView-facing plain revoke (revoke_resource_refs) never rides
    /// the retire path -- only the rotation method records there.
    #[test]
    fn plain_webview_revoke_does_not_touch_the_retire_path() {
        let core = MockCoreChannel::new();
        core.register("render-0", "derived/render-0.png").unwrap();
        core.issue("render-0", "rev-0").unwrap();

        core.revoke_resource("render-0").unwrap();

        assert!(core.retire_calls.lock().unwrap().is_empty());
    }

    // ---- M2-AC5: packaged-mode resolution (fail-closed spawn) -------------

    /// The explicit `M2RC1_PACKAGED=1` switch resolves the sidecar dir from
    /// the running exe's directory, even before any sidecar exe is checked.
    #[test]
    fn packaged_resolution_explicit_flag_wins() {
        let dir = tempfile::tempdir().unwrap();
        let resolved = resolve_packaged_sidecar_dir(Some("1"), None, Some(dir.path()));
        assert_eq!(
            resolved,
            Some(dir.path().join("resources").join("core-sidecar"))
        );
        // explicit flag wins over a dev src_root too
        let resolved =
            resolve_packaged_sidecar_dir(Some("1"), Some("G:/repo/src"), Some(dir.path()));
        assert_eq!(
            resolved,
            Some(dir.path().join("resources").join("core-sidecar"))
        );
    }

    /// A bare launch (no M2RC1_SRC_ROOT) is packaged ONLY when the
    /// install-relative sidecar exe actually exists; anything else falls
    /// back to the dev contract.
    #[test]
    fn packaged_resolution_bare_launch_requires_sidecar_exe() {
        let dir = tempfile::tempdir().unwrap();
        // no sidecar exe on disk -> not packaged (dev contract applies)
        let resolved = resolve_packaged_sidecar_dir(None, None, Some(dir.path()));
        assert_eq!(resolved, None);
        // with host_bridge.exe present -> packaged
        let sidecar = dir.path().join("resources").join("core-sidecar");
        std::fs::create_dir_all(&sidecar).unwrap();
        std::fs::write(sidecar.join("host_bridge.exe"), b"fake").unwrap();
        let resolved = resolve_packaged_sidecar_dir(None, None, Some(dir.path()));
        assert_eq!(resolved, Some(sidecar));
    }

    /// Dev environments (M2RC1_SRC_ROOT set, no explicit flag) never enter
    /// packaged mode, even when an installed layout is visible nearby.
    #[test]
    fn packaged_resolution_dev_env_stays_dev() {
        let dir = tempfile::tempdir().unwrap();
        let sidecar = dir.path().join("resources").join("core-sidecar");
        std::fs::create_dir_all(&sidecar).unwrap();
        std::fs::write(sidecar.join("host_bridge.exe"), b"fake").unwrap();
        let resolved = resolve_packaged_sidecar_dir(None, Some("G:/repo/src"), Some(dir.path()));
        assert_eq!(resolved, None);
        // no current exe at all -> never packaged
        let resolved = resolve_packaged_sidecar_dir(None, None, None);
        assert_eq!(resolved, None);
    }

    /// AC2 fail-closed: a missing packaged sidecar exe is the typed
    /// PACKAGED_SIDECAR_MISSING error — no system-python fallback is even
    /// attempted (the error surfaces before any Command is built).
    #[test]
    fn packaged_spawn_missing_sidecar_fails_closed() {
        let dir = tempfile::tempdir().unwrap();
        let missing = dir.path().join("host_bridge.exe");
        let error = match StdioCoreChannel::spawn_packaged(
            &missing,
            &dir.path().join("d"),
            &dir.path().join("m"),
            &dir.path().join("c.sqlite"),
        ) {
            Err(error) => error,
            Ok(_) => panic!("packaged spawn must fail closed for a missing sidecar exe"),
        };
        assert_eq!(error.code, "CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING");
    }
}
