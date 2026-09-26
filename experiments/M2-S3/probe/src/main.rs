// M2-S3 isolated Tauri asset-protocol feasibility probe (research instrument).
//
// NOT product code. It exists only to answer S1-B1: can a real Tauri/WebView2
// custom-scheme asset protocol serve restricted derived-cache bytes under the
// Contract 1.1 T5/T6 semantics (opaque mapping ID in the WebView, typed
// rejections, no path leakage, revocation/expiry on next resolve, in-flight
// reads not interrupted)?
//
// Design notes:
// - The WebView-visible reference is an opaque random mapping ID
//   (`m2res://.../m2id/<id>`; on Windows Tauri serves custom schemes over
//   `http://m2res.localhost/...`). The Rust "host" layer holds the only
//   ID -> (relative path, TTL, revoked) table -- the M2-S2 MappingIdAuthority
//   shape, re-prototyped in Rust.
// - The built-in Tauri `asset:` protocol (convertFileSrc) is deliberately NOT
//   used: it requires the WebView to hold an OS path, which Contract 1.1 T5.1
//   forbids. This probe registers a custom scheme instead.
// - Error responses carry a stable code in a JSON body only; no OS path, no
//   table contents, no fixture bytes ever leave the host in an error.
// - Resolve containment is re-derived from the filesystem (canonicalize) at
//   request time, mirroring the M2-S2 handle-verified containment layer in a
//   simplified form (full TOCTOU handle semantics are out of scope here; the
//   product would open-then-verify per Contract 1.1 §10.2).

// console kept visible on purpose: probe evidence includes startup stderr
// #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use base64::engine::general_purpose::URL_SAFE_NO_PAD as B64;
use base64::Engine;
use rand::RngCore;
use serde::Serialize;
use tauri::Manager;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use std::time::{Duration, Instant};

const SCHEME: &str = "m2res";
const HOST: &str = "m2res.localhost";
const EXP_TTL: Duration = Duration::from_millis(2500);

#[derive(Clone, Copy, PartialEq)]
enum CachePolicy {
    NoStore,
    Bare,
}

struct Entry {
    rel: PathBuf,
    revoked: bool,
    expires_at: Option<Instant>,
    cache_policy: CachePolicy,
}

struct ProbeState {
    lab: PathBuf,
    scope_root: PathBuf,
    table: Mutex<HashMap<String, Entry>>,
    issue_guard: Mutex<Option<String>>, // host-side refusal for the user-source fixture
}

#[derive(Serialize)]
struct ProbeStateJson {
    scheme_base: String,
    ids: std::collections::BTreeMap<String, String>,
    expiring_ttl_ms: u64,
    fixtures: std::collections::BTreeMap<String, String>, // name -> sha256
    issue_guard: Option<String>,                          // host-side user-source refusal code
}

fn b64_id() -> String {
    let mut bytes = [0u8; 32]; // 256-bit random -> 43-char base64url opaque ID
    rand::thread_rng().fill_bytes(&mut bytes);
    B64.encode(bytes)
}

fn sha256_hex(data: &[u8]) -> String {
    use std::fmt::Write;
    // tiny SHA-256 to avoid pulling a crypto crate into the probe
    let mut h = Sha256::new();
    h.update(data);
    let digest = h.finish();
    let mut out = String::with_capacity(64);
    for b in digest {
        write!(out, "{:02x}", b).unwrap();
    }
    out
}

// Minimal SHA-256 (FIPS 180-4), probe-only.
struct Sha256 {
    state: [u32; 8],
    buffer: [u8; 64],
    buffer_len: usize,
    total_len: u64,
}

