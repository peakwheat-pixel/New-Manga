using NewManga.App.Services;
using NewManga.DesignSystem.Controls;

namespace NewManga.App.ViewModels.Fluent;

/// <summary>
/// FEA-06-RESIDUAL-3 AC-1 (格 1) / AC-2 (格 5): the Fluent-owned mapping from the frozen Host
/// <see cref="TaskProjectionInfo"/> (C060 <c>library_get_task_projection</c>) to the two workbench
/// control surfaces — the batch matrix and the 9-row console table.
///
/// <para>红线：本类型**不引用** V2 映射（<c>StudioRunControllerDataSource</c>/<c>IRunDataSource</c>/
/// <c>StudioRunProjection</c>），只消费冻结的 <see cref="TaskProjectionInfo"/> record；缺失字段一律
/// 呈现「—」，**绝不**用 0 或推测值充数（V11R-A-2 AC4「不伪造进度」）。</para>
///
/// <para>术语（卡面落表，逐字使用）：七状态 <c>Queued</c>/<c>Running</c>/<c>Done</c>/<c>Failed</c>/
/// <c>Blocked</c>/<c>Stale</c>/<c>Skipped</c>（另加设计系统的 <c>NotStarted</c>/<c>Locked</c> 兜底）；
/// 9 行 <see cref="LineLabels"/> 的冻结顺序 <c>RunId</c>/<c>RunStatus</c>/<c>OverallProgress</c>/
/// <c>CurrentPageId</c>/<c>CurrentStepType</c>/<c>Completed</c>/<c>Failed</c>/<c>Skipped</c>/<c>Blocked</c>。</para>
/// </summary>
public sealed class FluentRunProjection
{
    /// <summary>Honest missing value for one projected field (AC-2: <c>Counts</c> 缺失显示「—」而非 0).</summary>
    public const string Missing = "—";

    /// <summary>AC-2 冻结的 9 行顺序（术语落表，逐字使用）。</summary>
    public static readonly IReadOnlyList<string> LineLabels = new[]
    {
        "RunId",
        "RunStatus",
        "OverallProgress",
        "CurrentPageId",
        "CurrentStepType",
        "Completed",
        "Failed",
        "Skipped",
        "Blocked",
    };

    private FluentRunProjection(
        string runId,
        string runStatus,
        StatusKind runStatusKind,
        string overallProgress,
        string currentPageId,
        string currentStepType,
        string completed,
        string failed,
        string skipped,
        string blocked,
        RunControlsInfo controls,
        IReadOnlyList<FluentRunRow> rows)
    {
        RunId = runId;
        RunStatus = runStatus;
        RunStatusKind = runStatusKind;
        OverallProgress = overallProgress;
        CurrentPageId = currentPageId;
        CurrentStepType = currentStepType;
        Completed = completed;
        Failed = failed;
        Skipped = skipped;
        Blocked = blocked;
        Controls = controls;
        Rows = rows;
        Lines = new[]
        {
            new FluentRunLine("RunId", runId),
            new FluentRunLine("RunStatus", runStatus),
            new FluentRunLine("OverallProgress", overallProgress),
            new FluentRunLine("CurrentPageId", currentPageId),
            new FluentRunLine("CurrentStepType", currentStepType),
            new FluentRunLine("Completed", completed),
            new FluentRunLine("Failed", failed),
            new FluentRunLine("Skipped", skipped),
            new FluentRunLine("Blocked", blocked),
        };
    }

    /// <summary>The host run id exactly as projected (<see cref="Missing"/> when absent).</summary>
    public string RunId { get; }
    /// <summary>The raw Core run status string (<see cref="Missing"/> when absent).</summary>
    public string RunStatus { get; }
    /// <summary>The seven-state channel for <see cref="RunStatus"/> (verbatim <see cref="StatusKind"/> name).</summary>
    public StatusKind RunStatusKind { get; }
    /// <summary>Localized status label; never only a colour (design 03 §4 / StatusCatalog).</summary>
    public string RunStatusLabel => StatusCatalog.Label(RunStatusKind);
    /// <summary>Localized run state text (frozen run vocabulary, own copy — no V2 reference).</summary>
    public string RunStatusText => RunStateText(RunStatus);
    public string OverallProgress { get; }
    public string CurrentPageId { get; }
    public string CurrentStepType { get; }
    public string Completed { get; }
    public string Failed { get; }
    public string Skipped { get; }
    public string Blocked { get; }
    /// <summary>AC-2: control availability comes ONLY from this frozen projection record.</summary>
    public RunControlsInfo Controls { get; }
    /// <summary>Batch matrix rows (per-page rows in Core target order).</summary>
    public IReadOnlyList<FluentRunRow> Rows { get; }
    /// <summary>AC-2 的 9 行（冻结顺序 = <see cref="LineLabels"/>）。</summary>
    public IReadOnlyList<FluentRunLine> Lines { get; }

    public bool HasRows => Rows.Count > 0;

    /// <summary>
    /// Run bar copy bound by both control surfaces. Without a projection the bar keeps the honest
    /// empty copy (no fabricated progress); the progress suffix appears only when the Host projects it.
    /// </summary>
    public string BarText
    {
        get
        {
            if (RunId == Missing)
            {
                return string.Empty;
            }

            var progress = OverallProgress == Missing ? string.Empty : $" · {OverallProgress}";
            return $"Run {RunId} · {RunStatusText}{progress}";
        }
    }

    /// <summary>
    /// The honest "no projection" instance: every field <see cref="Missing"/> and every control
    /// disabled. Used by both surfaces before the first successful poll — never a fake 0%.
    /// </summary>
    public static FluentRunProjection None { get; } = new(
        Missing, Missing, StatusKind.NotStarted, Missing, Missing, Missing,
        Missing, Missing, Missing, Missing,
        new RunControlsInfo(false, false, false, false, false, false),
        Array.Empty<FluentRunRow>());

