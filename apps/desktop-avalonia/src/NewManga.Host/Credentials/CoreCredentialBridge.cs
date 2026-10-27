using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Credentials;

/// <summary>
/// CREDENTIAL-PORT-1: production bridge to the frozen Core's P15 credential faces
/// (<c>BindProfileCredential</c> / <c>ClearProfileCredential</c>, protocol minor 7) plus the two
/// profile list reads used for the legacy create/replace conflict check. The Core only ever sees a
/// <c>credential_ref</c> — never the secret.
/// </summary>
public sealed class CoreCredentialBridge : ICoreCredentialBridge
{
    private const int CredentialMinor = 7;

    private readonly CoreServiceClient _core;
    private readonly TimeSpan _timeout;

    public CoreCredentialBridge(CoreServiceClient core, TimeSpan timeout)
    {
        _core = core;
        _timeout = timeout;
    }

    public async Task<bool> IsConfiguredAsync(CredentialTarget target, CancellationToken cancellationToken)
    {
        var command = target.Kind == CredentialTarget.ProviderApiKind
            ? "settings_provider_profiles_list"
            : "settings_network_profiles_list";
        CoreResponse response;
        try
        {
            response = await _core.SendAsync(
                command,
                CredentialMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteEndObject();
                },
                _timeout,
                    cancellationToken)
                .ConfigureAwait(false);
        }
        catch (CoreOperationException ex)
        {
            throw MapCoreError(ex, "CREDENTIAL_STORE_UNAVAILABLE");
        }

        var result = response.Result ?? throw new CredentialPortException(
            "CREDENTIAL_STORE_UNAVAILABLE", $"{command} returned no result");
        if (!result.TryGetProperty("profiles", out var profiles) || profiles.ValueKind != JsonValueKind.Array)
        {
            throw new CredentialPortException("CREDENTIAL_STORE_UNAVAILABLE", $"{command} returned no profiles");
        }

        var ownerProperty = target.Kind == CredentialTarget.ProviderApiKind ? "profile_id" : "network_profile_id";
        foreach (var profile in profiles.EnumerateArray())
        {
            if (profile.ValueKind == JsonValueKind.Object &&
                profile.TryGetProperty(ownerProperty, out var owner) &&
                owner.ValueKind == JsonValueKind.String &&
                string.Equals(owner.GetString(), target.OwnerId, StringComparison.Ordinal))
            {
                return profile.TryGetProperty("credential_state", out var state) &&
                       state.ValueKind == JsonValueKind.String &&
                       string.Equals(state.GetString(), "configured", StringComparison.Ordinal);
            }
        }

        throw new CredentialPortException("CREDENTIAL_NOT_FOUND", "profile not found");
    }

    public async Task BindAsync(CredentialTarget target, string credentialRef, CancellationToken cancellationToken)
    {
        CoreResponse response;
        try
        {
            response = await _core.SendAsync(
                "BindProfileCredential",
                CredentialMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WritePropertyName("target");
                    target.WriteWire(writer);
                    writer.WriteString("credential_ref", credentialRef);
                    writer.WriteEndObject();
                },
                _timeout,
                    cancellationToken)
                .ConfigureAwait(false);
        }
        catch (CoreOperationException ex)
        {
            throw MapCoreError(ex, "CREDENTIAL_BIND_FAILED");
        }

        EnsureState(response.Result, "configured", "CREDENTIAL_BIND_FAILED");
    }

    public async Task ClearAsync(CredentialTarget target, CancellationToken cancellationToken)
    {
        CoreResponse response;
        try
        {
            response = await _core.SendAsync(
                "ClearProfileCredential",
                CredentialMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WritePropertyName("target");
                    target.WriteWire(writer);
                    writer.WriteEndObject();
                },
                _timeout,
                    cancellationToken)
                .ConfigureAwait(false);
        }
        catch (CoreOperationException ex)
        {
            throw MapCoreError(ex, "CREDENTIAL_CLEAR_FAILED");
        }

        EnsureState(response.Result, "missing", "CREDENTIAL_CLEAR_FAILED");
    }

    private static CredentialPortException MapCoreError(CoreOperationException error, string fallbackCode) =>
        error.Code switch
        {
            "SETTINGS_ITEM_NOT_FOUND" => new CredentialPortException(
                "CREDENTIAL_NOT_FOUND", "profile not found", error),
            "SETTINGS_INVALID_INPUT" => new CredentialPortException(
                "INVALID_ARGUMENTS", "core rejected the credential target or ref", error),
            _ => new CredentialPortException(fallbackCode, $"core returned {error.Code}", error),
        };

    private static void EnsureState(JsonElement? result, string expected, string failureCode)
    {
        if (result is null)
        {
            throw new CredentialPortException(failureCode, "core returned no result");
        }

        if (result.Value.TryGetProperty("state", out var state) &&
            state.ValueKind == JsonValueKind.String &&
            string.Equals(state.GetString(), expected, StringComparison.Ordinal))
        {
            return;
        }

        throw new CredentialPortException(failureCode, "core returned an unexpected credential state");
    }
}
