namespace NewManga.CoreClient.Commands;

/// <summary>
/// AC2 mapping table: every one of the 66 runtime production commands is registered exactly once,
/// organised into the six domain services. Twelve commands are migrated to the existing sidecars;
/// the rest are explicit NOT_SUPPORTED with a per-command reason (never silently missing).
///
/// Implemented set (probed against the frozen sidecars, evidence under
/// verification/HOST-COMMAND-MIGRATION-1/parity/):
///   core.ping, ListBooks, ListRecycleBinBooks, CreateBook, CreateChapter, list_chapters,
///   list_chapter_pages, list_regions, settings.get, backup.list, plugins.list,
///   cleanup.preview, GetExportHistory (core_service protocol 2.3) and issue/revoke/revoke_resource
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
    };

    private static readonly HashSet<string> BridgeBindings = new(StringComparer.Ordinal)
    {
        "issue_resource_url",
        "revoke_ref",
        "revoke_resource_refs",
    };

    /// <summary>Commands whose legacy implementation is a Core round-trip still missing from the frozen Core.</summary>
    private static readonly Dictionary<string, string> CoreRoute = new(StringComparer.Ordinal)
    {
        ["library_get_reader_projection"] = "GetReaderProjection",
        ["library_save_reading_progress"] = "SaveReadingProgress",
        ["set_region_type"] = "set_region_type",
        ["list_region_revisions"] = "list_region_revisions",
        ["restore_region_revision"] = "restore_region_revision",
        ["rerender_page"] = "rerender_page",
        ["resolve_page_resource"] = "resolve_page_resource",
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

            var reason = CoreRoute.TryGetValue(name, out var route)
                ? $"旧壳经 Core 命令 `{route}` 实现；冻结 core_service.exe 在 S2 探测中未返回可用结果" +
                  "（见 verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json），" +
                  "故本 Slice 显式 NOT_SUPPORTED，待 Core 命令补齐后接入。"
                : "该命令的语义在旧 Tauri/Rust host 本地实现（设置持久化、凭证、插件、备份恢复、导入导出或运行编排）；" +
                  "S2 只迁移已探测通过的命令面，host-local 逻辑按 AD-002 在后续 Slice 移植，本 Slice 显式 NOT_SUPPORTED。";

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
