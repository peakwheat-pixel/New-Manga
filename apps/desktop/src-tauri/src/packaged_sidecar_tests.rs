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
    let sources = [
        (
            "selected-a.png",
            include_bytes!("../../../../experiments/TASK-016/samples/jp_horizontal.png").as_slice(),
        ),
        (
            "selected-b.png",
            include_bytes!("../../../../experiments/TASK-016/samples/ko_horizontal.png").as_slice(),
        ),
        ("selected-invalid.png", b"invalid image".as_slice()),
    ]
    .map(|(name, bytes)| {
        let path = lab._dir.path().join(name);
        fs::write(&path, bytes).unwrap();
        path
    });
    let channel = lab.start_library();
    channel.open_host_session().expect("OpenHostSession");
    let book = channel.create_book("Multi-import acceptance").unwrap();
    let chapter = channel
        .create_chapter(&book.book_id, "Chapter 1", None)
        .unwrap();

    let summary = channel
        .import_from_paths(&sources, "file", &chapter.chapter_id, None)
        .expect("batched ImportPages should process all selected sources");
    let pages = channel.list_chapter_pages(&chapter.chapter_id).unwrap();
    let summary = serde_json::to_value(summary).unwrap();
    assert_eq!(summary["imported_files"], 2);
    assert_eq!(summary["rejected_files"], 1);
    assert_eq!(pages["pages"].as_array().unwrap().len(), 2);

    let folder = lab._dir.path().join("selected-folder");
    fs::create_dir(&folder).unwrap();
    for (name, bytes) in [
        (
            "01-jp-vertical.png",
            include_bytes!("../../../../experiments/TASK-016/samples/jp_vertical.png").as_slice(),
        ),
        (
            "02-art-text.png",
            include_bytes!("../../../../experiments/TASK-016/samples/art_text.png").as_slice(),
        ),
        (
            "03-long-tile.png",
            include_bytes!("../../../../experiments/TASK-016/samples/long_tile.png").as_slice(),
        ),
    ] {
        fs::write(folder.join(name), bytes).unwrap();
    }
    let folder_summary = channel
        .import_from_path(&folder, "directory", &chapter.chapter_id, None)
        .expect("folder grant should import each direct child in one ImportPages request");
    let folder_summary = serde_json::to_value(folder_summary).unwrap();
    assert_eq!(folder_summary["imported_files"], 3);
    let pages = channel.list_chapter_pages(&chapter.chapter_id).unwrap();
    assert_eq!(pages["pages"].as_array().unwrap().len(), 5);
    println!("PACKAGED_RESULT host_multi_and_folder_import_reach_frozen_import_pages=PASS multi_sources=3 requests=1 imported=2 rejected=1 folder_direct_children=3 folder_requests=1 pages=5");
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
                "book_id": "missing-book",
                "chapter_ids": ["missing-chapter"],
                "ordered_page_ids": ["missing-page"],
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

