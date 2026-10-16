use rand::{rngs::OsRng, RngCore};
use serde::Serialize;
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, File, Metadata, OpenOptions};
use std::io::Read;
use std::path::{Component, Path};
use std::time::{SystemTime, UNIX_EPOCH};

const BASE64URL: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
const IMPORT_IMAGE_EXTENSIONS: &[&str] = &["bmp", "gif", "jpeg", "jpg", "png", "webp"];
const IMPORT_FILE_EXTENSIONS: &[&str] = &["bmp", "gif", "jpeg", "jpg", "pdf", "png", "webp"];

#[derive(Clone, Copy, Debug)]
pub(crate) struct HostIssuerError(pub(crate) &'static str);

#[derive(Debug)]
pub(crate) struct ImportGrant {
    pub(crate) grant_id: String,
    pub(crate) payload: Value,
    pub(crate) reference: Value,
}

#[derive(Debug)]
pub(crate) struct ExportGrant {
    pub(crate) grant_id: String,
    pub(crate) payload: Value,
    pub(crate) reference: String,
}

#[derive(Serialize)]
pub(crate) struct ImportSummary {
    chapter_id: String,
    cancelled: bool,
    imported_files: u64,
    skipped_files: u64,
    rejected_files: u64,
    pending_files: u64,
}

impl ImportSummary {
    pub(crate) fn cancelled(chapter_id: String) -> Self {
        Self {
            chapter_id,
            cancelled: true,
            imported_files: 0,
            skipped_files: 0,
            rejected_files: 0,
            pending_files: 0,
        }
    }
}

#[derive(Serialize)]
pub(crate) struct ExportSummary {
    export_id: String,
    status: String,
}

pub(crate) fn random_token(bytes: &mut [u8]) -> Result<String, HostIssuerError> {
    random_bytes(bytes)?;
    Ok(base64url(bytes))
}

pub(crate) fn random_bytes(bytes: &mut [u8]) -> Result<(), HostIssuerError> {
    OsRng
        .try_fill_bytes(bytes)
        .map_err(|_| HostIssuerError("HOST_CREDENTIAL_UNAVAILABLE"))?;
    Ok(())
}

pub(crate) fn base64url(bytes: &[u8]) -> String {
    let mut encoded = String::with_capacity((bytes.len() * 4 + 2) / 3);
    for chunk in bytes.chunks(3) {
        let a = chunk[0];
        let b = *chunk.get(1).unwrap_or(&0);
        let c = *chunk.get(2).unwrap_or(&0);
        encoded.push(BASE64URL[(a >> 2) as usize] as char);
        encoded.push(BASE64URL[(((a & 0x03) << 4) | (b >> 4)) as usize] as char);
        if chunk.len() > 1 {
            encoded.push(BASE64URL[(((b & 0x0f) << 2) | (c >> 6)) as usize] as char);
        }
        if chunk.len() > 2 {
            encoded.push(BASE64URL[(c & 0x3f) as usize] as char);
        }
    }
    encoded
}

pub(crate) fn build_import_grant(
    selected_path: &Path,
    source_kind: &str,
    session_id: &str,
    grant_id: String,
    signing_key: &[u8; 32],
) -> Result<ImportGrant, HostIssuerError> {
    if !matches!(source_kind, "file" | "directory") || session_id.is_empty() {
        return Err(HostIssuerError("REF_MALFORMED"));
    }
    let source_path = selected_path
        .to_str()
        .ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
    validate_absolute_path(source_path)?;
    reject_reparse_path(selected_path)?;

    let metadata = fs::metadata(selected_path).map_err(|_| HostIssuerError("REF_SCOPE_DENIED"))?;
    let (scope_identity, entries) = if source_kind == "directory" {
        if !metadata.is_dir() {
            return Err(HostIssuerError("REF_SCOPE_DENIED"));
        }
        let directory = open_path(selected_path, true)?;
        let identity = file_identity(&directory).ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
        let mut paths = Vec::new();
        for item in
            fs::read_dir(selected_path).map_err(|_| HostIssuerError("SOURCE_READ_FAILED"))?
        {
            let path = item
                .map_err(|_| HostIssuerError("SOURCE_READ_FAILED"))?
                .path();
            reject_reparse_path(&path)?;
            if path.is_file()
                && import_extension(&path)
                    .is_some_and(|ext| IMPORT_IMAGE_EXTENSIONS.contains(&ext.as_str()))
            {
                paths.push(path);
            }
        }
        paths.sort_by(|a, b| {
            natural_cmp(
                a.file_name().and_then(|n| n.to_str()).unwrap_or_default(),
                b.file_name().and_then(|n| n.to_str()).unwrap_or_default(),
            )
        });
        let entries = paths
            .iter()
            .map(|path| import_entry(path))
            .collect::<Result<Vec<_>, _>>()?;
        if entries.is_empty() {
            return Err(HostIssuerError("REF_SCOPE_DENIED"));
        }
        (Some(json!([identity.0, identity.1])), entries)
    } else {
        if !metadata.is_file()
            || import_extension(selected_path)
                .is_none_or(|ext| !IMPORT_FILE_EXTENSIONS.contains(&ext.as_str()))
        {
            return Err(HostIssuerError("REF_SCOPE_DENIED"));
        }
        (None, vec![import_entry(selected_path)?])
    };

    let expires_at = unix_seconds() + 299.0;
    let expires_signed = format!("{expires_at:.6}");
    let mut signed_fields = Map::new();
    signed_fields.insert("access".into(), json!("read-only"));
    signed_fields.insert("entries".into(), Value::Array(entries.clone()));
    signed_fields.insert("expires_at".into(), json!(expires_signed));
    signed_fields.insert("grant_id".into(), json!(grant_id));
    signed_fields.insert("operation".into(), json!("ImportPages"));
    signed_fields.insert("scope_class".into(), json!("user-source"));
    signed_fields.insert(
        "scope_identity".into(),
        scope_identity.clone().unwrap_or(Value::Null),
    );
    signed_fields.insert("session_id".into(), json!(session_id));
    signed_fields.insert("source_kind".into(), json!(source_kind));
    signed_fields.insert("source_path".into(), json!(source_path));
    let signature = sign_json(signing_key, &Value::Object(signed_fields.clone()))?;

    let mut payload = Value::Object(signed_fields);
    payload["expires_at"] = json!(expires_at);
    payload["signing_key"] = json!(base64url(signing_key));
    payload["signature"] = json!(signature);

    Ok(ImportGrant {
        grant_id: grant_id.clone(),
        payload,
        reference: json!({ "grant_id": grant_id, "host_signature": signature }),
    })
}

pub(crate) fn validate_export_request(
    request: &Value,
) -> Result<(&'static str, &'static str), HostIssuerError> {
    let fields = request
        .as_object()
        .ok_or(HostIssuerError("INVALID_REQUEST"))?;
    let expected = [
        "book_id",
        "chapter_ids",
        "ordered_page_ids",
        "format",
        "format_options",
        "stale_policy",
    ];
    if fields.len() != expected.len() || expected.iter().any(|field| !fields.contains_key(*field)) {
        return Err(HostIssuerError("INVALID_REQUEST"));
    }
    for field in ["book_id"] {
        if fields[field].as_str().is_none_or(str::is_empty) {
            return Err(HostIssuerError("INVALID_REQUEST"));
        }
    }
    for field in ["chapter_ids", "ordered_page_ids"] {
        let values = fields[field]
            .as_array()
            .filter(|values| !values.is_empty())
            .ok_or(HostIssuerError("INVALID_REQUEST"))?;
        let mut seen = std::collections::HashSet::new();
        if values.iter().any(|value| {
            value.as_str().is_none_or(str::is_empty) || !seen.insert(value.as_str().unwrap())
        }) {
            return Err(HostIssuerError("INVALID_REQUEST"));
        }
    }
    if !matches!(
        fields["stale_policy"].as_str(),
        Some("abort" | "continue_existing")
    ) {
        return Err(HostIssuerError("INVALID_REQUEST"));
    }
    let options = fields["format_options"]
        .as_object()
        .ok_or(HostIssuerError("INVALID_REQUEST"))?;
    let (format, extension) = match fields["format"].as_str() {
        Some("png")
            if options.is_empty() && fields["ordered_page_ids"].as_array().unwrap().len() == 1 =>
        {
            ("png", "png")
        }
        Some("zip")
            if options.len() == 1
                && matches!(
                    options.get("compression").and_then(Value::as_str),
                    Some("standard" | "fast" | "store")
                ) =>
        {
            ("zip", "zip")
        }
        Some("cbz") if options.is_empty() => ("cbz", "cbz"),
        Some("pdf")
            if options.len() == 1
                && matches!(
                    options.get("pdf_content").and_then(Value::as_str),
                    Some("image_only" | "searchable_dual_layer")
                ) =>
        {
            ("pdf", "pdf")
        }
        Some("text") if options.len() == 1 => {
            match options.get("text_representation").and_then(Value::as_str) {
                Some("txt") => ("text", "txt"),
                Some("json") => ("text", "json"),
                Some("markdown") => ("text", "md"),
                _ => return Err(HostIssuerError("INVALID_REQUEST")),
            }
        }
        _ => return Err(HostIssuerError("INVALID_REQUEST")),
    };
    Ok((format, extension))
}

pub(crate) fn build_export_grant(
    selected_path: &Path,
    format: &str,
    extension: &str,
    session_id: &str,
    grant_id: String,
    signing_key: &[u8; 32],
) -> Result<ExportGrant, HostIssuerError> {
    if !matches!(format, "png" | "zip" | "cbz" | "pdf" | "text") || session_id.is_empty() {
        return Err(HostIssuerError("REF_MALFORMED"));
    }
    let target_path = selected_path
        .to_str()
        .ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
    validate_absolute_path(target_path)?;
    let parent = selected_path
        .parent()
        .ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
    reject_reparse_path(parent)?;
    if !parent.is_dir() {
        return Err(HostIssuerError("REF_SCOPE_DENIED"));
    }
    if import_extension(selected_path).as_deref() != Some(extension) {
        return Err(HostIssuerError("REF_SCOPE_DENIED"));
    }
    let replace_existing = match fs::symlink_metadata(selected_path) {
        Ok(metadata) => {
            if metadata.file_type().is_symlink()
                || is_reparse_point(&metadata)
                || !metadata.is_file()
            {
                return Err(HostIssuerError("REF_REPARSE_POINT"));
            }
            true
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => false,
        Err(_) => return Err(HostIssuerError("REF_SCOPE_DENIED")),
    };
    let expires_at = unix_seconds() + 300.0;
    let signature_input = format!(
        "{grant_id}\0{session_id}\0{target_path}\0{format}\0{}\0{expires_at:.6}",
        if replace_existing { "1" } else { "0" }
    );
    let signature = base64url(&hmac_sha256(signing_key, signature_input.as_bytes()));
    let payload = json!({
        "grant_id": grant_id,
        "session_id": session_id,
        "target_path": target_path,
        "format": format,
        "replace_existing": replace_existing,
        "expires_at": expires_at,
        "signing_key": base64url(signing_key),
        "signature": signature,
    });
    Ok(ExportGrant {
        grant_id: grant_id.clone(),
        payload,
        reference: format!("etref1.{grant_id}.{signature}"),
    })
}

pub(crate) fn import_summary(value: Value) -> Result<ImportSummary, HostIssuerError> {
    let chapter_id = value
        .get("chapter_id")
        .and_then(Value::as_str)
        .ok_or(HostIssuerError("PROTOCOL_MALFORMED"))?
        .to_string();
    let cancelled = value
        .get("cancelled")
        .and_then(Value::as_bool)
        .ok_or(HostIssuerError("PROTOCOL_MALFORMED"))?;
    let sources = value
        .get("sources")
        .and_then(Value::as_array)
        .ok_or(HostIssuerError("PROTOCOL_MALFORMED"))?;
    let mut summary = ImportSummary {
        chapter_id,
        cancelled,
        imported_files: 0,
        skipped_files: 0,
        rejected_files: 0,
        pending_files: 0,
    };
    for file in sources.iter().flat_map(|source| {
        source
            .get("files")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
    }) {
        match file.get("outcome").and_then(Value::as_str) {
            Some("imported") => summary.imported_files += 1,
            Some("skipped") => summary.skipped_files += 1,
            Some("rejected" | "partial") => summary.rejected_files += 1,
            Some("pending") => summary.pending_files += 1,
            _ => return Err(HostIssuerError("PROTOCOL_MALFORMED")),
        }
    }
    Ok(summary)
}

pub(crate) fn export_summary(value: Value) -> Result<ExportSummary, HostIssuerError> {
    let export_id = value
        .get("export_id")
        .and_then(Value::as_str)
        .filter(|id| !id.is_empty())
        .ok_or(HostIssuerError("PROTOCOL_MALFORMED"))?
        .to_string();
    let status = value
        .get("status")
        .and_then(Value::as_str)
        .filter(|status| *status == "pending")
        .ok_or(HostIssuerError("PROTOCOL_MALFORMED"))?
        .to_string();
    Ok(ExportSummary { export_id, status })
}

fn import_entry(path: &Path) -> Result<Value, HostIssuerError> {
    let filename = path.to_str().ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
    validate_absolute_path(filename)?;
    let mut file = File::open(path).map_err(|_| HostIssuerError("SOURCE_READ_FAILED"))?;
    let before = file
        .metadata()
        .map_err(|_| HostIssuerError("SOURCE_READ_FAILED"))?;
    let before_id = file_identity(&file).ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
    let mut digest = Sha256::new();
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let count = file
            .read(&mut buffer)
            .map_err(|_| HostIssuerError("SOURCE_READ_FAILED"))?;
        if count == 0 {
            break;
        }
        digest.update(&buffer[..count]);
    }
    let after = file
        .metadata()
        .map_err(|_| HostIssuerError("SOURCE_READ_FAILED"))?;
    reject_reparse_path(path)?;
    let current = fs::symlink_metadata(path).map_err(|_| HostIssuerError("REF_SCOPE_DENIED"))?;
    let after_id = file_identity(&file).ok_or(HostIssuerError("REF_SCOPE_DENIED"))?;
    let current_file = File::open(path).map_err(|_| HostIssuerError("REF_SCOPE_DENIED"))?;
    if before_id != after_id
        || after_id != file_identity(&current_file).ok_or(HostIssuerError("REF_SCOPE_DENIED"))?
        || before.len() != after.len()
        || current.len() != after.len()
    {
        return Err(HostIssuerError("FILE_IDENTITY_CHANGED"));
    }
    Ok(json!({
        "path": filename,
        "facts": {
            "volume_serial": before_id.0,
            "file_index": before_id.1,
            "size": before.len(),
            "sha256": hex_lower(&digest.finalize()),
        }
    }))
}

fn sign_json(key: &[u8; 32], value: &Value) -> Result<String, HostIssuerError> {
    let bytes = serde_json::to_vec(value).map_err(|_| HostIssuerError("REF_MALFORMED"))?;
    Ok(base64url(&hmac_sha256(key, &bytes)))
}

fn hmac_sha256(key: &[u8], message: &[u8]) -> [u8; 32] {
    let mut key_block = [0u8; 64];
    if key.len() > key_block.len() {
        key_block[..32].copy_from_slice(&Sha256::digest(key));
    } else {
        key_block[..key.len()].copy_from_slice(key);
    }
    let mut inner = Sha256::new();
    let mut outer = Sha256::new();
    for byte in key_block {
        inner.update([byte ^ 0x36]);
        outer.update([byte ^ 0x5c]);
    }
    inner.update(message);
    outer.update(inner.finalize());
    outer.finalize().into()
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut result = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        result.push(HEX[(byte >> 4) as usize] as char);
        result.push(HEX[(byte & 15) as usize] as char);
    }
    result
}