    /// <summary>Maps one C060 projection. Purely a projection read: nothing is derived or invented.</summary>
    public static FluentRunProjection From(TaskProjectionInfo projection)
    {
        var rows = new List<FluentRunRow>(projection.Rows.Count);
        for (var index = 0; index < projection.Rows.Count; index++)
        {
            var row = projection.Rows[index];
            var kind = MapStatus(row.Status);
            rows.Add(new FluentRunRow(
                row.PageId,
                // R3-001：Core 的 page_order 是 **1-based**（src/application/tasks/projection.py:206-207 的
                // fallback `index + 1`；DB pages.sort_order 亦从 1 开始，见
                // tests/library/test_import_images.py:42 `(1, 1)`）。这里在映射边界就归一为
                // 「1-based 显示序」，视图直接渲染 `第 {Order} 页`，不再额外 +1（旧实现会显示第 2 页）。
                row.PageOrder is > 0 ? row.PageOrder.Value : index + 1,
                string.IsNullOrWhiteSpace(row.Filename) ? Missing : row.Filename,
                kind,
                StatusCatalog.Label(kind),
                StatusKey(kind),
                row.ErrorCode,
                // list-item a11y: main text + status (design 03 §5).
                $"{row.Filename} · {StatusCatalog.Label(kind)}"));
        }

        return new FluentRunProjection(
            Value(projection.RunId),
            Value(projection.RunStatus),
            MapStatus(projection.RunStatus),
            projection.OverallProgress is { } progress ? $"{progress:P0}" : Missing,
            Value(projection.CurrentPageId),
            Value(projection.CurrentStepType),
            Count(projection.Counts?.Completed),

            Count(projection.Counts?.Failed),
            Count(projection.Counts?.Skipped),
            Count(projection.Counts?.Blocked),
            projection.Controls ?? new RunControlsInfo(false, false, false, false, false, false),
            rows);
    }

    /// <summary>Map one Core status string onto the frozen nine-state status language.</summary>
    public static StatusKind MapStatus(string? status) => status?.Trim().ToLowerInvariant() switch
    {
        "queued" or "pending" or "waiting" => StatusKind.Queued,
        "running" or "processing" => StatusKind.Running,
        "done" or "completed" or "completed_with_failures" => StatusKind.Done,
        "failed" or "error" or "interrupted" => StatusKind.Failed,
        "blocked" => StatusKind.Blocked,
        "stale" => StatusKind.Stale,
        "skipped" => StatusKind.Skipped,
        "locked" => StatusKind.Locked,
        _ => StatusKind.NotStarted,
    };

    /// <summary>The verbatim seven-state name for one status channel (卡面术语落表).</summary>
    public static string StatusKey(StatusKind kind) => kind switch
    {
        StatusKind.Queued => nameof(StatusKind.Queued),
        StatusKind.Running => nameof(StatusKind.Running),
        StatusKind.Done => nameof(StatusKind.Done),
        StatusKind.Failed => nameof(StatusKind.Failed),
        StatusKind.Blocked => nameof(StatusKind.Blocked),
        StatusKind.Stale => nameof(StatusKind.Stale),
        StatusKind.Skipped => nameof(StatusKind.Skipped),
        StatusKind.Locked => nameof(StatusKind.Locked),
        _ => nameof(StatusKind.NotStarted),
    };

    /// <summary>Localized run state text (own Fluent copy; no V2 type is referenced).</summary>
    public static string RunStateText(string? state) => state?.Trim().ToLowerInvariant() switch
    {
        "completed" or "done" => "已完成",
        "completed_with_failures" => "已完成（有失败页）",
        "running" or "processing" => "进行中",
        "failed" or "error" => "失败",
        "interrupted" => "已中断",
        "blocked" => "阻塞",
        "waiting" or "pending" or "queued" => "等待",
        "skipped" => "跳过",
        "cancelled" or "canceled" or "stopped" => "已取消",
        "paused" => "已暂停",
        "stale" => "过期",
        null or "" => "未知",
        _ => state!,
    };

    /// <summary>
    /// R3-007：Run 是否已到终态（Core <c>run_status</c> 词汇）。终态后 Workbench 释放跟踪的 RunId
    /// 并停止轮询，使「开始处理」重新可用（同一章节可再次提交新的 Run）。
    /// </summary>
    public static bool IsTerminalRunStatus(string? status) => status?.Trim().ToLowerInvariant() is
        "completed" or "done" or "completed_with_failures" or "failed" or "error" or "interrupted" or
        "cancelled" or "canceled" or "stopped";

    private static string Value(string? value) => string.IsNullOrWhiteSpace(value) ? Missing : value!;

    private static string Count(int? value) => value?.ToString() ?? Missing;
}

/// <summary>
/// One row of the AC-1 batch matrix: real Host row fields + the frozen status channel.
/// <see cref="Order"/> is the 1-based display/business order (= Core <c>page_order</c>, R3-001).
/// </summary>
public sealed record FluentRunRow(
    string PageId,
    int Order,
    string Filename,
    StatusKind Status,
    string StatusLabel,
    string StatusKey,
    string? ErrorCode,
    string AccessibleName)
{
    /// <summary>Visible status cell text: symbol + label; the colour is never the only channel.</summary>
    public string StatusCell => $"{StatusCatalog.Symbol(Status)} {StatusLabel}";

    public string ErrorCell => string.IsNullOrWhiteSpace(ErrorCode) ? FluentRunProjection.Missing : ErrorCode!;
}

/// <summary>One labelled field of the AC-2 9-row table.</summary>
public sealed record FluentRunLine(string Label, string Value);
