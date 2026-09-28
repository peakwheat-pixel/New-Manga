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
    pub page_count: u32,
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
            "version": { "major": 1, "minor": 0 },
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
}

impl Drop for StdioLibraryChannel {
    fn drop(&mut self) {
        let req = serde_json::json!({
            "protocol": "new-manga.core",
            "version": { "major": 1, "minor": 0 },
            "request_id": "shutdown-drop",
            "command": "core.shutdown",
            "payload": {},
        });
        if let Ok(mut stdin) = self.stdin.lock() {
            let _ = writeln!(stdin, "{req}");
            let _ = stdin.flush();
        }
        if let Ok(mut child) = self.child.lock() {
            let _ = child.wait();
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
}

/// In-memory mock channel for testing without spawning Python.
pub struct MockLibraryChannel {
    ping_result: Mutex<Result<PingResult, LibraryError>>,
    books_result: Mutex<Result<Vec<BookSummary>, LibraryError>>,
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
        }
    }

    pub fn set_books(&self, books: Vec<BookSummary>) {
        *self.books_result.lock().unwrap() = Ok(books);
    }

    pub fn set_books_error(&self, error: LibraryError) {
        *self.books_result.lock().unwrap() = Err(error);
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
            page_count: 5,
            created_at: "2026-09-28T00:00:00Z".to_string(),
            updated_at: "2026-09-28T00:00:00Z".to_string(),
        }]);

        let loaded = channel.list_books().unwrap();
        assert_eq!(loaded.len(), 1);
        assert_eq!(loaded[0].book_id, "book-1");
        assert_eq!(loaded[0].page_count, 5);

        channel.set_books_error(LibraryError::unavailable("connection lost"));
        let err = channel.list_books().unwrap_err();
        assert_eq!(err.code, "CORE_UNAVAILABLE");
        assert_eq!(err.retryable, true);
    }
}
