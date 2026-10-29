using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// V11R-F0-1 AC3/AC5 + V11R-F0-2 AC2/AC5: the ten Region write commands and the one page-scoped
/// Region text read projection are registered on the Core channel with the frozen Region
/// command-family minor (3) and the dispatcher writes EXACTLY the payload
/// bootstrap/core_service.py validates -- asserted without a live sidecar (the real echo path is
/// pinned by tests/core/test_region_write_commands.py and
/// tests/core/test_region_text_read_command.py on the Python side).
///
/// The frozen 66-command Rust snapshot is not edited: the parity assertions derive the legacy set
/// from the snapshot and the additive V11R set explicitly, so a missing or duplicated binding still
/// fails closed.
/// </summary>
public sealed class RegionWriteCommandTests
{
    private const int RegionFamilyMinor = 3;

    private static readonly string[] RegionReadCommands =
    {
        "list_page_region_texts",
    };

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

        // V11R-F0-2: the page-scoped text read projection shares the same family/minor.
        Assert.Equal(
            RegionReadCommands.ToHashSet(StringComparer.Ordinal),
            HostCommandRegistry.RegionReadCommandNames.ToHashSet(StringComparer.Ordinal));
        foreach (var name in RegionReadCommands)
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.Equal(HostCommandDomain.Region, descriptor.Domain);
            Assert.Equal(HostCommandChannel.CoreService, descriptor.Channel);
            Assert.True(descriptor.IsImplemented, $"{name} must be IMPLEMENTED (V11R-F0-2)");
            Assert.Null(descriptor.Reason);
            Assert.Equal(name, descriptor.CoreCommand);
            Assert.Equal(RegionFamilyMinor, descriptor.CoreMinor);
            Assert.Contains(name, regionDomainNames);
        }
    }

    [Fact]
    public void Registry_AppendsTheV11RCommands_WithoutEditingTheFrozenSnapshot()
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
        // ... and the only additions are exactly the explicit V11R additive set
        // (F0-1 write commands + F0-2 text read projection).
        var additive = registryNames.Except(snapshotNames, StringComparer.Ordinal)
            .ToHashSet(StringComparer.Ordinal);
        Assert.Equal(HostCommandRegistry.V11RAdditiveCommandNames, additive);
        Assert.Equal(
            HostCommandRegistry.RegionWriteCommandNames
                .Concat(HostCommandRegistry.RegionReadCommandNames)
                .ToHashSet(StringComparer.Ordinal),
            additive);
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
        foreach (var name in RegionWriteCommands.Concat(RegionReadCommands))
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
                $"{descriptor.Name} must be implemented after V11R-F0-1/F0-2"));
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
        // V11R-F0-2: the page-scoped text read projection (optional filter).
        {
            "list_page_region_texts",
            "{\"page_id\":\"page-1\"}",
            "{\"page_id\":\"page-1\"}"
        },
        {
            "list_page_region_texts",
            "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r2\"]}",
            "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r2\"]}"
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
        // V11R-F0-2: the read projection's boundary validation.
        { "list_page_region_texts", "{}" },
        { "list_page_region_texts", "{\"page_id\":\"\"}" },
        { "list_page_region_texts", "{\"page_id\":\"page-1\",\"region_ids\":[]}" },
        { "list_page_region_texts", "{\"page_id\":\"page-1\",\"region_ids\":\"r1\"}" },
        { "list_page_region_texts", "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r1\"]}" },
        { "list_page_region_texts", "{\"page_id\":\"page-1\",\"region_ids\":[\"\",\"r2\"]}" },
        // V11R-F0-1 I1/P2-5: domain-invalid values must fail BEFORE any frame.
        { "create_region", "{\"page_id\":\"page-1\",\"reading_order\":0," +
                            "\"geometry\":{\"points\":[[0.1,0.1],[0.2,0.2]]}}" },
        { "create_region", "{\"page_id\":\"page-1\",\"reading_order\":-1," +
                            "\"geometry\":{\"points\":[[0.1,0.1],[0.2,0.2]]}}" },
        { "create_region", "{\"page_id\":\"page-1\"," +
                            "\"geometry\":{\"points\":[[-0.1,0.1],[0.2,0.2]]}}" },
        { "create_region", "{\"page_id\":\"page-1\"," +
                            "\"geometry\":{\"points\":[[0.1,0.1],[1.2,0.4]]}}" },
        { "create_region", "{\"page_id\":\"page-1\"," +
                            "\"geometry\":{\"points\":[[0.1,0.1],[0.2,2.0]]}}" },
        { "save_region_geometry", "{\"region_id\":\"r1\"," +
                                   "\"geometry\":{\"points\":[[0.1,0.1],[0.2,0.2]]}," +
                                   "\"expected_revision\":0}" },
        { "delete_region", "{\"region_id\":\"r1\",\"expected_revision\":0}" },
        { "split_region", "{\"region_id\":\"r1\"," +
                          "\"parts\":[[[0.1,0.1],[0.2,0.2]],[[0.2,0.1],[0.3,0.2]]]," +
                          "\"expected_revision\":-2}" },
        { "merge_regions", "{\"page_id\":\"page-1\",\"region_ids\":[\"r1\",\"r2\"]," +
                            "\"expected_revisions\":{\"r1\":0,\"r2\":1}}" },
        { "reorder_regions", "{\"page_id\":\"page-1\",\"ordered_region_ids\":[\"r1\"]," +
                              "\"expected_revisions\":{\"r1\":0}}" },
        { "pin_revision", "{\"region_id\":\"r1\",\"revision_no\":0,\"pinned\":true}" },
        { "pin_revision", "{\"region_id\":\"r1\",\"revision_no\":-3,\"pinned\":true}" },
        { "set_region_lock", "{\"region_id\":\"r1\",\"region_locked\":true," +
                              "\"expected_revision\":0}" },
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
    public void RegionTextProjection_ParsesTheCoreResultWithoutLosingFields()
    {
        const string json = """
        {
          "page_id": "page-1",
          "page_size": {"width": 1000, "height": 1500},
          "regions": [
            {
              "region_id": "r1",
              "page_id": "page-1",
              "region_type": "speech",
              "sfx_policy": "skip",
              "reading_order": 2,
              "geometry": {
                "bbox": [0.1, 0.2, 0.3, 0.4],
                "polygon": [[0.1, 0.2], [0.4, 0.2], [0.4, 0.6], [0.1, 0.6]]
              },
              "text": {
                "ocr_text": "原文テキスト",
                "machine_translation": "机翻",
                "edited_translation": "人工译文",
                "final_translation": "人工译文",
                "final_source": "edited",
                "edited_confirmed": true,
                "manual_edited": true,
                "translation_locked": true
              },
              "locks": {
                "region_locked": true,
                "translation_locked": true,
                "inpaint_locked": false
              },
              "review_state": "confirmed",
              "origin": "user",
              "revision_no": 4,
              "current_revision_id": "rev-4",
              "is_pinned": true,
              "pinned_revision_nos": [1, 4],
              "created_at": "2026-01-01T00:00:00.000+00:00",
              "updated_at": "2026-01-01T00:00:01.000+00:00"
            }
          ]
        }
        """;

        var projection = RegionPageTextProjection.Parse(Args(json));
        Assert.Equal("page-1", projection.PageId);
        Assert.Equal(1000, projection.PageWidth);
        Assert.Equal(1500, projection.PageHeight);
        var region = Assert.Single(projection.Regions);
        Assert.Equal("r1", region.RegionId);
        Assert.Equal(2, region.ReadingOrder);
        Assert.NotNull(region.Geometry);
        Assert.Equal(new[] { 0.1, 0.2, 0.3, 0.4 }, region.Geometry!.Bbox);
        Assert.Equal(4, region.Geometry.Polygon.Count);
        Assert.Equal(new[] { 0.1, 0.2 }, region.Geometry.Polygon[0]);
        Assert.Equal("原文テキスト", region.Text.OcrText);
        Assert.Equal("人工译文", region.Text.FinalTranslation);
        Assert.Equal("edited", region.Text.FinalSource);
        Assert.True(region.Text.EditedConfirmed);
        Assert.True(region.Text.TranslationLocked);
        Assert.True(region.Locks.RegionLocked);
        Assert.True(region.Locks.TranslationLocked);
        Assert.False(region.Locks.InpaintLocked);
        Assert.Equal("confirmed", region.ReviewState);
        Assert.Equal("user", region.Origin);
        Assert.Equal(4, region.RevisionNo);
        Assert.Equal("rev-4", region.CurrentRevisionId);
        Assert.True(region.IsPinned);
        Assert.Equal(new[] { 1, 4 }, region.PinnedRevisionNos);
        Assert.Equal("2026-01-01T00:00:00.000+00:00", region.CreatedAt);
    }

    [Fact]
    public void RegionTextProjection_KeepsNullPageSizeAndGeometryExplicit()
    {
        const string json = """
        {
          "page_id": "unknown-page",
          "page_size": null,
          "regions": [
            {
              "region_id": "r1", "page_id": "p", "region_type": "speech",
              "sfx_policy": "skip", "reading_order": 0, "geometry": null,
              "text": {
                "ocr_text": "", "machine_translation": "", "edited_translation": "",
                "final_translation": "", "final_source": "none",
                "edited_confirmed": false, "manual_edited": false,
                "translation_locked": false
              },
              "locks": {
                "region_locked": false, "translation_locked": false,
                "inpaint_locked": false
              },
              "review_state": "unreviewed", "origin": "user", "revision_no": 1,
              "current_revision_id": "rev-1", "is_pinned": false,
              "pinned_revision_nos": [], "created_at": "t", "updated_at": "t"
            }
          ]
        }
        """;

        var projection = RegionPageTextProjection.Parse(Args(json));
        Assert.Null(projection.PageWidth);
        Assert.Null(projection.PageHeight);
        var region = Assert.Single(projection.Regions);
        Assert.Null(region.Geometry);
        Assert.Equal("none", region.Text.FinalSource);
        Assert.Empty(region.PinnedRevisionNos);
    }

    [Fact]
    public void RegionTextProjection_RejectsMalformedProjection()
    {
        var missingText = Args("""
        {"page_id":"p","page_size":null,"regions":[
          {"region_id":"r1","page_id":"p","region_type":"speech","sfx_policy":"skip",
           "reading_order":0,"geometry":null,"locks":{"region_locked":false,
           "translation_locked":false,"inpaint_locked":false},
           "review_state":"unreviewed","origin":"user","revision_no":1,
           "current_revision_id":"rev-1","is_pinned":false,
           "pinned_revision_nos":[],"created_at":"t","updated_at":"t"}
        ]}
        """);
        Assert.Throws<FormatException>(() => RegionPageTextProjection.Parse(missingText));

        var malformedGeometry = Args(
            "{\"page_id\":\"p\",\"page_size\":null,\"regions\":[]}");
        Assert.Empty(RegionPageTextProjection.Parse(malformedGeometry).Regions);
    }

    [Fact]
    public void Evidence_RegionWriteRegistration_IsWritten()
    {
        SidecarFixture.WriteEvidenceJson("commands/v11r-region-write-registration.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("task", "V11R-F0-1 + V11R-F0-2");
            writer.WriteString("ac", "F0-1 AC3/AC5 + F0-2 AC2/AC5");
            writer.WriteString("core_contract", "doc/contracts/V11R_REGION_WRITE_CONTRACT.md");
            writer.WriteNumber("region_family_minor", RegionFamilyMinor);
            writer.WriteString("registry_total", HostCommandRegistry.All.Count.ToString());
            writer.WriteNumber(
                "additive_commands",
                HostCommandRegistry.V11RAdditiveCommandNames.Count);
            writer.WriteStartArray("commands");
            foreach (var name in RegionWriteCommands.Concat(RegionReadCommands))
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
