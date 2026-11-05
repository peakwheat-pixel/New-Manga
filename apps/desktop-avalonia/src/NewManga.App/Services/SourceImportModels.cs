using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;

namespace NewManga.App.Services;

/// <summary>
/// FEA-09-UI-1: the referenced-source import face (C-16 v1.1 §1/§4 command face — plan preview,
/// confirm, receipt polling, running cancel, one-shot password via Host secret_ref). This is a
/// DELIBERATELY SEPARATE interface: <see cref="IHostController"/> is the FROZEN C-07 API
/// inventory baseline (54 members, doc/plan/FEA-C07_API_INVENTORY.md, checked by
/// tools/generate_api_inventory.py --check) and this Task's Appointment is consume-only, so the
/// four methods live here; the production controllers implement both interfaces instead of
/// widening the frozen face (no C-07 UNFREEZE). Consumers resolve it as an OPTIONAL capability
/// (<c>controller as ISourceImportController</c>) — when a controller does not offer it, the
/// referenced-import entry reports a typed refusal instead of pretending to import.
/// </summary>
public interface ISourceImportController
{
    /// <summary>
    /// Plan preview for referenced sources: registers/authorizes each root, mints the read
    /// grants (Host signs — the UI never does) and asks the Core for the plan. Null when the
    /// Host is not ready / read-only / the Core refused (typed code on
    /// <see cref="HostViewSnapshot.LastError"/>).
    /// </summary>
    Task<SourcePlanPreview?> PlanReferencedImportAsync(
        string chapterId,
        IReadOnlyList<ReferenceImportSource> sources,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Confirms a plan (optionally with the password for encrypted sources; the password goes
    /// only into one Host-minted DPAPI secret reference — C-16 v1.1 §3 — and is never stored,
    /// logged or echoed). Retry-safe: the Core binds the operation id; re-confirming a consumed
    /// plan is a typed <c>SOURCE_PLAN_STALE</c> refusal, never a duplicate submission.
    /// </summary>
    Task<SourceImportStartResult> StartReferencedImportAsync(
        SourcePlanPreview plan,
        string? password,
        CancellationToken cancellationToken = default);

    /// <summary>Receipt poll (read-only); terminal receipts clean up any pending secret reference.</summary>
    Task<SourceImportReceipt?> GetReferencedImportReceiptAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>Running cancel (<c>cancel_import</c>); the receipt converges through polling.</summary>
    Task<SourceImportCancelResult> CancelReferencedImportAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// FEA-11-SCAN-1 (I-2 / AC-S2): after a referenced import reaches the terminal
    /// <see cref="SourceImportOperationState.Completed"/> state, register its sources as Host-side
    /// periodic read-only scan targets (in-process only: no wire command, no persistence). The Host
    /// overwrites a target by <c>source_id</c>, so repeated imports never grow the set. A null
    /// implementation is a no-op; registration failures never change the import result.
    /// </summary>
    void RegisterCompletedImportScanTargets(
        string bookId,
        IReadOnlyList<ReferenceImportSource> sources);
}

/// <summary>
/// FEA-11-SCAN-1 (I-2): one completed-import source handed to the Host scan registry. The path is
/// needed by the Host to mint read grants; it never leaves the in-process registration call.
/// </summary>
public sealed record SourceScanTargetRegistration(
    string SourceId,
    string Path,
    IReadOnlyList<string> ProjectIds,
    string Version);

/// <summary>
/// FEA-09-UI-1: one user-picked referenced import source. <see cref="Path"/> stays inside the
/// view model / controller seam (the Host needs it to mint the grant); it never reaches plan
/// previews, receipts, error text or evidence — those carry the file name only.
/// </summary>
public sealed record ReferenceImportSource(string Path, bool IsFolder);

/// <summary>
/// FEA-09-UI-1: the plan preview the ImportDock renders before the user confirms. Mirrors the
/// frozen C-16 v1.1 §4 <c>PlanImportReferences</c> response; secret/token/path fields are not
/// modelled at all so they cannot leak into the UI by construction.
/// </summary>
public sealed record SourcePlanPreview(
    string ChapterId,
    string DuplicatePolicy,
    string PlanId,
    string PlanDigest,
    IReadOnlyList<string> GrantIds,
    IReadOnlyList<SourcePlanItemView> Items,
    SourcePlanTotals Totals)
{
    public bool NeedsPassword => Items.Any(item => item.Status == "encrypted");
}

/// <summary>One plan row (file name only — the full path is deliberately not carried).</summary>
public sealed record SourcePlanItemView(
    int SourceIndex,
    string DisplayName,
    string SourceKind,
    string Status,
    int? WillImport,
    string? ReasonCode,
    bool AlreadyReferenced);

/// <summary>Plan totals exactly as the Core reports them (C-16 v1.1 §4).</summary>
public sealed record SourcePlanTotals(
    int Import,
    int Skip,
    int Unsupported,
    int Failed);

/// <summary>C-16 v1.1 §4 operation state machine.</summary>
public enum SourceImportOperationState
{
    Unknown,
    Accepted,
    Running,
    Completed,
    Cancelled,
    Failed,
}

/// <summary>C-16 v1.1 §4 frozen count field set (missing fields default 0).</summary>
public sealed record SourceImportCounts(
    int ImportedPages = 0,
    int SkippedPages = 0,
    int SkippedSources = 0,
    int FailedSources = 0,
    int UnsupportedEntries = 0,
    int PendingPages = 0)
{
    public static SourceImportCounts Zero { get; } = new();

    /// <summary>C-16 §4 frozen formula: planned = imported + unsupported + pending (per page).</summary>
    public int PlannedPages => ImportedPages + UnsupportedEntries + PendingPages;
}

/// <summary>One receipt item row (file name only).</summary>
public sealed record SourceImportReceiptItem(
    int SourceIndex,
    string SourceName,
    string SourceKind,
    string Outcome,
    string? ReasonCode,
    int CommittedPages,
    int RemainingPages,
    SourceImportCounts Counts);

/// <summary>The UI-facing receipt (C-16 v1.1 §4 frozen shape, secret-free projection).</summary>
public sealed record SourceImportReceipt(
    string OperationId,
    string ChapterId,
    SourceImportOperationState State,
    bool CancelRequested,
    int CommittedBoundary,
    IReadOnlyList<SourceImportReceiptItem> Items,
    SourceImportCounts Totals)
{
    public bool IsTerminal => State is SourceImportOperationState.Completed
        or SourceImportOperationState.Cancelled
        or SourceImportOperationState.Failed;

    public bool IsActive => State is SourceImportOperationState.Accepted
        or SourceImportOperationState.Running;
}

/// <summary>Typed start outcome — never throws into the UI.</summary>
public sealed record SourceImportStartResult(
    bool Ok,
    string? OperationId,
    string? ErrorCode,
    string Message)
{
    public static SourceImportStartResult NotReady() =>
        new(false, null, "HOST_NOT_READY", "Host 尚未就绪：引用导入不可用");

    public static SourceImportStartResult ReadOnly() =>
        new(false, null, "HOST_READ_ONLY", "Host 处于只读模式：引用导入被拒绝");

    public static SourceImportStartResult Failed(string code, string message) =>
        new(false, null, code, message);

    public static SourceImportStartResult Accepted(string operationId) =>
        new(true, operationId, null, "导入已提交");
}

/// <summary>Typed cancel outcome (C-16 v1.1 §4 CancelImport semantics).</summary>
public sealed record SourceImportCancelResult(
    bool Ok,
    bool Accepted,
    string? State,
    string? ErrorCode)
{
    public static SourceImportCancelResult Failed(string code) => new(false, false, null, code);
}

/// <summary>
/// FEA-09-UI-1: exact wire payloads for the C-16 v1.1 §1/§4 commands the ImportDock consumes.
/// Built with <see cref="Utf8JsonWriter"/> (reflection JSON is disabled in the App), matching
/// the <see cref="ImportExportPayloads"/> convention. The start payload's optional
/// <c>secret_ref</c> carries ONLY the Host-minted token/path/expiry metadata (C-16 §3).
/// </summary>
public static class SourceImportPayloads
{
    public static JsonElement RegisterRoot(string path) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("locator", path);
        writer.WritePropertyName("roots");
        writer.WriteStartArray();
        writer.WriteStringValue(path);
        writer.WriteEndArray();
        writer.WriteEndObject();
    });

