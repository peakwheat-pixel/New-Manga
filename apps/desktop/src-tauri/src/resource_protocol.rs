//! The `m2res` custom URI scheme protocol (M2-RC1).
//!
//! URL form (Windows/WebView2): `http://m2res.localhost/m2id/<opaque-id>?chunk=<n>`
//!
//! Serving pipeline per request (RC1-AC4, M2-S2 semantics productised):
//! 1. opaque-ID format gate (43-char base64url) — malformed before any lookup;
//! 2. EVERY request resolves via the Core control bridge first (F-01): a
//!    Core rejection propagates typed errors (REF_UNKNOWN_ID / REF_REVOKED /
//!    REF_EXPIRED). There is deliberately NO host-side grant cache: the
//!    resolve result is consumed directly (the write-only GrantCache remnant
//!    was removed by M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF);
//! 3. open the target **once** (GENERIC_READ / FILE_SHARE_READ /
//!    FILE_FLAG_BACKUP_SEMANTICS) and verify **from that handle**: containment
//!    (final path re-derived from the handle stays inside the scope root),
//!    file identity (volume serial + file index vs issue-time facts), size
//!    (issue-time size + T1 256 MiB limit);
//! 4. the issue-time digest is re-verified through the handle on EVERY
//!    request (F-02: catches equal-size in-place rewrites; an mtime-gated
//!    short-circuit is unsound because NTFS LastWriteTime granularity
//!    follows the system timer tick, so a rewrite landing in the same tick
//!    as the verified write reads back the identical mtime) without
//!    materialising the file;
//! 5. the requested chunk (≤16 MiB) is CAPTURED during that same single
//!    sequential read, so the served bytes are exactly the digest-covered
//!    bytes — no digest→serve TOCTOU window remains;
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
use std::path::PathBuf;

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

