using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// AC1/AC2/AC3 contract parity: the committed Rust-derived snapshot and the C# command registry must
/// describe exactly the same 66 production commands, with no silent gaps. Every command is either
/// IMPLEMENTED (sidecar channel named) or explicit NOT_SUPPORTED with a readable reason. The probe
/// evidence proves the nine core_service routes really work on the frozen sidecar.
/// </summary>
public sealed class CommandParityContractTests
{
    private const string SnapshotPath = "verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json";
    private const string ProbePath = "verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json";

    private static readonly Dictionary<HostCommandDomain, int> ExpectedDomainCounts = new()
    {
        [HostCommandDomain.Settings] = 33,
        [HostCommandDomain.Library] = 8,
        [HostCommandDomain.Region] = 6,
        [HostCommandDomain.Reader] = 4,
        [HostCommandDomain.Resource] = 3,
        [HostCommandDomain.Workbench] = 12,
    };

    private static readonly (string Command, string CoreCommand)[] ImplementedCoreRoutes =
    {
        ("core_ping", "core.ping"),
        ("library_list_books", "ListBooks"),
        ("library_list_recycle_bin_books", "ListRecycleBinBooks"),
        ("library_create_book", "CreateBook"),
        ("create_chapter", "CreateChapter"),
        ("list_chapters", "list_chapters"),
        ("list_chapter_pages", "list_chapter_pages"),
        ("list_regions", "list_regions"),
        ("settings_get", "settings.get"),
        ("backup_list", "backup.list"),
        ("plugins_list", "plugins.list"),
        ("cleanup_preview", "cleanup.preview"),
        ("library_get_export_history", "GetExportHistory"),
    };

    [Fact]
    public void Snapshot_Has66ProductionCommands_AndExcludesTestOnlySurface()
    {
        var snapshot = RepoLocator.ReadElement(SnapshotPath);
        var commands = snapshot.GetProperty("commands");
        Assert.Equal(66, commands.GetArrayLength());
        Assert.Equal(66, snapshot.GetProperty("counts").GetProperty("production").GetInt32());
        Assert.Equal(4, snapshot.GetProperty("counts").GetProperty("probe_only").GetInt32());
        Assert.Equal(3, snapshot.GetProperty("counts").GetProperty("ac1_test").GetInt32());
        Assert.Equal(1, snapshot.GetProperty("counts").GetProperty("removed").GetInt32());

        var names = new HashSet<string>(StringComparer.Ordinal);
        foreach (var command in commands.EnumerateArray())
        {
            var name = command.GetProperty("name").GetString()!;
            Assert.True(names.Add(name), $"duplicate snapshot command {name}");
            var handler = command.GetProperty("handler");
            Assert.Equal(JsonValueKind.Object, handler.ValueKind);
            Assert.EndsWith(".rs", handler.GetProperty("file").GetString()!, StringComparison.Ordinal);
            Assert.True(handler.GetProperty("line").GetInt32() > 0);
            Assert.False(string.IsNullOrWhiteSpace(command.GetProperty("returns").GetString()));
            Assert.False(string.IsNullOrWhiteSpace(command.GetProperty("error_type").GetString()));
        }

        Assert.Equal(66, names.Count);
        Assert.Contains("core_ping", names);
        Assert.Contains("issue_resource_url", names);
        Assert.DoesNotContain("probe_config", names);
        Assert.DoesNotContain("ac1_request", names);
        Assert.DoesNotContain("register_catalog", names);
    }

    [Fact]
    public void Registry_CoversSnapshotExactly_WithSixDomains()
    {
        var snapshot = RepoLocator.ReadElement(SnapshotPath);
        var snapshotNames = snapshot.GetProperty("commands").EnumerateArray()
            .Select(command => command.GetProperty("name").GetString()!)
            .ToHashSet(StringComparer.Ordinal);
        var registryNames = HostCommandRegistry.All.Keys.ToHashSet(StringComparer.Ordinal);

        Assert.Equal(66, registryNames.Count);
        Assert.True(registryNames.SetEquals(snapshotNames), "C# registry and Rust snapshot command sets differ");

        foreach (var domain in Enum.GetValues<HostCommandDomain>())
        {
            var count = HostCommandRegistry.ForDomain(domain).Count;
            Assert.Equal(ExpectedDomainCounts[domain], count);
            Assert.True(count > 0, $"{domain} domain is empty");
        }

        Assert.Equal(66, ExpectedDomainCounts.Values.Sum());
        var total = Enum.GetValues<HostCommandDomain>().Sum(domain => HostCommandRegistry.ForDomain(domain).Count);
        Assert.Equal(66, total);
    }

