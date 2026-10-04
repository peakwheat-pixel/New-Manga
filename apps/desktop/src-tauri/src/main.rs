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
//! production-only `settings_get`/`settings_update_section` pair, and
//! M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4) the production-only
//! `set_region_type`/`list_regions` pair — the production surface is pinned
//! at exactly nine commands by unit test.

// console note (updated M2-RG1 r1 rework, P3-1): dev builds keep the console
// on purpose — probe evidence includes startup stderr. Release builds are
// GUI-subsystem (windows_subsystem attribute above); the sidecar spawn points
// carry CREATE_NO_WINDOW, so on Windows the packaged app and its sidecars
// surface no console window while stdio (pipe) semantics stay unchanged.

mod ac1_bridge;
mod core_bridge;
mod library_bridge;
mod resource_protocol;

use ac1_bridge::Ac1Channel;
use core_bridge::{CoreChannel, CoreError, StdioCoreChannel};
use library_bridge::{BookSummary, LibraryChannel, PingResult, StdioLibraryChannel};
use resource_protocol::{ScopeRoots};
use serde::Serialize;
use std::path::PathBuf;
use std::sync::Arc;
use tauri::Manager;

/// Commands every mode exposes: the product WebView surface. No path-shaped
/// parameter, no TTL parameter, no probe capability.
pub const PRODUCTION_COMMANDS: &[&str] = &[
    "issue_resource_url",
    "revoke_ref",
    "revoke_resource_refs",
    "core_ping",
    "library_list_books",
    // M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): the settings read/
    // write pair, production-only like the IPC1 commands below.
    "settings_get",
    "settings_update_section",
    // M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): the region retype
    // write/read pair, production-only like the settings pair above.
    "set_region_type",
    "list_regions",
];

/// Commands that exist ONLY in probe mode (`M2RC1_PROBE_OUT` set by the
/// evidence runner). In production mode they are not registered, so a
/// WebView invoke fails with "command not found" before any logic runs.
pub const PROBE_ONLY_COMMANDS: &[&str] =
    &["probe_config", "probe_write_results", "probe_exit", "probe_issue_url"];

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
pub const SETTINGS_PRODUCTION_ONLY_COMMANDS: &[&str] =
    &["settings_get", "settings_update_section"];

/// M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): the region retype pair is
/// production-only as well (same option-B precedent — the frozen test-mode
/// surfaces keep their historical shape).
pub const RETYPE_PRODUCTION_ONLY_COMMANDS: &[&str] =
    &["set_region_type", "list_regions"];

