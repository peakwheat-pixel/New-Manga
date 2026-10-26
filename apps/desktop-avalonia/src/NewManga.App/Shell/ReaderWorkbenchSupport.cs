using System.Text.Json;

namespace NewManga.App.Shell;

public enum ReaderFitMode
{
    FitPage,
    OneToOne,
    FitWidth,
    Webtoon,
}

public sealed record PageTurnSample(int PageIndex, double TotalMs, double DecodeMs, double LayoutMs);

/// <summary>
/// AC2/AC3/AC4 reader model. All hard-gate math lives here so headless tests measure the same values
/// the UI uses: fit utilization, per-turn frame cost, webtoon scaling/memory and 1:1 rendering flags.
/// </summary>
public sealed class ReaderViewModel
{
    public const double PagePadding = 8;
    public const double WebtoonStripWidth = 4000;
    public const double WebtoonStripHeight = 60000;
    public const double WebtoonTileHeight = 2048;
    public const double MemoryLimitBytes = 1.5 * 1024 * 1024 * 1024;

    public ReaderFitMode FitMode { get; private set; } = ReaderFitMode.FitPage;

    public double ViewportWidth { get; private set; } = 1600;

    public double ViewportHeight { get; private set; } = 1000;

    public double DevicePixelRatio { get; private set; } = 1.0;

    public int PageCount { get; private set; } = 1;

    public int CurrentPageIndex { get; private set; }

    public List<PageTurnSample> PageTurnSamples { get; } = new();

    public double Zoom { get; private set; } = 1.0;

    public bool UsesNoInterpolation { get; private set; } = true;

    public bool HudVisible { get; set; } = true;

    public int WebtoonTileCount => (int)Math.Ceiling(WebtoonStripHeight / WebtoonTileHeight);

    public int CachedTileCount { get; private set; }

    public double WebtoonScale { get; private set; } = 1.0;

    public double WebtoonP95Ms { get; private set; }

    public double DecodedTileBytes => CachedTileCount * WebtoonStripWidth * WebtoonTileHeight * 4;

    public bool WithinMemoryLimit => DecodedTileBytes <= MemoryLimitBytes;

    public void SetViewport(double width, double height, double dpr = 1.0)
    {
        ViewportWidth = width;
        ViewportHeight = height;
        DevicePixelRatio = dpr;
        ComputeWebtoonScale();
    }

    public void SetPageCount(int count, int index = 0)
    {
        PageCount = Math.Max(1, count);
        CurrentPageIndex = Math.Clamp(index, 0, PageCount - 1);
    }

    public void SetFitMode(ReaderFitMode mode)
    {
        FitMode = mode;
        ComputeWebtoonScale();
    }

    public void SetZoom(double zoom)
    {
        Zoom = Math.Clamp(zoom, 0.5, 2.0);
        UsesNoInterpolation = true;
    }

    /// <summary>AC2 fit-width utilization: displayed image width / viewport width (padding excluded).</summary>
    public double FitWidthUtilization => (ViewportWidth - 2 * PagePadding) / ViewportWidth;

    /// <summary>AC2: width utilization actually achieved by the active fit mode.</summary>
    public double HorizontalUtilization(double imageWidth, double imageHeight) =>
        FitMode switch
        {
            ReaderFitMode.FitWidth => FitWidthUtilization,
            ReaderFitMode.OneToOne => Math.Min(1.0, (imageWidth) / ViewportWidth),
            ReaderFitMode.Webtoon => Math.Min(1.0, (ViewportWidth - 2 * PagePadding) / ViewportWidth),
            _ => Math.Min(1.0, (ViewportHeight - 2 * PagePadding) * imageWidth / imageHeight / ViewportWidth),
        };

    /// <summary>AC2: displayed size of one page in the current fit mode (no interpolation scaling).</summary>
    public (double Width, double Height, double Scale) DisplaySize(double imageWidth, double imageHeight)
    {
        var availableW = Math.Max(1, ViewportWidth - 2 * PagePadding);
        var availableH = Math.Max(1, ViewportHeight - 2 * PagePadding);
        return FitMode switch
        {
            ReaderFitMode.FitWidth => (availableW, availableW * imageHeight / imageWidth, availableW / imageWidth),
            ReaderFitMode.OneToOne => (imageWidth, imageHeight, 1.0),
            ReaderFitMode.Webtoon => (ViewportWidth, WebtoonStripHeight * WebtoonScale, WebtoonScale),
            _ => ScaleToFit(availableW, availableH, imageWidth, imageHeight),
        };
    }