    [Fact]
    public void EveryNotSupportedCommand_HasReason_AndEveryImplementedCommand_HasChannel()
    {
        var implemented = HostCommandRegistry.All.Values.Where(command => command.IsImplemented).ToArray();
        var notSupported = HostCommandRegistry.All.Values.Where(command => !command.IsImplemented).ToArray();

        Assert.Equal(24, implemented.Length);
        Assert.Equal(42, notSupported.Length);
        Assert.Equal(66, implemented.Length + notSupported.Length);

        foreach (var command in implemented)
        {
            Assert.True(
                command.Channel is HostCommandChannel.CoreService or HostCommandChannel.HostBridge,
                $"{command.Name} has no sidecar channel");
            if (command.Channel == HostCommandChannel.CoreService)
            {
                Assert.False(string.IsNullOrWhiteSpace(command.CoreCommand));
                Assert.True(command.CoreMinor > 0);
            }
        }

        foreach (var command in notSupported)
        {
            Assert.Equal(HostCommandChannel.None, command.Channel);
            Assert.False(string.IsNullOrWhiteSpace(command.Reason), $"{command.Name} lacks a NOT_SUPPORTED reason");
            Assert.True(command.Reason!.Length > 30, $"{command.Name} reason is too vague");
        }

        var createChapter = HostCommandRegistry.Get("create_chapter");
        Assert.True(createChapter.IsImplemented);
        Assert.Equal("CreateChapter", createChapter.CoreCommand);
        Assert.Equal(8, createChapter.CoreMinor);
    }

    [Fact]
    public void ImplementedCoreCommands_AreProvenByProbeEvidence()
    {
        var probe = RepoLocator.ReadElement(ProbePath);
        var byCommand = probe.GetProperty("probes").EnumerateArray()
            .ToDictionary(
                record => record.GetProperty("command").GetString()!,
                record => record,
                StringComparer.Ordinal);

        foreach (var (command, coreCommand) in ImplementedCoreRoutes)
        {
            Assert.True(byCommand.TryGetValue(coreCommand, out var record), $"probe evidence missing {coreCommand} for {command}");
            Assert.True(record.GetProperty("ok").GetBoolean(), $"probe of {coreCommand} failed; {command} cannot claim parity");
            Assert.True(record.GetProperty("raw_request_ascii").GetBoolean());
        }

        Assert.True(byCommand.TryGetValue("CreateChapter", out var createChapter));
        Assert.True(createChapter.GetProperty("ok").GetBoolean());
        Assert.True(createChapter.GetProperty("raw_request_ascii").GetBoolean());
    }

    [Fact]
    public void CoverageMatrix_IsWrittenAsEvidence()
    {
        var snapshot = RepoLocator.ReadElement(SnapshotPath);
        var snapshotCommands = snapshot.GetProperty("commands").EnumerateArray()
            .ToDictionary(
                command => command.GetProperty("name").GetString()!,
                command => command,
                StringComparer.Ordinal);

        var rows = new List<object>();
        var implemented = new List<string>();
        var notSupported = new List<object>();
        foreach (var descriptor in HostCommandRegistry.All.Values.OrderBy(command => command.Name, StringComparer.Ordinal))
        {
            var snapshotCommand = snapshotCommands[descriptor.Name];
            var handler = snapshotCommand.GetProperty("handler");
            rows.Add(new
            {
                name = descriptor.Name,
                domain = descriptor.Domain.ToString().ToLowerInvariant(),
                rust_handler = handler.GetProperty("file").GetString() + ":" + handler.GetProperty("line").GetInt32(),
                rust_params = snapshotCommand.GetProperty("params").GetArrayLength(),
                rust_returns = snapshotCommand.GetProperty("returns").GetString(),
                status = descriptor.Status.ToString(),
                channel = descriptor.Channel.ToString(),
                core_command = descriptor.CoreCommand,
                core_minor = descriptor.CoreMinor,
                reason = descriptor.Reason,
            });

            if (descriptor.IsImplemented)
            {
                implemented.Add(descriptor.Name);
            }
            else
            {
                notSupported.Add(new { name = descriptor.Name, domain = descriptor.Domain.ToString().ToLowerInvariant(), reason = descriptor.Reason });
            }
        }

        SidecarFixture.WriteEvidenceJson("commands/parity-contract.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2/AC3");
            writer.WriteString("snapshot", SnapshotPath);
            writer.WriteString("probe", ProbePath);
            writer.WriteNumber("snapshot_commands", 66);
            writer.WriteNumber("implemented", implemented.Count);
            writer.WriteNumber("not_supported", notSupported.Count);
            writer.WriteNumber("coverage_percent", 100);
            writer.WriteBoolean("every_command_has_owner", true);
            writer.WriteStartObject("domain_counts");
            foreach (var domain in Enum.GetValues<HostCommandDomain>())
            {
                writer.WriteNumber(domain.ToString().ToLowerInvariant(), HostCommandRegistry.ForDomain(domain).Count);
            }

            writer.WriteEndObject();
            writer.WriteStartArray("implemented_commands");
            foreach (var name in implemented)
            {
                writer.WriteStringValue(name);
            }

            writer.WriteEndArray();
            writer.WriteStartArray("not_supported_commands");
            foreach (var row in notSupported)
            {
                writer.WriteStartObject();
                writer.WriteString("name", row.GetType().GetProperty("name")!.GetValue(row)!.ToString());
                writer.WriteString("reason", row.GetType().GetProperty("reason")!.GetValue(row)!.ToString());
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteStartArray("matrix");
            foreach (var row in rows)
            {
                writer.WriteStartObject();
                foreach (var property in row.GetType().GetProperties())
                {
                    var value = property.GetValue(row);
                    if (value is null)
                    {
                        writer.WriteNull(property.Name);
                    }
                    else if (value is int number)
                    {
                        writer.WriteNumber(property.Name, number);
                    }
                    else if (value is bool flag)
                    {
                        writer.WriteBoolean(property.Name, flag);
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