pub fn command_allowlist(probe_mode: bool, ac1_mode: bool) -> Vec<&'static str> {
    let mut commands: Vec<&'static str> = if probe_mode || ac1_mode {
        PRODUCTION_COMMANDS
            .iter()
            .copied()
            .filter(|command| {
                !IPC1_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !SETTINGS_PRODUCTION_ONLY_COMMANDS.contains(command)
                    && !RETYPE_PRODUCTION_ONLY_COMMANDS.contains(command)
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
fn revoke_resource_refs(state: tauri::State<'_, AppState>, resource_id: String) -> Result<u32, String> {
    state.channel.revoke_resource(&resource_id).map_err(|error| error.code)
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
        Some(root) => {
            env_path("M2RC1_DERIVED_ROOT").unwrap_or_else(|| {
                let path = root.join("derived");
                ensure_dir(&path);
                path
            })
        }
        None => env_path("M2RC1_DERIVED_ROOT").expect("M2RC1_DERIVED_ROOT required"),
    };
    let managed_root = match &user_root {
        Some(root) => {
            env_path("M2RC1_MANAGED_ROOT").unwrap_or_else(|| {
                let path = root.join("managed");
                ensure_dir(&path);
                path
            })
        }
        None => env_path("M2RC1_MANAGED_ROOT").expect("M2RC1_MANAGED_ROOT required"),
    };
    // RC2 (F-03): the app refuses to run without its catalog authority. The
    // launcher seeds the Core/SQLite store (catalog_loader in packaged form)
    // and passes the path; without it every issue would fail closed anyway.
    let catalog_db = match &user_root {
        Some(root) => {
            env_path("M2RC2_CATALOG_DB").unwrap_or_else(|| {
                let path = root.join("catalog").join("catalog.sqlite");
                ensure_dir(path.parent().unwrap_or(root));
                path
            })
        }
        None => env_path("M2RC2_CATALOG_DB")
            .expect("M2RC2_CATALOG_DB required (Core/SQLite catalog authority)"),
    };
    // the embedded page URL has no query string, so the probe mode switch is
    // the presence of M2RC1_PROBE_OUT (set only by the evidence runner)
    let probe_mode = std::env::var("M2RC1_PROBE_OUT").is_ok();
    // M2-AC1: the acceptance mode is its own explicit test startup
    // configuration — never combined with the RC1 probe mode.
    let ac1_mode = !probe_mode && std::env::var("M2AC1_TEST_MODE").as_deref() == Ok("1");

    // M2-AC5 packaged-vs-dev spawn dispatch. The library/acceptance bridges
    // keep their frozen `spawn(python_exe, src_root, ...)` signatures (their
    // files are outside this task's allowed paths): in packaged mode the
    // arguments are repointed at the frozen exes — the PyInstaller entry
    // wrappers ignore the `-m <module>` argv, and the sidecar dir as
    // cwd/PYTHONPATH is inert — so the channel code stays untouched.
    let channel = match &packaged_dir {
        Some(dir) => StdioCoreChannel::spawn_packaged(
            &dir.join("host_bridge.exe"),
            &derived_root,
            &managed_root,
            &catalog_db,
        ),
        None => StdioCoreChannel::spawn(
            &python_exe, &src_root, &derived_root, &managed_root, &catalog_db,
        ),
    }
    .expect("python core sidecar failed to start");
    let ac1 = if ac1_mode {
        Some(
            match &packaged_dir {
                Some(dir) => Ac1Channel::spawn(
                    &dir.join("acceptance_bridge.exe").to_string_lossy(),
                    dir,
                ),
                None => Ac1Channel::spawn(&python_exe, &src_root),
            }
            .expect("acceptance core sidecar failed to start"),
        )
    } else {
        None
    };
    let data_root = match &user_root {
        Some(root) => Some(env_path("NEWMANGA_DATA_ROOT").unwrap_or_else(|| {
            let path = root.join("data");
            ensure_dir(&path);
            path
        })),
        None => env_path("NEWMANGA_DATA_ROOT"),
    };
    let is_production = !probe_mode && !ac1_mode;
    let library: Option<Box<dyn LibraryChannel>> = if is_production {
        let chan = match &packaged_dir {
            Some(dir) => StdioLibraryChannel::spawn(
                &dir.join("core_service.exe").to_string_lossy(),
                dir,
                data_root.as_deref(),
            ),
            None => StdioLibraryChannel::spawn(
                &python_exe,
                &src_root,
                data_root.as_deref(),
            ),
        }
        .expect("production core library sidecar failed to start");
        Some(Box::new(chan))
    } else {
        None
    };

    let state = AppState {
        channel: Box::new(channel),
        roots: ScopeRoots { derived: derived_root, managed: managed_root },
        fixture_shas: fixture_shas(),
        ac1,
        library,
    };

    let builder = tauri::Builder::default()
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
            settings_get,
            settings_update_section,
            set_region_type,
            list_regions
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
    use crate::resource_protocol::{
        build_url, handle_m2res_request, ScopeRoots, CHUNK_SIZE, ID_LENGTH,
    };
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
    /// artifact: the app manifest declares exactly the ten live commands
    /// (seven resource-channel + three M2-AC1 acceptance; R2-06),
    /// and no plugin-shaped surface remains.
    #[test]
    fn app_acl_manifest_is_generated_and_enforced() {
        let manifest: serde_json::Value = serde_json::from_str(
            include_str!("../gen/schemas/acl-manifests.json"),
        )
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
        for command in command_allowlist(true, false)
            .into_iter()
            .chain(command_allowlist(false, true))
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
    fn production_surface_is_exactly_nine_commands() {
        // M2-SETTINGS-IPC-CHANNEL: five -> seven (settings_get +
        // settings_update_section, contract rev 1.3 §5.3; pinned wire names)
        // M2-REGION-RETYPE-CORE: seven -> nine (set_region_type +
        // list_regions, contract rev 1.4 §5.4; pinned wire names)
        assert_eq!(
            command_allowlist(false, false),
            vec![
                "issue_resource_url",
                "revoke_ref",
                "revoke_resource_refs",
                "core_ping",
                "library_list_books",
                "settings_get",
                "settings_update_section",
                "set_region_type",
                "list_regions",
            ]
        );
    }

    #[test]
    fn probe_surface_adds_exactly_the_four_probe_commands() {
        let probe = command_allowlist(true, false);
        for command in PROBE_ONLY_COMMANDS {
            assert!(probe.contains(command), "{command} missing from probe surface");
        }
        // M2-IPC1 ruling (DSH r2 P2-1 option B): test modes keep the frozen
        // RC2 surface — the production-only IPC1 commands are absent.
        for command in IPC1_PRODUCTION_ONLY_COMMANDS {
            assert!(!probe.contains(command), "{command} must stay production-only");
        }
        // M2-SETTINGS-IPC-CHANNEL: the settings pair is production-only too
        for command in SETTINGS_PRODUCTION_ONLY_COMMANDS {
            assert!(!probe.contains(command), "{command} must stay production-only");
        }
        // M2-REGION-RETYPE-CORE: the retype pair is production-only too
        for command in RETYPE_PRODUCTION_ONLY_COMMANDS {
            assert!(!probe.contains(command), "{command} must stay production-only");
        }
        assert_eq!(
            probe.len(),
            PRODUCTION_COMMANDS.len()
                - IPC1_PRODUCTION_ONLY_COMMANDS.len()
                - SETTINGS_PRODUCTION_ONLY_COMMANDS.len()
                - RETYPE_PRODUCTION_ONLY_COMMANDS.len()
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
            assert!(!ac1.contains(command), "{command} must stay production-only");
        }
        // M2-SETTINGS-IPC-CHANNEL: the settings pair is production-only too
        for command in SETTINGS_PRODUCTION_ONLY_COMMANDS {
            assert!(!ac1.contains(command), "{command} must stay production-only");
        }
        // M2-REGION-RETYPE-CORE: the retype pair is production-only too
        for command in RETYPE_PRODUCTION_ONLY_COMMANDS {
            assert!(!ac1.contains(command), "{command} must stay production-only");
        }
        assert_eq!(
            ac1.len(),
            PRODUCTION_COMMANDS.len()
                - IPC1_PRODUCTION_ONLY_COMMANDS.len()
                - SETTINGS_PRODUCTION_ONLY_COMMANDS.len()
                - RETYPE_PRODUCTION_ONLY_COMMANDS.len()
                + AC1_TEST_COMMANDS.len()
        );
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
        assert!(channel.issue_probe("res-never", "rev-1", 5.0).unwrap_err().code == "RESOURCE_NOT_CATALOGED");
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
            assert_eq!(std::str::from_utf8(&response.body).unwrap(), "{\"code\":\"REF_MALFORMED\"}");
        }
    }

    #[test]
    fn unknown_well_formed_id_typed_404() {
        let (env, _sha) = env_with_fixture(b"payload");
        let well_formed = "A".repeat(ID_LENGTH).replace('A', "a");
        let response = handle_m2res_request(&url_for(&well_formed, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.status, 404);
        assert_eq!(std::str::from_utf8(&response.body).unwrap(), "{\"code\":\"REF_UNKNOWN_ID\"}");
    }

    #[test]
    fn chunk_offset_beyond_size_rejected() {
        let (env, _sha) = env_with_fixture(b"tiny payload");
        let opaque = registered(&env, "res-001", "asset.png", b"tiny payload");
        let response = handle_m2res_request(&url_for(&opaque, Some(1)), &env.channel, &env.roots);
        assert_eq!(response.status, 400);
        let body = std::str::from_utf8(&response.body).unwrap();
        assert!(body.contains("REF_MALFORMED") || body.contains("REF_UNKNOWN_ID"), "{body}");
    }

    #[test]
    fn responses_carry_no_store() {
        let (env, _sha) = env_with_fixture(b"payload");
        let well_formed = "b".repeat(ID_LENGTH).replace('b', "c");
        let response = handle_m2res_request(&url_for(&well_formed, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.cache_control, "no-store");
    }

    #[test]
    fn revoked_id_propagates_typed_410() {
        let (env, _sha) = env_with_fixture(b"payload");
        let opaque = registered(&env, "res-001", "asset.png", b"payload");
        env.channel.revoke(&opaque).unwrap();
        let response = handle_m2res_request(&url_for(&opaque, Some(0)), &env.channel, &env.roots);
        assert_eq!(response.status, 410);
        assert_eq!(std::str::from_utf8(&response.body).unwrap(), "{\"code\":\"REF_REVOKED\"}");
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
        assert_eq!(std::str::from_utf8(&second.body).unwrap(), "{\"code\":\"FILE_IDENTITY_CHANGED\"}");
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
        assert_eq!(second.status, 410, "revoked URL must not be served from cache");
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
        let facts = resource_protocol::capture_facts_for_tests(&env.roots.derived.join("asset.png"))
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
        assert_eq!(second.status, 410, "expired URL must not be served from cache");
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
        let existing = std::fs::OpenOptions::new().write(true).open(&target).unwrap();
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
            let existing = std::fs::OpenOptions::new().write(true).open(&target).unwrap();
            {
                use std::io::{Seek, SeekFrom};
                let mut existing = existing;
                existing.seek(SeekFrom::Start(0)).unwrap();
                existing.write_all(&flipped).unwrap();
            }

            let second = handle_m2res_request(&url, &env.channel, &env.roots);
            assert_eq!(second.status, 400, "round {round}: rewritten content must not be served");
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
        let seed = std::process::Command::new(&python)
            .arg("-m")
            .arg("infrastructure.resource_channel.catalog_loader")
            .current_dir(&src_root)
            .arg("--db")
            .arg(&catalog_db)
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
        let seed = std::process::Command::new(&python)
            .arg("-m")
            .arg("infrastructure.resource_channel.catalog_loader")
            .current_dir(&src_root)
            .arg("--db")
            .arg(&catalog_db)
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
        assert!(ping.capabilities.contains(&"library.list_books".to_string()));

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

        let channel = StdioLibraryChannel::spawn(
            &python,
            &src_root,
            Some(&data_root),
        )
        .expect("library sidecar spawn");

        // 1. Ping round-trip succeeds
        let ping = channel.ping().expect("ping");
        assert_eq!(ping.status, "ready");
        assert_eq!(ping.protocol_version.major, 1);
        // M2-PROD-DETECT-3 integration (DSH r1 R4): protocol minor bump
        // 1.0 -> 1.1 (core.detect added); M2-SETTINGS-IPC-CHANNEL: 1.1 -> 2
        // (settings_get/settings_update_section added);
        // M2-REGION-RETYPE-CORE: 2 -> 3 (set_region_type/list_regions
        // added). This real-sidecar assertion is the consequence sync for
        // the widenings. The MockChannel self-consistency stub above (:1194)
        // keeps its own minor 0 by design.
        assert_eq!(ping.protocol_version.minor, 3);
        assert!(ping.capabilities.contains(&"library.list_books".to_string()));

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

        let channel = StdioLibraryChannel::spawn(
            &python,
            &src_root,
            Some(&data_root),
        )
        .expect("library sidecar spawn");

        // 1. full projection read on a fresh install
        let full = channel.get_settings(None).expect("full settings read");
        assert!(full.get("settings").is_some(), "projection envelope: {full}");

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
        let still = channel.get_settings(Some("sfx")).expect("read after reject");
        assert_eq!(still["settings"]["sfx"]["policy"], "translate");
    }

    // ---- M2-AC5: packaged-mode resolution (fail-closed spawn) -------------

    /// The explicit `M2RC1_PACKAGED=1` switch resolves the sidecar dir from
    /// the running exe's directory, even before any sidecar exe is checked.
    #[test]
    fn packaged_resolution_explicit_flag_wins() {
        let dir = tempfile::tempdir().unwrap();
        let resolved = resolve_packaged_sidecar_dir(Some("1"), None, Some(dir.path()));
        assert_eq!(resolved, Some(dir.path().join("resources").join("core-sidecar")));
        // explicit flag wins over a dev src_root too
        let resolved =
            resolve_packaged_sidecar_dir(Some("1"), Some("G:/repo/src"), Some(dir.path()));
        assert_eq!(resolved, Some(dir.path().join("resources").join("core-sidecar")));
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
        let resolved =
            resolve_packaged_sidecar_dir(None, Some("G:/repo/src"), Some(dir.path()));
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
