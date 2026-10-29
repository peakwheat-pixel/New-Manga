using System.Text.Json;

namespace NewManga.App.Services;

/// <summary>
/// V11R-A-2 (audit P-02, contract §5.2): the four frozen Run control actions the UI may request.
/// The Core wire names are <c>pause</c> / <c>continue</c> / <c>stop</c> / <c>restart</c>; the Core's
/// own <c>abandon</c> action is intentionally not exposed by the frozen UI enum (recorded as a known
/// gap in <c>doc/contracts/V11R_COMMAND_CONTRACT_V1.md</c>).
/// </summary>
public enum RunControlAction
{
    Pause,
    Resume,
    Stop,
    Restart,
}

/// <summary>
/// V11R-A-2 (contract §5.2): one typed Run start request. <see cref="Scope"/> is the frozen
/// <c>PipelineScope</c> object (<c>book</c> / <c>chapter</c> / <c>page_selection</c> / <c>page</c> /
/// <c>region</c>), <see cref="Overrides"/> the optional pipeline overrides object and
/// <see cref="IdempotencyKey"/> is mandatory — the Core reuses the accepted run for the same key and
/// fingerprint (<c>IDEMPOTENCY_KEY_REUSED</c> otherwise).
/// </summary>
public sealed record RunStartRequest(
    string Command,
    IReadOnlyDictionary<string, object?> Scope,
    IReadOnlyDictionary<string, object?>? Overrides,
    string IdempotencyKey);

/// <summary>StartRun result (C056): the accepted run id plus its status ("pending" when created).</summary>
public sealed record RunStartInfo(string RunId, string Status)
{
    public static RunStartInfo FromJson(JsonElement value) => new(
        RunJson.ReadString(value, "run_id") ?? string.Empty,
        RunJson.ReadString(value, "status") ?? "pending");
}

/// <summary>
/// ControlRun / ResumeBlockedRun / RetryFailedTargets result (C057/C058/C061): the run id + status,
/// plus the child run when the Core restarted a run (C057 restart).
/// </summary>
public sealed record RunControlInfo(
    string RunId,
    string Status,
    string? NewRunId = null,
    string? NewRunStatus = null)
{
    public static RunControlInfo FromJson(JsonElement value) => new(
        RunJson.ReadString(value, "run_id") ?? string.Empty,
        RunJson.ReadString(value, "status") ?? string.Empty,
        RunJson.ReadString(value, "new_run_id"),
        RunJson.ReadString(value, "new_run_status"));
}

/// <summary>
/// One frozen <c>PipelineScope</c> projection echoed by GetRunSnapshot. Only the fields the Core
/// sends for the matching <see cref="Kind"/> are populated; nothing is inferred.
/// </summary>
public sealed record RunScopeInfo(
    string Kind,
    string? BookId = null,
    string? ChapterId = null,
    string? PageId = null,
    string? RegionId = null,
    IReadOnlyList<string>? PageIds = null)
{
    public static RunScopeInfo FromJson(JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            return new RunScopeInfo(string.Empty);
        }

        var pageIds = RunJson.ReadStringArray(value, "page_ids");
        return new RunScopeInfo(
            RunJson.ReadString(value, "kind") ?? string.Empty,
            RunJson.ReadString(value, "book_id"),
            RunJson.ReadString(value, "chapter_id"),
            RunJson.ReadString(value, "page_id"),
            RunJson.ReadString(value, "region_id"),
            pageIds);
    }
}

/// <summary>One run target row (page or region) in Core target order.</summary>
public sealed record RunTargetInfo(string TargetId, string TargetType, int Order)
{
    public static RunTargetInfo? FromJson(JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            return null;
        }

        var targetId = RunJson.ReadString(value, "target_id");
        if (string.IsNullOrEmpty(targetId))
        {
            return null;
        }

        return new RunTargetInfo(
            targetId,
            RunJson.ReadString(value, "target_type") ?? string.Empty,
            RunJson.ReadInt(value, "order") ?? 0);
    }
}

