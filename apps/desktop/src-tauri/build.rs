fn main() {
    // RC2-AC1 (F-03) + R2-01(a): the app's own commands are declared in the
    // APPLICATION manifest of the Access Control List (NOT as an inlined
    // plugin -- plugin entries are keyed `plugin:<name>|<cmd>` and never
    // match bare command invocations, so the ACL layer silently skipped
    // them). With `__app-acl__` present, Tauri enforces the capability for
    // every bare command: `capabilities/m2rc1-commands.json` grants exactly
    // the ten commands below to the main window (seven RC1/RC2 + three
    // M2-AC1 acceptance commands), and any other command name (e.g. the
    // deleted `register_catalog`) is refused by the ACL before the invoke
    // handler is consulted. The three acceptance commands additionally
    // require the M2-AC1 test mode at runtime (main.rs).
    //
    // Synchronisation note (R2-04): the command list below, the literal list
    // in main.rs `generate_handler!`, and the `command_allowlist` constant
    // array are three hand-maintained views of the same surface; the Rust
    // unit tests pin the constants and the E2E runner pins the announced
    // allowlist per mode. Keep all three in sync in the same commit.
    tauri_build::try_build(
        tauri_build::Attributes::new().app_manifest(tauri_build::AppManifest::new().commands(&[
            "issue_resource_url",
            "revoke_ref",
            "revoke_resource_refs",
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
        ])),
    )
    .expect("failed to run tauri-build");
}
