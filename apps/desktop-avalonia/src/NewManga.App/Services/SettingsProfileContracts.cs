using System.Text;
using System.Text.Json;
using NewManga.CoreClient.Commands;

namespace NewManga.App.Services;

/// <summary>
/// SETTINGS-PROFILE-UI-1: UI-facing contracts for the P15 provider/network profile faces plus the
/// provider-binding slot and network default. These records contain only non-secret profile fields
/// (the Core never returns a credential secret; profile rows expose <c>credential_state</c> only).
/// </summary>
public static class SettingsCapabilities
{
    public const string Ocr = "OCR";
    public const string Translation = "Translation";
    public const string Inpaint = "Inpaint";
    public const string Detection = "Detection";
    public const string Rendering = "Rendering";

    /// <summary>The exact capability vocabulary the frozen Core validates (<c>CAPABILITY_NAMES</c>).</summary>
    public static readonly IReadOnlyList<string> All = new[] { Ocr, Translation, Inpaint, Detection, Rendering };
}

public static class NetworkModes
{
    public const string Direct = "Direct";
    public const string System = "System";
    public const string Http = "HTTP";
    public const string Https = "HTTPS";
    public const string Socks5 = "SOCKS5";

    /// <summary>The exact mode vocabulary the frozen Core validates (<c>mode_map</c>).</summary>
    public static readonly IReadOnlyList<string> All = new[] { Direct, System, Http, Https, Socks5 };

    public static bool RequiresProxyEndpoint(string mode) =>
        mode is Http or Https or Socks5;
}

/// <summary>One provider profile row (Core <c>settings_provider_profiles_list</c> projection).</summary>
public sealed record ProviderProfileInfo(
    string ProfileId,
    string ProviderId,
    string DisplayName,
    IReadOnlyList<string> Capabilities,
    string Endpoint,
    string Model,
    string? NetworkProfileId,
    bool Enabled,
    string CredentialState)
{
    public string DisplayText =>
        $"{DisplayName} · {ProviderId} · {string.Join("/", Capabilities)} · {(Enabled ? "enabled" : "disabled")}";
}

/// <summary>Editable provider-profile fields (mirrors the legacy Tauri command arguments).</summary>
public sealed record ProviderProfileDraft(
    string ProviderId,
    string DisplayName,
    IReadOnlyList<string> Capabilities,
    string Endpoint,
    string Model,
    string? NetworkProfileId,
    bool Enabled);

/// <summary>One network profile row (Core <c>settings_network_profiles_list</c> projection).</summary>
public sealed record NetworkProfileInfo(
    string NetworkProfileId,
    string DisplayName,
    string Mode,
    string? ProxyEndpoint,
    bool VerifyTls,
    string TlsVerificationState,
    bool AllowProxyFailureDirectFallback,
    string CredentialState)
{
    public string DisplayText =>
        $"{DisplayName} · {Mode}" +
        (string.IsNullOrEmpty(ProxyEndpoint) ? string.Empty : " · " + ProxyEndpoint) +
        (VerifyTls ? " · TLS" : " · TLS-off") +
        " · " + CredentialState;
}

/// <summary>
/// Editable network-profile fields. <see cref="VerifyTls"/>/<see cref="AllowFallback"/> are nullable
/// because the Core treats them as optional on create and required on update; the UI always sends
/// explicit values, and <see cref="ConfirmDisableTlsVerification"/> mirrors the legacy boolean.
/// </summary>
public sealed record NetworkProfileDraft(
    string DisplayName,
    string Mode,
    string? ProxyEndpoint,
    bool VerifyTls,
    bool ConfirmDisableTlsVerification,
    bool AllowProxyFailureDirectFallback);

/// <summary>Provider-binding scope (P15 <c>BindingScope</c>: global | book | chapter).</summary>
public sealed record ProfileBindingScope(string Kind, string? BookId = null, string? ChapterId = null)
{
    public const string Global = "global";
    public const string Book = "book";
    public const string Chapter = "chapter";

    public static readonly IReadOnlyList<string> Kinds = new[] { Global, Book, Chapter };

    public string DisplayText => Kind switch
    {
        Global => "全局（global）",
        Book => $"书籍（book: {BookId}）",
        Chapter => $"章节（chapter: {ChapterId}）",
        _ => Kind,
    };
}

public enum SettingsProfileStatus
{
    /// <summary>Operation completed (created/updated/deleted/default set/test passed…).</summary>
    Success,

    NotFound,
    Conflict,
    InvalidArguments,
    TlsConfirmationRequired,
    Unavailable,
    NotReady,
    Failed,
}