/// <summary>GetRunSnapshot projection (C059): command, scope, status and the expanded targets.</summary>
public sealed record RunSnapshotInfo(
    string RunId,
    string Command,
    RunScopeInfo Scope,
    string Status,
    IReadOnlyList<RunTargetInfo> Targets,
    string? SourceRunId = null,
    string? RetryReason = null)
{
    public static RunSnapshotInfo FromJson(JsonElement value)
    {
        var targets = new List<RunTargetInfo>();
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty("targets", out var targetsElement) &&
            targetsElement.ValueKind == JsonValueKind.Array)
        {
            foreach (var target in targetsElement.EnumerateArray())
            {
                var parsed = RunTargetInfo.FromJson(target);
                if (parsed is not null)
                {
                    targets.Add(parsed);
                }
            }
        }

        return new RunSnapshotInfo(
            RunJson.ReadString(value, "run_id") ?? string.Empty,
            RunJson.ReadString(value, "command") ?? string.Empty,
            RunScopeInfo.FromJson(RunJson.ReadObject(value, "scope")),
            RunJson.ReadString(value, "status") ?? string.Empty,
            targets,
            RunJson.ReadString(value, "source_run_id"),
            RunJson.ReadString(value, "retry_reason"));
    }
}

/// <summary>One stage in the projection's stage flow (<c>type</c>/<c>label</c>/<c>state</c>).</summary>
public sealed record RunStepFlowInfo(string Type, string Label, string State)
{
    public static RunStepFlowInfo FromJson(JsonElement value) => new(
        RunJson.ReadString(value, "type") ?? string.Empty,
        RunJson.ReadString(value, "label") ?? string.Empty,
        RunJson.ReadString(value, "state") ?? string.Empty);
}

/// <summary>One per-page row of the task projection.</summary>
public sealed record RunRowInfo(
    string PageId,
    int? PageOrder,
    string Filename,
    string Status,
    bool IsLocked,
    bool IsPipelineCurrent,
    string? ErrorCode)
{
    public static RunRowInfo FromJson(JsonElement value) => new(
        RunJson.ReadString(value, "page_id") ?? string.Empty,
        RunJson.ReadInt(value, "page_order"),
        RunJson.ReadString(value, "filename") ?? string.Empty,
        RunJson.ReadString(value, "status") ?? string.Empty,
        RunJson.ReadBool(value, "is_locked") ?? false,
        RunJson.ReadBool(value, "is_pipeline_current") ?? false,
        RunJson.ReadString(value, "error_code"));
}

/// <summary>One executed step of a projection task (provider/model/device are the real Core values).</summary>
public sealed record RunStepInfo(
    string StepRunId,
    string StepType,
    string Status,
    int? RetryNo,
    string? ErrorCode,
    string? ErrorMessage,
    string? Provider,
    string? Model,
    string? Device)
{
    public static RunStepInfo FromJson(JsonElement value) => new(
        RunJson.ReadString(value, "step_run_id") ?? string.Empty,
        RunJson.ReadString(value, "step_type") ?? string.Empty,
        RunJson.ReadString(value, "status") ?? string.Empty,
        RunJson.ReadInt(value, "retry_no"),
        RunJson.ReadString(value, "error_code"),
        RunJson.ReadString(value, "error_message"),
        RunJson.ReadString(value, "provider"),
        RunJson.ReadString(value, "model"),
        RunJson.ReadString(value, "device"));
}

/// <summary>One per-page (or per-region) task with its executed steps.</summary>
public sealed record RunTaskInfo(
    string TaskId,
    string PageId,
    string Status,
    string? ErrorCode,
    string? ErrorMessage,
    IReadOnlyList<RunStepInfo> Steps)
{
    public static RunTaskInfo FromJson(JsonElement value)
    {
        var steps = new List<RunStepInfo>();
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty("steps", out var stepsElement) &&
            stepsElement.ValueKind == JsonValueKind.Array)
        {
            foreach (var step in stepsElement.EnumerateArray())
            {
                if (step.ValueKind == JsonValueKind.Object)
                {
                    steps.Add(RunStepInfo.FromJson(step));
                }
            }
        }

        return new RunTaskInfo(
            RunJson.ReadString(value, "task_id") ?? string.Empty,
            RunJson.ReadString(value, "page_id") ?? string.Empty,
            RunJson.ReadString(value, "status") ?? string.Empty,
            RunJson.ReadString(value, "error_code"),
            RunJson.ReadString(value, "error_message"),
            steps);
    }
}

