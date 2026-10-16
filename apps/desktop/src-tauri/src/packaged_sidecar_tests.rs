//! Real packaged-sidecar acceptance path. The existing tests in `main.rs`
//! and `library_bridge.rs` intentionally keep their source-backed contract.

use crate::core_bridge::{CoreChannel, StdioCoreChannel};
use crate::library_bridge::{LibraryChannel, StdioLibraryChannel};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::Duration;

struct PackagedLab {
    _dir: tempfile::TempDir,
    bundle: PathBuf,
    derived: PathBuf,
    managed: PathBuf,
    catalog: PathBuf,
    data: PathBuf,
}

impl PackagedLab {
    fn new() -> Self {
        assert_eq!(std::env::var("M2RC1_PACKAGED").unwrap_or_default(), "1");
        assert!(std::env::var_os("M2RC1_SRC_ROOT").is_none());
        assert!(std::env::var_os("M2RC1_PYTHON").is_none());

        let bundle = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("target/core-sidecar/core-sidecar")
            .canonicalize()
            .expect("current worktree frozen sidecar bundle exists");
        let dir = tempfile::tempdir().expect("isolated packaged acceptance data root");
        let derived = dir.path().join("derived");
        let managed = dir.path().join("managed");
        let catalog = dir.path().join("catalog.sqlite");
        let data = dir.path().join("data");
        fs::create_dir_all(&derived).unwrap();
        fs::create_dir_all(&managed).unwrap();
        fs::create_dir_all(&data).unwrap();

        println!("PACKAGED_ENV M2RC1_PACKAGED=1 M2RC1_SRC_ROOT=<unset> M2RC1_PYTHON=<unset>");
        Self {
            _dir: dir,
            bundle,
            derived,
            managed,
            catalog,
            data,
        }
    }

    fn exe(&self, name: &str) -> PathBuf {
        self.bundle.join(name)
    }

    fn report_start<T: std::fmt::Debug>(&self, exe: &Path, args: T) {
        let exe = exe.canonicalize().expect("frozen executable path");
        assert!(
            exe.starts_with(&self.bundle),
            "executable must come from bundle"
        );
        let bytes = fs::read(&exe).expect("read executable for SHA-256 evidence");
        let sha256 = format!("{:x}", Sha256::digest(&bytes));
        println!(
            "PACKAGED_START exe={} bytes={} sha256={} args={args:?}",
            exe.display(),
            bytes.len(),
            sha256
        );
    }