fn unix_seconds() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

fn validate_absolute_path(raw: &str) -> Result<(), HostIssuerError> {
    let path = Path::new(raw);
    if !path.is_absolute()
        || raw
            .split(['\\', '/'])
            .any(|part| matches!(part, "." | ".."))
        || path
            .components()
            .any(|part| matches!(part, Component::CurDir | Component::ParentDir))
        || path.file_name().is_none()
    {
        return Err(HostIssuerError("REF_SCOPE_DENIED"));
    }
    Ok(())
}

fn reject_reparse_path(path: &Path) -> Result<(), HostIssuerError> {
    for ancestor in path.ancestors() {
        let metadata =
            fs::symlink_metadata(ancestor).map_err(|_| HostIssuerError("REF_SCOPE_DENIED"))?;
        if metadata.file_type().is_symlink() || is_reparse_point(&metadata) {
            return Err(HostIssuerError("REF_REPARSE_POINT"));
        }
    }
    Ok(())
}

#[cfg(windows)]
fn is_reparse_point(metadata: &Metadata) -> bool {
    use std::os::windows::fs::MetadataExt;
    metadata.file_attributes() & 0x400 != 0
}

#[cfg(not(windows))]
fn is_reparse_point(_: &Metadata) -> bool {
    false
}

fn file_identity(file: &File) -> Option<(u64, u64)> {
    crate::resource_protocol::file_identity(file)
}