public sealed record SettingsProfileResult(
    SettingsProfileStatus Status,
    string? ErrorCode = null,
    string? Message = null)
{
    public bool IsSuccess => Status == SettingsProfileStatus.Success;

    public static SettingsProfileResult Success(string? message = null) => new(SettingsProfileStatus.Success, null, message);

    public static SettingsProfileResult NotReady() =>
        new(SettingsProfileStatus.NotReady, "HOST_NOT_READY", "Host 未就绪");
}

/// <summary>One diagnostic stage of <c>settings_network_profiles_test</c> (real Core probe result).</summary>
public sealed record NetworkTestStageInfo(string Stage, string Status, string? Reason, int? DurationMs);

/// <summary>Typed view of the Core network test result (never fabricated: comes from the command).</summary>
public sealed record NetworkTestInfo(
    string Status,
    string? FailedStage,
    bool DirectFallbackUsed,
    IReadOnlyList<NetworkTestStageInfo> Stages)
{
    public string Summary =>
        $"status={Status}" +
        (string.IsNullOrEmpty(FailedStage) ? string.Empty : $", failed_stage={FailedStage}") +
        $", direct_fallback={DirectFallbackUsed}" +
        ", " + string.Join(
            "; ",
            Stages.Select(stage =>
                $"{stage.Stage}:{stage.Status}" +
                (string.IsNullOrEmpty(stage.Reason) ? string.Empty : $"({stage.Reason})") +
                (stage.DurationMs is { } ms ? $" {ms}ms" : string.Empty)));
}

/// <summary>Typed view of <c>settings_network_profile_resolve</c>.</summary>
public sealed record NetworkResolveInfo(string? NetworkProfileId, string Mode, string Source)
{
    public string Summary => $"network_profile_id={NetworkProfileId ?? "(none)"} · mode={Mode} · source={Source}";
}

/// <summary>Result of one provider-binding set/clear (what the Core confirmed).</summary>
public sealed record ProviderBindingResult(bool IsCleared, string? ProfileId, string? Capability, string? Source);

