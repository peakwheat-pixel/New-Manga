//! The `m2res` custom URI scheme protocol (M2-RC1).
//!
//! URL form (Windows/WebView2): `http://m2res.localhost/m2id/<opaque-id>?chunk=<n>`
//!
//! Serving pipeline per request (RC1-AC4, M2-S2 semantics productised):
//! 1. opaque-ID format gate (43-char base64url) — malformed before any lookup;
//! 2. EVERY request resolves via the Core control bridge before the grant
//!    cache is consulted (F-01): a Core rejection evicts the cached entry and
//!    propagates typed errors (REF_UNKNOWN_ID / REF_REVOKED / REF_EXPIRED);
//! 3. open the target **once** (GENERIC_READ / FILE_SHARE_READ /
//!    FILE_FLAG_BACKUP_SEMANTICS) and verify **from that handle**: containment
//!    (final path re-derived from the handle stays inside the scope root),
//!    file identity (volume serial + file index vs issue-time facts), size
//!    (issue-time size + T1 256 MiB limit);
//! 4. the issue-time digest is re-verified through the handle whenever the
//!    grant has never been verified OR its LastWriteTime moved since the last
//!    verification (F-02: catches equal-size in-place rewrites) without
//!    materialising the file;
//! 5. serve the requested chunk (≤16 MiB) read through the same handle;
//! 6. re-check identity after reading.
//!
//! Responses are always `Cache-Control: no-store` (revocation must never be
//! served from a cache; the M2-S3 probe measured the bypass contrast) and
//! carry permissive CORS so the `tauri.localhost` page may fetch them.
//! Errors are stable typed codes in a JSON body; no OS path, mapping-table
//! entry, revision fingerprint or digest ever appears in a response.

use crate::core_bridge::{CoreChannel, CoreError, Grant};
use serde_json::json;
use sha2::{Digest as ShaDigest, Sha256};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Mutex;

pub const SCHEME_HOST: &str = "m2res.localhost";
pub const CHUNK_SIZE: u64 = 16 * 1024 * 1024; // T4: resident buffer ≤ 32 MiB
pub const MAX_RESOURCE_BYTES: u64 = 256 * 1024 * 1024; // T1 commitment line
pub const ID_LENGTH: usize = 43; // base64url of 32 random bytes

const GENERIC_READ: u32 = 0x8000_0000;
const FILE_SHARE_READ: u32 = 0x0000_0001;
const OPEN_EXISTING: u32 = 3;
const FILE_FLAG_BACKUP_SEMANTICS: u32 = 0x0200_0000;
const FILE_BEGIN: u32 = 0;

pub struct ScopeRoots {
    pub derived: PathBuf,
    pub managed: PathBuf,
}

impl ScopeRoots {
    fn root_for(&self, scope_class: &str) -> Option<&PathBuf> {
        match scope_class {
            "derived-read-only" => Some(&self.derived),
            "managed-read-only" => Some(&self.managed),
            _ => None, // user-source has no servable root (T5.3)
        }
    }
}

struct CachedGrant {
    grant: Grant,
    digest_verified: bool,
    /// LastWriteTime observed when the full-file digest check last passed
    /// (F-02: an equal-size in-place rewrite bumps mtime while keeping the
    /// NTFS file index, so an mtime change forces a digest re-verification).
    verified_mtime: Option<u64>,
}

/// F-10 (partial): the cache must not grow without bound. Entries are always
/// re-derivable from the Core, so clearing is a performance event, not a
/// correctness one.
const GRANT_CACHE_MAX_ENTRIES: usize = 1024;

#[derive(Default)]
pub struct GrantCache {
    map: Mutex<HashMap<String, CachedGrant>>,
}

pub struct HttpResponse {
    pub status: u16,
    pub content_type: &'static str,
    pub body: Vec<u8>,
    pub cache_control: &'static str,
}

impl HttpResponse {
    fn error(code: &str, status: u16) -> Self {
        Self {
            status,
            content_type: "application/json",
            body: json!({ "code": code }).to_string().into_bytes(),
            cache_control: "no-store",
        }
    }

