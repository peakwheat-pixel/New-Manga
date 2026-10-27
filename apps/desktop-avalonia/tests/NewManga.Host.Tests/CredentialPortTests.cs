using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.Host.Credentials;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// CREDENTIAL-PORT-1: Host credential port. The unit tests drive the coordinator with a fake vault +
/// fake Core bridge (fast, no sidecar); the integration test exercises the real two-phase protocol
/// against the frozen sidecars and the real Windows Credential Manager (secrets are random test
/// markers and every entry is deleted in <c>finally</c>).
/// </summary>
public sealed class CredentialPortTests
{
    private const string MarkerSecret = "credential-port-test-secret-9f4a7c2e-DO-NOT-LEAK";

    private static JsonElement Json(string text)
    {
        using var document = JsonDocument.Parse(text);
        return document.RootElement.Clone();
    }

    private static HostCredentialCoordinator NewCoordinator(
        ICredentialStore store,
        ICoreCredentialBridge bridge,
        out string logDirectory)
    {
        logDirectory = Path.Combine(
            Path.GetTempPath(),
            "newmanga-credential-tests",
            "logs-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(logDirectory);
        return new HostCredentialCoordinator(
            bridge,
            store,
            logDirectory,
            () => Enumerable.Repeat((byte)0xAB, 16).ToArray());
    }

    [Fact]
    public async Task Put_CreatesVaultEntry_AndBindsCoreRef_WithLegacyRefFormat()
    {
        var store = new FakeCredentialStore();
        var bridge = new FakeCoreCredentialBridge { Configured = false };
        var coordinator = NewCoordinator(store, bridge, out var logDirectory);
        try
        {
            var result = await coordinator.PutAsync(Json(
                $"{{\"target\":{{\"kind\":\"provider_api\",\"profile_id\":\"profile-1\"}}," +
                "\"intent\":\"create\"," +
                $"\"secret\":\"{MarkerSecret}\"}}"));

            Assert.Equal("configured", result.GetProperty("state").GetString());
            Assert.Single(bridge.BoundRefs);
            Assert.Matches("^NewManga/provider/profile-1/[0-9a-f]{32}$", bridge.BoundRefs[0]);
            Assert.True(store.Exists(bridge.BoundRefs[0]));
            Assert.Equal(MarkerSecret, store.Read(bridge.BoundRefs[0]));

            var evidence = Directory.GetFiles(coordinator.EvidenceDirectory);
            Assert.NotEmpty(evidence);
            foreach (var file in Directory.GetFiles(logDirectory, "*", SearchOption.AllDirectories))
            {
                Assert.DoesNotContain(MarkerSecret, ReadAllTextShared(file), StringComparison.Ordinal);
            }
        }
        finally
        {
            TryDeleteDirectory(logDirectory);
        }
    }

    [Fact]
    public async Task Put_IntentMismatch_IsTypedConflict_AndWritesNothing()
    {
        var store = new FakeCredentialStore();
        var bridge = new FakeCoreCredentialBridge { Configured = true };
        var coordinator = NewCoordinator(store, bridge, out var logDirectory);
        try
        {
            var conflict = await Assert.ThrowsAsync<CredentialPortException>(() => coordinator.PutAsync(Json(
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"profile-1\"}," +
                "\"intent\":\"create\"," +
                $"\"secret\":\"{MarkerSecret}\"}}")));
            Assert.Equal("CREDENTIAL_CONFLICT", conflict.Code);
            Assert.Empty(store.Entries);
            Assert.Empty(bridge.BoundRefs);

            bridge.Configured = false;
            var replaceConflict = await Assert.ThrowsAsync<CredentialPortException>(() => coordinator.PutAsync(Json(
                "{\"target\":{\"kind\":\"proxy_auth\",\"network_profile_id\":\"net-1\"}," +
                "\"intent\":\"replace\"," +
                $"\"secret\":\"{MarkerSecret}\"}}")));
            Assert.Equal("CREDENTIAL_CONFLICT", replaceConflict.Code);
            Assert.Empty(store.Entries);
        }
        finally
        {
            TryDeleteDirectory(logDirectory);
        }
    }

    [Fact]
    public async Task Put_BindFailure_DeletesVaultEntry_NoOrphan()
    {
        var store = new FakeCredentialStore();
        var bridge = new FakeCoreCredentialBridge
        {
            Configured = false,
            BindFailure = new CredentialPortException("CREDENTIAL_NOT_FOUND", "profile not found"),
        };
        var coordinator = NewCoordinator(store, bridge, out var logDirectory);
        try
        {
            var error = await Assert.ThrowsAsync<CredentialPortException>(() => coordinator.PutAsync(Json(
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"profile-1\"}," +
                "\"intent\":\"create\"," +
                $"\"secret\":\"{MarkerSecret}\"}}")));
            Assert.Equal("CREDENTIAL_NOT_FOUND", error.Code);
            Assert.Empty(store.Entries);
            Assert.DoesNotContain(MarkerSecret, error.ToString(), StringComparison.Ordinal);
        }
        finally
        {
            TryDeleteDirectory(logDirectory);
        }
    }

    [Fact]
    public async Task Clear_ClearsCoreAndRemovesLeftoverVaultEntries()
    {
        var store = new FakeCredentialStore();
        store.Store("NewManga/provider/profile-1/deadbeef", "leftover");
        var bridge = new FakeCoreCredentialBridge { Configured = true };
        var coordinator = NewCoordinator(store, bridge, out var logDirectory);
        try
        {
            var result = await coordinator.ClearAsync(Json(
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"profile-1\"}}"));

            Assert.Equal("missing", result.GetProperty("state").GetString());
            Assert.Single(bridge.Cleared);
            Assert.Empty(store.Entries);
            var evidence = Directory.GetFiles(coordinator.EvidenceDirectory, "clear-*.json").Single();
            Assert.Contains("\"orphans_removed\": 1", File.ReadAllText(evidence), StringComparison.Ordinal);
        }
        finally
        {
            TryDeleteDirectory(logDirectory);
        }
    }

    [Fact]
    public async Task InvalidTargets_AreRejectedBeforeAnyVaultWrite()
    {
        var store = new FakeCredentialStore();
        var bridge = new FakeCoreCredentialBridge();
        var coordinator = NewCoordinator(store, bridge, out var logDirectory);
        try
        {
            var cases = new[]
            {
                "{\"target\":{\"kind\":\"unknown\",\"profile_id\":\"p\"},\"intent\":\"create\",\"secret\":\"s\"}",
                "{\"target\":{\"kind\":\"provider_api\"},\"intent\":\"create\",\"secret\":\"s\"}",
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"a/b\"},\"intent\":\"create\",\"secret\":\"s\"}",
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"p\",\"extra\":true},\"intent\":\"create\",\"secret\":\"s\"}",
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"p\"},\"intent\":\"bogus\",\"secret\":\"s\"}",
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"p\"},\"intent\":\"create\",\"secret\":\"\"}",
                "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"p\"},\"intent\":\"create\"}",
            };
            foreach (var payload in cases)
            {
                var error = await Assert.ThrowsAsync<CredentialPortException>(
                    () => coordinator.PutAsync(Json(payload)));
                Assert.Equal("INVALID_ARGUMENTS", error.Code);
            }

            Assert.Empty(store.Entries);
            Assert.Empty(bridge.BoundRefs);
        }
        finally
        {
            TryDeleteDirectory(logDirectory);
        }
    }

    [Fact]
    public void VaultPrefix_MatchesCoreMakeCredentialRef()
    {
        // Core's ports.providers.credentials.make_credential_ref: NewManga/<kind>/<name>.
        Assert.Equal("NewManga/provider/profile-1", new CredentialTarget("provider_api", "profile-1").VaultPrefix);
        Assert.Equal("NewManga/proxy/net-1", new CredentialTarget("proxy_auth", "net-1").VaultPrefix);
    }

    [HostSidecarFact]
    public async Task CredentialPutAndClear_AgainstFrozenSidecar_FullChain()
    {
        var options = HostFixture.CreateOptions("credential-port", out var dataRoot, parity: true);
        var vault = new WindowsCredentialStore();
        var createdProfiles = new List<string>();
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.NotNull(runtime.Commands);
            Assert.NotNull(runtime.Credentials);

            var created = await runtime.Commands!.InvokeAsync(
                "settings_provider_profiles_create",
                Json("{\"provider_id\":\"openai-compatible\",\"display_name\":\"CREDENTIAL-PORT-1 probe\"," +
                     "\"capabilities\":[\"Translation\"],\"endpoint\":\"http://127.0.0.1:1\"," +
                     "\"model\":\"credential-port-model\",\"network_profile_id\":null,\"enabled\":true}"));
            var profileId = created.Value.GetProperty("profile").GetProperty("profile_id").GetString()!;
            createdProfiles.Add(profileId);

            var put = await runtime.Commands.InvokeAsync(
                "credential_put",
                Json($"{{\"target\":{{\"kind\":\"provider_api\",\"profile_id\":\"{profileId}\"}}," +
                     "\"intent\":\"create\"," +
                     $"\"secret\":\"{MarkerSecret}\"}}"));
            Assert.Equal(HostCommandChannel.HostLocal, put.Channel);
            Assert.Equal("configured", put.Value.GetProperty("state").GetString());

            var prefix = $"NewManga/provider/{profileId}/";
            var refs = vault.Enumerate(prefix);
            Assert.Single(refs);
            Assert.Matches("^NewManga/provider/.+/[0-9a-f]{32}$", refs[0]);
            Assert.Equal(MarkerSecret, vault.Read(refs[0]));

            var configuredList = await runtime.Commands.InvokeAsync(
                "settings_provider_profiles_list",
                Json("{}"));
            var configuredProfile = configuredList.Value.GetProperty("profiles").EnumerateArray()
                .Single(profile => profile.GetProperty("profile_id").GetString() == profileId);
            Assert.Equal("configured", configuredProfile.GetProperty("credential_state").GetString());

            var conflict = await Assert.ThrowsAsync<CredentialPortException>(() => runtime.Commands.InvokeAsync(
                "credential_put",
                Json($"{{\"target\":{{\"kind\":\"provider_api\",\"profile_id\":\"{profileId}\"}}," +
                     "\"intent\":\"create\"," +
                     $"\"secret\":\"{MarkerSecret}\"}}")));
            Assert.Equal("CREDENTIAL_CONFLICT", conflict.Code);

            var clear = await runtime.Commands.InvokeAsync(
                "credential_clear",
                Json($"{{\"target\":{{\"kind\":\"provider_api\",\"profile_id\":\"{profileId}\"}}}}"));
            Assert.Equal("missing", clear.Value.GetProperty("state").GetString());
            Assert.Empty(vault.Enumerate(prefix));

            var missingList = await runtime.Commands.InvokeAsync(
                "settings_provider_profiles_list",
                Json("{}"));
            var missingProfile = missingList.Value.GetProperty("profiles").EnumerateArray()
                .Single(profile => profile.GetProperty("profile_id").GetString() == profileId);
            Assert.Equal("missing", missingProfile.GetProperty("credential_state").GetString());

            var unknown = await Assert.ThrowsAsync<CredentialPortException>(() => runtime.Commands.InvokeAsync(
                "credential_put",
                Json("{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"missing-profile\"}," +
                     "\"intent\":\"create\"," +
                     $"\"secret\":\"{MarkerSecret}\"}}")));
            Assert.Equal("CREDENTIAL_NOT_FOUND", unknown.Code);
            Assert.Empty(vault.Enumerate("NewManga/provider/missing-profile/"));

            // AC3: the marker secret must not appear in any host log/evidence file. The Host is
            // still running, so host.log is read through a shared-read stream instead of File.ReadAllText.
            var leak = new List<string>();
            foreach (var file in Directory.GetFiles(options.LogDirectory, "*", SearchOption.AllDirectories))
            {
                if (ReadAllTextShared(file).Contains(MarkerSecret, StringComparison.Ordinal))
                {
                    leak.Add(file);
                }
            }

            Assert.Empty(leak);

            HostFixture.WriteEvidenceJson("credentials/credential-port.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC4");
                writer.WriteString("profile_id", profileId);
                writer.WriteString("put_state", "configured");
                writer.WriteString("clear_state", "missing");
                writer.WriteBoolean("vault_ref_format_matched", true);
                writer.WriteString("vault_ref_prefix", prefix);
                writer.WriteBoolean("conflict_code_typed", true);
                writer.WriteBoolean("unknown_profile_code_typed", true);
                writer.WriteBoolean("vault_entries_after_clear", vault.Enumerate(prefix).Count == 0);
                writer.WriteBoolean("secret_leak_scan_clean", leak.Count == 0);
                writer.WriteString("generated_at_utc", DateTimeOffset.UtcNow.ToString("o"));
                writer.WriteEndObject();
            });