    public static JsonElement PlanRequest(string chapterId, IReadOnlyList<string> grants, string duplicatePolicy) =>
        Build(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("chapter_id", chapterId);
            writer.WritePropertyName("grants");
            writer.WriteStartArray();
            foreach (var grant in grants)
            {
                writer.WriteStringValue(grant);
            }

            writer.WriteEndArray();
            writer.WriteString("duplicate_policy", duplicatePolicy);
            writer.WriteEndObject();
        });

    public static JsonElement StartRequest(
        string chapterId,
        string planId,
        string planDigest,
        IReadOnlyList<string> grants,
        string duplicatePolicy,
        string operationId,
        (string Token, string Path, double ExpiresAt)? secretRef = null) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("chapter_id", chapterId);
        writer.WriteString("plan_id", planId);
        writer.WriteString("plan_digest", planDigest);
        writer.WritePropertyName("grants");
        writer.WriteStartArray();
        foreach (var grant in grants)
        {
            writer.WriteStringValue(grant);
        }

        writer.WriteEndArray();
        writer.WriteString("duplicate_policy", duplicatePolicy);
        writer.WriteString("operation_id", operationId);
        if (secretRef is { } secret)
        {
            writer.WritePropertyName("secret_ref");
            writer.WriteStartObject();
            writer.WriteString("token", secret.Token);
            writer.WriteString("path", secret.Path);
            writer.WriteNumber("expires_at", secret.ExpiresAt);
            writer.WriteEndObject();
        }

        writer.WriteEndObject();
    });

    public static JsonElement OperationId(string operationId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("operation_id", operationId);
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

/// <summary>
/// FEA-09-UI-1: total JSON readers for the plan/receipt responses (never throw; missing/typed
/// fields degrade to the C-16 §4 defaults).
/// </summary>
internal static class SourceImportJson
{
    public static SourcePlanPreview? ParsePlan(
        string chapterId,
        string duplicatePolicy,
        IReadOnlyList<string> grantIds,
        JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            return null;
        }

        var planId = ReadString(value, "plan_id");
        var planDigest = ReadString(value, "plan_digest");
        if (string.IsNullOrEmpty(planId) || string.IsNullOrEmpty(planDigest))
        {
            return null;
        }

        var items = new List<SourcePlanItemView>();
        if (value.TryGetProperty("sources", out var sources) && sources.ValueKind == JsonValueKind.Array)
        {
            foreach (var source in sources.EnumerateArray())
            {
                if (source.ValueKind != JsonValueKind.Object)
                {
                    continue;
                }

                items.Add(new SourcePlanItemView(
                    ReadInt(source, "source_index") ?? items.Count,
                    ReadString(source, "source_name") ?? "?",
                    ReadString(source, "source_kind") ?? "?",
                    ReadString(source, "status") ?? "error",
                    ReadNullableInt(source, "will_import"),
                    ReadString(source, "reason_code"),
                    ReadBool(source, "already_referenced", false)));
            }
        }

        var totalsElement = value.GetPropertyOrDefault("totals");
        var totals = new SourcePlanTotals(
            ReadInt(totalsElement, "import") ?? 0,
            ReadInt(totalsElement, "skip") ?? 0,
            ReadInt(totalsElement, "unsupported") ?? 0,
            ReadInt(totalsElement, "failed") ?? 0);
        return new SourcePlanPreview(
            chapterId,
            duplicatePolicy,
            planId,
            planDigest,
            grantIds,
            items,
            totals);
    }

    public static SourceImportReceipt? ParseReceipt(JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            return null;
        }

        var operationId = ReadString(value, "operation_id");
        if (string.IsNullOrEmpty(operationId))
        {
            return null;
        }

        var items = new List<SourceImportReceiptItem>();
        if (value.TryGetProperty("items", out var elements) && elements.ValueKind == JsonValueKind.Array)
        {
            foreach (var element in elements.EnumerateArray())
            {
                if (element.ValueKind != JsonValueKind.Object)
                {
                    continue;
                }

                items.Add(new SourceImportReceiptItem(
                    ReadInt(element, "source_index") ?? items.Count,
                    ReadString(element, "source_name") ?? "?",
                    ReadString(element, "source_kind") ?? "?",
                    ReadString(element, "outcome") ?? "pending",
                    ReadString(element, "reason_code"),
                    ReadInt(element, "committed_pages") ?? 0,
                    ReadInt(element, "remaining_pages") ?? 0,
                    ParseCounts(element.GetPropertyOrDefault("counts"))));
            }
        }

        return new SourceImportReceipt(
            operationId,
            ReadString(value, "chapter_id") ?? string.Empty,
            ParseState(ReadString(value, "state")),
            ReadBool(value, "cancel_requested", false),
            ReadInt(value, "committed_boundary") ?? 0,
            items,
            ParseCounts(value.GetPropertyOrDefault("totals")));
    }

    public static SourceImportCounts ParseCounts(JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            return SourceImportCounts.Zero;
        }

        return new SourceImportCounts(
            ReadInt(value, "imported_pages") ?? 0,
            ReadInt(value, "skipped_pages") ?? 0,
            ReadInt(value, "skipped_sources") ?? 0,
            ReadInt(value, "failed_sources") ?? 0,
            ReadInt(value, "unsupported_entries") ?? 0,
            ReadInt(value, "pending_pages") ?? 0);
    }

    public static SourceImportOperationState ParseState(string? state) => state switch
    {
        "accepted" => SourceImportOperationState.Accepted,
        "running" => SourceImportOperationState.Running,
        "completed" => SourceImportOperationState.Completed,
        "cancelled" => SourceImportOperationState.Cancelled,
        "failed" => SourceImportOperationState.Failed,
        _ => SourceImportOperationState.Unknown,
    };

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

    private static int? ReadNullableInt(JsonElement value, string name) =>
        value.ValueKind == JsonValueKind.Object &&
        value.TryGetProperty(name, out var property) &&
        property.ValueKind == JsonValueKind.Number &&
        property.TryGetInt32(out var parsed)
            ? parsed
            : null;

    internal static bool ReadBool(JsonElement value, string name, bool fallback) =>
        value.ValueKind == JsonValueKind.Object &&
        value.TryGetProperty(name, out var property) &&
        property.ValueKind is JsonValueKind.True or JsonValueKind.False
            ? property.GetBoolean()
            : fallback;
}

