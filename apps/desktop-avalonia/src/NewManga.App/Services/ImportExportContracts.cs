using System.Globalization;
using System.Text.Json;

namespace NewManga.App.Services;

/// <summary>IMPORT-EXPORT-UI-1: what the user asked the picker for.</summary>
public enum ImportSourceKind
{
    Files,
    Folder,
}

/// <summary>The Core export job states surfaced by <c>GetExportSnapshot</c> (wire strings).</summary>
public enum ExportJobState
{
    Unknown,
    Pending,
    Running,
    Publishing,
    Completed,
    Skipped,
    Cancelled,
    Failed,
}

/// <summary>One import attempt as the UI shows it. Typed: no exception ever reaches the page.</summary>
public sealed record ImportOutcome(
    bool Ok,
    string Message,
    string? ErrorCode = null,
    int ImportedFiles = 0,
    int SkippedFiles = 0)
{
    public bool IsNotReady => ErrorCode == "HOST_NOT_READY";

    public static ImportOutcome NotReady() =>
        new(false, "Host 尚未就绪：导入不可用", "HOST_NOT_READY");

    public static ImportOutcome Failed(string code, string message) => new(false, message, code);

    public static ImportOutcome Success(int importedFiles, int skippedFiles) => new(
        true,
        importedFiles + skippedFiles == 0
            ? "没有新文件可导入"
            : $"已导入 {importedFiles} 个文件" + (skippedFiles > 0 ? $"，跳过 {skippedFiles} 个重复" : string.Empty),
        null,
        importedFiles,
        skippedFiles);
}

/// <summary>StartExport projection (job accepted by the Core).</summary>
public sealed record ExportStartInfo(
    string ExportId,
    string Status,
    int PageCount)
{
    public ExportJobState State => ExportJson.ParseState(Status);

    public static ExportStartInfo FromJson(JsonElement value) => new(
        ExportJson.ReadString(value, "export_id") ?? string.Empty,
        ExportJson.ReadString(value, "status") ?? "pending",
        ExportJson.ReadInt(value, "ordered_page_ids") is { } count
            ? count
            : ExportJson.ReadArrayLength(value, "ordered_page_ids"));

    public static ExportStartInfo FromState(string exportId, string status, int pageCount) =>
        new(exportId, status, pageCount);
}

/// <summary>One GetExportSnapshot projection.</summary>
public sealed record ExportSnapshotInfo(
    string ExportId,
    ExportJobState State,
    int CompletedPages,
    int TotalPages,
    string? CurrentPageId = null,
    string? OutputPath = null,
    string? Sha256 = null,
    string? ErrorCode = null,
    string? Format = null)
{
    public bool IsTerminal => State is ExportJobState.Completed or ExportJobState.Cancelled
        or ExportJobState.Failed or ExportJobState.Skipped;

    public bool IsActive => State is ExportJobState.Pending or ExportJobState.Running
        or ExportJobState.Publishing;

    public double ProgressPercent => TotalPages <= 0
        ? 0
        : Math.Clamp(CompletedPages * 100.0 / TotalPages, 0, 100);

    public static ExportSnapshotInfo FromJson(JsonElement value)
    {
        var state = ExportJson.ParseState(ExportJson.ReadString(value, "status"));
        var completed = ExportJson.ReadInt(value, "completed_pages") ?? 0;
        var total = ExportJson.ReadInt(value, "total_pages") ?? 0;
        string? outputPath = null;
        string? sha256 = null;
        string? format = null;
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty("output", out var output) &&
            output.ValueKind == JsonValueKind.Object)
        {
            outputPath = ExportJson.ReadString(output, "output_path");
            sha256 = ExportJson.ReadString(output, "sha256");
            format = ExportJson.ReadString(output, "format");
        }

        return new ExportSnapshotInfo(
            ExportJson.ReadString(value, "export_id") ?? string.Empty,
            state,
            completed,
            total,
            ExportJson.ReadString(value, "current_page_id"),
            outputPath,
            sha256,
            ExportJson.ReadString(value, "error_code"),
            format);
    }

    public static ExportSnapshotInfo FromState(
        string exportId,
        ExportJobState state,
        int completedPages = 0,
        int totalPages = 0,
        string? outputPath = null,
        string? sha256 = null,
        string? errorCode = null,
        string? format = "zip") =>
        new(exportId, state, completedPages, totalPages, null, outputPath, sha256, errorCode, format);
}

