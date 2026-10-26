using System.Text.Json;

namespace NewManga.CoreClient.Commands;

public enum HostCommandDomain
{
    Settings,
    Library,
    Region,
    Reader,
    Resource,
    Workbench,
}

public enum HostCommandChannel
{
    None,
    CoreService,
    HostBridge,
}

public enum HostCommandStatus
{
    Implemented,
    NotSupported,
}

/// <summary>One migrated production command (name is the legacy WebView IPC name).</summary>
public sealed record HostCommandDescriptor(
    string Name,
    HostCommandDomain Domain,
    HostCommandChannel Channel,
    HostCommandStatus Status,
    string? Reason,
    string? CoreCommand,
    int CoreMinor)
{
    public bool IsImplemented => Status == HostCommandStatus.Implemented;
}

/// <summary>Typed, UI-renderable refusal for commands outside the S2 migrated set.</summary>
public sealed class HostCommandNotSupportedException : Exception
{
    public HostCommandNotSupportedException(HostCommandDescriptor descriptor)
        : base($"[NOT_SUPPORTED] {descriptor.Name}: {descriptor.Reason}")
    {
        Descriptor = descriptor;
    }

    public HostCommandDescriptor Descriptor { get; }

    public string Code => "NOT_SUPPORTED";

    public string UserMessage => $"命令 {Descriptor.Name} 尚未迁移到新 Host（{Descriptor.Reason}）。";
}

public sealed class HostCommandUnknownException : Exception
{
    public HostCommandUnknownException(string name)
        : base($"[UNKNOWN_COMMAND] {name} is not part of the production command surface")
    {
        Name = name;
    }

    public string Name { get; }

    public string Code => "UNKNOWN_COMMAND";
}

/// <summary>Result of one migrated command: the legacy IPC value shape, untouched.</summary>
public sealed record HostCommandResult(
    string Name,
    HostCommandStatus Status,
    HostCommandChannel Channel,
    JsonElement Value);