internal static class JsonElementExtensions
{
    public static JsonElement GetPropertyOrDefault(this JsonElement value, string name) =>
        value.ValueKind == JsonValueKind.Object && value.TryGetProperty(name, out var property)
            ? property
            : default;
}

/// <summary>UI text for the referenced import face; typed codes only — no paths, no secrets.</summary>
public static class SourceImportText
{
    public static string PlanStatus(string status, string? reasonCode) => status switch
    {
        "ok" => "可导入",
        "encrypted" => "已加密（导入时需要密码）",
        "unsupported" => "不支持（" + ReasonText(reasonCode) + "）",
        "error" => "读取失败（" + CodeText(reasonCode) + "）",
        _ => "未知状态",
    };

    private static string ReasonText(string? reasonCode) =>
        string.IsNullOrEmpty(reasonCode) ? string.Empty :
        CodeText(reasonCode) == reasonCode ? reasonCode : CodeText(reasonCode) + "，" + reasonCode;

    public static string ReceiptOutcome(string outcome, string? reasonCode) => outcome switch
    {
        "imported" => "已导入",
        "skipped" => "已跳过",
        "failed" => "失败（" + ReasonText(reasonCode) + "）",
        "pending" => "待处理",
        "unsupported" => "不支持（" + ReasonText(reasonCode) + "）",
        _ => outcome,
    };

