using System.Text.Json;
using NewManga.CoreClient.Commands;

namespace NewManga.App.Shell;

public enum WindowMaterialKind
{
    Mica,
    OpaqueFallback,
}

/// <summary>AC1: Win11 gets Mica; Win10 (and unknown) falls back to an opaque background.</summary>
public static class WindowMaterial
{
    public static (WindowMaterialKind Kind, string[] Hints) Choose(int major, int build) =>
        major >= 10 && build >= 22000
            ? (WindowMaterialKind.Mica, new[] { "Mica", "Blur", "None" })
            : (WindowMaterialKind.OpaqueFallback, new[] { "None" });

    public static (WindowMaterialKind Kind, string[] Hints) ForCurrentOs()
    {
        var version = Environment.OSVersion.Version;
        return Choose(version.Major, version.Build);
    }
}

/// <summary>
/// AC4 wiring ledger: which S2-migrated commands the S3 shell consumes, plus the explicit NS batch
/// that the shelf/settings pages still need (registered, not yet migrated).
/// </summary>
public static class ShellCommandCatalog
{
    public static IReadOnlyList<string> WiredImplemented { get; } = new[]
    {
        "core_ping",
        "library_list_books",
        "library_list_recycle_bin_books",
        "library_create_book",
        "create_chapter",
        "list_chapters",
        "list_chapter_pages",
        "list_regions",
        "settings_get",
        "backup_list",
        "plugins_list",
        "cleanup_preview",
        "library_get_export_history",
    };

    public sealed record NsBatchItem(string Command, string Batch, string Page, string Reason, string Status);

    public static IReadOnlyList<NsBatchItem> NsBatch { get; } = new NsBatchItem[]
    {
        new("settings_update_section", "S3-A", "设置-外观", "设置写回需要 host-local 设置持久化迁移", "PLANNED"),
        new("settings_provider_profiles_list", "S3-A", "设置-提供方", "provider profile 读面依赖 host-local 设置库", "PLANNED"),
        new("settings_network_profiles_list", "S3-A", "设置-网络", "网络 profile 读面依赖 host-local 设置库", "PLANNED"),
        new("settings_resolve_overrides", "S3-A", "设置-覆盖", "解析逻辑在 Rust host 本地", "PLANNED"),
        new("backup_create", "S3-B", "设置-数据", "备份写面依赖 host-local 备份包实现", "PLANNED"),
        new("plugins_set_enabled", "S3-B", "设置-插件", "插件运行时开关在 Rust host 本地", "PLANNED"),
        new("cleanup_run", "S3-B", "设置-数据", "清理执行面依赖 host-local 缓存编排", "PLANNED"),
        new("library_get_reader_projection", "S3-C", "阅读器", "冻结 Core 的 GetReaderProjection 负载语义待验证", "PLANNED"),
    };

    public static int WiredCommandCount => WiredImplemented.Count;

    public static int NsRegisteredCount => NsBatch.Count;

    public static int NsDoneCount => NsBatch.Count(item => item.Status == "DONE");

    /// <summary>Every wired command must exist in the S2 registry and actually be implemented.</summary>
    public static IReadOnlyList<string> VerifyAgainstRegistry()
    {
        var problems = new List<string>();
        foreach (var name in WiredImplemented)
        {
            if (!HostCommandRegistry.All.TryGetValue(name, out var descriptor))
            {
                problems.Add($"wired command missing from S2 registry: {name}");
            }
            else if (!descriptor.IsImplemented)
            {
                problems.Add($"wired command is NOT_SUPPORTED in S2: {name}");
            }
        }

        foreach (var item in NsBatch)
        {
            if (HostCommandRegistry.All.TryGetValue(item.Command, out var descriptor) && descriptor.IsImplemented)
            {
                problems.Add($"NS batch item is already implemented: {item.Command}");
            }
        }

        return problems;
    }

    public static void WriteEvidence(string path, string scope, int hotSwitchSamples, IReadOnlyList<double> switchMs, double p95)
    {
        var verified = VerifyAgainstRegistry();
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("ac", "AC4");
        writer.WriteString("scope", scope);
        writer.WriteNumber("wired_implemented_count", WiredCommandCount);
        writer.WriteNumber("ns_registered_count", NsRegisteredCount);
        writer.WriteNumber("ns_done_count", NsDoneCount);
        writer.WriteBoolean("registry_verified", verified.Count == 0);
        writer.WriteStartArray("registry_problems");
        foreach (var problem in verified)
        {
            writer.WriteStringValue(problem);
        }

        writer.WriteEndArray();
        writer.WriteStartArray("wired_implemented");
        foreach (var name in WiredImplemented)
        {
            writer.WriteStringValue(name);
        }

        writer.WriteEndArray();
        writer.WriteStartArray("ns_batch");
        foreach (var item in NsBatch)
        {
            writer.WriteStartObject();
            writer.WriteString("command", item.Command);
            writer.WriteString("batch", item.Batch);
            writer.WriteString("page", item.Page);
            writer.WriteString("status", item.Status);
            writer.WriteString("reason", item.Reason);
            writer.WriteEndObject();
        }

        writer.WriteEndArray();
        writer.WriteNumber("hot_switch_samples", hotSwitchSamples);
        if (switchMs.Count > 0)
        {
            writer.WriteNumber("hot_switch_min_ms", Math.Round(switchMs.Min(), 3));
            writer.WriteNumber("hot_switch_max_ms", Math.Round(switchMs.Max(), 3));
            writer.WriteNumber("hot_switch_p95_ms", Math.Round(p95, 3));
        }

        writer.WriteEndObject();
    }
}