/// <summary>
/// Projection counters. <c>null</c> means "the Core did not report this counter" — the service layer
/// never substitutes a plausible-looking 0 (V11R-A-2 AC4: no fabricated progress).
/// </summary>
public sealed record RunCountsInfo(
    int? Total = null,
    int? Completed = null,
    int? Failed = null,
    int? Skipped = null,
    int? Blocked = null,
    int? Waiting = null,
    int? Processing = null)
{
    public static RunCountsInfo FromJson(JsonElement value) => new(
        RunJson.ReadInt(value, "total"),
        RunJson.ReadInt(value, "completed"),
        RunJson.ReadInt(value, "failed"),
        RunJson.ReadInt(value, "skipped"),
        RunJson.ReadInt(value, "blocked"),
        RunJson.ReadInt(value, "waiting"),
        RunJson.ReadInt(value, "processing"));
}

/// <summary>The Core-projected control availability flags for one run.</summary>
public sealed record RunControlsInfo(
    bool CanPause,
    bool CanStop,
    bool CanContinue,
    bool CanRestart,
    bool CanAbandon,
    bool CanRetryFailed)
{
    public static RunControlsInfo FromJson(JsonElement value) => new(
        RunJson.ReadBool(value, "can_pause") ?? false,
        RunJson.ReadBool(value, "can_stop") ?? false,
        RunJson.ReadBool(value, "can_continue") ?? false,
        RunJson.ReadBool(value, "can_restart") ?? false,
        RunJson.ReadBool(value, "can_abandon") ?? false,
        RunJson.ReadBool(value, "can_retry_failed") ?? false);
}

/// <summary>
/// GetTaskProjection projection (C060) exactly as the Core composes it: per-page rows, per-task
/// executions with their stage steps, counters, blocked reasons and controls. The service layer only
/// parses — it never derives or invents progress numbers (V11R-A-2 AC4).
/// </summary>
public sealed record TaskProjectionInfo(
    string RunId,
    string RunStatus,
    string? RunTitle,
    double? OverallProgress,
    string? CurrentPageId,
    string? CurrentStepType,
    IReadOnlyList<RunStepFlowInfo> StepFlow,
    IReadOnlyList<RunRowInfo> Rows,
    IReadOnlyList<RunTaskInfo> Tasks,
    RunCountsInfo Counts,
    IReadOnlyList<string> BlockedReasons,
    RunControlsInfo Controls)
{
    public static TaskProjectionInfo FromJson(JsonElement value)
    {
        var stepFlow = new List<RunStepFlowInfo>();
        var rows = new List<RunRowInfo>();
        var tasks = new List<RunTaskInfo>();
        if (value.ValueKind == JsonValueKind.Object)
        {
            AppendObjects(value, "step_flow", stepFlow, RunStepFlowInfo.FromJson);
            AppendObjects(value, "rows", rows, RunRowInfo.FromJson);
            AppendObjects(value, "tasks", tasks, RunTaskInfo.FromJson);
        }

        return new TaskProjectionInfo(
            RunJson.ReadString(value, "run_id") ?? string.Empty,
            RunJson.ReadString(value, "run_status") ?? string.Empty,
            RunJson.ReadString(value, "run_title"),
            RunJson.ReadDouble(value, "overall_progress"),
            RunJson.ReadString(value, "current_page_id"),
            RunJson.ReadString(value, "current_step_type"),
            stepFlow,
            rows,
            tasks,
            RunCountsInfo.FromJson(RunJson.ReadObject(value, "counts")),
            RunJson.ReadStringArray(value, "blocked_reasons") ?? Array.Empty<string>(),
            RunControlsInfo.FromJson(RunJson.ReadObject(value, "controls")));
    }

    private static void AppendObjects<T>(
        JsonElement value,
        string property,
        List<T> target,
        Func<JsonElement, T> parse)
    {
        if (!value.TryGetProperty(property, out var array) || array.ValueKind != JsonValueKind.Array)
        {
            return;
        }

        foreach (var item in array.EnumerateArray())
        {
            if (item.ValueKind == JsonValueKind.Object)
            {
                target.Add(parse(item));
            }
        }
    }
}