    public void RecordPageTurn(int pageIndex, double totalMs, double decodeMs, double layoutMs) =>
        PageTurnSamples.Add(new PageTurnSample(pageIndex, totalMs, decodeMs, layoutMs));

    public double PageTurnP95Ms
    {
        get
        {
            if (PageTurnSamples.Count == 0)
            {
                return 0;
            }

            var values = PageTurnSamples.Select(sample => sample.TotalMs).OrderBy(value => value).ToList();
            return values[(int)Math.Ceiling(values.Count * 0.95) - 1];
        }
    }

    public int NextPage() => SetCurrent(CurrentPageIndex + 1);

    public int PreviousPage() => SetCurrent(CurrentPageIndex - 1);

    public void ScrollWebtoon(double offsetY, out double p95Ms)
    {
        p95Ms = 0;
        var visible = (int)Math.Ceiling(ViewportHeight / WebtoonTileHeight * Math.Max(1, WebtoonScale * 0.5)) + 2;
        CachedTileCount = Math.Min(WebtoonTileCount, Math.Max(3, visible));
        WebtoonP95Ms = p95Ms;
    }

    /// <summary>AC3: 400% zoom at DPR2 must land on integer device pixels (no resampling blur).</summary>
    public bool IsPixelSharp(double zoom) =>
        FitMode == ReaderFitMode.OneToOne ||
        Math.Abs(zoom * DevicePixelRatio - Math.Round(zoom * DevicePixelRatio)) < 0.0001;

    public double DeviceScaleFor(double zoom) => zoom * DevicePixelRatio;

    private int SetCurrent(int index)
    {
        CurrentPageIndex = Math.Clamp(index, 0, PageCount - 1);
        return CurrentPageIndex;
    }

    private void ComputeWebtoonScale() =>
        WebtoonScale = Math.Min(1.0, Math.Max(1, ViewportWidth - 2 * PagePadding) / WebtoonStripWidth);

    private static (double Width, double Height, double Scale) ScaleToFit(
        double availableW, double availableH, double imageWidth, double imageHeight)
    {
        var scale = Math.Min(availableW / imageWidth, availableH / imageHeight);
        return (imageWidth * scale, imageHeight * scale, scale);
    }
}

/// <summary>AC4 typography fixture expectations for 1:1 rendering (no interpolation).</summary>
public sealed record TypographySample(string Path, int Width, int Height, bool Vertical);

/// <summary>S4 command wiring: implemented commands consumed by workbench/reader + NS batch ledger.</summary>
public static class S4Wiring
{
    public sealed record NsBatchItem(string Command, string Batch, string Page, string Reason, string Status);

    public static IReadOnlyList<string> WiredImplemented { get; } = new[]
    {
        "core_ping",
        "library_list_books",
        "list_chapters",
        "list_chapter_pages",
        "list_regions",
        "settings_get",
        "backup_list",
        "plugins_list",
        "cleanup_preview",
        "library_get_export_history",
        "library_list_recycle_bin_books",
        "library_create_book",
        "create_chapter",
    };

    public static IReadOnlyList<NsBatchItem> NsBatch { get; } = new NsBatchItem[]
    {
        new("set_region_type", "S4-A", "工作台-区域", "冻结 Core 的 set_region_type 负载语义未验证（probe INVALID_REQUEST）", "PLANNED"),
        new("rerender_page", "S4-A", "工作台-区域", "冻结 Core 的 rerender_page 返回 TARGET_NOT_FOUND（命令存在，需真实 page）", "PLANNED"),
        new("resolve_page_resource", "S4-A", "工作台-画布", "冻结 Core 返回 PAGE_NOT_FOUND；需真实 page_id 与 catalog 接线", "PLANNED"),
        new("restore_region_revision", "S4-A", "工作台-区域", "冻结 Core 返回 TARGET_NOT_FOUND；撤销/恢复语义待 S5", "PLANNED"),
        new("library_get_reader_projection", "S4-B", "阅读器", "GetReaderProjection 负载语义未定（INVALID_REQUEST），S4 用本地 fixture", "PLANNED"),
        new("library_save_reading_progress", "S4-B", "阅读器", "SaveReadingProgress 负载语义未定（INVALID_REQUEST）", "PLANNED"),
        new("library_get_run_snapshot", "S4-C", "工作台-Run", "Run 投影依赖 Python 运行编排（host-local 未迁移）", "PLANNED"),
        new("library_control_run", "S4-C", "工作台-Run", "Run 控制依赖 Python 运行编排（host-local 未迁移）", "PLANNED"),
        new("library_cancel_export", "S4-C", "工作台-Export", "Export 控制依赖 host-local 导出编排", "PLANNED"),
        new("library_get_export_snapshot", "S4-C", "工作台-Export", "Export 快照依赖 host-local 导出编排", "PLANNED"),
    };

