//! M2-RC1 — Contract-Aligned Large-Media Resource Channel Runtime.
//!
//! Vertical slice: Python Core (reference authority) ⇄ Tauri/Rust host
//! (`m2res` custom protocol over a stdio control bridge) ⇄ React/WebView
//! (opaque protocol URLs only). Bytes stay outside the JSON/Base64 IPC plane
//! (Contract 1.1 §10); the WebView never sees an OS path (T5.1).

// console kept visible on purpose: probe evidence includes startup stderr

mod core_bridge;
mod resource_protocol;

use core_bridge::{CoreChannel, CoreError, StdioCoreChannel};
use resource_protocol::{GrantCache, ScopeRoots};
use serde::Serialize;
use std::path::PathBuf;
use std::sync::Arc;
use tauri::Manager;

struct AppState {
    channel: Box<dyn CoreChannel>,
    cache: GrantCache,
    roots: ScopeRoots,
    fixture_shas: serde_json::Value,
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
fn register_catalog(state: tauri::State<'_, AppState>, resource_id: String, rel_path: String) -> Result<(), String> {
    state
        .channel
        .register(&resource_id, &rel_path)
        .map_err(|error| error.code)
}

#[tauri::command]
fn issue_resource_url(
    state: tauri::State<'_, AppState>,
    resource_id: String,
    revision: String,
    ttl_override: Option<f64>,
) -> Result<IssuedUrl, String> {
    let issued = state
        .channel
        .issue(&resource_id, &revision, ttl_override)
        .map_err(|error| error.code)?;
    into_issued(issued).map_err(|error| error.code)
}

#[tauri::command]
fn revoke_ref(state: tauri::State<'_, AppState>, opaque_id: String) -> Result<(), String> {
    state.channel.revoke(&opaque_id).map_err(|error| error.code)
}

#[tauri::command]
fn revoke_resource_refs(state: tauri::State<'_, AppState>, resource_id: String) -> Result<u32, String> {
    state.channel.revoke_resource(&resource_id).map_err(|error| error.code)
}

#[tauri::command]
fn probe_config(state: tauri::State<'_, AppState>) -> serde_json::Value {
    // the embedded page URL has no query string, so the probe mode switch is
    // the presence of M2RC1_PROBE_OUT (set only by the evidence runner)
    let probe_auto = std::env::var("M2RC1_PROBE_OUT").is_ok();
    serde_json::json!({
        "probe_auto": probe_auto,
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

fn env_path(name: &str) -> Option<PathBuf> {
    std::env::var(name).ok().map(PathBuf::from)
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
    let python_exe = std::env::var("M2RC1_PYTHON").unwrap_or_else(|_| "python".to_string());
    let src_root = env_path("M2RC1_SRC_ROOT").expect("M2RC1_SRC_ROOT must point at the repo src dir");
    let derived_root = env_path("M2RC1_DERIVED_ROOT").expect("M2RC1_DERIVED_ROOT required");
    let managed_root = env_path("M2RC1_MANAGED_ROOT").expect("M2RC1_MANAGED_ROOT required");

    let channel = StdioCoreChannel::spawn(&python_exe, &src_root, &derived_root, &managed_root)
        .expect("python core sidecar failed to start");
    let state = AppState {
        channel: Box::new(channel),
        cache: GrantCache::default(),
        roots: ScopeRoots { derived: derived_root, managed: managed_root },
        fixture_shas: fixture_shas(),
    };

    tauri::Builder::default()
        .setup(|app| {
            // progress channel: mirror the page's window title to stderr so
            // the runner can observe probe progress without the invoke bridge
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                for _ in 0..90 {
                    std::thread::sleep(std::time::Duration::from_secs(2));
                    for window in handle.webview_windows().values() {
                        let title = window.title().unwrap_or_default();
                        eprintln!("[m2rc1-title] {title}");
                    }
                }
            });
            Ok(())
        })
        .manage(state)
        .register_uri_scheme_protocol("m2res", |ctx, request| {
            let state = ctx.app_handle().state::<AppState>();
            let uri = request.uri().to_string();
            let response =
                resource_protocol::handle_m2res_request(&uri, state.channel.as_ref(), &state.cache, &state.roots);
            let mut builder = tauri::http::Response::builder()
                .status(response.status)
                .header("Content-Type", response.content_type)
                .header("Cache-Control", response.cache_control)
                .header("Access-Control-Allow-Origin", "*");
            if response.status == 206 || !response.body.is_empty() {
                builder = builder.header("X-M2RC1-Served", "chunk");
            }
            builder.body(response.body).unwrap()
        })
        .invoke_handler(tauri::generate_handler![
            register_catalog,
            issue_resource_url,
            revoke_ref,
            revoke_resource_refs,
            probe_config,
            probe_write_results,
            probe_exit
        ])
        .run(tauri::generate_context!())
        .expect("error while running M2-RC1 desktop runtime");
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core_bridge::MockCoreChannel;
    use crate::resource_protocol::{
        build_url, handle_m2res_request, ScopeRoots, GrantCache, CHUNK_SIZE, ID_LENGTH,
    };
    use std::io::Write;

    struct TestEnv {
        roots: ScopeRoots,
        channel: MockCoreChannel,
        cache: GrantCache,
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
            roots: ScopeRoots { derived, managed },
            channel: MockCoreChannel::new(),
            cache: GrantCache::default(),
        };
        // leak the tempdir for the duration of the test scope
        std::mem::forget(dir);
        (env, sha)
    }

    fn url_for(id: &str, chunk: Option<u64>) -> String {
        let base = build_url(id);
        match chunk {
            Some(n) => format!("{base}?chunk={n}"),
            None => base,
        }
    }

    fn registered(env: &TestEnv, rel: &str, payload: &[u8]) -> String {
        let sha = write_resource(&env.roots.derived, rel, payload);
        env.channel.register("res-001", rel).unwrap();
        let issued = env.channel.issue("res-001", "rev-1", None).unwrap();
        // make the mock grant match the real file so handle verification passes
        let opaque = issued.opaque_id.clone();
        let mut table = env.channel.table.lock().unwrap();
        let entry = table.get_mut(&opaque).unwrap();
        entry.grant.size = payload.len() as u64;
        entry.grant.sha256 = sha;
        let metadata = std::fs::metadata(env.roots.derived.join(rel)).unwrap();
        // capture real identity via the same helper the product uses
        drop(table);
        let (volume, index, _size) =
            resource_protocol::capture_facts_for_tests(&env.roots.derived.join(rel))
                .expect("issue-time facts from fixture handle");
        let mut table = env.channel.table.lock().unwrap();
        let entry = table.get_mut(&opaque).unwrap();
        entry.grant.volume_serial = volume;
        entry.grant.file_index = index;
        let _ = metadata;
        opaque
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
            let response = handle_m2res_request(&url_for(bad, Some(0)), &env.channel, &env.cache, &env.roots);
            assert_eq!(response.status, 400, "id {bad:?}");
            assert_eq!(std::str::from_utf8(&response.body).unwrap(), "{\"code\":\"REF_MALFORMED\"}");
        }
    }