    public static string StateText(SourceImportOperationState state) => state switch
    {
        SourceImportOperationState.Accepted => "已接受",
        SourceImportOperationState.Running => "导入中…",
        SourceImportOperationState.Completed => "导入完成",
        SourceImportOperationState.Cancelled => "已取消",
        SourceImportOperationState.Failed => "导入失败",
        _ => "未知状态",
    };

    public static string CodeText(string? code) => code switch
    {
        "SOURCE_FORMAT_UNSUPPORTED" => "格式不支持（含 AES 加密 ZIP）",
        "SOURCE_PASSWORD_REQUIRED" => "需要密码",
        "SOURCE_PASSWORD_INVALID" => "密码错误",
        "SOURCE_PLAN_STALE" => "预览已过期：源在确认前发生了变化，请重新预览",
        "SOURCE_IMPORT_BUSY" => "同一作品已有进行中的导入",
        "SOURCE_OPERATION_NOT_FOUND" => "导入操作不存在（可能已重启）",
        "SOURCE_OPERATION_CONFLICT" => "导入请求与操作记录不一致",
        "SOURCE_ACCESS_DENIED" => "源访问被拒绝（授权/范围校验失败）",
        "SOURCE_GRANT_EXPIRED" => "源授权已过期，请重新预览",
        "SOURCE_GRANT_REVOKED" => "源授权已撤销",
        "SOURCE_BUDGET_EXCEEDED" => "超出读取预算",
        "SOURCE_ENTRY_MISSING" => "源条目缺失",
        "SOURCE_PROJECT_MISMATCH" => "源与目标项目不匹配",
        "SOURCE_REGISTRY_UNAVAILABLE" => "源授权存储不可用",
        "SOURCE_REGISTRY_BUSY" => "源授权存储忙，请重试",
        "CORE_CAPABILITY_MISSING" => "当前 Core 不支持该操作",
        _ => string.IsNullOrEmpty(code) ? "未知错误" : code,
    };
}

