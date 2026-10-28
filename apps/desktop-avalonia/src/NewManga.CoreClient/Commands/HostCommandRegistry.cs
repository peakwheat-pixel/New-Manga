namespace NewManga.CoreClient.Commands;

/// <summary>
/// AC2 mapping table: every one of the 66 runtime production commands is registered exactly once,
/// organised into the six domain services. Sixty-six commands are migrated: the S2/A1/A2 sets,
/// thirteen NS-WIRE-B1 bindings, nine NS-WIRE-B2 bindings, five S4-CMD-BATCH-1 bindings, the
/// four Host-local grant/shell faces and the CREDENTIAL-PORT-1 credential pair (OS vault +
/// Core BindProfileCredential/ClearProfileCredential). There is no NOT_SUPPORTED command left.
///
/// Implemented set (probed against the frozen sidecars, evidence under
/// verification/HOST-COMMAND-MIGRATION-1/parity/, verification/NS-WIRE-A1/,
/// verification/NS-WIRE-B1/, verification/NS-WIRE-B2/, verification/RUN-EXPORT-E2E-1/ and
/// verification/S4-CMD-BATCH-1/):
///   core.ping, ListBooks, ListRecycleBinBooks, CreateBook, CreateChapter, list_chapters,
///   list_chapter_pages, list_regions, settings.get, backup.list, plugins.list,
///   cleanup.preview, GetExportHistory (core_service protocol 2.3), the RUN-EXPORT-E2E-1 run/export
///   set, the NS-WIRE-A1 settings/plugins/backup/cleanup batch, the NS-WIRE-B1 P15 settings /
///   provider binding / network profile / backup / cleanup / plugin / permanent-delete batch,
///   the NS-WIRE-B2 backup-restore / provider-profile / provider-binding / network-test /
///   network-resolve / batch-delete / region-revision batch,
///   the S4-CMD-BATCH-1 region write + reader progress batch, and issue/revoke/revoke_resource
/// </summary>
public static class HostCommandRegistry
{
    private static readonly string[] SettingsNames =
    {
        "settings_get",
        "settings_update_section",
        "cleanup_preview",
        "cleanup_run",
        "cleanup_retry_pending",
        "backup_create",
        "backup_list",
        "backup_restore",
        "backup_delete",
        "plugins_list",
        "plugins_set_enabled",
        "plugins_set_plugin_enabled",
        "plugins_audit_list",
        "plugins_open_directory",
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
    };

    private static readonly string[] LibraryNames =
    {
        "library_list_books",
        "library_list_recycle_bin_books",
        "library_create_book",
        "create_chapter",
        "library_import_file",
        "library_import_folder",
        "library_delete_book_permanently",
        "library_delete_books_permanently",
    };

    private static readonly string[] RegionNames =
    {
        "set_region_type",
        "list_regions",
        "list_region_revisions",
        "restore_region_revision",
        "rerender_page",
        "resolve_page_resource",
    };

    private static readonly string[] ReaderNames =
    {
        "list_chapters",
        "list_chapter_pages",
        "library_get_reader_projection",
        "library_save_reading_progress",
    };

    private static readonly string[] ResourceNames =
    {
        "issue_resource_url",
        "revoke_ref",
        "revoke_resource_refs",
    };

    private static readonly string[] WorkbenchNames =
    {
        "core_ping",
        "library_start_run",
        "library_control_run",
        "library_resume_blocked_run",
        "library_get_run_snapshot",
        "library_get_task_projection",
        "library_retry_failed_targets",
        "library_reveal_export_folder",
        "library_get_export_history",
        "library_start_export",
        "library_cancel_export",
        "library_get_export_snapshot",
    };

    private sealed record CoreBinding(string CoreCommand, int Minor);