    fn seed_catalog(&self, rows: &[(&str, &str)]) {
        fs::write(self.derived.join("asset.png"), b"sidecar-payload").unwrap();
        let loader = self.exe("catalog_loader.exe");
        let mut args = vec![
            "--db".to_string(),
            self.catalog.to_string_lossy().into_owned(),
            "--initialize-preview-namespace".to_string(),
            self.derived.to_string_lossy().into_owned(),
        ];
        for (resource_id, relative_path) in rows {
            args.extend([
                "--set".to_string(),
                format!("{resource_id}={relative_path}"),
            ]);
        }
        self.report_start(&loader, &args);
        let output = Command::new(&loader)
            .args(&args)
            .current_dir(&self.bundle)
            .output()
            .expect("frozen catalog_loader.exe starts");
        println!(
            "PACKAGED_EXIT exe={} code={} stdout={} stderr={}",
            loader.display(),
            output.status.code().unwrap_or(-1),
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(output.status.success(), "frozen catalog loader failed");
    }

    fn start_library(&self) -> StdioLibraryChannel {
        let exe = self.exe("core_service.exe");
        let exe_arg = exe.to_string_lossy().into_owned();
        self.report_start(&exe, ["-m", "bootstrap.core_service"]);
        // Reviewer reproduced two false 30s timeouts in a 111.59s loaded six-test run; the isolated retry passed in 13.58s. The 68,717,156-byte frozen PyInstaller executable needs headroom, while its real startup ping remains mandatory.
        let startup_timeout_secs = match std::env::var("M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS") {
            Ok(value) => value
                .parse::<u64>()
                .expect("M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS must be an integer"),
            Err(std::env::VarError::NotPresent) => 120,
            Err(error) => panic!("cannot read M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS: {error}"),
        };
        assert!(startup_timeout_secs > 0, "startup timeout must be positive");
        println!("PACKAGED_STARTUP_TIMEOUT_SECS={startup_timeout_secs}");
        StdioLibraryChannel::spawn_with_startup_ping(
            &exe_arg,
            &self.bundle,
            Some(&self.data),
            Some(&self.derived),
            Some(&self.catalog),
            Duration::from_secs(startup_timeout_secs),
        )
        .expect("production startup ping over the frozen core_service.exe")
    }
}

#[test]
fn real_core_sidecar_round_trip() {
    let lab = PackagedLab::new();
    lab.seed_catalog(&[("res-sidecar", "asset.png")]);
    let exe = lab.exe("host_bridge.exe");
    lab.report_start(&exe, Vec::<&str>::new());
    let channel = StdioCoreChannel::spawn_packaged(&exe, &lab.derived, &lab.managed, &lab.catalog)
        .expect("frozen host_bridge.exe starts");

    let issued = channel.issue("res-sidecar", "rev-1").expect("issue");
    assert!(issued.opaque_id.starts_with("m2id.v1."));
    let grant = channel.resolve(&issued.opaque_id).expect("resolve");
    assert_eq!(grant.rel_path, "asset.png");
    assert_eq!(grant.size, 15);
    assert_eq!(grant.sha256.len(), 64);
    channel.revoke(&issued.opaque_id).unwrap();
    let error = channel.resolve(&issued.opaque_id).unwrap_err();
    assert_eq!(error.code, "REF_REVOKED");
    drop(channel); // StdioCoreChannel sends shutdown and waits for this frozen child.
    println!(
        "PACKAGED_RESULT real_core_sidecar_round_trip=PASS typed_error=REF_REVOKED shutdown=sent"
    );
}

#[test]
fn real_library_sidecar_round_trip_and_eof() {
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    let ping = channel.ping().expect("ping");
    assert_eq!(ping.status, "ready");
    assert_eq!(ping.protocol_version.major, 2);
    assert_eq!(ping.protocol_version.minor, 3);
    assert!(ping
        .capabilities
        .contains(&"library.list_books".to_string()));
    assert!(channel.list_books().expect("list_books").is_empty());
    channel.kill_for_test();
    let error = channel.ping().unwrap_err();
    assert_eq!(error.code, "CORE_UNAVAILABLE");
    assert!(error.retryable);
    println!("PACKAGED_RESULT real_library_sidecar_round_trip_and_eof=PASS protocol=2.3 eof=CORE_UNAVAILABLE");
}

#[test]
fn real_core_sidecar_settings_round_trip_and_typed_rejection() {
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    let full = channel.get_settings(None).expect("full settings read");
    assert!(full.get("settings").is_some());
    let unset = channel.get_settings(Some("sfx")).expect("section read");
    assert_eq!(unset["settings"]["sfx"], serde_json::Value::Null);
    let updated = channel
        .update_settings_section("sfx", &serde_json::json!({ "policy": "translate" }))
        .expect("legal update");
    assert_eq!(updated["settings"]["sfx"]["policy"], "translate");
    let readback = channel.get_settings(Some("sfx")).expect("readback");
    assert_eq!(readback["settings"]["sfx"]["policy"], "translate");
    let error = channel
        .update_settings_section("sfx", &serde_json::json!({ "policy": "bogus" }))
        .unwrap_err();
    assert_eq!(error.code, "INVALID_REQUEST");
    assert_eq!(error.category, "validation");
    let still = channel
        .get_settings(Some("sfx"))
        .expect("read after reject");
    assert_eq!(still["settings"]["sfx"]["policy"], "translate");
    println!("PACKAGED_RESULT real_core_sidecar_settings_round_trip_and_typed_rejection=PASS typed_error=INVALID_REQUEST");
}

#[test]
fn real_core_sidecar_retype_pair_empty_page_and_typed_rejection() {
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    let empty = channel
        .list_regions("no-such-page")
        .expect("unknown page is an empty read");
    assert_eq!(empty["regions"], serde_json::json!([]));
    let error = channel
        .set_region_type("no-such-region", "sfx", None)
        .unwrap_err();
    assert_eq!(error.code, "TARGET_NOT_FOUND");
    assert_eq!(error.category, "not_found");
    println!("PACKAGED_RESULT real_core_sidecar_retype_pair_empty_page_and_typed_rejection=PASS typed_error=TARGET_NOT_FOUND");
}

#[test]
fn real_core_sidecar_rc4_commands_round_trip_typed_errors() {
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    assert_eq!(
        channel
            .list_region_revisions("no-such-region")
            .unwrap_err()
            .code,
        "TARGET_NOT_FOUND"
    );
    assert_eq!(
        channel
            .restore_region_revision("no-such-region", 1, 1)
            .unwrap_err()
            .code,
        "TARGET_NOT_FOUND"
    );
    assert_eq!(
        channel.rerender_page("no-such-page").unwrap_err().code,
        "TARGET_NOT_FOUND"
    );
    println!("PACKAGED_RESULT real_core_sidecar_rc4_commands_round_trip_typed_errors=PASS typed_error=TARGET_NOT_FOUND");
}

#[test]
fn real_core_sidecar_answers_startup_ping_on_fresh_catalog() {
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    let ping = channel.ping().expect("post-startup ping");
    assert_eq!(ping.status, "ready");
    assert_eq!(ping.protocol_version.major, 2);
    assert_eq!(ping.protocol_version.minor, 3);
    assert!(lab.catalog.is_file(), "frozen Core bound the fresh catalog");
    println!("PACKAGED_RESULT real_core_sidecar_answers_startup_ping_on_fresh_catalog=PASS protocol=2.3 catalog=created");
}

#[test]
fn host_import_grant_round_trip_reaches_frozen_import_pages() {
    let lab = PackagedLab::new();
    let source = lab._dir.path().join("selected.png");
    fs::write(&source, b"selected import source").unwrap();
    let channel = lab.start_library();
    channel.open_host_session().expect("OpenHostSession");

    // The typed ImportPages error proves registration succeeded without an unrelated library fixture.
    let error = channel
        .import_from_path(&source, "file", "missing-chapter", None)
        .err()
        .expect("ImportPages should return the missing chapter error");
    assert_eq!(error.code, "TARGET_NOT_FOUND");
    assert_eq!(error.category, "not_found");
    println!("PACKAGED_RESULT host_import_grant_round_trip_reaches_frozen_import_pages=PASS register=accepted import_error=TARGET_NOT_FOUND");
}

#[test]
fn host_export_grant_round_trip_reaches_frozen_start_export() {
    let lab = PackagedLab::new();
    let target = lab._dir.path().join("export.png");
    let channel = lab.start_library();
    channel.open_host_session().expect("OpenHostSession");

    // The typed StartExport error proves RegisterExportTarget accepted the grant.
    let error = channel
        .start_export_to_path(
            &target,
            serde_json::json!({
                "chapter_id": "missing-chapter",
                "page_ids": ["missing-page"],
                "format": "png",
                "format_options": {},
                "stale_policy": "abort"
            }),
        )
        .err()
        .expect("StartExport should return the missing chapter error");
    assert_eq!(error.code, "TARGET_NOT_FOUND");
    assert_eq!(error.category, "not_found");
    assert!(!target.exists());
    println!("PACKAGED_RESULT host_export_grant_round_trip_reaches_frozen_start_export=PASS register=accepted export_error=TARGET_NOT_FOUND target_written=false");
}