/// <summary>One row of <c>GetExportHistory</c> (durable export record).</summary>
public sealed record ExportHistoryEntry(
    string ExportId,
    string Format,
    string Status,
    string? OutputPath,
    string? Sha256,
    int PageCount,
    string? CompletedAt)
{
    public ExportJobState State => ExportJson.ParseState(Status);

    public static ExportHistoryEntry FromJson(JsonElement value) => new(
        ExportJson.ReadString(value, "export_id") ?? string.Empty,
        ExportJson.ReadString(value, "format") ?? "?",
        ExportJson.ReadString(value, "status") ?? "?",
        ExportJson.ReadString(value, "output_path"),
        ExportJson.ReadString(value, "sha256"),
        ExportJson.ReadArrayLength(value, "ordered_page_ids"),
        ExportJson.ReadString(value, "completed_at"));
}

/// <summary>
/// IMPORT-EXPORT-UI-1: exact wire payloads for the import/export commands the pages consume.
/// Kept separate from the controller so headless tests pin the key sets the dispatcher expects.
/// Built with <see cref="Utf8JsonWriter"/> (reflection-based JsonSerializer is disabled in the App),
/// matching the existing SettingsProfilePayload convention.
/// </summary>
public static class ImportExportPayloads
{
    public static JsonElement LibraryImportFile(
        string chapterId,
        IReadOnlyList<string> paths,
        string duplicatePolicy) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("chapter_id", chapterId);
        writer.WritePropertyName("paths");
        writer.WriteStartArray();
        foreach (var path in paths)
        {
            writer.WriteStringValue(path);
        }

        writer.WriteEndArray();
        writer.WriteString("duplicate_policy", duplicatePolicy);
        writer.WriteEndObject();
    });

    public static JsonElement LibraryImportFolder(
        string chapterId,
        string path,
        string duplicatePolicy) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("chapter_id", chapterId);
        writer.WriteString("path", path);
        writer.WriteString("duplicate_policy", duplicatePolicy);
        writer.WriteEndObject();
    });

    /// <summary>
    /// The six-field StartExport request the Host validates; the Host appends the minted
    /// <c>target_ref</c> after validating/confining the target (GRANT-ISSUER-1).
    /// </summary>
    public static JsonElement StartExportRequest(
        string bookId,
        IReadOnlyList<string> chapterIds,
        IReadOnlyList<string> orderedPageIds,
        string format = "zip",
        string stalePolicy = "abort") => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("book_id", bookId);
        writer.WritePropertyName("chapter_ids");
        writer.WriteStartArray();
        foreach (var chapterId in chapterIds)
        {
            writer.WriteStringValue(chapterId);
        }

        writer.WriteEndArray();
        writer.WritePropertyName("ordered_page_ids");
        writer.WriteStartArray();
        foreach (var pageId in orderedPageIds)
        {
            writer.WriteStringValue(pageId);
        }

        writer.WriteEndArray();
        writer.WriteString("format", format);
        writer.WritePropertyName("format_options");
        writer.WriteStartObject();
        if (string.Equals(format, "zip", StringComparison.Ordinal))
        {
            writer.WriteString("compression", "standard");
        }

        writer.WriteEndObject();
        writer.WriteString("stale_policy", stalePolicy);
        writer.WriteEndObject();
    });

    public static JsonElement ExportId(string exportId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("export_id", exportId);
        writer.WriteEndObject();
    });

    /// <summary>GetReaderProjection in the translated mode (the only exportable input face).</summary>
    public static JsonElement ReaderProjectionTranslated(string chapterId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("chapter_id", chapterId);
        writer.WriteString("mode", "translated");
        writer.WriteString("start_position", "beginning");
        writer.WriteEndObject();
    });

    private static JsonElement Build(Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            write(writer);
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }
}

