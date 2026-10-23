fn main() {
    println!("cargo:rerun-if-env-changed=M2RC1_DEV_PREVIEW");

    // M2-AC5-BUILD-FRESH-CHECKOUT: fail-closed, actionable probe for the
    // gitignored Core sidecar bundle BEFORE tauri_build::try_build runs.
    //
    // tauri.conf.json declares `bundle.resources` pointing at
    // `target/core-sidecar/core-sidecar`, which is a PyInstaller build
    // artifact (gitignored, so absent on a fresh checkout). When it is
    // missing, try_build aborts with an opaque internal error
    // ("resource path ... doesn't exist") that gives the developer no
    // recoverable next step (root cause of the M2-AC5 integration i1
    // EXIT=101). This probe replaces that with an actionable panic whose
    // first line names the problem and points at the regeneration script.
    //
    // Deliberately NOT auto-running PyInstaller here: build.rs must stay
    // fast, deterministic and free of Python/venv dependencies; fail-closed
    // + diagnosable beats hidden heavy rebuilds. The build script's cwd is
    // unspecified, so anchor on CARGO_MANIFEST_DIR (this crate's dir).
    let dev_preview = std::env::var("M2RC1_DEV_PREVIEW").unwrap_or_default() == "1";
    if !dev_preview {
        let sidecar_bundle = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join("core-sidecar")
            .join("core-sidecar");
        if !sidecar_bundle.is_dir() {
            panic!(
                "missing sidecar bundle: {} does not exist (gitignored build artifact, absent on a fresh checkout).\n\
                 Fix: run `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1` from the repository root (add -Force to rebuild an existing bundle).\n\
                 See packaging/m2ac5/README.md (fresh checkout section) for the full setup.",
                sidecar_bundle.display()
            );
        }
    } else {
        // Local preview runs Python Core via `python -m infrastructure.resource_channel.host_bridge`; it never bundles a sidecar.
    }

    // RC2-AC1 (F-03) + R2-01(a): the app's own commands are declared in the
    // APPLICATION manifest of the Access Control List (NOT as an inlined
    // plugin -- plugin entries are keyed `plugin:<name>|<cmd>` and never
    // match bare command invocations, so the ACL layer silently skipped
    // them). With `__app-acl__` present, Tauri enforces the capability for
    // every bare command: `capabilities/m2rc1-commands.json` grants exactly
    // the sixty-eight commands below: 61 production (3 resource + 2 IPC1 +
    // 2 create + 2 existing settings + 3 cleanup + 4 backup + 19 P15 settings
    // + 2 retype + 3 RC-4 + 1 page
    // resolve + 2 page navigation + 2 Reader + 3 Host Issuer + 6 Run +
    // 1 reveal + 3 export + 2 delete), four probe, and three M2-AC1 acceptance commands;
    // any other command name
    // (e.g. the deleted `register_catalog`) is refused by the ACL before the invoke
    // handler is consulted. The settings_* pair (M2-SETTINGS-IPC-CHANNEL,
    // contract rev 1.3 §5.3), the cleanup trio (SETTINGS-OPEN-B-2, design
    // §4.3) and the region-retype pair (M2-REGION-RETYPE-
    // CORE, contract rev 1.4 §5.4) and P15 rev 2.7 settings are production-only; the probe commands
    // additionally require probe mode, and the three acceptance commands
    // require the M2-AC1 test mode at runtime (main.rs).
    //
    // Synchronisation note (R2-04): the command list below, the literal list
    // in main.rs `generate_handler!`, and the `command_allowlist` constant
    // array are three hand-maintained views of the same surface; the Rust
    // unit tests pin the constants and the E2E runner pins the announced
    // allowlist per mode. Keep all three in sync in the same commit.
    tauri_build::try_build(tauri_build::Attributes::new().app_manifest(
        tauri_build::AppManifest::new().commands(&[
            "issue_resource_url",
            "revoke_ref",
            "revoke_resource_refs",
            "core_ping",
            "library_list_books",
            "library_list_recycle_bin_books",
            "library_create_book",
            "create_chapter",
            // M2-SETTINGS-IPC-CHANNEL (contract rev 1.3 §5.3): production-
            // only settings read/write pair; ACL-declared so the capability
            // file can name them, registered at runtime ONLY in production
            // mode (main.rs SETTINGS_PRODUCTION_ONLY_COMMANDS).
            "settings_get",
            "settings_update_section",
            // SETTINGS-OPEN-B-2 (design §4.3): production-only cache/Revision
            // maintenance trio; ACL-declared so the capability file can name
            // them, registered at runtime ONLY in production mode (main.rs
            // CLEANUP_PRODUCTION_ONLY_COMMANDS).
            "cleanup_preview",
            "cleanup_run",
            "cleanup_retry_pending",
            // SETTINGS-OPEN-C-2-BACKUP (design §3.4): production-only
            // .nmbak package face; ACL-declared so the capability file can
            // name them, registered at runtime ONLY in production mode
            // (main.rs BACKUP_PRODUCTION_ONLY_COMMANDS).
            "backup_create",
            "backup_list",
            "backup_restore",
            "backup_delete",
            // P15-C1 rev 2.7 G21/G22/G23/G24: 19 production-only settings commands.
            "settings_provider_profiles_list",
            "settings_provider_profiles_create",
            "settings_provider_profiles_update",
            "settings_provider_profiles_delete",
            "settings_provider_bindings_set",
            "settings_provider_bindings_clear",
            "settings_provider_bindings_resolve",
            "settings_provider_run_snapshot_get",
            "settings_network_profiles_list",
            "settings_network_profiles_create",
            "settings_network_profiles_update",
            "settings_network_profiles_delete",
            "settings_network_profiles_test",
            "settings_network_profile_default_set",
            "settings_network_profile_default_clear",
            "settings_network_profile_resolve",
            "settings_resolve_overrides",
            "credential_put",
            "credential_clear",
            // M2-REGION-RETYPE-CORE (contract rev 1.4 §5.4): production-
            // only region retype write/read pair; ACL-declared so the
            // capability file can name them, registered at runtime ONLY in
            // production mode (main.rs RETYPE_PRODUCTION_ONLY_COMMANDS).
            "set_region_type",
            "list_regions",
            // RC-4 history/restore/render commands: production-only at
            // runtime, but declared here so the Tauri ACL can name them.
            "list_region_revisions",
            "restore_region_revision",
            "rerender_page",
            // M2-PAGE-RESOURCE-RESOLVE-1: production-only page display
            // image resolve; declared here so the Tauri ACL can name it.
            "resolve_page_resource",
            // M2-PAGE-NAV-PROJECTION-1: production-only page navigation
            // projections; declared here so the Tauri ACL can name them.
            "list_chapters",
            "list_chapter_pages",
            // READER-IPC-1: production-only Reader projection and progress
            // commands; omitted from frozen probe/AC1 runtime surfaces.
            "library_get_reader_projection",
            "library_save_reading_progress",
            // HOST-ISSUER-1 safe user actions. HostControl methods themselves
            // are internal stdio operations and are not Tauri commands.
            "library_import_file",
            "library_import_folder",
            "library_start_export",
            // RUN-IPC-1: production-only transport for the P13-C1 §5.5 Run
            // command surface; ACL-declared so the capability file can name
            // them, registered at runtime ONLY in production mode.
            "library_start_run",
            "library_control_run",
            "library_resume_blocked_run",
            "library_get_run_snapshot",
            "library_get_task_projection",
            "library_retry_failed_targets",
            // EXPORT-REVEAL-1: current-session export reveal, production-only
            // at runtime; the opener plugin itself remains inaccessible to JS.
            "library_reveal_export_folder",
            // EXPORT-IPC-1: production-only transport for the export control
            // and query surface; declared so the capability file can name them.
            "library_cancel_export",
            "library_get_export_snapshot",
            "library_get_export_history",
            // P09-AC3-DELETE-1: production-only project-level permanent deletion commands
            "library_delete_book_permanently",
            "library_delete_books_permanently",
            "probe_config",
            "probe_write_results",
            "probe_exit",
            "probe_issue_url",
            // M2-AC1 acceptance commands: ACL-declared so the capability file
            // can name them, but registered at runtime ONLY in the explicit
            // test startup configuration (M2AC1_TEST_MODE=1) — production
            // and probe modes never register them (main.rs AC1_TEST_COMMANDS).
            "ac1_request",
            "ac1_write_results",
            "ac1_exit",
        ]),
    ))
    .expect("failed to run tauri-build");
}
