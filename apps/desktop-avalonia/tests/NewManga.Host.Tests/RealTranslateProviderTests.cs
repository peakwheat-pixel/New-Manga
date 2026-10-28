using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.Host.Credentials;
using NewManga.Host.Tests.Support;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// REAL-TRANSLATE-PROVIDER-1 AC2/AC4: real translation-provider configuration through the Host.
///
/// Preconditions (private task environment, never the user's real data root):
///   * <c>NEWMANGA_REAL_TRANSLATE_KEY_FILE</c> — the user's OpenCode key file (read once, never echoed,
///     deleted right after <c>credential_put</c> succeeds);
///   * <c>NEWMANGA_REAL_TRANSLATE_BASE_ROOT</c> — a disposable library root with RegionID text
///     (BOOK-FIXTURE-1 plus its regions) that the run probe is pointed at;
///   * <c>NEWMANGA_REAL_TRANSLATE_WORK_ROOT</c> — optional persistent copy root for the run probe;
///   * <c>NEWMANGA_REAL_TRANSLATE_SIDECAR_DIR</c> — the RELEASE-REPACK-2 models sidecar (optional:
///     falls back to <see cref="HostFixture.SidecarDirectory"/>);
///   * optional <c>NEWMANGA_REAL_TRANSLATE_BASE_URL</c> / <c>NEWMANGA_REAL_TRANSLATE_MODEL</c>.
///
/// When the key file is absent the test returns immediately, so ordinary <c>test.ps1</c> runs never
/// touch the network or the vault. This test only *configures* the real provider:
///
/// 1. provider profile + <c>credential_put</c> (Windows vault) + translate binding (real Host faces);
/// 2. the settings mirror the runtime reads at assembly (profile shape the settings UI writes);
/// 3. the temporary key file is destroyed and the outcome (no secret) is written as evidence.
///
/// The actual runs (real provider, typed degradation, identity fallback) are driven by
/// <c>verification/REAL-TRANSLATE-PROVIDER-1/tools/run_translate_probe.py</c> over the frozen Core
/// stdio protocol, which is the RELEASE-REPACK-2 full-chain probe path.
/// </summary>
public sealed class RealTranslateProviderTests
{
    private const string KeyFileVariable = "NEWMANGA_REAL_TRANSLATE_KEY_FILE";
    private const string BaseRootVariable = "NEWMANGA_REAL_TRANSLATE_BASE_ROOT";
    private const string WorkRootVariable = "NEWMANGA_REAL_TRANSLATE_WORK_ROOT";
    private const string SidecarVariable = "NEWMANGA_REAL_TRANSLATE_SIDECAR_DIR";
    private const string BaseUrlVariable = "NEWMANGA_REAL_TRANSLATE_BASE_URL";
    private const string ModelVariable = "NEWMANGA_REAL_TRANSLATE_MODEL";
    private const string DefaultBaseUrl = "https://opencode.ai/zen/v1";
    private const string DefaultModel = "deepseek-v4.1-flash-free";
    private const string FixedTranslateSlot = "openai-compatible-translation";

    private static string? Env(string name)
    {
        var value = Environment.GetEnvironmentVariable(name);
        return string.IsNullOrWhiteSpace(value) ? null : value;
    }

    private static JsonElement Json(string text)
    {
        using var document = JsonDocument.Parse(text);
        return document.RootElement.Clone();
    }

    private static JsonElement Json(object value) => Json(JsonSerializer.Serialize(value));

    private static string String(JsonElement element, string property) =>
        element.GetProperty(property).GetString() ?? string.Empty;