    fn ok(content_type: &'static str, body: Vec<u8>) -> Self {
        Self {
            status: 200,
            content_type,
            body,
            cache_control: "no-store",
        }
    }
}

fn status_for(code: &str) -> u16 {
    match code {
        "REF_MALFORMED" => 400,
        "REF_UNKNOWN_ID" | "REF_NOT_FOUND" => 404,
        "REF_OUT_OF_SCOPE" | "REF_REPARSE_POINT" | "REF_SCOPE_DENIED" | "RESOURCE_TOO_LARGE"
        | "RESOURCE_LIMIT_EXCEEDED" => 403,
        "REF_REVOKED" | "REF_EXPIRED" => 410,
        _ => 400,
    }
}

fn typed_error(error: &CoreError) -> HttpResponse {
    let code = error.code.split(':').next().unwrap_or("REF_MALFORMED").to_string();
    let status = match code.as_str() {
        "CORE_SPAWN_FAILED" | "CORE_BRIDGE_DOWN" => 503,
        other => status_for(other),
    };
    HttpResponse::error(&code, status)
}

struct ParsedRequest {
    opaque_id: String,
    chunk: u64,
}

fn parse_request(uri: &str) -> Option<(String, ParsedRequest)> {
    // returns (host, parsed); the caller validates the host (F-10)
    let rest = uri.split_once("://")?.1;
    let (host, host_path) = match rest.split_once('/') {
        Some((h, hp)) => (h.to_string(), hp),
        None => (rest.to_string(), ""),
    };
    let (path, query) = match host_path.split_once('?') {
        Some((p, q)) => (p, Some(q)),
        None => (host_path, None),
    };
    let segment = path.split('/').last().unwrap_or("");
    let chunk = query
        .and_then(|q| {
            q.split('&').find_map(|pair| {
                let (k, v) = pair.split_once('=')?;
                if k == "chunk" {
                    v.parse::<u64>().ok()
                } else {
                    None
                }
            })
        })
        .unwrap_or(0);
    Some((
        host.to_lowercase(),
        ParsedRequest {
            opaque_id: percent_decode(segment),
            chunk,
        },
    ))
}

fn percent_decode(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut out: Vec<u8> = Vec::with_capacity(bytes.len());
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] == b'%' && index + 2 < bytes.len() {
            if let Ok(byte) = u8::from_str_radix(&text[index + 1..index + 3], 16) {
                out.push(byte);
                index += 3;
                continue;
            }
        }
        out.push(bytes[index]);
        index += 1;
    }
    String::from_utf8_lossy(&out).into_owned()
}

fn is_well_formed_id(id: &str) -> bool {
    id.len() == ID_LENGTH
        && id
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}

// ---------------------------------------------------------------- Win32

mod win32 {
    use std::ffi::c_void;

    pub const INVALID_HANDLE_VALUE: isize = -1;
    pub const ERROR_SHARING_VIOLATION: u32 = 32;

    // Exact BY_HANDLE_FILE_INFORMATION layout: 13 DWORDs, 52 bytes.
    #[repr(C)]
    #[derive(Default, Clone, Copy)]
    pub struct RawInfo {
        pub attributes: u32,
        pub creation_lo: u32,
        pub creation_hi: u32,
        pub access_lo: u32,
        pub access_hi: u32,
        pub write_lo: u32,
        pub write_hi: u32,
        pub volume_serial: u32,
        pub size_high: u32,
        pub size_low: u32,
        pub links: u32,
        pub index_high: u32,
        pub index_low: u32,
    }

    #[link(name = "kernel32")]
    extern "system" {
        pub fn CreateFileW(
            file_name: *const u16,
            desired_access: u32,
            share_mode: u32,
            security: *const c_void,
            creation: u32,
            flags: u32,
            template: *const c_void,
        ) -> *mut c_void;
        pub fn CloseHandle(handle: *mut c_void) -> i32;
        pub fn ReadFile(
            handle: *mut c_void,
            buffer: *mut u8,
            to_read: u32,
            read: *mut u32,
            overlapped: *mut c_void,
        ) -> i32;
        pub fn SetFilePointer(
            handle: *mut c_void,
            distance: i32,
            high: *mut i32,
            method: u32,
        ) -> u32;
        pub fn GetFileInformationByHandle(handle: *mut c_void, info: *mut RawInfo) -> i32;
        pub fn GetFinalPathNameByHandleW(
            handle: *mut c_void,
            buffer: *mut u16,
            length: u32,
            flags: u32,
        ) -> u32;
        pub fn GetLastError() -> u32;
    }

