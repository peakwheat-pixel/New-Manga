using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// NS-WIRE-B2 AC1/AC2/AC3: the final nine NOT_SUPPORTED commands are Core-backed with the route +
/// minor proven by verification/NS-RECLASSIFY-1, really execute against the frozen sidecars (a
/// projected result or a typed domain error — both prove the handler ran), and reject bad arguments
/// at the dispatcher boundary before any frame reaches the Core. The two credential commands were
/// BLOCKED here and are unblocked by CREDENTIAL-PORT-1 (Host OS vault + Core BindProfileCredential/
/// ClearProfileCredential); this file now asserts they are Host-local implemented.
/// </summary>
public sealed class CommandWiringB2Tests
{
    private static readonly Dictionary<string, (string CoreCommand, int Minor)> B2Routes = new(StringComparer.Ordinal)
    {
        ["backup_restore"] = ("backup.restore", 3),
        ["settings_provider_profiles_create"] = ("settings_provider_profiles_create", 7),
        ["settings_provider_profiles_update"] = ("settings_provider_profiles_update", 7),
        ["settings_provider_profiles_delete"] = ("settings_provider_profiles_delete", 7),
        ["settings_provider_bindings_set"] = ("settings_provider_bindings_set", 7),
        ["settings_network_profiles_test"] = ("settings_network_profiles_test", 7),
        ["settings_network_profile_resolve"] = ("settings_network_profile_resolve", 7),
        ["library_delete_books_permanently"] = ("PermanentlyDeleteBooks", 10),
        ["list_region_revisions"] = ("list_region_revisions", 3),
    };

