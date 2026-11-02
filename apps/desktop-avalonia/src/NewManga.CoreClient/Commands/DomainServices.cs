using System.Text.Json;

namespace NewManga.CoreClient.Commands;

/// <summary>One of the six AC2 domain services. Each owns exactly one domain of the registry.</summary>
public abstract class HostDomainService
{
    private readonly HostCommandDispatcher _dispatcher;

    protected HostDomainService(HostCommandDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    public abstract HostCommandDomain Domain { get; }

    public IReadOnlyList<HostCommandDescriptor> Descriptors => HostCommandRegistry.ForDomain(Domain);

    public int ImplementedCount => Descriptors.Count(descriptor => descriptor.IsImplemented);

    public int NotSupportedCount => Descriptors.Count(descriptor => !descriptor.IsImplemented);

    public async Task<HostCommandResult> InvokeAsync(
        string name,
        JsonElement args = default,
        CancellationToken cancellationToken = default)
    {
        var descriptor = HostCommandRegistry.Get(name);
        if (descriptor.Domain != Domain)
        {
            throw new ArgumentException(
                $"{name} belongs to {descriptor.Domain}, not {Domain}",
                nameof(name));
        }

        return await _dispatcher.InvokeAsync(name, args, cancellationToken).ConfigureAwait(false);
    }
}

public sealed class SettingsCommandService : HostDomainService
{
    public SettingsCommandService(HostCommandDispatcher dispatcher)
        : base(dispatcher)
    {
    }

    public override HostCommandDomain Domain => HostCommandDomain.Settings;
}

public sealed class LibraryCommandService : HostDomainService
{
    public LibraryCommandService(HostCommandDispatcher dispatcher)
        : base(dispatcher)
    {
    }

    public override HostCommandDomain Domain => HostCommandDomain.Library;
}

public sealed class RegionCommandService : HostDomainService
{
    public RegionCommandService(HostCommandDispatcher dispatcher)
        : base(dispatcher)
    {
    }

    public override HostCommandDomain Domain => HostCommandDomain.Region;
}

public sealed class ReaderCommandService : HostDomainService
{
    public ReaderCommandService(HostCommandDispatcher dispatcher)
        : base(dispatcher)
    {
    }

    public override HostCommandDomain Domain => HostCommandDomain.Reader;
}

public sealed class ResourceCommandService : HostDomainService
{
    public ResourceCommandService(HostCommandDispatcher dispatcher)
        : base(dispatcher)
    {
    }

    public override HostCommandDomain Domain => HostCommandDomain.Resource;
}

public sealed class WorkbenchCommandService : HostDomainService
{
    public WorkbenchCommandService(HostCommandDispatcher dispatcher)
        : base(dispatcher)
    {
    }

    public override HostCommandDomain Domain => HostCommandDomain.Workbench;
}
