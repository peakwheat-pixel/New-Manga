//! Production Library & Core Lifecycle Bridge (M2-IPC1).
//!
//! Connects the Tauri host to the Python Core service sidecar (`bootstrap.core_service`)
//! over stdio JSON-lines with Core protocol 2.3 envelopes.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::{HashMap, HashSet};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::mpsc::SyncSender;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ProtocolVersion {
    pub major: u32,
    pub minor: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct PingResult {
    pub status: String,
    pub protocol_version: ProtocolVersion,
    pub capabilities: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct BookSummary {
    pub book_id: String,
    pub title: String,
    pub original_title: String,
    pub is_favorite: bool,
    pub is_archived: bool,
    /// M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN (frozen None channel): `None`
    /// serializes as JSON `null` = unknown/missing data; a counted value
    /// stays a number (a KNOWN 0 must stay distinguishable from `null`).
    pub page_count: Option<u32>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ChapterNavSummary {
    pub chapter_id: String,
    pub title: String,
    pub chapter_number: String,
    pub sort_order: i64,
}

/// EXPORT-IPC-1 (contract rev 2.5 §5.8): Safe WebView projection of export output.
/// Whitelisted reconstruction: output_path is strictly excluded.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ExportProgressOutputView {
    pub format: String,
    pub sha256: Option<String>,
}

/// EXPORT-IPC-1 (contract rev 2.5 §5.8): Safe WebView projection of export lineage.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ExportPageLineageView {
    pub page_id: String,
    pub order: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_artifact_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_artifact_revision_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rendered_from_revision_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub current_source_revision_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_run_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stale: Option<bool>,
}

/// EXPORT-IPC-1 (contract rev 2.5 §5.8): Safe WebView projection of export progress snapshot.
/// Strictly excludes output_path and any OS path representation.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ExportProgressSnapshotView {
    pub export_id: String,
    pub status: String,
    pub completed_pages: u64,
    pub total_pages: u64,
    pub current_page_id: Option<String>,
    pub accepted_at: String,
    pub completed_at: Option<String>,
    pub output: Option<ExportProgressOutputView>,
    pub lineage: Vec<ExportPageLineageView>,
    pub error_code: Option<String>,
}

/// EXPORT-IPC-1 (contract rev 2.5 §5.8): Safe WebView projection of export history entry.
/// Whitelisted reconstruction: output_path is strictly excluded.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ExportHistoryEntryView {
    pub export_id: String,
    pub book_id: String,
    pub chapter_ids: Vec<String>,
    pub ordered_page_ids: Vec<String>,
    pub format: String,
    pub format_options: serde_json::Value,
    pub created_at: String,
    pub completed_at: Option<String>,
    pub status: String,
    pub sha256: Option<String>,
    pub lineage: Vec<ExportPageLineageView>,
}

/// EXPORT-IPC-1 (contract rev 2.5 §5.8): History query response view.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ExportHistoryResponseView {
    pub exports: Vec<ExportHistoryEntryView>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct LibraryError {
    pub code: String,
    pub category: String,
    pub retryable: bool,
    pub message: Option<String>,
    pub details: Option<Value>,
}

impl LibraryError {
    pub fn new(code: &str, category: &str, retryable: bool, message: Option<&str>) -> Self {
        Self {
            code: code.to_string(),
            category: category.to_string(),
            retryable,
            message: message.map(ToString::to_string),
            details: None,
        }
    }

    pub fn unavailable(msg: &str) -> Self {
        Self::new("CORE_UNAVAILABLE", "unavailable", true, Some(msg))
    }

    pub fn malformed(msg: &str) -> Self {
        Self::new("PROTOCOL_MALFORMED", "validation", false, Some(msg))
    }
}

impl std::fmt::Display for LibraryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}: {} (category={}, retryable={})",
            self.code,
            self.message.as_deref().unwrap_or("no message"),
            self.category,
            self.retryable
        )
    }
}

impl std::error::Error for LibraryError {}

pub fn decode_response(line: &str) -> Result<serde_json::Value, LibraryError> {
    let value: serde_json::Value =
        serde_json::from_str(line).map_err(|e| LibraryError::malformed(&e.to_string()))?;

    if let Some(err) = value.get("error").filter(|v| !v.is_null()) {
        let code = err
            .get("code")
            .and_then(|c| c.as_str())
            .unwrap_or("UNKNOWN")
            .to_string();
        let category = err
            .get("category")
            .and_then(|c| c.as_str())
            .unwrap_or("unknown")
            .to_string();
        let retryable = err
            .get("retryable")
            .and_then(|r| r.as_bool())
            .unwrap_or(false);
        let message = err
            .get("message")
            .and_then(|m| m.as_str())
            .map(ToString::to_string);
        return Err(LibraryError {
            code,
            category,
            retryable,
            message,
            details: err.get("details").cloned(),
        });
    }

    Ok(value
        .get("result")
        .cloned()
        .unwrap_or(serde_json::Value::Null))
}

pub fn project_export_lineage(val: &Value) -> Result<ExportPageLineageView, LibraryError> {
    let page_id = val
        .get("page_id")
        .and_then(Value::as_str)
        .ok_or_else(|| LibraryError::malformed("missing page_id in lineage"))?
        .to_string();
    let order = val
        .get("order")
        .and_then(Value::as_i64)
        .ok_or_else(|| LibraryError::malformed("missing order in lineage"))?;
    let source_artifact_id = val
        .get("source_artifact_id")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let source_artifact_revision_id = val
        .get("source_artifact_revision_id")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let source_sha256 = val
        .get("source_sha256")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let rendered_from_revision_id = val
        .get("rendered_from_revision_id")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let current_source_revision_id = val
        .get("current_source_revision_id")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let source_run_id = val
        .get("source_run_id")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let stale = val.get("stale").and_then(Value::as_bool);

    Ok(ExportPageLineageView {
        page_id,
        order,
        source_artifact_id,
        source_artifact_revision_id,
        source_sha256,
        rendered_from_revision_id,
        current_source_revision_id,
        source_run_id,
        stale,
    })
}

pub fn project_export_snapshot(val: Value) -> Result<ExportProgressSnapshotView, LibraryError> {
    let export_id = val
        .get("export_id")
        .and_then(Value::as_str)
        .ok_or_else(|| LibraryError::malformed("missing export_id in snapshot"))?
        .to_string();
    let status = val
        .get("status")
        .and_then(Value::as_str)
        .ok_or_else(|| LibraryError::malformed("missing status in snapshot"))?
        .to_string();
    let completed_pages = val
        .get("completed_pages")
        .and_then(Value::as_u64)
        .unwrap_or(0);
    let total_pages = val.get("total_pages").and_then(Value::as_u64).unwrap_or(0);
    let current_page_id = val
        .get("current_page_id")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let accepted_at = val
        .get("accepted_at")
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string();
    let completed_at = val
        .get("completed_at")
        .and_then(Value::as_str)
        .map(ToString::to_string);
    let output = match val.get("output") {
        Some(Value::Object(o)) => {
            let format = o
                .get("format")
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_string();
            let sha256 = o
                .get("sha256")
                .and_then(Value::as_str)
                .map(ToString::to_string);
            Some(ExportProgressOutputView { format, sha256 })
        }
        _ => None,
    };
    let lineage = match val.get("lineage") {
        Some(Value::Array(arr)) => {
            let mut items = Vec::with_capacity(arr.len());
            for l in arr {
                items.push(project_export_lineage(l)?);
            }
            items
        }
        _ => Vec::new(),
    };
    let error_code = val
        .get("error_code")
        .and_then(Value::as_str)
        .map(ToString::to_string);

    Ok(ExportProgressSnapshotView {
        export_id,
        status,
        completed_pages,
        total_pages,
        current_page_id,
        accepted_at,
        completed_at,
        output,
        lineage,
        error_code,
    })
}

pub fn project_export_history(val: Value) -> Result<ExportHistoryResponseView, LibraryError> {
    let exports_array = match val.get("exports") {
        Some(Value::Array(arr)) => arr,
        Some(Value::Null) | None => {
            return Ok(ExportHistoryResponseView {
                exports: Vec::new(),
            })
        }
        _ => return Err(LibraryError::malformed("exports field must be an array")),
    };
    let mut exports = Vec::with_capacity(exports_array.len());
    for item in exports_array {
        let export_id = item
            .get("export_id")
            .and_then(Value::as_str)
            .ok_or_else(|| LibraryError::malformed("missing export_id in history entry"))?
            .to_string();
        let book_id = item
            .get("book_id")
            .and_then(Value::as_str)
            .ok_or_else(|| LibraryError::malformed("missing book_id in history entry"))?
            .to_string();
        let chapter_ids = item
            .get("chapter_ids")
            .and_then(Value::as_array)
            .map(|arr| {
                arr.iter()
                    .filter_map(Value::as_str)
                    .map(ToString::to_string)
                    .collect()
            })
            .unwrap_or_default();
        let ordered_page_ids = item
            .get("ordered_page_ids")
            .and_then(Value::as_array)
            .map(|arr| {
                arr.iter()
                    .filter_map(Value::as_str)
                    .map(ToString::to_string)
                    .collect()
            })
            .unwrap_or_default();
        let format = item
            .get("format")
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        let format_options = item
            .get("format_options")
            .cloned()
            .unwrap_or_else(|| Value::Object(Default::default()));
        let created_at = item
            .get("created_at")
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        let completed_at = item
            .get("completed_at")
            .and_then(Value::as_str)
            .map(ToString::to_string);
        let status = item
            .get("status")
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        let sha256 = item
            .get("sha256")
            .and_then(Value::as_str)
            .map(ToString::to_string);
        let lineage = match item.get("lineage") {
            Some(Value::Array(arr)) => {
                let mut items = Vec::with_capacity(arr.len());
                for l in arr {
                    items.push(project_export_lineage(l)?);
                }
                items
            }
            _ => Vec::new(),
        };
        exports.push(ExportHistoryEntryView {
            export_id,
            book_id,
            chapter_ids,
            ordered_page_ids,
            format,
            format_options,
            created_at,
            completed_at,
            status,
            sha256,
            lineage,
        });
    }
    Ok(ExportHistoryResponseView { exports })
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum P15SettingsCommand {
    ProviderProfilesList,
    ProviderProfilesCreate,
    ProviderProfilesUpdate,
    ProviderProfilesDelete,
    ProviderBindingsSet,
    ProviderBindingsClear,
    ProviderBindingsResolve,
    ProviderRunSnapshotGet,
    NetworkProfilesList,
    NetworkProfilesCreate,
    NetworkProfilesUpdate,
    NetworkProfilesDelete,
    NetworkProfilesTest,
    NetworkProfileDefaultSet,
    NetworkProfileDefaultClear,
    NetworkProfileResolve,
    ResolveOverrides,
    BindProfileCredential,
    ClearProfileCredential,
}

impl P15SettingsCommand {
    fn core_name(self) -> &'static str {
        match self {
            Self::ProviderProfilesList => "settings_provider_profiles_list",
            Self::ProviderProfilesCreate => "settings_provider_profiles_create",
            Self::ProviderProfilesUpdate => "settings_provider_profiles_update",
            Self::ProviderProfilesDelete => "settings_provider_profiles_delete",
            Self::ProviderBindingsSet => "settings_provider_bindings_set",
            Self::ProviderBindingsClear => "settings_provider_bindings_clear",
            Self::ProviderBindingsResolve => "settings_provider_bindings_resolve",
            Self::ProviderRunSnapshotGet => "settings_provider_run_snapshot_get",
            Self::NetworkProfilesList => "settings_network_profiles_list",
            Self::NetworkProfilesCreate => "settings_network_profiles_create",
            Self::NetworkProfilesUpdate => "settings_network_profiles_update",
            Self::NetworkProfilesDelete => "settings_network_profiles_delete",
            Self::NetworkProfilesTest => "settings_network_profiles_test",
            Self::NetworkProfileDefaultSet => "settings_network_profile_default_set",
            Self::NetworkProfileDefaultClear => "settings_network_profile_default_clear",
            Self::NetworkProfileResolve => "settings_network_profile_resolve",
            Self::ResolveOverrides => "settings_resolve_overrides",
            Self::BindProfileCredential => P15_BIND_PROFILE_CREDENTIAL,
            Self::ClearProfileCredential => P15_CLEAR_PROFILE_CREDENTIAL,
        }
    }
}

const P15_BIND_PROFILE_CREDENTIAL: &str = "BindProfileCredential";
const P15_CLEAR_PROFILE_CREDENTIAL: &str = "ClearProfileCredential";
pub const P15_HOST_ONLY_COMMANDS: [&str; 2] =
    [P15_BIND_PROFILE_CREDENTIAL, P15_CLEAR_PROFILE_CREDENTIAL];

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
#[allow(dead_code)]
pub enum P15CredentialTarget {
    ProviderApi { profile_id: String },
    ProxyAuth { network_profile_id: String },
}

pub type StatusEmitter = Arc<dyn Fn(&str, &str) + Send + Sync>;

pub trait LibraryChannel: Send + Sync {
    fn ping(&self) -> Result<PingResult, LibraryError>;
    fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError>;
    fn create_book(&self, _title: &str) -> Result<BookSummary, LibraryError> {
        Err(LibraryError::unavailable("Create channel is unavailable"))
    }
    fn create_chapter(
        &self,
        _book_id: &str,
        _title: &str,
        _chapter_number: Option<&str>,
    ) -> Result<ChapterNavSummary, LibraryError> {
        Err(LibraryError::unavailable("Create channel is unavailable"))
    }
    /// M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): read the pipeline
    /// settings projection — `{}` (full) or `{"section": name}` (one
    /// section, JSON `null` when unset). Returns the raw result JSON (the
    /// `{"settings": ...}` projection); the host never interprets keys.
    fn get_settings(&self, section: Option<&str>) -> Result<serde_json::Value, LibraryError>;
    /// M2-SETTINGS-IPC-CHANNEL: upsert one section via the Core's
    /// `settings.update_section` (`settings.update_section`); value-domain
    /// validation (sfx.policy) lives Core-side BEFORE persistence — the
    /// typed rejection (INVALID_REQUEST) propagates as `LibraryError.code`.
    fn update_settings_section(
        &self,
        section: &str,
        values: &serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError>;
    fn p15_settings(
        &self,
        _command: P15SettingsCommand,
        _payload: serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable(
            "P15 settings channel is unavailable",
        ))
    }
    fn bind_profile_credential(
        &self,
        target: P15CredentialTarget,
        credential_ref: &str,
    ) -> Result<(), LibraryError> {
        let target = serde_json::to_value(target)
            .map_err(|_| LibraryError::unavailable("P15 credential target is invalid"))?;
        let result = self.p15_settings(
            P15SettingsCommand::BindProfileCredential,
            serde_json::json!({ "target": target, "credential_ref": credential_ref }),
        )?;
        if result == serde_json::json!({ "state": "configured" }) {
            Ok(())
        } else {
            Err(LibraryError::new(
                "SETTINGS_UNAVAILABLE",
                "unavailable",
                true,
                None,
            ))
        }
    }
    fn clear_profile_credential(&self, target: P15CredentialTarget) -> Result<(), LibraryError> {
        let target = serde_json::to_value(target)
            .map_err(|_| LibraryError::unavailable("P15 credential target is invalid"))?;
        let result = self.p15_settings(
            P15SettingsCommand::ClearProfileCredential,
            serde_json::json!({ "target": target }),
        )?;
        if result == serde_json::json!({ "state": "missing" }) {
            Ok(())
        } else {
            Err(LibraryError::new(
                "SETTINGS_UNAVAILABLE",
                "unavailable",
                true,
                None,
            ))
        }
    }
    /// M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): retype one region via
    /// the Core's `set_region_type`. All domain authority (the RegionType
    /// six-value closed set, the EV-8 policy re-snapshot, the optimistic
    /// `expected_revision` guard) lives Core-side BEFORE persistence; the
    /// typed rejection (INVALID_REQUEST / INPUT_REVISION_CHANGED /
    /// TARGET_NOT_FOUND) propagates as `LibraryError.code` and the result
    /// is the post-retype effective state
    /// (`{region_id, revision_no, region_type, sfx_policy}`) as raw JSON.
    fn set_region_type(
        &self,
        region_id: &str,
        new_region_type: &str,
        expected_revision: Option<i64>,
    ) -> Result<serde_json::Value, LibraryError>;
    /// M2-REGION-RETYPE-CORE: the RegionListSummary read channel via the
    /// Core's `list_regions` — the raw `{"regions": [...]}` projection
    /// passes through; a page with no rows is an empty list, not an error.
    fn list_regions(&self, page_id: &str) -> Result<serde_json::Value, LibraryError>;
    /// RC-4 read-only revision history projection.
    fn list_region_revisions(&self, region_id: &str) -> Result<serde_json::Value, LibraryError>;
    /// RC-4 explicit restore creates a new revision under the Core's
    /// transaction-time current-revision guard.
    fn restore_region_revision(
        &self,
        region_id: &str,
        revision_no: i64,
        expected_revision: i64,
    ) -> Result<serde_json::Value, LibraryError>;
    /// RC-4 synchronous render and resource-channel preview projection.
    fn rerender_page(&self, page_id: &str) -> Result<serde_json::Value, LibraryError>;
    /// M2-PAGE-RESOURCE-RESOLVE-1 (contract rev 1.7 §5): resolve one page's
    /// immutable managed original to its servable resource catalog key
    /// (`{resource_id, revision}`); Core publishes the first resolve into
    /// the derived read-only root and later resolves return the same key.
    /// PAGE_NOT_FOUND (unknown page / no managed original) propagates as
    /// `LibraryError.code`.
    fn resolve_page_resource(&self, page_id: &str) -> Result<serde_json::Value, LibraryError>;

    /// M2-PAGE-NAV-PROJECTION-1 (contract rev 1.8 §5): the read-only page
    /// navigation projections -- one book's chapters / one chapter's pages,
    /// both in the user's current sort_order. Unknown parent ids yield
    /// EMPTY lists (fail-soft, P3-4 precedent).
    fn list_chapters(&self, book_id: &str) -> Result<serde_json::Value, LibraryError>;

    fn list_chapter_pages(&self, chapter_id: &str) -> Result<serde_json::Value, LibraryError>;

    /// P16-C1 (contract rev 2.1 §5/§6.3): pass the reader projection through
    /// unchanged; the page resource refs remain opaque to the host.
    fn get_reader_projection(
        &self,
        _chapter_id: &str,
        _mode: &str,
        _start_position: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Reader channel is unavailable"))
    }

    /// P16-C1: save only the caller's progress values. Optional values are
    /// omitted when absent so an elapsed-time interval is never replayed.
    fn save_reading_progress(
        &self,
        _chapter_id: &str,
        _mode: &str,
        _page_id: &str,
        _scroll_offset_y: Option<f64>,
        _elapsed_seconds_delta: Option<f64>,
    ) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Reader channel is unavailable"))
    }

    fn import_from_path(
        &self,
        path: &Path,
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        let _ = (path, source_kind, chapter_id, duplicate_policy);
        Err(LibraryError::unavailable("Host issuer is unavailable"))
    }
    fn import_from_paths(
        &self,
        paths: &[PathBuf],
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        let _ = (paths, source_kind, chapter_id, duplicate_policy);
        Err(LibraryError::unavailable("Host issuer is unavailable"))
    }

    fn start_export_to_path(
        &self,
        path: &Path,
        request: Value,
    ) -> Result<crate::host_issuer::ExportSummary, LibraryError> {
        let _ = (path, request);
        Err(LibraryError::unavailable("Host issuer is unavailable"))
    }

    /// P13-C1 (contract rev 2.0 section 5.5): the frozen Run command surface.
    /// The host is pure transport here -- every domain rule (the
    /// PipelineCommand closed set, PipelineScope resolution, idempotency
    /// semantics, the control-action state matrix and every DTO/projection
    /// shape) lives Core-side BEFORE persistence, and typed rejections
    /// (INVALID_REQUEST / IDEMPOTENCY_KEY_REUSED / TARGET_NOT_FOUND / ...)
    /// propagate as `LibraryError.code`. The wire command names below are the
    /// PascalCase names frozen in section 5.5 (`StartRun`, ...), NOT the
    /// snake_case names used by the older command families.
    ///
    /// The defaults are fail-closed so that test doubles and wrappers keep
    /// compiling; the production channel overrides all six.
    fn start_run(
        &self,
        _command: &str,
        _scope: &serde_json::Value,
        _overrides: Option<&serde_json::Value>,
        _idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Run channel is unavailable"))
    }

    fn control_run(
        &self,
        _run_id: &str,
        _action: &str,
        _idempotency_key: Option<&str>,
    ) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Run channel is unavailable"))
    }

    fn resume_blocked_run(&self, _run_id: &str) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Run channel is unavailable"))
    }

    fn get_run_snapshot(&self, _run_id: &str) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Run channel is unavailable"))
    }

    fn get_task_projection(&self, _run_id: &str) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Run channel is unavailable"))
    }

    fn retry_failed_targets(
        &self,
        _run_id: &str,
        _idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        Err(LibraryError::unavailable("Run channel is unavailable"))
    }
    /// Returns a current-session export's output directory using trusted Core history.
    fn export_output_directory(&self, export_id: &str) -> Result<PathBuf, LibraryError> {
        let _ = export_id;
        Err(LibraryError::new(
            "EXPORT_NOT_FOUND",
            "not_found",
            false,
            None,
        ))
    }

    /// EVENTS-FWD-1 (rev 2.4 §6.4): Register an event sink for background
    /// core events forwarded to WebView. Default is a no-op.
    fn set_event_sink(&self, _sink: EventSink) {}

    /// EXPORT-IPC-1 (contract rev 2.5 §5.8): Export control and query surface.
    /// Returns whitelisted safe views without output_path or file references.
    fn cancel_export(&self, _export_id: &str) -> Result<ExportProgressSnapshotView, LibraryError> {
        Err(LibraryError::unavailable("Export channel is unavailable"))
    }

    fn get_export_snapshot(
        &self,
        _export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
        Err(LibraryError::unavailable("Export channel is unavailable"))
    }

    fn get_export_history(&self) -> Result<ExportHistoryResponseView, LibraryError> {
        Err(LibraryError::unavailable("Export channel is unavailable"))
    }

    /// P20-ISOLATION-1: Register a lifecycle status emitter for sidecar health events.
    fn set_status_emitter(&self, _emitter: StatusEmitter) {}

    /// P20-ISOLATION-1: Trigger supervisor recovery if the channel is currently unhealthy or disconnected.
    fn trigger_restart(&self) {}

    /// P20-ISOLATION-1: Query whether the sidecar channel is in an unhealthy, restarting, or fatal state.
    fn is_unhealthy(&self) -> bool {
        false
    }
}

