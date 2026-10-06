//! Production Library & Core Lifecycle Bridge (M2-IPC1).
//!
//! Connects the Tauri host to the Python Core service sidecar (`bootstrap.core_service`)
//! over stdio JSON-lines with Contract 1.1 typed envelopes.

use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

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

    Ok(value.get("result").cloned().unwrap_or(serde_json::Value::Null))
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
    fn list_region_revisions(
        &self,
        region_id: &str,
    ) -> Result<serde_json::Value, LibraryError>;
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
}

/// The command argv pinned for spawning the production Core service.
pub fn spawn_args() -> Vec<&'static str> {
    vec!["-m", "bootstrap.core_service"]
}

pub struct StdioLibraryChannel {
    child: Mutex<Child>,
    stdin: Mutex<ChildStdin>,
    stdout: Mutex<BufReader<ChildStdout>>,
    request_id_gen: AtomicU64,
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

        let mut child = cmd
            .spawn()
            .map_err(|e| LibraryError::unavailable(&format!("Failed to spawn Core: {e}")))?;

        let stdin = child
            .stdin
            .take()
            .ok_or_else(|| LibraryError::unavailable("Failed to open child stdin"))?;
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| LibraryError::unavailable("Failed to open child stdout"))?;

        Ok(Self {
            child: Mutex::new(child),
            stdin: Mutex::new(stdin),
            stdout: Mutex::new(BufReader::new(stdout)),
            request_id_gen: AtomicU64::new(1),
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
        let request = serde_json::json!({
            "protocol": "new-manga.core",
            "version": { "major": 1, "minor": 4 },
            "request_id": req_id,
            "command": command,
            "payload": payload,
        });

        let mut line = request.to_string();
        line.push('\n');

        {
            let mut stdin = self.stdin.lock().map_err(|_| {
                LibraryError::unavailable("Internal mutex poisoned (stdin)")
            })?;
            stdin
                .write_all(line.as_bytes())
                .map_err(|e| LibraryError::unavailable(&format!("stdin write failed: {e}")))?;
            stdin
                .flush()
                .map_err(|e| LibraryError::unavailable(&format!("stdin flush failed: {e}")))?;
        }

        let mut response_line = String::new();
        {
            let mut stdout = self.stdout.lock().map_err(|_| {
                LibraryError::unavailable("Internal mutex poisoned (stdout)")
            })?;
            stdout
                .read_line(&mut response_line)
                .map_err(|e| LibraryError::unavailable(&format!("stdout read failed: {e}")))?;
        }

        if response_line.is_empty() {
            return Err(LibraryError::unavailable("Core stdout closed (EOF)"));
        }

        decode_response(response_line.trim_end())
    }

    #[cfg(test)]
    pub fn kill_for_test(&self) {
        if let Ok(mut child) = self.child.lock() {
            let _ = child.kill();
            let _ = child.wait();
        }
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
        let req = serde_json::json!({
            "protocol": "new-manga.core",
            "version": { "major": 1, "minor": 4 },
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
    }
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

    fn list_region_revisions(
        &self,
        region_id: &str,
    ) -> Result<serde_json::Value, LibraryError> {
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
}

/// In-memory mock channel for testing without spawning Python.
pub struct MockLibraryChannel {
    ping_result: Mutex<Result<PingResult, LibraryError>>,
    books_result: Mutex<Result<Vec<BookSummary>, LibraryError>>,
    settings_result: Mutex<Result<serde_json::Value, LibraryError>>,
    retype_result: Mutex<Result<serde_json::Value, LibraryError>>,
    regions_result: Mutex<Result<serde_json::Value, LibraryError>>,
    domain_result: Mutex<Result<serde_json::Value, LibraryError>>,
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
        }
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

    fn list_region_revisions(
        &self,
        _region_id: &str,
    ) -> Result<serde_json::Value, LibraryError> {
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
}

#[cfg(test)]
mod tests {
    use super::*;

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
        let success = r#"{"protocol":"new-manga.core","version":{"major":1,"minor":0},"request_id":"1","result":{"status":"ready"},"error":null}"#;
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
}