    private static readonly Dictionary<string, CoreBinding> CoreBindings = new(StringComparer.Ordinal)
    {
        ["core_ping"] = new("core.ping", 3),
        ["library_list_books"] = new("ListBooks", 3),
        ["library_list_recycle_bin_books"] = new("ListRecycleBinBooks", 3),
        ["library_create_book"] = new("CreateBook", 8),
        ["create_chapter"] = new("CreateChapter", 8),
        ["list_chapters"] = new("list_chapters", 3),
        ["list_chapter_pages"] = new("list_chapter_pages", 3),
        ["list_regions"] = new("list_regions", 3),
        ["settings_get"] = new("settings.get", 3),
        ["backup_list"] = new("backup.list", 3),
        ["plugins_list"] = new("plugins.list", 3),
        ["cleanup_preview"] = new("cleanup.preview", 3),
        ["library_get_export_history"] = new("GetExportHistory", 3),
        // NS-WIRE-A1 batch A1: S3-A/B/C settings / plugins / backup / cleanup faces.
        // Payloads/minors are the ones proven against the frozen core_service by
        // verification/NS-WIRE-A1/probe-results.json (P15 settings face needs minor 7).
        ["settings_update_section"] = new("settings.update_section", 3),
        ["settings_provider_profiles_list"] = new("settings_provider_profiles_list", 7),
        ["settings_network_profiles_list"] = new("settings_network_profiles_list", 7),
        ["settings_resolve_overrides"] = new("settings_resolve_overrides", 7),
        ["backup_create"] = new("backup.create", 3),
        ["plugins_set_enabled"] = new("plugins.set_enabled", 3),
        ["cleanup_run"] = new("cleanup.run", 3),
        ["library_get_reader_projection"] = new("GetReaderProjection", 3),
        // RUN-EXPORT-E2E-1: the Run/Export control + projection faces are Core-backed
        // commands of the frozen 2.3 protocol (minor 3). Payload validation mirrors the
        // legacy Tauri signatures; typed Core errors (PROVIDER_NOT_CONFIGURED /
        // INVALID_RUN_TRANSITION / EXPORT_NOT_FOUND / EXPORT_INPUT_UNAVAILABLE) pass through.
        ["library_start_run"] = new("StartRun", 3),
        ["library_control_run"] = new("ControlRun", 3),
        ["library_resume_blocked_run"] = new("ResumeBlockedRun", 3),
        ["library_get_run_snapshot"] = new("GetRunSnapshot", 3),
        ["library_get_task_projection"] = new("GetTaskProjection", 3),
        ["library_retry_failed_targets"] = new("RetryFailedTargets", 3),
        ["library_start_export"] = new("StartExport", 3),
        ["library_cancel_export"] = new("CancelExport", 3),
        ["library_get_export_snapshot"] = new("GetExportSnapshot", 3),
        // NS-WIRE-B1 batch B1: the 13 remaining high-confidence NS commands whose Core routes were
        // proven by verification/NS-RECLASSIFY-1/reclassification.json. Payloads/minors come from the
        // exact probe that succeeded: the P15 settings face needs minor 7 and the DELETE face needs
        // minor 10; the backup/cleanup/plugin/run faces stay on minor 3.
        ["backup_delete"] = new("backup.delete", 3),
        ["cleanup_retry_pending"] = new("cleanup.retry_pending", 3),
        ["plugins_audit_list"] = new("plugins.audit_list", 3),
        ["plugins_set_plugin_enabled"] = new("plugins.set_plugin_enabled", 3),
        ["library_delete_book_permanently"] = new("PermanentlyDeleteBook", 10),
        ["settings_network_profile_default_clear"] = new("settings_network_profile_default_clear", 7),
        ["settings_network_profile_default_set"] = new("settings_network_profile_default_set", 7),
        ["settings_network_profiles_create"] = new("settings_network_profiles_create", 7),
        ["settings_network_profiles_delete"] = new("settings_network_profiles_delete", 7),
        ["settings_network_profiles_update"] = new("settings_network_profiles_update", 7),
        ["settings_provider_bindings_clear"] = new("settings_provider_bindings_clear", 7),
        ["settings_provider_bindings_resolve"] = new("settings_provider_bindings_resolve", 7),
        ["settings_provider_run_snapshot_get"] = new("settings_provider_run_snapshot_get", 7),
        // S4-CMD-BATCH-1 batch: the region write face (set/restore/rerender/resolve) and the reader
        // progress write face. The Core envelopes stay at protocol minor 3 exactly like the
        // list_regions / list_chapters read faces; payload shapes are proven against the frozen
        // core_service by verification/S4-CMD-BATCH-1/commands/s4-integration-results.json.
        ["set_region_type"] = new("set_region_type", 3),
        ["restore_region_revision"] = new("restore_region_revision", 3),
        ["rerender_page"] = new("rerender_page", 3),
        ["resolve_page_resource"] = new("resolve_page_resource", 3),
        ["library_save_reading_progress"] = new("SaveReadingProgress", 3),
        // NS-WIRE-B2 batch: the last nine commands whose Core routes were proven by
        // verification/NS-RECLASSIFY-1/reclassification.json (route + handler executed; the old S2
        // probes only failed because of wrong payloads / fake ids). Payloads below are the exact
        // ones the frozen core_service accepts (verified by verification/NS-WIRE-B2/probe-results.json
        // and the NS-WIRE-B2 integration tests): the P15 settings/credential faces need minor 7,
        // PermanentlyDeleteBooks needs minor 10, backup.restore and list_region_revisions stay on
        // minor 3 exactly like their sibling read faces.
        ["backup_restore"] = new("backup.restore", 3),
        ["settings_provider_profiles_create"] = new("settings_provider_profiles_create", 7),
        ["settings_provider_profiles_update"] = new("settings_provider_profiles_update", 7),
        ["settings_provider_profiles_delete"] = new("settings_provider_profiles_delete", 7),
        ["settings_provider_bindings_set"] = new("settings_provider_bindings_set", 7),
        ["settings_network_profiles_test"] = new("settings_network_profiles_test", 7),
        ["settings_network_profile_resolve"] = new("settings_network_profile_resolve", 7),
        ["library_delete_books_permanently"] = new("PermanentlyDeleteBooks", 10),
        ["list_region_revisions"] = new("list_region_revisions", 3),
    };

