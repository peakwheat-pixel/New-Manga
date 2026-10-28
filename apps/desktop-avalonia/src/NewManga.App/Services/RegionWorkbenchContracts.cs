using NewManga.CoreClient;

namespace NewManga.App.Services;

/// <summary>
/// READER-WORKBENCH-1: typed outcome of one region write (retype / revision restore). Mirrors the
/// reader-progress discipline: the UI never sees a thrown exception, only a typed status.
/// </summary>
public enum RegionOperationStatus
{
    /// <summary>The Core committed the write; <see cref="RegionOperationResult.RevisionNo"/> is new.</summary>
    Success,

    /// <summary>No Core: host is starting / failed / already running.</summary>
    NotReady,

    /// <summary>Host is read-only until parity; nothing was sent to the Core.</summary>
    ReadOnly,

    /// <summary>Core or transport rejected the write; <see cref="RegionOperationResult.ErrorCode"/> is typed.</summary>
    Failed,
}

/// <summary>READER-WORKBENCH-1: result of one region write attempt (never thrown into the UI).</summary>
public sealed record RegionOperationResult(
    RegionOperationStatus Status,
    string? ErrorCode = null,
    int RevisionNo = 0,
    string? RegionType = null,
    string? SfxPolicy = null,
    string? Message = null)
{
    public bool IsSuccess => Status == RegionOperationStatus.Success;

    public static RegionOperationResult Success(RegionWriteSnapshot snapshot, string message) => new(
        RegionOperationStatus.Success,
        null,
        snapshot.RevisionNo,
        snapshot.RegionType,
        snapshot.SfxPolicy,
        message);

    public static RegionOperationResult NotReady() =>
        new(RegionOperationStatus.NotReady, "HOST_NOT_READY", Message: "Host 未就绪");

    public static RegionOperationResult ReadOnly() =>
        new(RegionOperationStatus.ReadOnly, "HOST_READ_ONLY", Message: "只读模式：Host 未达 parity，写操作已禁用");

    public static RegionOperationResult Failed(string code, string? message = null) =>
        new(RegionOperationStatus.Failed, code, Message: message);
}

/// <summary>READER-WORKBENCH-1: result of one manual page rerender attempt.</summary>
public sealed record PageRerenderOutcome(
    RegionOperationStatus Status,
    string? ErrorCode = null,
    string? ArtifactId = null,
    int RevisionNo = 0,
    int ReportCount = 0,
    bool PreviewPublished = false,
    string? Message = null)
{
    public bool IsSuccess => Status == RegionOperationStatus.Success;

    public static PageRerenderOutcome Success(PageRerenderResult result, string message) => new(
        RegionOperationStatus.Success,
        null,
        result.ArtifactId,
        result.RevisionNo,
        result.Reports.Count,
        !string.IsNullOrEmpty(result.PreviewResourceId),
        message);

    public static PageRerenderOutcome NotReady() =>
        new(RegionOperationStatus.NotReady, "HOST_NOT_READY", Message: "Host 未就绪");

    public static PageRerenderOutcome ReadOnly() =>
        new(RegionOperationStatus.ReadOnly, "HOST_READ_ONLY", Message: "只读模式：Host 未达 parity，写操作已禁用");

    public static PageRerenderOutcome Failed(string code, string? message = null) =>
        new(RegionOperationStatus.Failed, code, Message: message);
}