/// <summary>
/// SETTINGS-PROFILE-UI-1: exact dispatcher payloads for the P15 profile commands. The dispatcher
/// re-validates every key (missing/typed-wrong arguments become <c>INVALID_ARGUMENTS</c> before any
/// Core frame), so the UI payload must mirror the legacy Tauri signatures exactly.
/// </summary>
public static class SettingsProfilePayload
{
    public static JsonElement ProviderCreate(ProviderProfileDraft draft) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("provider_id", draft.ProviderId);
        writer.WriteString("display_name", draft.DisplayName);
        WriteCapabilities(writer, draft.Capabilities);
        writer.WriteString("endpoint", draft.Endpoint);
        writer.WriteString("model", draft.Model);
        WriteNullableString(writer, "network_profile_id", draft.NetworkProfileId);
        writer.WriteBoolean("enabled", draft.Enabled);
        writer.WriteEndObject();
    });

    public static JsonElement ProviderUpdate(string profileId, ProviderProfileDraft draft) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("profile_id", profileId);
        writer.WriteString("display_name", draft.DisplayName);
        WriteCapabilities(writer, draft.Capabilities);
        writer.WriteString("endpoint", draft.Endpoint);
        writer.WriteString("model", draft.Model);
        WriteNullableString(writer, "network_profile_id", draft.NetworkProfileId);
        writer.WriteBoolean("enabled", draft.Enabled);
        writer.WriteEndObject();
    });

    public static JsonElement ProviderDelete(string profileId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("profile_id", profileId);
        writer.WriteEndObject();
    });

    public static JsonElement NetworkCreate(NetworkProfileDraft draft) => BuildNetwork(writer =>
    {
        writer.WriteString("display_name", draft.DisplayName);
        writer.WriteString("mode", draft.Mode);
        WriteNullableString(writer, "proxy_endpoint", draft.ProxyEndpoint);
        writer.WriteBoolean("verify_tls", draft.VerifyTls);
        writer.WriteBoolean("confirm_disable_tls_verification", draft.ConfirmDisableTlsVerification);
        writer.WriteBoolean("allow_proxy_failure_direct_fallback", draft.AllowProxyFailureDirectFallback);
    });

    public static JsonElement NetworkUpdate(string networkProfileId, NetworkProfileDraft draft) => BuildNetwork(writer =>
    {
        writer.WriteString("network_profile_id", networkProfileId);
        writer.WriteString("display_name", draft.DisplayName);
        writer.WriteString("mode", draft.Mode);
        WriteNullableString(writer, "proxy_endpoint", draft.ProxyEndpoint);
        writer.WriteBoolean("verify_tls", draft.VerifyTls);
        writer.WriteBoolean("confirm_disable_tls_verification", draft.ConfirmDisableTlsVerification);
        writer.WriteBoolean("allow_proxy_failure_direct_fallback", draft.AllowProxyFailureDirectFallback);
    });

    public static JsonElement NetworkDelete(string networkProfileId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("network_profile_id", networkProfileId);
        writer.WriteEndObject();
    });

    public static JsonElement NetworkTest(string networkProfileId, string providerProfileId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("network_profile_id", networkProfileId);
        writer.WriteString("provider_profile_id", providerProfileId);
        writer.WriteEndObject();
    });

    public static JsonElement NetworkResolve(string? providerProfileId) => Build(writer =>
    {
        writer.WriteStartObject();
        if (!string.IsNullOrWhiteSpace(providerProfileId))
        {
            writer.WriteString("provider_profile_id", providerProfileId);
        }

        writer.WriteEndObject();
    });

    public static JsonElement NetworkDefaultSet(string networkProfileId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("network_profile_id", networkProfileId);
        writer.WriteEndObject();
    });

    public static JsonElement Empty() => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteEndObject();
    });

    public static JsonElement BindingSet(ProfileBindingScope scope, string capability, string profileId) => Build(writer =>
    {
        writer.WriteStartObject();
        WriteScope(writer, scope);
        writer.WriteString("capability", capability);
        writer.WriteString("profile_id", profileId);
        writer.WriteEndObject();
    });

    public static JsonElement BindingClear(ProfileBindingScope scope, string capability) => Build(writer =>
    {
        writer.WriteStartObject();
        WriteScope(writer, scope);
        writer.WriteString("capability", capability);
        writer.WriteEndObject();
    });

    public static JsonElement BindingResolve(string capability) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("capability", capability);
        writer.WriteEndObject();
    });

    private static void WriteCapabilities(Utf8JsonWriter writer, IReadOnlyList<string> capabilities)
    {
        writer.WritePropertyName("capabilities");
        writer.WriteStartArray();
        foreach (var capability in capabilities)
        {
            writer.WriteStringValue(capability);
        }

        writer.WriteEndArray();
    }

    private static void WriteScope(Utf8JsonWriter writer, ProfileBindingScope scope)
    {
        writer.WritePropertyName("scope");
        writer.WriteStartObject();
        writer.WriteString("kind", scope.Kind);
        if (scope.Kind == ProfileBindingScope.Book)
        {
            writer.WriteString("book_id", scope.BookId);
        }
        else if (scope.Kind == ProfileBindingScope.Chapter)
        {
            writer.WriteString("chapter_id", scope.ChapterId);
        }

        writer.WriteEndObject();
    }

    private static void WriteNullableString(Utf8JsonWriter writer, string property, string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            writer.WriteNull(property);
        }
        else
        {
            writer.WriteString(property, value);
        }
    }

    private static JsonElement BuildNetwork(Action<Utf8JsonWriter> write) => Build(writer =>
    {
        writer.WriteStartObject();
        write(writer);
        writer.WriteEndObject();
    });

    private static JsonElement Build(Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            write(writer);
        }

        using var document = JsonDocument.Parse(Encoding.UTF8.GetString(stream.ToArray()));
        return document.RootElement.Clone();
    }
}

/// <summary>SETTINGS-PROFILE-UI-1: maps Core/Host typed failures onto UI-renderable profile outcomes.</summary>
public static class SettingsProfileResultMapper
{
    public static SettingsProfileResult MapCode(string? code, string? message = null) => code switch
    {
        "SETTINGS_ITEM_NOT_FOUND" or "SETTINGS_NOT_FOUND" => new(SettingsProfileStatus.NotFound, code, message),
        "SETTINGS_CONFLICT" => new(SettingsProfileStatus.Conflict, code, message),
        "SETTINGS_INVALID_INPUT" or "INVALID_ARGUMENTS" => new(SettingsProfileStatus.InvalidArguments, code, message),
        "TLS_CONFIRMATION_REQUIRED" => new(SettingsProfileStatus.TlsConfirmationRequired, code, message),
        "SETTINGS_UNAVAILABLE" or "HOST_READ_ONLY" => new(SettingsProfileStatus.Unavailable, code, message),
        "HOST_NOT_READY" => new(SettingsProfileStatus.NotReady, code, message),
        _ => new(SettingsProfileStatus.Failed, code ?? "SETTINGS_PROFILE_FAILED", message),
    };

    public static SettingsProfileResult MapException(Exception exception)
    {
        if (exception is HostCommandInvalidArgumentsException)
        {
            return MapCode("INVALID_ARGUMENTS", "参数不符合 Host 契约");
        }

        if (exception is HostCommandNotSupportedException)
        {
            return new SettingsProfileResult(SettingsProfileStatus.Unavailable, "SETTINGS_PROFILE_UNAVAILABLE");
        }

        var code = exception.GetType().GetProperty("Code")?.GetValue(exception)?.ToString();
        return MapCode(code);
    }
}