    private static readonly HashSet<string> BridgeBindings = new(StringComparer.Ordinal)
    {
        "issue_resource_url",
        "revoke_ref",
        "revoke_resource_refs",
    };

    /// <summary>
    /// GRANT-ISSUER-1 / CREDENTIAL-PORT-1: Host-local commands. The import pair mints host_issuer
    /// grants and drives the Core through the host-control envelope plus ImportPages; the two shell
    /// actions open a whitelisted OS directory; the credential pair writes/reads the OS vault and
    /// binds/clears only the opaque <c>credential_ref</c> in the Core. None is a plain passthrough.
    /// </summary>
    private static readonly HashSet<string> HostLocalBindings = new(StringComparer.Ordinal)
    {
        "library_import_file",
        "library_import_folder",
        "library_reveal_export_folder",
        "plugins_open_directory",
        "credential_put",
        "credential_clear",
    };

    private static readonly IReadOnlyDictionary<string, HostCommandDescriptor> Commands =
        BuildCommands();

    private static readonly IReadOnlyDictionary<HostCommandDomain, HostCommandDescriptor[]> ByDomain =
        Enum.GetValues<HostCommandDomain>().ToDictionary(
            domain => domain,
            domain => Commands.Values.Where(command => command.Domain == domain)
                .OrderBy(command => command.Name, StringComparer.Ordinal)
                .ToArray());

    public static IReadOnlyDictionary<string, HostCommandDescriptor> All => Commands;

    public static IReadOnlyList<HostCommandDescriptor> ForDomain(HostCommandDomain domain) => ByDomain[domain];

    public static HostCommandDescriptor Get(string name) =>
        Commands.TryGetValue(name, out var descriptor)
            ? descriptor
            : throw new HostCommandUnknownException(name);

    private static IReadOnlyDictionary<string, HostCommandDescriptor> BuildCommands()
    {
        var descriptors = new List<HostCommandDescriptor>(66);
        AddDomain(descriptors, HostCommandDomain.Settings, SettingsNames);
        AddDomain(descriptors, HostCommandDomain.Library, LibraryNames);
        AddDomain(descriptors, HostCommandDomain.Region, RegionNames);
        AddDomain(descriptors, HostCommandDomain.Reader, ReaderNames);
        AddDomain(descriptors, HostCommandDomain.Resource, ResourceNames);
        AddDomain(descriptors, HostCommandDomain.Workbench, WorkbenchNames);

        var byName = descriptors.ToDictionary(descriptor => descriptor.Name, StringComparer.Ordinal);
        if (byName.Count != descriptors.Count)
        {
            throw new InvalidOperationException("duplicate production command in the S2 registry");
        }

        return byName;
    }

    private static void AddDomain(List<HostCommandDescriptor> target, HostCommandDomain domain, string[] names)
    {
        foreach (var name in names)
        {
            if (CoreBindings.TryGetValue(name, out var binding))
            {
                target.Add(new HostCommandDescriptor(
                    name,
                    domain,
                    HostCommandChannel.CoreService,
                    HostCommandStatus.Implemented,
                    null,
                    binding.CoreCommand,
                    binding.Minor));
                continue;
            }

            if (BridgeBindings.Contains(name))
            {
                target.Add(new HostCommandDescriptor(
                    name,
                    domain,
                    HostCommandChannel.HostBridge,
                    HostCommandStatus.Implemented,
                    null,
                    null,
                    0));
                continue;
            }

            if (HostLocalBindings.Contains(name))
            {
                target.Add(new HostCommandDescriptor(
                    name,
                    domain,
                    HostCommandChannel.HostLocal,
                    HostCommandStatus.Implemented,
                    null,
                    null,
                    0));
                continue;
            }

            // Defensive only: every production command is bound after CREDENTIAL-PORT-1, so this
            // branch is unreachable (a parity test asserts 66/0). It stays explicit rather than
            // silently dropping a command if a future name is added without a binding.
            const string reason =
                "该命令在旧 Tauri/Rust host 本地实现，S2/Credential Slice 未覆盖；新增命令必须同时登记绑定，" +
                "不得依赖本兜底分支。";

            target.Add(new HostCommandDescriptor(
                name,
                domain,
                HostCommandChannel.None,
                HostCommandStatus.NotSupported,
                reason,
                null,
                0));
        }
    }
}
