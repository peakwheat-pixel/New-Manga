using System.Text;
using System.Text.Json;
using NewManga.CoreClient.Commands;

namespace NewManga.App.Services;

/// <summary>
/// CREDENTIAL-UI-1: UI-facing credential contracts. These records never contain a secret — only the
/// typed target identity, the Core-reported <c>credential_state</c> (configured/missing) and typed error
/// codes, exactly what the settings page may render and what tests/evidence may record.
/// </summary>
public static class CredentialKinds
{
    /// <summary>Provider API key target (<c>target.profile_id</c>).</summary>
    public const string ProviderApi = "provider_api";

    /// <summary>Proxy password target (<c>target.network_profile_id</c>).</summary>
    public const string ProxyAuth = "proxy_auth";
}

/// <summary>One selectable credential target (profile id + display label + Core credential state).</summary>
public sealed record CredentialTargetOption(
    string Kind,
    string OwnerId,
    string DisplayName,
    string CredentialState)
{
    public bool IsConfigured => string.Equals(CredentialState, "configured", StringComparison.Ordinal);

    public string KindLabel => Kind == CredentialKinds.ProviderApi ? "Provider API Key" : "代理密码";

    public string StateLabel => IsConfigured ? "configured" : "missing";

    /// <summary>Combo-box row: label + state, never a secret.</summary>
    public string DisplayText => $"{KindLabel} · {DisplayName} · {StateLabel}";
}

public enum CredentialOperationStatus
{
    /// <summary>Put succeeded: Core bound the opaque ref (state=configured).</summary>
    Configured,

    /// <summary>Clear succeeded: Core state is missing and vault leftovers are gone.</summary>
    Cleared,

    /// <summary>CREDENTIAL_CONFLICT: intent does not match the current configured state.</summary>
    Conflict,

    /// <summary>CREDENTIAL_NOT_FOUND: the target profile does not exist (or was deleted).</summary>
    NotFound,

    /// <summary>INVALID_ARGUMENTS: the Host rejected target/intent/secret.</summary>
    InvalidArguments,

    /// <summary>CREDENTIAL_STORE_UNAVAILABLE: OS vault or Core bridge unavailable.</summary>
    Unavailable,

    /// <summary>Host is not ready yet (no Core connection).</summary>
    NotReady,

    /// <summary>Any other typed failure; <see cref="CredentialOperationResult.ErrorCode"/> is stable.</summary>
    Failed,
}

/// <summary>Typed result of one credential operation; safe to render and record.</summary>
public sealed record CredentialOperationResult(
    CredentialOperationStatus Status,
    string? ErrorCode = null,
    string? Message = null)
{
    public bool IsSuccess => Status is CredentialOperationStatus.Configured or CredentialOperationStatus.Cleared;

    public static CredentialOperationResult Configured() => new(CredentialOperationStatus.Configured);

    public static CredentialOperationResult Cleared() => new(CredentialOperationStatus.Cleared);

    public static CredentialOperationResult NotReady() =>
        new(CredentialOperationStatus.NotReady, "HOST_NOT_READY", "Host 未就绪");
}

/// <summary>
/// CREDENTIAL-UI-1: exact command payloads for <c>credential_put</c>/<c>credential_clear</c>.
/// The secret is written only into this transient <see cref="JsonElement"/> (the Host command channel
/// needs it); it is never logged, persisted, recorded in evidence or echoed by the UI.
/// </summary>
public static class CredentialCommandPayload
{
    public static JsonElement BuildPut(string kind, string ownerId, string intent, string secret)
    {
        if (string.IsNullOrEmpty(secret))
        {
            throw new ArgumentException("secret must not be empty", nameof(secret));
        }

        return Build(writer =>
        {
            writer.WriteStartObject();
            WriteTarget(writer, kind, ownerId);
            writer.WriteString("intent", intent);
            writer.WriteString("secret", secret);
            writer.WriteEndObject();
        });
    }

    public static JsonElement BuildClear(string kind, string ownerId) => Build(writer =>
    {
        writer.WriteStartObject();
        WriteTarget(writer, kind, ownerId);
        writer.WriteEndObject();
    });

    private static void WriteTarget(Utf8JsonWriter writer, string kind, string ownerId)
    {
        writer.WritePropertyName("target");
        writer.WriteStartObject();
        writer.WriteString("kind", kind);
        writer.WriteString(kind == CredentialKinds.ProviderApi ? "profile_id" : "network_profile_id", ownerId);
        writer.WriteEndObject();
    }

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

/// <summary>CREDENTIAL-UI-1: maps Host/Core typed failures onto UI-renderable credential outcomes.</summary>
public static class CredentialResultMapper
{
    public static CredentialOperationResult MapCode(string? code, string? message = null) => code switch
    {
        "CREDENTIAL_CONFLICT" => new(CredentialOperationStatus.Conflict, code, message),
        "CREDENTIAL_NOT_FOUND" => new(CredentialOperationStatus.NotFound, code, message),
        "CREDENTIAL_STORE_UNAVAILABLE" or "CREDENTIAL_CLEAR_FAILED" or "CREDENTIAL_BIND_FAILED" or
            "CREDENTIAL_STORE_FAILED" or "HOST_READ_ONLY" =>
            new(CredentialOperationStatus.Unavailable, code, message),
        "INVALID_ARGUMENTS" => new(CredentialOperationStatus.InvalidArguments, code, message),
        "HOST_NOT_READY" => new(CredentialOperationStatus.NotReady, code, message),
        _ => new(CredentialOperationStatus.Failed, code ?? "CREDENTIAL_FAILED", message),
    };

    /// <summary>Maps a dispatcher/credential exception without ever touching its message secret-free body.</summary>
    public static CredentialOperationResult MapException(Exception exception) => exception switch
    {
        HostCredentialFailure failure => MapCode(failure.Code, failure.Detail),
        HostCommandInvalidArgumentsException => MapCode("INVALID_ARGUMENTS", "参数不符合 Host 契约"),
        HostCommandNotSupportedException => new(CredentialOperationStatus.Unavailable, "CREDENTIAL_COMMAND_UNAVAILABLE"),
        _ => MapCode(ErrorCodeOf(exception) ?? "CREDENTIAL_FAILED"),
    };

    private static string? ErrorCodeOf(Exception exception)
    {
        var property = exception.GetType().GetProperty("Code");
        return property?.GetValue(exception)?.ToString();
    }
}

/// <summary>
/// CREDENTIAL-UI-1: host-side credential failure mirrored into the App assembly so the App never
/// references the Host's internal types. Kept tiny on purpose: only the stable code + detail.
/// </summary>
public sealed class HostCredentialFailure : Exception
{
    public HostCredentialFailure(string code, string? detail = null)
        : base($"[{code}] {detail}")
    {
        Code = code;
        Detail = detail;
    }

    public string Code { get; }

    public string? Detail { get; }
}
