using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.Host.Credentials;
using NewManga.CoreClient.Wire;

namespace NewManga.Host;

/// <summary>
/// CREDENTIAL-PORT-1 AC2/AC3: Host command face for <c>credential_put</c>/<c>credential_clear</c>.
///
/// Two-phase protocol (mirrors the legacy Tauri <c>settings_bridge.rs:288-350</c>):
///   put:   validate target/intent → mint <c>NewManga/&lt;kind&gt;/&lt;owner&gt;/&lt;nonce&gt;</c> → write the secret
///          into the OS vault → <c>BindProfileCredential(ref)</c>; any failure deletes the vault entry
///          (no orphan credential ever outlives a failed put).
///   clear: <c>ClearProfileCredential(target)</c> (the Core clears the profile ref AND deletes the
///          vault entry) → Host deletes any leftover refs under the target prefix (defense in depth),
///          so both ends are clean; failures stay typed.
///
/// The secret only travels App→Host inside the command payload; the Core receives the opaque ref.
/// Evidence never contains the secret or the vault ref suffix.
/// </summary>
public sealed class HostCredentialCoordinator
{
    public const string PutCommand = "credential_put";
    public const string ClearCommand = "credential_clear";

    private const int MaxSecretLength = 4096;

    private readonly ICoreCredentialBridge _bridge;
    private readonly ICredentialStore _store;
    private readonly string _evidenceDirectory;
    private readonly Func<byte[]> _nonce;

    public HostCredentialCoordinator(
        ICoreCredentialBridge bridge,
        ICredentialStore store,
        string logDirectory,
        Func<byte[]>? nonce = null)
    {
        _bridge = bridge;
        _store = store;
        _evidenceDirectory = Path.Combine(logDirectory, "credentials");
        _nonce = nonce ?? (() =>
        {
            var bytes = new byte[16];
            RandomNumberGenerator.Fill(bytes);
            return bytes;
        });
        Directory.CreateDirectory(_evidenceDirectory);
    }

    public string EvidenceDirectory => _evidenceDirectory;

    /// <summary>Dispatcher entry point for the two Host-local credential commands.</summary>
    public async Task<HostCommandResult> HandleCommandAsync(
        string name,
        JsonElement payload,
        CancellationToken cancellationToken)
    {
        var value = name switch
        {
            PutCommand => await PutAsync(payload, cancellationToken).ConfigureAwait(false),
            ClearCommand => await ClearAsync(payload, cancellationToken).ConfigureAwait(false),
            _ => throw new HostCommandNotSupportedException(HostCommandRegistry.Get(name)),
        };
        return new HostCommandResult(name, HostCommandStatus.Implemented, HostCommandChannel.HostLocal, value);
    }

