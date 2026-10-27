using System.Text.Json;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.CoreClient.Tests.Support;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// AC2/AC3/AC4 execution parity: the migrated commands really run against the frozen sidecars
/// (core_service protocol 2.3 + host_bridge wire v1), Chinese survives the round trip byte-for-byte,
/// and every remaining command fails with a typed NOT_SUPPORTED carrying its reason.
/// </summary>
public sealed class CommandIntegrationTests
{
    public const string ChineseTitle = "\u96fe\u6e2f\u6765\u4fe1\u30fb\u65e5\u672c\u8a9e\u30c6\u30b9\u30c8";

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
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
            Settings = new SettingsCommandService(dispatcher);
            Library = new LibraryCommandService(dispatcher);
            Region = new RegionCommandService(dispatcher);
            Reader = new ReaderCommandService(dispatcher);
            Resource = new ResourceCommandService(dispatcher);
            Workbench = new WorkbenchCommandService(dispatcher);
        }

        public SidecarFixture.CommandEnvironment Environment { get; }

        public CoreServiceClient Core { get; }

        public HostBridgeClient Bridge { get; }

        public HostCommandDispatcher Dispatcher { get; }

        public SettingsCommandService Settings { get; }

        public LibraryCommandService Library { get; }

        public RegionCommandService Region { get; }

        public ReaderCommandService Reader { get; }

        public ResourceCommandService Resource { get; }

        public WorkbenchCommandService Workbench { get; }

        public static async Task<CommandTestContext> StartAsync(string name)
        {
            var environment = SidecarFixture.CreateCommandEnvironment(name);
            var core = await CoreServiceClient.StartAsync(environment.CoreOptions);
            try
            {
                var bridge = await HostBridgeClient.StartAsync(environment.BridgeOptions);
                var dispatcher = new HostCommandDispatcher(core, bridge);
                return new CommandTestContext(environment, core, bridge, dispatcher);
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
    public async Task TwelveImplementedCommands_ExecuteAgainstFrozenSidecars()
    {
        await using var context = await CommandTestContext.StartAsync("commands-integration");
        var results = new List<object>();

        async Task<JsonElement> Run(string name, string argsJson = "{}")
        {
            var result = await context.Dispatcher.InvokeAsync(name, Args(argsJson));
            results.Add(new
            {
                command = name,
                status = result.Status.ToString(),
                channel = result.Channel.ToString(),
                value_kind = result.Value.ValueKind.ToString(),
            });
            return result.Value;
        }

        var ping = await Run("core_ping");
        Assert.Equal("ready", ping.GetProperty("status").GetString());
        Assert.Equal(2, ping.GetProperty("protocol_version").GetProperty("major").GetInt32());
        Assert.Equal(3, ping.GetProperty("protocol_version").GetProperty("minor").GetInt32());

        var books = await Run("library_list_books");
        Assert.Equal(JsonValueKind.Array, books.ValueKind);
        Assert.Equal(0, books.GetArrayLength());

        var recycle = await Run("library_list_recycle_bin_books");
        Assert.Equal(JsonValueKind.Array, recycle.ValueKind);

        var createdBook = await Run("library_create_book", "{\"title\":\"S2 parity probe book\"}");
        var bookId = createdBook.GetProperty("book_id").GetString();
        Assert.False(string.IsNullOrEmpty(bookId));
        var createdChapter = await Run(
            "create_chapter",
            $"{{\"book_id\":\"{bookId}\",\"title\":\"Chapter 1\",\"chapter_number\":\"1\"}}");
        var chapterId = createdChapter.GetProperty("chapter_id").GetString();
        Assert.False(string.IsNullOrEmpty(chapterId));

        await Run("list_chapters", $"{{\"book_id\":\"{bookId}\"}}");
        await Run("list_chapter_pages", $"{{\"chapter_id\":\"{chapterId}\"}}");
        var regions = await Run("list_regions", "{\"page_id\":\"page-1\"}");
        Assert.True(regions.ValueKind is JsonValueKind.Array or JsonValueKind.Object);

        var settings = await Run("settings_get");
        Assert.True(settings.TryGetProperty("settings", out _), "settings.get must return a settings projection");

        var backups = await Run("backup_list");
        Assert.Equal(JsonValueKind.Array, backups.ValueKind);

        var plugins = await Run("plugins_list");
        Assert.True(plugins.TryGetProperty("global_enabled", out _));

        var cleanup = await Run("cleanup_preview");
        Assert.True(cleanup.TryGetProperty("targets", out _));

        var exports = await Run("library_get_export_history");
        Assert.True(exports.TryGetProperty("exports", out _));

        // NS-WIRE-A1 batch A1: settings / plugins / backup / cleanup faces against the frozen Core.
        var settingsUpdated = await Run("settings_update_section", "{\"section\":\"ocr\",\"values\":{}}");
        Assert.True(settingsUpdated.TryGetProperty("settings", out _), "settings.update_section must return the settings projection");
        var providerProfiles = await Run("settings_provider_profiles_list");
        Assert.True(providerProfiles.TryGetProperty("profiles", out _), "provider profiles list must return a profiles array");
        var networkProfiles = await Run("settings_network_profiles_list");
        Assert.True(networkProfiles.TryGetProperty("profiles", out _), "network profiles list must return a profiles array");
        var overrides = await Run("settings_resolve_overrides", "{\"keys\":[\"sfx.policy\"]}");
        Assert.True(overrides.TryGetProperty("values", out _), "resolve_overrides must return resolved values");
        var backupCreated = await Run("backup_create", "{\"backup_type\":\"manual\"}");
        Assert.False(string.IsNullOrEmpty(backupCreated.GetProperty("backup_id").GetString()), "backup.create must return a backup_id");
        var pluginsToggled = await Run("plugins_set_enabled", "{\"enabled\":false}");
        Assert.False(pluginsToggled.GetProperty("global_enabled").GetBoolean(), "plugins.set_enabled must project global_enabled=false");
        var cleanupRun = await Run("cleanup_run");
        Assert.True(cleanupRun.TryGetProperty("removed", out _), "cleanup.run must project the CleanupOutcome");
        // The reader projection success path needs a chapter WITH pages; this fixture data root has
        // none, so the real execution must surface the Core's typed TARGET_NOT_FOUND (routing proof).
        // The success path is covered by verification/NS-WIRE-A1/probe-results.json against BOOK-FIXTURE-1.
        var readerProjectionError = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync(
                "library_get_reader_projection",
                Args($"{{\"chapter_id\":\"{chapterId}\",\"mode\":\"original\",\"start_position\":\"beginning\"}}")));
        Assert.Equal("TARGET_NOT_FOUND", readerProjectionError.Code);

        // RUN-EXPORT-E2E-1: Run/Export control + projection faces really execute against the
        // frozen Core. This fixture root has a book without page artifacts, so StartRun must
        // fail with the Core's typed INVALID_REQUEST (EMPTY_TARGET_SELECTION) and the read
        // commands must surface typed TARGET_NOT_FOUND / EXPORT_NOT_FOUND -- never a silent
        // success. The real production-chain evidence (models sidecar, BOOK-FIXTURE 8 pages,
        // StartRun accepted, run snapshot/task projection, export attempt) is under
        // verification/RUN-EXPORT-E2E-1/probe-*.json.
        var runErrors = new[]
        {
            await Assert.ThrowsAsync<CoreOperationException>(
                () => context.Dispatcher.InvokeAsync(
                    "library_start_run",
                    Args($"{{\"command\":\"translate_untranslated\",\"scope\":{{\"kind\":\"book\",\"book_id\":\"{bookId}\"}},\"overrides\":{{}},\"idempotency_key\":\"it-run-1\"}}"))),
            await Assert.ThrowsAsync<CoreOperationException>(
                () => context.Dispatcher.InvokeAsync("library_get_run_snapshot", Args("{\"run_id\":\"run-missing\"}"))),
            await Assert.ThrowsAsync<CoreOperationException>(
                () => context.Dispatcher.InvokeAsync("library_get_task_projection", Args("{\"run_id\":\"run-missing\"}"))),
            await Assert.ThrowsAsync<CoreOperationException>(
                () => context.Dispatcher.InvokeAsync("library_get_export_snapshot", Args("{\"export_id\":\"export-missing\"}"))),
            await Assert.ThrowsAsync<CoreOperationException>(
                () => context.Dispatcher.InvokeAsync("library_cancel_export", Args("{\"export_id\":\"export-missing\"}"))),
            await Assert.ThrowsAsync<CoreOperationException>(
                () => context.Dispatcher.InvokeAsync(
                    "library_start_export",
                    Args($"{{\"book_id\":\"{bookId}\",\"chapter_ids\":[\"{chapterId}\"],\"ordered_page_ids\":[\"page-missing\"],\"format\":\"pdf\",\"format_options\":{{\"pdf_content\":\"image_only\"}},\"stale_policy\":\"abort\",\"target_ref\":\"etref1.not-registered.probe\"}}"))),
        };
        Assert.All(runErrors, error => Assert.False(string.IsNullOrEmpty(error.Code)));
        Assert.Equal("INVALID_REQUEST", runErrors[0].Code);
        Assert.Equal("TARGET_NOT_FOUND", runErrors[1].Code);
        Assert.Equal("EXPORT_NOT_FOUND", runErrors[3].Code);

        // S4-CMD-BATCH-1: the region write face and the reader progress face. This integration data
        // root has no pages/regions/clean artifacts, so every write surface must surface the Core's
        // typed rejection (routing proof); the success paths are covered against the seeded region
        // fixture by S4RegionReaderCommandTests (scripts/seed_s4_region_fixture.py).
        var setRegionTypeError = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync(
                "set_region_type",
                Args("{\"region_id\":\"missing-region\",\"new_region_type\":\"narration\"}")));
        Assert.Equal("TARGET_NOT_FOUND", setRegionTypeError.Code);

        var restoreRevisionError = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync(
                "restore_region_revision",
                Args("{\"region_id\":\"missing-region\",\"revision_no\":1,\"expected_revision\":1}")));
        Assert.Equal("TARGET_NOT_FOUND", restoreRevisionError.Code);

        var rerenderError = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync("rerender_page", Args("{\"page_id\":\"missing-page\"}")));
        Assert.Equal("TARGET_NOT_FOUND", rerenderError.Code);

        // The resolve face projects a missing page as the route-specific PAGE_NOT_FOUND code
        // (core_service.py handle_resolve_page_resource error mapping), unlike the region writes.
        var resolvePageError = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync("resolve_page_resource", Args("{\"page_id\":\"missing-page\"}")));
        Assert.Equal("PAGE_NOT_FOUND", resolvePageError.Code);

        var saveProgressError = await Assert.ThrowsAsync<CoreOperationException>(
            () => context.Dispatcher.InvokeAsync(
                "library_save_reading_progress",
                Args("{\"chapter_id\":\"missing-chapter\",\"mode\":\"original\",\"page_id\":\"missing-page\"," +
                     "\"scroll_offset_y\":0,\"elapsed_seconds_delta\":1}")));
        Assert.Equal("TARGET_NOT_FOUND", saveProgressError.Code);

        var issued = await Run("issue_resource_url", "{\"resource_id\":\"res-1\",\"revision\":\"rev-1\"}");
        var grantId = issued.GetProperty("id").GetString();
        Assert.False(string.IsNullOrEmpty(grantId));
        Assert.True(issued.GetProperty("size").GetInt64() > 0);
        var grant = await context.Bridge.ResolveAsync(grantId!);
        Assert.Equal("managed-read-only", grant.ScopeClass);
        Assert.Equal("book/page01.jpg", grant.RelPath);

        var revoked = await Run("revoke_ref", $"{{\"opaque_id\":\"{grantId}\"}}");
        Assert.True(revoked.GetProperty("revoked").GetBoolean());
        var revokedError = await Assert.ThrowsAsync<BridgeException>(() => context.Bridge.ResolveAsync(grantId!));
        Assert.Equal("REF_REVOKED", revokedError.Code);

        await Run("issue_resource_url", "{\"resource_id\":\"res-1\",\"revision\":\"rev-2\"}");
        var revokedCount = await Run("revoke_resource_refs", "{\"resource_id\":\"res-1\"}");
        Assert.True(revokedCount.GetProperty("revoked_count").GetInt64() >= 1);

        // Success-path count is unchanged: the five S4-CMD-BATCH-1 write commands cannot succeed on
        // this empty data root, so they are proven by typed rejection here (routing) and by
        // commands/s4-region-reader-results.json against the seeded region fixture (success).
        Assert.Equal(24, results.Count); // 20 core + 4 bridge (issue x2)
        Assert.Equal(20, results.Count(row => row.GetType().GetProperty("channel")!.GetValue(row)!.ToString() == "CoreService"));
        Assert.Equal(4, results.Count(row => row.GetType().GetProperty("channel")!.GetValue(row)!.ToString() == "HostBridge"));

        SidecarFixture.WriteEvidenceJson("commands/integration-results.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2/AC3/AC4");
            writer.WriteNumber("implemented_commands_executed", results.Count);
            writer.WriteNumber("s4_routing_probes", 5);
            writer.WriteNumber("core_service_channel", 20);
            writer.WriteNumber("host_bridge_channel", 4);
            writer.WriteBoolean("all_ok", true);
            writer.WriteStartArray("results");
            foreach (var row in results)
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
    public async Task ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake()
    {
        await using var context = await CommandTestContext.StartAsync("commands-chinese");
        var created = await context.Dispatcher.InvokeAsync(
            "library_create_book",
            Args("{\"title\":\"" + ChineseTitle + "\"}"));
        Assert.Equal(ChineseTitle, created.Value.GetProperty("title").GetString());

        var books = await context.Dispatcher.InvokeAsync("library_list_books");
        var matched = false;
        foreach (var book in books.Value.EnumerateArray())
        {
            if (string.Equals(book.GetProperty("title").GetString(), ChineseTitle, StringComparison.Ordinal))
            {
                matched = true;
                break;
            }
        }

        Assert.True(matched, "created Chinese title must come back exactly through ListBooks");

        var frames = context.Core.Wire.Frames;
        Assert.NotEmpty(frames);
        Assert.True(context.Core.Wire.AllRequestsAsciiOnly);
        var createFrame = frames.First(frame => frame.RequestLine.Contains("\"command\":\"CreateBook\"", StringComparison.Ordinal));
        Assert.Contains("\\u96fe", createFrame.RequestLine, StringComparison.Ordinal);
        Assert.Contains("5c7539366665", createFrame.RequestUtf8Hex, StringComparison.Ordinal);
        Assert.DoesNotContain(ChineseTitle, createFrame.RequestLine, StringComparison.Ordinal);

        SidecarFixture.WriteEvidenceJson("commands/chinese-roundtrip.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4");
            writer.WriteString("command", "library_create_book -> CreateBook");
            writer.WriteString("title_expected", ChineseTitle);
            writer.WriteString("title_received", created.Value.GetProperty("title").GetString());
            writer.WriteBoolean("exact_match", true);
            writer.WriteBoolean("request_ascii_only", createFrame.RequestAsciiOnly);
            writer.WriteString("create_request_line", createFrame.RequestLine);
            writer.WriteString("create_request_utf8_hex", createFrame.RequestUtf8Hex);
            writer.WriteEndObject();
        });
    }

    [SidecarFact]
    public async Task NotSupportedSurface_ReturnsTypedErrorsWithReasons()
    {
        await using var context = await CommandTestContext.StartAsync("commands-not-supported");
        var typed = new List<object>();
        foreach (var descriptor in HostCommandRegistry.All.Values.Where(command => !command.IsImplemented)
                     .OrderBy(command => command.Name, StringComparer.Ordinal))
        {
            var error = await Assert.ThrowsAsync<HostCommandNotSupportedException>(
                () => context.Dispatcher.InvokeAsync(descriptor.Name));
            Assert.Equal("NOT_SUPPORTED", error.Code);
            Assert.Contains(descriptor.Name, error.Message, StringComparison.Ordinal);
            Assert.False(string.IsNullOrWhiteSpace(descriptor.Reason));
            typed.Add(new { command = descriptor.Name, domain = descriptor.Domain.ToString(), code = error.Code });
        }

        Assert.Equal(2, typed.Count);
        Assert.Equal(
            new[] { "credential_clear", "credential_put" },
            typed.Select(row => (string)row.GetType().GetProperty("command")!.GetValue(row)!)
                .OrderBy(name => name, StringComparer.Ordinal));
        var unknown = await Assert.ThrowsAsync<HostCommandUnknownException>(
            () => context.Dispatcher.InvokeAsync("not_a_production_command"));
        Assert.Equal("UNKNOWN_COMMAND", unknown.Code);

        SidecarFixture.WriteEvidenceJson("commands/not-supported-typed-errors.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2/AC3");
            writer.WriteNumber("typed_not_supported", typed.Count);
            writer.WriteBoolean("every_reason_present", true);
            writer.WriteString("unknown_command_code", unknown.Code);
            writer.WriteStartArray("commands");
            foreach (var row in typed)
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
    public async Task DomainServices_CoverEveryCommandExactlyOnce()
    {
        await using var context = await CommandTestContext.StartAsync("commands-domains");
        var services = new HostDomainService[]
        {
            context.Settings,
            context.Library,
            context.Region,
            context.Reader,
            context.Resource,
            context.Workbench,
        };

        var seen = new HashSet<string>(StringComparer.Ordinal);
        var summary = new List<object>();
        foreach (var service in services)
        {
            Assert.NotEmpty(service.Descriptors);
            foreach (var descriptor in service.Descriptors)
            {
                Assert.Equal(service.Domain, descriptor.Domain);
                Assert.True(seen.Add(descriptor.Name), $"command registered twice: {descriptor.Name}");
            }

            summary.Add(new
            {
                domain = service.Domain.ToString(),
                commands = service.Descriptors.Count,
                implemented = service.ImplementedCount,
                not_supported = service.NotSupportedCount,
            });
        }

        Assert.Equal(66, seen.Count);
        Assert.Equal(66, services.Sum(service => service.Descriptors.Count));
        Assert.Equal(64, services.Sum(service => service.ImplementedCount));

        var crossDomain = await Assert.ThrowsAsync<ArgumentException>(
            () => context.Settings.InvokeAsync("library_list_books", Args("{}")));
        Assert.Contains("Library", crossDomain.Message, StringComparison.Ordinal);

        SidecarFixture.WriteEvidenceJson("commands/domain-services.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("services", services.Length);
            writer.WriteNumber("commands_covered", seen.Count);
            writer.WriteBoolean("cross_domain_rejected", true);
            writer.WriteStartArray("domains");
            foreach (var row in summary)
            {
                writer.WriteStartObject();
                foreach (var property in row.GetType().GetProperties())
                {
                    var value = property.GetValue(row)!;
                    if (value is int number)
                    {
                        writer.WriteNumber(property.Name, number);
                    }
                    else
                    {
                        writer.WriteString(property.Name, value.ToString());
                    }
                }

                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }
}
