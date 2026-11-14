using NewManga.CoreClient.Commands;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// E-1 / CMD-COVERAGE-ASSERT-FIX: every production command is reachable through exactly one route —
/// either one of the six typed <see cref="HostDomainService"/> ports, or the
/// <see cref="HostCommandDispatcher"/> direct family (<c>Drafts</c> / <c>SourceSync</c>).
///
/// These facts read only the static registry plus the services' <c>Descriptors</c> projection, so they
/// need **no sidecar**. The old version of this coverage check lived behind <c>[SidecarFact]</c>, so it
/// skipped in the normal fixture-less suite — which is how it stayed broken: it asserted that the six
/// services covered all 111 commands, while 21 of them (Drafts 6 + SourceSync 15) are dispatcher-routed
/// by design.
/// </summary>
public sealed class CommandCoverageRoutingTests
{
    private static readonly HostCommandDomain[] DispatcherRoutedDomains =
    {
        HostCommandDomain.Drafts,
        HostCommandDomain.SourceSync,
    };

    private static HostDomainService[] Services()
    {
        // Every constructor parameter of HostCommandDispatcher is optional, so no Core is needed here.
        var dispatcher = new HostCommandDispatcher();
        return new HostDomainService[]
        {
            new SettingsCommandService(dispatcher),
            new LibraryCommandService(dispatcher),
            new RegionCommandService(dispatcher),
            new ReaderCommandService(dispatcher),
            new ResourceCommandService(dispatcher),
            new WorkbenchCommandService(dispatcher),
        };
    }

    private static HashSet<string> CoveredNames() =>
        Services()
            .SelectMany(service => service.Descriptors)
            .Select(descriptor => descriptor.Name)
            .ToHashSet(StringComparer.Ordinal);

    private static HashSet<string> DispatcherFamilyNames() =>
        HostCommandRegistry.DraftsCommandNames
            .Concat(HostCommandRegistry.SourceSyncCommandNames)
            .ToHashSet(StringComparer.Ordinal);

    /// <summary>
    /// The routing rule itself: a name is unrouted when no service claims it and it is not part of a
    /// dispatcher-routed family. AC3 reuses this same predicate to prove it still bites.
    /// </summary>
    private static string? FirstUnrouted(
        IEnumerable<string> names,
        IReadOnlySet<string> covered,
        IReadOnlySet<string> families) =>
        names.FirstOrDefault(name => !covered.Contains(name) && !families.Contains(name));

    [Fact]
    public void SixServices_CoverEveryNonDispatcherCommandExactlyOnce()
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        var services = Services();
        foreach (var service in services)
        {
            Assert.NotEmpty(service.Descriptors);
            foreach (var descriptor in service.Descriptors)
            {
                Assert.Equal(service.Domain, descriptor.Domain);
                Assert.True(seen.Add(descriptor.Name), $"command registered twice: {descriptor.Name}");
            }
        }

        var all = HostCommandRegistry.All;
        var expected = all.Values
            .Where(descriptor => !DispatcherRoutedDomains.Contains(descriptor.Domain))
            .Select(descriptor => descriptor.Name)
            .ToHashSet(StringComparer.Ordinal);

        Assert.Equal(expected, seen);

        // The registry is fully accounted for by "six services" + "dispatcher-routed families".
        var routed = all.Values.Count(descriptor => DispatcherRoutedDomains.Contains(descriptor.Domain));
        Assert.Equal(all.Count, seen.Count + routed);
    }

    [Fact]
    public void EveryUncoveredCommand_BelongsToADispatcherRoutedFamily()
    {
        var covered = CoveredNames();
        var families = DispatcherFamilyNames();
        var uncovered = HostCommandRegistry.All.Keys.Where(name => !covered.Contains(name)).ToArray();

        // Non-vacuous: the dispatcher families really do carry commands the services do not.
        Assert.NotEmpty(uncovered);
        Assert.All(uncovered, name => Assert.Contains(name, families));
        Assert.All(uncovered, name => Assert.Contains(
            HostCommandRegistry.All[name].Domain, DispatcherRoutedDomains));

        // The families must not smuggle in names that are not production commands.
        Assert.All(families, name => Assert.True(
            HostCommandRegistry.All.ContainsKey(name),
            $"dispatcher family lists a non-production command: {name}"));

        // EXACTLY ONE route (r1 复核 P2-1): a command covered by a typed service must not ALSO be
        // listed as a dispatcher-routed family member. Without this, adding e.g. `create_region` to
        // SourceSyncCommandNames keeps every other assertion green while the two routes overlap.
        Assert.Empty(covered.Intersect(families, StringComparer.Ordinal));
    }

    [Fact]
    public void EveryDomain_HasAtLeastOneCommand()
    {
        foreach (var domain in Enum.GetValues<HostCommandDomain>())
        {
            Assert.NotEmpty(HostCommandRegistry.ForDomain(domain));
        }
    }

    /// <summary>
    /// AC3 discriminating power: the routing predicate must reject a command that no service claims
    /// and that does not belong to a dispatcher family. Proved twice — synthetically, and by dropping
    /// one real command out of the covered set.
    /// </summary>
    [Fact]
    public void AC3_AnOutOfRouteCommand_IsReportedAsUnrouted()
    {
        var covered = CoveredNames();
        var families = DispatcherFamilyNames();

        // Baseline: the real registry has no unrouted command.
        Assert.Null(FirstUnrouted(HostCommandRegistry.All.Keys, covered, families));

        // Synthetic: a brand-new command that never gets a route.
        Assert.Equal(
            "synthetic_unrouted_command",
            FirstUnrouted(HostCommandRegistry.All.Keys.Append("synthetic_unrouted_command"), covered, families));

        // Real-data probe: drop one genuinely service-routed command from the covered set and the
        // same predicate must immediately report it.
        var victim = covered.First(name =>
            !DispatcherRoutedDomains.Contains(HostCommandRegistry.All[name].Domain));
        var withoutVictim = covered.Where(name => name != victim).ToHashSet(StringComparer.Ordinal);
        Assert.Equal(victim, FirstUnrouted(HostCommandRegistry.All.Keys, withoutVictim, families));
    }

    /// <summary>
    /// P2-1 (r1 复核) discriminating power: the "exactly one route" rule must reject an overlap,
    /// i.e. a command that a typed service claims AND that is listed in a dispatcher family.
    /// </summary>
    [Fact]
    public void P2_1_AnOverlappingRoute_IsReported()
    {
        var covered = CoveredNames();
        var families = DispatcherFamilyNames();

        // Baseline: no command is on both routes.
        Assert.Empty(covered.Intersect(families, StringComparer.Ordinal));

        // Real-data probe: pretend one genuinely typed command is also a dispatcher-family member.
        var victim = covered.First(name =>
            !DispatcherRoutedDomains.Contains(HostCommandRegistry.All[name].Domain));
        var familiesWithOverlap = new HashSet<string>(families, StringComparer.Ordinal) { victim };
        Assert.Contains(victim, covered.Intersect(familiesWithOverlap, StringComparer.Ordinal));
    }
}