// (M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF) The former `GrantCache`/`CachedGrant`
// is gone. After the F-02 fix removed the last read consumer, the cache was
// write-only: `CachedGrant.grant` was inserted and never read (dead code,
// F02 integration C2-(b)), and every request already resolved via the Core
// unconditionally (F-01) and consumed `fresh_grant` directly. There is no
// cached state left to invalidate: revocation/expiry live entirely in the
// Core resolve, and `Cache-Control: no-store` still forbids WebView caching.

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
        // 64-bit seek (M2-FIX-DIGEST-SEEK-2GIB): replaces the former 32-bit
        // `SetFilePointer(distance: i32, high: *mut i32)` whose `offset as i32`
        // cast truncated every offset ≥ 2^31 (and whose null HIGHDWORD pointer
        // made the upper half permanently zero). LARGE_INTEGER is inlined as a
        // plain `i64` (same 8-byte value type, no crate dependency).
        pub fn SetFilePointerEx(
            handle: *mut c_void,
            distance: i64,
            new_position: *mut i64,
            method: u32,
        ) -> i32;
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
    // Defence in depth (M2-FIX-DIGEST-SEEK-2GIB): the issue path already
    // refuses files above MAX_RESOURCE_BYTES, but the seek itself must also
    // fail closed instead of ever positioning past the ruled limit (a
    // truncated or mis-positioned seek used to surface as a silently empty
    // or wrong-window read).
    if offset > MAX_RESOURCE_BYTES {
        return Err(CoreError::new(&format!(
            "RESOURCE_TOO_LARGE:seek_offset={offset} exceeds limit={MAX_RESOURCE_BYTES}"
        )));
    }
    // 64-bit seek (M2-FIX-DIGEST-SEEK-2GIB): SetFilePointerEx takes the
    // offset as one 64-bit LARGE_INTEGER, so nothing is truncated, and the
    // resulting position is verified against the request instead of being
    // ignored (the former fire-and-forget SetFilePointer call could fail or
    // land elsewhere and the read would proceed from the wrong offset).
    unsafe {
        let mut landed: i64 = -1;
        let ok = win32::SetFilePointerEx(handle, offset as i64, &mut landed, FILE_BEGIN);
        if ok == 0 || landed != offset as i64 {
            return Err(CoreError::new(&format!(
                "OPEN_FAILED:seek_to={offset} landed_at={landed}"
            )));
        }
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

/// Single-pass digest + capture (M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF): one
/// sequential read of the whole file accumulates the SHA-256 digest AND
/// captures the target chunk bytes. The former implementation streamed the
/// full-file digest, then re-read the chunk once and threw the bytes away,
/// then read it again to serve — three passes over the storage for one
/// request. With the single pass, the bytes returned to the caller are
/// exactly the bytes the digest covered: no digest→serve TOCTOU window
/// remains (an equal-size in-place rewrite landing between "verify" and
/// "serve" can no longer be served unchecked; the F-02 semantics that
/// reject such rewrites are unchanged). Peak resident memory: one streaming
/// block (≤ CHUNK_SIZE) + the captured chunk (≤ CHUNK_SIZE) = ≤ 32 MiB,
/// inside the ruled T4 budget.
fn stream_digest_and_capture(
    handle: *mut std::ffi::c_void,
    expected_size: u64,
    chunk_offset: u64,
    chunk_len: usize,
) -> Result<(String, Vec<u8>), CoreError> {
    let mut digest = Sha256::new();
    let mut captured = vec![0u8; chunk_len];
    let mut served: u64 = 0;
    while served < expected_size {
        let want = usize::try_from((expected_size - served).min(CHUNK_SIZE)).unwrap_or(usize::MAX);
        let block = read_through(handle, served, want)?;
        if block.is_empty() {
            break;
        }
        digest.update(&block);
        let block_start = served;
        let block_end = served + block.len() as u64;
        // copy the slice(s) intersecting [chunk_offset, chunk_offset+chunk_len)
        let capture_start = chunk_offset.max(block_start);
        let capture_end = (chunk_offset + chunk_len as u64).min(block_end);
        if capture_start < capture_end {
            let from = (capture_start - block_start) as usize;
            let to = (capture_end - block_start) as usize;
            let into = (capture_start - chunk_offset) as usize;
            captured[into..into + (to - from)].copy_from_slice(&block[from..to]);
        }
        served = block_end;
    }
    if served != expected_size {
        return Err(CoreError::new("FILE_SIZE_CHANGED"));
    }
    Ok((hex(digest.finalize()), captured))
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
    let (volume, index, size, _mtime) = identity_size_mtime(opened.handle)?;
    if volume != grant.volume_serial || index != grant.file_index {
        return Err(CoreError::new("FILE_IDENTITY_CHANGED"));
    }
    if size != grant.size {
        return Err(CoreError::new("FILE_SIZE_CHANGED"));
    }
    if size > MAX_RESOURCE_BYTES {
        return Err(CoreError::new("RESOURCE_TOO_LARGE"));
    }

    // F-02 (fixed) + single pass (M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF): the
    // issue-time digest is re-verified through the handle on EVERY request.
    // The former `digest_verified`/`verified_mtime` gate was unsound: NTFS
    // LastWriteTime granularity follows the system timer tick, so an
    // equal-size in-place rewrite landing in the same tick as the verified
    // write read back the IDENTICAL mtime (AC1 probe: mtime_delta_100ns=0,
    // rewritten content served with status 200) and the rewritten bytes
    // bypassed the digest check. One sequential read now both accumulates
    // the digest and captures the chunk: the served bytes ARE the
    // digest-covered bytes, so the former digest→serve re-read window is
    // structurally gone. Cost: one full-file streaming read per request,
    // bounded by MAX_RESOURCE_BYTES (the "等长重写必拒" semantics are
    // unchanged — any byte-level rewrite anywhere in the file still fails
    // the whole request with CONTENT_DIGEST_MISMATCH).
    let want = ((size - chunk_offset).min(CHUNK_SIZE)) as usize;
    let (digest, captured) =
        stream_digest_and_capture(opened.handle, size, chunk_offset, want)?;
    if digest != grant.sha256 {
        return Err(CoreError::new("CONTENT_DIGEST_MISMATCH"));
    }

    // post-read identity re-check (RC1-AC4): every served byte was already
    // read and digest-covered above, so this re-check only asserts the
    // handle still names the granted file when the response is assembled.
    let (post_volume, post_index, _, _) = identity_size_mtime(opened.handle)?;
    if post_volume != grant.volume_serial || post_index != grant.file_index {
        return Err(CoreError::new("FILE_IDENTITY_CHANGED"));
    }
    Ok(captured)
}

// ------------------------------------------------------------- request flow

pub fn handle_m2res_request(
    uri: &str,
    channel: &dyn CoreChannel,
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
    // expiry semantics). With the write-only GrantCache removed there is no
    // host-side state at all: the fresh grant is consumed directly, and the
    // Core-side resolve sliding the TTL remains the T6 "active consumption"
    // renewal for this request.
    let fresh_grant = match channel.resolve(&full_id) {
        Ok(grant) => grant,
        Err(error) => return typed_error(&error),
    };

    let chunk_offset = parsed
        .chunk
        .checked_mul(CHUNK_SIZE)
        .ok_or_else(|| HttpResponse::error("REF_MALFORMED", 400));
    let chunk_offset = match chunk_offset {
        Ok(offset) if offset < fresh_grant.size => offset,
        _ => return HttpResponse::error("REF_MALFORMED", 400),
    };

    match verify_and_serve(&fresh_grant, roots, chunk_offset) {
        Ok(chunk) => HttpResponse::ok("application/octet-stream", chunk),
        Err(error) => typed_error(&error),
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

#[cfg(test)]
mod tests {
    use super::*;

    /// Small on-disk fixture opened through the production `open_once` path;
    /// `OpenedFile`'s Drop closes the handle before the TempDir is removed
    /// (reverse declaration order), matching the main.rs test-fixture style.
    fn open_fixture(payload: &[u8]) -> (tempfile::TempDir, OpenedFile) {
        let dir = tempfile::tempdir().expect("tempdir");
        let path = dir.path().join("asset.bin");
        std::fs::write(&path, payload).expect("write fixture");
        let opened = open_once(&path.to_string_lossy()).expect("open fixture");
        (dir, opened)
    }

    // (M2-FIX-DIGEST-SEEK-2GIB) AC3①: an offset above MAX_RESOURCE_BYTES must
    // fail closed with a discriminable typed error instead of silently
    // seeking/truncating (the pre-fix code served an empty Ok here).
    #[test]
    fn read_through_rejects_offset_above_resource_limit() {
        let (_dir, opened) = open_fixture(b"0123456789");
        let error = read_through(opened.handle, MAX_RESOURCE_BYTES + 1, 4).unwrap_err();
        assert!(
            error.code.starts_with("RESOURCE_TOO_LARGE"),
            "expected RESOURCE_TOO_LARGE-prefixed code, got {}",
            error.code
        );
    }

    /// AC3①/AC1: an offset beyond the 32-bit seek range (2^32, which the old
    /// `SetFilePointer(offset as i32)` path truncated to 0 and served FILE
    /// HEAD bytes for) must be rejected, not silently mis-read.
    #[test]
    fn read_through_rejects_offset_beyond_i32_seek_range() {
        let (_dir, opened) = open_fixture(b"0123456789");
        let error = read_through(opened.handle, 0x1_0000_0000, 4).unwrap_err();
        assert!(
            error.code.starts_with("RESOURCE_TOO_LARGE"),
            "expected RESOURCE_TOO_LARGE-prefixed code, got {}",
            error.code
        );
    }

    // AC3② regression anchors: behaviour strictly inside the 256 MiB limit is
    // byte-for-byte unchanged by the 64-bit seek fix.
    #[test]
    fn read_through_serves_requested_window_within_limit() {
        let (_dir, opened) = open_fixture(b"0123456789");
        assert_eq!(read_through(opened.handle, 2, 3).unwrap(), b"234");
        assert_eq!(read_through(opened.handle, 8, 8).unwrap(), b"89");
    }

    /// An in-limit offset past EOF still yields an empty (truncated) buffer —
    /// unchanged short-read semantics at the boundary.
    #[test]
    fn read_through_at_limit_offset_yields_empty_tail() {
        let (_dir, opened) = open_fixture(b"0123456789");
        let buffer = read_through(opened.handle, MAX_RESOURCE_BYTES, 4).unwrap();
        assert!(buffer.is_empty());
    }
}