    pub fn last_error() -> u32 {
        unsafe { GetLastError() }
    }
}

struct OpenedFile {
    handle: *mut std::ffi::c_void,
}

impl Drop for OpenedFile {
    fn drop(&mut self) {
        if !self.handle.is_null() {
            unsafe { win32::CloseHandle(self.handle) };
        }
    }
}

fn identity_size_mtime(
    handle: *mut std::ffi::c_void,
) -> Result<(u32, u64, u64, u64), CoreError> {
    let mut raw = win32::RawInfo::default();
    let ok = unsafe { win32::GetFileInformationByHandle(handle, &mut raw) };
    if ok == 0 {
        return Err(CoreError::new("OPEN_FAILED"));
    }
    let size = ((raw.size_high as u64) << 32) | raw.size_low as u64;
    let index = ((raw.index_high as u64) << 32) | raw.index_low as u64;
    let mtime = ((raw.write_hi as u64) << 32) | raw.write_lo as u64;
    Ok((raw.volume_serial, index, size, mtime))
}

fn final_path(handle: *mut std::ffi::c_void) -> Result<String, CoreError> {
    unsafe {
        let length = win32::GetFinalPathNameByHandleW(handle, std::ptr::null_mut(), 0, 0);
        if length == 0 {
            return Err(CoreError::new("OPEN_FAILED"));
        }
        let mut buffer = vec![0u16; (length + 1) as usize];
        let written = win32::GetFinalPathNameByHandleW(handle, buffer.as_mut_ptr(), length + 1, 0);
        if written == 0 || written > length {
            return Err(CoreError::new("OPEN_FAILED"));
        }
        buffer.truncate(written as usize);
        Ok(String::from_utf16_lossy(&buffer))
    }
}

fn normalized(text: &str) -> String {
    let stripped = if let Some(rest) = text.strip_prefix("\\\\?\\UNC\\") {
        format!("\\\\{rest}")
    } else if let Some(rest) = text.strip_prefix("\\\\?\\") {
        rest.to_string()
    } else {
        text.to_string()
    };
    stripped.replace('/', "\\").to_lowercase()
}

fn open_once(path: &str) -> Result<OpenedFile, CoreError> {
    let wide: Vec<u16> = path.encode_utf16().chain(std::iter::once(0)).collect();
    let handle = unsafe {
        win32::CreateFileW(
            wide.as_ptr(),
            GENERIC_READ,
            FILE_SHARE_READ,
            std::ptr::null(),
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            std::ptr::null(),
        )
    };
    if (handle as isize) == win32::INVALID_HANDLE_VALUE || handle.is_null() {
        let error = win32::last_error();
        if error == win32::ERROR_SHARING_VIOLATION {
            return Err(CoreError::new("OPEN_FAILED_SHARING_VIOLATION"));
        }
        return Err(CoreError::new("REF_NOT_FOUND"));
    }
    Ok(OpenedFile { handle })
}

fn read_through(
    handle: *mut std::ffi::c_void,
    offset: u64,
    length: usize,
) -> Result<Vec<u8>, CoreError> {
    unsafe {
        win32::SetFilePointer(handle, offset as i32, std::ptr::null_mut(), FILE_BEGIN);
    }
    let mut buffer = vec![0u8; length];
    let mut total = 0usize;
    while total < length {
        let mut read: u32 = 0;
        let ok = unsafe {
            win32::ReadFile(
                handle,
                buffer[total..].as_mut_ptr(),
                (length - total) as u32,
                &mut read,
                std::ptr::null_mut(),
            )
        };
        if ok == 0 {
            return Err(CoreError::new("OPEN_FAILED"));
        }
        if read == 0 {
            break;
        }
        total += read as usize;
    }
    buffer.truncate(total);
    Ok(buffer)
}