fn reader_progress_payload(
    chapter_id: &str,
    mode: &str,
    page_id: &str,
    scroll_offset_y: Option<f64>,
    elapsed_seconds_delta: Option<f64>,
) -> Value {
    let mut payload = serde_json::json!({
        "chapter_id": chapter_id,
        "mode": mode,
        "page_id": page_id,
    });
    if let Some(offset) = scroll_offset_y {
        payload["scroll_offset_y"] = serde_json::json!(offset);
    }
    if let Some(elapsed) = elapsed_seconds_delta {
        payload["elapsed_seconds_delta"] = serde_json::json!(elapsed);
    }
    payload
}

pub type EventSink = Arc<dyn Fn(&str, Value) + Send + Sync>;

pub const FORWARDED_CORE_EVENTS: &[(&str, &str)] = &[
    ("TaskFailed", "core:TaskFailed"),
    ("RunPaused", "core:RunPaused"),
    ("RunCompleted", "core:RunCompleted"),
    ("CurrentPageStepChanged", "core:CurrentPageStepChanged"),
    ("ExportProgressChanged", "core:ExportProgressChanged"),
    ("ReadingProgressChanged", "core:ReadingProgressChanged"),
];

/// EVENTS-FWD-1 (contract rev 2.4 §6.4): Project a Core wire event to its
/// safe WebView representation. Only the six frozen event types are accepted.
/// Payloads are strictly sanitized to exclude any local filesystem paths,
/// references, credentials, or binary bytes (M2-C1 §10.2 / §10.3 / §10.4).
pub fn project_forwarded_event(
    event_type: &str,
    raw_payload: &Value,
) -> Option<(&'static str, Value)> {
    let (_, tauri_event_name) = FORWARDED_CORE_EVENTS
        .iter()
        .find(|(core_name, _)| *core_name == event_type)?;

    let projected_payload = match event_type {
        "TaskFailed" => {
            let mut obj = serde_json::Map::new();
            if let Some(run_id) = raw_payload.get("run_id").and_then(Value::as_str) {
                obj.insert("run_id".into(), Value::String(run_id.into()));
            } else {
                return None;
            }
            if let Some(task_id) = raw_payload.get("task_id").and_then(Value::as_str) {
                obj.insert("task_id".into(), Value::String(task_id.into()));
            } else {
                return None;
            }
            if let Some(page_id) = raw_payload.get("page_id") {
                if !page_id.is_null() {
                    if let Some(pid) = page_id.as_str() {
                        obj.insert("page_id".into(), Value::String(pid.into()));
                    }
                } else {
                    obj.insert("page_id".into(), Value::Null);
                }
            }
            if let Some(error_code) = raw_payload.get("error_code") {
                if !error_code.is_null() {
                    if let Some(ec) = error_code.as_str() {
                        obj.insert("error_code".into(), Value::String(ec.into()));
                    }
                } else {
                    obj.insert("error_code".into(), Value::Null);
                }
            }
            Value::Object(obj)
        }
        "RunPaused" => {
            let run_id = raw_payload.get("run_id").and_then(Value::as_str)?;
            let status = raw_payload.get("status").and_then(Value::as_str)?;
            if status != "paused" {
                return None;
            }
            serde_json::json!({
                "run_id": run_id,
                "status": "paused"
            })
        }
        "RunCompleted" => {
            let run_id = raw_payload.get("run_id").and_then(Value::as_str)?;
            let status = raw_payload.get("status").and_then(Value::as_str)?;
            if status != "completed" && status != "completed_with_failures" {
                return None;
            }
            serde_json::json!({
                "run_id": run_id,
                "status": status
            })
        }
        "CurrentPageStepChanged" => {
            let run_id = raw_payload.get("run_id").and_then(Value::as_str)?;
            let current_step_type = raw_payload
                .get("current_step_type")
                .and_then(Value::as_str)?;
            let page_id = raw_payload.get("current_page_id").and_then(Value::as_str);
            serde_json::json!({
                "run_id": run_id,
                "current_page_id": page_id,
                "current_step_type": current_step_type
            })
        }
        "ExportProgressChanged" => {
            let export_id = raw_payload.get("export_id").and_then(Value::as_str)?;
            let status = raw_payload.get("status").and_then(Value::as_str)?;
            let completed_pages = raw_payload.get("completed_pages").and_then(Value::as_u64)?;
            let total_pages = raw_payload.get("total_pages").and_then(Value::as_u64)?;
            serde_json::json!({
                "export_id": export_id,
                "status": status,
                "completed_pages": completed_pages,
                "total_pages": total_pages
            })
        }
        "ReadingProgressChanged" => {
            let book_id = raw_payload.get("book_id").and_then(Value::as_str)?;
            let chapter_id = raw_payload.get("chapter_id").and_then(Value::as_str)?;
            let mode = raw_payload.get("mode").and_then(Value::as_str)?;
            if mode != "original" && mode != "translated" {
                return None;
            }
            serde_json::json!({
                "book_id": book_id,
                "chapter_id": chapter_id,
                "mode": mode
            })
        }
        _ => return None,
    };

    Some((*tauri_event_name, projected_payload))
}

pub(crate) fn dispatch_stdout_line(
    line: &str,
    event_sink: &Mutex<Option<EventSink>>,
    pending_responses: &Mutex<HashMap<String, SyncSender<Result<String, LibraryError>>>>,
) {
    let trimmed = line.trim_end();
    if trimmed.is_empty() {
        return;
    }
    if let Ok(val) = serde_json::from_str::<Value>(trimmed) {
        // 1. Check whether this line is a typed event envelope (event_type present)
        if let Some(event_type) = val.get("event_type").and_then(Value::as_str) {
            if let Some(raw_payload) = val.get("payload") {
                if let Some((tauri_name, projected)) =
                    project_forwarded_event(event_type, raw_payload)
                {
                    if let Ok(sink_lock) = event_sink.lock() {
                        if let Some(sink) = sink_lock.as_ref() {
                            sink(tauri_name, projected);
                        }
                    }
                }
            }
            return;
        }

        // 2. Check whether this line is an application or host-control response (request_id present)
        if let Some(req_id) = val.get("request_id").and_then(Value::as_str) {
            let mut lock = pending_responses.lock().unwrap();
            if let Some(sender) = lock.remove(req_id) {
                let _ = sender.send(Ok(line.to_string()));
                return;
            }
        }
    }

    // Fallback: if not parsed as Event or registered response, route to the single pending caller
    let mut lock = pending_responses.lock().unwrap();
    if lock.len() == 1 {
        let single_key = lock.keys().next().cloned().unwrap();
        if let Some(sender) = lock.remove(&single_key) {
            let _ = sender.send(Ok(line.to_string()));
        }
    }
}

/// The command argv pinned for spawning the production Core service.
pub fn spawn_args() -> Vec<&'static str> {
    vec!["-m", "bootstrap.core_service"]
}

pub(crate) enum WriterCommand {
    Write(Vec<u8>, std::sync::mpsc::SyncSender<std::io::Result<()>>),
    Shutdown,
}

/// Bounded mutex acquisition with lock poisoning recovery.
/// Eliminates infinite mutex blocking while guaranteeing that poisoned locks
/// (e.g. child process handle) are recovered and not silently skipped.
pub(crate) fn lock_timeout_recover<T>(
    mutex: &std::sync::Mutex<T>,
    timeout: Duration,
) -> Option<std::sync::MutexGuard<'_, T>> {
    let start = Instant::now();
    let poll = Duration::from_millis(5);
    loop {
        match mutex.try_lock() {
            Ok(guard) => return Some(guard),
            Err(std::sync::TryLockError::Poisoned(p)) => return Some(p.into_inner()),
            Err(std::sync::TryLockError::WouldBlock) => {
                if start.elapsed() >= timeout {
                    return None;
                }
                std::thread::sleep(poll);
            }
        }
    }
}

pub struct StdioLibraryChannel {
    pub(crate) child: Mutex<Child>,
    writer_tx: std::sync::mpsc::Sender<WriterCommand>,
    writer_join_handle: Mutex<Option<std::thread::JoinHandle<()>>>,
    transaction_lock: Mutex<()>,
    request_id_gen: AtomicU64,
    host_session: Mutex<Option<HostSession>>,
    session_export_ids: Mutex<HashSet<String>>,
    event_sink: Arc<Mutex<Option<EventSink>>>,
    pending_responses: Arc<Mutex<HashMap<String, SyncSender<Result<String, LibraryError>>>>>,
    is_down: Arc<AtomicBool>,
    on_down: Arc<Mutex<Option<Arc<dyn Fn() + Send + Sync>>>>,
    reader_join_handle: Mutex<Option<std::thread::JoinHandle<()>>>,
    shutdown_executed: AtomicBool,
}

struct HostSession {
    host_session_id: String,
    credential: String,
    core_session_id: String,
    signing_key: [u8; 32],
}

impl Drop for HostSession {
    fn drop(&mut self) {
        self.credential.clear();
        self.signing_key.fill(0);
    }
}

fn build_host_control_envelope(
    request_id: &str,
    command: &str,
    payload: Value,
    session: Option<&HostSession>,
) -> Value {
    let mut request = serde_json::json!({
        "protocol": "new-manga.core",
        "version": { "major": 2, "minor": 3 },
        "request_id": request_id,
        "channel": "host-control",
        "command": command,
        "payload": payload,
    });
    if let Some(session) = session {
        request["core_session_id"] = serde_json::json!(session.core_session_id);
        request["host_session_id"] = serde_json::json!(session.host_session_id);
        request["host_session_credential"] = serde_json::json!(session.credential);
    }
    request
}

fn build_application_envelope(request_id: &str, command: &str, payload: Value) -> Value {
    build_application_envelope_at_minor(request_id, command, payload, 3)
}

fn build_application_envelope_at_minor(
    request_id: &str,
    command: &str,
    payload: Value,
    minor: u32,
) -> Value {
    serde_json::json!({
        "protocol": "new-manga.core",
        "version": { "major": 2, "minor": minor },
        "request_id": request_id,
        "command": command,
        "payload": payload,
    })
}

fn parse_created_book(value: Value) -> Result<BookSummary, LibraryError> {
    serde_json::from_value(value).map_err(|error| {
        LibraryError::malformed(&format!("Failed to parse CreateBook result: {error}"))
    })
}

fn parse_created_chapter(value: Value) -> Result<ChapterNavSummary, LibraryError> {
    serde_json::from_value(value).map_err(|error| {
        LibraryError::malformed(&format!("Failed to parse CreateChapter result: {error}"))
    })
}

impl StdioLibraryChannel {
    pub fn spawn(
        python_exe: &str,
        src_root: &std::path::Path,
        data_root: Option<&std::path::Path>,
    ) -> Result<Self, LibraryError> {
        Self::spawn_with_resource_roots(python_exe, src_root, data_root, None, None)
    }

    /// RC-4 production spawn. The optional roots bind Core preview writes to
    /// the same catalog and derived directory used by the resource bridge;
    /// the historical spawn signature remains available to existing callers.
    pub fn spawn_with_resource_roots(
        python_exe: &str,
        src_root: &std::path::Path,
        data_root: Option<&std::path::Path>,
        derived_root: Option<&std::path::Path>,
        catalog_db: Option<&std::path::Path>,
    ) -> Result<Self, LibraryError> {
        // M2-RG1 AC2: Command-construction section only — CREATE_NO_WINDOW on
        // Windows; argv/cwd/env/stdio semantics unchanged.
        let mut cmd = Command::new(python_exe);
        cmd.args(spawn_args())
            .current_dir(src_root)
            .env("PYTHONPATH", src_root)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit());