/// <summary>UI-facing text for the export job states; lists stay honest about unknown states.</summary>
public static class ImportExportFormatting
{
    public static string ImportStatus(ImportOutcome outcome) =>
        outcome.Ok ? outcome.Message
            : outcome.ErrorCode is null ? outcome.Message
            : $"{outcome.Message}（{outcome.ErrorCode}）";

    public static string ExportStateText(ExportJobState state) => state switch
    {
        ExportJobState.Pending => "等待导出…",
        ExportJobState.Running => "导出中…",
        ExportJobState.Publishing => "写入文件…",
        ExportJobState.Completed => "导出完成",
        ExportJobState.Skipped => "已跳过（目标已存在）",
        ExportJobState.Cancelled => "已取消",
        ExportJobState.Failed => "导出失败",
        _ => "未知状态",
    };

    public static string SnapshotStatus(ExportSnapshotInfo snapshot)
    {
        if (snapshot.State == ExportJobState.Completed)
        {
            var sha = string.IsNullOrEmpty(snapshot.Sha256) ? string.Empty : $" · sha256 {snapshot.Sha256}";
            return $"导出完成：{snapshot.OutputPath}{sha}";
        }

        if (snapshot.State == ExportJobState.Failed)
        {
            return $"导出失败{FormatCode(snapshot.ErrorCode)}";
        }

        if (snapshot.State == ExportJobState.Cancelled)
        {
            return "已取消（未发布文件）";
        }

        var progress = snapshot.TotalPages <= 0
            ? string.Empty
            : $" {snapshot.CompletedPages}/{snapshot.TotalPages} 页";
        return ExportStateText(snapshot.State) + progress;
    }

    public static string HistoryLine(ExportHistoryEntry entry)
    {
        var size = string.IsNullOrEmpty(entry.Sha256) ? string.Empty : $" · {entry.Sha256[..Math.Min(12, entry.Sha256.Length)]}…";
        return $"{entry.ExportId} · {entry.Format} · {ExportStateText(entry.State)}{size}";
    }

    /// <summary>Deterministic, filesystem-safe default file name for the ZIP export target.</summary>
    public static string DefaultExportFileName(string bookTitle, string chapterTitle)
    {
        var stem = Sanitize(bookTitle) + "-" + Sanitize(chapterTitle);
        var stamp = DateTimeOffset.UtcNow.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
        return $"{stem}-{stamp}.zip";
    }

    public static string Sanitize(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return "book";
        }

        var invalid = Path.GetInvalidFileNameChars();
        var chars = value.Trim().Select(ch => invalid.Contains(ch) ? '_' : ch).ToArray();
        var cleaned = new string(chars).Trim(' ', '.', '_');
        return string.IsNullOrEmpty(cleaned) ? "book" : cleaned[..Math.Min(60, cleaned.Length)];
    }

    private static string FormatCode(string? code) => string.IsNullOrEmpty(code) ? string.Empty : $"（{code}）";
}

/// <summary>Small, total JSON readers shared by the controller parsers (never throw into the UI).</summary>
internal static class ExportJson
{
    public static string? ReadString(JsonElement value, string name)
    {
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty(name, out var property) &&
            property.ValueKind == JsonValueKind.String)
        {
            return property.GetString();
        }

        return null;
    }

    public static int? ReadInt(JsonElement value, string name)
    {
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty(name, out var property) &&
            property.ValueKind == JsonValueKind.Number &&
            property.TryGetInt32(out var parsed))
        {
            return parsed;
        }

        return null;
    }

    public static int ReadArrayLength(JsonElement value, string name)
    {
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty(name, out var property) &&
            property.ValueKind == JsonValueKind.Array)
        {
            return property.GetArrayLength();
        }

        return 0;
    }

    public static ExportJobState ParseState(string? status) => status switch
    {
        "pending" => ExportJobState.Pending,
        "running" => ExportJobState.Running,
        "publishing" => ExportJobState.Publishing,
        "completed" => ExportJobState.Completed,
        "skipped" => ExportJobState.Skipped,
        "cancelled" => ExportJobState.Cancelled,
        "failed" => ExportJobState.Failed,
        _ => ExportJobState.Unknown,
    };
}