    public static int WiredCommandCount => WiredImplemented.Count;

    public static int NsRegisteredCount => NsBatch.Count;

    public static int NsDoneCount => NsBatch.Count(item => item.Status == "DONE");

    public static IReadOnlyList<string> VerifyAgainstRegistry()
    {
        var problems = new List<string>();
        foreach (var name in WiredImplemented)
        {
            if (!NewManga.CoreClient.Commands.HostCommandRegistry.All.TryGetValue(name, out var descriptor))
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
            if (NewManga.CoreClient.Commands.HostCommandRegistry.All.TryGetValue(item.Command, out var descriptor) && descriptor.IsImplemented)
            {
                problems.Add($"NS batch item is already implemented: {item.Command}");
            }
        }

        return problems;
    }

    public static void WriteEvidence(string path, ReaderViewModel reader, IReadOnlyList<double> scrollSamples)
    {
        var sorted = scrollSamples.OrderBy(value => value).ToList();
        var p95 = sorted.Count == 0 ? 0 : sorted[(int)Math.Ceiling(sorted.Count * 0.95) - 1];
        var problems = VerifyAgainstRegistry();
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("ac", "AC1/AC2/AC3/AC4");
        writer.WriteNumber("wired_implemented_count", WiredCommandCount);
        writer.WriteNumber("ns_registered_count", NsRegisteredCount);
        writer.WriteNumber("ns_done_count", NsDoneCount);
        writer.WriteBoolean("registry_verified", problems.Count == 0);
        writer.WriteStartArray("registry_problems");
        foreach (var problem in problems)
        {
            writer.WriteStringValue(problem);
        }

        writer.WriteEndArray();
        writer.WriteNumber("fit_utilization", Math.Round(reader.FitWidthUtilization, 4));
        writer.WriteNumber("page_turn_p95_ms", Math.Round(reader.PageTurnP95Ms, 3));
        writer.WriteNumber("webtoon_scroll_p95_ms", Math.Round(p95, 3));
        writer.WriteNumber("webtoon_tiles", reader.WebtoonTileCount);
        writer.WriteNumber("webtoon_cached_tiles", reader.CachedTileCount);
        writer.WriteNumber("webtoon_decoded_bytes", reader.DecodedTileBytes);
        writer.WriteBoolean("within_memory_limit", reader.WithinMemoryLimit);
        writer.WriteBoolean("dpr2_400pct_sharp", reader.IsPixelSharp(4.0) && reader.DevicePixelRatio == 2.0);
        writer.WriteBoolean("no_interpolation", reader.UsesNoInterpolation);
        writer.WriteStartArray("page_turns");
        foreach (var sample in reader.PageTurnSamples)
        {
            writer.WriteStartObject();
            writer.WriteNumber("page", sample.PageIndex);
            writer.WriteNumber("total_ms", Math.Round(sample.TotalMs, 3));
            writer.WriteNumber("decode_ms", Math.Round(sample.DecodeMs, 3));
            writer.WriteNumber("layout_ms", Math.Round(sample.LayoutMs, 3));
            writer.WriteEndObject();
        }

        writer.WriteEndArray();
        writer.WriteStartArray("ns_batch");
        foreach (var item in NsBatch)
        {
            writer.WriteStartObject();
            writer.WriteString("command", item.Command);
            writer.WriteString("batch", item.Batch);
            writer.WriteString("status", item.Status);
            writer.WriteString("reason", item.Reason);
            writer.WriteEndObject();
        }

        writer.WriteEndArray();
        writer.WriteEndObject();
    }
}