    #[test]
    fn unknown_well_formed_id_typed_404() {
        let (env, _sha) = env_with_fixture(b"payload");
        let well_formed = "A".repeat(ID_LENGTH).replace('A', "a");
        let response = handle_m2res_request(&url_for(&well_formed, Some(0)), &env.channel, &env.cache, &env.roots);
        assert_eq!(response.status, 404);
        assert_eq!(std::str::from_utf8(&response.body).unwrap(), "{\"code\":\"REF_UNKNOWN_ID\"}");
    }

    #[test]
    fn chunk_offset_beyond_size_rejected() {
        let (env, _sha) = env_with_fixture(b"tiny payload");
        let opaque = registered(&env, "asset.png", b"tiny payload");
        let response = handle_m2res_request(&url_for(&opaque, Some(1)), &env.channel, &env.cache, &env.roots);
        assert_eq!(response.status, 400);
        let body = std::str::from_utf8(&response.body).unwrap();
        assert!(body.contains("REF_MALFORMED") || body.contains("REF_UNKNOWN_ID"), "{body}");
    }

    #[test]
    fn responses_carry_no_store() {
        let (env, _sha) = env_with_fixture(b"payload");
        let well_formed = "b".repeat(ID_LENGTH).replace('b', "c");
        let response = handle_m2res_request(&url_for(&well_formed, Some(0)), &env.channel, &env.cache, &env.roots);
        assert_eq!(response.cache_control, "no-store");
    }

    #[test]
    fn revoked_id_propagates_typed_410() {
        let (env, _sha) = env_with_fixture(b"payload");
        let opaque = registered(&env, "asset.png", b"payload");
        env.channel.revoke(&opaque).unwrap();
        let response = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.cache, &env.roots);
        assert_eq!(response.status, 410);
        assert_eq!(std::str::from_utf8(&response.body).unwrap(), "{\"code\":\"REF_REVOKED\"}");
    }

    #[test]
    fn full_chunk_serving_matches_bytes_and_digest_check() {
        let payload: Vec<u8> = (0..64_000u32).map(|i| (i % 251) as u8).collect();
        let (env, sha) = env_with_fixture(&payload);
        let opaque = registered(&env, "asset.png", &payload);
        assert_eq!(sha.len(), 64);
        let response = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.cache, &env.roots);
        assert_eq!(response.status, 200);
        assert_eq!(response.body.len(), payload.len());
        assert_eq!(&response.body[..], &payload[..]);
        assert_eq!(response.cache_control, "no-store");
    }

    #[test]
    fn identity_change_invalidates_cache_entry() {
        let payload = b"payload-v1".to_vec();
        let (env, _sha) = env_with_fixture(&payload);
        let opaque = registered(&env, "asset.png", &payload);
        // first request verifies and caches
        let first = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.cache, &env.roots);
        assert_eq!(first.status, 200);
        // replace with a *new* file (unlink first: an in-place overwrite keeps
        // the same NTFS file index, the M2-S2 lesson)
        let replaced = b"payload-v2-with-different-length!!";
        let target = env.roots.derived.join("asset.png");
        std::fs::remove_file(&target).unwrap();
        std::fs::write(&target, replaced).unwrap();
        let second = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.cache, &env.roots);
        assert_eq!(second.status, 400);
        assert_eq!(std::str::from_utf8(&second.body).unwrap(), "{\"code\":\"FILE_IDENTITY_CHANGED\"}");
    }

    /// Integration with the real Python Core sidecar: exercises the stdio
    /// JSON-lines bridge end to end (issue -> resolve -> grant facts).
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

        let channel = StdioCoreChannel::spawn(
            &python,
            &src_root,
            &derived,
            &dir.path().join("scope").join("managed"),
        )
        .expect("sidecar spawn");
        channel.register("res-sidecar", "asset.png").unwrap();
        let issued = channel.issue("res-sidecar", "rev-1", None).expect("issue");
        assert!(issued.opaque_id.starts_with("m2id.v1."));
        let grant = channel.resolve(&issued.opaque_id).expect("resolve");
        assert_eq!(grant.rel_path, "asset.png");
        assert_eq!(grant.size, 15);
        assert_eq!(grant.sha256.len(), 64);
        channel.revoke(&issued.opaque_id).unwrap();
        let error = channel.resolve(&issued.opaque_id).unwrap_err();
        assert_eq!(error.code, "REF_REVOKED");
    }
}
