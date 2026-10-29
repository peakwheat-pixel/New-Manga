using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// V11R-F0-1 AC3/AC5: the ten Region write commands are registered on the Core channel with the
/// frozen Region command-family minor (3) and the dispatcher writes EXACTLY the payload
/// bootstrap/core_service.py validates -- asserted without a live sidecar (the real echo path is
/// pinned by tests/core/test_region_write_commands.py on the Python side).
///
/// The frozen 66-command Rust snapshot is not edited: the parity assertions derive the legacy set
/// from the snapshot and the additive V11R set explicitly, so a missing or duplicated binding still
/// fails closed.
/// </summary>
public sealed class RegionWriteCommandTests
{
    private const int RegionFamilyMinor = 3;

    private static readonly string[] RegionWriteCommands =
    {
        "create_region",
        "delete_region",
        "save_region_geometry",
        "merge_regions",
        "split_region",
        "reorder_regions",
        "save_manual_translation",
        "confirm_region_final",
        "set_region_lock",
        "pin_revision",
    };

    private static readonly string[] LegacySnapshotPaths =
    {
        "verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json",
    };

    [Fact]
    public void Registry_RegionWriteCommands_AreCoreBackedOnTheRegionFamilyMinor()
    {
        Assert.Equal(
            RegionWriteCommands.ToHashSet(StringComparer.Ordinal),
            HostCommandRegistry.RegionWriteCommandNames.ToHashSet(StringComparer.Ordinal));

        foreach (var name in RegionWriteCommands)
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.Equal(HostCommandDomain.Region, descriptor.Domain);
            Assert.Equal(HostCommandChannel.CoreService, descriptor.Channel);
            Assert.True(descriptor.IsImplemented, $"{name} must be IMPLEMENTED (V11R-F0-1)");
            Assert.Null(descriptor.Reason);
            Assert.Equal(name, descriptor.CoreCommand);
            Assert.Equal(RegionFamilyMinor, descriptor.CoreMinor);
        }