/// <summary>
/// V11R-A-2 (contract §5.2 / R-08): the Run domain service seam.
///
/// Every method maps 1:1 onto a registered production command — C056 <c>library_start_run</c>,
/// C057 <c>library_control_run</c>, C058 <c>library_resume_blocked_run</c>,
/// C059 <c>library_get_run_snapshot</c>, C060 <c>library_get_task_projection</c>,
/// C061 <c>library_retry_failed_targets</c> — all on protocol minor 3. Refusals return
/// <c>null</c> and publish a typed code through <see cref="HostViewSnapshot.LastError"/>; methods
/// never throw into the UI.
///
/// Idempotency keys (R-08): <see cref="RunStartRequest.IdempotencyKey"/> is mandatory,
/// <see cref="RetryFailedTargetsAsync"/> takes a mandatory non-nullable key, and
/// <see cref="ControlRunAsync"/> requires one only for <see cref="RunControlAction.Restart"/>.
/// A missing/blank key is refused locally with <c>INVALID_REQUEST</c> — never silently generated.
/// </summary>
public interface IRunController
{
    /// <summary>C056 <c>library_start_run</c> → Core <c>StartRun</c> (minor 3).</summary>
    Task<RunStartInfo?> StartRunAsync(RunStartRequest request, CancellationToken ct = default);

    /// <summary>
    /// C057 <c>library_control_run</c> → Core <c>ControlRun</c> (minor 3). <paramref name="idempotencyKey"/>
    /// is mandatory for <see cref="RunControlAction.Restart"/> and ignored otherwise (the frozen Core
    /// rejects a key on non-restart actions).
    /// </summary>
    Task<RunControlInfo?> ControlRunAsync(
        string runId,
        RunControlAction action,
        string? idempotencyKey = null,
        CancellationToken ct = default);

    /// <summary>C058 <c>library_resume_blocked_run</c> → Core <c>ResumeBlockedRun</c> (minor 3).</summary>
    Task<RunControlInfo?> ResumeBlockedRunAsync(string runId, CancellationToken ct = default);

    /// <summary>C059 <c>library_get_run_snapshot</c> → Core <c>GetRunSnapshot</c> (minor 3).</summary>
    Task<RunSnapshotInfo?> GetRunSnapshotAsync(string runId, CancellationToken ct = default);

    /// <summary>C060 <c>library_get_task_projection</c> → Core <c>GetTaskProjection</c> (minor 3).</summary>
    Task<TaskProjectionInfo?> GetTaskProjectionAsync(string runId, CancellationToken ct = default);

    /// <summary>
    /// C061 <c>library_retry_failed_targets</c> → Core <c>RetryFailedTargets</c> (minor 3).
    /// <paramref name="idempotencyKey"/> is mandatory.
    /// </summary>
    Task<RunControlInfo?> RetryFailedTargetsAsync(
        string runId,
        string idempotencyKey,
        CancellationToken ct = default);
}

/// <summary>
/// V11R-A-2: exact wire payloads for the six Run commands. Kept separate from the controller so the
/// dispatcher-expected key sets are pinned independently and tests can assert them without a Core.
/// Built with <see cref="Utf8JsonWriter"/> (reflection-based JsonSerializer is disabled in the App).
/// </summary>
public static class RunPayloads
{
    /// <summary>
    /// C056 StartRun payload. Note the dispatcher (<c>HostCommandDispatcher.WriteCorePayload</c>)
    /// injects the Host-side default <c>overrides.provider_bindings</c> when the caller sends none, so
    /// an absent <see cref="RunStartRequest.Overrides"/> keeps that default behaviour.
    /// </summary>
    public static JsonElement StartRun(RunStartRequest request) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("command", request.Command);
        writer.WritePropertyName("scope");
        WriteObject(writer, request.Scope);
        if (request.Overrides is not null)
        {
            writer.WritePropertyName("overrides");
            WriteObject(writer, request.Overrides);
        }

