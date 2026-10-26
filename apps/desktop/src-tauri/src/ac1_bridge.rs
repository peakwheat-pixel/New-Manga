//! M2-AC1 acceptance bridge (doc/tasks/M2-AC1.md).
//!
//! A second Core sidecar — `python -m bootstrap.acceptance_bridge` — that
//! drives the deterministic acceptance loop (Mock/Local pipeline → SQLite
//! persistence → restart → restore → Reader → PNG export) over the same
//! stdio JSON-lines wire shape as the resource-channel control bridge.
//!
//! Surface discipline (Task 禁止范围): this channel is spawned ONLY when the
//! host is started in the explicit test configuration (`M2AC1_TEST_MODE=1`),
//! and its commands are registered only in that mode. The production command
//! surface (`PRODUCTION_COMMANDS` in main.rs) never gains them.

use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::Mutex;

#[derive(Debug, Clone)]
pub struct Ac1Error {
    pub code: String,
}

impl Ac1Error {
    pub fn new(code: &str) -> Self {
        Self { code: code.to_string() }
    }
}

fn decode_response(line: &str) -> Result<serde_json::Value, Ac1Error> {
    let value: serde_json::Value =
        serde_json::from_str(line).map_err(|_| Ac1Error::new("AC1_BRIDGE_MALFORMED"))?;
    if let Some(error) = value.get("error") {
        let code = error
            .get("code")
            .and_then(|c| c.as_str())
            .unwrap_or("AC1_BRIDGE_MALFORMED")
            .to_string();
        return Err(Ac1Error { code });
    }
    Ok(value.get("result").cloned().unwrap_or(serde_json::Value::Null))
}

// Keep this test-only channel's current wire form; drift must surface instead of silently changing the contract.
fn ascii_only_request_line(request: &serde_json::Value) -> Result<String, Ac1Error> {
    let line = request.to_string();
    if !line.is_ascii() {
        return Err(Ac1Error::new("AC1_BRIDGE_NON_ASCII_PAYLOAD"));
    }
    Ok(line)
}

/// The acceptance Core sidecar. One request at a time (the acceptance loop
/// is strictly sequential); `round_trip` serialises through the mutexes.
pub struct Ac1Channel {
    child: Mutex<Child>,
    stdin: Mutex<ChildStdin>,
    stdout: Mutex<BufReader<ChildStdout>>,
}

/// The acceptance sidecar argv shape, pinned here and unit-tested (F-011,
/// DSH r1): the module must be `bootstrap.acceptance_bridge`, never the
/// production resource-channel control plane.
pub fn spawn_args() -> Vec<&'static str> {
    vec!["-m", "bootstrap.acceptance_bridge"]
}

impl Ac1Channel {
    /// Spawn `python -m bootstrap.acceptance_bridge` with the repository
    /// `src` on the module path. The child inherits the host environment
    /// (NEWMANGA_DATA_ROOT, M2AC1_TEST_MODE, M2RC2_CATALOG_DB), so the data
    /// root isolation is decided entirely by the runner-supplied env.
    pub fn spawn(
        python_exe: &str,
        src_root: &std::path::Path,
    ) -> Result<Self, Ac1Error> {
        // M2-RG1 AC2: Command-construction section only — CREATE_NO_WINDOW on
        // Windows; argv/cwd/env/stdio semantics unchanged.
        let mut cmd = Command::new(python_exe);
        cmd.args(spawn_args())
            .current_dir(src_root)
            .env("PYTHONPATH", src_root)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit());
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x0800_0000;
            cmd.creation_flags(CREATE_NO_WINDOW);
        }
        let mut child = cmd
            .spawn()
            .map_err(|error| Ac1Error { code: format!("AC1_SPAWN_FAILED:{error}") })?;
        let stdin = child
            .stdin
            .take()
            .ok_or_else(|| Ac1Error::new("AC1_SPAWN_FAILED"))?;
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| Ac1Error::new("AC1_SPAWN_FAILED"))?;
        Ok(Self {
            child: Mutex::new(child),
            stdin: Mutex::new(stdin),
            stdout: Mutex::new(BufReader::new(stdout)),
        })
    }

    pub fn round_trip(
        &self,
        method: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value, Ac1Error> {
        let request = serde_json::json!({ "id": 1, "method": method, "params": params });
        let mut line = ascii_only_request_line(&request)?;
        line.push('\n');
        {
            let mut stdin = self.stdin.lock().unwrap();
            stdin
                .write_all(line.as_bytes())
                .map_err(|_| Ac1Error::new("AC1_BRIDGE_DOWN"))?;
            stdin
                .flush()
                .map_err(|_| Ac1Error::new("AC1_BRIDGE_DOWN"))?;
        }
        let mut response_line = String::new();
        {
            let mut stdout = self.stdout.lock().unwrap();
            stdout
                .read_line(&mut response_line)
                .map_err(|_| Ac1Error::new("AC1_BRIDGE_DOWN"))?;
        }
        if response_line.is_empty() {
            return Err(Ac1Error::new("AC1_BRIDGE_DOWN"));
        }
        decode_response(response_line.trim_end())
    }
}

impl Drop for Ac1Channel {
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn non_ascii_payload_returns_visible_error_code() {
        let error = ascii_only_request_line(&serde_json::json!({ "title": "雾港来信" }))
            .expect_err("non-ASCII payload must fail");
        assert_eq!(error.code, "AC1_BRIDGE_NON_ASCII_PAYLOAD");
    }

    /// Wire shape: the request line carries id/method/params only; a typed
    /// error response decodes to `Ac1Error` with the Core-side code.
    #[test]
    fn decode_response_maps_typed_errors() {
        let error = decode_response(r#"{"id":1,"error":{"code":"AC1_NOT_SEEDED"}}"#)
            .unwrap_err();
        assert_eq!(error.code, "AC1_NOT_SEEDED");
        let value =
            decode_response(r#"{"id":1,"result":{"pong":true}}"#).expect("result decodes");
        assert_eq!(value.get("pong").and_then(|p| p.as_bool()), Some(true));
    }

    /// The spawn argv literally targets the acceptance bridge module (F-011,
    /// DSH r1: the original test name promised this but only asserted the
    /// failure path; the argv is now pinned as data).
    #[test]
    fn spawn_args_target_the_acceptance_module() {
        assert_eq!(
            spawn_args(),
            vec!["-m", "bootstrap.acceptance_bridge"],
            "the acceptance channel must spawn bootstrap.acceptance_bridge, \
             never the resource-channel control plane"
        );
    }

    /// A bogus python executable fails the spawn with the typed code.
    #[test]
    fn spawn_fails_typed_on_missing_python() {
        let error = Ac1Channel::spawn(
            "definitely-not-a-real-python-executable",
            std::path::Path::new("."),
        )
        .err()
        .expect("a bogus python executable must fail the spawn");
        assert!(error.code.starts_with("AC1_SPAWN_FAILED"));
    }
}
