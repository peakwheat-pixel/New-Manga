fn main() {
    // RC2-AC1 (F-03): the app's own commands are managed by the Tauri ACL via
    // an inlined plugin, so `capabilities/m2rc1-commands.json` gates which
    // window may invoke them at all (defense in depth on top of the
    // conditional invoke_handler registration in main.rs). Probe-mode-only
    // commands are declared here too: the ACL answers "is this window
    // allowed", while the runtime allowlist answers "does this command exist
    // in this mode".
    tauri_build::try_build(
        tauri_build::Attributes::new().plugin(
            "m2rc1-commands",
            tauri_build::InlinedPlugin::new()
                .commands(&[
                    "issue_resource_url",
                    "revoke_ref",
                    "revoke_resource_refs",
                    "probe_config",
                    "probe_write_results",
                    "probe_exit",
                    "probe_issue_url",
                ])
                .default_permission(tauri_build::DefaultPermissionRule::AllowAllCommands),
        ),
    )
    .expect("failed to run tauri-build");
}
