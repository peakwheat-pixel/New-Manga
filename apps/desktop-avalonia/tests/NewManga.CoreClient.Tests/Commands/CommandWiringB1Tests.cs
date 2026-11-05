using System.Text.Json;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// NS-WIRE-B1 AC1/AC2/AC3: the thirteen high-confidence NOT_SUPPORTED commands wired in batch B1 are
/// Core-backed with the exact route/minor proven by verification/NS-RECLASSIFY-1, really execute
/// against the frozen sidecars (success or a typed domain error — both prove the handler ran), and
/// reject bad arguments at the dispatcher boundary before any frame reaches the Core.
/// </summary>
public sealed class CommandWiringB1Tests
{
    private static readonly Dictionary<string, (string CoreCommand, int Minor)> B1Routes = new(StringComparer.Ordinal)
    {
        ["backup_delete"] = ("backup.delete", 3),
        ["cleanup_retry_pending"] = ("cleanup.retry_pending", 3),
        ["plugins_audit_list"] = ("plugins.audit_list", 3),
        ["plugins_set_plugin_enabled"] = ("plugins.set_plugin_enabled", 3),
        ["library_delete_book_permanently"] = ("PermanentlyDeleteBook", 10),
        ["settings_network_profile_default_clear"] = ("settings_network_profile_default_clear", 7),
        ["settings_network_profile_default_set"] = ("settings_network_profile_default_set", 7),
        ["settings_network_profiles_create"] = ("settings_network_profiles_create", 7),
        ["settings_network_profiles_delete"] = ("settings_network_profiles_delete", 7),
        ["settings_network_profiles_update"] = ("settings_network_profiles_update", 7),
        ["settings_provider_bindings_clear"] = ("settings_provider_bindings_clear", 7),
        ["settings_provider_bindings_resolve"] = ("settings_provider_bindings_resolve", 7),
        ["settings_provider_run_snapshot_get"] = ("settings_provider_run_snapshot_get", 7),
    };

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
    }

    [Fact]
    public void Registry_B1Commands_AreCoreBackedWithProbedMinor()
    {
        // CREDENTIAL-PORT-1 migrated the last two commands (credential_put/clear):
        // every registered command is implemented. Totals are DERIVED from the
        // registry (V11R-F0-1 appends the Region write batch).
        Assert.Equal(
            HostCommandRegistry.All.Count,
            HostCommandRegistry.All.Values.Count(command => command.IsImplemented));
        Assert.Equal(0, HostCommandRegistry.All.Values.Count(command => !command.IsImplemented));

        foreach (var (name, expected) in B1Routes)
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.True(descriptor.IsImplemented, $"{name} must be IMPLEMENTED after NS-WIRE-B1");
            Assert.Equal(HostCommandChannel.CoreService, descriptor.Channel);
            Assert.Equal(expected.CoreCommand, descriptor.CoreCommand);
            Assert.Equal(expected.Minor, descriptor.CoreMinor);
        }
    }

    [Fact]
    public void Registry_B1Commands_StayInTheSixDomainSurface()
    {
        // Derived: the six domains partition the registry exactly once.
        Assert.Equal(
            HostCommandRegistry.All.Count,
            Enum.GetValues<HostCommandDomain>()
                .Sum(domain => HostCommandRegistry.ForDomain(domain).Count));
        Assert.All(B1Routes.Keys, name =>
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.Equal(descriptor, HostCommandRegistry.ForDomain(descriptor.Domain).Single(command => command.Name == name));
        });
    }

    private sealed class CommandTestContext : IAsyncDisposable
    {
        private CommandTestContext(
            SidecarFixture.CommandEnvironment environment,
            CoreServiceClient core,
            HostBridgeClient bridge,
            HostCommandDispatcher dispatcher)
        {
            Environment = environment;
            Core = core;
            Bridge = bridge;
            Dispatcher = dispatcher;
        }

        public SidecarFixture.CommandEnvironment Environment { get; }

        public CoreServiceClient Core { get; }

        public HostBridgeClient Bridge { get; }

        public HostCommandDispatcher Dispatcher { get; }

        public static async Task<CommandTestContext> StartAsync(string name)
        {
            var environment = SidecarFixture.CreateCommandEnvironment(name);
            var core = await CoreServiceClient.StartAsync(environment.CoreOptions);
            try
            {
                var bridge = await HostBridgeClient.StartAsync(environment.BridgeOptions);
                return new CommandTestContext(environment, core, bridge, new HostCommandDispatcher(core, bridge));
            }
            catch
            {
                await core.DisposeAsync();
                throw;
            }
        }

        public async ValueTask DisposeAsync()
        {
            await Bridge.DisposeAsync();
            await Core.DisposeAsync();
            SidecarFixture.TryDeleteDirectory(Environment.DataRoot);
        }
    }

    [SidecarFact]
    public async Task B1Commands_ExecuteAgainstFrozenCore()
    {
        await using var context = await CommandTestContext.StartAsync("commands-ns-b1");
        var executed = new List<object>();

        async Task<JsonElement> Run(string name, string argsJson = "{}")
        {
            var result = await context.Dispatcher.InvokeAsync(name, Args(argsJson));
            Assert.Equal(HostCommandStatus.Implemented, result.Status);
            Assert.Equal(HostCommandChannel.CoreService, result.Channel);
            var coreCommand = HostCommandRegistry.Get(name).CoreCommand!;
            var frame = context.Core.Wire.Frames.LastOrDefault(candidate =>
                candidate.RequestLine.Contains($"\"command\":\"{coreCommand}\"", StringComparison.Ordinal));
            Assert.NotNull(frame);
            executed.Add(new
            {
                command = name,
                basis = "success",
                core_command = coreCommand,
                request_line = frame!.RequestLine,
            });
            return result.Value;
        }

        void TypedFailure(string name, string coreCommand, string errorCode, CoreOperationException exception)
        {
            Assert.Equal(errorCode, exception.Code);
            var frame = context.Core.Wire.Frames.LastOrDefault(candidate =>
                candidate.RequestLine.Contains($"\"command\":\"{coreCommand}\"", StringComparison.Ordinal));
            Assert.NotNull(frame);
            executed.Add(new
            {
                command = name,
                basis = $"typed_{errorCode}",
                core_command = coreCommand,
                request_line = frame!.RequestLine,
            });
        }

        // ---- backup / cleanup / plugin face ------------------------------------------------
        var backup = await Run("backup_create", "{\"backup_type\":\"manual\"}");
        var backupId = backup.GetProperty("backup_id").GetString();
        Assert.False(string.IsNullOrEmpty(backupId));
        var deletedBackup = await Run("backup_delete", $"{{\"backup_id\":\"{backupId}\"}}");
        Assert.True(deletedBackup.GetProperty("removed").GetBoolean());

        var retried = await Run("cleanup_retry_pending");
        Assert.True(retried.TryGetProperty("removed", out _), "cleanup.retry_pending must project the CleanupOutcome");

        var audit = await Run("plugins_audit_list", "{\"limit\":5}");
        Assert.True(
            audit.ValueKind is JsonValueKind.Object or JsonValueKind.Array,
            "plugins.audit_list must return the audit ledger projection");

        var pluginFailure = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync(
                "plugins_set_plugin_enabled",
                Args("{\"plugin_id\":\"no-such-plugin\",\"enabled\":false}")));
        TypedFailure("plugins_set_plugin_enabled", "plugins.set_plugin_enabled", "PLUGIN_NOT_FOUND", pluginFailure);

        // ---- P15 network profile lifecycle -------------------------------------------------
        var createdProfile = await Run(
            "settings_network_profiles_create",
            "{\"display_name\":\"NS-WIRE-B1 probe network\",\"mode\":\"Direct\",\"proxy_endpoint\":null}");
        var profileId = createdProfile.GetProperty("profile").GetProperty("network_profile_id").GetString();
        Assert.False(string.IsNullOrEmpty(profileId));

        var defaultSet = await Run(
            "settings_network_profile_default_set",
            $"{{\"network_profile_id\":\"{profileId}\"}}");
        Assert.Equal(profileId, defaultSet.GetProperty("network_profile_id").GetString());

        var updatedProfile = await Run(
            "settings_network_profiles_update",
            $"{{\"network_profile_id\":\"{profileId}\",\"display_name\":\"NS-WIRE-B1 probe network v2\"," +
            "\"mode\":\"Direct\",\"proxy_endpoint\":null,\"verify_tls\":true," +
            "\"allow_proxy_failure_direct_fallback\":false}");
        Assert.Equal(
            "NS-WIRE-B1 probe network v2",
            updatedProfile.GetProperty("profile").GetProperty("display_name").GetString());

        var clearedDefault = await Run("settings_network_profile_default_clear");
        Assert.True(clearedDefault.TryGetProperty("network_profile_id", out var clearedId));
        Assert.Equal(JsonValueKind.Null, clearedId.ValueKind);

        var deletedProfile = await Run(
            "settings_network_profiles_delete",
            $"{{\"network_profile_id\":\"{profileId}\"}}");
        Assert.True(deletedProfile.GetProperty("deleted").GetBoolean());

        // ---- provider bindings + typed run snapshot ----------------------------------------
        var bindingsCleared = await Run(
            "settings_provider_bindings_clear",
            "{\"scope\":{\"kind\":\"global\"},\"capability\":\"Translation\"}");
        Assert.True(bindingsCleared.GetProperty("cleared").GetBoolean());

        var resolved = await Run("settings_provider_bindings_resolve", "{\"capability\":\"Translation\"}");
        Assert.True(resolved.TryGetProperty("source", out _), "bindings resolve must return the resolution view");

        var runSnapshotFailure = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync(
                "settings_provider_run_snapshot_get",
                Args("{\"run_id\":\"no-such-run\"}")));
        TypedFailure(
            "settings_provider_run_snapshot_get",
            "settings_provider_run_snapshot_get",
            "TARGET_NOT_FOUND",
            runSnapshotFailure);

        // ---- permanent delete face (protocol minor 10) -------------------------------------
        var book = await Run("library_create_book", "{\"title\":\"NS-WIRE-B1 delete probe\"}");
        var bookId = book.GetProperty("book_id").GetString();
        var deletedBook = await Run(
            "library_delete_book_permanently",
            $"{{\"payload\":{{\"book_id\":\"{bookId}\",\"confirm_permanent_delete\":true}}}}");
        Assert.Equal(bookId, deletedBook.GetProperty("book_id").GetString());
        Assert.True(deletedBook.GetProperty("deleted").GetBoolean());

        SidecarFixture.WriteEvidenceJson("commands/ns-b1-integration.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2");
            writer.WriteString("sidecar", "frozen core_service (AC11 unlabelled copy)");
            writer.WriteNumber("wired_commands", B1Routes.Count);
            writer.WriteNumber("executed", executed.Count);
            writer.WriteStartArray("results");
            foreach (var row in executed)
            {
                writer.WriteStartObject();
                foreach (var property in row.GetType().GetProperties())
                {
                    writer.WriteString(property.Name, property.GetValue(row)!.ToString());
                }

                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    [SidecarFact]
    public async Task B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame()
    {
        await using var context = await CommandTestContext.StartAsync("commands-ns-b1-invalid");
        var framesBefore = context.Core.Wire.Frames.Count;
        var cases = new (string Command, string Args)[]
        {
            ("backup_delete", "{}"),
            ("plugins_set_plugin_enabled", "{\"enabled\":false}"),
            ("plugins_set_plugin_enabled", "{\"plugin_id\":\"p\",\"enabled\":\"yes\"}"),
            ("plugins_audit_list", "{\"limit\":-1}"),
            ("plugins_audit_list", "{\"limit\":\"many\"}"),
            ("library_delete_book_permanently", "{\"book_id\":\"book-1\"}"),
            ("library_delete_book_permanently", "{\"book_id\":\"\",\"confirm_permanent_delete\":true}"),
            ("settings_network_profile_default_set", "{}"),
            ("settings_network_profiles_create", "{\"display_name\":\"x\"}"),
            ("settings_network_profiles_create", "{\"display_name\":\"x\",\"mode\":\"Direct\",\"proxy_endpoint\":5}"),
            ("settings_network_profiles_update", "{\"network_profile_id\":\"p\",\"display_name\":\"x\",\"mode\":\"Direct\"}"),
            ("settings_network_profiles_delete", "{}"),
            ("settings_provider_bindings_clear", "{\"capability\":\"Translation\"}"),
            ("settings_provider_bindings_resolve", "{}"),
            ("settings_provider_run_snapshot_get", "{}"),
        };

        var rejected = new List<object>();
        foreach (var (command, args) in cases)
        {
            var error = await Assert.ThrowsAsync<HostCommandInvalidArgumentsException>(
                () => context.Dispatcher.InvokeAsync(command, Args(args)));
            Assert.Equal("INVALID_ARGUMENTS", error.Code);
            rejected.Add(new { command, args, code = error.Code });
        }

        Assert.Equal(framesBefore, context.Core.Wire.Frames.Count);

        SidecarFixture.WriteEvidenceJson("commands/ns-b1-invalid-arguments.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("cases", rejected.Count);
            writer.WriteNumber("core_frames_before", framesBefore);
            writer.WriteNumber("core_frames_after", context.Core.Wire.Frames.Count);
            writer.WriteBoolean("rejected_before_core", framesBefore == context.Core.Wire.Frames.Count);
            writer.WriteStartArray("cases_detail");
            foreach (var row in rejected)
            {
                writer.WriteStartObject();
                foreach (var property in row.GetType().GetProperties())
                {
                    writer.WriteString(property.Name, property.GetValue(row)!.ToString());
                }

                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------------------------------
    // FEA-12-PREREQ-1 / M2-C1 rev 2.13: the read-only delete preview + the single-delete digest
    // additive fields. Registration only -- the Core runtime does not implement the command yet.
    // The negative control SIMULATES the pre-registration behaviour by removing the 5 rev 2.13
    // codes from the NEW projector's allow-list: they degrade to category=unknown WITHOUT the code
    // being rewritten. (The TRUE baseline had no delete-family allow-list at all -- see
    // verification/FEA-12-PREREQ-1/logs/baseline-negative-control-base-035468a81.log.)
    // ---------------------------------------------------------------------------------------

    private const string DigestA =
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

    private static string WritePayload(string command, string argsJson)
    {
        return NewManga.CoreClient.Wire.WireJson.Write(
            writer => HostCommandDispatcher.WriteCorePayload(command, Args(argsJson), writer));
    }

    private static void AssertInvalidPayload(string command, string argsJson)
    {
        var error = Assert.Throws<HostCommandInvalidArgumentsException>(
            () => WritePayload(command, argsJson));
        Assert.Equal("INVALID_ARGUMENTS", error.Code);
    }

    [Fact]
    public void Fea12_Registry_RegistersDeletePreviewAtTargetWire11_AndKeepsDeleteMinor10()
    {
        var preview = HostCommandRegistry.Get("library_preview_permanent_delete_books");
        Assert.True(preview.IsImplemented);
        Assert.Equal(HostCommandChannel.CoreService, preview.Channel);
        Assert.Equal("PreviewPermanentDeleteBooks", preview.CoreCommand);
        Assert.Equal(11, preview.CoreMinor);
        Assert.Equal(DeleteTrashWireTargets.PreviewPermanentDeleteBooksMinor, preview.CoreMinor);
        Assert.Contains("library_preview_permanent_delete_books", HostCommandRegistry.DeleteTrashCommandNames);
        Assert.Contains("library_preview_permanent_delete_books", HostCommandRegistry.V11RAdditiveCommandNames);
        Assert.True(HostCommandRegistry.IsDeleteTrashCommand("library_preview_permanent_delete_books"));

        // The existing single-delete command keeps its frozen per-command wire minor (10).
        var single = HostCommandRegistry.Get("library_delete_book_permanently");
        Assert.Equal("PermanentlyDeleteBook", single.CoreCommand);
        Assert.Equal(10, single.CoreMinor);

        // Capability registration (contract metadata): the runtime probe belongs to FEA-12-CORE.
        Assert.Equal(
            new[] { DeleteTrashWireTargets.DeletePreviewCapability },
            HostCommandRegistry.RequiredCapabilities("library_preview_permanent_delete_books"));
        Assert.Equal(
            new[]
            {
                "library.delete.preview/1",
                "library.trash.read/1",
                "library.trash.write/1",
            },
            HostCommandRegistry.DeleteTrashCapabilities.OrderBy(capability => capability, StringComparer.Ordinal));
    }

    [Fact]
    public void Fea12_PreviewPayload_WritesFrozenCamelBookIds_AndRejectsOpenShape()
    {
        // The camelCase bookIds key is the frozen C-04b :41 literal and must NOT be normalized.
        var line = WritePayload(
            "library_preview_permanent_delete_books",
            "{\"bookIds\":[\"book-1\",\"book-2\"]}");
        Assert.Contains("\"bookIds\":[\"book-1\",\"book-2\"]", line, StringComparison.Ordinal);
        Assert.DoesNotContain("book_ids", line, StringComparison.Ordinal);

        AssertInvalidPayload("library_preview_permanent_delete_books", "{}");
        AssertInvalidPayload("library_preview_permanent_delete_books", "{\"bookIds\":[]}");
        AssertInvalidPayload("library_preview_permanent_delete_books", "{\"bookIds\":[\"b\",\"b\"]}");
        AssertInvalidPayload("library_preview_permanent_delete_books", "{\"bookIds\":[1]}");
        AssertInvalidPayload(
            "library_preview_permanent_delete_books", "{\"bookIds\":[\"b\"],\"extra\":1}");
        // A snake_case caller is a closed-shape violation, not a silent alias.
        AssertInvalidPayload(
            "library_preview_permanent_delete_books", "{\"book_ids\":[\"b\"]}");
        var tooMany = string.Join(",", Enumerable.Range(0, 21).Select(index => $"\"book-{index}\""));
        AssertInvalidPayload(
            "library_preview_permanent_delete_books", $"{{\"bookIds\":[{tooMany}]}}");
    }

    [Fact]
    public void Fea12_SingleDelete_ForwardsInventoryDigestAdditively_AndNeverSynthesizesIt()
    {
        var withDigest = WritePayload(
            "library_delete_book_permanently",
            $"{{\"payload\":{{\"book_id\":\"book-1\",\"confirm_permanent_delete\":true," +
            $"\"inventory_digest\":\"{DigestA}\"}}}}");
        Assert.Contains(
            $"\"inventory_digest\":\"{DigestA}\"", withDigest, StringComparison.Ordinal);

        // A legacy caller that does not send the additive field is still forwarded unchanged
        // (the new Core fail-closes; the Host must not synthesize a digest).
        var legacy = WritePayload(
            "library_delete_book_permanently",
            "{\"payload\":{\"book_id\":\"book-1\",\"confirm_permanent_delete\":true}}");
        Assert.DoesNotContain("inventory_digest", legacy, StringComparison.Ordinal);

        AssertInvalidPayload(
            "library_delete_book_permanently",
            "{\"book_id\":\"book-1\",\"confirm_permanent_delete\":true,\"inventory_digest\":5}");
    }

    [Fact]
    public void Fea12_DeleteErrorProjection_NegativeControl_UnknownDegradesButCodeIsPreserved()
    {
        // Reconstructed pre-registration allow-list = the NEW projector minus the 5 rev 2.13 codes.
        // NOTE: the true baseline delete family had NO allow-list projection at all (Core errors
        // passed through unchanged); the recorded baseline probe demonstrates the real degradation
        // path with the existing ProjectRunError + its 19-code run allow-list. AC3 conclusion is
        // unchanged (baseline script + frozen-Core live probe are both real).
        var preRegistration = HostCommandRegistry.AllowedDeleteTrashErrorCodes
            .Where(code => !HostCommandRegistry.Fea12DeleteTrashErrorCodes.Contains(code))
            .ToHashSet(StringComparer.Ordinal);
        Assert.DoesNotContain("BOOK_DELETE_STALE_PREVIEW", preRegistration);
        Assert.DoesNotContain("BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE", preRegistration);

        var expected = new[]
        {
            ("BOOK_DELETE_STALE_PREVIEW", "conflict", false),
            ("BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE", "unavailable", true),
        };
        foreach (var (code, category, retryable) in expected)
        {
            // Source taxonomy is deliberately wrong: registration, not the source, is normative.
            var source = new CoreOperationException(code, "internal", false, "raw core message", "req-1");

            var baseline = HostCommandDispatcher.ProjectDeleteTrashError(source, preRegistration);
            Assert.Equal(code, baseline.Code); // the code is NEVER rewritten
            Assert.Equal("unknown", baseline.Category);
            Assert.False(baseline.Retryable);

            var registered = HostCommandDispatcher.ProjectDeleteTrashError(
                source, HostCommandRegistry.AllowedDeleteTrashErrorCodes);
            Assert.Equal(code, registered.Code);
            Assert.Equal(category, registered.Category);
            Assert.Equal(retryable, registered.Retryable);
        }

        // Every existing registered delete code keeps its command-level projection unchanged.
        var existing = new CoreOperationException(
            "BOOK_DELETE_CONFLICT", "conflict", false, "conflict", "req-2");
        Assert.Same(
            existing,
            HostCommandDispatcher.ProjectDeleteTrashError(
                existing, HostCommandRegistry.AllowedDeleteTrashErrorCodes));
    }
}
