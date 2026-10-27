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
        Assert.Equal(55, HostCommandRegistry.All.Values.Count(command => command.IsImplemented));
        Assert.Equal(11, HostCommandRegistry.All.Values.Count(command => !command.IsImplemented));

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
        Assert.Equal(66, HostCommandRegistry.All.Count);
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
}