impl Sha256 {
    fn new() -> Self {
        Self {
            state: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
                0x5be0cd19,
            ],
            buffer: [0u8; 64],
            buffer_len: 0,
            total_len: 0,
        }
    }

    fn update(&mut self, mut data: &[u8]) {
        self.total_len = self.total_len.wrapping_add(data.len() as u64);
        if self.buffer_len > 0 {
            let need = 64 - self.buffer_len;
            let take = need.min(data.len());
            self.buffer[self.buffer_len..self.buffer_len + take].copy_from_slice(&data[..take]);
            self.buffer_len += take;
            data = &data[take..];
            if self.buffer_len == 64 {
                let block = self.buffer;
                self.compress(&block);
                self.buffer_len = 0;
            }
        }
        while data.len() >= 64 {
            let mut block = [0u8; 64];
            block.copy_from_slice(&data[..64]);
            self.compress(&block);
            data = &data[64..];
        }
        if !data.is_empty() {
            self.buffer[..data.len()].copy_from_slice(data);
            self.buffer_len = data.len();
        }
    }

    fn finish(mut self) -> [u8; 32] {
        let bit_len = self.total_len.wrapping_mul(8);
        self.update(&[0x80]);
        while self.buffer_len != 56 {
            self.update(&[0x00]);
        }
        self.update(&bit_len.to_be_bytes());
        let mut out = [0u8; 32];
        for (i, word) in self.state.iter().enumerate() {
            out[i * 4..i * 4 + 4].copy_from_slice(&word.to_be_bytes());
        }
        out
    }

    fn compress(&mut self, block: &[u8; 64]) {
        const K: [u32; 64] = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
            0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
            0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
            0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
            0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
            0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
            0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
            0xc67178f2,
        ];
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                block[i * 4],
                block[i * 4 + 1],
                block[i * 4 + 2],
                block[i * 4 + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut h] = self.state;
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = h
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(t1);
            d = c;
            c = b;
            b = a;
            a = t1.wrapping_add(t2);
        }
        let input = [a, b, c, d, e, f, g, h];
        for (s, v) in self.state.iter_mut().zip(input) {
            *s = s.wrapping_add(v);
        }
    }
}

// ---------------------------------------------------------------- issuing

fn issue(
    state: &ProbeState,
    rel: &str,
    ttl: Option<Duration>,
    cache_policy: CachePolicy,
) -> Result<String, String> {
    let target = state.scope_root.join(rel);
    // existence check only: containment is deliberately NOT enforced at issue
    // time (canonicalize here would resolve a junction and hide exactly the
    // attack the resolve layer must catch). The authoritative containment
    // check happens per-request in handle_request, mirroring the M2-S2
    // resolver's issue-facts / resolve-verification split.
    target.canonicalize().map_err(|_| "REF_NOT_FOUND".to_string())?;
    let id = b64_id();
    state.table.lock().unwrap().insert(
        id.clone(),
        Entry {
            rel: PathBuf::from(rel),
            revoked: false,
            expires_at: ttl.map(|t| Instant::now() + t),
            cache_policy,
        },
    );
    Ok(id)
}