    private static readonly string[] CredentialCommands = { "credential_clear", "credential_put" };

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
    }

    [Fact]
    public void Registry_B2Commands_AreCoreBackedWithProbedMinor()
    {
        // Derived: every registered command is implemented (V11R-F0-1 appends
        // the Region write batch on top of the frozen legacy 66).
        Assert.Equal(
            HostCommandRegistry.All.Count,
            HostCommandRegistry.All.Values.Count(command => command.IsImplemented));
        Assert.Equal(0, HostCommandRegistry.All.Values.Count(command => !command.IsImplemented));

        foreach (var (name, expected) in B2Routes)
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.True(descriptor.IsImplemented, $"{name} must be IMPLEMENTED after NS-WIRE-B2");
            Assert.Equal(HostCommandChannel.CoreService, descriptor.Channel);
            Assert.Equal(expected.CoreCommand, descriptor.CoreCommand);
            Assert.Equal(expected.Minor, descriptor.CoreMinor);
            Assert.Null(descriptor.Reason);
        }

        // CREDENTIAL-PORT-1 unblocked the pair: Host-local (OS vault + Core bind/clear), no BLOCKED reason.
        foreach (var name in CredentialCommands)
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.True(descriptor.IsImplemented, $"{name} must be IMPLEMENTED after CREDENTIAL-PORT-1");
            Assert.Equal(HostCommandChannel.HostLocal, descriptor.Channel);
            Assert.Null(descriptor.Reason);
        }
    }

    [Fact]
    public void Inventory_B2Commands_IsWrittenAsEvidence()
    {
        var rows = new List<object>();
        foreach (var name in B2Routes.Keys.Concat(CredentialCommands).OrderBy(item => item, StringComparer.Ordinal))
        {
            var descriptor = HostCommandRegistry.Get(name);
            rows.Add(new
            {
                command = descriptor.Name,
                domain = descriptor.Domain.ToString().ToLowerInvariant(),
                status = descriptor.Status.ToString(),
                channel = descriptor.Channel.ToString(),
                core_command = descriptor.CoreCommand ?? string.Empty,
                core_minor = descriptor.CoreMinor,
                reason = descriptor.Reason ?? string.Empty,
            });
        }

        Assert.Equal(11, rows.Count);

        SidecarFixture.WriteEvidenceJson("commands/ns-b2-inventory.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1");
            writer.WriteString("base", "verification/NS-RECLASSIFY-1/reclassification.json");
            writer.WriteString(
                "registry",
                $"HostCommandRegistry ({HostCommandRegistry.All.Values.Count(command => command.IsImplemented)}" +
                $" IMPLEMENTED / {HostCommandRegistry.All.Values.Count(command => !command.IsImplemented)}" +
                $" NOT_SUPPORTED of {HostCommandRegistry.All.Count})");
            writer.WriteNumber("commands", rows.Count);
            writer.WriteStartArray("inventory");
            foreach (var row in rows)
            {
                writer.WriteStartObject();
                foreach (var property in row.GetType().GetProperties())
                {
                    var value = property.GetValue(row);
                    if (value is int number)
                    {
                        writer.WriteNumber(property.Name, number);
                    }
                    else
                    {
                        writer.WriteString(property.Name, value?.ToString() ?? string.Empty);
                    }
                }

                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
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

    /// <summary>
    /// A loopback-only fake of one OpenAI-compatible <c>GET /models</c> endpoint. The frozen Core's
    /// network-test probe performs real TCP/HTTP operations, so the only way to assert a *passed*
    /// projection without external network is to serve the models document from 127.0.0.1.
    /// </summary>
    private sealed class FakeModelsEndpoint : IDisposable
    {
        private const string ModelsBody = "{\"data\":[{\"id\":\"ns-wire-b2-probe-model\"}]}";
        private readonly TcpListener _listener;
        private readonly CancellationTokenSource _stop = new();
        private readonly Task _accept;

        public FakeModelsEndpoint()
        {
            _listener = new TcpListener(IPAddress.Loopback, 0);
            _listener.Start();
            Port = ((IPEndPoint)_listener.LocalEndpoint).Port;
            _accept = Task.Run(AcceptAsync);
        }

        public int Port { get; }

        public string Endpoint => $"http://127.0.0.1:{Port}";

        private async Task AcceptAsync()
        {
            while (!_stop.IsCancellationRequested)
            {
                TcpClient client;
                try
                {
                    client = await _listener.AcceptTcpClientAsync(_stop.Token).ConfigureAwait(false);
                }
                catch (Exception)
                {
                    return;
                }

                _ = Task.Run(() => ServeAsync(client));
            }
        }

        private static async Task ServeAsync(TcpClient client)
        {
            using (client)
            {
                try
                {
                    var stream = client.GetStream();
                    var buffer = new byte[8192];
                    // The probe opens a bare TCP connection for its TCP stage and closes it without
                    // sending anything; an empty read is simply answered and dropped.
                    await stream.ReadAsync(buffer).ConfigureAwait(false);
                    var body = Encoding.UTF8.GetBytes(ModelsBody);
                    var head = Encoding.ASCII.GetBytes(
                        "HTTP/1.1 200 OK\r\n" +
                        "Content-Type: application/json\r\n" +
                        $"Content-Length: {body.Length}\r\n" +
                        "Connection: close\r\n\r\n");
                    await stream.WriteAsync(head).ConfigureAwait(false);
                    await stream.WriteAsync(body).ConfigureAwait(false);
                    await stream.FlushAsync().ConfigureAwait(false);
                }
                catch (Exception)
                {
                    // best effort: a closed client is not a test failure
                }
            }
        }

        public void Dispose()
        {
            _stop.Cancel();
            _listener.Stop();
            try
            {
                _accept.Wait(TimeSpan.FromSeconds(2));
            }
            catch (Exception)
            {
                // best effort
            }

            _stop.Dispose();
        }
    }

    [SidecarFact]
    public async Task B2Commands_ExecuteAgainstFrozenCore()
    {
        using var models = new FakeModelsEndpoint();
        await using var context = await CommandTestContext.StartAsync("commands-ns-b2");
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

        // ---- P15 network resolution + provider profile lifecycle ---------------------------
        var resolved = await Run("settings_network_profile_resolve");
        Assert.True(resolved.TryGetProperty("mode", out _), "network resolve must project the route mode");
        Assert.True(resolved.TryGetProperty("source", out _), "network resolve must project the route source");

        var createdNetwork = await Run(
            "settings_network_profiles_create",
            "{\"display_name\":\"NS-WIRE-B2 probe network\",\"mode\":\"Direct\",\"proxy_endpoint\":null}");
        var networkId = createdNetwork.GetProperty("profile").GetProperty("network_profile_id").GetString();
        Assert.False(string.IsNullOrEmpty(networkId));

        var createdProfile = await Run(
            "settings_provider_profiles_create",
            "{\"provider_id\":\"openai-compatible\",\"display_name\":\"NS-WIRE-B2 probe provider\"," +
            $"\"capabilities\":[\"Translation\"],\"endpoint\":\"{models.Endpoint}\"," +
            "\"model\":\"ns-wire-b2-model\",\"network_profile_id\":" + $"\"{networkId}\"," +
            "\"enabled\":true}");
        var profileId = createdProfile.GetProperty("profile").GetProperty("profile_id").GetString();
        Assert.False(string.IsNullOrEmpty(profileId));
        Assert.Equal(
            "NS-WIRE-B2 probe provider",
            createdProfile.GetProperty("profile").GetProperty("display_name").GetString());
        Assert.Contains(
            "Translation",
            createdProfile.GetProperty("profile").GetProperty("capabilities").EnumerateArray()
                .Select(item => item.GetString()));
        Assert.Equal(
            "missing",
            createdProfile.GetProperty("profile").GetProperty("credential_state").GetString());

        var updatedProfile = await Run(
            "settings_provider_profiles_update",
            $"{{\"profile_id\":\"{profileId}\",\"display_name\":\"NS-WIRE-B2 probe provider v2\"," +
            "\"capabilities\":[\"Translation\"]," + $"\"endpoint\":\"{models.Endpoint}\"," +
            "\"model\":\"ns-wire-b2-model-v2\",\"network_profile_id\":null,\"enabled\":true}");
        Assert.Equal(
            "NS-WIRE-B2 probe provider v2",
            updatedProfile.GetProperty("profile").GetProperty("display_name").GetString());
        Assert.Equal(
            "ns-wire-b2-model-v2",
            updatedProfile.GetProperty("profile").GetProperty("model").GetString());

        var binding = await Run(
            "settings_provider_bindings_set",
            $"{{\"scope\":{{\"kind\":\"global\"}},\"capability\":\"Translation\",\"profile_id\":\"{profileId}\"}}");
        Assert.Equal(
            profileId,
            binding.GetProperty("binding").GetProperty("profile_id").GetString());

        // The frozen Core runs real diagnostic stages; the loopback fake makes the projection pass.
        var networkTest = await Run(
            "settings_network_profiles_test",
            $"{{\"network_profile_id\":\"{networkId}\",\"provider_profile_id\":\"{profileId}\"}}");
        Assert.Equal("passed", networkTest.GetProperty("status").GetString());
        Assert.Equal(JsonValueKind.Null, networkTest.GetProperty("failed_stage").ValueKind);
        Assert.Equal(6, networkTest.GetProperty("stages").GetArrayLength());
        Assert.All(
            networkTest.GetProperty("stages").EnumerateArray(),
            stage => Assert.Contains(
                stage.GetProperty("status").GetString(),
                new[] { "passed", "not_applicable" }));

        // Delete is only legal once the binding is gone (the Core guards it with SETTINGS_CONFLICT).
        var clearedBinding = await Run(
            "settings_provider_bindings_clear",
            "{\"scope\":{\"kind\":\"global\"},\"capability\":\"Translation\"}");
        Assert.True(clearedBinding.GetProperty("cleared").GetBoolean());
        var deletedProfile = await Run(
            "settings_provider_profiles_delete",
            $"{{\"profile_id\":\"{profileId}\"}}");
        Assert.True(deletedProfile.GetProperty("deleted").GetBoolean());

        // ---- batch permanent delete (protocol minor 10) -----------------------------------
        var bookOne = await Run("library_create_book", "{\"title\":\"NS-WIRE-B2 batch delete A\"}");
        var bookOneId = bookOne.GetProperty("book_id").GetString();
        var bookTwo = await Run("library_create_book", "{\"title\":\"NS-WIRE-B2 batch delete B\"}");
        var bookTwoId = bookTwo.GetProperty("book_id").GetString();
        Assert.NotEqual(bookOneId, bookTwoId);

        var batch = await Run(
            "library_delete_books_permanently",
            $"{{\"book_ids\":[\"{bookOneId}\"],\"confirmed_book_ids\":[\"{bookOneId}\"]," +
            "\"confirm_count\":1,\"confirm_permanent_delete\":true}");
        Assert.Equal(1, batch.GetProperty("requested_count").GetInt32());
        Assert.Equal(1, batch.GetProperty("completed_count").GetInt32());
        var batchItems = batch.GetProperty("items");
        Assert.Equal(1, batchItems.GetArrayLength());
        Assert.Equal(bookOneId, batchItems[0].GetProperty("book_id").GetString());
        Assert.Equal("deleted", batchItems[0].GetProperty("status").GetString());

        // ---- backup restore (protocol minor 3) --------------------------------------------
        var backup = await Run("backup_create", "{\"backup_type\":\"manual\"}");
        var backupId = backup.GetProperty("backup_id").GetString();
        Assert.False(string.IsNullOrEmpty(backupId));
        var restored = await Run(
            "backup_restore",
            $"{{\"backup_id\":\"{backupId}\",\"confirm_restore\":true}}");
        Assert.Equal(backupId, restored.GetProperty("restored_from").GetString());
        Assert.False(string.IsNullOrEmpty(restored.GetProperty("pre_restore_backup_id").GetString()));
        Assert.True(restored.TryGetProperty("managed_consistency", out _));

        SidecarFixture.WriteEvidenceJson("commands/ns-b2-integration.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2/AC3");
            writer.WriteString("sidecar", "frozen core_service (AC11 unlabelled copy)");
            writer.WriteNumber("wired_commands", B2Routes.Count);
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

    [S4RegionFixtureFact]
    public async Task ListRegionRevisions_ExecutesAgainstRegionFixture()
    {
        Assert.True(S4RegionFixture.TryGet(out var sourceRoot, out var metaPath, out _));
        var metadata = S4RegionFixture.ReadMetadata(metaPath);
        var dataRoot = S4RegionFixture.CopyDurableToDisposable(sourceRoot, "ns-b2-region-revisions");
        var options = S4RegionFixture.CreateCoreOptions("commands-ns-b2-region", dataRoot);
        await using var core = await CoreServiceClient.StartAsync(options);
        var dispatcher = new HostCommandDispatcher(core);

        var result = await dispatcher.InvokeAsync(
            "list_region_revisions",
            Args($"{{\"region_id\":\"{metadata.RegionId}\"}}"));
        Assert.Equal(HostCommandStatus.Implemented, result.Status);
        Assert.Equal(metadata.RegionId, result.Value.GetProperty("region_id").GetString());
        var currentNo = result.Value.GetProperty("current_revision_no").GetInt32();
        Assert.True(currentNo >= 1, "the frozen Core must project the current revision number");
        var revisions = result.Value.GetProperty("revisions");
        Assert.True(revisions.GetArrayLength() >= 1, "the revision history must not be empty");
        Assert.Contains(
            revisions.EnumerateArray(),
            revision => revision.GetProperty("is_current").GetBoolean()
                        && revision.GetProperty("revision_no").GetInt32() == currentNo);

        var frame = core.Wire.Frames.LastOrDefault(candidate =>
            candidate.RequestLine.Contains("\"command\":\"list_region_revisions\"", StringComparison.Ordinal));
        Assert.NotNull(frame);

        SidecarFixture.WriteEvidenceJson("commands/ns-b2-list-region-revisions.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2");
            writer.WriteString("fixture", "S4-CMD-BATCH-1 region fixture (disposable copy)");
            writer.WriteString("region_id", metadata.RegionId);
            writer.WriteNumber("current_revision_no", currentNo);
            writer.WriteNumber("revision_count", revisions.GetArrayLength());
            writer.WriteString("core_command", "list_region_revisions");
            writer.WriteNumber("core_minor", 3);
            writer.WriteString("request_line", frame!.RequestLine);
            writer.WriteString("response_line", frame.ResponseLine);
            writer.WriteEndObject();
        });

        SidecarFixture.TryDeleteDirectory(dataRoot);
    }

    [SidecarFact]
    public async Task B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame()
    {
        await using var context = await CommandTestContext.StartAsync("commands-ns-b2-invalid");
        var framesBefore = context.Core.Wire.Frames.Count;
        var cases = new (string Command, string Args)[]
        {
            ("backup_restore", "{}"),
            ("backup_restore", "{\"backup_id\":\"b1\"}"),
            ("backup_restore", "{\"backup_id\":\"b1\",\"confirm_restore\":\"yes\"}"),
            ("settings_provider_profiles_create", "{\"display_name\":\"x\"}"),
            ("settings_provider_profiles_create", "{\"provider_id\":\"p\",\"display_name\":\"x\",\"capabilities\":[],\"endpoint\":\"http://127.0.0.1:1\",\"model\":\"m\",\"enabled\":true}"),
            ("settings_provider_profiles_create", "{\"provider_id\":\"p\",\"display_name\":\"x\",\"capabilities\":[\"Translation\"],\"endpoint\":\"http://127.0.0.1:1\",\"model\":\"m\",\"enabled\":\"yes\"}"),
            ("settings_provider_profiles_update", "{}"),
            ("settings_provider_profiles_delete", "{}"),
            ("settings_provider_bindings_set", "{\"capability\":\"Translation\"}"),
            ("settings_provider_bindings_set", "{\"scope\":\"global\",\"capability\":\"Translation\",\"profile_id\":\"p\"}"),
            ("settings_network_profiles_test", "{}"),
            ("settings_network_profile_resolve", "{\"provider_profile_id\":5}"),
            ("library_delete_books_permanently", "{}"),
            ("library_delete_books_permanently", "{\"book_ids\":[\"b\"],\"confirmed_book_ids\":[\"b\"]}"),
            ("library_delete_books_permanently", "{\"book_ids\":[],\"confirmed_book_ids\":[],\"confirm_count\":0,\"confirm_permanent_delete\":true}"),
            ("library_delete_books_permanently", "{\"book_ids\":[\"b\"],\"confirmed_book_ids\":[\"b\"],\"confirm_count\":\"1\",\"confirm_permanent_delete\":true}"),
            ("list_region_revisions", "{}"),
            ("list_region_revisions", "{\"region_id\":\"\"}"),
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

        SidecarFixture.WriteEvidenceJson("commands/ns-b2-invalid-arguments.json", writer =>
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
