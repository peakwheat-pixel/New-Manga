fn main() {
    // RC2-AC1 (F-03) + R2-01(a): the app's own commands are declared in the
    // APPLICATION manifest of the Access Control List (NOT as an inlined
    // plugin -- plugin entries are keyed `plugin:<name>|<cmd>` and never
    // match bare command invocations, so the ACL layer silently skipped
    // them). With `__app-acl__` present, Tauri enforces the capability for
    // every bare command: `capabilities/m2rc1-commands.json` grants exactly
    // the seven commands below to the main window, and any other command
    // name (e.g. the deleted `register_catalog`) is refused by the ACL
    // before the invoke handler is consulted.
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
        ])),
    )
    .expect("failed to run tauri-build");
}