#[cfg(windows)]
fn open_path(path: &Path, directory: bool) -> Result<File, HostIssuerError> {
    use std::os::windows::fs::OpenOptionsExt;
    const FILE_FLAG_BACKUP_SEMANTICS: u32 = 0x0200_0000;
    OpenOptions::new()
        .read(true)
        .custom_flags(if directory {
            FILE_FLAG_BACKUP_SEMANTICS
        } else {
            0
        })
        .open(path)
        .map_err(|_| HostIssuerError("REF_SCOPE_DENIED"))
}

#[cfg(not(windows))]
fn open_path(path: &Path, _: bool) -> Result<File, HostIssuerError> {
    File::open(path).map_err(|_| HostIssuerError("REF_SCOPE_DENIED"))
}

fn import_extension(path: &Path) -> Option<String> {
    path.extension()?.to_str().map(str::to_ascii_lowercase)
}

#[derive(Debug, PartialEq, Eq)]
enum SortPart {
    Text(String),
    Digits(String),
}

fn natural_cmp(left: &str, right: &str) -> std::cmp::Ordering {
    let left = natural_parts(left);
    let right = natural_parts(right);
    for (a, b) in left.iter().zip(&right) {
        let order = match (a, b) {
            (SortPart::Text(a), SortPart::Text(b)) => a.cmp(b),
            (SortPart::Digits(a), SortPart::Digits(b)) => {
                let a = a.trim_start_matches('0');
                let a = if a.is_empty() { "0" } else { a };
                let b = b.trim_start_matches('0');
                let b = if b.is_empty() { "0" } else { b };
                a.len().cmp(&b.len()).then_with(|| a.cmp(b))
            }
            (SortPart::Digits(_), SortPart::Text(_)) => std::cmp::Ordering::Less,
            (SortPart::Text(_), SortPart::Digits(_)) => std::cmp::Ordering::Greater,
        };
        if order != std::cmp::Ordering::Equal {
            return order;
        }
    }
    left.len().cmp(&right.len())
}

