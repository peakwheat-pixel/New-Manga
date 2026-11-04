using System.Collections.Generic;
using System.Linq;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// FEA-05-PORT-1: the Draft family registration surface. These are the tests that
/// make the port/registry part of the card verifiable without a live Core.
/// </summary>
public sealed class DraftCommandRegistryTests
{
    [Fact]
    public void Drafts_Family_IsRegisteredOnTheDraftsDomainWithCoreMinorThree()
    {
        var drafts = HostCommandRegistry.DraftsCommandNames.ToArray();
        Assert.Equal(6, drafts.Length);
        Assert.Equal(
            new[]
            {
                "drafts_apply", "drafts_discard", "drafts_open",
                "drafts_patch", "drafts_prepare", "drafts_status",
            },
            drafts.OrderBy(name => name, System.StringComparer.Ordinal).ToArray());

        foreach (var name in drafts)
        {
            var descriptor = HostCommandRegistry.Get(name);
            Assert.Equal(HostCommandDomain.Drafts, descriptor.Domain);
            Assert.Equal(HostCommandChannel.CoreService, descriptor.Channel);
            Assert.Equal(name, descriptor.CoreCommand);
            Assert.Equal(3, descriptor.CoreMinor);
        }
    }

    [Fact]
    public void Additive_Set_IsTheUnionOfTheDeclaredFamilies()
    {
        var expected = HostCommandRegistry.RegionWriteCommandNames
            .Concat(HostCommandRegistry.RegionReadCommandNames)
            .Concat(HostCommandRegistry.DraftsCommandNames)
            .Concat(HostCommandRegistry.SourceCommandNames)
            .Concat(HostCommandRegistry.SourceSyncCommandNames)
            .ToHashSet(System.StringComparer.Ordinal);

        Assert.Equal(40, HostCommandRegistry.V11RAdditiveCommandNames.Count);
        Assert.Equal(expected, HostCommandRegistry.V11RAdditiveCommandNames.ToHashSet(System.StringComparer.Ordinal));
    }

    [Fact]
    public void Drafts_Domain_IsPartitionedExactlyOnce()
    {
        var domainNames = HostCommandRegistry.ForDomain(HostCommandDomain.Drafts)
            .Select(descriptor => descriptor.Name)
            .ToHashSet(System.StringComparer.Ordinal);
        Assert.Equal(HostCommandRegistry.DraftsCommandNames, domainNames);

        var total = System.Enum.GetValues<HostCommandDomain>()
            .Sum(domain => HostCommandRegistry.ForDomain(domain).Count);
        Assert.Equal(HostCommandRegistry.All.Count, total);
    }

    [Theory]
    [InlineData("drafts_open", new[] { "sessionId", "pageId", "pageBindingVersion" })]
    [InlineData("drafts_patch", new[] { "draftId", "sessionId", "patch" })]
    [InlineData("drafts_prepare", new[] { "regionId", "patch", "origin" })]
    [InlineData("drafts_apply", new[] { "token", "candidateIds" })]
    [InlineData("drafts_discard", new[] { "draftId", "sessionId" })]
    public void WriteCorePayload_RequiresTheDeclaredFields(string command, string[] required)
    {
        // Fail-closed: a payload missing a required field must throw before framing.
        var missing = required[0];
        var json = "{" + string.Join(",", required
            .Where(field => field != missing)
            .Select(field => $"\"{field}\":\"x\"")) + "}";
        using var document = System.Text.Json.JsonDocument.Parse(json);
        using var stream = new System.IO.MemoryStream();
        using var writer = new System.Text.Json.Utf8JsonWriter(stream);

        var error = Assert.Throws<HostCommandInvalidArgumentsException>(
            () => HostCommandDispatcher.WriteCorePayload(command, document.RootElement, writer));
        Assert.Equal("INVALID_ARGUMENTS", error.Code);
    }

    [Fact]
    public void WriteCorePayload_DraftsStatus_RequiresExactlyOneOfDraftIdOrSessionId()
    {
        AssertXorThrows("{}");
        AssertXorThrows("{\"draftId\":\"d1\",\"sessionId\":\"s1\"}");

        // Both single-key shapes are accepted.
        Freeze("{\"draftId\":\"d1\"}");
        Freeze("{\"sessionId\":\"s1\"}");

        static void AssertXorThrows(string json)
        {
            using var document = System.Text.Json.JsonDocument.Parse(json);
            using var stream = new System.IO.MemoryStream();
            using var writer = new System.Text.Json.Utf8JsonWriter(stream);
            var error = Assert.Throws<HostCommandInvalidArgumentsException>(
                () => HostCommandDispatcher.WriteCorePayload("drafts_status", document.RootElement, writer));
            Assert.Equal("INVALID_ARGUMENTS", error.Code);
        }

        static void Freeze(string json)
        {
            using var document = System.Text.Json.JsonDocument.Parse(json);
            using var stream = new System.IO.MemoryStream();
            using var writer = new System.Text.Json.Utf8JsonWriter(stream);
            HostCommandDispatcher.WriteCorePayload("drafts_status", document.RootElement, writer);
        }
    }
}
