namespace NewManga.App.Services;

/// <summary>
/// TRANS-ENTRY-UI (L1-T-C) AC1/AC2/AC4: the ONE place where a run/provider failure becomes a
/// user-visible Chinese sentence. Every string here is asserted by tests, so the UI can never go
/// back to printing a bare Core code (the black-box state the card describes).
///
/// Deliberate honesty (AC2, card §"容易翻车的点"): the frozen Core reports *both* a wrong model
/// name and a 402 no-quota answer as <c>INVALID_INPUT</c>, so this mapper does NOT invent a
/// distinction — it says both possibilities in one sentence. 429 keeps its own retryable line and
/// 401/403 keeps its own non-retryable line, because those two ARE distinguishable on the wire.
/// </summary>
public static class TranslateErrorText
{
    /// <summary>AC4: the restart constraint measured by T-A/L2 (provider instances are built at assembly).</summary>
    public const string RestartHint = "修改模型配置后需重启应用生效。";

    /// <summary>AC1: what the workbench shows instead of sending StartRun with no provider.</summary>
    public const string ProviderNotConfigured =
        "还没有可用的翻译模型 Provider：请到「设置 → Provider 与凭据」添加并启用一个，然后回到这里重试。修改模型配置后需重启应用生效。";

    /// <summary>AC2: 401/403 — retrying the same key can never help.</summary>
    public const string ProviderAuthFailed =
        "Provider 拒绝了当前凭据（401/403，API key 无效或无权限）。请到「设置 → Provider 与凭据」更新 key 后重启应用；这类错误重试不会改善。";

    /// <summary>
    /// AC2: 404 (wrong model) and 402 (no quota) both arrive as <c>INVALID_INPUT</c>; the UI must
    /// not fake a distinction, so this sentence names both and says the Core does not separate them.
    /// </summary>
    public const string RequestRejectedRaw =
        "请求被拒绝：可能是模型名写错（404），也可能是账户额度/余额不足（402）。Core 目前对这两种情况返回同一个错误码，请核对模型名与账户额度后重试。";

    /// <summary>AC2: 429 — the only retryable class; the intent key is reused on retry.</summary>
    public const string ProviderRateLimited =
        "Provider 限流（429）：稍等片刻再重试即可，重试会复用同一个意图键，不会重复接受 Run。";

    /// <summary>AC3: the preflight verdict for a chapter with no pages (never INVALID_REQUEST).</summary>
    public const string EmptyChapter = "本章没有可处理的页面：请先导入页面（或在章节里补页）再开始翻译。";

    /// <summary>AC4: shown next to the start action, independent of any failure.</summary>
    public const string RestartHintShort = RestartHint;

    /// <summary>
    /// Maps a Host/Core error code to the user-visible sentence. Unknown codes keep their code so a
    /// failure stays diagnosable (same discipline as <c>RunStatusMonitor.StepErrorText</c>).
    /// </summary>
    public static string ForCode(string? code)
    {
        if (string.IsNullOrWhiteSpace(code))
        {
            return ProviderNotConfigured;
        }

        return code.Trim().ToUpperInvariant() switch
        {
            "PROVIDER_NOT_CONFIGURED" => ProviderNotConfigured,
            "PROVIDER_AUTH_FAILED" => ProviderAuthFailed,
            "PROVIDER_RATE_LIMITED" or "RATE_LIMITED" => ProviderRateLimited,
            "INVALID_REQUEST" or "INVALID_INPUT" => RequestRejectedRaw,
            _ => $"{code.Trim()}（未识别的错误码，请连同此码反馈）",
        };
    }
}