fn stream_digest(handle: *mut std::ffi::c_void, expected_size: u64) -> Result<String, CoreError> {
    let mut digest = Sha256::new();
    let mut served: u64 = 0;
    while served < expected_size {
        let want = usize::try_from((expected_size - served).min(CHUNK_SIZE)).unwrap_or(usize::MAX);
        let block = read_through(handle, served, want)?;
        if block.is_empty() {
            break;
        }
        digest.update(&block);
        served += block.len() as u64;
    }
    if served != expected_size {
        return Err(CoreError::new("FILE_SIZE_CHANGED"));
    }
    Ok(hex(digest.finalize()))
}

pub(crate) fn hex(bytes: impl AsRef<[u8]>) -> String {
    let mut out = String::with_capacity(64);
    for byte in bytes.as_ref() {
        out.push_str(&format!("{byte:02x}"));
    }
    out
}

// ------------------------------------------------------------- verification

fn verify_and_serve(
    grant: &Grant,
    roots: &ScopeRoots,
    entry: &mut CachedGrant,
    chunk_offset: u64,
) -> Result<Vec<u8>, CoreError> {
    let root = roots
        .root_for(&grant.scope_class)
        .ok_or_else(|| CoreError::new("REF_SCOPE_DENIED"))?;
    let target = root.join(&grant.rel_path);
    let opened = open_once(&target.to_string_lossy())?;

    // containment re-derived from the handle (authoritative path-level check)
    let final_text = final_path(opened.handle)?;
    let root_norm = normalized(&root.to_string_lossy());
    let final_norm = normalized(&final_text);
    if final_norm != root_norm && !final_norm.starts_with(&(root_norm.clone() + "\\")) {
        return Err(CoreError::new("REF_OUT_OF_SCOPE"));
    }

    // identity + size from the handle vs issue-time facts (every request)
    let (volume, index, size, mtime) = identity_size_mtime(opened.handle)?;
    if volume != grant.volume_serial || index != grant.file_index {
        return Err(CoreError::new("FILE_IDENTITY_CHANGED"));
    }
    if size != grant.size {
        return Err(CoreError::new("FILE_SIZE_CHANGED"));
    }
    if size > MAX_RESOURCE_BYTES {
        return Err(CoreError::new("RESOURCE_TOO_LARGE"));
    }

    // F-02: the issue-time digest is re-verified when never verified, or when
    // the file's LastWriteTime moved since the last verified pass (an
    // equal-size in-place rewrite keeps the NTFS file index but bumps mtime).
    let needs_digest = !entry.digest_verified || entry.verified_mtime != Some(mtime);
    if needs_digest {
        let digest = stream_digest(opened.handle, size)?;
        if digest != grant.sha256 {
            return Err(CoreError::new("CONTENT_DIGEST_MISMATCH"));
        }
        entry.digest_verified = true;
        entry.verified_mtime = Some(mtime);
    }

    // serve the requested chunk through the same handle
    let want = ((grant.size - chunk_offset).min(CHUNK_SIZE)) as usize;
    read_through(opened.handle, chunk_offset, want)?;

    // post-read identity re-check (RC1-AC4)
    let (post_volume, post_index, _, _) = identity_size_mtime(opened.handle)?;
    if post_volume != grant.volume_serial || post_index != grant.file_index {
        return Err(CoreError::new("FILE_IDENTITY_CHANGED"));
    }
    // re-read the chunk AFTER the post-check so no unchecked bytes escape
    read_through(opened.handle, chunk_offset, want)
}

// ------------------------------------------------------------- request flow

