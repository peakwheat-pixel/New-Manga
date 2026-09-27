//! Core↔host control bridge (M2-RC1).
//!
//! The Python Core owns reference authority (issuance, resolution, revocation,
//! sliding TTL). The Tauri host is the trusted layer (Contract 1.1 T5.2): it
//! receives a control-plane grant (derived-cache relative path + issue-time
//! facts) over a stdio JSON-lines sidecar channel and then reads the file
//! itself. Resource bytes never cross this bridge (Contract §10: bytes stay
//! outside ordinary JSON/Base64 IPC, events and errors).

use rand::Rng;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Grant {
    #[serde(rename = "scope_class")]
    pub scope_class: String,
    #[serde(rename = "resource_id")]
    pub resource_id: String,
    #[serde(rename = "revision_fingerprint")]
    pub revision_fingerprint: String,
    #[serde(rename = "rel_path")]
    pub rel_path: String,
    #[serde(rename = "size")]
    pub size: u64,
    #[serde(rename = "sha256")]
    pub sha256: String,
    #[serde(rename = "volume_serial")]
    pub volume_serial: u32,
    #[serde(rename = "file_index")]
    pub file_index: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IssuedRef {
    #[serde(rename = "id")]
    pub opaque_id: String,
    #[serde(rename = "size")]
    pub size: u64,
}

#[derive(Debug, Clone)]
pub struct CoreError {
    pub code: String,
}

impl CoreError {
    pub fn new(code: &str) -> Self {
        Self { code: code.to_string() }
    }
}

fn decode_response(line: &str) -> Result<serde_json::Value, CoreError> {
    let value: serde_json::Value =
        serde_json::from_str(line).map_err(|_| CoreError::new("REF_MALFORMED"))?;
    if let Some(error) = value.get("error") {
        let code = error
            .get("code")
            .and_then(|c| c.as_str())
            .unwrap_or("UNKNOWN")
            .to_string();
        return Err(CoreError { code });
    }
    Ok(value.get("result").cloned().unwrap_or(serde_json::Value::Null))
}

/// Control-plane transport; `MockCoreChannel` drives Rust-side unit tests,
/// `StdioCoreChannel` talks to the real Python Core sidecar.
///
/// RC2 (F-03): there is no `register` on this surface. The catalog
/// (`resource_id -> rel_path`) lives in the Core/SQLite store; the host can
/// only name catalog entries when issuing. `issue` never carries a TTL
/// override -- the probe-only override lives on `issue_probe` and is only
/// reachable from the probe-mode command surface.
pub trait CoreChannel: Send + Sync {
    /// Issue an opaque reference for a cataloged resource; the Core resolves
    /// the path from its catalog authority and applies the ruled 300 s
    /// sliding default TTL.
    fn issue(&self, resource_id: &str, revision: &str) -> Result<IssuedRef, CoreError>;
    /// Probe-only issue with an explicit TTL override (evidence runner
    /// lifecycle scenarios). The production command surface never exposes
    /// this; the Core refuses values above its default.
    fn issue_probe(
        &self,
        resource_id: &str,
        revision: &str,
        ttl_seconds: f64,
    ) -> Result<IssuedRef, CoreError>;
    fn resolve(&self, opaque_id: &str) -> Result<Grant, CoreError>;
    fn revoke(&self, opaque_id: &str) -> Result<(), CoreError>;
    fn revoke_resource(&self, resource_id: &str) -> Result<u32, CoreError>;
}

/// Real Python Core sidecar over stdio JSON-lines (wire v1). The catalog
/// authority is the Core's SQLite store (path handed over via
/// `M2RC2_CATALOG_DB`); the host holds no catalog state at all (RC2 F-03).
pub struct StdioCoreChannel {
    child: Mutex<Child>,
    stdin: Mutex<ChildStdin>,
    stdout: Mutex<BufReader<ChildStdout>>,
}

impl StdioCoreChannel {
    /// Spawn `python -m infrastructure.resource_channel.host_bridge` with the
    /// repository `src` on the module path, the servable scope roots and the
    /// catalog database in the environment.
    pub fn spawn(
        python_exe: &str,
        src_root: &std::path::Path,
        derived_root: &std::path::Path,
        managed_root: &std::path::Path,
        catalog_db: &std::path::Path,
    ) -> Result<Self, CoreError> {
        let mut child = Command::new(python_exe)
            .arg("-m")
            .arg("infrastructure.resource_channel.host_bridge")
            .current_dir(src_root)
            .env("M2RC1_DERIVED_ROOT", derived_root)
            .env("M2RC1_MANAGED_ROOT", managed_root)
            .env("M2RC2_CATALOG_DB", catalog_db)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .map_err(|error| CoreError { code: format!("CORE_SPAWN_FAILED:{error}") })?;
        let stdin = child
            .stdin
            .take()
            .ok_or_else(|| CoreError::new("CORE_SPAWN_FAILED"))?;
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| CoreError::new("CORE_SPAWN_FAILED"))?;
        Ok(Self {
            child: Mutex::new(child),
            stdin: Mutex::new(stdin),
            stdout: Mutex::new(BufReader::new(stdout)),
        })
    }

    fn round_trip(
        &self,
        method: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value, CoreError> {
        let request = serde_json::json!({ "id": 1, "method": method, "params": params });
        let mut line = request.to_string();
        line.push('\n');
        {
            let mut stdin = self.stdin.lock().unwrap();
            stdin
                .write_all(line.as_bytes())
                .map_err(|_| CoreError::new("CORE_BRIDGE_DOWN"))?;
            stdin
                .flush()
                .map_err(|_| CoreError::new("CORE_BRIDGE_DOWN"))?;
        }
        let mut response_line = String::new();
        {
            let mut stdout = self.stdout.lock().unwrap();
            stdout
                .read_line(&mut response_line)
                .map_err(|_| CoreError::new("CORE_BRIDGE_DOWN"))?;
        }
        if response_line.is_empty() {
            return Err(CoreError::new("CORE_BRIDGE_DOWN"));
        }
        decode_response(response_line.trim_end())
    }
}

impl Drop for StdioCoreChannel {
    fn drop(&mut self) {
        let shutdown = serde_json::json!({"id": 0, "method": "shutdown"}).to_string();
        if let Ok(mut stdin) = self.stdin.lock() {
            let _ = stdin.write_all(shutdown.as_bytes());
            let _ = stdin.write_all(b"\n");
            let _ = stdin.flush();
        }
        if let Ok(mut child) = self.child.lock() {
            let _ = child.wait();
        }
    }
}

impl CoreChannel for StdioCoreChannel {
    fn issue(&self, resource_id: &str, revision: &str) -> Result<IssuedRef, CoreError> {
        self.issue_via_wire(resource_id, revision, None)
    }

    fn issue_probe(
        &self,
        resource_id: &str,
        revision: &str,
        ttl_seconds: f64,
    ) -> Result<IssuedRef, CoreError> {
        self.issue_via_wire(resource_id, revision, Some(ttl_seconds))
    }

    fn resolve(&self, opaque_id: &str) -> Result<Grant, CoreError> {
        let value = self.round_trip("resolve", serde_json::json!({ "id": opaque_id }))?;
        serde_json::from_value(value).map_err(|_| CoreError::new("REF_MALFORMED"))
    }

    fn revoke(&self, opaque_id: &str) -> Result<(), CoreError> {
        self.round_trip("revoke", serde_json::json!({ "id": opaque_id }))?;
        Ok(())
    }

    fn revoke_resource(&self, resource_id: &str) -> Result<u32, CoreError> {
        let value = self.round_trip(
            "revoke_resource",
            serde_json::json!({ "resource_id": resource_id }),
        )?;
        Ok(value.get("revoked_count").and_then(|c| c.as_u64()).unwrap_or(0) as u32)
    }
}

impl StdioCoreChannel {
    /// Wire shape pinned here: the host names a catalog entry only — no
    /// rel_path, no scope_class (Core/SQLite authority, F-03); the TTL
    /// override exists only on the probe path.
    fn issue_via_wire(
        &self,
        resource_id: &str,
        revision: &str,
        ttl_seconds: Option<f64>,
    ) -> Result<IssuedRef, CoreError> {
        let value =
            self.round_trip("issue", build_issue_params(resource_id, revision, ttl_seconds))?;
        serde_json::from_value(value).map_err(|_| CoreError::new("REF_MALFORMED"))
    }
}

/// Pure wire-shape builder (unit-tested): the issue request names a catalog
/// entry only. There is no rel_path/scope_class key to smuggle paths through,
/// and `ttl_seconds` exists only on the probe path (F-03).
pub(crate) fn build_issue_params(
    resource_id: &str,
    revision: &str,
    ttl_seconds: Option<f64>,
) -> serde_json::Value {
    let mut params = serde_json::json!({
        "resource_id": resource_id,
        "revision_fingerprint": revision,
    });
    if let Some(ttl) = ttl_seconds {
        params["ttl_seconds"] = serde_json::json!(ttl);
    }
    params
}

/// In-process mock for Rust unit tests; mirrors the Python semantics that the
/// pytest suite verifies against the real service. The catalog map plays the
/// role of the Core's SQLite store: tests seed it through `register` (the
/// stand-in for the catalog loader), and `issue` resolves paths from it --
/// mirroring the fail-closed `RESOURCE_NOT_CATALOGED` behaviour of the real
/// bridge.
pub struct MockCoreChannel {
    pub catalog: Mutex<HashMap<String, String>>,
    pub table: Mutex<HashMap<String, MockEntry>>,
}

pub struct MockEntry {
    pub grant: Grant,
    pub revoked: bool,
    /// None = no expiry (mirrors the Core's default TTL); Some(instant) when
    /// the issue came through the probe-only TTL override path.
    pub expires_at: Option<std::time::Instant>,
}

impl MockCoreChannel {
    pub fn new() -> Self {
        Self {
            catalog: Mutex::new(HashMap::new()),
            table: Mutex::new(HashMap::new()),
        }
    }

    /// Seed the mock catalog (the stand-in for the Core-side catalog loader);
    /// not part of the `CoreChannel` transport surface.
    pub fn register(&self, resource_id: &str, rel_path: &str) -> Result<(), CoreError> {
        self.catalog
            .lock()
            .unwrap()
            .insert(resource_id.to_string(), rel_path.to_string());
        Ok(())
    }

    fn issue_internal(
        &self,
        resource_id: &str,
        revision: &str,
        ttl_override: Option<f64>,
    ) -> Result<IssuedRef, CoreError> {
        let rel = self
            .catalog
            .lock()
            .unwrap()
            .get(resource_id)
            .cloned()
            .ok_or_else(|| CoreError::new("RESOURCE_NOT_CATALOGED"))?;
        // opaque IDs follow the Python service convention: m2id.v1.<43 chars>
        let segment: String = rand::thread_rng()
            .sample_iter(rand::distributions::Alphanumeric)
            .take(43)
            .map(char::from)
            .collect();
        let opaque_id = format!("m2id.v1.{segment}");
        let metadata = std::fs::metadata(&rel).ok();
        let grant = Grant {
            scope_class: "derived-read-only".into(),
            resource_id: resource_id.into(),
            revision_fingerprint: revision.into(),
            rel_path: rel,
            size: metadata.as_ref().map(|m| m.len()).unwrap_or(0),
            sha256: String::new(),
            volume_serial: 0,
            file_index: 0,
        };
        let size = grant.size;
        let expires_at = ttl_override
            .map(|secs| std::time::Instant::now() + std::time::Duration::from_secs_f64(secs));
        self.table.lock().unwrap().insert(
            opaque_id.clone(),
            MockEntry { grant, revoked: false, expires_at },
        );
        Ok(IssuedRef { opaque_id, size })
    }
}

impl Default for MockCoreChannel {
    fn default() -> Self {
        Self::new()
    }
}

impl CoreChannel for MockCoreChannel {
    fn issue(&self, resource_id: &str, revision: &str) -> Result<IssuedRef, CoreError> {
        self.issue_internal(resource_id, revision, None)
    }

    fn issue_probe(
        &self,
        resource_id: &str,
        revision: &str,
        ttl_seconds: f64,
    ) -> Result<IssuedRef, CoreError> {
        self.issue_internal(resource_id, revision, Some(ttl_seconds))
    }

    fn resolve(&self, opaque_id: &str) -> Result<Grant, CoreError> {
        let mut table = self.table.lock().unwrap();
        let entry = table
            .get_mut(opaque_id)
            .ok_or_else(|| CoreError::new("REF_UNKNOWN_ID"))?;
        if entry.revoked {
            return Err(CoreError::new("REF_REVOKED"));
        }
        if let Some(expires_at) = entry.expires_at {
            if std::time::Instant::now() >= expires_at {
                return Err(CoreError::new("REF_EXPIRED"));
            }
        }
        Ok(entry.grant.clone())
    }

    fn revoke(&self, opaque_id: &str) -> Result<(), CoreError> {
        let mut table = self.table.lock().unwrap();
        let entry = table
            .get_mut(opaque_id)
            .ok_or_else(|| CoreError::new("REF_UNKNOWN_ID"))?;
        entry.revoked = true;
        Ok(())
    }

    fn revoke_resource(&self, resource_id: &str) -> Result<u32, CoreError> {
        let mut table = self.table.lock().unwrap();
        let mut count = 0;
        for entry in table.values_mut() {
            if entry.grant.resource_id == resource_id && !entry.revoked {
                entry.revoked = true;
                count += 1;
            }
        }
        Ok(count)
    }
}