        var regionDomainNames = HostCommandRegistry
            .ForDomain(HostCommandDomain.Region)
            .Select(descriptor => descriptor.Name)
            .ToHashSet(StringComparer.Ordinal);
        Assert.True(
            RegionWriteCommands.All(regionDomainNames.Contains),
            "every V11R region write command must be registered in the Region domain");
    }

    [Fact]
    public void Registry_AppendsTheTenCommands_WithoutEditingTheFrozenSnapshot()
    {
        var snapshot = RepoLocator.ReadElement(LegacySnapshotPaths[0]);
        var snapshotNames = snapshot.GetProperty("commands").EnumerateArray()
            .Select(command => command.GetProperty("name").GetString()!)
            .ToHashSet(StringComparer.Ordinal);
        var registryNames = HostCommandRegistry.All.Keys.ToHashSet(StringComparer.Ordinal);

        // The frozen legacy surface is still fully covered ...
        Assert.True(
            registryNames.IsSupersetOf(snapshotNames),
            "the frozen production snapshot commands must all stay registered");
        // ... and the only additions are exactly the explicit V11R region-write set.
        var additive = registryNames.Except(snapshotNames, StringComparer.Ordinal)
            .ToHashSet(StringComparer.Ordinal);
        Assert.Equal(HostCommandRegistry.RegionWriteCommandNames, additive);
        Assert.Equal(
            snapshot.GetProperty("counts").GetProperty("production").GetInt32() + additive.Count,
            registryNames.Count);

        // Six domains partition the registry exactly once.
        Assert.Equal(
            registryNames.Count,
            Enum.GetValues<HostCommandDomain>()
                .Sum(domain => HostCommandRegistry.ForDomain(domain).Count));
    }

    [Fact]
    public void Registry_EveryAddedCommandHasExactlyOneDomainAndBinding()
    {
        foreach (var name in RegionWriteCommands)
        {
            var domains = Enum.GetValues<HostCommandDomain>()
                .Where(domain => HostCommandRegistry.ForDomain(domain)
                    .Any(descriptor => descriptor.Name == name))
                .ToArray();
            Assert.Single(domains);
            Assert.Equal(HostCommandDomain.Region, domains[0]);
        }

        Assert.All(
            HostCommandRegistry.All.Values,
            descriptor => Assert.True(
                descriptor.IsImplemented,
                $"{descriptor.Name} must be implemented after V11R-F0-1"));
    }

    public static TheoryData<string, string, string> PayloadCases => new()
    {
        {
            "create_region",
            "{\"page_id\":\"page-1\",\"region_type\":\"sfx\",\"reading_order\":3," +
            "\"geometry\":{\"points\":[[0.1,0.2],[0.3,0.4]]}}",
            "{\"page_id\":\"page-1\",\"region_type\":\"sfx\",\"reading_order\":3," +
            "\"geometry\":{\"points\":[[0.1,0.2],[0.3,0.4]]}}"
        },
        {
            "create_region",
            "{\"page_id\":\"page-1\",\"geometry\":{\"points\":[[0.1,0.2],[0.3,0.4]]}}",
            "{\"page_id\":\"page-1\",\"geometry\":{\"points\":[[0.1,0.2],[0.3,0.4]]}}"
        },
        {
            "delete_region",
            "{\"region_id\":\"r1\",\"expected_revision\":4}",
            "{\"region_id\":\"r1\",\"expected_revision\":4}"
        },
        {
            "save_region_geometry",
            "{\"region_id\":\"r1\",\"geometry\":{\"points\":[[0.2,0.2],[0.5,0.5]]}," +
            "\"expected_revision\":2}",
            "{\"region_id\":\"r1\",\"geometry\":{\"points\":[[0.2,0.2],[0.5,0.5]]}," +
            "\"expected_revision\":2}"
        },
        {
            "merge_regions",
            "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r2\"]," +
            "\"expected_revisions\":{\"r1\":1,\"r2\":2}}",
            "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r2\"]," +
            "\"expected_revisions\":{\"r1\":1,\"r2\":2}}"
        },
        {
            "split_region",
            "{\"region_id\":\"r1\",\"parts\":[[[0.1,0.1],[0.2,0.2]],[[0.2,0.1],[0.3,0.2]]]," +
            "\"expected_revision\":5}",
            "{\"region_id\":\"r1\",\"parts\":[[[0.1,0.1],[0.2,0.2]],[[0.2,0.1],[0.3,0.2]]]," +
            "\"expected_revision\":5}"
        },
        {
            "reorder_regions",
            "{\"page_id\":\"page-1\",\"ordered_region_ids\":[\"r2\",\"r1\"]," +
            "\"expected_revisions\":{\"r2\":1,\"r1\":1}}",
            "{\"page_id\":\"page-1\",\"ordered_region_ids\":[\"r2\",\"r1\"]," +
            "\"expected_revisions\":{\"r2\":1,\"r1\":1}}"
        },
        {
            "save_manual_translation",
            "{\"region_id\":\"r1\",\"edited_translation\":\"\",\"expected_revision\":3}",
            "{\"region_id\":\"r1\",\"edited_translation\":\"\",\"expected_revision\":3}"
        },
        {
            "save_manual_translation",
            "{\"region_id\":\"r1\",\"edited_translation\":\"人工译文\"}",
            "{\"region_id\":\"r1\",\"edited_translation\":\"人工译文\"}"
        },
        {
            "confirm_region_final",
            "{\"region_id\":\"r1\"}",
            "{\"region_id\":\"r1\"}"
        },
        {
            "set_region_lock",
            "{\"region_id\":\"r1\",\"region_locked\":true,\"translation_locked\":false," +
            "\"expected_revision\":7}",
            "{\"region_id\":\"r1\",\"region_locked\":true,\"translation_locked\":false," +
            "\"expected_revision\":7}"
        },
        {
            "set_region_lock",
            "{\"region_id\":\"r1\",\"inpaint_locked\":true}",
            "{\"region_id\":\"r1\",\"inpaint_locked\":true}"
        },
        {
            "pin_revision",
            "{\"region_id\":\"r1\",\"revision_no\":2,\"pinned\":true," +
            "\"expected_revision\":2}",
            "{\"region_id\":\"r1\",\"revision_no\":2,\"pinned\":true," +
            "\"expected_revision\":2}"
        },
    };

    [Theory]
    [MemberData(nameof(PayloadCases))]
    public void Dispatcher_WritesExactlyTheCoreValidatedPayload(
        string command,
        string argsJson,
        string expectedJson)
    {
        var actual = WireJson.Write(writer =>
            HostCommandDispatcher.WriteCorePayload(command, Args(argsJson), writer));
        Assert.True(
            JsonElement.DeepEquals(Args(expectedJson), Args(actual)),
            $"{command} payload mismatch: {actual}");
        Assert.Equal(
            command,
            HostCommandRegistry.Get(command).CoreCommand);
    }

    [Fact]
    public void Dispatcher_PreservesNestedNumbersAndChineseTextWithoutLoss()
    {
        var payload = WireJson.Write(writer => HostCommandDispatcher.WriteCorePayload(
            "save_manual_translation",
            Args("{\"region_id\":\"r1\",\"edited_translation\":\"霧港来信・日本語テスト\"}"),
            writer));
        using var document = JsonDocument.Parse(payload);
        Assert.Equal(
            "霧港来信・日本語テスト",
            document.RootElement.GetProperty("edited_translation").GetString());
    }

    public static TheoryData<string, string> InvalidArgumentCases => new()
    {
        { "create_region", "{}" },
        { "create_region", "{\"page_id\":\"page-1\"}" },
        { "create_region", "{\"page_id\":\"\",\"geometry\":{\"points\":[[0.1,0.1],[0.2,0.2]]}}" },
        { "create_region", "{\"page_id\":\"page-1\",\"geometry\":{}}" },
        { "create_region", "{\"page_id\":\"page-1\",\"geometry\":{\"points\":[[0.1,0.1]]}}" },
        { "create_region", "{\"page_id\":\"page-1\",\"geometry\":{\"points\":[[0.1,0.1],[0.2]]}}" },
        { "create_region", "{\"page_id\":\"page-1\",\"geometry\":{\"points\":[[0.1,0.1],[\"x\",0.2]]}}" },
        { "create_region", "{\"region_type\":\"speech\",\"geometry\":{\"points\":[[0.1,0.1],[0.2,0.2]]}}" },
        { "delete_region", "{}" },
        { "save_region_geometry", "{\"region_id\":\"r1\"}" },
        { "merge_regions", "{}" },
        { "merge_regions", "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\"]}" },
        { "merge_regions", "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"\"]}" },
        { "merge_regions", "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r2\"]," +
                            "\"expected_revisions\":{\"r1\":\"one\"}}" },
        { "split_region", "{}" },
        { "split_region", "{\"region_id\":\"r1\",\"parts\":[[[0.1,0.1],[0.2,0.2]]]}" },
        { "split_region", "{\"region_id\":\"r1\",\"parts\":[[[0.1,0.1]],[[0.2,0.2],[0.3,0.3]]]}" },
        { "reorder_regions", "{}" },
        { "reorder_regions", "{\"page_id\":\"page-1\",\"ordered_region_ids\":[]}" },
        { "save_manual_translation", "{}" },
        { "save_manual_translation", "{\"region_id\":\"r1\"}" },
        { "save_manual_translation", "{\"region_id\":\"r1\",\"edited_translation\":5}" },
        { "confirm_region_final", "{}" },
        { "set_region_lock", "{}" },
        { "set_region_lock", "{\"region_id\":\"r1\"}" },
        { "set_region_lock", "{\"region_id\":\"r1\",\"region_locked\":\"yes\"}" },
        { "pin_revision", "{}" },
        { "pin_revision", "{\"region_id\":\"r1\",\"revision_no\":1}" },
        { "pin_revision", "{\"region_id\":\"r1\",\"revision_no\":\"1\",\"pinned\":true}" },
        { "pin_revision", "{\"region_id\":\"r1\",\"revision_no\":1,\"pinned\":\"yes\"}" },
    };

    [Theory]
    [MemberData(nameof(InvalidArgumentCases))]
    public void Dispatcher_RejectsInvalidArguments_WithTypedCode(string command, string argsJson)
    {
        var error = Assert.Throws<HostCommandInvalidArgumentsException>(
            () => WireJson.Write(writer =>
                HostCommandDispatcher.WriteCorePayload(command, Args(argsJson), writer)));
        Assert.Equal("INVALID_ARGUMENTS", error.Code);
        Assert.Equal(command, error.Name);
    }

    [Fact]
    public void Evidence_RegionWriteRegistration_IsWritten()
    {
        SidecarFixture.WriteEvidenceJson("commands/v11r-region-write-registration.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("task", "V11R-F0-1");
            writer.WriteString("ac", "AC3/AC5");
            writer.WriteString("core_contract", "doc/contracts/V11R_REGION_WRITE_CONTRACT.md");
            writer.WriteNumber("region_family_minor", RegionFamilyMinor);
            writer.WriteString("registry_total", HostCommandRegistry.All.Count.ToString());
            writer.WriteNumber("additive_commands", RegionWriteCommands.Length);
            writer.WriteStartArray("commands");
            foreach (var name in RegionWriteCommands)
            {
                var descriptor = HostCommandRegistry.Get(name);
                writer.WriteStartObject();
                writer.WriteString("name", descriptor.Name);
                writer.WriteString("domain", descriptor.Domain.ToString());
                writer.WriteString("channel", descriptor.Channel.ToString());
                writer.WriteString("core_command", descriptor.CoreCommand);
                writer.WriteNumber("core_minor", descriptor.CoreMinor);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
    }
}