fn normalized(path: &Path) -> String {
    let text = path.to_string_lossy().to_string();
    let text = text
        .strip_prefix(r"\\?\")
        .map(|s| s.to_string())
        .unwrap_or(text);
    text.replace('/', r"\").to_lowercase()
}

fn ensure_inside_scope(scope_root: &Path, canonical: &Path) -> Result<(), String> {
    let root = normalized(scope_root);
    let target = normalized(canonical);
    if target == root || target.starts_with(&(root + "\\")) {
        Ok(())
    } else {
        Err("REF_OUT_OF_SCOPE".to_string())
    }
}

fn sign_all(state: &ProbeState) -> ProbeStateJson {
    // host-side user-source guard: the `user_source_private.png` fixture lives
    // OUTSIDE the scope root; attempting to issue it must be refused.
    let user_source_abs = state.lab.join("outside").join("user_source_private.png");
    let guard = ensure_inside_scope(&state.scope_root, &user_source_abs).unwrap_err();
    *state.issue_guard.lock().unwrap() = Some(guard.clone());

    let mut ids = std::collections::BTreeMap::new();
    let mut put = |ids: &mut std::collections::BTreeMap<String, String>, key: &str, result: Result<String, String>| {
        match result {
            Ok(id) => {
                ids.insert(key.to_string(), id);
            }
            Err(code) => {
                // a refused issue is itself evidence: the JS side will fetch
                // this sentinel, get REF_MALFORMED, and record FAIL with the
                // observed issue refusal in its place
                ids.insert(key.to_string(), format!("__ISSUE_REFUSED_{code}__"));
            }
        }
    };
    put(&mut ids, "valid", issue(state, "asset.png", None, CachePolicy::NoStore));
    put(&mut ids, "large", issue(state, "typical.png", None, CachePolicy::NoStore));
    put(&mut ids, "revocable", issue(state, "asset.png", None, CachePolicy::NoStore));
    put(&mut ids, "expiring", issue(state, "asset.png", Some(EXP_TTL), CachePolicy::NoStore));
    // rel deliberately points at the in-scope junction: resolve containment must reject
    put(&mut ids, "junction", issue(state, "linkj/nested.png", None, CachePolicy::NoStore));
    // in-flight stream: large asset that the JS revokes mid-read
    put(&mut ids, "inflight", issue(state, "typical.png", None, CachePolicy::NoStore));
    // cache-bypass contrast pair
    put(&mut ids, "cache_bare", issue(state, "asset.png", None, CachePolicy::Bare));
    put(&mut ids, "cache_ctrl", issue(state, "asset.png", None, CachePolicy::NoStore));

    let fixtures = std::collections::BTreeMap::from([
        (
            "asset".to_string(),
            sha256_hex(&std::fs::read(state.scope_root.join("asset.png")).unwrap()),
        ),
        (
            "typical".to_string(),
            sha256_hex(&std::fs::read(state.scope_root.join("typical.png")).unwrap()),
        ),
    ]);

    ProbeStateJson {
        scheme_base: format!("http://{HOST}"),
        ids,
        expiring_ttl_ms: EXP_TTL.as_millis() as u64,
        fixtures,
        issue_guard: state.issue_guard.lock().unwrap().clone(),
    }
}

// ---------------------------------------------------------------- protocol

struct ProbeResponse {
    status: u16,
    content_type: &'static str,
    body: Vec<u8>,
    cache_control: Option<&'static str>,
}

fn typed_error(code: &str, status: u16) -> ProbeResponse {
    let body = serde_json::json!({ "code": code }).to_string().into_bytes();
    ProbeResponse {
        status,
        content_type: "application/json",
        body,
        cache_control: Some("no-store"),
    }
}

fn handle_request(state: &ProbeState, uri: &str) -> ProbeResponse {
    let path = match url::path_of(uri) {
        Some(p) => p,
        None => return typed_error("REF_MALFORMED", 400),
    };
    let id = match url::last_segment_percent_decoded(&path) {
        Some(id) if !id.is_empty() => id,
        _ => return typed_error("REF_MALFORMED", 400),
    };
    // ID format gate: opaque IDs are base64url(24 bytes) == 43 chars of
    // [A-Za-z0-9_-]. Anything else (path text, traversal, "..", absolute
    // paths) is malformed before the table is even consulted.
    if id.len() != 43 || !id.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-') {
        return typed_error("REF_MALFORMED", 400);
    }

    let (rel, cache_policy, revoked, expired) = {
        let table = state.table.lock().unwrap();
        match table.get(&id) {
            None => return typed_error("REF_UNKNOWN_ID", 404),
            Some(entry) => (
                entry.rel.clone(),
                entry.cache_policy,
                entry.revoked,
                entry.expires_at.map(|t| Instant::now() >= t).unwrap_or(false),
            ),
        }
    };
    if revoked {
        return typed_error("REF_REVOKED", 410);
    }
    if expired {
        return typed_error("REF_EXPIRED", 410);
    }

    let target = match state.scope_root.join(&rel).canonicalize() {
        Ok(p) => p,
        Err(_) => return typed_error("REF_NOT_FOUND", 404),
    };
    if let Err(code) = ensure_inside_scope(&state.scope_root, &target) {
        return typed_error(&code, 403);
    }
    match std::fs::read(&target) {
        Ok(bytes) => ProbeResponse {
            status: 200,
            content_type: "image/png",
            body: bytes,
            cache_control: match cache_policy {
                CachePolicy::NoStore => Some("no-store"),
                CachePolicy::Bare => None,
            },
        },
        Err(_) => typed_error("REF_NOT_FOUND", 404),
    }
}

// tiny URL helpers (probe-only; the full URL grammar is not needed here)
mod url {
    pub fn path_of(uri: &str) -> Option<String> {
        let rest = uri.split_once("://")?.1;
        let path = rest.split_once('/')?.1;
        let path = path.split(['?', '#']).next().unwrap_or("");
        Some(format!("/{path}"))
    }

    pub fn last_segment_percent_decoded(path: &str) -> Option<String> {
        let segment = path.rsplit('/').next()?;
        Some(percent_decode(segment))
    }

    pub fn percent_decode(text: &str) -> String {
        let bytes = text.as_bytes();
        let mut out: Vec<u8> = Vec::with_capacity(bytes.len());
        let mut i = 0;
        while i < bytes.len() {
            if bytes[i] == b'%' && i + 2 < bytes.len() + 1 && i + 2 < bytes.len() + 1 {
                if i + 2 < bytes.len() {
                    let hex = &text[i + 1..i + 3];
                    if let Ok(byte) = u8::from_str_radix(hex, 16) {
                        out.push(byte);
                        i += 3;
                        continue;
                    }
                }
                out.push(bytes[i]);
                i += 1;
            } else {
                out.push(bytes[i]);
                i += 1;
            }
        }
        String::from_utf8_lossy(&out).into_owned()
    }
}

// ---------------------------------------------------------------- commands

#[tauri::command]
fn get_probe_state(state: tauri::State<ProbeState>) -> ProbeStateJson {
    sign_all(&state)
}

#[tauri::command]
fn revoke(id: String, state: tauri::State<ProbeState>) -> Result<String, String> {
    let mut table = state.table.lock().unwrap();
    match table.get_mut(&id) {
        Some(entry) => {
            entry.revoked = true;
            Ok("REVOKED".into())
        }
        None => Err("REF_UNKNOWN_ID".into()),
    }
}

#[tauri::command]
fn write_results(payload: String) -> Result<String, String> {
    let out = std::env::var("M2S3_PROBE_OUT").unwrap_or_else(|_| {
        std::env::temp_dir().join("m2s3-probe-results.json").to_string_lossy().into_owned()
    });
    std::fs::write(&out, payload).map_err(|e| e.to_string())?;
    Ok(out)
}

#[tauri::command]
fn exit_probe(app: tauri::AppHandle, code: i32) {
    app.exit(code);
}

// ---------------------------------------------------------------- main

fn respond(resp: ProbeResponse) -> tauri::http::Response<Vec<u8>> {
    let mut builder = tauri::http::Response::builder()
        .status(resp.status)
        .header("Content-Type", resp.content_type)
        .header("Access-Control-Allow-Origin", "*");
    if let Some(cc) = resp.cache_control {
        builder = builder.header("Cache-Control", cc);
    }
    builder.body(resp.body).unwrap()
}

fn log_line(msg: &str) {
    use std::io::Write;
    let p = std::env::var("M2S3_PROBE_LOG").unwrap_or_else(|_| {
        std::env::temp_dir().join("m2s3-probe.log").to_string_lossy().into_owned()
    });
    if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(&p) {
        let _ = writeln!(f, "[{}] {}", Instant::now().elapsed().as_secs_f64(), msg);
    }
}

fn main() {
    log_line("main: starting");
    let lab = PathBuf::from(std::env::var("M2S3_LAB").unwrap_or_else(|_| {
        std::env::temp_dir().join("m2s3-lab").to_string_lossy().into_owned()
    }));
    let scope_root = lab.join("scope").join("derived");
    log_line("main: scope root resolved");
    let state = ProbeState {
        lab,
        scope_root,
        table: Mutex::new(HashMap::new()),
        issue_guard: Mutex::new(None),
    };

    tauri::Builder::default()
        .manage(state)
        .register_uri_scheme_protocol(SCHEME, |ctx, request| {
            let state: tauri::State<ProbeState> = ctx.app_handle().state();
            let uri = request.uri().to_string();
            let handled = handle_request(&state, &uri);
            respond(handled)
        })
        .invoke_handler(tauri::generate_handler![
            get_probe_state,
            revoke,
            write_results,
            exit_probe
        ])
        .setup(|_app| {
            log_line("setup: complete");
            Ok(())
        })
        .run(tauri::generate_context!());
    log_line("main: run returned");
}