#[test]
fn run_command_wire_reaches_the_frozen_core_run_family() {
    // RUN-IPC-1: fixture-free evidence that the host transport really reaches the
    // Core's frozen Run family (P13-C1 section 5.5). A wrong wire name, a wrong
    // payload shape or a missing channel override would surface as a transport /
    // protocol failure (or as the trait's fail-closed CORE_UNAVAILABLE default);
    // a live Core answers at the DOMAIN level instead -- which is exactly what
    // these assertions pin. No book/chapter fixture is needed, so the read-only
    // and rejection paths can be proven on the frozen 2.3 bundle today.
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    assert_eq!(channel.ping().expect("post-startup ping").status, "ready");

    fn assert_domain_rejection(label: &str, error: crate::library_bridge::LibraryError) {
        println!(
            "RUN_IPC_RESULT {label} code={} category={}",
            error.code, error.category
        );
        assert_ne!(
            error.code, "CORE_UNAVAILABLE",
            "{label} must not fall through to the fail-closed default"
        );
        assert_ne!(
            error.code, "PROTOCOL_MALFORMED",
            "{label} must be a Core domain rejection, not a wire-level failure"
        );
    }

    assert_domain_rejection(
        "get_run_snapshot",
        channel
            .get_run_snapshot("no-such-run")
            .expect_err("an unknown run id must be rejected"),
    );
    assert_domain_rejection(
        "get_task_projection",
        channel
            .get_task_projection("no-such-run")
            .expect_err("an unknown run id must be rejected"),
    );
    assert_domain_rejection(
        "control_run",
        channel
            .control_run("no-such-run", "pause", None)
            .expect_err("an unknown run id must be rejected"),
    );
    assert_domain_rejection(
        "resume_blocked_run",
        channel
            .resume_blocked_run("no-such-run")
            .expect_err("an unknown run id must be rejected"),
    );
    assert_domain_rejection(
        "retry_failed_targets",
        channel
            .retry_failed_targets("no-such-run", "idem-key-run-ipc-1")
            .expect_err("an unknown run id must be rejected"),
    );
    assert_domain_rejection(
        "start_run",
        channel
            .start_run(
                "detect",
                &serde_json::json!({ "book_id": "missing-book" }),
                None,
                "idem-key-run-ipc-1",
            )
            .expect_err("an unresolvable scope must be rejected"),
    );
    println!("PACKAGED_RESULT run_command_wire_reaches_the_frozen_core_run_family=PASS six_commands=domain_rejections");
}

#[test]
fn real_library_sidecar_event_sink_registration_and_lifecycle() {
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    let received_events = std::sync::Arc::new(std::sync::Mutex::new(Vec::<(String, serde_json::Value)>::new()));
    let sink_events = std::sync::Arc::clone(&received_events);
    channel.set_event_sink(std::sync::Arc::new(move |name, payload| {
        sink_events.lock().unwrap().push((name.to_string(), payload));
    }));

    let ping = channel.ping().expect("ping");
    assert_eq!(ping.status, "ready");
    let books = channel.list_books().expect("list_books");
    assert!(books.is_empty());

    // In steady-state idle operations, 0 spontaneous events emitted
    assert!(received_events.lock().unwrap().is_empty());
    println!("PACKAGED_RESULT real_library_sidecar_event_sink_registration_and_lifecycle=PASS event_sink=registered");
}

#[test]
fn export_command_wire_reaches_the_frozen_core_export_family() {
    // EXPORT-IPC-1: fixture-free evidence that the host transport really reaches the
    // Core's frozen Export family (M2-C1 rev 2.5 §5.8). A wrong wire name, a wrong
    // payload shape or a missing channel override would surface as a transport /
    // protocol failure (or as the trait's fail-closed CORE_UNAVAILABLE default);
    // a live Core answers at the DOMAIN level instead -- which is exactly what
    // these assertions pin. No book/chapter fixture is needed, so the read-only
    // and rejection paths can be proven on the frozen 2.3 bundle today.
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    assert_eq!(channel.ping().expect("post-startup ping").status, "ready");

    fn assert_domain_rejection(label: &str, error: crate::library_bridge::LibraryError) {
        println!(
            "EXPORT_IPC_RESULT {label} code={} category={}",
            error.code, error.category
        );
        assert_ne!(
            error.code, "CORE_UNAVAILABLE",
            "{label} must not fall through to the fail-closed default"
        );
        assert_ne!(
            error.code, "PROTOCOL_MALFORMED",
            "{label} must be a Core domain rejection, not a wire-level failure"
        );
    }

    // AC4-② & AC4-③: GetExportSnapshot on unknown export_id returns domain-level EXPORT_NOT_FOUND
    let snapshot_err = channel
        .get_export_snapshot("no-such-export-id")
        .expect_err("unknown export_id must return domain error");
    assert_domain_rejection("get_export_snapshot", snapshot_err.clone());
    assert_eq!(snapshot_err.code, "EXPORT_NOT_FOUND");
    assert_eq!(snapshot_err.category, "not_found");

    // AC4-② & AC4-③: CancelExport on unknown export_id returns domain-level EXPORT_NOT_FOUND
    let cancel_err = channel
        .cancel_export("no-such-export-id")
        .expect_err("unknown export_id must return domain error");
    assert_domain_rejection("cancel_export", cancel_err.clone());
    assert_eq!(cancel_err.code, "EXPORT_NOT_FOUND");
    assert_eq!(cancel_err.category, "not_found");

    // AC4-② & AC4-③: GetExportHistory on fresh catalog returns empty list without error
    let history = channel
        .get_export_history()
        .expect("empty export history must return empty list, not error");
    assert!(
        history.exports.is_empty(),
        "fresh catalog must yield empty export history"
    );

    // AC3: Path zero leakage assertions - serialized history must not contain any paths or target refs
    let history_serialized = serde_json::to_string(&history).expect("must serialize history");
    assert!(
        !history_serialized.contains("output_path"),
        "history view must not contain output_path"
    );
    assert!(
        !history_serialized.contains("target_ref"),
        "history view must not contain target_ref"
    );
    assert!(
        !history_serialized.contains(":\\"),
        "history view must not contain drive path"
    );

    println!("PACKAGED_RESULT export_command_wire_reaches_the_frozen_core_export_family=PASS three_commands=domain_verified");
}