/// <summary>
/// FEA-09-UI-1: production orchestrator for the referenced-source import flow. Owns the exact
/// production chain — <see cref="HostCommandDispatcher"/> (real Host-local routing to the Core
/// stdio commands) plus <see cref="SourceReadCoordinator"/> (register/issue/secret grants) — so
/// the ImportDock never fakes an import and never signs anything itself.
///
/// Secret handling follows C-16 v1.1 §3: the plaintext password lives only in the caller's
/// argument for the duration of one start; it is written once as a DPAPI one-shot token
/// (<see cref="SourceSecretStore"/>), referenced in the start payload as metadata only, and
/// revoked/deleted on terminal state, cancel failure, or dispose. Nothing secret is returned,
/// logged, or put into any modelled record.
/// </summary>
public sealed class SourceImportCoordinator : IAsyncDisposable
{
    /// <summary>
    /// Fixed rendition descriptor digest for import-time grants (64 hex, contract shape; the
    /// Core treats it as an opaque cache/identity key — identity checks use the entry facts).
    /// </summary>
    private static readonly string RenditionParamsDigest = Convert.ToHexString(
        SHA256.HashData(Encoding.UTF8.GetBytes("fea09-ui-1-import-rendition-v1"))).ToLowerInvariant();

    private readonly HostCommandDispatcher _commands;
    private readonly SourceReadCoordinator _sources;
    private readonly string _dataRoot;
    private readonly Action<SourceScanTargetRegistration>? _registerScanTarget;

    private (string Token, string Path)? _activeSecret;

    public SourceImportCoordinator(
        HostCommandDispatcher commands,
        SourceReadCoordinator sources,
        string dataRoot,
        Action<SourceScanTargetRegistration>? registerScanTarget = null)
    {
        _commands = commands;
        _sources = sources;
        _dataRoot = dataRoot;
        _registerScanTarget = registerScanTarget;
    }

    /// <summary>
    /// Registers each source root (reusing an identical, non-revoked registry entry when present)
    /// and asks the Core for a plan. Typed failures propagate to the caller (the controller maps
    /// them onto <c>LastError</c>); an unparseable response returns null.
    /// </summary>
    public async Task<SourcePlanPreview?> PlanAsync(
        string chapterId,
        IReadOnlyList<ReferenceImportSource> sources,
        string duplicatePolicy,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(chapterId) || sources.Count == 0)
        {
            return null;
        }

        var grants = new List<string>();
        foreach (var source in sources)
        {
            grants.AddRange(await IssueGrantsAsync(source, cancellationToken).ConfigureAwait(false));
        }

