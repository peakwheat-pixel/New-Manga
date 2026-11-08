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
    // I2/P2-E: the Region write face's bounded input limits (contract v1.3
    // §1.3/§2). The SAME numbers are enforced by the Core before persistence;
    // rejecting them here keeps obviously-invalid requests from ever opening a
    // long write transaction.
    private const int MaxRegionsPerPage = 500;
    private const int MaxRegionIdsPerBatch = 64;
    private const int MaxSplitParts = 64;
    private const int MaxGeometryPoints = 512;

    // FEA-12-PREREQ-1 / M2-C1 §5.13: the read-only delete preview accepts 1..20 book ids,
    // exactly like the frozen batch delete limit (§5.11.2).
    private const int MaxBookDeleteBatchSize = 20;

    private readonly CoreServiceClient? _core;
    private readonly HostBridgeClient? _bridge;
    private readonly Func<string, JsonElement, CancellationToken, Task<HostCommandResult>>? _hostLocal;

    /// <summary>FEA-11 (C-17 §5.2): Host-injected durable journal. The Host
    /// begins/authorizes the operation, runs the Core call it receives, and
    /// returns (operation_id, core result).</summary>
    private readonly Func<
        string,
        JsonElement,
        Func<JsonElement, CancellationToken, Task<CoreResponse>>,
        CancellationToken,
        Task<(string OperationId, JsonElement Result)>>? _journal;

    /// <summary>FEA-11 (C-17 §3.2): ACK/recovery/failure are Host-coordinated;
    /// the delegate owns the Core call and the durable journal transition.</summary>
    private readonly Func<string, JsonElement, CancellationToken, Task<JsonElement>>? _operationJournal;

    /// <summary>FEA-11 (C-17 §4): the sync capability probe gate runs before
    /// dispatch for sync commands that do not ride the operation journal
    /// (scan). Missing capabilities must fail closed, never UNKNOWN_COMMAND.</summary>
    private readonly Func<string, CancellationToken, Task>? _capabilityGate;

    /// <summary>
    /// FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4 / R-4): the Run pre-dispatch
    /// source-read authorization hook. It runs before the Core dispatch for
    /// every Run command that triggers step execution; a typed authorization
    /// failure (or a Host-side source refusal) means the Run command is NEVER
    /// dispatched and that exact typed code reaches the caller (R-5).
    /// </summary>
    private readonly Func<string, JsonElement, CancellationToken, Task>? _runAuthorize;

    /// <summary>
    /// FEA-11-RUN-GRANT-2C (C-16 v1.6 §2.4): the result-returning variant of the Run pre-dispatch
    /// hook. It performs the same best-effort authorization as <see cref="_runAuthorize"/> but also
    /// returns the Host-owned authorization summary (the frozen command/scope plus counts) that the
    /// post-dispatch hook uses to start the renewal loop. The payload is opaque to this project
    /// (Host-owned JSON) and NEVER becomes a wire field or an App surface.
    /// </summary>
    private readonly Func<string, JsonElement, CancellationToken, Task<JsonElement?>>? _runAuthorizeWithResult;

    /// <summary>
    /// FEA-11-RUN-GRANT-2C (D-5): the Host-internal post-dispatch hook for the Run commands. It runs
    /// AFTER the Core accepted the command (the result is already produced); a hook failure never
    /// changes that result. Zero wire change, zero new command, zero App surface — the renewal it may
    /// start is Host-internal.
    /// </summary>
    private readonly Func<string, JsonElement, JsonElement, JsonElement?, CancellationToken, Task>?
        _runDispatched;

    /// <summary>The Run commands that trigger step execution (R-4). Read-only
    /// Run commands (get snapshot/projection) are deliberately absent.</summary>
    public static IReadOnlySet<string> RunAuthorizationCommands { get; } = new HashSet<string>(
        StringComparer.Ordinal)
    {
        "library_start_run",
        "library_control_run",
        "library_resume_blocked_run",
        "library_retry_failed_targets",
    };

    public HostCommandDispatcher(
        CoreServiceClient? core = null,
        HostBridgeClient? bridge = null,
        Func<string, JsonElement, CancellationToken, Task<HostCommandResult>>? hostLocal = null,
        Func<string, JsonElement, Func<JsonElement, CancellationToken, Task<CoreResponse>>, CancellationToken,
            Task<(string OperationId, JsonElement Result)>>? journal = null,
        Func<string, JsonElement, CancellationToken, Task<JsonElement>>? operationJournal = null,
        Func<string, CancellationToken, Task>? capabilityGate = null,
        Func<string, JsonElement, CancellationToken, Task>? runAuthorize = null,
        Func<string, JsonElement, CancellationToken, Task<JsonElement?>>? runAuthorizeWithResult = null,
        Func<string, JsonElement, JsonElement, JsonElement?, CancellationToken, Task>? runDispatched = null)
    {
        _core = core;
        _bridge = bridge;
        _hostLocal = hostLocal;
        _journal = journal;
        _operationJournal = operationJournal;
        _capabilityGate = capabilityGate;
        _runAuthorize = runAuthorize;
        _runAuthorizeWithResult = runAuthorizeWithResult;
        _runDispatched = runDispatched;
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

        // FEA-12-CORE / M2-C1 §5.13/§5.14 + R-002 option (b): capability-gated commands are probed
        // BEFORE the dispatch try-block. A missing capability is a Host protocol verdict, not a Core
        // application error, so it must bypass ProjectDeleteTrashError (which would degrade it to
        // category=unknown and hide the protocol taxonomy from the UI). The probe is the injected
        // Host gate (HostRuntime) or, when the Host did not inject one, the CoreClient's own
        // core.ping probe -- never the command itself (UNKNOWN_COMMAND is not a probe channel).
        var requiredCapabilities = HostCommandRegistry.RequiredCapabilities(descriptor.Name);
        if (requiredCapabilities.Count > 0)
        {
            if (_capabilityGate is { } capabilityGate)
            {
                await capabilityGate(descriptor.Name, cancellationToken).ConfigureAwait(false);
            }
            else if (_core is { } probeCore)
            {
                await probeCore.RequireCapabilitiesAsync(requiredCapabilities, cancellationToken)
                    .ConfigureAwait(false);
            }
            else
            {
                // Fail closed: without a Core channel there is no legal way to verify the
                // capabilities, so the command must not be dispatched unprobed.
                throw new CoreOperationException(
                    "CORE_CAPABILITY_MISSING", "protocol", false,
                    "no Core channel available to probe required capabilities", null);
            }
        }

        try
        {
            // FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4 / R-4/R-5): authorize the
            // Run's source reads BEFORE any dispatch. A typed authorization
            // failure propagates out of this try-block (the Run projection
            // keeps its code; no new Run-face code is introduced) and the Core
            // Run command is never sent.
            // FEA-11-RUN-GRANT-2C: the result-returning variant additionally hands the Host-owned
            // authorization summary to the post-dispatch hook (renewal start), never to the wire.
            var runCommand = RunAuthorizationCommands.Contains(descriptor.Name);
            JsonElement? authorization = null;
            if (runCommand && _runAuthorizeWithResult is { } runAuthorizeWithResult)
            {
                authorization = await runAuthorizeWithResult(descriptor.Name, payload, cancellationToken)
                    .ConfigureAwait(false);
            }
            else if (runCommand && _runAuthorize is { } runAuthorize)
            {
                await runAuthorize(descriptor.Name, payload, cancellationToken)
                    .ConfigureAwait(false);
            }

            var result = descriptor.Channel switch
            {
                HostCommandChannel.CoreService => await InvokeCoreAsync(descriptor, payload, cancellationToken)
                    .ConfigureAwait(false),

                HostCommandChannel.CoreHostControl => await InvokeHostControlAsync(descriptor, payload, cancellationToken)
                    .ConfigureAwait(false),
                HostCommandChannel.HostBridge => await InvokeBridgeAsync(descriptor, payload, cancellationToken)
                    .ConfigureAwait(false),
                HostCommandChannel.HostLocal when _hostLocal is not null => await _hostLocal(
                        descriptor.Name, payload, cancellationToken)
                    .ConfigureAwait(false),
                _ => throw new HostCommandNotSupportedException(descriptor),
            };

            // FEA-11-RUN-GRANT-2C: the Host-internal post-dispatch hook. It never changes the already
            // produced Core result, and its own failure is a best-effort skip (the Run was dispatched).
            if (runCommand && _runDispatched is { } runDispatched)
            {
                try
                {
                    await runDispatched(
                            descriptor.Name, payload, result.Value, authorization, cancellationToken)
                        .ConfigureAwait(false);
                }
                catch (Exception error) when (error is not OperationCanceledException)
                {
                    // Best-effort Host bookkeeping only; the dispatch already succeeded.
                    _ = error;
                }
            }

            return result;
        }
        catch (CoreOperationException error) when (HostCommandRegistry.IsRunCommand(name))
        {
            throw ProjectRunError(error, HostCommandRegistry.AllowedRunErrorCodes);
        }
        catch (CoreOperationException error) when (HostCommandRegistry.IsDeleteTrashCommand(name))
        {
            throw ProjectDeleteTrashError(error, HostCommandRegistry.AllowedDeleteTrashErrorCodes);
        }
    }

    /// <summary>Host projection only. Unknown codes are diagnostic, never UI action selectors.
    /// The explicit registration set also permits a pre-registration compatibility check.
    /// No recovery or retry action is executed by this projection.</summary>
    public static CoreOperationException ProjectRunError(
        CoreOperationException error, IReadOnlySet<string> allowedRunErrorCodes)
    {
        if (!allowedRunErrorCodes.Contains(error.Code))
        {
            return new CoreOperationException(
                error.Code, "unknown", false, "Run operation failed", error.RequestId);
        }

        // Normative C-08 values apply only AFTER registration, regardless of source taxonomy.
        return error.Code switch
        {
            "RUN_STALE_PREVIEW" => new(error.Code, "conflict", false,
                "Run preview is stale; prepare again", error.RequestId),
            "RUN_PREVIEW_EXPIRED" => new(error.Code, "conflict", false,
                "Run preview expired; prepare again", error.RequestId),
            "RUN_SNAPSHOT_INCOMPLETE" => new(error.Code, "unavailable", true,
                "Run snapshot is incomplete", error.RequestId),
            _ => error, // Existing registered command-level mappings remain unchanged.
        };
    }

    /// <summary>
    /// FEA-12-PREREQ-1 / M2-C1 rev 2.13: Host projection for the delete/trash family. This is the
    /// C-08 <c>AllowedRunErrorCodes</c> pattern extended to delete: a code outside the allow-list
    /// keeps its ORIGINAL <c>code</c> string and is projected as <c>category=unknown</c> /
    /// <c>retryable=false</c> — diagnostic only, never a UI branch, retry or recovery selector.
    /// Registered rev 2.13 codes take the frozen C-04b/C-09 category+retryable. Every other
    /// registered code keeps its existing command-level projection unchanged.
    /// </summary>
    public static CoreOperationException ProjectDeleteTrashError(
        CoreOperationException error, IReadOnlySet<string> allowedDeleteTrashErrorCodes)
    {
        if (!allowedDeleteTrashErrorCodes.Contains(error.Code))
        {
            return new CoreOperationException(
                error.Code, "unknown", false, "Delete operation failed", error.RequestId);
        }

        return error.Code switch
        {
            "BOOK_DELETE_STALE_PREVIEW" => new(error.Code, "conflict", false,
                "Permanent-delete preview is stale; preview again", error.RequestId),
            "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE" => new(error.Code, "unavailable", true,
                "Protection inventory is unavailable", error.RequestId),
            "TRASH_ENTRY_NOT_FOUND" => new(error.Code, "not_found", false,
                "Trash entry was not found", error.RequestId),
            "TRASH_RESTORE_CONFLICT" => new(error.Code, "conflict", false,
                "Trash restore conflict", error.RequestId),
            "TRASH_RESTORE_LAYER_MISMATCH" => new(error.Code, "conflict", false,
                "Trash restore layer mismatch", error.RequestId),
            _ => error, // Existing registered command-level mappings remain unchanged.
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

    private async Task<HostCommandResult> InvokeHostControlAsync(
        HostCommandDescriptor descriptor,
        JsonElement args,
        CancellationToken cancellationToken)
    {
        var capabilityGate = _capabilityGate;
        if (capabilityGate is not null && descriptor.Name == "source_scan_sync")
        {
            await capabilityGate(descriptor.Name, cancellationToken).ConfigureAwait(false);
        }

        var operationJournal = _operationJournal;
        if (operationJournal is not null
            && HostCommandRegistry.IsSourceOperationCompletion(descriptor.Name))
        {
            var result = await operationJournal(descriptor.Name, args, cancellationToken)
                .ConfigureAwait(false);
            return new HostCommandResult(
                descriptor.Name, descriptor.Status, descriptor.Channel, result);
        }

        var journal = _journal;
        if (journal is not null && HostCommandRegistry.IsSourceSyncWrite(descriptor.Name))
        {
            // The journal delegate owns the ordering *and* the final payload:
            // the Host injects the operation_id/host authorization it minted
            // (C-17 §5.2), then hands the payload back for the Core call.
            var coreForJournal = _core;
            Func<JsonElement, CancellationToken, Task<CoreResponse>> call = coreForJournal is null
                ? (_, _) => throw new SidecarException(
                    SidecarErrorCode.ProcessExited,
                    SidecarSpec.CoreServiceName,
                    $"{descriptor.Name} requires a running core_service")
                : (finalPayload, ct) => coreForJournal.SendHostControlAsync(
                    descriptor.CoreCommand!,
                    writer => WriteFlattened(finalPayload, writer),
                    TimeSpan.FromSeconds(120),
                    coreForJournal.HostSession,
                    ct);
            var (operationId, result) = await journal(
                    descriptor.Name,
                    args,
                    call,
                    cancellationToken)
                .ConfigureAwait(false);
            var merged = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
            {
                ["operation_id"] = operationId,
                ["result"] = result.ValueKind == JsonValueKind.Undefined ? null : result.Clone(),
            });
            return new HostCommandResult(descriptor.Name, descriptor.Status, descriptor.Channel, merged);
        }

        var core = _core
            ?? throw new SidecarException(
                SidecarErrorCode.ProcessExited,
                SidecarSpec.CoreServiceName,
                $"{descriptor.Name} requires a running core_service");

        var response = await core.SendHostControlAsync(
                descriptor.CoreCommand!,
                writer => WriteHostControlPayload(descriptor.Name, args, writer),
                TimeSpan.FromSeconds(60),
                core.HostSession,
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
    /// FEA-11-RESIDUAL-4A D-1 (authorized fix): the HOST-CONTROL payload writer.
    ///
    /// <c>CoreServiceClient.SendHostControlAsync</c> has ALREADY opened the
    /// envelope's <c>"payload"</c> object (CoreServiceClient.cs:585-588), so a
    /// host-control payload callback must write the payload's FIELDS into that
    /// object — never a second complete object. Before this fix the host-control
    /// branch handed <see cref="WriteCorePayload"/> (which writes its own
    /// <c>WriteStartObject</c>/<c>WriteEndObject</c>) to that callback, so the
    /// Core received a doubly nested / malformed payload and answered
    /// <c>INVALID_JSON</c>; the same defect class as the R1 ACK/recovery
    /// six-field flattening in <c>SourceOperationCoordinator</c>.
    ///
    /// The unchanged <see cref="WriteCorePayload"/> stays the APP-channel
    /// writer (<c>CoreServiceClient.SendAsync</c> expects a complete payload
    /// object), so the frozen wire shapes of the application channel are
    /// untouched.
    /// </summary>
    private static void WriteHostControlPayload(
        string name, JsonElement args, Utf8JsonWriter writer)
    {
        var buffer = new System.Buffers.ArrayBufferWriter<byte>();
        using (var probe = new Utf8JsonWriter(buffer))
        {
            WriteCorePayload(name, args, probe);
        }
        using var document = JsonDocument.Parse(buffer.WrittenMemory);
        WriteFlattened(document.RootElement, writer);
    }

    /// <summary>Write the FIELDS of one payload object into an already-opened
    /// payload object (the host-control envelope contract).</summary>
    private static void WriteFlattened(JsonElement payload, Utf8JsonWriter writer)
    {
        if (payload.ValueKind != JsonValueKind.Object)
        {
            return;
        }
        foreach (var property in payload.EnumerateObject())
        {
            property.WriteTo(writer);
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
                // FEA-12-PREREQ-1 / M2-C1 rev 2.13 §5.11.1a: additive digest passthrough only --
                // never synthesized or enforced here (the Core stays the semantic authority), and
                // the per-command wire minor stays 10. Optional: a legacy caller that omits it is
                // still forwarded unchanged (the new Core fail-closes with INVALID_REQUEST).
                WriteOptionalString(writer, name, deletePayload, "inventory_digest");
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
                // FEA-12-PREREQ-1 / M2-C1 rev 2.13 §5.11.1a: additive set-level + per-book digest
                // passthrough (two-level binding is Core's job; the wire minor stays 10).
                WriteOptionalString(writer, name, deleteBooksPayload, "inventory_digest");
                WriteOptionalDigestMap(writer, name, deleteBooksPayload, "inventory_digests");
                break;
            }

            // FEA-12-PREREQ-1 / M2-C1 rev 2.13 (§5.13/§5.14): the delete preview and the trash
            // command family. These are NEW commands, so the dispatcher enforces a strict closed
            // shape (unknown keys fail before any Core frame). Registration only: the frozen Core
            // has no handler for them yet and the runtime capability probe belongs to FEA-12-CORE.
            case "library_preview_permanent_delete_books":
                RejectUnknownKeys(name, payload, "bookIds");
                writer.WritePropertyName("bookIds");
                WriteBookIdArray(writer, name, payload, "bookIds");
                break;
            case "library_move_to_trash":
            case "library_restore_from_trash":
                RejectUnknownKeys(name, payload, "entries", "idempotency_key");
                writer.WritePropertyName("entries");
                WriteTrashEntries(writer, name, payload);
                writer.WriteString("idempotency_key", RequireString(name, payload, "idempotency_key"));
                break;
            case "library_list_trash":
                RejectUnknownKeys(name, payload, "cursor", "limit");
                WriteOptionalString(writer, name, payload, "cursor");
                WriteOptionalPositiveInt64(writer, name, payload, "limit");
                break;
            case "library_purge_trash":
                RejectUnknownKeys(name, payload, "entries", "confirm", "idempotency_key");
                if (!RequireBool(name, payload, "confirm"))
                {
                    throw new HostCommandInvalidArgumentsException(
                        name, "argument 'confirm' must be true (PurgeTrash is not a soft delete)");
                }

                writer.WritePropertyName("entries");
                WriteTrashEntries(writer, name, payload);
                writer.WriteBoolean("confirm", true);
                writer.WriteString("idempotency_key", RequireString(name, payload, "idempotency_key"));
                break;

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
                WriteRequiredStringArray(writer, name, payload, "region_ids", minimum: 2, maximum: MaxRegionIdsPerBatch);
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
                WriteRequiredStringArray(writer, name, payload, "ordered_region_ids", minimum: 1, maximum: MaxRegionsPerPage);
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
            // FEA-05-PORT-1: Draft family (C078-C083). Explicit cases keep the fail-closed
            // discipline (no default pass-through of unknown Draft args); payload keys are
            // camelCase and converted to the Core snake_case faces by the handler.
            case "drafts_open":
                writer.WriteString("sessionId", RequireString(name, payload, "sessionId"));
                writer.WriteString("pageId", RequireString(name, payload, "pageId"));
                WriteOptionalString(writer, name, payload, "regionId");
                WriteOptionalString(writer, name, payload, "baseRevisionId");
                writer.WriteNumber("pageBindingVersion", RequireNumber(name, payload, "pageBindingVersion"));
                break;
            case "drafts_patch":
                writer.WriteString("draftId", RequireString(name, payload, "draftId"));
                writer.WriteString("sessionId", RequireString(name, payload, "sessionId"));
                writer.WritePropertyName("patch");
                RequireObject(name, payload, "patch").WriteTo(writer);
                WriteOptionalNumber(writer, name, payload, "undoCursor");
                break;
            case "drafts_prepare":
                writer.WriteString("regionId", RequireString(name, payload, "regionId"));
                writer.WritePropertyName("patch");
                RequireObject(name, payload, "patch").WriteTo(writer);
                writer.WriteString("origin", RequireString(name, payload, "origin"));
                WriteOptionalString(writer, name, payload, "draftId");
                WriteOptionalString(writer, name, payload, "baseRevisionId");
                break;
            case "drafts_apply":
                writer.WritePropertyName("token");
                RequireObject(name, payload, "token").WriteTo(writer);
                writer.WritePropertyName("candidateIds");
                WriteStringArray(writer, name, payload, "candidateIds");
                break;
            case "drafts_status":
                if (payload.TryGetProperty("draftId", out _) == payload.TryGetProperty("sessionId", out _))
                {
                    throw new HostCommandInvalidArgumentsException(name, "exactly one of 'draftId' or 'sessionId' is required");
                }
                if (payload.TryGetProperty("draftId", out _))
                {
                    writer.WriteString("draftId", RequireString(name, payload, "draftId"));
                }
                else
                {
                    writer.WriteString("sessionId", RequireString(name, payload, "sessionId"));
                }
                break;
            case "drafts_discard":
                writer.WriteString("draftId", RequireString(name, payload, "draftId"));
                writer.WriteString("sessionId", RequireString(name, payload, "sessionId"));
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
        int minimum = 1,
        int maximum = int.MaxValue)
    {
        var minimumCount = Math.Max(requireNonEmpty ? 1 : 0, minimum);
        if (!args.TryGetProperty(property, out var value) ||
            value.ValueKind != JsonValueKind.Array ||
            value.GetArrayLength() < minimumCount)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"missing required string[] argument '{property}'");
        }

        // I2/P2-E: bounded input; the Core enforces the same contract limit
        // (a huge list runs inside ONE write transaction).
        if (value.GetArrayLength() > maximum)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' supports at most {maximum} entries");
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
    /// FEA-12-PREREQ-1: strict closed-shape guard for the NEW M2-C1 rev 2.13 commands only. The
    /// existing legacy commands keep their historical pass-through behavior (the Core remains the
    /// semantic authority); a new command must reject unknown keys before any Core frame.
    /// </summary>
    private static void RejectUnknownKeys(string command, JsonElement payload, params string[] allowed)
    {
        if (payload.ValueKind != JsonValueKind.Object)
        {
            throw new HostCommandInvalidArgumentsException(command, "payload must be an object");
        }

        foreach (var property in payload.EnumerateObject())
        {
            var known = false;
            foreach (var name in allowed)
            {
                if (string.Equals(property.Name, name, StringComparison.Ordinal))
                {
                    known = true;
                    break;
                }
            }

            if (!known)
            {
                throw new HostCommandInvalidArgumentsException(
                    command, $"unexpected argument '{property.Name}' (closed shape)");
            }
        }
    }

    /// <summary>
    /// FEA-12-PREREQ-1 / M2-C1 §5.13: the preview's <c>bookIds</c> (non-empty distinct strings,
    /// 1..20). The key keeps the frozen C-04b camelCase literal.
    /// </summary>
    private static void WriteBookIdArray(
        Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"missing required string[] argument '{property}'");
        }

        if (value.GetArrayLength() < 1 || value.GetArrayLength() > MaxBookDeleteBatchSize)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' requires 1..{MaxBookDeleteBatchSize} entries");
        }

        var seen = new HashSet<string>(StringComparer.Ordinal);
        writer.WriteStartArray();
        foreach (var element in value.EnumerateArray())
        {
            if (element.ValueKind != JsonValueKind.String ||
                string.IsNullOrEmpty(element.GetString()) ||
                !seen.Add(element.GetString()!))
            {
                throw new HostCommandInvalidArgumentsException(
                    command, $"argument '{property}' must contain distinct non-empty strings");
            }

            writer.WriteStringValue(element.GetString());
        }

        writer.WriteEndArray();
    }

    /// <summary>
    /// FEA-12-PREREQ-1 / M2-C1 §5.14: <c>TrashEntryRef[1..N]</c> where each ref is the closed
    /// shape exactly <c>{book_id}</c> (request-side snake_case per C-09 SC-B06).
    /// </summary>
    private static void WriteTrashEntries(Utf8JsonWriter writer, string command, JsonElement args)
    {
        if (!args.TryGetProperty("entries", out var entries) ||
            entries.ValueKind != JsonValueKind.Array ||
            entries.GetArrayLength() < 1)
        {
            throw new HostCommandInvalidArgumentsException(
                command, "missing required non-empty object[] argument 'entries'");
        }

        writer.WriteStartArray();
        foreach (var entry in entries.EnumerateArray())
        {
            if (entry.ValueKind != JsonValueKind.Object)
            {
                throw new HostCommandInvalidArgumentsException(
                    command, "argument 'entries' must contain objects");
            }

            RejectUnknownKeys(command, entry, "book_id");
            writer.WriteStartObject();
            writer.WriteString("book_id", RequireString(command, entry, "book_id"));
            writer.WriteEndObject();
        }

        writer.WriteEndArray();
    }

    /// <summary>
    /// FEA-12-PREREQ-1 / M2-C1 §5.11.1a: additive per-book digest map for the batch delete.
    /// Type/shape only -- the Core validates the sha256 format and the two-level binding.
    /// </summary>
    private static void WriteOptionalDigestMap(
        Utf8JsonWriter writer, string command, JsonElement args, string property)
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
                entry.Value.ValueKind != JsonValueKind.String ||
                string.IsNullOrEmpty(entry.Value.GetString()))
            {
                throw new HostCommandInvalidArgumentsException(
                    command, $"argument '{property}' must map non-empty book ids to non-empty digest strings");
            }

            writer.WriteString(entry.Name, entry.Value.GetString());
        }

        writer.WriteEndObject();
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
        WritePointArray(writer, command, points, $"{property}.points", minimum: 2, maximum: MaxGeometryPoints);
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

        if (parts.GetArrayLength() > MaxSplitParts)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{property}' supports at most {MaxSplitParts} point lists");
        }

        writer.WritePropertyName(property);
        writer.WriteStartArray();
        var index = 0;
        foreach (var part in parts.EnumerateArray())
        {
            index += 1;
            WritePointArray(writer, command, part, $"{property}[{index}]", minimum: 2, maximum: MaxGeometryPoints);
        }

        writer.WriteEndArray();
    }

    private static void WritePointArray(
        Utf8JsonWriter writer,
        string command,
        JsonElement array,
        string label,
        int minimum,
        int maximum = int.MaxValue)
    {
        if (array.ValueKind != JsonValueKind.Array || array.GetArrayLength() < minimum)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{label}' needs at least {minimum} [x, y] points");
        }

        // I2/P2-E: bounded vertex count (contract v1.3 §1.3).
        if (array.GetArrayLength() > maximum)
        {
            throw new HostCommandInvalidArgumentsException(
                command, $"argument '{label}' supports at most {maximum} points");
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

    private static int RequireNumber(string command, JsonElement args, string property)
    {
        if (args.ValueKind == JsonValueKind.Object &&
            args.TryGetProperty(property, out var value) &&
            value.ValueKind == JsonValueKind.Number &&
            value.TryGetInt32(out var number))
        {
            return number;
        }

        throw new HostCommandInvalidArgumentsException(command, $"missing required integer argument '{property}'");
    }

    private static void WriteOptionalNumber(Utf8JsonWriter writer, string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return;
        }

        if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out var number))
        {
            throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' must be an integer");
        }

        writer.WriteNumber(property, number);
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