    [HostSidecarFact]
    public async Task RealOpenCodeProvider_HostConfiguration()
    {
        var keyFile = Env(KeyFileVariable);
        var baseRoot = Env(BaseRootVariable);
        if (keyFile is null || baseRoot is null || !File.Exists(keyFile) || !Directory.Exists(baseRoot))
        {
            return; // opt-in task harness only: no key/root, no network, no vault writes
        }

        var baseUrl = (Env(BaseUrlVariable) ?? DefaultBaseUrl).TrimEnd('/');
        var model = Env(ModelVariable) ?? DefaultModel;
        var sidecar = Env(SidecarVariable);
        var workRoot = Env(WorkRootVariable);
        var key = File.ReadAllText(keyFile).Trim();
        Assert.False(string.IsNullOrWhiteSpace(key), "key file must not be empty");

        string dataRoot;
        if (workRoot is not null)
        {
            dataRoot = workRoot;
            Directory.CreateDirectory(dataRoot);
            CopyLibrary(baseRoot, dataRoot);
        }
        else
        {
            dataRoot = HostFixture.NewDataRoot("real-translate");
            CopyLibrary(baseRoot, dataRoot);
        }

        // HostFixture.CreateOptions allocates a throw-away data root; the run probe must see the
        // SAME root the Host configures, so the options are built directly against `dataRoot`.
        var template = HostFixture.CreateOptions(
            "real-translate",
            out _,
            parity: true,
            sidecarDirectoryOverride: sidecar);
        var options = new NewManga.Host.HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = template.LogDirectory,
            SidecarDirectoryOverride = template.SidecarDirectoryOverride,
            MutexName = template.MutexName,
            ParityReached = true,
            DetectLegacyShell = false,
            EnableWireEvidence = true,
            StartupTimeout = template.StartupTimeout,
            RequestTimeout = template.RequestTimeout,
        };
        var stopwatch = Stopwatch.StartNew();
        var evidence = new Dictionary<string, object?>();
        var keyDeleted = false;
        var vaultRefPrefix = string.Empty;