        var response = await _commands
            .InvokeAsync("plan_import_references", SourceImportPayloads.PlanRequest(chapterId, grants, duplicatePolicy), cancellationToken)
            .ConfigureAwait(false);
        return SourceImportJson.ParsePlan(chapterId, duplicatePolicy, grants, response.Value);
    }

    /// <summary>
    /// Confirms a plan. When a password is supplied for encrypted sources (C-16 v1.1 §3):
    /// capability check → one DPAPI token file → fresh Secret-G grants cloned from the plan's
    /// grants → a re-plan bound to the secret grants (start must match the plan's grants exactly)
    /// → start with the token/path/expiry metadata. The secret context is cleaned up on the next
    /// terminal receipt, cancel, failure, or dispose — never on success paths that still need it.
    /// </summary>
    public async Task<SourceImportStartResult> StartAsync(
        SourcePlanPreview plan,
        string? password,
        CancellationToken cancellationToken)
    {
        if (plan is null || string.IsNullOrWhiteSpace(plan.ChapterId))
        {
            return SourceImportStartResult.Failed("INVALID_REQUEST", "导入计划无效");
        }

        var accepted = false;
        await CleanupSecretAsync().ConfigureAwait(false);
        if (plan.Items.Count(item => item.Status == "encrypted") > 1)
        {
            return SourceImportStartResult.Failed("SOURCE_PASSWORD_REQUIRED", "一次仅支持一个加密源，请分别确认");
        }

        var grants = plan.GrantIds;
        string planId = plan.PlanId;
        string planDigest = plan.PlanDigest;
        (string Token, string Path, double ExpiresAt)? secretRef = null;

        // Defensive: a plain start never carries a secret; a leftover context from an aborted
        // password attempt is cleaned before the new operation begins.
        if (string.IsNullOrEmpty(password) || !plan.NeedsPassword)
        {
            await CleanupSecretAsync().ConfigureAwait(false);
        }

        try
        {
            if (!string.IsNullOrEmpty(password) && plan.NeedsPassword)
            {
                if (!await _sources.SupportsResolveSecretAsync(cancellationToken).ConfigureAwait(false))
                {
                    return SourceImportStartResult.Failed(
                        "CORE_CAPABILITY_MISSING",
                        SourceImportText.CodeText("CORE_CAPABILITY_MISSING"));
                }

                await CleanupSecretAsync().ConfigureAwait(false);
                var (token, secretPath) = SourceSecretStore.WritePassword(
                    _dataRoot,
                    Encoding.UTF8.GetBytes(password));
                _activeSecret = (token, secretPath);
                var expiresAt = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0 + 120;
                var secretGrants = await _sources
                    .IssueSecretGrantsAsync(plan.GrantIds, token, secretPath, expiresAt, cancellationToken)
                    .ConfigureAwait(false);
                // The start request must carry exactly the grants of the plan it confirms, so
                // the secret clones need their own plan before start.
                var replan = await _commands
                    .InvokeAsync(
                        "plan_import_references",
                        SourceImportPayloads.PlanRequest(plan.ChapterId, secretGrants, plan.DuplicatePolicy),
                        cancellationToken)
                    .ConfigureAwait(false);
                var replanned = SourceImportJson.ParsePlan(plan.ChapterId, plan.DuplicatePolicy, secretGrants, replan.Value);
                if (replanned is null)
                {
                    return SourceImportStartResult.Failed("SOURCE_PLAN_STALE", SourceImportText.CodeText("SOURCE_PLAN_STALE"));
                }

                planId = replanned.PlanId;
                planDigest = replanned.PlanDigest;
                grants = secretGrants;
                secretRef = (token, secretPath, expiresAt);
            }

            var operationId = "op-" + Guid.NewGuid().ToString("N");
            var start = await _commands
                .InvokeAsync(
                    "start_import_references",
                    SourceImportPayloads.StartRequest(
                        plan.ChapterId, planId, planDigest, grants, plan.DuplicatePolicy, operationId, secretRef),
                    cancellationToken)
                .ConfigureAwait(false);
            if (!SourceImportJson.ReadBool(start.Value, "accepted", false))
                return SourceImportStartResult.Failed("SOURCE_OPERATION_CONFLICT", SourceImportText.CodeText("SOURCE_OPERATION_CONFLICT"));
            accepted = true;
            return SourceImportStartResult.Accepted(operationId);
        }
        catch (Exception ex) when (IsTypedFailure(ex))
        {
            var code = TypedCode(ex);
            return SourceImportStartResult.Failed(code, SourceImportText.CodeText(code));
        }
        finally
        {
            if (!accepted) await CleanupSecretAsync().ConfigureAwait(false);
        }
    }

    /// <summary>Reads the receipt; a terminal receipt triggers the secret cleanup (idempotent).
    /// Typed failures propagate to the caller.</summary>
    public async Task<SourceImportReceipt?> GetReceiptAsync(string operationId, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(operationId))
        {
            return null;
        }

        var response = await _commands
            .InvokeAsync("get_import_receipt", SourceImportPayloads.OperationId(operationId), cancellationToken)
            .ConfigureAwait(false);
        var receipt = SourceImportJson.ParseReceipt(response.Value);
        if (receipt is { IsTerminal: true })
        {
            await CleanupSecretAsync().ConfigureAwait(false);
        }

        return receipt;
    }

    /// <summary>Cancels a running import (C-16 v1.1 §4); the receipt converges through polling.</summary>
    public async Task<SourceImportCancelResult> CancelAsync(string operationId, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(operationId))
        {
            return SourceImportCancelResult.Failed("INVALID_REQUEST");
        }

        try
        {
            var response = await _commands
                .InvokeAsync("cancel_import", SourceImportPayloads.OperationId(operationId), cancellationToken)
                .ConfigureAwait(false);
            // C-16 v1.1 §4: {operation_id, accepted: bool, state} — accepted:false means the
            // operation was already terminal when the cancel arrived.
            var accepted = SourceImportJson.ReadBool(response.Value, "accepted", false);
            var state = SourceImportJson.ReadString(response.Value, "state");
            return new SourceImportCancelResult(true, accepted, state, null);
        }
        catch (Exception ex) when (IsTypedFailure(ex))
        {
            return SourceImportCancelResult.Failed(TypedCode(ex));
        }
    }

    public async ValueTask DisposeAsync() => await CleanupSecretAsync().ConfigureAwait(false);

    /// <summary>
    /// FEA-11-SCAN-1 (I-2 / AC-S2): derives the C-16 identity of each completed-import source and
    /// hands it to the Host scan registry. Only the App knows the user-picked paths; the Host never
    /// guesses an id. A folder import's lease source id IS its registry id (see
    /// <see cref="IssueGrantsAsync"/>), so the exact registry entry is looked up by root path; a file
    /// import reuses the deterministic <see cref="StableSourceId"/>. Unresolvable sources are skipped
    /// (no id → no target), never guessed.
    /// </summary>
    public void RegisterCompletedScanTargets(string bookId, IReadOnlyList<ReferenceImportSource> sources)
    {
        var register = _registerScanTarget;
        if (register is null || string.IsNullOrWhiteSpace(bookId) || sources.Count == 0)
        {
            return;
        }

        // Re-registration overwrites by source_id (AC-S2), so a repeated import stays one target.
        var targets = new Dictionary<string, SourceScanTargetRegistration>(StringComparer.Ordinal);
        foreach (var source in sources)
        {
            var path = Path.GetFullPath(source.Path);
            string? sourceId;
            if (source.IsFolder)
            {
                sourceId = _sources.Registry.List()
                    .Where(entry => entry.RevokedAt is null
                        && entry.Roots.Length == 1
                        && string.Equals(entry.Roots[0].Root, path, StringComparison.OrdinalIgnoreCase))
                    .Select(entry => entry.RegistryId)
                    .FirstOrDefault();
            }
            else
            {
                sourceId = StableSourceId(path);
            }

            if (string.IsNullOrWhiteSpace(sourceId))
            {
                continue;
            }

            targets[sourceId] = new SourceScanTargetRegistration(
                sourceId, path, new[] { bookId }, "1");
        }

        foreach (var target in targets.Values)
        {
            register(target);
        }
    }

    /// <summary>Pass the selected path and kind to Host; only Host enumerates and authorizes folders.</summary>
    private async Task<IReadOnlyList<string>> IssueGrantsAsync(ReferenceImportSource source, CancellationToken cancellationToken)
    {
        var path = Path.GetFullPath(source.Path);
        var authorization = await FindOrRegisterRootAsync(path, cancellationToken).ConfigureAwait(false);
        var kind = source.IsFolder ? "folder" : KindOf(path);
        return new[]
        {
            await _sources.IssueAsync(
                authorization.RegistryId, authorization.Generation, path, kind,
                source.IsFolder ? authorization.RegistryId : StableSourceId(path),
                "1", RenditionOf(kind), cancellationToken: cancellationToken).ConfigureAwait(false),
        };
    }

    /// <summary>
    /// Reuses an existing non-revoked entry with exactly the same root set (the registry appends
    /// a new entry on every register, so blind registering would grow it without bound).
    /// </summary>
    private async Task<(string RegistryId, int Generation)> FindOrRegisterRootAsync(string path, CancellationToken cancellationToken)
    {
        var response = await _commands
            .InvokeAsync("source_list_roots", default, cancellationToken)
            .ConfigureAwait(false);
        if (response.Value.ValueKind == JsonValueKind.Object &&
            response.Value.TryGetProperty("entries", out var entries) &&
            entries.ValueKind == JsonValueKind.Array)
        {
            foreach (var entry in entries.EnumerateArray())
            {
                if (entry.ValueKind != JsonValueKind.Object ||
                    (SourceImportJson.ReadBool(entry, "revoked", false)) ||
                    !entry.TryGetProperty("roots", out var roots) ||
                    roots.ValueKind != JsonValueKind.Array ||
                    roots.GetArrayLength() != 1)
                {
                    continue;
                }

                var root = roots[0].ValueKind == JsonValueKind.String ? roots[0].GetString() : null;
                var registryId = SourceImportJson.ReadString(entry, "registry_id");
                var generation = SourceImportJson.ReadInt(entry, "generation");
                if (string.Equals(root, path, StringComparison.OrdinalIgnoreCase) &&
                    !string.IsNullOrEmpty(registryId) && generation is { } alive)
                {
                    return (registryId, alive);
                }
            }
        }

        var registered = await _commands
            .InvokeAsync("source_register_root", SourceImportPayloads.RegisterRoot(path), cancellationToken)
            .ConfigureAwait(false);
        var id = SourceImportJson.ReadString(registered.Value, "registry_id");
        var createdGeneration = SourceImportJson.ReadInt(registered.Value, "generation");
        if (string.IsNullOrEmpty(id) || createdGeneration is null)
        {
            throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        }

        return (id, createdGeneration.Value);
    }

    private async Task CleanupSecretAsync()
    {
        var secret = _activeSecret;
        _activeSecret = null;
        if (secret is null)
        {
            return;
        }

        SourceSecretStore.DeleteIfPresent(secret.Value.Path);
        try
        {
            await _sources.RevokeSecretGrantsAsync(CancellationToken.None).ConfigureAwait(false);
        }
        catch
        {
            // best effort: grants expire on their own (C-16 §2 TTL)
        }
    }

    private static string KindOf(string path) => Path.GetExtension(path).ToLowerInvariant() switch
    {
        ".zip" => "zip",
        ".cbz" => "cbz",
        ".pdf" => "pdf",
        _ => "image",
    };

    /// <summary>
    /// The Core derives the source kind from <c>scope.rendition.decoder</c> (frozen
    /// source_read_refs.py <c>_KINDS = {"image","folder","zip","cbz","pdf"}</c>), so the decoder
    /// IS the kind; the params digest is the fixed import-time identity key.
    /// </summary>
    private static JsonElement RenditionOf(string kind)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            writer.WriteStartObject();
            writer.WriteString("decoder", kind);
            writer.WriteNumber("scale", 1.0);
            writer.WriteString("params_digest", RenditionParamsDigest);
            writer.WriteEndObject();
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }

    /// <summary>
    /// Deterministic per-path source id (sha256 of the normalized upper path; the path itself is
    /// not recoverable from it) so the same source keeps its identity across sessions.
    /// </summary>
    private static string StableSourceId(string normalizedPath)
    {
        var digest = SHA256.HashData(Encoding.UTF8.GetBytes(normalizedPath.ToUpperInvariant()));
        return "src-" + Convert.ToHexString(digest).ToLowerInvariant()[..16];
    }

    private static bool IsTypedFailure(Exception ex) => ex is
        CoreOperationException or SourceAccessException or SidecarException or
        NewManga.CoreClient.Bridge.BridgeException or HostCommandInvalidArgumentsException or
        IOException or UnauthorizedAccessException or InvalidOperationException or ArgumentException or
        OperationCanceledException;

    private static string TypedCode(Exception ex) => ex switch
    {
        CoreOperationException core => core.Code,
        SourceAccessException source => source.Message,
        SidecarException sidecar => sidecar.Code.ToString(),
        NewManga.CoreClient.Bridge.BridgeException => "HOST_UNAVAILABLE",
        HostCommandInvalidArgumentsException => "INVALID_ARGUMENTS",
        OperationCanceledException => "CANCELLED",
        _ => "HOST_UNAVAILABLE",
    };
}