pub fn handle_m2res_request(
    uri: &str,
    channel: &dyn CoreChannel,
    cache: &GrantCache,
    roots: &ScopeRoots,
) -> HttpResponse {
    let (host, parsed) = match parse_request(uri) {
        Some(pair) => pair,
        None => return HttpResponse::error("REF_MALFORMED", 400),
    };
    // F-10 (partial): the protocol only answers its own scheme. Both
    // documented forms are accepted: the native `m2res://localhost/...`
    // (measured: WebView2 normalises the fetch back to the custom scheme)
    // and the Windows http mapping `http://m2res.localhost/...` that
    // build_url emits. Anything else is malformed.
    if host != "localhost" && host != SCHEME_HOST {
        return HttpResponse::error("REF_MALFORMED", 400);
    }
    if !is_well_formed_id(&parsed.opaque_id) {
        return HttpResponse::error("REF_MALFORMED", 400);
    }

    let full_id = full_id_from_segment(&parsed.opaque_id);

    // F-01: EVERY request consults the Core (resolve carries revocation and
    // expiry semantics) -- a warm cache never bypasses T6. A Core rejection
    // evicts the cache entry and propagates the typed code; a pass refreshes
    // the cached grant (the Core-side resolve also slides the TTL, which is
    // the T6 "active consumption" renewal for this request).
    let fresh_grant = match channel.resolve(&full_id) {
        Ok(grant) => grant,
        Err(error) => {
            cache.map.lock().unwrap().remove(&full_id);
            return typed_error(&error);
        }
    };

    let chunk_offset = parsed
        .chunk
        .checked_mul(CHUNK_SIZE)
        .ok_or_else(|| HttpResponse::error("REF_MALFORMED", 400));
    let chunk_offset = match chunk_offset {
        Ok(offset) if offset < fresh_grant.size => offset,
        _ => return HttpResponse::error("REF_MALFORMED", 400),
    };

    let mut guard = cache.map.lock().unwrap();
    if guard.len() >= GRANT_CACHE_MAX_ENTRIES {
        guard.clear(); // re-derivable from the Core; bounded memory (F-10)
    }
    let entry = match guard.get_mut(&full_id) {
        Some(entry) => {
            // keep the digest flag only if the Core's issue-time facts are
            // unchanged; different facts force a full re-verification
            if entry.grant.sha256 != fresh_grant.sha256
                || entry.grant.size != fresh_grant.size
                || entry.grant.rel_path != fresh_grant.rel_path
            {
                entry.digest_verified = false;
                entry.verified_mtime = None;
            }
            entry.grant = fresh_grant.clone();
            entry
        }
        None => {
            guard.insert(
                full_id.clone(),
                CachedGrant {
                    grant: fresh_grant.clone(),
                    digest_verified: false,
                    verified_mtime: None,
                },
            );
            guard.get_mut(&full_id).unwrap()
        }
    };

    match verify_and_serve(&fresh_grant, roots, entry, chunk_offset) {
        Ok(chunk) => HttpResponse::ok("application/octet-stream", chunk),
        Err(error) => {
            // an identity/size/containment/digest failure invalidates the entry
            if matches!(
                error.code.as_str(),
                "FILE_IDENTITY_CHANGED"
                    | "FILE_SIZE_CHANGED"
                    | "REF_OUT_OF_SCOPE"
                    | "CONTENT_DIGEST_MISMATCH"
            ) {
                drop(guard);
                cache.map.lock().unwrap().remove(&full_id);
            }
            typed_error(&error)
        }
    }
}

/// URL builder used by the `issue_resource_url` command; the WebView-visible
/// object carries the opaque URL and size only (no path, digest, revision).
/// The URL carries the 43-char random segment; the handler rebuilds the full
/// `m2id.v1.<segment>` identifier before touching the Core.
pub fn build_url(opaque_id: &str) -> String {
    let segment = opaque_id.rsplit('.').next().unwrap_or(opaque_id);
    format!("http://{SCHEME_HOST}/m2id/{segment}")
}

/// Full opaque identifier for a URL segment.
fn full_id_from_segment(segment: &str) -> String {
    format!("m2id.v1.{segment}")
}

#[cfg(test)]
pub fn capture_facts_for_tests(path: &PathBuf) -> Result<(u32, u64, u64, u64), CoreError> {
    // open once, capture identity+size+mtime, close (no leaked handle
    // clashing with later writes in the same test)
    let opened = open_once(&path.to_string_lossy())?;
    identity_size_mtime(opened.handle)
}