        writer.WriteString("idempotency_key", request.IdempotencyKey);
        writer.WriteEndObject();
    });

    /// <summary>C057 ControlRun payload; <c>idempotency_key</c> is written only for restart.</summary>
    public static JsonElement ControlRun(string runId, RunControlAction action, string? idempotencyKey) =>
        Build(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("run_id", runId);
            writer.WriteString("action", ActionName(action));
            if (action == RunControlAction.Restart && !string.IsNullOrWhiteSpace(idempotencyKey))
            {
                writer.WriteString("idempotency_key", idempotencyKey);
            }

            writer.WriteEndObject();
        });

    public static JsonElement RunId(string runId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("run_id", runId);
        writer.WriteEndObject();
    });

    /// <summary>C061 RetryFailedTargets payload (run id + mandatory idempotency key).</summary>
    public static JsonElement RetryFailedTargets(string runId, string idempotencyKey) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("run_id", runId);
        writer.WriteString("idempotency_key", idempotencyKey);
        writer.WriteEndObject();
    });

    /// <summary>Frozen Core wire name for one control action (contract §5.2 / core_service.py).</summary>
    public static string ActionName(RunControlAction action) => action switch
    {
        RunControlAction.Pause => "pause",
        RunControlAction.Resume => "continue",
        RunControlAction.Stop => "stop",
        RunControlAction.Restart => "restart",
        _ => throw new ArgumentOutOfRangeException(nameof(action), action, "unknown run control action"),
    };

    private static void WriteObject(Utf8JsonWriter writer, IReadOnlyDictionary<string, object?> value)
    {
        writer.WriteStartObject();
        foreach (var pair in value)
        {
            WriteValue(writer, pair.Key, pair.Value);
        }

        writer.WriteEndObject();
    }

    private static void WriteValue(Utf8JsonWriter writer, string property, object? value)
    {
        switch (value)
        {
            case null:
                writer.WriteNull(property);
                break;
            case string text:
                writer.WriteString(property, text);
                break;
            case bool flag:
                writer.WriteBoolean(property, flag);
                break;
            case int number:
                writer.WriteNumber(property, number);
                break;
            case long number:
                writer.WriteNumber(property, number);
                break;
            case double number:
                writer.WriteNumber(property, number);
                break;
            case JsonElement element:
                writer.WritePropertyName(property);
                element.WriteTo(writer);
                break;
            case IEnumerable<string> items:
                writer.WritePropertyName(property);
                writer.WriteStartArray();
                foreach (var item in items)
                {
                    writer.WriteStringValue(item);
                }

                writer.WriteEndArray();
                break;
            default:
                throw new ArgumentException(
                    $"unsupported run payload value type for '{property}': {value.GetType().Name}",
                    nameof(value));
        }
    }

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

/// <summary>Small, total JSON readers shared by the Run projections (never throw into the UI).</summary>
internal static class RunJson
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

    public static double? ReadDouble(JsonElement value, string name)
    {
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty(name, out var property) &&
            property.ValueKind == JsonValueKind.Number &&
            property.TryGetDouble(out var parsed) &&
            !double.IsNaN(parsed) &&
            !double.IsInfinity(parsed))
        {
            return parsed;
        }

        return null;
    }

    public static bool? ReadBool(JsonElement value, string name)
    {
        if (value.ValueKind == JsonValueKind.Object &&
            value.TryGetProperty(name, out var property) &&
            property.ValueKind is JsonValueKind.True or JsonValueKind.False)
        {
            return property.GetBoolean();
        }

        return null;
    }

    public static JsonElement ReadObject(JsonElement value, string name) =>
        value.ValueKind == JsonValueKind.Object &&
        value.TryGetProperty(name, out var property) &&
        property.ValueKind == JsonValueKind.Object
            ? property
            : default;

    public static IReadOnlyList<string>? ReadStringArray(JsonElement value, string name)
    {
        if (value.ValueKind != JsonValueKind.Object ||
            !value.TryGetProperty(name, out var property) ||
            property.ValueKind != JsonValueKind.Array)
        {
            return null;
        }

        var items = new List<string>();
        foreach (var item in property.EnumerateArray())
        {
            if (item.ValueKind == JsonValueKind.String)
            {
                items.Add(item.GetString()!);
            }
        }

        return items;
    }
}
