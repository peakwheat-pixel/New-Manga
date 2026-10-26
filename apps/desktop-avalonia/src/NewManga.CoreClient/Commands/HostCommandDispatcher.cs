using System.Text.Json;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Transport;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Commands;

public sealed class HostCommandInvalidArgumentsException : Exception
{
    public HostCommandInvalidArgumentsException(string name, string detail)
        : base($"[INVALID_ARGUMENTS] {name}: {detail}")
    {
        Name = name;
    }

    public string Name { get; }

    public string Code => "INVALID_ARGUMENTS";
}

/// <summary>
/// AC2/AC3 dispatcher: maps the legacy WebView command names onto the migrated C# services. The
/// payload shape is passed through unchanged (the Core is the semantic authority); NOT_SUPPORTED
/// commands fail with a typed, UI-renderable reason instead of an opaque error.
/// </summary>
public sealed class HostCommandDispatcher
{
    private readonly CoreServiceClient? _core;
    private readonly HostBridgeClient? _bridge;

    public HostCommandDispatcher(CoreServiceClient? core = null, HostBridgeClient? bridge = null)
    {
        _core = core;
        _bridge = bridge;
    }

    public IReadOnlyDictionary<string, HostCommandDescriptor> Commands => HostCommandRegistry.All;

    public async Task<HostCommandResult> InvokeAsync(
        string name,
        JsonElement args = default,
        CancellationToken cancellationToken = default)
    {
        var descriptor = HostCommandRegistry.Get(name);
        if (!descriptor.IsImplemented)
        {
            throw new HostCommandNotSupportedException(descriptor);
        }

        var payload = args.ValueKind == JsonValueKind.Object ? args : EmptyObject();
        return descriptor.Channel switch
        {
            HostCommandChannel.CoreService => await InvokeCoreAsync(descriptor, payload, cancellationToken)
                .ConfigureAwait(false),
            HostCommandChannel.HostBridge => await InvokeBridgeAsync(descriptor, payload, cancellationToken)
                .ConfigureAwait(false),
            _ => throw new HostCommandNotSupportedException(descriptor),
        };
    }

    private async Task<HostCommandResult> InvokeCoreAsync(
        HostCommandDescriptor descriptor,
        JsonElement args,
        CancellationToken cancellationToken)
    {
        var core = _core
            ?? throw new SidecarException(
                SidecarErrorCode.ProcessExited,
                SidecarSpec.CoreServiceName,
                $"{descriptor.Name} requires a running core_service");

        var response = await core.SendAsync(
                descriptor.CoreCommand!,
                descriptor.CoreMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    foreach (var property in args.EnumerateObject())
                    {
                        property.WriteTo(writer);
                    }

                    writer.WriteEndObject();
                },
                TimeSpan.FromSeconds(30),
                cancellationToken)
            .ConfigureAwait(false);

        return new HostCommandResult(
            descriptor.Name,
            descriptor.Status,
            descriptor.Channel,
            response.Result ?? EmptyObject());
    }

    private async Task<HostCommandResult> InvokeBridgeAsync(
        HostCommandDescriptor descriptor,
        JsonElement args,
        CancellationToken cancellationToken)
    {
        var bridge = _bridge
            ?? throw new SidecarException(
                SidecarErrorCode.ProcessExited,
                SidecarSpec.HostBridgeName,
                $"{descriptor.Name} requires a running host_bridge");

        switch (descriptor.Name)
        {
            case "issue_resource_url":
            {
                var resourceId = RequireString(descriptor.Name, args, "resource_id");
                var revision = RequireString(descriptor.Name, args, "revision");
                var issued = await bridge.IssueAsync(resourceId, revision, cancellationToken).ConfigureAwait(false);
                return new HostCommandResult(
                    descriptor.Name,
                    descriptor.Status,
                    descriptor.Channel,
                    BuildJson(writer =>
                    {
                        writer.WriteStartObject();
                        writer.WriteString("id", issued.GrantId);
                        writer.WriteNumber("size", issued.Size);
                        writer.WriteEndObject();
                    }));
            }

            case "revoke_ref":
            {
                var opaqueId = RequireString(descriptor.Name, args, "opaque_id");
                await bridge.RevokeAsync(opaqueId, cancellationToken).ConfigureAwait(false);
                return new HostCommandResult(
                    descriptor.Name,
                    descriptor.Status,
                    descriptor.Channel,
                    BuildJson(writer =>
                    {
                        writer.WriteStartObject();
                        writer.WriteBoolean("revoked", true);
                        writer.WriteEndObject();
                    }));
            }

            case "revoke_resource_refs":
            {
                var resourceId = RequireString(descriptor.Name, args, "resource_id");
                var count = await bridge.RevokeResourceAsync(resourceId, cancellationToken).ConfigureAwait(false);
                return new HostCommandResult(
                    descriptor.Name,
                    descriptor.Status,
                    descriptor.Channel,
                    BuildJson(writer =>
                    {
                        writer.WriteStartObject();
                        writer.WriteNumber("revoked_count", count);
                        writer.WriteEndObject();
                    }));
            }

            default:
                throw new HostCommandNotSupportedException(descriptor);
        }
    }

    private static string RequireString(string command, JsonElement args, string property)
    {
        if (args.ValueKind == JsonValueKind.Object &&
            args.TryGetProperty(property, out var value) &&
            value.ValueKind == JsonValueKind.String &&
            value.GetString() is { Length: > 0 } text)
        {
            return text;
        }

        throw new HostCommandInvalidArgumentsException(command, $"missing required string argument '{property}'");
    }

    private static JsonElement EmptyObject()
    {
        using var document = JsonDocument.Parse("{}");
        return document.RootElement.Clone();
    }

    private static JsonElement BuildJson(Action<Utf8JsonWriter> write)
    {
        var line = WireJson.Write(write);
        using var document = JsonDocument.Parse(line);
        return document.RootElement.Clone();
    }
}
