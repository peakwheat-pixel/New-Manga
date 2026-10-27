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
                writer => WriteCorePayload(descriptor.Name, args, writer),
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

    /// <summary>
    /// NS-WIRE-A1: the legacy Tauri command signatures are enforced at the dispatcher boundary and
    /// translated to the exact Core payload each route proved against the frozen sidecar. Unknown
    /// commands keep the historical pass-through (Core remains the semantic authority).
    /// </summary>
    private static void WriteCorePayload(string name, JsonElement args, Utf8JsonWriter writer)
    {
        var payload = args.ValueKind == JsonValueKind.Object ? args : EmptyObject();
        writer.WriteStartObject();
        switch (name)
        {
            case "settings_update_section":
                writer.WriteString("section", RequireString(name, payload, "section"));
                writer.WritePropertyName("values");
                RequireObject(name, payload, "values").WriteTo(writer);
                break;
            case "settings_provider_profiles_list":
            case "settings_network_profiles_list":
            case "cleanup_run":
                // Legacy signatures take no arguments; the Core faces reject stray payload keys.
                break;
            case "settings_resolve_overrides":
                writer.WritePropertyName("keys");
                WriteStringArray(writer, name, payload, "keys");
                WriteOptionalString(writer, name, payload, "book_id");
                WriteOptionalString(writer, name, payload, "chapter_id");
                WriteOptionalString(writer, name, payload, "run_id");
                break;
            case "backup_create":
                writer.WriteString("backup_type", OptionalString(name, payload, "backup_type") ?? "manual");
                break;
            case "plugins_set_enabled":
                writer.WriteBoolean("enabled", RequireBool(name, payload, "enabled"));
                break;
            case "library_start_run":
                writer.WriteString("command", RequireString(name, payload, "command"));
                writer.WritePropertyName("scope");
                RequireObject(name, payload, "scope").WriteTo(writer);
                if (payload.TryGetProperty("overrides", out var overrides) &&
                    overrides.ValueKind != JsonValueKind.Null)
                {
                    writer.WritePropertyName("overrides");
                    overrides.WriteTo(writer);
                }

                writer.WriteString("idempotency_key", RequireString(name, payload, "idempotency_key"));
                break;
            case "library_control_run":
                writer.WriteString("run_id", RequireString(name, payload, "run_id"));
                writer.WriteString("action", RequireString(name, payload, "action"));
                WriteOptionalString(writer, name, payload, "idempotency_key");
                break;
            case "library_resume_blocked_run":
            case "library_get_run_snapshot":
            case "library_get_task_projection":
                writer.WriteString("run_id", RequireString(name, payload, "run_id"));
                break;
            case "library_retry_failed_targets":
                writer.WriteString("run_id", RequireString(name, payload, "run_id"));
                writer.WriteString("idempotency_key", RequireString(name, payload, "idempotency_key"));
                break;
            case "library_start_export":
                writer.WriteString("book_id", RequireString(name, payload, "book_id"));
                writer.WritePropertyName("chapter_ids");
                WriteRequiredStringArray(writer, name, payload, "chapter_ids", requireNonEmpty: true);
                writer.WritePropertyName("ordered_page_ids");
                WriteRequiredStringArray(writer, name, payload, "ordered_page_ids", requireNonEmpty: true);
                writer.WriteString("format", RequireString(name, payload, "format"));
                writer.WritePropertyName("format_options");
                RequireObject(name, payload, "format_options").WriteTo(writer);
                writer.WriteString("stale_policy", RequireString(name, payload, "stale_policy"));
                writer.WriteString("target_ref", RequireString(name, payload, "target_ref"));
                break;
            case "library_cancel_export":
            case "library_get_export_snapshot":
                writer.WriteString("export_id", RequireString(name, payload, "export_id"));
                break;
            case "library_get_export_history":
                break;
            case "library_get_reader_projection":
                writer.WriteString("chapter_id", RequireString(name, payload, "chapter_id"));
                writer.WriteString("mode", RequireString(name, payload, "mode"));
                writer.WriteString("start_position", RequireString(name, payload, "start_position"));
                break;
            // NS-WIRE-B1 batch B1: the legacy Tauri signatures of the backup / cleanup / plugin /
            // permanent-delete / P15 settings faces. Required arguments are enforced at the dispatcher
            // boundary (INVALID_ARGUMENTS); optional ones are only sent when present, exactly like the
            // legacy json!() construction did. Nullable strings keep the explicit JSON null the Core
            // expects (proxy_endpoint).
            case "backup_delete":
                writer.WriteString("backup_id", RequireString(name, payload, "backup_id"));
                break;
            case "cleanup_retry_pending":
            case "settings_network_profile_default_clear":
                // Legacy signatures take no arguments; the Core faces reject stray payload keys.
                break;
            case "plugins_audit_list":
                WriteOptionalInt(writer, name, payload, "limit");
                break;
            case "plugins_set_plugin_enabled":
                writer.WriteString("plugin_id", RequireString(name, payload, "plugin_id"));
                writer.WriteBoolean("enabled", RequireBool(name, payload, "enabled"));
                break;
            case "library_delete_book_permanently":
            {
                // Legacy takes one optional object argument; accept the clipped object and the
                // inlined shape so both call styles keep working.
                var deletePayload = OptionalObject(name, payload, "payload") ?? payload;
                writer.WriteString("book_id", RequireString(name, deletePayload, "book_id"));
                writer.WriteBoolean(
                    "confirm_permanent_delete",
                    RequireBool(name, deletePayload, "confirm_permanent_delete"));
                break;
            }

            case "settings_network_profile_default_set":
                writer.WriteString("network_profile_id", RequireString(name, payload, "network_profile_id"));
                break;
            case "settings_network_profiles_create":
                writer.WriteString("display_name", RequireString(name, payload, "display_name"));
                writer.WriteString("mode", RequireString(name, payload, "mode"));
                WriteNullableString(writer, name, payload, "proxy_endpoint");
                WriteOptionalBool(writer, name, payload, "verify_tls");
                WriteOptionalBool(writer, name, payload, "confirm_disable_tls_verification");
                WriteOptionalBool(writer, name, payload, "allow_proxy_failure_direct_fallback");
                break;
            case "settings_network_profiles_update":
                writer.WriteString("network_profile_id", RequireString(name, payload, "network_profile_id"));
                writer.WriteString("display_name", RequireString(name, payload, "display_name"));
                writer.WriteString("mode", RequireString(name, payload, "mode"));
                WriteNullableString(writer, name, payload, "proxy_endpoint");
                writer.WriteBoolean("verify_tls", RequireBool(name, payload, "verify_tls"));
                WriteOptionalBool(writer, name, payload, "confirm_disable_tls_verification");
                writer.WriteBoolean(
                    "allow_proxy_failure_direct_fallback",
                    RequireBool(name, payload, "allow_proxy_failure_direct_fallback"));
                break;
            case "settings_network_profiles_delete":
                writer.WriteString("network_profile_id", RequireString(name, payload, "network_profile_id"));
                break;
            case "settings_provider_bindings_clear":
                writer.WritePropertyName("scope");
                RequireObject(name, payload, "scope").WriteTo(writer);
                writer.WriteString("capability", RequireString(name, payload, "capability"));
                break;
            case "settings_provider_bindings_resolve":
                writer.WriteString("capability", RequireString(name, payload, "capability"));
                WriteOptionalString(writer, name, payload, "book_id");
                WriteOptionalString(writer, name, payload, "chapter_id");
                WriteOptionalString(writer, name, payload, "run_id");
                break;
            case "settings_provider_run_snapshot_get":
                writer.WriteString("run_id", RequireString(name, payload, "run_id"));
                break;
            default:
                foreach (var property in payload.EnumerateObject())
                {
                    property.WriteTo(writer);
                }

                break;
        }

        writer.WriteEndObject();
    }

    private static void WriteRequiredStringArray(
        Utf8JsonWriter writer,
        string command,
        JsonElement args,
        string property,
        bool requireNonEmpty)
    {
        if (!args.TryGetProperty(property, out var value) ||
            value.ValueKind != JsonValueKind.Array ||
            value.GetArrayLength() == 0)
        {
            throw new HostCommandInvalidArgumentsException(command, $"missing required string[] argument '{property}'");
        }

        writer.WriteStartArray();
        foreach (var element in value.EnumerateArray())
        {
            if (element.ValueKind != JsonValueKind.String || string.IsNullOrEmpty(element.GetString()))
            {
                throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must contain non-empty strings");
            }

            writer.WriteStringValue(element.GetString());
        }

        writer.WriteEndArray();
    }

    private static JsonElement RequireObject(string command, JsonElement args, string property)
    {
        if (args.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Object)
        {
            return value;
        }

        throw new HostCommandInvalidArgumentsException(command, $"missing required object argument '{property}'");
    }

    private static bool RequireBool(string command, JsonElement args, string property)
    {
        if (args.TryGetProperty(property, out var value) &&
            value.ValueKind is JsonValueKind.True or JsonValueKind.False)
        {
            return value.GetBoolean();
        }

        throw new HostCommandInvalidArgumentsException(command, $"missing required boolean argument '{property}'");
    }

    private static string? OptionalString(string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind == JsonValueKind.String && value.GetString() is { Length: > 0 } text)
        {
            return text;
        }

        throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be a non-empty string");
    }

    private static void WriteOptionalString(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        var value = OptionalString(command, args, property);
        if (value is not null)
        {
            writer.WriteString(property, value);
        }
    }

    /// <summary>NS-WIRE-B1: nullable string that keeps an explicit JSON null (legacy Option&lt;String&gt;).</summary>
    private static void WriteNullableString(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            writer.WriteNull(property);
            return;
        }

        if (value.ValueKind == JsonValueKind.String && value.GetString() is { Length: > 0 } text)
        {
            writer.WriteString(property, text);
            return;
        }

        throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be a string or null");
    }

    private static void WriteOptionalBool(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind is JsonValueKind.True or JsonValueKind.False)
        {
            writer.WriteBoolean(property, value.GetBoolean());
            return;
        }

        throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be a boolean");
    }

    private static void WriteOptionalInt(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind == JsonValueKind.Number &&
            value.TryGetInt32(out var number) &&
            number >= 0)
        {
            writer.WriteNumber(property, number);
            return;
        }

        throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be a non-negative integer");
    }

    private static JsonElement? OptionalObject(string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind == JsonValueKind.Object)
        {
            return value;
        }

        throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be an object");
    }

    private static void WriteStringArray(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new HostCommandInvalidArgumentsException(command, $"missing required string[] argument '{property}'");
        }

        writer.WriteStartArray();
        foreach (var element in value.EnumerateArray())
        {
            if (element.ValueKind != JsonValueKind.String || string.IsNullOrEmpty(element.GetString()))
            {
                throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must contain non-empty strings");
            }

            writer.WriteStringValue(element.GetString());
        }

        writer.WriteEndArray();
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
