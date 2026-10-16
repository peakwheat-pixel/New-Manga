//! Production Library & Core Lifecycle Bridge (M2-IPC1).
//!
//! Connects the Tauri host to the Python Core service sidecar (`bootstrap.core_service`)
//! over stdio JSON-lines with Core protocol 2.3 envelopes.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::io::{BufRead, BufReader, Write};
use std::path::Path;
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
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
}

impl LibraryError {
    pub fn new(code: &str, category: &str, retryable: bool, message: Option<&str>) -> Self {
        Self {
            code: code.to_string(),
            category: category.to_string(),
            retryable,
            message: message.map(ToString::to_string),
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
    let total_pages = val
        .get("total_pages")
        .and_then(Value::as_u64)
        .unwrap_or(0);
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
            let sha256 = o.get("sha256").and_then(Value::as_str).map(ToString::to_string);
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
        Some(Value::Null) | None => return Ok(ExportHistoryResponseView { exports: Vec::new() }),
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

pub trait LibraryChannel: Send + Sync {
    fn ping(&self) -> Result<PingResult, LibraryError>;
    fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError>;
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
    /// EVENTS-FWD-1 (rev 2.4 §6.4): Register an event sink for background
    /// core events forwarded to WebView. Default is a no-op.
    fn set_event_sink(&self, _sink: EventSink) {}

    /// EXPORT-IPC-1 (contract rev 2.5 §5.8): Export control and query surface.
    /// Returns whitelisted safe views without output_path or file references.
    fn cancel_export(
        &self,
        _export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
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
            let current_step_type = raw_payload.get("current_step_type").and_then(Value::as_str)?;
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

pub struct StdioLibraryChannel {
    child: Mutex<Child>,
    stdin: Mutex<ChildStdin>,
    transaction_lock: Mutex<()>,
    request_id_gen: AtomicU64,
    host_session: Mutex<Option<HostSession>>,
    event_sink: Arc<Mutex<Option<EventSink>>>,
    pending_responses: Arc<Mutex<HashMap<String, SyncSender<Result<String, LibraryError>>>>>,
    is_down: Arc<AtomicBool>,
    reader_join_handle: Mutex<Option<std::thread::JoinHandle<()>>>,
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
    serde_json::json!({
        "protocol": "new-manga.core",
        "version": { "major": 2, "minor": 3 },
        "request_id": request_id,
        "command": command,
        "payload": payload,
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

        let pending_responses: Arc<Mutex<HashMap<String, SyncSender<Result<String, LibraryError>>>>> =
            Arc::new(Mutex::new(HashMap::new()));
        let event_sink: Arc<Mutex<Option<EventSink>>> = Arc::new(Mutex::new(None));
        let is_down = Arc::new(AtomicBool::new(false));

        let pending_clone = Arc::clone(&pending_responses);
        let sink_clone = Arc::clone(&event_sink);
        let is_down_clone = Arc::clone(&is_down);

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
                            break;
                        }
                    }
                }
            })
            .map_err(|e| LibraryError::unavailable(&format!("Failed to spawn reader thread: {e}")))?;

        Ok(Self {
            child: Mutex::new(child),
            stdin: Mutex::new(stdin),
            transaction_lock: Mutex::new(()),
            request_id_gen: AtomicU64::new(1),
            host_session: Mutex::new(None),
            event_sink,
            pending_responses,
            is_down,
            reader_join_handle: Mutex::new(Some(reader_thread)),
        })
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

    fn exchange(&self, request: Value) -> Result<Value, LibraryError> {
        let req_id = request
            .get("request_id")
            .and_then(Value::as_str)
            .unwrap_or("host-control-request")
            .to_string();

        let mut line = request.to_string();
        line.push('\n');

        let _tx_guard = self
            .transaction_lock
            .lock()
            .map_err(|_| LibraryError::unavailable("Internal mutex poisoned (transaction)"))?;

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
            let mut pending = self
                .pending_responses
                .lock()
                .map_err(|_| LibraryError::unavailable("Internal mutex poisoned (pending)"))?;
            pending.insert(req_id.clone(), tx);
        }

        {
            let mut stdin = self
                .stdin
                .lock()
                .map_err(|_| LibraryError::unavailable("Internal mutex poisoned (stdin)"))?;
            if let Err(e) = stdin.write_all(line.as_bytes()) {
                let mut pending = self.pending_responses.lock().unwrap();
                pending.remove(&req_id);
                return Err(LibraryError::unavailable(&format!("stdin write failed: {e}")));
            }
            if let Err(e) = stdin.flush() {
                let mut pending = self.pending_responses.lock().unwrap();
                pending.remove(&req_id);
                return Err(LibraryError::unavailable(&format!("stdin flush failed: {e}")));
            }
        }

        let response_line = match rx.recv() {
            Ok(Ok(resp)) => resp,
            Ok(Err(err)) => return Err(err),
            Err(_) => return Err(LibraryError::unavailable("Core stdout closed (EOF)")),
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

        decode_response(response_line.trim_end())
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
        if chapter_id.is_empty()
            || duplicate_policy.is_some_and(|p| !matches!(p, "skip" | "import_as_new"))
        {
            return Err(LibraryError::new(
                "INVALID_REQUEST",
                "validation",
                false,
                None,
            ));
        }
        let mut grant_id_bytes = [0; 32];
        let grant = crate::host_issuer::build_import_grant(
            path,
            source_kind,
            &session.host_session_id,
            format!(
                "grant_{}",
                crate::host_issuer::random_token(&mut grant_id_bytes).map_err(host_issuer_error)?
            ),
            &session.signing_key,
        )
        .map_err(host_issuer_error)?;
        let registration =
            self.host_control_round_trip("RegisterImportSource", grant.payload, Some(session))?;
        if registration.get("registered") != Some(&Value::Bool(true)) {
            self.revoke_host_grant(session, "import", &grant.grant_id);
            return Err(LibraryError::malformed(
                "Core did not register import grant",
            ));
        }
        let mut payload = serde_json::json!({
            "chapter_id": chapter_id,
            "sources": [grant.reference],
        });
        if let Some(policy) = duplicate_policy {
            payload["duplicate_policy"] = serde_json::json!(policy);
        }
        let result = match self.round_trip("ImportPages", payload) {
            Ok(result) => result,
            Err(error) => {
                self.revoke_host_grant(session, "import", &grant.grant_id);
                return Err(error);
            }
        };
        match crate::host_issuer::import_summary(result) {
            Ok(summary) => Ok(summary),
            Err(error) => {
                self.revoke_host_grant(session, "import", &grant.grant_id);
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
    let poll_interval = std::time::Duration::from_millis(50);
    while start.elapsed() < timeout {
        if let Some(status) = child.try_wait()? {
            return Ok(status);
        }
        std::thread::sleep(poll_interval);
    }
    let _ = child.kill();
    child.wait()
}

impl Drop for StdioLibraryChannel {
    fn drop(&mut self) {
        if let Ok(mut session) = self.host_session.lock() {
            if let Some(session) = session.take() {
                let _ = self.host_control_round_trip(
                    "CloseHostSession",
                    serde_json::json!({}),
                    Some(&session),
                );
            }
        }
        let req = serde_json::json!({
            "protocol": "new-manga.core",
            "version": { "major": 2, "minor": 3 },
            "request_id": "shutdown-drop",
            "command": "core.shutdown",
            "payload": {},
        });
        if let Ok(mut stdin) = self.stdin.lock() {
            let _ = writeln!(stdin, "{req}");
            let _ = stdin.flush();
        }
        if let Ok(mut child) = self.child.lock() {
            let _ = wait_timeout_or_kill(&mut child, std::time::Duration::from_secs(5));
        }
        if let Ok(mut handle_slot) = self.reader_join_handle.lock() {
            if let Some(handle) = handle_slot.take() {
                let _ = handle.join();
            }
        }
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
        let val = self.round_trip("core.ping", serde_json::json!({}))?;
        serde_json::from_value(val)
            .map_err(|e| LibraryError::malformed(&format!("Failed to parse PingResult: {e}")))
    }

    fn list_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
        let val = self.round_trip("ListBooks", serde_json::json!({}))?;
        serde_json::from_value(val)
            .map_err(|e| LibraryError::malformed(&format!("Failed to parse BookSummary list: {e}")))
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
        self.export_with_session(session, path, request)
    }

    fn set_event_sink(&self, sink: EventSink) {
        *self.event_sink.lock().unwrap() = Some(sink);
    }

    fn cancel_export(
        &self,
        export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
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
                    sha256: Some("abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234".to_string()),
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

    fn cancel_export(
        &self,
        _export_id: &str,
    ) -> Result<ExportProgressSnapshotView, LibraryError> {
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn spawn_args_target_core_service_module() {
        assert_eq!(
            spawn_args(),
            vec!["-m", "bootstrap.core_service"],
            "StdioLibraryChannel must spawn bootstrap.core_service"
        );
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
        let got_102 = rx2.recv_timeout(Duration::from_millis(200)).unwrap().unwrap();
        assert!(got_102.contains("\"request_id\":\"req-102\""));

        let got_101 = rx1.recv_timeout(Duration::from_millis(200)).unwrap().unwrap();
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

        let view = project_export_snapshot(raw_core_snapshot).expect("project snapshot must succeed");
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
        assert!(!serialized.contains("output_path"), "must not contain output_path");
        assert!(!serialized.contains("target_path"), "must not contain target_path");
        assert!(!serialized.contains("internal_file_path"), "must not contain internal_file_path");
        assert!(!serialized.contains("grant_secret"), "must not contain grant_id");
        assert!(!serialized.contains("C:\\"), "must not contain Windows drive path");
        assert!(!serialized.contains("secret"), "must not contain private path components");
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
        assert!(!serialized.contains("output_path"), "must not contain output_path");
        assert!(!serialized.contains("stale_policy"), "must not contain stale_policy");
        assert!(!serialized.contains("target_ref"), "must not contain target_ref");
        assert!(!serialized.contains("grant-sec"), "must not contain grant credentials");
        assert!(!serialized.contains("D:\\"), "must not contain Windows drive path");
        assert!(!serialized.contains("Private"), "must not contain private path components");
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
}
