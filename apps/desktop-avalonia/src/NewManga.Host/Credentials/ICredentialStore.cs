using System.Text.Json;

namespace NewManga.Host.Credentials;

/// <summary>Typed credential-port failure. Codes are stable, UI-renderable, and never contain a secret.</summary>
public sealed class CredentialPortException : Exception
{
    public CredentialPortException(string code, string detail, Exception? inner = null)
        : base($"[{code}] {detail}", inner)
    {
        Code = code;
    }

    /// <summary>One of CREDENTIAL_* / INVALID_ARGUMENTS.</summary>
    public string Code { get; }
}

/// <summary>A vault failure. Codes are stable and secret-free.</summary>
public sealed class CredentialStoreException : Exception
{
    public CredentialStoreException(string code, string detail, int? win32Error = null, Exception? inner = null)
        : base($"[{code}] {detail}", inner)
    {
        Code = code;
        Win32Error = win32Error;
    }

    public string Code { get; }

    public int? Win32Error { get; }
}

/// <summary>
/// CREDENTIAL-PORT-1 AC1: the Host-side protected credential store port. Only opaque vault target
/// names flow through it; secrets are written and read from the OS vault (Windows Credential
/// Manager) by the concrete adapter, never by the Core and never to disk/logs from this layer.
/// </summary>
public interface ICredentialStore
{
    /// <summary>True when the vault holds a secret under <paramref name="targetName"/>.</summary>
    bool Exists(string targetName);

    /// <summary>Stores <paramref name="secret"/> under <paramref name="targetName"/>; throws when the target exists.</summary>
    void Store(string targetName, string secret);

    /// <summary>Reads the secret back (tests/verification only; production never logs or returns it).</summary>
    string Read(string targetName);

    /// <summary>Deletes the target; throws <c>NOT_FOUND</c> when it does not exist.</summary>
    void Delete(string targetName);

    /// <summary>Lists vault target names starting with <paramref name="prefix"/> (orphan checks only).</summary>
    IReadOnlyList<string> Enumerate(string prefix);
}

/// <summary>
/// CREDENTIAL-PORT-1 AC1: the Core half of the two-phase protocol. The Core only ever receives a
/// <c>credential_ref</c> that the Host minted after writing the secret into the OS vault; it binds
/// or clears that ref on the profile and (on clear) deletes the vault entry itself.
/// </summary>
public interface ICoreCredentialBridge
{
    Task<bool> IsConfiguredAsync(CredentialTarget target, CancellationToken cancellationToken);

    Task BindAsync(CredentialTarget target, string credentialRef, CancellationToken cancellationToken);

    Task ClearAsync(CredentialTarget target, CancellationToken cancellationToken);
}

/// <summary>
/// The legacy P15 credential target: a provider API key (provider profile) or a proxy password
/// (network profile). Kept wire-compatible with the old Tauri <c>P15CredentialTarget</c>.
/// </summary>
public sealed record CredentialTarget(string Kind, string OwnerId)
{
    public const string ProviderApiKind = "provider_api";
    public const string ProxyAuthKind = "proxy_auth";

    /// <summary>Vault kind segment used by Core's <c>make_credential_ref</c>.</summary>
    public string VaultKind => Kind == ProviderApiKind ? "provider" : "proxy";

    /// <summary>Canonical vault prefix <c>NewManga/&lt;kind&gt;/&lt;owner&gt;</c> (identical to Core's refs).</summary>
    public string VaultPrefix => $"NewManga/{VaultKind}/{OwnerId}";

    /// <summary>Wire object for <c>BindProfileCredential</c> / <c>ClearProfileCredential</c>.</summary>
    public void WriteWire(Utf8JsonWriter writer)
    {
        writer.WriteStartObject();
        writer.WriteString("kind", Kind);
        if (Kind == ProviderApiKind)
        {
            writer.WriteString("profile_id", OwnerId);
        }
        else
        {
            writer.WriteString("network_profile_id", OwnerId);
        }

        writer.WriteEndObject();
    }

    public static CredentialTarget Parse(Utf8JsonReader reader)
    {
        throw new NotSupportedException("use Parse(JsonElement)");
    }

    public static CredentialTarget Parse(System.Text.Json.JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            throw Invalid("target must be an object");
        }

        ThrowIfUnknownKeys(value, "kind", "profile_id", "network_profile_id");
        var kind = OptionalString(value, "kind") ?? throw Invalid("target.kind is required");
        return kind switch
        {
            ProviderApiKind => new CredentialTarget(kind, RequiredOwner(value, "profile_id")),
            ProxyAuthKind => new CredentialTarget(kind, RequiredOwner(value, "network_profile_id")),
            _ => throw Invalid("target.kind must be provider_api or proxy_auth"),
        };
    }

    private static string RequiredOwner(System.Text.Json.JsonElement value, string property)
    {
        var owner = OptionalString(value, property) ?? throw Invalid($"target.{property} is required");
        if (owner.Length == 0 || owner.Length > 200 ||
            owner.Contains('/') || owner.Contains('\\') ||
            owner.Any(char.IsControl) || owner != owner.Trim())
        {
            throw Invalid($"target.{property} is not a safe profile id");
        }

        return owner;
    }

    private static string? OptionalString(System.Text.Json.JsonElement value, string property) =>
        value.TryGetProperty(property, out var element) && element.ValueKind != JsonValueKind.Null
            ? element.ValueKind == JsonValueKind.String
                ? element.GetString()
                : throw Invalid($"target.{property} must be a string")
            : null;

    private static void ThrowIfUnknownKeys(System.Text.Json.JsonElement value, params string[] allowed)
    {
        var allowedSet = allowed.ToHashSet(StringComparer.Ordinal);
        foreach (var property in value.EnumerateObject())
        {
            if (!allowedSet.Contains(property.Name))
            {
                throw Invalid($"unknown target key: {property.Name}");
            }
        }
    }

    private static CredentialPortException Invalid(string detail) =>
        new("INVALID_ARGUMENTS", detail);
}