    public async Task<JsonElement> PutAsync(JsonElement payload, CancellationToken cancellationToken = default)
    {
        var target = ParseTarget(payload);
        var intent = ReadIntent(payload);
        var secret = ReadSecret(payload);

        var configuredBefore = await _bridge.IsConfiguredAsync(target, cancellationToken).ConfigureAwait(false);
        if (intent == "create" && configuredBefore)
        {
            throw new CredentialPortException("CREDENTIAL_CONFLICT", "a credential is already configured for this profile");
        }

        if (intent == "replace" && !configuredBefore)
        {
            throw new CredentialPortException("CREDENTIAL_CONFLICT", "no credential is configured for this profile");
        }

        var credentialRef = $"{target.VaultPrefix}/{ToHex(_nonce())}";
        try
        {
            _store.Store(credentialRef, secret);
        }
        catch (CredentialStoreException ex)
        {
            throw new CredentialPortException("CREDENTIAL_STORE_UNAVAILABLE", "the OS credential store is unavailable", ex);
        }

        try
        {
            await _bridge.BindAsync(target, credentialRef, cancellationToken).ConfigureAwait(false);
        }
        catch
        {
            // AC2: a failed bind must not leave an orphan vault entry behind.
            TryDelete(credentialRef);
            throw;
        }

        WriteEvidence("put", target, intent: intent, configuredBefore: configuredBefore);
        return BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("state", "configured");
            writer.WriteEndObject();
        });
    }

    public async Task<JsonElement> ClearAsync(JsonElement payload, CancellationToken cancellationToken = default)
    {
        var target = ParseTarget(payload);
        await _bridge.ClearAsync(target, cancellationToken).ConfigureAwait(false);

        // AC2: the Core clears the profile ref and deletes the vault entry; remove any leftover refs
        // under the target prefix as defense in depth (count reported, no secret in evidence).
        var removed = 0;
        foreach (var leftover in _store.Enumerate(target.VaultPrefix + "/"))
        {
            if (TryDelete(leftover))
            {
                removed++;
            }
        }

        WriteEvidence("clear", target, removed: removed);
        return BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("state", "missing");
            writer.WriteEndObject();
        });
    }

    private static CredentialTarget ParseTarget(JsonElement payload)
    {
        if (payload.ValueKind != JsonValueKind.Object ||
            !payload.TryGetProperty("target", out var target) ||
            target.ValueKind != JsonValueKind.Object)
        {
            throw new CredentialPortException("INVALID_ARGUMENTS", "target is required");
        }

        return CredentialTarget.Parse(target);
    }

    private static string ReadIntent(JsonElement payload)
    {
        if (!payload.TryGetProperty("intent", out var intent) || intent.ValueKind != JsonValueKind.String)
        {
            throw new CredentialPortException("INVALID_ARGUMENTS", "intent is required (create|replace)");
        }

        return intent.GetString() switch
        {
            "create" => "create",
            "replace" => "replace",
            _ => throw new CredentialPortException("INVALID_ARGUMENTS", "intent must be create or replace"),
        };
    }

    private static string ReadSecret(JsonElement payload)
    {
        if (!payload.TryGetProperty("secret", out var secret) || secret.ValueKind != JsonValueKind.String)
        {
            throw new CredentialPortException("INVALID_ARGUMENTS", "secret is required");
        }

        var value = secret.GetString() ?? string.Empty;
        if (value.Length == 0)
        {
            throw new CredentialPortException("INVALID_ARGUMENTS", "secret must not be empty");
        }

        if (value.Length > MaxSecretLength)
        {
            throw new CredentialPortException("INVALID_ARGUMENTS", "secret is too long");
        }

        return value;
    }

    private void WriteEvidence(
        string operation,
        CredentialTarget target,
        string? intent = null,
        bool? configuredBefore = null,
        int? removed = null)
    {
        var path = Path.Combine(_evidenceDirectory, $"{operation}-{DateTime.UtcNow:yyyyMMddTHHmmssfffffffZ}.json");
        // RELEASE-REPACK-3: build the evidence JSON with Utf8JsonWriter instead of
        // reflection-based JsonSerializer.Serialize so the trimmed Release publish has no
        // IL2026/RequiresUnreferencedCode diagnostics (Debug builds did not surface it).
        // Indented output keeps the human-readable evidence format the tests assert.
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true }))
        {
            writer.WriteStartObject();
            writer.WriteString("operation", operation);
            writer.WriteString("target_kind", target.Kind);
            writer.WriteString("owner_hash", ToHex(SHA256.HashData(Encoding.UTF8.GetBytes(target.OwnerId)))[..16]);
            writer.WriteString("intent", intent);
            writer.WriteBoolean("configured_before", configuredBefore ?? false);
            writer.WriteString("state", operation == "put" ? "configured" : "missing");
            writer.WriteNumber("orphans_removed", removed ?? 0);
            writer.WriteString("generated_at_utc", DateTimeOffset.UtcNow.ToString("o"));
            writer.WriteEndObject();
        }

        File.WriteAllText(path, System.Text.Encoding.UTF8.GetString(stream.ToArray()));
    }

    private bool TryDelete(string credentialRef)
    {
        try
        {
            _store.Delete(credentialRef);
            return true;
        }
        catch (CredentialStoreException)
        {
            return false;
        }
    }

    private static string ToHex(byte[] bytes) => Convert.ToHexString(bytes).ToLowerInvariant();

    private static JsonElement BuildJson(Action<Utf8JsonWriter> write)
    {
        var line = WireJson.Write(write);
        using var document = JsonDocument.Parse(line);
        return document.RootElement.Clone();
    }
}