fn reader_store_hashes(data_root: &Path) -> [Option<String>; 2] {
    ["library.db", "library.db-wal"].map(|name| match fs::read(data_root.join(name)) {
        Ok(bytes) => Some(format!("{:x}", Sha256::digest(bytes))),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => None,
        Err(error) => panic!("cannot read isolated progress store: {error}"),
    })
}

#[test]
fn reader_commands_reach_frozen_core_with_typed_rejections() {
    // The isolated data directory keeps the persistent save command away
    // from the main repository and any user library. These deliberately
    // reject so no successful progress write or projection is fabricated.
    let lab = PackagedLab::new();
    let channel = lab.start_library();
    let ping = channel.ping().expect("frozen Core startup ping");
    assert_eq!(
        (ping.protocol_version.major, ping.protocol_version.minor),
        (2, 3)
    );

    let missing_chapter = channel
        .get_reader_projection("missing-chapter", "original", "resume")
        .unwrap_err();
    assert_eq!(missing_chapter.code, "TARGET_NOT_FOUND");
    assert_eq!(missing_chapter.category, "not_found");

    let invalid_mode = channel
        .get_reader_projection("missing-chapter", "invalid", "resume")
        .unwrap_err();
    assert_eq!(invalid_mode.code, "INVALID_REQUEST");
    assert_eq!(invalid_mode.category, "validation");

    let database = lab.data.join("library.db");
    assert!(database.is_file(), "isolated library database must exist");
    let before = reader_store_hashes(&lab.data);
    let missing_page = channel
        .save_reading_progress("missing-chapter", "original", "missing-page", None, None)
        .unwrap_err();
    assert_eq!(missing_page.code, "TARGET_NOT_FOUND");
    assert_eq!(missing_page.category, "not_found");
    assert_eq!(
        reader_store_hashes(&lab.data),
        before,
        "rejected progress save must not change SQLite data"
    );

    let data_path = lab.data.to_string_lossy();
    for error in [&missing_chapter, &invalid_mode, &missing_page] {
        assert!(!error
            .message
            .as_deref()
            .unwrap_or("")
            .contains(data_path.as_ref()));
    }
    println!("READER_IPC_RESULT get_reader_projection=TARGET_NOT_FOUND invalid_mode=INVALID_REQUEST save_reading_progress=TARGET_NOT_FOUND sqlite_unchanged=true protocol=2.3");
}