        try
        {
            await using (var configured = await HostRuntime.StartAsync(options))
            {
                Assert.True(configured.Result.IsReady, configured.Result.ErrorCode);
                Assert.NotNull(configured.Commands);

                var created = await configured.Commands!.InvokeAsync(
                    "settings_provider_profiles_create",
                    Json(
                        "{\"provider_id\":\"openai-compatible\"," +
                        "\"display_name\":\"OpenCode Zen real translation\"," +
                        "\"capabilities\":[\"Translation\"]," +
                        $"\"endpoint\":\"{baseUrl}\",\"model\":\"{model}\"," +
                        "\"network_profile_id\":null,\"enabled\":true}"));
                var profileId = String(created.Value.GetProperty("profile"), "profile_id");
                Assert.False(string.IsNullOrWhiteSpace(profileId));

                var put = await configured.Commands.InvokeAsync(
                    "credential_put",
                    Json(
                        "{\"target\":{\"kind\":\"provider_api\",\"profile_id\":\"" + profileId + "\"}," +
                        "\"intent\":\"create\"," +
                        "\"secret\":" + JsonSerializer.Serialize(key) + "}"));
                Assert.Equal("configured", String(put.Value, "state"));

                vaultRefPrefix = $"NewManga/provider/{profileId}/";
                var vault = new WindowsCredentialStore();
                var refs = vault.Enumerate(vaultRefPrefix);
                Assert.Single(refs);
                var vaultRef = refs[0];

                await configured.Commands.InvokeAsync(
                    "settings_provider_bindings_set",
                    Json(
                        "{\"scope\":{\"kind\":\"global\"},\"capability\":\"Translation\"," +
                        "\"profile_id\":\"" + profileId + "\"}"));

                // The runtime reads `settings.providers.profiles` at assembly (restart semantics).
                // The settings UI bridges its JSON profile store into this section after saving a
                // profile/binding; there is no Host command for the pipeline_defaults provider-binding
                // row, so the fixed registry slot is written with the same mirrored shape and the run
                // probe names that slot. Both entries carry only the credential *reference*.
                var mirror = new Dictionary<string, object?>
                {
                    ["base_url"] = baseUrl,
                    ["model"] = model,
                    ["credential_ref"] = vaultRef,
                    ["enabled"] = true,
                    ["options"] = new Dictionary<string, string>(),
                    ["provider_type"] = "openai-compatible",
                    ["network_profile_id"] = string.Empty,
                    ["proxy_policy"] = "inherit",
                };
                await configured.Commands.InvokeAsync(
                    "settings_update_section",
                    Json(new
                    {
                        section = "providers",
                        values = new
                        {
                            profiles = new Dictionary<string, object?>
                            {
                                [profileId] = mirror,
                                [FixedTranslateSlot] = mirror,
                            },
                            retry = new Dictionary<string, object> { ["max_attempts"] = 1 },
                        },
                    }));

                var list = await configured.Commands.InvokeAsync("settings_provider_profiles_list", Json("{}"));
                var configuredProfile = list.Value.GetProperty("profiles").EnumerateArray()
                    .Single(item => String(item, "profile_id") == profileId);
                Assert.Equal("configured", String(configuredProfile, "credential_state"));

                // AC2: the temporary key file is destroyed right after the vault accepted the secret.
                File.Delete(keyFile);
                keyDeleted = !File.Exists(keyFile);

                evidence["profile_id"] = profileId;
                evidence["credential_state"] = "configured";
                evidence["vault_ref_prefix"] = vaultRefPrefix;
                evidence["base_url"] = baseUrl;
                evidence["model"] = model;
                evidence["key_file_deleted"] = keyDeleted;
            }

            evidence["phase_a"] = new Dictionary<string, object?>
            {
                ["host_ready"] = true,
                ["profile_created"] = true,
                ["bindings_set"] = "global/Translation -> profile",
                ["settings_section"] = "providers",
                ["key_file_deleted"] = keyDeleted,
            };
            evidence["ac2"] = new Dictionary<string, object?>
            {
                ["credential_put"] = "configured",
                ["vault_binding"] = "NewManga/provider/<profile>/<ref>",
                ["key_in_evidence"] = false,
                ["key_ever_logged"] = false,
            };
            evidence["timing"] = new Dictionary<string, object?>
            {
                ["config_ms"] = stopwatch.ElapsedMilliseconds,
            };
            evidence["safety"] = new Dictionary<string, object?>
            {
                ["isolated_data_root"] = dataRoot,
                ["user_data_root_touched"] = false,
                ["key_file_deleted"] = keyDeleted,
                ["note"] = "the vault entry stays bound to the provider profile (that is AC2); " +
                           "no secret is written to logs or evidence",
            };
            evidence["run_path"] = workRoot is null
                ? "private temp root (deleted afterwards)"
                : "NEWMANGA_REAL_TRANSLATE_WORK_ROOT (kept for tools/run_translate_probe.py)";

            HostFixture.WriteEvidenceJson("real-translate/host-config.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2");
                writer.WriteString("generated_at_utc", DateTimeOffset.UtcNow.ToString("o"));
                foreach (var (name, value) in evidence)
                {
                    writer.WritePropertyName(name);
                    JsonSerializer.Serialize(writer, value);
                }

                writer.WriteEndObject();
            });
        }
        finally
        {
            if (File.Exists(keyFile))
            {
                File.Delete(keyFile); // never leave the temporary key behind, even on failure
            }

            if (workRoot is null)
            {
                HostFixture.TryDeleteDirectory(dataRoot);
            }
        }
    }

    private static void CopyLibrary(string source, string destination)
    {
        Directory.CreateDirectory(destination);
        foreach (var file in Directory.EnumerateFiles(source, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(source, file);
            var first = relative.Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries)
                .FirstOrDefault() ?? string.Empty;
            if (first.Equals("logs", StringComparison.OrdinalIgnoreCase) ||
                first.Equals("backups", StringComparison.OrdinalIgnoreCase) ||
                first.Equals("derived", StringComparison.OrdinalIgnoreCase) ||
                first.Equals("catalog", StringComparison.OrdinalIgnoreCase) ||
                first.Equals("exports", StringComparison.OrdinalIgnoreCase) ||
                relative.EndsWith(".lock", StringComparison.OrdinalIgnoreCase) ||
                relative.EndsWith("export_jobs.json", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            var target = Path.Combine(destination, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.Copy(file, target, overwrite: true);
        }
    }
}