        if let Some(root) = data_root {
            cmd.env("NEWMANGA_DATA_ROOT", root);
        }
        if let Some(root) = derived_root {
            cmd.env("M2RC1_DERIVED_ROOT", root);
        }
        if let Some(path) = catalog_db {
            cmd.env("M2RC2_CATALOG_DB", path);
        }

        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x0800_0000;
            cmd.creation_flags(CREATE_NO_WINDOW);
        }

        let child = cmd
            .spawn()
            .map_err(|e| LibraryError::unavailable(&format!("Failed to spawn Core: {e}")))?;

        Self::adopt_child(child)
    }

    fn adopt_child(mut child: Child) -> Result<Self, LibraryError> {
        let stdin = child
            .stdin
            .take()
            .ok_or_else(|| LibraryError::unavailable("Failed to open child stdin"))?;
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| LibraryError::unavailable("Failed to open child stdout"))?;

        let pending_responses: Arc<
            Mutex<HashMap<String, SyncSender<Result<String, LibraryError>>>>,
        > = Arc::new(Mutex::new(HashMap::new()));
        let event_sink: Arc<Mutex<Option<EventSink>>> = Arc::new(Mutex::new(None));
        let is_down = Arc::new(AtomicBool::new(false));
        let on_down: Arc<Mutex<Option<Arc<dyn Fn() + Send + Sync>>>> = Arc::new(Mutex::new(None));

        let pending_clone = Arc::clone(&pending_responses);
        let sink_clone = Arc::clone(&event_sink);
        let is_down_clone = Arc::clone(&is_down);
        let on_down_clone = Arc::clone(&on_down);

        let reader_thread = std::thread::Builder::new()
            .name("stdio-library-reader".to_string())
            .spawn(move || {
                let mut reader = BufReader::new(stdout);
                loop {
                    let mut line = String::new();
                    match reader.read_line(&mut line) {
                        Ok(0) => {
                            is_down_clone.store(true, Ordering::SeqCst);
                            let mut lock = pending_clone.lock().unwrap();
                            for (_req_id, sender) in lock.drain() {
                                let _ = sender.send(Err(LibraryError::unavailable(
                                    "Core stdout closed (EOF)",
                                )));
                            }
                            if let Ok(guard) = on_down_clone.lock() {
                                if let Some(ref cb) = *guard {
                                    cb();
                                }
                            }
                            break;
                        }
                        Ok(_) => {
                            dispatch_stdout_line(&line, &sink_clone, &pending_clone);
                        }
                        Err(err) => {
                            is_down_clone.store(true, Ordering::SeqCst);
                            let mut lock = pending_clone.lock().unwrap();
                            for (_req_id, sender) in lock.drain() {
                                let _ = sender.send(Err(LibraryError::unavailable(&format!(
                                    "stdout read failed: {err}"
                                ))));
                            }
                            if let Ok(guard) = on_down_clone.lock() {
                                if let Some(ref cb) = *guard {
                                    cb();
                                }
                            }
                            break;
                        }
                    }
                }
            })
            .map_err(|e| {
                LibraryError::unavailable(&format!("Failed to spawn reader thread: {e}"))
            })?;

        let (writer_tx, writer_rx) = std::sync::mpsc::channel::<WriterCommand>();
        let writer_thread = std::thread::Builder::new()
            .name("stdio-library-writer".to_string())
            .spawn(move || {
                let mut stdin = stdin;
                while let Ok(cmd) = writer_rx.recv() {
                    match cmd {
                        WriterCommand::Write(bytes, reply) => {
                            let res = stdin.write_all(&bytes).and_then(|_| stdin.flush());
                            let _ = reply.send(res);
                        }
                        WriterCommand::Shutdown => break,
                    }
                }
            })
            .map_err(|e| {
                LibraryError::unavailable(&format!("Failed to spawn writer thread: {e}"))
            })?;

        Ok(Self {
            child: Mutex::new(child),
            writer_tx,
            writer_join_handle: Mutex::new(Some(writer_thread)),
            transaction_lock: Mutex::new(()),
            request_id_gen: AtomicU64::new(1),
            host_session: Mutex::new(None),
            session_export_ids: Mutex::new(HashSet::new()),
            event_sink,
            pending_responses,
            is_down,
            on_down,
            reader_join_handle: Mutex::new(Some(reader_thread)),
            shutdown_executed: AtomicBool::new(false),
        })
    }

    /// Asynchronous pipe write governed by explicit timeout.
    /// Eliminates OS pipe write blocking by executing writes on a dedicated writer thread.
    fn write_stdin_timeout(
        &self,
        bytes: Vec<u8>,
        timeout: Option<Duration>,
    ) -> Result<(), LibraryError> {
        if self.is_down.load(Ordering::SeqCst) {
            return Err(LibraryError::unavailable("Channel is shutting down"));
        }
        let (reply_tx, reply_rx) = std::sync::mpsc::sync_channel(1);
        self.writer_tx
            .send(WriterCommand::Write(bytes, reply_tx))
            .map_err(|_| LibraryError::unavailable("Stdin writer thread unavailable"))?;

        match timeout {
            Some(t) => match reply_rx.recv_timeout(t) {
                Ok(Ok(())) => Ok(()),
                Ok(Err(e)) => Err(LibraryError::unavailable(&format!("stdin write failed: {e}"))),
                Err(std::sync::mpsc::RecvTimeoutError::Timeout) => {
                    Err(LibraryError::unavailable("stdin write timed out"))
                }
                Err(std::sync::mpsc::RecvTimeoutError::Disconnected) => {
                    Err(LibraryError::unavailable("Stdin writer thread disconnected"))
                }
            },
            None => match reply_rx.recv() {
                Ok(Ok(())) => Ok(()),
                Ok(Err(e)) => Err(LibraryError::unavailable(&format!("stdin write failed: {e}"))),
                Err(_) => Err(LibraryError::unavailable("Stdin writer thread disconnected")),
            },
        }
    }

    pub fn set_on_down(&self, cb: Arc<dyn Fn() + Send + Sync>) {
        if let Ok(mut guard) = self.on_down.lock() {
            *guard = Some(cb);
        }
    }

    pub fn round_trip(
        &self,
        command: &str,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        let req_id = format!(
            "req-{}",
            self.request_id_gen.fetch_add(1, Ordering::Relaxed)
        );
        let request = build_application_envelope(&req_id, command, payload);

        self.exchange(request)
    }

    fn round_trip_create(
        &self,
        command: &str,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        let req_id = format!(
            "create-req-{}",
            self.request_id_gen.fetch_add(1, Ordering::Relaxed)
        );
        let request = build_application_envelope_at_minor(&req_id, command, payload, 8);
        self.exchange_expected_minor(request, Some(8))
    }

    fn round_trip_p15(
        &self,
        command: &str,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        let req_id = format!(
            "p15-req-{}",
            self.request_id_gen.fetch_add(1, Ordering::Relaxed)
        );
        let request = build_application_envelope_at_minor(&req_id, command, payload, 7);
        self.exchange_expected_minor(request, Some(7))
    }

    fn acquire_transaction_lock(
        &self,
        timeout: Option<Duration>,
    ) -> Result<std::sync::MutexGuard<'_, ()>, LibraryError> {
        match timeout {
            None => self
                .transaction_lock
                .lock()
                .map_err(|_| LibraryError::unavailable("Internal mutex poisoned (transaction)")),
            Some(limit) => {
                let start = Instant::now();
                let poll = Duration::from_millis(10);
                loop {
                    match self.transaction_lock.try_lock() {
                        Ok(guard) => return Ok(guard),
                        Err(std::sync::TryLockError::Poisoned(_)) => {
                            return Err(LibraryError::unavailable(
                                "Internal mutex poisoned (transaction)",
                            ));
                        }
                        Err(std::sync::TryLockError::WouldBlock) => {
                            if start.elapsed() >= limit {
                                return Err(LibraryError::unavailable(
                                    "Timed out waiting for transaction lock",
                                ));
                            }
                            std::thread::sleep(poll);
                        }
                    }
                }
            }
        }
    }

    fn exchange(&self, request: Value) -> Result<Value, LibraryError> {
        self.exchange_expected_minor(request, None)
    }

    fn exchange_expected_minor(
        &self,
        request: Value,
        expected_minor: Option<u32>,
    ) -> Result<Value, LibraryError> {
        self.exchange_expected_minor_timeout(request, expected_minor, None)
    }

    fn exchange_expected_minor_timeout(
        &self,
        request: Value,
        expected_minor: Option<u32>,
        timeout: Option<Duration>,
    ) -> Result<Value, LibraryError> {
        let start = Instant::now();
        let req_id = request
            .get("request_id")
            .and_then(Value::as_str)
            .unwrap_or("host-control-request")
            .to_string();

        let mut line = request.to_string();
        line.push('\n');

        let _tx_guard = self.acquire_transaction_lock(timeout)?;

        #[cfg(test)]
        TEST_AFTER_TRANSACTION_LOCK_HOOK.with(|cell| {
            if let Some(hook) = cell.borrow_mut().as_mut() {
                hook(&req_id);
            }
        });

        if self.is_down.load(Ordering::SeqCst) {
            return Err(LibraryError::unavailable("Core stdout closed (EOF)"));
        }

        let (tx, rx) = std::sync::mpsc::sync_channel(1);
        {
            let mut pending = lock_timeout_recover(&self.pending_responses, Duration::from_millis(100))
                .ok_or_else(|| LibraryError::unavailable("Timed out acquiring pending mutex"))?;
            pending.insert(req_id.clone(), tx);
        }

        let remaining_for_write = match timeout {
            Some(limit) => {
                let elapsed = start.elapsed();
                if elapsed >= limit {
                    if let Some(mut pending) = lock_timeout_recover(&self.pending_responses, Duration::from_millis(50)) {
                        pending.remove(&req_id);
                    }
                    return Err(LibraryError::unavailable("Core request timed out before write"));
                }
                Some(limit - elapsed)
            }
            None => None,
        };

        if let Err(e) = self.write_stdin_timeout(line.into_bytes(), remaining_for_write) {
            if let Some(mut pending) = lock_timeout_recover(&self.pending_responses, Duration::from_millis(50)) {
                pending.remove(&req_id);
            }
            return Err(e);
        }

        let response_line = match timeout {
            Some(limit) => {
                let elapsed = start.elapsed();
                let remaining = if elapsed >= limit {
                    Duration::from_millis(0)
                } else {
                    limit - elapsed
                };
                match rx.recv_timeout(remaining) {
                    Ok(Ok(resp)) => resp,
                    Ok(Err(err)) => return Err(err),
                    Err(std::sync::mpsc::RecvTimeoutError::Timeout) => {
                        if let Some(mut pending) = lock_timeout_recover(&self.pending_responses, Duration::from_millis(50)) {
                            pending.remove(&req_id);
                        }
                        return Err(LibraryError::unavailable("Core request timed out"));
                    }
                    Err(std::sync::mpsc::RecvTimeoutError::Disconnected) => {
                        return Err(LibraryError::unavailable("Core stdout closed (EOF)"));
                    }
                }
            }
            None => match rx.recv() {
                Ok(Ok(resp)) => resp,
                Ok(Err(err)) => return Err(err),
                Err(_) => return Err(LibraryError::unavailable("Core stdout closed (EOF)")),
            },
        };

        #[cfg(test)]
        TEST_RESPONSE_OBSERVER.with(|cell| {
            if let Some(observer) = cell.borrow_mut().as_mut() {
                observer(&req_id, response_line.trim_end());
            }
        });

        #[cfg(test)]
        TEST_BEFORE_TRANSACTION_UNLOCK_HOOK.with(|cell| {
            if let Some(hook) = cell.borrow_mut().as_mut() {
                hook(&req_id);
            }
        });

        drop(_tx_guard);

        if response_line.is_empty() {
            return Err(LibraryError::unavailable("Core stdout closed (EOF)"));
        }

        if let Some(minor) = expected_minor {
            let envelope: Value = serde_json::from_str(response_line.trim_end())
                .map_err(|_| LibraryError::unavailable("Core settings response is invalid"))?;
            if envelope.get("protocol").and_then(Value::as_str) != Some("new-manga.core")
                || envelope.pointer("/version/major").and_then(Value::as_u64) != Some(2)
                || envelope.pointer("/version/minor").and_then(Value::as_u64)
                    != Some(u64::from(minor))
            {
                return Err(LibraryError::new(
                    "SETTINGS_UNAVAILABLE",
                    "unavailable",
                    true,
                    None,
                ));
            }
        }

        decode_response(response_line.trim_end())
    }

    pub fn round_trip_timeout(
        &self,
        command: &str,
        payload: serde_json::Value,
        timeout: Option<Duration>,
    ) -> Result<serde_json::Value, LibraryError> {
        let req_id = format!(
            "req-{}",
            self.request_id_gen.fetch_add(1, Ordering::Relaxed)
        );
        let request = build_application_envelope(&req_id, command, payload);

        self.exchange_expected_minor_timeout(request, None, timeout)
    }

    pub fn ping_timeout(&self, timeout: Duration) -> Result<PingResult, LibraryError> {
        let val = self.round_trip_timeout("core.ping", serde_json::json!({}), Some(timeout))?;
        serde_json::from_value(val)
            .map_err(|e| LibraryError::malformed(&format!("Failed to parse PingResult: {e}")))
    }

    fn host_control_round_trip(
        &self,
        command: &str,
        payload: Value,
        session: Option<&HostSession>,
    ) -> Result<Value, LibraryError> {
        let request_id = format!(
            "hostctl-{}",
            self.request_id_gen.fetch_add(1, Ordering::Relaxed)
        );
        let request = build_host_control_envelope(&request_id, command, payload, session);
        self.exchange(request)
    }

    pub fn open_host_session(&self) -> Result<(), LibraryError> {
        let mut current = self
            .host_session
            .lock()
            .map_err(|_| LibraryError::unavailable("Host session state is unavailable"))?;
        if current.is_some() {
            return Err(LibraryError::new(
                "HOST_SESSION_ALREADY_OPENED",
                "conflict",
                false,
                None,
            ));
        }
        let mut credential_bytes = [0; 32];
        let credential =
            crate::host_issuer::random_token(&mut credential_bytes).map_err(host_issuer_error)?;
        credential_bytes.fill(0);
        let mut session_bytes = [0; 32];
        let host_session_id = format!(
            "host_{}",
            crate::host_issuer::random_token(&mut session_bytes).map_err(host_issuer_error)?
        );
        session_bytes.fill(0);
        let mut signing_key = [0; 32];
        crate::host_issuer::random_bytes(&mut signing_key).map_err(host_issuer_error)?;
        let result = self.host_control_round_trip(
            "OpenHostSession",
            serde_json::json!({
                "host_session_id": host_session_id.clone(),
                "host_session_credential": credential.clone(),
            }),
            None,
        )?;
        let core_session_id = result
            .get("core_session_id")
            .and_then(Value::as_str)
            .filter(|id| !id.is_empty())
            .ok_or_else(|| LibraryError::malformed("Host session response is invalid"))?
            .to_string();
        *current = Some(HostSession {
            host_session_id,
            credential,
            core_session_id,
            signing_key,
        });
        Ok(())
    }

    fn revoke_host_grant(&self, session: &HostSession, kind: &str, grant_id: &str) {
        let command = match kind {
            "import" => "RevokeImportSource",
            _ => "RevokeExportTarget",
        };
        let _ = self.host_control_round_trip(
            command,
            serde_json::json!({ "grant_id": grant_id }),
            Some(session),
        );
    }

    fn import_with_session(
        &self,
        session: &HostSession,
        path: &Path,
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        let path = path.to_path_buf();
        self.import_paths_with_session(
            session,
            std::slice::from_ref(&path),
            source_kind,
            chapter_id,
            duplicate_policy,
        )
    }

    fn import_paths_with_session(
        &self,
        session: &HostSession,
        paths: &[PathBuf],
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        if chapter_id.is_empty()
            || paths.is_empty()
            || (source_kind == "directory" && paths.len() != 1)
            || duplicate_policy.is_some_and(|p| !matches!(p, "skip" | "import_as_new"))
        {
            return Err(LibraryError::new(
                "INVALID_REQUEST",
                "validation",
                false,
                None,
            ));
        }
        let grants = paths
            .iter()
            .map(|path| {
                let mut grant_id_bytes = [0; 32];
                let grant_id = format!(
                    "grant_{}",
                    crate::host_issuer::random_token(&mut grant_id_bytes)
                        .map_err(host_issuer_error)?
                );
                crate::host_issuer::build_import_grant(
                    path,
                    source_kind,
                    &session.host_session_id,
                    grant_id,
                    &session.signing_key,
                )
                .map_err(host_issuer_error)
            })
            .collect::<Result<Vec<_>, _>>()?;
        let grant_ids = grants
            .iter()
            .map(|grant| grant.grant_id.clone())
            .collect::<Vec<_>>();
        let references = grants
            .iter()
            .map(|grant| grant.reference.clone())
            .collect::<Vec<_>>();
        for grant in grants {
            let registration =
                self.host_control_round_trip("RegisterImportSource", grant.payload, Some(session));
            match registration {
                Ok(value) if value.get("registered") == Some(&Value::Bool(true)) => {}
                Ok(_) => {
                    for id in &grant_ids {
                        self.revoke_host_grant(session, "import", id);
                    }
                    return Err(LibraryError::malformed(
                        "Core did not register import grant",
                    ));
                }
                Err(error) => {
                    for id in &grant_ids {
                        self.revoke_host_grant(session, "import", id);
                    }
                    return Err(error);
                }
            }
        }
        let mut payload = serde_json::json!({
            "chapter_id": chapter_id,
            "sources": references,
        });
        if let Some(policy) = duplicate_policy {
            payload["duplicate_policy"] = serde_json::json!(policy);
        }
        let result = match self.round_trip("ImportPages", payload) {
            Ok(result) => result,
            Err(error) => {
                for id in &grant_ids {
                    self.revoke_host_grant(session, "import", id);
                }
                return Err(error);
            }
        };
        match crate::host_issuer::import_summary(result) {
            Ok(summary) => Ok(summary),
            Err(error) => {
                for id in &grant_ids {
                    self.revoke_host_grant(session, "import", id);
                }
                Err(host_issuer_error(error))
            }
        }
    }

    fn export_with_session(
        &self,
        session: &HostSession,
        path: &Path,
        mut request: Value,
    ) -> Result<crate::host_issuer::ExportSummary, LibraryError> {
        let (format, extension) =
            crate::host_issuer::validate_export_request(&request).map_err(host_issuer_error)?;
        let mut grant_id_bytes = [0; 32];
        let grant = crate::host_issuer::build_export_grant(
            path,
            format,
            extension,
            &session.host_session_id,
            format!(
                "grant_{}",
                crate::host_issuer::random_token(&mut grant_id_bytes).map_err(host_issuer_error)?
            ),
            &session.signing_key,
        )
        .map_err(host_issuer_error)?;
        let registration =
            self.host_control_round_trip("RegisterExportTarget", grant.payload, Some(session))?;
        if registration.get("registered") != Some(&Value::Bool(true)) {
            self.revoke_host_grant(session, "export", &grant.grant_id);
            return Err(LibraryError::malformed(
                "Core did not register export grant",
            ));
        }
        request["target_ref"] = serde_json::json!(grant.reference);
        let result = match self.round_trip("StartExport", request) {
            Ok(result) => result,
            Err(error) => {
                self.revoke_host_grant(session, "export", &grant.grant_id);
                return Err(error);
            }
        };
        match crate::host_issuer::export_summary(result) {
            Ok(summary) => Ok(summary),
            Err(error) => {
                self.revoke_host_grant(session, "export", &grant.grant_id);
                Err(host_issuer_error(error))
            }
        }
    }

    /// M2-DERIVED-GC-2 (design §2.3): the production spawn waits for the
    /// Core's startup `core.ping` before the channel sidecar is started --
    /// the Core answers ping only after it holds the namespace protection
    /// and its startup GC window is done. `timeout` is the ready deadline;
    /// on expiry (or a dead/failing Core) this OWN child is stopped and
    /// reaped (`wait_timeout_or_kill`) so the blocked stdout read gets its
    /// EOF, the reader worker is JOINED (no leaked read thread can steal a
    /// later business response), and the half-open channel is dropped
    /// instead of delivered. A `Drop` on that terminated channel writes to
    /// a broken pipe (ignored) and reaps an already-exited child, so it
    /// never waits the 5 s shutdown path again. Normal round-trip
    /// signatures, request serialization and lock semantics are unchanged.
    pub fn spawn_with_startup_ping(
        python_exe: &str,
        src_root: &std::path::Path,
        data_root: Option<&std::path::Path>,
        derived_root: Option<&std::path::Path>,
        catalog_db: Option<&std::path::Path>,
        startup_timeout: Duration,
    ) -> Result<Self, LibraryError> {
        let channel = Self::spawn_with_resource_roots(
            python_exe,
            src_root,
            data_root,
            derived_root,
            catalog_db,
        )?;
        if channel.wait_first_ping(startup_timeout) {
            Ok(channel)
        } else {
            // Returning Err drops the channel here: stdin/stdout handles and
            // the reaped child all die with it, and no caller can observe the
            // half-open channel.
            Err(LibraryError::unavailable(
                "production core startup ping timed out or failed",
            ))
        }
    }

    /// One coordinated `core.ping` with a deadline. The reader WORKER holds
    /// only the stdout lock while it blocks on `read_line`; the coordinator
    /// takes the CHILD lock to stop the process and never waits on the
    /// stdout lock, so the two locks cannot deadlock. The worker is joined
    /// before the verdict is returned.
    fn wait_first_ping(&self, timeout: Duration) -> bool {
        let deadline = Instant::now() + timeout;
        std::thread::scope(|scope| {
            let worker = scope.spawn(|| self.ping());
            loop {
                if worker.is_finished() {
                    break;
                }
                if Instant::now() >= deadline {
                    // Holding the child lock only: the worker holds the
                    // stdout lock and does not wait on the child lock.
                    if let Ok(mut child) = self.child.lock() {
                        let _ = wait_timeout_or_kill(&mut child, Duration::from_millis(500));
                    }
                    break;
                }
                std::thread::sleep(Duration::from_millis(25));
            }
            matches!(worker.join(), Ok(Ok(_)))
        })
    }

    #[cfg(test)]
    pub fn kill_for_test(&self) {
        if let Ok(mut child) = self.child.lock() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }

    /// Test-only injection surface (RC-4 N-1 precedent): wrap an arbitrary
    /// child as a channel so the startup-ping deadline/kill path can be
    /// exercised against a process that never answers.
    #[cfg(test)]
    pub fn adopt_child_for_test(child: Child) -> Result<Self, LibraryError> {
        Self::adopt_child(child)
    }
}

pub fn wait_timeout_or_kill(
    child: &mut Child,
    timeout: std::time::Duration,
) -> Result<std::process::ExitStatus, std::io::Error> {
    let start = std::time::Instant::now();
    let poll_interval = std::time::Duration::from_millis(20);
    while start.elapsed() < timeout {
        if let Some(status) = child.try_wait()? {
            return Ok(status);
        }
        std::thread::sleep(poll_interval);
    }
    // Timeout reached: kill the process
    let _ = child.kill();
    // Hard upper bound: wait for killed child with bounded timeout (max 800ms),
    // eliminating unbounded child.wait() blocking
    let kill_wait_timeout = std::time::Duration::from_millis(800);
    let kill_start = std::time::Instant::now();
    while kill_start.elapsed() < kill_wait_timeout {
        if let Some(status) = child.try_wait()? {
            return Ok(status);
        }
        std::thread::sleep(poll_interval);
    }
    Err(std::io::Error::new(
        std::io::ErrorKind::TimedOut,
        format!(
            "Child process failed to exit after kill within {:?}",
            kill_wait_timeout
        ),
    ))
}

impl StdioLibraryChannel {
    pub fn shutdown_and_kill(&self, kill_timeout: Duration) {
        if self.shutdown_executed.swap(true, Ordering::SeqCst) {
            // R-009: Idempotent guard prevents duplicate cleanup and preserves single cumulative bound (< 3000ms)
            return;
        }
        self.is_down.store(true, Ordering::SeqCst);

        // 1. Unblock any threads waiting for responses immediately (max 50ms lock)
        if let Some(mut lock) = lock_timeout_recover(&self.pending_responses, Duration::from_millis(50)) {
            for (_req_id, sender) in lock.drain() {
                let _ = sender.send(Err(LibraryError::unavailable(
                    "Channel is shutting down",
                )));
            }
        }

        // 2. Try closing host session ONLY if host_session lock is available,
        // and exchange with bounded timeout (250ms total, including tx lock, stdin write, and recv).
        if let Some(mut session_slot) = lock_timeout_recover(&self.host_session, Duration::from_millis(50)) {
            if let Some(session) = session_slot.take() {
                let request_id = format!(
                    "hostctl-{}",
                    self.request_id_gen.fetch_add(1, Ordering::Relaxed)
                );
                let request = build_host_control_envelope(
                    &request_id,
                    "CloseHostSession",
                    serde_json::json!({}),
                    Some(&session),
                );
                let _ = self.exchange_expected_minor_timeout(
                    request,
                    None,
                    Some(Duration::from_millis(250)),
                );
            }
        }

        // 3. Send core.shutdown to stdin if possible (strictly bounded to 100ms via writer thread)
        let req = serde_json::json!({
            "protocol": "new-manga.core",
            "version": { "major": 2, "minor": 3 },
            "request_id": "shutdown-drop",
            "command": "core.shutdown",
            "payload": {},
        });
        let mut req_str = req.to_string();
        req_str.push('\n');
        let _ = self.write_stdin_timeout(req_str.into_bytes(), Some(Duration::from_millis(100)));

        // 4. Wait for child with timeout or kill (strictly bounded, recovering poisoned lock)
        if let Some(mut child) = lock_timeout_recover(&self.child, Duration::from_millis(100)) {
            let _ = wait_timeout_or_kill(&mut child, kill_timeout);
        }

        // 5. Join reader thread with bounded timeout (hard upper bound: 150ms)
        // Eliminates unbounded handle.join() block if reader thread is hung on stdout
        if let Some(mut handle_slot) = lock_timeout_recover(&self.reader_join_handle, Duration::from_millis(50)) {
            if let Some(handle) = handle_slot.take() {
                let (done_tx, done_rx) = std::sync::mpsc::sync_channel(1);
                let joiner = std::thread::Builder::new()
                    .name("reader-join-guard".to_string())
                    .spawn(move || {
                        let _ = handle.join();
                        let _ = done_tx.send(());
                    });
                if joiner.is_ok() {
                    let _ = done_rx.recv_timeout(Duration::from_millis(150));
                }
            }
        }

        // 6. Join writer thread with bounded timeout (hard upper bound: 100ms)
        if let Some(mut handle_slot) = lock_timeout_recover(&self.writer_join_handle, Duration::from_millis(50)) {
            if let Some(handle) = handle_slot.take() {
                let _ = self.writer_tx.send(WriterCommand::Shutdown);
                let (done_tx, done_rx) = std::sync::mpsc::sync_channel(1);
                let joiner = std::thread::Builder::new()
                    .name("writer-join-guard".to_string())
                    .spawn(move || {
                        let _ = handle.join();
                        let _ = done_tx.send(());
                    });
                if joiner.is_ok() {
                    let _ = done_rx.recv_timeout(Duration::from_millis(100));
                }
            }
        }
    }
}

impl Drop for StdioLibraryChannel {
    fn drop(&mut self) {
        self.shutdown_and_kill(std::time::Duration::from_millis(1200));
    }
}

#[cfg(test)]
thread_local! {
    static TEST_AFTER_TRANSACTION_LOCK_HOOK: std::cell::RefCell<Option<Box<dyn FnMut(&str)>>> =
        std::cell::RefCell::new(None);
    static TEST_BEFORE_TRANSACTION_UNLOCK_HOOK: std::cell::RefCell<Option<Box<dyn FnMut(&str)>>> =
        std::cell::RefCell::new(None);
    static TEST_RESPONSE_OBSERVER: std::cell::RefCell<Option<Box<dyn FnMut(&str, &str)>>> =
        std::cell::RefCell::new(None);
}

#[cfg(test)]
pub(crate) fn set_test_after_transaction_lock_hook<F>(f: Option<F>)
where
    F: FnMut(&str) + 'static,
{
    TEST_AFTER_TRANSACTION_LOCK_HOOK.with(|cell| {
        *cell.borrow_mut() = f.map(|func| Box::new(func) as Box<dyn FnMut(&str)>);
    });
}

#[cfg(test)]
pub(crate) fn set_test_before_transaction_unlock_hook<F>(f: Option<F>)
where
    F: FnMut(&str) + 'static,
{
    TEST_BEFORE_TRANSACTION_UNLOCK_HOOK.with(|cell| {
        *cell.borrow_mut() = f.map(|func| Box::new(func) as Box<dyn FnMut(&str)>);
    });
}

#[cfg(test)]
pub(crate) fn set_test_response_observer<F>(f: Option<F>)
where
    F: FnMut(&str, &str) + 'static,
{
    TEST_RESPONSE_OBSERVER.with(|cell| {
        *cell.borrow_mut() = f.map(|func| Box::new(func) as Box<dyn FnMut(&str, &str)>);
    });
}

impl LibraryChannel for StdioLibraryChannel {
    fn ping(&self) -> Result<PingResult, LibraryError> {
        self.ping_timeout(Duration::from_millis(2000))
    }

    fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
        let val = self.round_trip("ListBooks", serde_json::json!({}))?;
        serde_json::from_value(val)
            .map_err(|e| LibraryError::malformed(&format!("Failed to parse BookSummary list: {e}")))
    }

    fn create_book(&self, title: &str) -> Result<BookSummary, LibraryError> {
        let value = self.round_trip_create("CreateBook", serde_json::json!({ "title": title }))?;
        parse_created_book(value)
    }

    fn create_chapter(
        &self,
        book_id: &str,
        title: &str,
        chapter_number: Option<&str>,
    ) -> Result<ChapterNavSummary, LibraryError> {
        let mut payload = serde_json::json!({ "book_id": book_id, "title": title });
        if let Some(chapter_number) = chapter_number {
            payload["chapter_number"] = serde_json::json!(chapter_number);
        }
        let value = self.round_trip_create("CreateChapter", payload)?;
        parse_created_chapter(value)
    }

    fn get_settings(&self, section: Option<&str>) -> Result<serde_json::Value, LibraryError> {
        // contract rev 1.3 §5.3: the full projection ({} payload) or one
        // section ({"section": name}); the result passes through as raw JSON
        let payload = match section {
            Some(name) => serde_json::json!({ "section": name }),
            None => serde_json::json!({}),
        };
        self.round_trip("settings.get", payload)
    }

    fn update_settings_section(
        &self,
        section: &str,
        values: &serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        // contract rev 1.3 §5.3: value-domain validation (sfx.policy) is
        // Core-side and pre-persistence; a typed INVALID_REQUEST rejection
        // arrives through decode_response as a normal LibraryError
        self.round_trip(
            "settings.update_section",
            serde_json::json!({ "section": section, "values": values }),
        )
    }

    fn p15_settings(
        &self,
        command: P15SettingsCommand,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        self.round_trip_p15(command.core_name(), payload)
    }

    fn set_region_type(
        &self,
        region_id: &str,
        new_region_type: &str,
        expected_revision: Option<i64>,
    ) -> Result<serde_json::Value, LibraryError> {
        // contract rev 1.4 §5.4: the optional optimistic guard rides the
        // payload only when the caller supplies it (its absence = the
        // user-direct write); the Core validates everything pre-persistence
        let mut payload = serde_json::json!({
            "region_id": region_id,
            "new_region_type": new_region_type,
        });
        if let Some(revision) = expected_revision {
            payload["expected_revision"] = serde_json::json!(revision);
        }
        self.round_trip("set_region_type", payload)
    }

    fn list_regions(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
        // contract rev 1.4 §5.4: the result is the raw {"regions": [...]}
        // projection (empty list for a page without rows, not an error)
        self.round_trip("list_regions", serde_json::json!({ "page_id": page_id }))
    }

    fn list_region_revisions(&self, region_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "list_region_revisions",
            serde_json::json!({ "region_id": region_id }),
        )
    }

    fn restore_region_revision(
        &self,
        region_id: &str,
        revision_no: i64,
        expected_revision: i64,
    ) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "restore_region_revision",
            serde_json::json!({
                "region_id": region_id,
                "revision_no": revision_no,
                "expected_revision": expected_revision,
            }),
        )
    }

    fn rerender_page(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip("rerender_page", serde_json::json!({ "page_id": page_id }))
    }

    fn resolve_page_resource(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "resolve_page_resource",
            serde_json::json!({ "page_id": page_id }),
        )
    }

    fn list_chapters(&self, book_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip("list_chapters", serde_json::json!({ "book_id": book_id }))
    }

    fn list_chapter_pages(&self, chapter_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "list_chapter_pages",
            serde_json::json!({ "chapter_id": chapter_id }),
        )
    }

    fn get_reader_projection(
        &self,
        chapter_id: &str,
        mode: &str,
        start_position: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "GetReaderProjection",
            serde_json::json!({
                "chapter_id": chapter_id,
                "mode": mode,
                "start_position": start_position,
            }),
        )
    }

    fn save_reading_progress(
        &self,
        chapter_id: &str,
        mode: &str,
        page_id: &str,
        scroll_offset_y: Option<f64>,
        elapsed_seconds_delta: Option<f64>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "SaveReadingProgress",
            reader_progress_payload(
                chapter_id,
                mode,
                page_id,
                scroll_offset_y,
                elapsed_seconds_delta,
            ),
        )
    }

    /// P13-C1 (contract rev 2.0 §5.5): the Run command family. The wire names
    /// are the PascalCase names frozen in §5.5; every shape and domain rule is
    /// validated Core-side, so the host forwards the payload as given and
    /// propagates the typed rejection code verbatim.
    fn start_run(
        &self,
        command: &str,
        scope: &serde_json::Value,
        overrides: Option<&serde_json::Value>,
        idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        let mut payload = serde_json::json!({
            "command": command,
            "scope": scope,
            "idempotency_key": idempotency_key,
        });
        if let Some(overrides) = overrides {
            payload["overrides"] = overrides.clone();
        }
        self.round_trip("StartRun", payload)
    }

    fn control_run(
        &self,
        run_id: &str,
        action: &str,
        idempotency_key: Option<&str>,
    ) -> Result<serde_json::Value, LibraryError> {
        // §5.5: `restart` MUST carry an idempotency key while the other
        // actions MUST NOT -- the Core enforces both, so the host forwards
        // exactly what the caller supplied and lets the typed rejection
        // (INVALID_REQUEST / IDEMPOTENCY_KEY_REUSED) propagate.
        let mut payload = serde_json::json!({ "run_id": run_id, "action": action });
        if let Some(key) = idempotency_key {
            payload["idempotency_key"] = serde_json::json!(key);
        }
        self.round_trip("ControlRun", payload)
    }

    fn resume_blocked_run(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip("ResumeBlockedRun", serde_json::json!({ "run_id": run_id }))
    }

    fn get_run_snapshot(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip("GetRunSnapshot", serde_json::json!({ "run_id": run_id }))
    }

    fn get_task_projection(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.round_trip("GetTaskProjection", serde_json::json!({ "run_id": run_id }))
    }

    fn retry_failed_targets(
        &self,
        run_id: &str,
        idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.round_trip(
            "RetryFailedTargets",
            serde_json::json!({ "run_id": run_id, "idempotency_key": idempotency_key }),
        )
    }

    fn import_from_path(
        &self,
        path: &Path,
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        let session = self
            .host_session
            .lock()
            .map_err(|_| LibraryError::unavailable("Host session state is unavailable"))?;
        let session = session
            .as_ref()
            .ok_or_else(|| LibraryError::new("HOST_SESSION_INVALID", "conflict", false, None))?;
        self.import_with_session(session, path, source_kind, chapter_id, duplicate_policy)
    }

    fn import_from_paths(
        &self,
        paths: &[PathBuf],
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        let session = self
            .host_session
            .lock()
            .map_err(|_| LibraryError::unavailable("Host session state is unavailable"))?;
        let session = session
            .as_ref()
            .ok_or_else(|| LibraryError::new("HOST_SESSION_INVALID", "conflict", false, None))?;
        self.import_paths_with_session(session, paths, source_kind, chapter_id, duplicate_policy)
    }

    fn start_export_to_path(
        &self,
        path: &Path,
        request: Value,
    ) -> Result<crate::host_issuer::ExportSummary, LibraryError> {
        let session = self
            .host_session
            .lock()
            .map_err(|_| LibraryError::unavailable("Host session state is unavailable"))?;
        let session = session
            .as_ref()
            .ok_or_else(|| LibraryError::new("HOST_SESSION_INVALID", "conflict", false, None))?;
        let summary = self.export_with_session(session, path, request)?;
        self.session_export_ids
            .lock()
            .map_err(|_| LibraryError::unavailable("Export session state is unavailable"))?
            .insert(summary.export_id.clone());
        Ok(summary)
    }

    fn export_output_directory(&self, export_id: &str) -> Result<PathBuf, LibraryError> {
        let session_export_ids = self
            .session_export_ids
            .lock()
            .map_err(|_| LibraryError::unavailable("Export session state is unavailable"))?;
        require_current_session_export(export_id, &session_export_ids)?;
        drop(session_export_ids);
        let history = self.round_trip("GetExportHistory", serde_json::json!({}))?;
        resolve_export_output_directory(export_id, history)
    }
    fn set_event_sink(&self, sink: EventSink) {
        *self.event_sink.lock().unwrap() = Some(sink);
    }

    fn cancel_export(&self, export_id: &str) -> Result<ExportProgressSnapshotView, LibraryError> {
        let val = self.round_trip(
            "CancelExport",
            serde_json::json!({ "export_id": export_id }),
        )?;
        project_export_snapshot(val)
    }

    fn get_export_snapshot(
        &self,
        export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
        let val = self.round_trip(
            "GetExportSnapshot",
            serde_json::json!({ "export_id": export_id }),
        )?;
        project_export_snapshot(val)
    }

    fn get_export_history(&self) -> Result<ExportHistoryResponseView, LibraryError> {
        let val = self.round_trip("GetExportHistory", serde_json::json!({}))?;
        project_export_history(val)
    }
}

fn export_not_found() -> LibraryError {
    LibraryError::new("EXPORT_NOT_FOUND", "not_found", false, None)
}

fn export_output_not_ready() -> LibraryError {
    LibraryError::new("EXPORT_OUTPUT_NOT_READY", "conflict", false, None)
}

fn export_path_unavailable() -> LibraryError {
    LibraryError::new("EXPORT_PATH_UNAVAILABLE", "unavailable", false, None)
}

fn require_current_session_export(
    export_id: &str,
    session_export_ids: &HashSet<String>,
) -> Result<(), LibraryError> {
    if !session_export_ids.contains(export_id) {
        return Err(export_not_found());
    }
    Ok(())
}

fn resolve_export_output_directory(
    export_id: &str,
    history: Value,
) -> Result<PathBuf, LibraryError> {
    let exports = history
        .get("exports")
        .and_then(Value::as_array)
        .ok_or_else(|| LibraryError::malformed("Core export history is malformed"))?;
    let Some(export) = exports
        .iter()
        .find(|row| row.get("export_id").and_then(Value::as_str) == Some(export_id))
    else {
        return Err(export_not_found());
    };
    if export.get("status").and_then(Value::as_str) != Some("completed") {
        return Err(export_output_not_ready());
    }
    let output_path = export
        .get("output_path")
        .and_then(Value::as_str)
        .map(PathBuf::from)
        .filter(|path| path.is_absolute())
        .ok_or_else(export_path_unavailable)?;
    if !output_path.is_file() {
        return Err(export_path_unavailable());
    }
    let directory = output_path
        .parent()
        .and_then(|path| path.canonicalize().ok())
        .filter(|path| path.is_dir() && path.to_str().is_some())
        .ok_or_else(export_path_unavailable)?;
    Ok(directory)
}

fn host_issuer_error(error: crate::host_issuer::HostIssuerError) -> LibraryError {
    let category = match error.0 {
        "SOURCE_READ_FAILED" => "unavailable",
        "HOST_CREDENTIAL_UNAVAILABLE" => "internal",
        _ => "validation",
    };
    LibraryError::new(error.0, category, false, None)
}

/// In-memory mock channel for testing without spawning Python.
pub struct MockLibraryChannel {
    ping_result: Mutex<Result<PingResult, LibraryError>>,
    books_result: Mutex<Result<Vec<BookSummary>, LibraryError>>,
    settings_result: Mutex<Result<serde_json::Value, LibraryError>>,
    retype_result: Mutex<Result<serde_json::Value, LibraryError>>,
    regions_result: Mutex<Result<serde_json::Value, LibraryError>>,
    domain_result: Mutex<Result<serde_json::Value, LibraryError>>,
    export_snapshot_result: Mutex<Result<ExportProgressSnapshotView, LibraryError>>,
    export_history_result: Mutex<Result<ExportHistoryResponseView, LibraryError>>,
    pub event_sink: Mutex<Option<EventSink>>,
}

impl MockLibraryChannel {
    pub fn new() -> Self {
        Self {
            ping_result: Mutex::new(Ok(PingResult {
                status: "ready".to_string(),
                protocol_version: ProtocolVersion { major: 1, minor: 0 },
                capabilities: vec!["library.list_books".to_string()],
            })),
            books_result: Mutex::new(Ok(Vec::new())),
            settings_result: Mutex::new(Ok(serde_json::json!({ "settings": {} }))),
            retype_result: Mutex::new(Ok(serde_json::json!({
                "region_id": "r1",
                "revision_no": 2,
                "region_type": "sfx",
                "sfx_policy": "skip",
            }))),
            regions_result: Mutex::new(Ok(serde_json::json!({ "regions": [] }))),
            domain_result: Mutex::new(Ok(serde_json::json!({}))),
            export_snapshot_result: Mutex::new(Ok(ExportProgressSnapshotView {
                export_id: "exp-mock-1".to_string(),
                status: "completed".to_string(),
                completed_pages: 1,
                total_pages: 1,
                current_page_id: None,
                accepted_at: "2026-10-16T12:00:00Z".to_string(),
                completed_at: Some("2026-10-16T12:01:00Z".to_string()),
                output: Some(ExportProgressOutputView {
                    format: "pdf".to_string(),
                    sha256: Some(
                        "abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234"
                            .to_string(),
                    ),
                }),
                lineage: Vec::new(),
                error_code: None,
            })),
            export_history_result: Mutex::new(Ok(ExportHistoryResponseView {
                exports: Vec::new(),
            })),
            event_sink: Mutex::new(None),
        }
    }

    pub fn set_export_snapshot_result(
        &self,
        result: Result<ExportProgressSnapshotView, LibraryError>,
    ) {
        *self.export_snapshot_result.lock().unwrap() = result;
    }

    pub fn set_export_history_result(
        &self,
        result: Result<ExportHistoryResponseView, LibraryError>,
    ) {
        *self.export_history_result.lock().unwrap() = result;
    }

    pub fn set_books(&self, books: Vec<BookSummary>) {
        *self.books_result.lock().unwrap() = Ok(books);
    }

    pub fn set_books_error(&self, error: LibraryError) {
        *self.books_result.lock().unwrap() = Err(error);
    }

    /// M2-SETTINGS-IPC-CHANNEL: pin the mocked settings projection (or a
    /// typed rejection, e.g. INVALID_REQUEST) for host-level tests.
    pub fn set_settings_result(&self, result: Result<serde_json::Value, LibraryError>) {
        *self.settings_result.lock().unwrap() = result;
    }

    /// M2-REGION-RETYPE-CORE: pin the mocked retype result / read
    /// projection (or a typed rejection) for host-level tests.
    pub fn set_retype_result(&self, result: Result<serde_json::Value, LibraryError>) {
        *self.retype_result.lock().unwrap() = result;
    }

    pub fn set_regions_result(&self, result: Result<serde_json::Value, LibraryError>) {
        *self.regions_result.lock().unwrap() = result;
    }

    /// M2-PAGE-RESOURCE-RESOLVE-1 (DSH r1 PR-01): pin the mocked
    /// domain-command result (history/restore/rerender/page-resolve share
    /// one slot) or a typed rejection for host-level tests.
    pub fn set_domain_result(&self, result: Result<serde_json::Value, LibraryError>) {
        *self.domain_result.lock().unwrap() = result;
    }

    #[allow(dead_code)]
    pub fn set_ping_error(&self, error: LibraryError) {
        *self.ping_result.lock().unwrap() = Err(error);
    }
}

impl Default for MockLibraryChannel {
    fn default() -> Self {
        Self::new()
    }
}

impl LibraryChannel for MockLibraryChannel {
    fn ping(&self) -> Result<PingResult, LibraryError> {
        self.ping_result.lock().unwrap().clone()
    }

    fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
        self.books_result.lock().unwrap().clone()
    }

    fn create_book(&self, _title: &str) -> Result<BookSummary, LibraryError> {
        self.domain_result
            .lock()
            .unwrap()
            .clone()
            .and_then(parse_created_book)
    }

    fn create_chapter(
        &self,
        _book_id: &str,
        _title: &str,
        _chapter_number: Option<&str>,
    ) -> Result<ChapterNavSummary, LibraryError> {
        self.domain_result
            .lock()
            .unwrap()
            .clone()
            .and_then(parse_created_chapter)
    }

    fn get_settings(&self, _section: Option<&str>) -> Result<serde_json::Value, LibraryError> {
        self.settings_result.lock().unwrap().clone()
    }

    fn update_settings_section(
        &self,
        _section: &str,
        _values: &serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        self.settings_result.lock().unwrap().clone()
    }

    fn bind_profile_credential(
        &self,
        _target: P15CredentialTarget,
        _credential_ref: &str,
    ) -> Result<(), LibraryError> {
        Err(LibraryError::unavailable(
            "mock credential exchange is not configured",
        ))
    }

    fn clear_profile_credential(&self, _target: P15CredentialTarget) -> Result<(), LibraryError> {
        Err(LibraryError::unavailable(
            "mock credential exchange is not configured",
        ))
    }

    fn set_region_type(
        &self,
        _region_id: &str,
        _new_region_type: &str,
        _expected_revision: Option<i64>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.retype_result.lock().unwrap().clone()
    }

    fn list_regions(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.regions_result.lock().unwrap().clone()
    }

    fn list_region_revisions(&self, _region_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn restore_region_revision(
        &self,
        _region_id: &str,
        _revision_no: i64,
        _expected_revision: i64,
    ) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn rerender_page(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn resolve_page_resource(&self, _page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn list_chapters(&self, _book_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn list_chapter_pages(&self, _chapter_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn get_reader_projection(
        &self,
        _chapter_id: &str,
        _mode: &str,
        _start_position: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn save_reading_progress(
        &self,
        _chapter_id: &str,
        _mode: &str,
        _page_id: &str,
        _scroll_offset_y: Option<f64>,
        _elapsed_seconds_delta: Option<f64>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    // RUN-IPC-1: the Run family is canned like every other mock method so
    // tests can drive both the success and the typed-rejection paths
    // deterministically.
    fn start_run(
        &self,
        _command: &str,
        _scope: &serde_json::Value,
        _overrides: Option<&serde_json::Value>,
        _idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn control_run(
        &self,
        _run_id: &str,
        _action: &str,
        _idempotency_key: Option<&str>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn resume_blocked_run(&self, _run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn get_run_snapshot(&self, _run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn get_task_projection(&self, _run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }

    fn retry_failed_targets(
        &self,
        _run_id: &str,
        _idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.domain_result.lock().unwrap().clone()
    }
    fn set_event_sink(&self, sink: EventSink) {
        *self.event_sink.lock().unwrap() = Some(sink);
    }

    fn cancel_export(&self, _export_id: &str) -> Result<ExportProgressSnapshotView, LibraryError> {
        self.export_snapshot_result.lock().unwrap().clone()
    }

    fn get_export_snapshot(
        &self,
        _export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
        self.export_snapshot_result.lock().unwrap().clone()
    }

    fn get_export_history(&self) -> Result<ExportHistoryResponseView, LibraryError> {
        self.export_history_result.lock().unwrap().clone()
    }
}

pub type LibraryChannelSpawner = Arc<
    dyn Fn(&LibrarySpawnConfig) -> Result<StdioLibraryChannel, LibraryError> + Send + Sync,
>;

/// Configuration required to spawn or respawn the Core library sidecar.
#[derive(Clone)]
pub struct LibrarySpawnConfig {
    pub sidecar_path: String,
    pub working_dir: PathBuf,
    pub data_root: Option<PathBuf>,
    pub derived_root: Option<PathBuf>,
    pub catalog_db: Option<PathBuf>,
    pub stable_duration: Duration,
    pub initial_backoff: Duration,
    pub heartbeat_interval: Duration,
    pub heartbeat_ping_timeout: Duration,
    pub custom_spawner: Option<LibraryChannelSpawner>,
}

impl LibrarySpawnConfig {
    pub fn new(
        sidecar_path: String,
        working_dir: PathBuf,
        data_root: Option<PathBuf>,
        derived_root: Option<PathBuf>,
        catalog_db: Option<PathBuf>,
    ) -> Self {
        Self {
            sidecar_path,
            working_dir,
            data_root,
            derived_root,
            catalog_db,
            stable_duration: Duration::from_secs(30),
            initial_backoff: Duration::from_millis(500),
            heartbeat_interval: Duration::from_millis(1500),
            heartbeat_ping_timeout: Duration::from_millis(2000),
            custom_spawner: None,
        }
    }
}

pub(crate) struct ResilientCoreContext {
    pub(crate) inner: Mutex<Option<Arc<StdioLibraryChannel>>>,
    pub(crate) config: LibrarySpawnConfig,
    pub(crate) is_restarting: AtomicBool,
    pub(crate) consecutive_failures: AtomicU32,
    pub(crate) last_spawn_time: Mutex<Option<Instant>>,
    pub(crate) is_fatal: AtomicBool,
    pub(crate) event_sink: Mutex<Option<EventSink>>,
    pub(crate) status_emitter: Mutex<Option<StatusEmitter>>,
    pub(crate) heartbeat_stop: AtomicBool,
}

impl ResilientCoreContext {
    pub fn is_unhealthy(&self) -> bool {
        if self.is_fatal.load(Ordering::SeqCst) || self.is_restarting.load(Ordering::SeqCst) {
            return true;
        }
        if let Ok(guard) = self.inner.lock() {
            match guard.as_ref() {
                Some(chan) => chan.is_down.load(Ordering::SeqCst),
                None => true,
            }
        } else {
            true
        }
    }

    pub fn trigger_restart(self: &Arc<Self>) {
        if self.heartbeat_stop.load(Ordering::Relaxed) || self.is_fatal.load(Ordering::SeqCst) {
            return;
        }

        // R-001: Replenish restart budget only if the sidecar has stably survived for >= stable_duration
        {
            if let Ok(mut last_spawn) = self.last_spawn_time.lock() {
                if let Some(spawned_at) = *last_spawn {
                    if spawned_at.elapsed() >= self.config.stable_duration {
                        eprintln!(
                            "[supervisor] sidecar survived stably for {:?}; replenishing restart budget",
                            spawned_at.elapsed()
                        );
                        self.consecutive_failures.store(0, Ordering::SeqCst);
                        *last_spawn = None;
                    }
                }
            }
        }

        const MAX_RETRIES: u32 = 3;
        if self.consecutive_failures.load(Ordering::SeqCst) >= MAX_RETRIES {
            self.is_fatal.store(true, Ordering::SeqCst);
            self.is_restarting.store(false, Ordering::SeqCst);
            if let Ok(guard) = self.status_emitter.lock() {
                if let Some(ref emitter) = *guard {
                    emitter("fatal", "后端服务异常，自动重启失败，请检查服务日志");
                }
            }
            return;
        }

        if self
            .is_restarting
            .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
            .is_err()
        {
            return;
        }

        // Re-check after acquiring restarting flag
        if self.consecutive_failures.load(Ordering::SeqCst) >= MAX_RETRIES {
            self.is_fatal.store(true, Ordering::SeqCst);
            self.is_restarting.store(false, Ordering::SeqCst);
            if let Ok(guard) = self.status_emitter.lock() {
                if let Some(ref emitter) = *guard {
                    emitter("fatal", "后端服务异常，自动重启失败，请检查服务日志");
                }
            }
            return;
        }

        // 立即向 UI 发送异常与热重启通知（AC1 有界时间 ≤ 5s，立即发射）
        if let Ok(guard) = self.status_emitter.lock() {
            if let Some(ref emitter) = *guard {
                emitter("restarting", "后端服务异常，正在尝试热重启...");
            }
        }

        let ctx = Arc::clone(self);
        std::thread::Builder::new()
            .name("core-self-healing".to_string())
            .spawn(move || {
                // 1. 清理并回收旧进程（R-009: 有界强制回收）
                // 先在短锁内 take 出 old channel，立即释放 inner 锁，再在锁外执行 shutdown_and_kill，
                // 避免持有 inner 锁长达数秒导致其他线程饿死
                let old = {
                    if let Some(mut guard) = lock_timeout_recover(&ctx.inner, Duration::from_millis(100)) {
                        guard.take()
                    } else {
                        None
                    }
                };
                if let Some(old) = old {
                    old.shutdown_and_kill(Duration::from_millis(1200));
                }

                let mut backoff = ctx.config.initial_backoff;
                let mut success = false;

                while ctx.consecutive_failures.load(Ordering::SeqCst) < MAX_RETRIES {
                    if ctx.heartbeat_stop.load(Ordering::Relaxed) {
                        break;
                    }
                    let attempt = ctx.consecutive_failures.fetch_add(1, Ordering::SeqCst) + 1;
                    eprintln!("[supervisor] Restarting core_service (attempt {attempt}/{MAX_RETRIES})...");
                    std::thread::sleep(backoff);
                    if ctx.heartbeat_stop.load(Ordering::Relaxed) {
                        break;
                    }

                    let spawn_res = match &ctx.config.custom_spawner {
                        Some(spawner) => spawner(&ctx.config),
                        None => {
                            let r = StdioLibraryChannel::spawn_with_startup_ping(
                                &ctx.config.sidecar_path,
                                &ctx.config.working_dir,
                                ctx.config.data_root.as_deref(),
                                ctx.config.derived_root.as_deref(),
                                ctx.config.catalog_db.as_deref(),
                                Duration::from_secs(15),
                            );
                            match r {
                                Ok(chan) => {
                                    if let Err(e) = chan.open_host_session() {
                                        Err(e)
                                    } else {
                                        Ok(chan)
                                    }
                                }
                                Err(e) => Err(e),
                            }
                        }
                    };

                    match spawn_res {
                        Ok(new_chan) => {
                            // 重新注入之前注册的 event_sink
                            if let Ok(guard) = ctx.event_sink.lock() {
                                if let Some(ref sink) = *guard {
                                    new_chan.set_event_sink(Arc::clone(sink));
                                }
                            }

                            // R-003: 绑定下次异常退出的瞬时感知回调（Weak 弱引用拆开所有权环）
                            let ctx_weak = Arc::downgrade(&ctx);
                            new_chan.set_on_down(Arc::new(move || {
                                if let Some(c) = ctx_weak.upgrade() {
                                    c.trigger_restart();
                                }
                            }));

                            // 记录启动时间
                            if let Ok(mut guard) = ctx.last_spawn_time.lock() {
                                *guard = Some(Instant::now());
                            }

                            // 原子安装新 channel
                            if let Ok(mut guard) = ctx.inner.lock() {
                                *guard = Some(Arc::new(new_chan));
                            }

                            // R-001: 启动成功不立即清零 consecutive_failures！
                            // 只有稳定存活超过 stable_duration 后才重置预算。
                            success = true;
                            eprintln!("[supervisor] core_service successfully recovered (used attempt {attempt}/{MAX_RETRIES})!");
                            break;
                        }
                        Err(err) => {
                            eprintln!("[supervisor] restart attempt {attempt} failed: {err}");
                            backoff = backoff.saturating_mul(2);
                        }
                    }
                }

                ctx.is_restarting.store(false, Ordering::SeqCst);

                if success {
                    if let Ok(guard) = ctx.status_emitter.lock() {
                        if let Some(ref emitter) = *guard {
                            emitter("recovered", "后端服务已恢复正常");
                        }
                    }
                } else {
                    ctx.is_fatal.store(true, Ordering::SeqCst);
                    if let Ok(guard) = ctx.status_emitter.lock() {
                        if let Some(ref emitter) = *guard {
                            emitter("fatal", "后端服务异常，自动重启失败，请检查服务日志");
                        }
                    }
                }
            })
            .expect("failed to spawn self-healing thread");
    }
}

pub struct ResilientLibraryChannel {
    pub(crate) ctx: Arc<ResilientCoreContext>,
}

impl ResilientLibraryChannel {
    pub fn new(config: LibrarySpawnConfig, initial_channel: Option<StdioLibraryChannel>) -> Self {
        let initial_failures = if initial_channel.is_none() { 1 } else { 0 };
        let initial_spawn_time = if initial_channel.is_some() {
            Some(Instant::now())
        } else {
            None
        };
        let ctx = Arc::new(ResilientCoreContext {
            inner: Mutex::new(initial_channel.map(Arc::new)),
            config,
            is_restarting: AtomicBool::new(false),
            consecutive_failures: AtomicU32::new(initial_failures),
            last_spawn_time: Mutex::new(initial_spawn_time),
            is_fatal: AtomicBool::new(false),
            event_sink: Mutex::new(None),
            status_emitter: Mutex::new(None),
            heartbeat_stop: AtomicBool::new(false),
        });

        // R-003: on_down captures Weak<ResilientCoreContext> to break strong reference cycle
        let ctx_weak = Arc::downgrade(&ctx);
        if let Ok(guard) = ctx.inner.lock() {
            if let Some(ref chan) = *guard {
                chan.set_on_down(Arc::new(move || {
                    if let Some(c) = ctx_weak.upgrade() {
                        c.trigger_restart();
                    }
                }));
            }
        }

        Self { ctx }
    }

    pub fn record_initial_failure(&self) {
        self.ctx.consecutive_failures.store(1, Ordering::SeqCst);
    }

    /// AC2 & R-008: Periodic heartbeat and dead/unresponsive sidecar recovery.
    pub fn start_heartbeat(&self) {
        let ctx = Arc::clone(&self.ctx);
        std::thread::Builder::new()
            .name("core-heartbeat".to_string())
            .spawn(move || {
                while !ctx.heartbeat_stop.load(Ordering::Relaxed) {
                    std::thread::sleep(ctx.config.heartbeat_interval);
                    if ctx.heartbeat_stop.load(Ordering::Relaxed) {
                        break;
                    }
                    if ctx.is_fatal.load(Ordering::SeqCst) {
                        continue;
                    }
                    if ctx.is_restarting.load(Ordering::SeqCst) {
                        continue;
                    }

                    // Replenish budget if sidecar has been stably alive for stable_duration
                    if let Ok(last_spawn) = ctx.last_spawn_time.lock() {
                        if let Some(spawned_at) = *last_spawn {
                            if spawned_at.elapsed() >= ctx.config.stable_duration {
                                if ctx.consecutive_failures.load(Ordering::SeqCst) > 0 {
                                    eprintln!(
                                        "[heartbeat] core_service stable for {:?}; replenishing restart budget",
                                        spawned_at.elapsed()
                                    );
                                    ctx.consecutive_failures.store(0, Ordering::SeqCst);
                                }
                            }
                        }
                    }

                    let chan_opt = {
                        if let Some(guard) = lock_timeout_recover(&ctx.inner, Duration::from_millis(50)) {
                            guard.clone()
                        } else {
                            None
                        }
                    };

                    let needs_restart = match chan_opt {
                        None => true,
                        Some(ref chan) => {
                            let is_alive = if let Some(mut child) = lock_timeout_recover(&chan.child, Duration::from_millis(50)) {
                                match child.try_wait() {
                                    Ok(None) => true,
                                    _ => false,
                                }
                            } else {
                                false
                            };

                            if chan.is_down.load(Ordering::SeqCst) {
                                true
                            } else if is_alive {
                                // R-008: Process is alive; probe IPC responsiveness with bounded ping timeout.
                                // Child lock was released above before ping_timeout to prevent blocking shutdown.
                                match chan.ping_timeout(ctx.config.heartbeat_ping_timeout) {
                                    Ok(_) => false,
                                    Err(err) => {
                                        eprintln!(
                                            "[heartbeat] core_service unresponsive to ping ({err}), triggering restart"
                                        );
                                        true
                                    }
                                }
                            } else {
                                true
                            }
                        }
                    };

                    if needs_restart && !ctx.heartbeat_stop.load(Ordering::Relaxed) {
                        eprintln!("[heartbeat] Detected dead or unresponsive core_service, triggering restart");
                        ctx.trigger_restart();
                    }
                }
            })
            .expect("failed to spawn heartbeat thread");
    }

    fn with_channel<R, F>(&self, f: F) -> Result<R, LibraryError>
    where
        F: FnOnce(&StdioLibraryChannel) -> Result<R, LibraryError>,
    {
        // R-009: Only hold inner lock long enough to clone the Arc<StdioLibraryChannel>,
        // never holding inner lock during IPC round-trip execution.
        let chan = {
            let guard = self
                .ctx
                .inner
                .lock()
                .map_err(|_| LibraryError::unavailable("Lock poisoned"))?;
            guard.clone()
        };

        match chan {
            Some(chan) => {
                let res = f(&chan);
                if let Err(ref err) = res {
                    if err.code == "CORE_UNAVAILABLE" || chan.is_down.load(Ordering::SeqCst) {
                        self.ctx.trigger_restart();
                    }
                }
                res
            }
            None => {
                if !self.ctx.is_fatal.load(Ordering::SeqCst) {
                    self.ctx.trigger_restart();
                }
                Err(LibraryError::unavailable(
                    "Core service is restarting or unavailable",
                ))
            }
        }
    }
}

// R-003, R-009: ResilientLibraryChannel::drop explicitly takes inner channel and executes bounded shutdown
impl Drop for ResilientLibraryChannel {
    fn drop(&mut self) {
        self.ctx.heartbeat_stop.store(true, Ordering::SeqCst);
        let chan = {
            if let Some(mut guard) = lock_timeout_recover(&self.ctx.inner, Duration::from_millis(100)) {
                guard.take()
            } else {
                None
            }
        };
        if let Some(chan) = chan {
            chan.shutdown_and_kill(Duration::from_millis(1200));
        }
    }
}

impl LibraryChannel for ResilientLibraryChannel {
    fn ping(&self) -> Result<PingResult, LibraryError> {
        self.with_channel(|c| c.ping())
    }

    fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
        self.with_channel(|c| c.list_books())
    }

    fn create_book(&self, title: &str) -> Result<BookSummary, LibraryError> {
        self.with_channel(|c| c.create_book(title))
    }

    fn create_chapter(
        &self,
        book_id: &str,
        title: &str,
        chapter_number: Option<&str>,
    ) -> Result<ChapterNavSummary, LibraryError> {
        self.with_channel(|c| c.create_chapter(book_id, title, chapter_number))
    }

    fn get_settings(&self, section: Option<&str>) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.get_settings(section))
    }

    fn update_settings_section(
        &self,
        section: &str,
        values: &serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.update_settings_section(section, values))
    }

    fn p15_settings(
        &self,
        command: P15SettingsCommand,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.p15_settings(command, payload))
    }

    fn bind_profile_credential(
        &self,
        target: P15CredentialTarget,
        secret: &str,
    ) -> Result<(), LibraryError> {
        self.with_channel(|c| c.bind_profile_credential(target, secret))
    }

    fn clear_profile_credential(&self, target: P15CredentialTarget) -> Result<(), LibraryError> {
        self.with_channel(|c| c.clear_profile_credential(target))
    }

    fn set_region_type(
        &self,
        region_id: &str,
        new_region_type: &str,
        expected_revision: Option<i64>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.set_region_type(region_id, new_region_type, expected_revision))
    }

    fn list_regions(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.list_regions(page_id))
    }

    fn list_region_revisions(&self, region_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.list_region_revisions(region_id))
    }

    fn restore_region_revision(
        &self,
        region_id: &str,
        revision_no: i64,
        expected_revision: i64,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.restore_region_revision(region_id, revision_no, expected_revision))
    }

    fn rerender_page(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.rerender_page(page_id))
    }

    fn resolve_page_resource(&self, page_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.resolve_page_resource(page_id))
    }

    fn list_chapters(&self, book_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.list_chapters(book_id))
    }

    fn list_chapter_pages(&self, chapter_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.list_chapter_pages(chapter_id))
    }

    fn get_reader_projection(
        &self,
        chapter_id: &str,
        mode: &str,
        start_position: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.get_reader_projection(chapter_id, mode, start_position))
    }

    fn save_reading_progress(
        &self,
        chapter_id: &str,
        mode: &str,
        page_id: &str,
        scroll_offset_y: Option<f64>,
        elapsed_seconds_delta: Option<f64>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| {
            c.save_reading_progress(
                chapter_id,
                mode,
                page_id,
                scroll_offset_y,
                elapsed_seconds_delta,
            )
        })
    }

    fn start_run(
        &self,
        command: &str,
        scope: &serde_json::Value,
        overrides: Option<&serde_json::Value>,
        idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.start_run(command, scope, overrides, idempotency_key))
    }

    fn control_run(
        &self,
        run_id: &str,
        action: &str,
        idempotency_key: Option<&str>,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.control_run(run_id, action, idempotency_key))
    }

    fn resume_blocked_run(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.resume_blocked_run(run_id))
    }

    fn get_run_snapshot(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.get_run_snapshot(run_id))
    }

    fn get_task_projection(&self, run_id: &str) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.get_task_projection(run_id))
    }

    fn retry_failed_targets(
        &self,
        run_id: &str,
        idempotency_key: &str,
    ) -> Result<serde_json::Value, LibraryError> {
        self.with_channel(|c| c.retry_failed_targets(run_id, idempotency_key))
    }

    fn import_from_path(
        &self,
        path: &Path,
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        self.with_channel(|c| c.import_from_path(path, source_kind, chapter_id, duplicate_policy))
    }

    fn import_from_paths(
        &self,
        paths: &[PathBuf],
        source_kind: &str,
        chapter_id: &str,
        duplicate_policy: Option<&str>,
    ) -> Result<crate::host_issuer::ImportSummary, LibraryError> {
        self.with_channel(|c| c.import_from_paths(paths, source_kind, chapter_id, duplicate_policy))
    }

    fn start_export_to_path(
        &self,
        path: &Path,
        request: Value,
    ) -> Result<crate::host_issuer::ExportSummary, LibraryError> {
        self.with_channel(|c| c.start_export_to_path(path, request))
    }

    fn export_output_directory(&self, export_id: &str) -> Result<PathBuf, LibraryError> {
        self.with_channel(|c| c.export_output_directory(export_id))
    }

    fn set_event_sink(&self, sink: EventSink) {
        if let Ok(mut guard) = self.ctx.event_sink.lock() {
            *guard = Some(Arc::clone(&sink));
        }
        if let Ok(guard) = self.ctx.inner.lock() {
            if let Some(ref chan) = *guard {
                chan.set_event_sink(sink);
            }
        }
    }

    fn set_status_emitter(&self, emitter: StatusEmitter) {
        if self.ctx.is_fatal.load(Ordering::SeqCst) {
            emitter("fatal", "后端服务异常，自动重启失败，请检查服务日志");
        } else if self.ctx.is_restarting.load(Ordering::SeqCst) {
            emitter("restarting", "后端服务异常，正在尝试热重启...");
        }
        if let Ok(mut guard) = self.ctx.status_emitter.lock() {
            *guard = Some(emitter);
        }
    }

    fn trigger_restart(&self) {
        self.ctx.trigger_restart();
    }

    fn is_unhealthy(&self) -> bool {
        self.ctx.is_unhealthy()
    }

    fn cancel_export(&self, export_id: &str) -> Result<ExportProgressSnapshotView, LibraryError> {
        self.with_channel(|c| c.cancel_export(export_id))
    }

    fn get_export_snapshot(
        &self,
        export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
        self.with_channel(|c| c.get_export_snapshot(export_id))
    }

    fn get_export_history(&self) -> Result<ExportHistoryResponseView, LibraryError> {
        self.with_channel(|c| c.get_export_history())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn create_results_are_rebuilt_from_the_contract_whitelist() {
        let book = parse_created_book(serde_json::json!({
            "book_id": "book-1",
            "title": "Book",
            "original_title": "",
            "is_favorite": false,
            "is_archived": false,
            "page_count": null,
            "created_at": "2026-10-17T00:00:00Z",
            "updated_at": "2026-10-17T00:00:00Z",
            "path": "C:/private/library.db",
            "secret": "secret-marker",
            "traceback": "private exception"
        }))
        .unwrap();
        let book = serde_json::to_value(book).unwrap();
        assert_eq!(book.as_object().unwrap().len(), 8);
        assert_eq!(book["book_id"], "book-1");
        assert!(!book.to_string().contains("private"));
        assert!(!book.to_string().contains("secret-marker"));

        let chapter = parse_created_chapter(serde_json::json!({
            "chapter_id": "chapter-1",
            "title": "Chapter",
            "chapter_number": "",
            "sort_order": 0,
            "path": "C:/private/library.db",
            "secret": "secret-marker"
        }))
        .unwrap();
        let chapter = serde_json::to_value(chapter).unwrap();
        assert_eq!(chapter.as_object().unwrap().len(), 4);
        assert_eq!(chapter["chapter_id"], "chapter-1");
        assert!(!chapter.to_string().contains("private"));
        assert!(!chapter.to_string().contains("secret-marker"));
    }

    #[test]
    fn p15_commands_map_to_the_frozen_core_surface_at_minor_seven() {
        let commands = [
            P15SettingsCommand::ProviderProfilesList,
            P15SettingsCommand::ProviderProfilesCreate,
            P15SettingsCommand::ProviderProfilesUpdate,
            P15SettingsCommand::ProviderProfilesDelete,
            P15SettingsCommand::ProviderBindingsSet,
            P15SettingsCommand::ProviderBindingsClear,
            P15SettingsCommand::ProviderBindingsResolve,
            P15SettingsCommand::ProviderRunSnapshotGet,
            P15SettingsCommand::NetworkProfilesList,
            P15SettingsCommand::NetworkProfilesCreate,
            P15SettingsCommand::NetworkProfilesUpdate,
            P15SettingsCommand::NetworkProfilesDelete,
            P15SettingsCommand::NetworkProfilesTest,
            P15SettingsCommand::NetworkProfileDefaultSet,
            P15SettingsCommand::NetworkProfileDefaultClear,
            P15SettingsCommand::NetworkProfileResolve,
            P15SettingsCommand::ResolveOverrides,
        ];
        let expected = [
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
        ];
        let mapped: Vec<_> = commands
            .into_iter()
            .map(P15SettingsCommand::core_name)
            .collect();
        assert_eq!(mapped, expected);

        let envelope = build_application_envelope_at_minor(
            "p15-test",
            P15_BIND_PROFILE_CREDENTIAL,
            serde_json::json!({
                "target": {"kind": "provider_api", "profile_id": "p-1"},
                "credential_ref": "private-ref"
            }),
            7,
        );
        assert_eq!(
            envelope["version"],
            serde_json::json!({"major": 2, "minor": 7})
        );
        assert!(envelope.get("channel").is_none());
        assert!(!mapped
            .iter()
            .any(|command| P15_HOST_ONLY_COMMANDS.contains(command)));
    }

    #[test]
    fn reader_progress_payload_omits_missing_optional_values() {
        assert_eq!(
            reader_progress_payload("chapter", "original", "page", None, None),
            serde_json::json!({
                "chapter_id": "chapter",
                "mode": "original",
                "page_id": "page",
            })
        );
        assert_eq!(
            reader_progress_payload("chapter", "original", "page", Some(12.0), Some(3.0),),
            serde_json::json!({
                "chapter_id": "chapter",
                "mode": "original",
                "page_id": "page",
                "scroll_offset_y": 12.0,
                "elapsed_seconds_delta": 3.0,
            })
        );
    }

    #[test]
    fn spawn_args_target_core_service_module() {
        assert_eq!(
            spawn_args(),
            vec!["-m", "bootstrap.core_service"],
            "StdioLibraryChannel must spawn bootstrap.core_service"
        );
    }

    #[test]
    fn export_reveal_rejects_unknown_and_foreign_session_ids() {
        let current_session_ids = HashSet::from(["current-export".to_string()]);
        for id in ["unknown-export", "older-core-export"] {
            let error = require_current_session_export(id, &current_session_ids).unwrap_err();
            assert_eq!(error.code, "EXPORT_NOT_FOUND");
            assert_eq!(error.category, "not_found");
        }
    }

    #[test]
    fn export_reveal_waits_for_completed_output_and_rejects_unavailable_paths() {
        let current = HashSet::from(["export-1".to_string()]);
        let running = serde_json::json!({
            "exports": [{ "export_id": "export-1", "status": "running", "output_path": "C:/out/export.pdf" }]
        });
        let error = resolve_export_output_directory("export-1", running).unwrap_err();
        assert_eq!(error.code, "EXPORT_OUTPUT_NOT_READY");
        assert_eq!(error.category, "conflict");

        let unavailable = serde_json::json!({
            "exports": [{ "export_id": "export-1", "status": "completed", "output_path": "C:/missing/export.pdf" }]
        });
        let error = resolve_export_output_directory("export-1", unavailable).unwrap_err();
        assert_eq!(error.code, "EXPORT_PATH_UNAVAILABLE");
        assert_eq!(error.category, "unavailable");
        assert!(require_current_session_export("export-1", &current).is_ok());
    }

    #[test]
    fn export_reveal_resolves_only_the_existing_completed_output_directory() {
        let temp = tempfile::tempdir().unwrap();
        let directory = temp.path().join("exports");
        std::fs::create_dir(&directory).unwrap();
        let output = directory.join("book.cbz");
        std::fs::write(&output, b"export").unwrap();
        let history = serde_json::json!({
            "exports": [{
                "export_id": "export-1",
                "status": "completed",
                "output_path": output.to_str().unwrap()
            }]
        });
        let expected = directory.canonicalize().unwrap();
        for _ in 0..2 {
            assert_eq!(
                resolve_export_output_directory("export-1", history.clone()).unwrap(),
                expected
            );
        }
    }

    #[test]
    fn decode_response_parses_success_and_error() {
        let success = r#"{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"1","result":{"status":"ready"},"error":null}"#;
        let res = decode_response(success).unwrap();
        assert_eq!(res.get("status").and_then(|s| s.as_str()), Some("ready"));

        let err_json = r#"{"protocol":"new-manga.core","version":{"major":1,"minor":0},"request_id":"1","result":null,"error":{"code":"PROTOCOL_VERSION_UNSUPPORTED","category":"validation","retryable":false,"message":"Unsupported"}}"#;
        let err = decode_response(err_json).unwrap_err();
        assert_eq!(err.code, "PROTOCOL_VERSION_UNSUPPORTED");
        assert_eq!(err.category, "validation");
        assert_eq!(err.retryable, false);
        assert_eq!(err.message.as_deref(), Some("Unsupported"));
    }

    #[test]
    fn host_control_envelope_is_separate_and_bound_to_both_sessions() {
        let open = build_host_control_envelope(
            "hostctl-open",
            "OpenHostSession",
            serde_json::json!({"host_session_id":"host-id","host_session_credential":"credential"}),
            None,
        );
        assert_eq!(open["version"], serde_json::json!({"major":2,"minor":3}));
        assert_eq!(open["channel"], "host-control");
        assert!(open.get("core_session_id").is_none());

        let session = HostSession {
            host_session_id: "host-id".into(),
            credential: "credential".into(),
            core_session_id: "core-id".into(),
            signing_key: [7; 32],
        };
        let register = build_host_control_envelope(
            "hostctl-register",
            "RegisterImportSource",
            serde_json::json!({"grant_id":"grant-id"}),
            Some(&session),
        );
        assert_eq!(register["channel"], "host-control");
        assert_eq!(register["core_session_id"], "core-id");
        assert_eq!(register["host_session_id"], "host-id");
        assert_eq!(register["host_session_credential"], "credential");
        assert!(register.get("signing_key").is_none());

        let ordinary =
            build_application_envelope("req-ordinary", "OpenHostSession", serde_json::json!({}));
        assert_eq!(
            ordinary["version"],
            serde_json::json!({"major":2,"minor":3})
        );
        assert!(ordinary.get("channel").is_none());
    }

    #[test]
    fn host_control_denial_codes_are_preserved_for_host_handling() {
        for code in [
            "HOST_ONLY_REQUIRED",
            "HOST_SESSION_INVALID",
            "CORE_SESSION_MISMATCH",
        ] {
            let category = if code == "HOST_ONLY_REQUIRED" {
                "validation"
            } else {
                "conflict"
            };
            let response = serde_json::json!({
                "protocol":"new-manga.core",
                "version":{"major":2,"minor":3},
                "request_id":"hostctl-test",
                "result":null,
                "error":{"code":code,"category":category,"retryable":false,"message":"rejected"}
            });
            let error = decode_response(&response.to_string()).unwrap_err();
            assert_eq!(error.code, code);
            assert_eq!(error.category, category);
        }
    }

    #[test]
    fn mock_channel_round_trip() {
        let channel = MockLibraryChannel::new();
        let ping = channel.ping().expect("ping succeeds");
        assert_eq!(ping.status, "ready");
        assert_eq!(ping.capabilities, vec!["library.list_books"]);

        let books = channel.list_books().expect("empty list succeeds");
        assert!(books.is_empty());

        channel.set_books(vec![BookSummary {
            book_id: "book-1".to_string(),
            title: "Test Book".to_string(),
            original_title: "Orig".to_string(),
            is_favorite: true,
            is_archived: false,
            page_count: Some(5),
            created_at: "2026-09-28T00:00:00Z".to_string(),
            updated_at: "2026-09-28T00:00:00Z".to_string(),
        }]);

        let loaded = channel.list_books().unwrap();
        assert_eq!(loaded.len(), 1);
        assert_eq!(loaded[0].book_id, "book-1");
        assert_eq!(loaded[0].page_count, Some(5));

        channel.set_books_error(LibraryError::unavailable("connection lost"));
        let err = channel.list_books().unwrap_err();
        assert_eq!(err.code, "CORE_UNAVAILABLE");
        assert_eq!(err.retryable, true);
    }

    #[test]
    fn book_summary_page_count_known_zero_and_null_are_distinguishable() {
        // M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN AC2: the frozen None channel must
        // keep a KNOWN 0 expressible -- the serialized wire forms of a known 0
        // and an unknown page_count must never conflate (0 != null).
        let summary = |page_count: Option<u32>| BookSummary {
            book_id: "book-1".to_string(),
            title: "T".to_string(),
            original_title: "O".to_string(),
            is_favorite: false,
            is_archived: false,
            page_count,
            created_at: "2026-09-28T00:00:00Z".to_string(),
            updated_at: "2026-09-28T00:00:00Z".to_string(),
        };

        let zero_json = serde_json::to_string(&summary(Some(0))).unwrap();
        let null_json = serde_json::to_string(&summary(None)).unwrap();
        assert!(
            zero_json.contains(r#""page_count":0"#),
            "a known 0 must serialize as the JSON number 0, got: {zero_json}"
        );
        assert!(
            null_json.contains(r#""page_count":null"#),
            "an unknown page_count must serialize as JSON null, got: {null_json}"
        );
        assert_ne!(zero_json, null_json);

        let zero_back: BookSummary = serde_json::from_str(&zero_json).unwrap();
        let null_back: BookSummary = serde_json::from_str(&null_json).unwrap();
        assert_eq!(zero_back.page_count, Some(0));
        assert_eq!(null_back.page_count, None);
    }

    #[test]
    fn settings_mock_channel_round_trip_and_typed_rejection() {
        // M2-SETTINGS-IPC-CHANNEL: the host-level settings surface maps 1:1
        // onto the LibraryChannel methods. The mock is a single preset slot
        // (no write semantics — the REAL channel round-trips the Core, see
        // real_core_sidecar_settings_round_trip_and_typed_rejection); what
        // is pinned here is the projection shape and the typed
        // INVALID_REQUEST pass-through.
        let channel = MockLibraryChannel::new();
        let full = channel.get_settings(None).unwrap();
        assert_eq!(full["settings"], serde_json::json!({}));

        channel.set_settings_result(Ok(serde_json::json!(
            { "settings": { "sfx": { "policy": "translate" } } }
        )));
        let section = channel.get_settings(Some("sfx")).unwrap();
        assert_eq!(section["settings"]["sfx"]["policy"], "translate");
        // both methods surface the same preset slot
        let updated = channel
            .update_settings_section("sfx", &serde_json::json!({ "policy": "manual" }))
            .unwrap();
        assert_eq!(updated["settings"]["sfx"]["policy"], "translate");

        channel.set_settings_result(Err(LibraryError::new(
            "INVALID_REQUEST",
            "validation",
            false,
            Some("settings.update_section sfx.policy must be one of ..."),
        )));
        let err = channel
            .update_settings_section("sfx", &serde_json::json!({ "policy": "bogus" }))
            .unwrap_err();
        assert_eq!(err.code, "INVALID_REQUEST");
        assert_eq!(err.category, "validation");
        assert!(!err.retryable);
    }

    #[test]
    fn retype_mock_channel_round_trip_and_typed_rejection() {
        // M2-REGION-RETYPE-CORE: the host-level retype surface maps 1:1 onto
        // the LibraryChannel methods (same discipline as the settings mock —
        // the REAL channel round-trips the Core). What is pinned here is the
        // post-retype effective-state shape and the typed pass-through of
        // the reused error codes (contract rev 1.4 §5.4).
        let channel = MockLibraryChannel::new();

        let retyped = channel
            .set_region_type("r1", "sfx", Some(1))
            .expect("retype succeeds");
        assert_eq!(retyped["region_id"], "r1");
        assert_eq!(retyped["revision_no"], 2);
        assert_eq!(retyped["region_type"], "sfx");
        assert_eq!(retyped["sfx_policy"], "skip");

        let regions = channel.list_regions("page-1").unwrap();
        assert_eq!(regions["regions"], serde_json::json!([]));

        channel.set_retype_result(Err(LibraryError::new(
            "INPUT_REVISION_CHANGED",
            "conflict",
            false,
            Some("region revision changed since it was read"),
        )));
        let conflict = channel.set_region_type("r1", "sfx", Some(1)).unwrap_err();
        assert_eq!(conflict.code, "INPUT_REVISION_CHANGED");
        assert_eq!(conflict.category, "conflict");
        assert!(!conflict.retryable);

        channel.set_regions_result(Err(LibraryError::new(
            "INVALID_REQUEST",
            "validation",
            false,
            Some("list_regions requires 'page_id': a non-empty string"),
        )));
        let invalid = channel.list_regions("").unwrap_err();
        assert_eq!(invalid.code, "INVALID_REQUEST");
        assert_eq!(invalid.category, "validation");
    }

    #[test]
    fn page_resolve_mock_channel_round_trip_and_typed_rejection() {
        // M2-PAGE-RESOURCE-RESOLVE-1 (DSH r1 PR-01): the page display-image
        // resolve rides the same LibraryChannel seam as the settings/retype
        // surfaces. What is pinned here is the result projection shape
        // ({resource_id, revision}, snake_case, contract rev 1.7 §5) and
        // the typed PAGE_NOT_FOUND pass-through; the REAL stdio channel
        // round-trips the same wire name through bootstrap.core_service
        // (real_core_sidecar_round_trip_and_eof in main.rs asserts the
        // protocol minor this command bumped).
        let channel = MockLibraryChannel::new();
        channel.set_domain_result(Ok(serde_json::json!({
            "resource_id": "page-original-page-1",
            "revision": "original",
        })));
        let resolved = channel
            .resolve_page_resource("page-1")
            .expect("resolve succeeds");
        assert_eq!(resolved["resource_id"], "page-original-page-1");
        assert_eq!(resolved["revision"], "original");

        channel.set_domain_result(Err(LibraryError::new(
            "PAGE_NOT_FOUND",
            "not_found",
            false,
            Some("page or its managed original is not available"),
        )));
        let err = channel.resolve_page_resource("page-1").unwrap_err();
        assert_eq!(err.code, "PAGE_NOT_FOUND");
        assert_eq!(err.category, "not_found");
        assert!(!err.retryable);
    }

    #[test]
    fn page_nav_mock_channel_round_trip_and_typed_pass_through() {
        // M2-PAGE-NAV-PROJECTION-1 (DSH r1 PR-01 precedent): the read-only
        // navigation projections ride the same LibraryChannel seam. What is
        // pinned here is the wrapper-envelope projection shape and the
        // typed pass-through discipline; the REAL stdio channel round-trips
        // the wire names through bootstrap.core_service (the real sidecar
        // round-trip test asserts the protocol minor this command pair
        // bumps).
        let channel = MockLibraryChannel::new();
        channel.set_domain_result(Ok(serde_json::json!({
            "chapters": [
                { "chapter_id": "c1", "title": "first", "chapter_number": "1", "sort_order": 1 },
                { "chapter_id": "c2", "title": "second", "chapter_number": "2", "sort_order": 2 }
            ],
        })));
        let chapters = channel
            .list_chapters("book-1")
            .expect("list_chapters succeeds");
        assert_eq!(chapters["chapters"][0]["chapter_id"], "c1");
        assert_eq!(chapters["chapters"][1]["sort_order"], 2);

        channel.set_domain_result(Ok(serde_json::json!({
            "pages": [
                { "page_id": "p1", "source_filename": "page-a.png", "sort_order": 0 },
                { "page_id": "p2", "source_filename": "page-b.png", "sort_order": 1 }
            ],
        })));
        let pages = channel
            .list_chapter_pages("chapter-1")
            .expect("list_chapter_pages succeeds");
        assert_eq!(pages["pages"][0]["page_id"], "p1");
        assert_eq!(pages["pages"][1]["source_filename"], "page-b.png");

        // DSH r1 PR-01: the "typed pass-through" half of this test's claim
        // needs an actual Err branch assertion, like the page-resolve
        // precedent above. The Mock forwards the LibraryError verbatim.
        channel.set_domain_result(Err(LibraryError::new(
            "INVALID_REQUEST",
            "validation",
            false,
            Some("list_chapters requires 'book_id': a non-empty string"),
        )));
        let err = channel.list_chapters("book-1").unwrap_err();
        assert_eq!(err.code, "INVALID_REQUEST");
        assert_eq!(err.category, "validation");
        assert!(!err.retryable);
    }

    #[test]
    fn wait_timeout_or_kill_terminates_hanging_process() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let mut child = Command::new(&python)
            .args(&["-c", "import time; time.sleep(10)"])
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn hanging process");

        let start = std::time::Instant::now();
        let status = wait_timeout_or_kill(&mut child, std::time::Duration::from_millis(150))
            .expect("wait_timeout_or_kill succeeds");

        assert!(start.elapsed() < std::time::Duration::from_secs(3));
        assert!(!status.success());
    }

    /// M2-DERIVED-GC-2 G3: the startup-ping deadline stops and reaps THIS
    /// child, the reader worker is joined (no leaked read lock), and the
    /// failure verdict returns well inside the 5 s Drop shutdown budget.
    #[test]
    fn startup_ping_deadline_kills_own_child_and_joins_worker() {
        let python = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".into());
        let child = Command::new(&python)
            .args(&["-c", "import time,sys; time.sleep(60)"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn silent child");
        let channel = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt child");

        let start = std::time::Instant::now();
        let answered = channel.wait_first_ping(std::time::Duration::from_millis(400));
        let elapsed = start.elapsed();

        assert!(!answered, "a silent child must not answer the startup ping");
        assert!(
            elapsed < std::time::Duration::from_secs(3),
            "deadline path must not block past the deadline: {elapsed:?}"
        );
        {
            let mut child = channel.child.lock().unwrap();
            assert!(
                child.try_wait().expect("reap status").is_some(),
                "the deadline path must have reaped the own child"
            );
        }
        // The channel is deliberately dropped here (the Err branch of
        // spawn_with_startup_ping): its Drop must not hang on the
        // already-reaped child nor wait a second shutdown budget.
        drop(channel);
    }

    /// M2-DERIVED-GC-2 G3: the happy path -- a REAL production core sidecar
    /// (fresh catalog: the Core performs the controlled namespace
    /// first-bind, the GC window, then answers ping) is delivered only
    /// after the startup ping round-trips.
    #[test]
    fn real_core_sidecar_answers_startup_ping_on_fresh_catalog() {
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
        let catalog_db = dir.path().join("catalog.sqlite");

        let channel = StdioLibraryChannel::spawn_with_startup_ping(
            &python,
            &src_root,
            Some(&dir.path().join("data")),
            Some(&derived),
            Some(&catalog_db),
            std::time::Duration::from_secs(30),
        )
        .expect("fresh-catalog core answers the startup ping");
        let ping = channel.ping().expect("post-startup ping");
        assert_eq!(ping.status, "ready");
        assert!(catalog_db.is_file(), "the core bound the fresh catalog");
    }

    /// Regression test for P22 AC2 (concurrent round_trip response ownership).
    /// Asserts that concurrent callers on the same StdioLibraryChannel instance
    /// receive their own responses deterministically under the per-channel transaction lock.
    #[test]
    fn same_channel_concurrent_round_trips_keep_response_ownership() {
        use std::sync::atomic::AtomicBool;
        use std::sync::mpsc;
        use std::sync::Arc;

        fn recv_bounded<T>(rx: &mpsc::Receiver<T>, timeout: std::time::Duration, phase: &str) -> T {
            rx.recv_timeout(timeout).unwrap_or_else(|err| match err {
                mpsc::RecvTimeoutError::Timeout => {
                    panic!("bounded wait timed out after {timeout:?} waiting for {phase}");
                }
                mpsc::RecvTimeoutError::Disconnected => {
                    panic!("coordination channel disconnected (sender dropped or panicked) waiting for {phase}");
                }
            })
        }

        let python = std::env::var("M2RC1_PYTHON").expect(
            "M2RC1_PYTHON must be explicitly set to P02-approved Python environment for testing",
        );

        let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let mut repo_root = manifest_dir.clone();
        for _ in 0..3 {
            repo_root.pop();
        }

        let p22_rebase_script = repo_root
            .join("verification")
            .join("P22-REBASE-1")
            .join("deterministic_concurrent_sidecar.py");
        let script_path = if p22_rebase_script.is_file() {
            p22_rebase_script
        } else {
            repo_root
                .join("verification")
                .join("P04")
                .join("deterministic_concurrent_sidecar.py")
        };
        assert!(
            script_path.is_file(),
            "test sidecar missing at expected path: {}",
            script_path.display()
        );

        let run_id = format!(
            "diagnostic_p22_{}_{}.jsonl",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_millis())
                .unwrap_or(0)
        );
        let log_path = repo_root.join("verification").join("P04").join(run_id);

        let mut cmd = Command::new(&python);
        cmd.arg(&script_path);
        cmd.env("P04_DIAGNOSTIC_LOG", &log_path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit());

        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x0800_0000;
            cmd.creation_flags(CREATE_NO_WINDOW);
        }

        let child = cmd
            .spawn()
            .expect("deterministic concurrency test sidecar spawn failed");
        let channel = Arc::new(
            StdioLibraryChannel::adopt_child_for_test(child)
                .expect("adopt child process into StdioLibraryChannel failed"),
        );

        let req_alpha = serde_json::json!({
            "caller": "caller_alpha",
            "token": "token-AAA-111",
        });
        let req_beta = serde_json::json!({
            "caller": "caller_beta",
            "token": "token-BBB-222",
        });

        let (alpha_locked_tx, alpha_locked_rx) = mpsc::channel();
        let (beta_calling_tx, beta_calling_rx) = mpsc::channel();

        let alpha_finished_read = Arc::new(AtomicBool::new(false));
        let beta_acquired_lock = Arc::new(AtomicBool::new(false));

        let chan_alpha = Arc::clone(&channel);
        let payload_alpha = req_alpha.clone();
        let alpha_finished_read_alpha = Arc::clone(&alpha_finished_read);
        let beta_acquired_lock_alpha = Arc::clone(&beta_acquired_lock);
        let handle_alpha = std::thread::spawn(move || {
            let capture = Arc::new(std::sync::Mutex::new((String::new(), String::new())));
            let capture_clone = Arc::clone(&capture);

            set_test_after_transaction_lock_hook(Some(move |_req_id: &str| {
                alpha_locked_tx
                    .send(())
                    .expect("failed to signal that alpha acquired transaction lock");
                recv_bounded(
                    &beta_calling_rx,
                    std::time::Duration::from_secs(10),
                    "beta calling round_trip announcement",
                );
            }));

            set_test_before_transaction_unlock_hook(Some(move |_req_id: &str| {
                alpha_finished_read_alpha.store(true, Ordering::SeqCst);
                assert!(
                    !beta_acquired_lock_alpha.load(Ordering::SeqCst),
                    "Beta must not have acquired transaction lock before Alpha releases it"
                );
            }));

            set_test_response_observer(Some(move |req_id: &str, raw: &str| {
                let mut lock = capture_clone.lock().unwrap();
                lock.0 = req_id.to_string();
                lock.1 = raw.to_string();
            }));

            let res = chan_alpha.round_trip("test.concurrent_alpha", payload_alpha);

            let (captured_id, captured_raw) = {
                let lock = capture.lock().unwrap();
                (lock.0.clone(), lock.1.clone())
            };

            set_test_after_transaction_lock_hook::<fn(&str)>(None);
            set_test_before_transaction_unlock_hook::<fn(&str)>(None);
            set_test_response_observer::<fn(&str, &str)>(None);

            (res, captured_raw, captured_id)
        });

        let chan_beta = Arc::clone(&channel);
        let chan_beta_probe = Arc::clone(&channel);
        let payload_beta = req_beta.clone();
        let alpha_finished_read_beta = Arc::clone(&alpha_finished_read);
        let beta_acquired_lock_beta = Arc::clone(&beta_acquired_lock);
        let handle_beta = std::thread::spawn(move || {
            recv_bounded(
                &alpha_locked_rx,
                std::time::Duration::from_secs(10),
                "alpha transaction lock acquisition",
            );

            // Deterministic lock contention probe:
            // Alpha is held inside TEST_AFTER_TRANSACTION_LOCK_HOOK waiting on beta_calling_rx.
            // Alpha is guaranteed to be holding transaction_lock. Assert that Beta's try_lock observes WouldBlock.
            let probe_result = chan_beta_probe.transaction_lock.try_lock();
            assert!(
                matches!(probe_result, Err(std::sync::TryLockError::WouldBlock)),
                "Beta must observe Alpha holding transaction_lock (WouldBlock) before entering round_trip, got: {:?}",
                probe_result.map(|_| "Unlocked")
            );

            set_test_after_transaction_lock_hook(Some(move |_req_id: &str| {
                beta_acquired_lock_beta.store(true, Ordering::SeqCst);
                assert!(
                    alpha_finished_read_beta.load(Ordering::SeqCst),
                    "Beta must acquire transaction_lock only after Alpha has finished its transaction read"
                );
            }));

            let capture = Arc::new(std::sync::Mutex::new((String::new(), String::new())));
            let capture_clone = Arc::clone(&capture);

            set_test_response_observer(Some(move |req_id: &str, raw: &str| {
                let mut lock = capture_clone.lock().unwrap();
                lock.0 = req_id.to_string();
                lock.1 = raw.to_string();
            }));

            beta_calling_tx
                .send(())
                .expect("failed to signal that beta is calling round_trip");

            let res = chan_beta.round_trip("test.concurrent_beta", payload_beta);

            let (captured_id, captured_raw) = {
                let lock = capture.lock().unwrap();
                (lock.0.clone(), lock.1.clone())
            };

            set_test_after_transaction_lock_hook::<fn(&str)>(None);
            set_test_response_observer::<fn(&str, &str)>(None);

            (res, captured_raw, captured_id)
        });

        let (res_alpha, raw_alpha, id_alpha) =
            handle_alpha.join().expect("caller alpha thread panicked");
        let (res_beta, raw_beta, id_beta) =
            handle_beta.join().expect("caller beta thread panicked");

        let val_alpha = res_alpha.expect("round_trip alpha failed");
        let val_beta = res_beta.expect("round_trip beta failed");

        let alpha_owned = val_alpha.get("echo_caller").and_then(|v| v.as_str())
            == Some("caller_alpha")
            && val_alpha.get("echo_token").and_then(|v| v.as_str()) == Some("token-AAA-111");
        let beta_owned = val_beta.get("echo_caller").and_then(|v| v.as_str())
            == Some("caller_beta")
            && val_beta.get("echo_token").and_then(|v| v.as_str()) == Some("token-BBB-222");

        let behavior = if alpha_owned && beta_owned {
            "PASS"
        } else {
            "FAIL"
        };

        let verdict_record = serde_json::json!({
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs_f64())
                .unwrap_or(0.0),
            "behavior": behavior,
            "static_expected_behavior": "PASS",
            "alpha_request": req_alpha,
            "alpha_request_id": id_alpha,
            "alpha_raw_response": raw_alpha,
            "alpha_owned": alpha_owned,
            "beta_request": req_beta,
            "beta_request_id": id_beta,
            "beta_raw_response": raw_beta,
            "beta_owned": beta_owned,
            "interleaving": "deterministic_serialized_alpha_then_beta_under_transaction_lock",
        });

        if let Some(parent) = log_path.parent() {
            std::fs::create_dir_all(parent)
                .expect("failed to create parent directory for P22 diagnostic verdict log");
        }

        let mut file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&log_path)
            .expect("failed to open/create P22 diagnostic verdict log file");
        writeln!(file, "{}", verdict_record)
            .expect("failed to write concurrency verdict record to diagnostic log");

        eprintln!(
            "[P22-REGRESSION] Concurrency verdict: behavior={behavior}, alpha_owned={alpha_owned}, beta_owned={beta_owned}"
        );
        eprintln!("[P22-REGRESSION] Caller alpha raw response: {raw_alpha}");
        eprintln!("[P22-REGRESSION] Caller beta raw response: {raw_beta}");

        assert!(
            alpha_owned,
            "Caller alpha must receive its own echo (expected caller_alpha/token-AAA-111), got val_alpha={val_alpha:?}"
        );
        assert!(
            beta_owned,
            "Caller beta must receive its own echo (expected caller_beta/token-BBB-222), got val_beta={val_beta:?}"
        );
        assert_eq!(
            behavior, "PASS",
            "concurrency behavior verdict must be PASS"
        );
    }

    // ---- EVENTS-FWD-1 (rev 2.4 §6.4) tests --------------------------------

    #[test]
    fn test_events_fwd_all_six_frozen_events_projected() {
        // 1. TaskFailed
        let raw = serde_json::json!({
            "run_id": "run-01",
            "task_id": "task-01",
            "page_id": "p-01",
            "error_code": "OCR_FAIL",
            "internal_secret": "do_not_leak"
        });
        let (name, projected) = project_forwarded_event("TaskFailed", &raw).unwrap();
        assert_eq!(name, "core:TaskFailed");
        assert_eq!(projected["run_id"], "run-01");
        assert_eq!(projected["task_id"], "task-01");
        assert_eq!(projected["page_id"], "p-01");
        assert_eq!(projected["error_code"], "OCR_FAIL");
        assert!(projected.get("internal_secret").is_none());

        // 2. RunPaused
        let raw = serde_json::json!({
            "run_id": "run-02",
            "status": "paused"
        });
        let (name, projected) = project_forwarded_event("RunPaused", &raw).unwrap();
        assert_eq!(name, "core:RunPaused");
        assert_eq!(projected["run_id"], "run-02");
        assert_eq!(projected["status"], "paused");

        // 3. RunCompleted
        let raw = serde_json::json!({
            "run_id": "run-03",
            "status": "completed"
        });
        let (name, projected) = project_forwarded_event("RunCompleted", &raw).unwrap();
        assert_eq!(name, "core:RunCompleted");
        assert_eq!(projected["run_id"], "run-03");
        assert_eq!(projected["status"], "completed");

        // 4. CurrentPageStepChanged
        let raw = serde_json::json!({
            "run_id": "run-04",
            "current_page_id": "p-04",
            "current_step_type": "inpaint"
        });
        let (name, projected) = project_forwarded_event("CurrentPageStepChanged", &raw).unwrap();
        assert_eq!(name, "core:CurrentPageStepChanged");
        assert_eq!(projected["run_id"], "run-04");
        assert_eq!(projected["current_page_id"], "p-04");
        assert_eq!(projected["current_step_type"], "inpaint");

        // 5. ExportProgressChanged
        let raw = serde_json::json!({
            "export_id": "export-05",
            "status": "in_progress",
            "completed_pages": 10,
            "total_pages": 50
        });
        let (name, projected) = project_forwarded_event("ExportProgressChanged", &raw).unwrap();
        assert_eq!(name, "core:ExportProgressChanged");
        assert_eq!(projected["export_id"], "export-05");
        assert_eq!(projected["status"], "in_progress");
        assert_eq!(projected["completed_pages"], 10);
        assert_eq!(projected["total_pages"], 50);

        // 6. ReadingProgressChanged
        let raw = serde_json::json!({
            "book_id": "b-06",
            "chapter_id": "c-06",
            "mode": "original"
        });
        let (name, projected) = project_forwarded_event("ReadingProgressChanged", &raw).unwrap();
        assert_eq!(name, "core:ReadingProgressChanged");
        assert_eq!(projected["book_id"], "b-06");
        assert_eq!(projected["chapter_id"], "c-06");
        assert_eq!(projected["mode"], "original");
    }

    #[test]
    fn test_events_fwd_strips_forbidden_paths_and_opaque_references() {
        let raw_with_paths = serde_json::json!({
            "run_id": "run-leak-test",
            "status": "completed",
            "target_path": "C:\\Users\\sensitive\\export.zip",
            "file_path": "/var/data/books/01/page.png",
            "abs_path": "D:\\secret\\original.jpg",
            "target_ref": "m2targetref.v1.abc123456",
            "opaque_id": "m2id.v1.xyz987654",
            "signing_key": "supersecretkey",
            "file_bytes": "AQIDBA=="
        });

        let (_, projected) = project_forwarded_event("RunCompleted", &raw_with_paths).unwrap();
        assert_eq!(projected["run_id"], "run-leak-test");
        assert_eq!(projected["status"], "completed");
        assert!(projected.get("target_path").is_none());
        assert!(projected.get("file_path").is_none());
        assert!(projected.get("abs_path").is_none());
        assert!(projected.get("target_ref").is_none());
        assert!(projected.get("opaque_id").is_none());
        assert!(projected.get("signing_key").is_none());
        assert!(projected.get("file_bytes").is_none());
    }

    #[test]
    fn test_events_fwd_fail_closed_on_unfrozen_events() {
        // G16 gap: CoreAvailabilityChanged is UNKNOWN/PROPOSAL - strictly excluded
        let raw = serde_json::json!({
            "status": "connected",
            "service": "core"
        });
        assert!(project_forwarded_event("CoreAvailabilityChanged", &raw).is_none());

        // G26 gap: ImportProgressChanged is PROPOSAL - strictly excluded
        let raw_import = serde_json::json!({
            "task_id": "imp-1",
            "current": 2,
            "total": 10
        });
        assert!(project_forwarded_event("ImportProgressChanged", &raw_import).is_none());

        // Arbitrary unknown event
        assert!(project_forwarded_event("SomeUnknownEvent", &raw).is_none());
    }

    #[test]
    fn test_events_fwd_dispatch_stdout_line_interleaved_with_responses() {
        let event_sink: Arc<Mutex<Option<EventSink>>> = Arc::new(Mutex::new(None));
        let pending: Arc<Mutex<HashMap<String, SyncSender<Result<String, LibraryError>>>>> =
            Arc::new(Mutex::new(HashMap::new()));

        let captured_events = Arc::new(Mutex::new(Vec::<(String, serde_json::Value)>::new()));
        let captured_clone = Arc::clone(&captured_events);
        *event_sink.lock().unwrap() = Some(Arc::new(move |name, payload| {
            captured_clone
                .lock()
                .unwrap()
                .push((name.to_string(), payload));
        }));

        // Register two pending callers
        let (tx1, rx1) = std::sync::mpsc::sync_channel(1);
        let (tx2, rx2) = std::sync::mpsc::sync_channel(1);
        pending.lock().unwrap().insert("req-101".to_string(), tx1);
        pending.lock().unwrap().insert("req-102".to_string(), tx2);

        // 1. Core emits an event (RunPaused)
        let event_line = r#"{"protocol":"new-manga.core","version":{"major":2,"minor":3},"event_id":"ev-1","event_type":"RunPaused","emitted_at":"2026-10-16T10:00:00Z","payload":{"run_id":"run-A","status":"paused"}}"#;
        dispatch_stdout_line(event_line, &event_sink, &pending);

        // 2. Core emits response for req-102
        let resp_102 = r#"{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-102","result":{"ok":true},"error":null}"#;
        dispatch_stdout_line(resp_102, &event_sink, &pending);

        // 3. Core emits an unfrozen/unsupported event (should be ignored)
        let ignored_event = r#"{"protocol":"new-manga.core","version":{"major":2,"minor":3},"event_id":"ev-2","event_type":"CoreAvailabilityChanged","emitted_at":"2026-10-16T10:00:01Z","payload":{"status":"degraded"}}"#;
        dispatch_stdout_line(ignored_event, &event_sink, &pending);

        // 4. Core emits another event (RunCompleted)
        let event_line_2 = r#"{"protocol":"new-manga.core","version":{"major":2,"minor":3},"event_id":"ev-3","event_type":"RunCompleted","emitted_at":"2026-10-16T10:00:02Z","payload":{"run_id":"run-B","status":"completed"}}"#;
        dispatch_stdout_line(event_line_2, &event_sink, &pending);

        // 5. Core emits response for req-101
        let resp_101 = r#"{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-101","result":{"data":123},"error":null}"#;
        dispatch_stdout_line(resp_101, &event_sink, &pending);

        // Verify that responses arrived to the right recipients without deadlock or mixing
        let got_102 = rx2
            .recv_timeout(Duration::from_millis(200))
            .unwrap()
            .unwrap();
        assert!(got_102.contains("\"request_id\":\"req-102\""));

        let got_101 = rx1
            .recv_timeout(Duration::from_millis(200))
            .unwrap()
            .unwrap();
        assert!(got_101.contains("\"request_id\":\"req-101\""));

        // Verify that only the 2 frozen events were dispatched
        let events = captured_events.lock().unwrap();
        assert_eq!(events.len(), 2);
        assert_eq!(events[0].0, "core:RunPaused");
        assert_eq!(events[0].1["run_id"], "run-A");
        assert_eq!(events[0].1["status"], "paused");
        assert_eq!(events[1].0, "core:RunCompleted");
        assert_eq!(events[1].1["run_id"], "run-B");
        assert_eq!(events[1].1["status"], "completed");
    }

    #[test]
    fn test_project_export_snapshot_whitelist_zero_path() {
        let raw_core_snapshot = serde_json::json!({
            "export_id": "exp-test-001",
            "status": "completed",
            "completed_pages": 5,
            "total_pages": 5,
            "current_page_id": serde_json::Value::Null,
            "accepted_at": "2026-10-16T12:00:00Z",
            "completed_at": "2026-10-16T12:01:00Z",
            "output_path": "C:\\Users\\User\\AppData\\Local\\secret\\exported.zip",
            "target_path_internal": "C:\\Users\\User\\AppData\\Local\\secret\\exported.zip",
            "grant_id": "grant_secret_999",
            "output": {
                "format": "zip",
                "output_path": "C:\\Users\\User\\AppData\\Local\\secret\\exported.zip",
                "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            },
            "lineage": [
                {
                    "page_id": "p-1",
                    "order": 1,
                    "source_artifact_id": "art-1",
                    "source_artifact_revision_id": "rev-1",
                    "source_sha256": "hash-1",
                    "rendered_from_revision_id": "rend-1",
                    "current_source_revision_id": "cur-1",
                    "source_run_id": "run-1",
                    "stale": false,
                    "internal_file_path": "C:\\Users\\User\\AppData\\Local\\page1.png"
                }
            ],
            "error_code": serde_json::Value::Null
        });

        let view =
            project_export_snapshot(raw_core_snapshot).expect("project snapshot must succeed");
        assert_eq!(view.export_id, "exp-test-001");
        assert_eq!(view.status, "completed");
        assert_eq!(view.completed_pages, 5);
        assert_eq!(view.total_pages, 5);
        assert_eq!(view.output.as_ref().unwrap().format, "zip");
        assert_eq!(
            view.output.as_ref().unwrap().sha256.as_deref(),
            Some("abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        );
        assert_eq!(view.lineage.len(), 1);
        assert_eq!(view.lineage[0].page_id, "p-1");

        // Serialize to JSON and assert zero path / zero secret leakage
        let serialized = serde_json::to_string(&view).expect("must serialize");
        assert!(
            !serialized.contains("output_path"),
            "must not contain output_path"
        );
        assert!(
            !serialized.contains("target_path"),
            "must not contain target_path"
        );
        assert!(
            !serialized.contains("internal_file_path"),
            "must not contain internal_file_path"
        );
        assert!(
            !serialized.contains("grant_secret"),
            "must not contain grant_id"
        );
        assert!(
            !serialized.contains("C:\\"),
            "must not contain Windows drive path"
        );
        assert!(
            !serialized.contains("secret"),
            "must not contain private path components"
        );
    }

    #[test]
    fn test_project_export_history_whitelist_zero_path() {
        let raw_core_history = serde_json::json!({
            "exports": [
                {
                    "export_id": "exp-hist-001",
                    "book_id": "book-1",
                    "chapter_ids": ["ch-1"],
                    "ordered_page_ids": ["p-1", "p-2"],
                    "format": "pdf",
                    "format_options": { "dpi": 300 },
                    "created_at": "2026-10-16T12:00:00Z",
                    "completed_at": "2026-10-16T12:01:00Z",
                    "status": "completed",
                    "sha256": "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
                    "output_path": "D:\\Private\\Manga\\Exports\\book.pdf",
                    "stale_policy": "abort",
                    "target_ref": { "grant_id": "grant-sec-888" },
                    "lineage": [
                        {
                            "page_id": "p-1",
                            "order": 0,
                            "source_sha256": "hash-0"
                        }
                    ]
                }
            ]
        });

        let view = project_export_history(raw_core_history).expect("project history must succeed");
        assert_eq!(view.exports.len(), 1);
        assert_eq!(view.exports[0].export_id, "exp-hist-001");
        assert_eq!(view.exports[0].format, "pdf");

        // Serialize to JSON and assert zero path / zero target_ref leakage
        let serialized = serde_json::to_string(&view).expect("must serialize");
        assert!(
            !serialized.contains("output_path"),
            "must not contain output_path"
        );
        assert!(
            !serialized.contains("stale_policy"),
            "must not contain stale_policy"
        );
        assert!(
            !serialized.contains("target_ref"),
            "must not contain target_ref"
        );
        assert!(
            !serialized.contains("grant-sec"),
            "must not contain grant credentials"
        );
        assert!(
            !serialized.contains("D:\\"),
            "must not contain Windows drive path"
        );
        assert!(
            !serialized.contains("Private"),
            "must not contain private path components"
        );
    }

    #[test]
    fn test_project_export_history_empty_cases() {
        let empty_exports = serde_json::json!({ "exports": [] });
        let view1 = project_export_history(empty_exports).expect("empty exports array succeeds");
        assert!(view1.exports.is_empty());

        let empty_obj = serde_json::json!({});
        let view2 = project_export_history(empty_obj).expect("empty object succeeds without error");
        assert!(view2.exports.is_empty());
    }

    #[test]
    fn test_mock_channel_export_methods() {
        let mock = MockLibraryChannel::new();
        let snap = mock.get_export_snapshot("exp-1").unwrap();
        assert_eq!(snap.export_id, "exp-mock-1");
        let cancel = mock.cancel_export("exp-1").unwrap();
        assert_eq!(cancel.export_id, "exp-mock-1");
        let hist = mock.get_export_history().unwrap();
        assert!(hist.exports.is_empty());

        // Error injection
        mock.set_export_snapshot_result(Err(LibraryError::new(
            "EXPORT_NOT_FOUND",
            "not_found",
            false,
            Some("export not found at C:\\secret\\path"),
        )));
        let err = mock.get_export_snapshot("exp-unknown").unwrap_err();
        assert_eq!(err.code, "EXPORT_NOT_FOUND");

        // History mock injection
        mock.set_export_history_result(Ok(ExportHistoryResponseView {
            exports: vec![ExportHistoryEntryView {
                export_id: "exp-hist-mock".to_string(),
                book_id: "b-1".to_string(),
                chapter_ids: vec![],
                ordered_page_ids: vec![],
                format: "cbz".to_string(),
                format_options: serde_json::json!({}),
                created_at: "2026-10-16T12:00:00Z".to_string(),
                completed_at: None,
                status: "running".to_string(),
                sha256: None,
                lineage: vec![],
            }],
        }));
        let hist2 = mock.get_export_history().unwrap();
        assert_eq!(hist2.exports.len(), 1);
        assert_eq!(hist2.exports[0].export_id, "exp-hist-mock");
    }

    #[test]
    fn resilient_channel_triggers_restart_and_emits_restarting_status() {
        let events = Arc::new(Mutex::new(Vec::<(String, String)>::new()));
        let events_clone = Arc::clone(&events);

        let config = LibrarySpawnConfig::new(
            "non_existent_executable".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );

        let ctx = Arc::new(ResilientCoreContext {
            inner: Mutex::new(None),
            config,
            is_restarting: AtomicBool::new(false),
            consecutive_failures: AtomicU32::new(0),
            last_spawn_time: Mutex::new(None),
            is_fatal: AtomicBool::new(false),
            event_sink: Mutex::new(None),
            status_emitter: Mutex::new(Some(Arc::new(move |status, msg| {
                events_clone.lock().unwrap().push((status.to_string(), msg.to_string()));
            }))),
            heartbeat_stop: AtomicBool::new(false),
        });

        // Trigger restart
        ctx.trigger_restart();

        // Immediately verify "restarting" status was emitted
        let emitted = events.lock().unwrap();
        assert!(!emitted.is_empty(), "Status must be emitted immediately upon restart trigger");
        assert_eq!(emitted[0].0, "restarting");
        assert!(emitted[0].1.contains("后端服务异常"));
    }

    #[test]
    fn resilient_channel_caps_retries_and_emits_fatal_after_three_failures() {
        let events = Arc::new(Mutex::new(Vec::<(String, String)>::new()));
        let events_clone = Arc::clone(&events);

        let config = LibrarySpawnConfig::new(
            "non_existent_executable".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );

        let ctx = Arc::new(ResilientCoreContext {
            inner: Mutex::new(None),
            config,
            is_restarting: AtomicBool::new(false),
            consecutive_failures: AtomicU32::new(3), // Already reached MAX_RETRIES
            last_spawn_time: Mutex::new(None),
            is_fatal: AtomicBool::new(false),
            event_sink: Mutex::new(None),
            status_emitter: Mutex::new(Some(Arc::new(move |status, msg| {
                events_clone.lock().unwrap().push((status.to_string(), msg.to_string()));
            }))),
            heartbeat_stop: AtomicBool::new(false),
        });

        // Trigger restart when consecutive_failures >= 3
        ctx.trigger_restart();

        let emitted = events.lock().unwrap();
        assert_eq!(emitted.len(), 1);
        assert_eq!(emitted[0].0, "fatal");
        assert!(emitted[0].1.contains("自动重启失败"));
    }

    /// R-001 verification: Simulate a "successful spawn -> rapid exit" loop.
    /// Asserts that rapid exits within stable_duration do NOT reset the failure counter,
    /// so the restart attempts are strictly capped at MAX_RETRIES (3) and transition to fatal,
    /// completely preventing infinite restart loops.
    #[test]
    fn resilient_channel_crash_loop_is_bounded_and_reaches_fatal() {
        let events = Arc::new(Mutex::new(Vec::<(String, String)>::new()));
        let events_clone = Arc::clone(&events);
        let spawn_counter = Arc::new(AtomicU32::new(0));
        let counter_clone = Arc::clone(&spawn_counter);

        let mut config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );
        config.initial_backoff = Duration::from_millis(10);
        config.stable_duration = Duration::from_secs(30);

        config.custom_spawner = Some(Arc::new(move |_cfg| {
            counter_clone.fetch_add(1, Ordering::SeqCst);
            // Spawn a real child that exits immediately, closing stdout (EOF)
            let child = Command::new("cmd")
                .args(["/c", "exit 0"])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null())
                .spawn()
                .expect("spawn short-lived child");
            StdioLibraryChannel::adopt_child_for_test(child)
        }));

        let resilient = ResilientLibraryChannel::new(config, None);
        // Explicitly set failures to 0 to test exactly 3 recovery attempts
        resilient.ctx.consecutive_failures.store(0, Ordering::SeqCst);

        resilient.set_status_emitter(Arc::new(move |status, msg| {
            events_clone.lock().unwrap().push((status.to_string(), msg.to_string()));
        }));

        // Trigger restart from supervisor
        resilient.trigger_restart();

        // Wait for the bounded retry cycle to complete (3 attempts)
        let start = Instant::now();
        while start.elapsed() < Duration::from_secs(5) {
            if resilient.ctx.is_fatal.load(Ordering::SeqCst) {
                break;
            }
            std::thread::sleep(Duration::from_millis(20));
        }

        assert!(
            resilient.ctx.is_fatal.load(Ordering::SeqCst),
            "Channel must enter fatal state when repeated short-lived crashes occur"
        );
        assert_eq!(
            spawn_counter.load(Ordering::SeqCst),
            3,
            "Total spawn attempts must be capped at MAX_RETRIES (3)"
        );

        // Verify that subsequent trigger_restart calls do NOT spawn any more instances
        resilient.trigger_restart();
        assert_eq!(
            spawn_counter.load(Ordering::SeqCst),
            3,
            "Spawn count must not increase after reaching fatal"
        );

        let emitted = events.lock().unwrap();
        let statuses: Vec<String> = emitted.iter().map(|(s, _)| s.clone()).collect();
        assert!(statuses.contains(&"restarting".to_string()));
        assert_eq!(statuses.last().map(|s| s.as_str()), Some("fatal"));
    }

    /// R-002 verification: Simulate startup failure (initial_channel is None).
    /// Asserts that the supervisor recovers cleanly without panicking or terminating host,
    /// and transitions from restarting to recovered when sidecar comes back up.
    #[test]
    fn resilient_channel_early_startup_failure_recovers_without_panic() {
        let events = Arc::new(Mutex::new(Vec::<(String, String)>::new()));
        let events_clone = Arc::clone(&events);

        let mut config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );
        config.initial_backoff = Duration::from_millis(10);

        config.custom_spawner = Some(Arc::new(move |_cfg| {
            // Spawn a process that stays alive
            let child = Command::new("cmd")
                .args(["/c", "pause"])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null())
                .spawn()
                .expect("spawn pause child");
            StdioLibraryChannel::adopt_child_for_test(child)
        }));

        // Simulate startup failure: initial_channel is None
        let resilient = ResilientLibraryChannel::new(config, None);
        assert!(resilient.is_unhealthy(), "Must be unhealthy when initial channel is None");

        // Ping returns unavailable rather than panicking
        let ping_res = resilient.ping();
        assert!(ping_res.is_err());
        assert_eq!(ping_res.unwrap_err().code, "CORE_UNAVAILABLE");

        resilient.set_status_emitter(Arc::new(move |status, msg| {
            events_clone.lock().unwrap().push((status.to_string(), msg.to_string()));
        }));

        // Trigger recovery
        resilient.trigger_restart();

        // Wait for recovery
        let start = Instant::now();
        while start.elapsed() < Duration::from_secs(5) {
            if !resilient.is_unhealthy() {
                break;
            }
            std::thread::sleep(Duration::from_millis(20));
        }

        assert!(!resilient.is_unhealthy(), "Channel should recover successfully");
        let emitted = events.lock().unwrap();
        let statuses: Vec<String> = emitted.iter().map(|(s, _)| s.clone()).collect();
        assert!(statuses.contains(&"restarting".to_string()));
        assert!(statuses.contains(&"recovered".to_string()));
    }

    /// R-003 verification: Asserts that on_down callback holds Weak reference,
    /// breaking the strong reference cycle (context -> channel -> callback -> context),
    /// and that Drop for ResilientLibraryChannel reaps the child process and joins the reader thread.
    #[test]
    fn resilient_channel_shutdown_breaks_cycle_and_reaps_child_process() {
        let config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );

        let child = Command::new("cmd")
            .args(["/c", "pause"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn pause child");
        let pid = child.id();

        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt child");
        let resilient = ResilientLibraryChannel::new(config, Some(chan));

        let weak_ctx = Arc::downgrade(&resilient.ctx);
        // Before drop: strong count must be 1 (resilient channel owns it; on_down callback holds only Weak)
        assert_eq!(
            Arc::strong_count(&resilient.ctx),
            1,
            "on_down must not hold a strong reference to ResilientCoreContext"
        );

        // Explicitly drop resilient channel
        drop(resilient);

        // After drop: context must be deallocated (strong count == 0)
        assert_eq!(
            weak_ctx.upgrade().is_none(),
            true,
            "ResilientCoreContext must be completely dropped without reference cycle"
        );

        // Give OS a moment to reap
        std::thread::sleep(Duration::from_millis(200));

        // Verify child process is no longer running
        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
            .output()
            .expect("tasklist query");
        let tasklist_str = String::from_utf8_lossy(&output.stdout);
        assert!(
            !tasklist_str.contains(&format!("\"{pid}\"")),
            "Child process {pid} must be terminated and reaped upon channel drop"
        );
    }

    /// R-008 verification: Heartbeat detects alive but unresponsive sidecar (e.g. hung/deadlocked).
    /// Asserts that periodic heartbeat probes responsiveness via ping_timeout; when ping times out,
    /// it detects the fault, emits "restarting", cleans up the hung process, and recovers.
    #[test]
    fn resilient_channel_heartbeat_detects_unresponsive_child_and_recovers() {
        let events = Arc::new(Mutex::new(Vec::<(String, String)>::new()));
        let events_clone = Arc::clone(&events);

        let mut config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );
        config.heartbeat_interval = Duration::from_millis(50);
        config.heartbeat_ping_timeout = Duration::from_millis(150);
        config.initial_backoff = Duration::from_millis(10);

        // Initial process: cmd /c pause (alive but never responds to IPC ping)
        let child = Command::new("cmd")
            .args(["/c", "pause"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn pause child");
        let initial_pid = child.id();
        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt initial");

        // Custom spawner returns a replacement child upon recovery
        config.custom_spawner = Some(Arc::new(move |_cfg| {
            let child = Command::new("cmd")
                .args(["/c", "pause"])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null())
                .spawn()
                .expect("spawn recovered child");
            StdioLibraryChannel::adopt_child_for_test(child)
        }));

        let resilient = ResilientLibraryChannel::new(config, Some(chan));
        resilient.set_status_emitter(Arc::new(move |status, msg| {
            events_clone.lock().unwrap().push((status.to_string(), msg.to_string()));
        }));

        // Start the periodic heartbeat
        resilient.start_heartbeat();

        // Wait for heartbeat to detect unresponsiveness and trigger recovery
        let start = Instant::now();
        while start.elapsed() < Duration::from_secs(5) {
            let emitted = events.lock().unwrap();
            let statuses: Vec<String> = emitted.iter().map(|(s, _)| s.clone()).collect();
            if statuses.contains(&"restarting".to_string()) && statuses.contains(&"recovered".to_string()) {
                break;
            }
            drop(emitted);
            std::thread::sleep(Duration::from_millis(20));
        }

        let emitted = events.lock().unwrap();
        let statuses: Vec<String> = emitted.iter().map(|(s, _)| s.clone()).collect();
        assert!(
            statuses.contains(&"restarting".to_string()),
            "Heartbeat must detect unresponsive sidecar and emit restarting status"
        );
        assert!(
            statuses.contains(&"recovered".to_string()),
            "Supervisor must successfully recover sidecar after detecting unresponsive process"
        );

        // Verify the old hung process was killed and cleaned up
        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {initial_pid}"), "/FO", "CSV", "/NH"])
            .output()
            .expect("tasklist query");
        let tasklist_str = String::from_utf8_lossy(&output.stdout);
        assert!(
            !tasklist_str.contains(&format!("\"{initial_pid}\"")),
            "Old unresponsive child process {initial_pid} must be terminated and reaped upon recovery"
        );
    }

    /// R-008 verification: Repeated unresponsiveness is strictly capped by retry budget to reach fatal.
    #[test]
    fn resilient_channel_heartbeat_unresponsive_child_caps_retries_and_reaches_fatal() {
        let events = Arc::new(Mutex::new(Vec::<(String, String)>::new()));
        let events_clone = Arc::clone(&events);
        let respawn_count = Arc::new(AtomicU32::new(0));
        let count_clone = Arc::clone(&respawn_count);

        let mut config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );
        config.heartbeat_interval = Duration::from_millis(50);
        config.heartbeat_ping_timeout = Duration::from_millis(150);
        config.initial_backoff = Duration::from_millis(10);
        config.stable_duration = Duration::from_secs(30);

        // Initial unresponsive process
        let child = Command::new("cmd")
            .args(["/c", "pause"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn pause child");
        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt initial");

        // Custom spawner repeatedly returns unresponsive processes
        config.custom_spawner = Some(Arc::new(move |_cfg| {
            count_clone.fetch_add(1, Ordering::SeqCst);
            let child = Command::new("cmd")
                .args(["/c", "pause"])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null())
                .spawn()
                .expect("spawn pause child");
            StdioLibraryChannel::adopt_child_for_test(child)
        }));

        let resilient = ResilientLibraryChannel::new(config, Some(chan));
        // Explicitly set consecutive_failures to 0 to test full budget of 3 retries
        resilient.ctx.consecutive_failures.store(0, Ordering::SeqCst);

        resilient.set_status_emitter(Arc::new(move |status, msg| {
            events_clone.lock().unwrap().push((status.to_string(), msg.to_string()));
        }));

        resilient.start_heartbeat();

        let start = Instant::now();
        while start.elapsed() < Duration::from_secs(6) {
            if resilient.ctx.is_fatal.load(Ordering::SeqCst) {
                break;
            }
            std::thread::sleep(Duration::from_millis(20));
        }

        assert!(
            resilient.ctx.is_fatal.load(Ordering::SeqCst),
            "Channel must enter fatal state when repeated unresponsive timeouts exhaust retry budget"
        );
        let emitted = events.lock().unwrap();
        let statuses: Vec<String> = emitted.iter().map(|(s, _)| s.clone()).collect();
        assert_eq!(statuses.last().map(|s| s.as_str()), Some("fatal"));
    }

    /// R-009 verification: Drop / shutdown with in-flight unresponsive request completes in bounded time.
    /// Asserts that in-flight requests waiting for an unresponsive sidecar do not block channel drop
    /// and that the child process is guaranteed to be terminated and reaped without leaving orphan processes.
    #[test]
    fn resilient_channel_drop_with_in_flight_unresponsive_call_terminates_in_bounded_time() {
        let config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );

        let child = Command::new("cmd")
            .args(["/c", "pause"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn pause child");
        let pid = child.id();

        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt initial");
        let resilient = Arc::new(ResilientLibraryChannel::new(config, Some(chan)));

        // Spawn a background thread that makes an IPC request against the unresponsive sidecar
        let resilient_clone = Arc::clone(&resilient);
        let worker_handle = std::thread::spawn(move || {
            resilient_clone.list_books()
        });

        // Give worker thread a moment to enter the IPC call and wait
        std::thread::sleep(Duration::from_millis(50));

        // Now drop the resilient channel (measuring bounded shutdown time)
        let start = Instant::now();
        // Explicitly shutdown inner channel as drop does
        resilient.ctx.heartbeat_stop.store(true, Ordering::Relaxed);
        if let Ok(mut guard) = resilient.ctx.inner.lock() {
            if let Some(c) = guard.take() {
                c.shutdown_and_kill(Duration::from_millis(1500));
            }
        }
        let elapsed = start.elapsed();

        assert!(
            elapsed < Duration::from_secs(3),
            "Channel shutdown must complete in bounded time (took {:?})",
            elapsed
        );

        // Worker thread must unblock and receive error
        let worker_res = worker_handle.join().expect("worker join");
        assert!(worker_res.is_err(), "In-flight request must fail upon shutdown");

        // Give OS a moment to reap
        std::thread::sleep(Duration::from_millis(200));

        // Assert child process is reaped
        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
            .output()
            .expect("tasklist query");
        assert!(output.status.success(), "tasklist query must exit successfully");
        let tasklist_str = String::from_utf8_lossy(&output.stdout);
        assert!(
            !tasklist_str.contains(&format!("\"{pid}\"")),
            "Child process {pid} must be terminated and reaped on bounded shutdown"
        );
    }

    /// R-009 verification: StdioLibraryChannel::drop does not hang indefinitely when host session is active and sidecar is hung.
    #[test]
    fn stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time() {
        let child = Command::new("cmd")
            .args(["/c", "pause"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn pause child");
        let pid = child.id();

        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt child");
        // Set an active host session so drop exercises the CloseHostSession path
        *chan.host_session.lock().unwrap() = Some(HostSession {
            host_session_id: "test-hs".to_string(),
            credential: "test-cred".to_string(),
            core_session_id: "test-cs".to_string(),
            signing_key: [0u8; 32],
        });

        let start = Instant::now();
        drop(chan);
        let elapsed = start.elapsed();

        assert!(
            elapsed < Duration::from_secs(3),
            "StdioLibraryChannel drop must be bounded under unresponsive session, took {:?}",
            elapsed
        );

        std::thread::sleep(Duration::from_millis(200));

        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
            .output()
            .expect("tasklist query");
        assert!(output.status.success(), "tasklist query must exit successfully");
        let tasklist_str = String::from_utf8_lossy(&output.stdout);
        assert!(
            !tasklist_str.contains(&format!("\"{pid}\"")),
            "Child process {pid} must be terminated and reaped upon StdioLibraryChannel drop"
        );
    }

    /// AC1 & AC2 (P20-CLOSE-BOUND-1): In-flight unresponsive request + external force kill overlay scenario.
    /// Scenario:
    /// 1. An in-flight request is pending against an unresponsive sidecar (cmd /c pause).
    /// 2. The sidecar process is externally force-killed (simulating `Stop-Process -Force` / taskkill /F).
    /// 3. The channel is dropped / shut down.
    /// Asserts:
    /// - Shutdown completes within hard upper bound (< 3000ms, typical < 100ms).
    /// - In-flight caller thread unblocks immediately and receives CORE_UNAVAILABLE.
    /// - Zero orphans: child process is completely terminated and verified absent via tasklist with success exit code.
    #[test]
    fn resilient_channel_drop_after_external_kill_with_in_flight_call_is_bounded_and_zero_orphan() {
        let config = LibrarySpawnConfig::new(
            "cmd.exe".to_string(),
            PathBuf::from("."),
            None,
            None,
            None,
        );

        let python_exe = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".to_string());
        let child = Command::new(&python_exe)
            .args(["-c", "import time; time.sleep(60)"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn hung python child");
        let pid = child.id();

        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt initial");
        let resilient = Arc::new(ResilientLibraryChannel::new(config, Some(chan)));

        // Start heartbeat so its thread is active and part of lifecycle verification
        resilient.start_heartbeat();

        // 1. Spawn in-flight request thread that hangs on unresponsive sidecar
        let resilient_clone = Arc::clone(&resilient);
        let worker_handle = std::thread::spawn(move || {
            resilient_clone.list_books()
        });

        // Handshake: synchronously verify in-flight request has entered pending wait state
        let handshake_start = Instant::now();
        loop {
            let has_pending = {
                if let Some(guard) = lock_timeout_recover(&resilient.ctx.inner, Duration::from_millis(50)) {
                    if let Some(ref c) = *guard {
                        c.pending_responses.lock().map(|p| !p.is_empty()).unwrap_or(false)
                    } else {
                        false
                    }
                } else {
                    false
                }
            };
            if has_pending {
                break;
            }
            assert!(
                handshake_start.elapsed() < Duration::from_secs(5),
                "Timed out waiting for in-flight call to enter pending state"
            );
            std::thread::sleep(Duration::from_millis(10));
        }

        // Suppress automatic restart to serialize cleanup and prevent race condition
        resilient.ctx.heartbeat_stop.store(true, Ordering::SeqCst);

        // 2. Simulate external force-kill (Stop-Process -Force / taskkill /F)
        let kill_status = Command::new("taskkill")
            .args(["/F", "/PID", &pid.to_string()])
            .output()
            .expect("execute external taskkill");
        assert!(
            kill_status.status.success(),
            "External kill must succeed for target PID {pid}"
        );

        // 3. Take the inner channel directly: MUST be Some (cannot be bypassed by auto-restart)
        let inner_chan = {
            let mut guard = lock_timeout_recover(&resilient.ctx.inner, Duration::from_millis(500))
                .expect("acquire ctx.inner lock");
            guard.take().expect("inner channel must be present, cannot be None")
        };

        // 4. Measure shutdown duration of the production shutdown entry point
        let shutdown_start = Instant::now();
        inner_chan.shutdown_and_kill(Duration::from_millis(1200));
        let shutdown_elapsed = shutdown_start.elapsed();
        println!(
            "[ac1-overlay-bound] measured shutdown_elapsed: {:?} ({} ms)",
            shutdown_elapsed,
            shutdown_elapsed.as_millis()
        );

        // Hard upper bound assertion: must be strictly bounded (< 3000ms)
        assert!(
            shutdown_elapsed < Duration::from_secs(3),
            "Shutdown after external kill with in-flight call must complete within 3s, took {:?}",
            shutdown_elapsed
        );

        // 5. In-flight worker thread must be unblocked and return Err within bounded time
        let (join_tx, join_rx) = std::sync::mpsc::sync_channel(1);
        let _joiner = std::thread::spawn(move || {
            let res = worker_handle.join();
            let _ = join_tx.send(res);
        });
        let worker_res = join_rx
            .recv_timeout(Duration::from_secs(2))
            .expect("worker thread must join within 2s of shutdown")
            .expect("worker thread joined without panic");
        assert!(
            worker_res.is_err(),
            "In-flight request must fail with unavailable error when sidecar is killed"
        );
        let err = worker_res.unwrap_err();
        assert_eq!(err.code, "CORE_UNAVAILABLE");

        // Give OS brief moment to complete process table cleanup
        std::thread::sleep(Duration::from_millis(100));

        // 6. Process tree / tasklist zero orphan assertion with exit code verification
        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
            .output()
            .expect("query tasklist for reaped child");
        assert!(output.status.success(), "tasklist query must return success exit code");
        let stdout_str = String::from_utf8_lossy(&output.stdout);
        assert!(
            !stdout_str.contains(&format!("\"{pid}\"")),
            "Target PID {pid} must NOT be present in process table"
        );
    }

    /// AC1 & AC4: Unit test confirming poisoned child mutex is recovered and killed (zero orphan guaranteed)
    #[test]
    fn poisoned_child_lock_is_recovered_and_killed() {
        let child = Command::new("cmd")
            .args(["/c", "pause"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn pause child");
        let pid = child.id();

        let chan = StdioLibraryChannel::adopt_child_for_test(child).expect("adopt initial");

        // Intentionally poison the child lock by panicking inside a thread holding it
        let _ = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _guard = chan.child.lock().unwrap();
            panic!("intentional test panic to poison child mutex");
        }));
        assert!(chan.child.is_poisoned(), "child mutex must be poisoned");

        // Now call shutdown_and_kill: it must recover the poisoned lock, kill the process, and not leak
        let start = Instant::now();
        chan.shutdown_and_kill(Duration::from_millis(1200));
        let elapsed = start.elapsed();

        assert!(
            elapsed < Duration::from_secs(3),
            "Shutdown under poisoned lock must complete within 3s, took {:?}",
            elapsed
        );

        std::thread::sleep(Duration::from_millis(100));
        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
            .output()
            .expect("query tasklist");
        assert!(output.status.success());
        let stdout_str = String::from_utf8_lossy(&output.stdout);
        assert!(
            !stdout_str.contains(&format!("\"{pid}\"")),
            "Process {pid} must be killed even when child mutex was poisoned"
        );
    }

    /// AC1 & AC4: Unit test confirming wait_timeout_or_kill has strict hard upper bound
    /// and does not hang infinitely even when process is already dead or refusing normal exit.
    #[test]
    fn wait_timeout_or_kill_returns_immediately_for_already_exited_child() {
        let mut child = Command::new("cmd")
            .args(["/c", "exit 0"])
            .spawn()
            .expect("spawn fast exit child");
        
        // Wait for it to finish first
        std::thread::sleep(Duration::from_millis(100));

        let start = Instant::now();
        let res = wait_timeout_or_kill(&mut child, Duration::from_millis(1500));
        let elapsed = start.elapsed();

        assert!(res.is_ok(), "Already-exited child must return Ok exit status");
        assert!(
            elapsed < Duration::from_millis(100),
            "Already-exited child check must complete immediately (< 100ms), took {:?}",
            elapsed
        );
    }

    /// AC1 & AC4: Unit test confirming reader join bounded guard prevents infinite hanging.
    #[test]
    fn reader_join_guard_enforces_hard_timeout_if_reader_hung() {
        let (done_tx, done_rx) = std::sync::mpsc::sync_channel(1);
        let hung_handle = std::thread::spawn(move || {
            // Simulate a permanently hung reader thread
            std::thread::sleep(Duration::from_secs(60));
        });

        let start = Instant::now();
        let joiner = std::thread::Builder::new()
            .name("test-reader-guard".to_string())
            .spawn(move || {
                let _ = hung_handle.join();
                let _ = done_tx.send(());
            });
        assert!(joiner.is_ok());

        // Hard bound timeout (500ms)
        let res = done_rx.recv_timeout(Duration::from_millis(500));
        let elapsed = start.elapsed();

        assert!(
            res.is_err(),
            "Hung reader must trigger timeout on bounded guard"
        );
        assert!(
            elapsed >= Duration::from_millis(450) && elapsed < Duration::from_millis(1200),
            "Guard must time out around 500ms, elapsed: {:?}",
            elapsed
        );
    }
}
