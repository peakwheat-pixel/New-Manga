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
    private readonly Func<string, JsonElement, CancellationToken, Task<HostCommandResult>>? _hostLocal;

    public HostCommandDispatcher(
        CoreServiceClient? core = null,
        HostBridgeClient? bridge = null,
        Func<string, JsonElement, CancellationToken, Task<HostCommandResult>>? hostLocal = null)
    {
        _core = core;
        _bridge = bridge;
        _hostLocal = hostLocal;
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
            HostCommandChannel.HostLocal when _hostLocal is not null => await _hostLocal(
                    descriptor.Name, payload, cancellationToken)
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
    ///
    /// V11R-F0-1: internal (instead of private) so the CoreClient test project can assert the exact
    /// written payload of the Region write commands without a live sidecar.
    /// </summary>
    internal static void WriteCorePayload(string name, JsonElement args, Utf8JsonWriter writer)
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
                // RUN-BINDING-FIX-1: carry Host-side default provider bindings (the frozen Core's
                // pipeline defaults are empty, so OCR otherwise fails PROVIDER_NOT_CONFIGURED).
                WriteStartRunOverrides(writer, name, payload);
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
            // NS-WIRE-B2: backup.restore is the B1 delete face's sibling. The Core handler refuses
            // anything but an explicit confirm_restore:true (BACKUP_RESTORE_REQUIRES_CONFIRMATION),
            // so the legacy boolean is required and forwarded verbatim.
            case "backup_restore":
                writer.WriteString("backup_id", RequireString(name, payload, "backup_id"));
                writer.WriteBoolean("confirm_restore", RequireBool(name, payload, "confirm_restore"));
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

            case "library_delete_books_permanently":
            {
                // NS-WIRE-B2: the batch permanent-delete face (protocol minor 10). The Core handler
                // requires the exact key set {book_ids, confirmed_book_ids, confirm_count,
                // confirm_permanent_delete} and rejects anything else with INVALID_REQUEST, so every
                // element is enforced here. Both the legacy inlined shape and the clipped
                // {"payload": {...}} shape are accepted, matching the single-book sibling.
                var deleteBooksPayload = OptionalObject(name, payload, "payload") ?? payload;
                writer.WritePropertyName("book_ids");
                WriteRequiredStringArray(writer, name, deleteBooksPayload, "book_ids", requireNonEmpty: true);
                writer.WritePropertyName("confirmed_book_ids");
                WriteRequiredStringArray(
                    writer,
                    name,
                    deleteBooksPayload,
                    "confirmed_book_ids",
                    requireNonEmpty: true);
                writer.WriteNumber(
                    "confirm_count",
                    RequireInt64(name, deleteBooksPayload, "confirm_count"));
                writer.WriteBoolean(
                    "confirm_permanent_delete",
                    RequireBool(name, deleteBooksPayload, "confirm_permanent_delete"));
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
            // NS-WIRE-B2 batch: the provider-profile CRUD, provider-binding write, network-diagnostic
            // and network-resolution faces. Payload keys mirror the legacy Tauri command signatures
            // (apps/desktop/src-tauri/src/settings_bridge.rs) one-to-one; network_profile_id stays an
            // explicit JSON null when the caller omits it (Core reads payload["network_profile_id"]).
            case "settings_provider_profiles_create":
                writer.WriteString("provider_id", RequireString(name, payload, "provider_id"));
                writer.WriteString("display_name", RequireString(name, payload, "display_name"));
                writer.WritePropertyName("capabilities");
                WriteRequiredStringArray(writer, name, payload, "capabilities", requireNonEmpty: true);
                writer.WriteString("endpoint", RequireString(name, payload, "endpoint"));
                writer.WriteString("model", RequireString(name, payload, "model"));
                WriteNullableString(writer, name, payload, "network_profile_id");
                writer.WriteBoolean("enabled", RequireBool(name, payload, "enabled"));
                break;
            case "settings_provider_profiles_update":
                writer.WriteString("profile_id", RequireString(name, payload, "profile_id"));
                writer.WriteString("display_name", RequireString(name, payload, "display_name"));
                writer.WritePropertyName("capabilities");
                WriteRequiredStringArray(writer, name, payload, "capabilities", requireNonEmpty: true);
                writer.WriteString("endpoint", RequireString(name, payload, "endpoint"));
                writer.WriteString("model", RequireString(name, payload, "model"));
                WriteNullableString(writer, name, payload, "network_profile_id");
                writer.WriteBoolean("enabled", RequireBool(name, payload, "enabled"));
                break;
            case "settings_provider_profiles_delete":
                writer.WriteString("profile_id", RequireString(name, payload, "profile_id"));
                break;
            case "settings_provider_bindings_set":
                writer.WritePropertyName("scope");
                RequireObject(name, payload, "scope").WriteTo(writer);
                writer.WriteString("capability", RequireString(name, payload, "capability"));
                writer.WriteString("profile_id", RequireString(name, payload, "profile_id"));
                break;
            case "settings_network_profiles_test":
                writer.WriteString("network_profile_id", RequireString(name, payload, "network_profile_id"));
                WriteOptionalString(writer, name, payload, "provider_profile_id");
                break;
            case "settings_network_profile_resolve":
                WriteOptionalString(writer, name, payload, "provider_profile_id");
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
            // S4-CMD-BATCH-1: region write face + reader progress face. The legacy Tauri signatures
            // are enforced here; the Core payload keys are identical to the wire contract.
            case "list_region_revisions":
                // NS-WIRE-B2: the legacy signature is a bare region_id (main.rs::list_region_revisions
                // forwards json!({"region_id": region_id})), so the wire payload is the same one key.
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                break;
            case "set_region_type":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                writer.WriteString("new_region_type", RequireString(name, payload, "new_region_type"));
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "restore_region_revision":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                writer.WriteNumber("revision_no", RequirePositiveInt64(name, payload, "revision_no"));
                writer.WriteNumber("expected_revision", RequireInt64(name, payload, "expected_revision"));
                break;
            case "rerender_page":
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                break;
            case "resolve_page_resource":
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                break;
            // V11R-F0-1: the Region write face (audit §5.1 F-01). The payload
            // keys are exactly the ones bootstrap/core_service.py validates;
            // required arguments are enforced here (INVALID_ARGUMENTS before
            // any Core frame), optional ones ride only when present. Geometry
            // is the editable normalized point list owned by the
            // application/editing/region_canvas.py mapping.
            case "create_region":
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                WriteOptionalString(writer, name, payload, "region_type");
                WriteOptionalPositiveInt64(writer, name, payload, "reading_order");
                WriteGeometryPayload(writer, name, payload, "geometry");
                break;
            case "delete_region":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "save_region_geometry":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                WriteGeometryPayload(writer, name, payload, "geometry");
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "merge_regions":
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                writer.WritePropertyName("region_ids");
                WriteRequiredStringArray(writer, name, payload, "region_ids", minimum: 2);
                WriteOptionalRevisionsMap(writer, name, payload, "expected_revisions");
                break;
            case "split_region":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                WriteGeometryPartsPayload(writer, name, payload, "parts");
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "reorder_regions":
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                writer.WritePropertyName("ordered_region_ids");
                WriteRequiredStringArray(writer, name, payload, "ordered_region_ids");
                WriteOptionalRevisionsMap(writer, name, payload, "expected_revisions");
                break;
            case "save_manual_translation":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                writer.WriteString("edited_translation", RequireText(name, payload, "edited_translation"));
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "confirm_region_final":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "set_region_lock":
                RequireAnyLockProperty(name, payload);
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                WriteOptionalBool(writer, name, payload, "region_locked");
                WriteOptionalBool(writer, name, payload, "translation_locked");
                WriteOptionalBool(writer, name, payload, "inpaint_locked");
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            case "pin_revision":
                writer.WriteString("region_id", RequireString(name, payload, "region_id"));
                writer.WriteNumber("revision_no", RequirePositiveInt64(name, payload, "revision_no"));
                writer.WriteBoolean("pinned", RequireBool(name, payload, "pinned"));
                WriteOptionalPositiveInt64(writer, name, payload, "expected_revision");
                break;
            // V11R-F0-2: the page-scoped Region text read projection. The
            // optional strict region filter is enforced as non-empty distinct
            // strings at the boundary; the Core additionally proves each id is
            // a live region of that page (TARGET_NOT_FOUND otherwise).
            case "list_page_region_texts":
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                WriteOptionalStringArray(writer, name, payload, "region_ids");
                break;
            case "library_save_reading_progress":
                writer.WriteString("chapter_id", RequireString(name, payload, "chapter_id"));
                writer.WriteString("mode", RequireString(name, payload, "mode"));
                writer.WriteString("page_id", RequireString(name, payload, "page_id"));
                WriteOptionalDouble(writer, name, payload, "scroll_offset_y");
                WriteOptionalDouble(writer, name, payload, "elapsed_seconds_delta");
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
        bool requireNonEmpty = true,
        int minimum = 1)
    {
        var minimumCount = Math.Max(requireNonEmpty ? 1 : 0, minimum);
        if (!args.TryGetProperty(property, out var value) ||
            value.ValueKind != JsonValueKind.Array ||
            value.GetArrayLength() < minimumCount)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"missing required string[] argument '{property}'");
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

    /// <summary>
    /// V11R-F0-2: the optional strict region filter of
    /// <c>list_page_region_texts</c> (non-empty distinct strings; omitted /
    /// null when the caller wants the whole page).
    /// </summary>
    private static void WriteOptionalStringArray(
        Utf8JsonWriter writer,
        string command,
        JsonElement args,
        string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind != JsonValueKind.Array || value.GetArrayLength() == 0)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' must be a non-empty string[] when present");
        }

        var seen = new HashSet<string>(StringComparer.Ordinal);
        writer.WritePropertyName(property);
        writer.WriteStartArray();
        foreach (var element in value.EnumerateArray())
        {
            if (element.ValueKind != JsonValueKind.String ||
                element.GetString() is not { Length: > 0 } text ||
                !seen.Add(text))
            {
                throw new HostCommandInvalidArgumentsException(
                    command, $"argument '{property}' must contain distinct non-empty strings");
            }

            writer.WriteStringValue(text);
        }

        writer.WriteEndArray();
    }

    /// <summary>
    /// V11R-F0-1: the Region write face's normalized canvas geometry payload
    /// ({"points": [[x, y], ...]}); the Core converts the points to page
    /// pixels through application/editing/region_canvas.py.
    /// </summary>
    private static void WriteGeometryPayload(
        Utf8JsonWriter writer,
        string command,
        JsonElement args,
        string property)
    {
        var geometry = RequireObject(command, args, property);
        if (!geometry.TryGetProperty("points", out var points))
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"missing required point array '{property}.points'");
        }

        writer.WritePropertyName(property);
        writer.WriteStartObject();
        writer.WritePropertyName("points");
        WritePointArray(writer, command, points, $"{property}.points", minimum: 2);
        writer.WriteEndObject();
    }

    /// <summary>
    /// V11R-F0-1: split parts ([[[x, y], ...], ...]); at least two parts, each
    /// with at least two points.
    /// </summary>
    private static void WriteGeometryPartsPayload(
        Utf8JsonWriter writer,
        string command,
        JsonElement args,
        string property)
    {
        if (!args.TryGetProperty(property, out var parts) ||
            parts.ValueKind != JsonValueKind.Array ||
            parts.GetArrayLength() < 2)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"missing required parts argument '{property}' (at least two point lists)");
        }

        writer.WritePropertyName(property);
        writer.WriteStartArray();
        var index = 0;
        foreach (var part in parts.EnumerateArray())
        {
            index += 1;
            WritePointArray(writer, command, part, $"{property}[{index}]", minimum: 2);
        }

        writer.WriteEndArray();
    }

    private static void WritePointArray(
        Utf8JsonWriter writer,
        string command,
        JsonElement array,
        string label,
        int minimum)
    {
        if (array.ValueKind != JsonValueKind.Array || array.GetArrayLength() < minimum)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{label}' needs at least {minimum} [x, y] points");
        }

        writer.WriteStartArray();
        foreach (var point in array.EnumerateArray())
        {
            if (point.ValueKind != JsonValueKind.Array || point.GetArrayLength() != 2)
            {
                throw new HostCommandInvalidArgumentsException(
                    command, $"argument '{label}' points must be [x, y] pairs");
            }

            writer.WriteStartArray();
            foreach (var axis in point.EnumerateArray())
            {
                if (axis.ValueKind != JsonValueKind.Number ||
                    !axis.TryGetDouble(out var value) ||
                    double.IsNaN(value) ||
                    double.IsInfinity(value))
                {
                    throw new HostCommandInvalidArgumentsException(
                        command, $"argument '{label}' coordinates must be finite numbers");
                }

                // I1/P2-5: the wire geometry is NORMALIZED (0..1); an
                // out-of-range coordinate is a domain-invalid argument and
                // must fail here, before any Core frame.
                if (value < 0 || value > 1)
                {
                    throw new HostCommandInvalidArgumentsException(
                        command,
                        $"argument '{label}' coordinates must be normalized within [0, 1]");
                }

                writer.WriteNumberValue(value);
            }

            writer.WriteEndArray();
        }

        writer.WriteEndArray();
    }

    /// <summary>
    /// V11R-F0-1: the multi-region optimistic guard
    /// ({"region_id": revision_no, ...}); values are enforced as integers here,
    /// the Core validates that the map covers exactly the affected regions.
    /// </summary>
    private static void WriteOptionalRevisionsMap(
        Utf8JsonWriter writer,
        string command,
        JsonElement args,
        string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind != JsonValueKind.Object)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' must be an object");
        }

        writer.WritePropertyName(property);
        writer.WriteStartObject();
        foreach (var entry in value.EnumerateObject())
        {
            if (string.IsNullOrEmpty(entry.Name) ||
                entry.Value.ValueKind != JsonValueKind.Number ||
                !entry.Value.TryGetInt64(out var revisionNo) ||
                revisionNo <= 0)
            {
                throw new HostCommandInvalidArgumentsException(
                    command, $"argument '{property}' must map non-empty region ids to POSITIVE integer revision numbers");
            }

            writer.WriteNumber(entry.Name, revisionNo);
        }

        writer.WriteEndObject();
    }

    /// <summary>V11R-F0-1: a text argument that may be an empty string (clearing a manual edit).</summary>
    private static string RequireText(string command, JsonElement args, string property)
    {
        if (args.ValueKind == JsonValueKind.Object &&
            args.TryGetProperty(property, out var value) &&
            value.ValueKind == JsonValueKind.String)
        {
            return value.GetString()!;
        }

        throw new HostCommandInvalidArgumentsException(command, $"missing required text argument '{property}'");
    }

    /// <summary>
    /// V11R-F0-1: ``set_region_lock`` must name at least one of the three
    /// locks (the Core rejects an empty lock set with INVALID_REQUEST; the
    /// dispatcher fails closed before any frame). The value TYPE is enforced by
    /// WriteOptionalBool per property.
    /// </summary>
    private static void RequireAnyLockProperty(string command, JsonElement args)
    {
        foreach (var property in new[] { "region_locked", "translation_locked", "inpaint_locked" })
        {
            if (args.TryGetProperty(property, out var value) && value.ValueKind != JsonValueKind.Null)
            {
                return;
            }
        }

        throw new HostCommandInvalidArgumentsException(
            command,
            "requires at least one of 'region_locked' / 'translation_locked' / 'inpaint_locked'");
    }

    /// <summary>
    /// V11R-F0-1 I1/P2-5: required positive integer (revision numbers are
    /// 1-based; a 0/negative value is a domain-invalid argument and must be
    /// rejected BEFORE any frame instead of round-tripping to the Core).
    /// </summary>
    private static long RequirePositiveInt64(string command, JsonElement args, string property)
    {
        var value = RequireInt64(command, args, property);
        if (value <= 0)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' must be a positive integer");
        }

        return value;
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

    /// <summary>
    /// RUN-BINDING-FIX-1: writes StartRun's <c>overrides</c> object with the Host-side default
    /// provider bindings merged in. Priority: explicit <c>overrides.provider_bindings</c> from the
    /// caller always wins (never merged/overwritten); otherwise the configured default is injected
    /// (default <c>{"ocr":"manga-ocr"}`, disabled through <see cref="RunBindingDefaults"/>). Other
    /// caller overrides are preserved. A non-object <c>overrides</c>/<c>provider_bindings</c> is a
    /// typed INVALID_ARGUMENTS rejection before any Core frame is sent.
    /// </summary>
    private static void WriteStartRunOverrides(Utf8JsonWriter writer, string command, JsonElement args)
    {
        JsonElement? userOverrides = null;
        if (args.TryGetProperty("overrides", out var overrides) && overrides.ValueKind != JsonValueKind.Null)
        {
            if (overrides.ValueKind != JsonValueKind.Object)
            {
                throw new HostCommandInvalidArgumentsException(command, "argument 'overrides' must be an object");
            }

            userOverrides = overrides;
        }

        JsonElement? userBindings = null;
        if (userOverrides is { } present &&
            present.TryGetProperty("provider_bindings", out var bindings) &&
            bindings.ValueKind != JsonValueKind.Null)
        {
            if (bindings.ValueKind != JsonValueKind.Object)
            {
                throw new HostCommandInvalidArgumentsException(
                    command,
                    "argument 'overrides.provider_bindings' must be an object");
            }

            userBindings = bindings;
        }

        // Only consult the environment when the caller did not provide explicit bindings.
        var defaults = userBindings is null ? RunBindingDefaults.Resolve() : null;
        if (userOverrides is null && userBindings is null && defaults is null)
        {
            return;
        }

        writer.WritePropertyName("overrides");
        writer.WriteStartObject();
        if (userOverrides is { } source)
        {
            foreach (var property in source.EnumerateObject())
            {
                if (property.NameEquals("provider_bindings"))
                {
                    continue;
                }

                property.WriteTo(writer);
            }
        }

        if (userBindings is { } explicitBindings)
        {
            writer.WritePropertyName("provider_bindings");
            explicitBindings.WriteTo(writer);
        }
        else if (defaults is { } defaultBindings)
        {
            writer.WritePropertyName("provider_bindings");
            defaultBindings.WriteTo(writer);
        }

        writer.WriteEndObject();
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

    private static long RequireInt64(string command, JsonElement args, string property)
    {
        if (args.ValueKind == JsonValueKind.Object &&
            args.TryGetProperty(property, out var value) &&
            value.ValueKind == JsonValueKind.Number &&
            value.TryGetInt64(out var number))
        {
            return number;
        }

        throw new HostCommandInvalidArgumentsException(command, $"missing required integer argument '{property}'");
    }

    private static void WriteOptionalInt64(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt64(out var number))
        {
            throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be an integer");
        }

        writer.WriteNumber(property, number);
    }

    /// <summary>
    /// V11R-F0-1 I1/P2-5: optional 1-based integer (``expected_revision`` /
    /// ``reading_order``): present =&gt; strictly positive, so domain-invalid
    /// values fail at the dispatcher boundary before any Core frame.
    /// </summary>
    private static void WriteOptionalPositiveInt64(
        Utf8JsonWriter writer,
        string command,
        JsonElement args,
        string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind != JsonValueKind.Number ||
            !value.TryGetInt64(out var number) ||
            number <= 0)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' must be a positive integer");
        }

        writer.WriteNumber(property, number);
    }

    private static void WriteOptionalDouble(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind != JsonValueKind.Number || !value.TryGetDouble(out var number) ||
            double.IsNaN(number) || double.IsInfinity(number))
        {
            throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be a finite number");
        }

        writer.WriteNumber(property, number);
    }

    private static void WriteStringArray(Utf8JsonWriter writer, string command, JsonElement args, string property)    {
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