fn natural_parts(name: &str) -> Vec<SortPart> {
    let mut parts = Vec::new();
    let mut text = String::new();
    let mut digits = String::new();
    for ch in name.chars() {
        if ch.is_ascii_digit() {
            if !text.is_empty() {
                parts.push(SortPart::Text(text.to_lowercase()));
                text.clear();
            }
            digits.push(ch);
        } else {
            if !digits.is_empty() {
                parts.push(SortPart::Digits(std::mem::take(&mut digits)));
            }
            text.push(ch);
        }
    }
    if !digits.is_empty() {
        parts.push(SortPart::Digits(digits));
    }
    if !text.is_empty() || parts.is_empty() {
        parts.push(SortPart::Text(text.to_lowercase()));
    }
    parts
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn hmac_sha256_matches_rfc4231_vector() {
        let digest = hmac_sha256(&[0x0b; 20], b"Hi There");
        assert_eq!(
            hex_lower(&digest),
            "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        );
        assert_eq!(base64url(&digest).len(), 43);
    }

    #[test]
    fn import_signature_matches_core_canonical_json_vector() {
        let fields = json!({
            "grant_id": "grant_0123456789abcdef",
            "session_id": "host_0123456789",
            "scope_class": "user-source",
            "operation": "ImportPages",
            "access": "read-only",
            "source_path": "C:/Users/Alice/source.png",
            "source_kind": "file",
            "scope_identity": null,
            "entries": [{
                "path": "C:/Users/Alice/source.png",
                "facts": {
                    "volume_serial": 12,
                    "file_index": 34,
                    "size": 3,
                    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
                }
            }],
            "expires_at": "1792100000.123456"
        });
        assert_eq!(
            sign_json(&[7; 32], &fields).unwrap(),
            "g31yr_GYnheT7MMIrw5arYfMESItfbVuqe3LV8c46W8"
        );
    }

    #[test]
    fn export_signature_matches_core_nul_join_vector() {
        let signed = [
            "grant_0123456789abcdef",
            "host_0123456789",
            "C:/Users/Alice/out.pdf",
            "pdf",
            "1",
            "1792100000.123456",
        ]
        .join("\0");
        assert_eq!(
            base64url(&hmac_sha256(&[9; 32], signed.as_bytes())),
            "Gm53WhbMd9hCDPTMhse7FGuHxILSJlNNPGLbN2wd3V4"
        );
    }

    #[test]
    fn base64url_encodes_32_byte_credentials_without_padding() {
        let encoded = base64url(&[0u8; 32]);
        assert_eq!(encoded.len(), 43);
        assert!(!encoded.contains('='));
        assert_eq!(encoded, "A".repeat(42) + "A");
    }

    #[test]
    fn natural_sort_matches_p09_page_order() {
        let mut names = vec!["page10.png", "page2.png", "Page1.png"];
        names.sort_by(|a, b| natural_cmp(a, b));
        assert_eq!(names, ["Page1.png", "page2.png", "page10.png"]);
    }

    #[test]
    fn import_grant_ref_has_only_frozen_fields_and_directory_is_direct_only() {
        let temp = tempdir().unwrap();
        let root = temp.path().join("picked");
        fs::create_dir(&root).unwrap();
        fs::write(root.join("page10.png"), b"ten").unwrap();
        fs::write(root.join("page2.png"), b"two").unwrap();
        fs::create_dir(root.join("nested")).unwrap();
        fs::write(root.join("nested").join("page1.png"), b"nested").unwrap();

        let before = unix_seconds();
        let grant = build_import_grant(
            &root,
            "directory",
            "session_0123456789",
            "grant_0123456789".into(),
            &[7; 32],
        )
        .unwrap();
        let after = unix_seconds();
        let expires_at = grant.payload["expires_at"].as_f64().unwrap();
        assert!(expires_at >= before + 299.0 && expires_at <= after + 299.0);
        assert_eq!(
            grant
                .reference
                .as_object()
                .unwrap()
                .keys()
                .cloned()
                .collect::<Vec<_>>(),
            vec!["grant_id", "host_signature"]
        );
        assert_eq!(grant.payload["entries"].as_array().unwrap().len(), 2);
        assert_eq!(
            grant.payload["entries"][0]["path"].as_str().unwrap(),
            root.join("page2.png").to_str().unwrap()
        );
        assert_eq!(grant.payload["scope_class"], "user-source");
        assert_eq!(grant.payload["operation"], "ImportPages");
        assert_eq!(grant.payload["access"], "read-only");
        assert_eq!(
            grant.payload["signature"],
            grant.reference["host_signature"]
        );
    }

    #[test]
    fn export_ref_is_one_target_token_with_frozen_prefix() {
        let temp = tempdir().unwrap();
        let target = temp.path().join("out.pdf");
        let grant = build_export_grant(
            &target,
            "pdf",
            "pdf",
            "session_0123456789",
            "grant_0123456789".into(),
            &[9; 32],
        )
        .unwrap();
        assert!(grant.reference.starts_with("etref1.grant_0123456789."));
        assert_eq!(grant.reference.split('.').count(), 3);
        assert!(grant.payload["signature"].as_str().unwrap().len() == 43);
        assert_eq!(
            grant.payload["expires_at"].as_f64().unwrap().floor(),
            unix_seconds().floor() + 300.0
        );
    }

    #[test]
    fn unsupported_import_source_and_mismatched_export_extension_fail_closed() {
        let temp = tempdir().unwrap();
        let source = temp.path().join("source.txt");
        fs::write(&source, b"not an import format").unwrap();
        assert_eq!(
            build_import_grant(
                &source,
                "file",
                "session_0123456789",
                "grant_0123456789".into(),
                &[7; 32],
            )
            .unwrap_err()
            .0,
            "REF_SCOPE_DENIED"
        );
        let target = temp.path().join("out.pdf");
        assert_eq!(
            build_export_grant(
                &target,
                "pdf",
                "png",
                "session_0123456789",
                "grant_0123456789".into(),
                &[9; 32],
            )
            .unwrap_err()
            .0,
            "REF_SCOPE_DENIED"
        );
        assert!(!target.exists());
    }

    #[test]
    fn webview_summaries_exclude_paths_and_refs() {
        let imported = import_summary(json!({
            "chapter_id": "chapter-1", "cancelled": false,
            "sources": [{"source_name":"C:/private/folder", "files":[
                {"filename":"C:/private/page.png", "outcome":"imported", "grant_id":"secret", "source_path":"C:/private"}
            ]}]
        })).unwrap();
        let text = serde_json::to_string(&imported).unwrap();
        assert!(
            !text.contains("private") && !text.contains("grant_id") && !text.contains("secret")
        );
        let exported = export_summary(json!({"export_id":"exp-1", "status":"pending", "output_path":"C:/private/out.pdf", "target_ref":"secret"})).unwrap();
        let text = serde_json::to_string(&exported).unwrap();
        assert!(
            !text.contains("private") && !text.contains("target_ref") && !text.contains("secret")
        );
    }
}