            foreach (var id in createdProfiles)
            {
                await runtime.Commands.InvokeAsync(
                    "settings_provider_profiles_delete",
                    Json($"{{\"profile_id\":\"{id}\"}}"));
            }
        }
        finally
        {
            foreach (var leftover in vault.Enumerate($"NewManga/provider/{createdProfiles.FirstOrDefault()}/"))
            {
                try
                {
                    vault.Delete(leftover);
                }
                catch (CredentialStoreException)
                {
                }
            }

            TryDeleteDirectory(dataRoot);
        }
    }

    /// <summary>Reads a file even while another process keeps it open (Host logs stay locked).</summary>
    private static string ReadAllTextShared(string path)
    {
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
        using var reader = new StreamReader(stream);
        return reader.ReadToEnd();
    }

    private static void TryDeleteDirectory(string directory)
    {
        try
        {
            if (Directory.Exists(directory))
            {
                Directory.Delete(directory, recursive: true);
            }
        }
        catch (IOException)
        {
        }
    }

    private sealed class FakeCredentialStore : ICredentialStore
    {
        private readonly Dictionary<string, string> _entries = new(StringComparer.Ordinal);

        public IReadOnlyDictionary<string, string> Entries => _entries;

        public bool Exists(string targetName) => _entries.ContainsKey(targetName);

        public void Store(string targetName, string secret)
        {
            if (_entries.ContainsKey(targetName))
            {
                throw new CredentialStoreException("ALREADY_EXISTS", targetName);
            }

            _entries[targetName] = secret;
        }

        public string Read(string targetName) =>
            _entries.TryGetValue(targetName, out var value)
                ? value
                : throw new CredentialStoreException("NOT_FOUND", targetName);

        public void Delete(string targetName)
        {
            if (!_entries.Remove(targetName))
            {
                throw new CredentialStoreException("NOT_FOUND", targetName);
            }
        }

        public IReadOnlyList<string> Enumerate(string prefix) =>
            _entries.Keys.Where(key => key.StartsWith(prefix, StringComparison.Ordinal)).OrderBy(key => key, StringComparer.Ordinal).ToArray();
    }

    private sealed class FakeCoreCredentialBridge : ICoreCredentialBridge
    {
        public bool Configured { get; set; }

        public Exception? BindFailure { get; set; }

        public Exception? ClearFailure { get; set; }

        public List<string> BoundRefs { get; } = new();

        public List<CredentialTarget> Cleared { get; } = new();

        public Task<bool> IsConfiguredAsync(CredentialTarget target, CancellationToken cancellationToken) =>
            Task.FromResult(Configured);

        public Task BindAsync(CredentialTarget target, string credentialRef, CancellationToken cancellationToken)
        {
            if (BindFailure is not null)
            {
                throw BindFailure;
            }

            BoundRefs.Add(credentialRef);
            return Task.CompletedTask;
        }

        public Task ClearAsync(CredentialTarget target, CancellationToken cancellationToken)
        {
            if (ClearFailure is not null)
            {
                throw ClearFailure;
            }

            Cleared.Add(target);
            return Task.CompletedTask;
        }
    }
}
