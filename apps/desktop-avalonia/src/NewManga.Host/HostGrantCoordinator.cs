using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Issuer;
using NewManga.CoreClient.Wire;

namespace NewManga.Host;

/// <summary>Typed shell-action refusal (codes mirror the legacy Tauri error strings).</summary>
public sealed class ShellActionException : Exception
{
    public ShellActionException(string code, string detail)
        : base($"[{code}] {detail}")
    {
        Code = code;
    }

    public string Code { get; }
}

/// <summary>
/// GRANT-ISSUER-1: Host side of the HOST-ISSUER-1 grant chain plus the two whitelisted shell
/// actions. It owns no paths from the UI: import sources are validated by <see cref="HostIssuer"/>,
/// export targets are the Host-chosen (or session-recorded) destination, and both shell actions only
/// open directories that resolve inside the Host data root (or a recorded export target directory).
/// </summary>
public sealed class HostGrantCoordinator
{
    private readonly CoreServiceClient _core;
    private readonly string _dataRoot;
    private readonly string _evidenceDirectory;
    private readonly TimeSpan _timeout;
    private readonly Action<string> _openDirectory;
    private readonly List<string> _sessionExportDirectories = new();
    private readonly object _evidenceGate = new();

    public HostGrantCoordinator(
        CoreServiceClient core,
        string dataRoot,
        string logDirectory,
        TimeSpan timeout,
        Action<string>? openDirectory = null)
    {
        _core = core;
        _dataRoot = Path.GetFullPath(dataRoot);
        _evidenceDirectory = Path.Combine(logDirectory, "grants");
        _timeout = timeout;
        _openDirectory = openDirectory ?? DefaultOpenDirectory;
        Directory.CreateDirectory(_evidenceDirectory);
        Directory.CreateDirectory(Path.Combine(_dataRoot, "exports"));
    }

    public string EvidenceDirectory => _evidenceDirectory;

    /// <summary>Opens (or returns) the host-control session; required before any grant work.</summary>
    public async Task<HostSessionInfo> EnsureSessionAsync(CancellationToken cancellationToken = default) =>
        _core.HostSession ?? await _core.OpenHostSessionAsync(cancellationToken).ConfigureAwait(false);

    // ------------------------------------------------------------------ import

    public async Task<JsonElement> ImportAsync(
        string chapterId,
        IReadOnlyList<string> paths,
        string sourceKind,
        string? duplicatePolicy,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            throw new HostCommandInvalidArgumentsException("library_import_file", "chapter_id is required");
        }

        if (sourceKind == "directory" && paths.Count != 1)
        {
            throw new HostCommandInvalidArgumentsException("library_import_folder", "exactly one folder is required");
        }

        if (duplicatePolicy is not (null or "skip" or "import_as_new"))
        {
            throw new HostCommandInvalidArgumentsException("library_import_file", "duplicate_policy must be skip or import_as_new");
        }

        var session = await EnsureSessionAsync(cancellationToken).ConfigureAwait(false);
        var grants = new List<ImportGrant>();
        foreach (var path in paths)
        {
            var grantId = "grant_" + HostIssuer.NewToken();
            grants.Add(HostIssuer.MintImportGrant(
                new[] { path }, "file", session.HostSessionId, grantId, session.SigningKey));
        }

        if (sourceKind == "directory")
        {
            grants.Clear();
            var grantId = "grant_" + HostIssuer.NewToken();
            grants.Add(HostIssuer.MintImportGrant(
                paths, "directory", session.HostSessionId, grantId, session.SigningKey));
        }

        var registered = new List<JsonElement>();
        try
        {
            foreach (var grant in grants)
            {
                var response = await _core.SendHostControlAsync(
                        "RegisterImportSource",
                        writer => WriteMembers(writer, grant.Payload),
                        _timeout,
                        session,
                        cancellationToken)
                    .ConfigureAwait(false);
                var result = response.Result ?? default;
                var ok = result.ValueKind == JsonValueKind.Object &&
                         result.TryGetProperty("registered", out var flag) &&
                         flag.ValueKind == JsonValueKind.True;
                if (!ok)
                {
                    throw new HostIssuerException("REF_MALFORMED", "Core did not register the import grant");
                }

                registered.Add(BuildJson(writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("grant_id", grant.GrantId);
                    writer.WriteString("source_kind", sourceKind);
                    writer.WriteBoolean("registered", true);
                    writer.WriteEndObject();
                }));
            }

            var importResult = await _core.SendAsync(
                    "ImportPages",
                    CoreProtocol.DefaultMinor,
                    writer =>
                    {
                        writer.WriteStartObject();
                        writer.WriteString("chapter_id", chapterId);
                        writer.WritePropertyName("sources");
                        writer.WriteStartArray();
                        foreach (var grant in grants)
                        {
                            grant.Reference.WriteTo(writer);
                        }

                        writer.WriteEndArray();
                        if (duplicatePolicy is not null)
                        {
                            writer.WriteString("duplicate_policy", duplicatePolicy);
                        }

                        writer.WriteEndObject();
                    },
                    _timeout,
                    cancellationToken)
                .ConfigureAwait(false);
            var resultElement = importResult.Result ?? BuildJson(_ => { });
            WriteEvidence("import", chapterId, sourceKind, registered, resultElement);
            // Legacy parity: the Tauri command returned ImportSummary (counts), while the wire
            // returns the per-source tree. Project the same counts the Rust host projected.
            var summary = ProjectImportSummary(resultElement);
            return BuildJson(writer => summary.WriteTo(writer));
        }
        catch (Exception error)
        {
            await RevokeGrantsAsync(session, grants.Select(grant => grant.GrantId), "import", cancellationToken)
                .ConfigureAwait(false);
            WriteEvidenceError("import", chapterId, sourceKind, registered, error);
            throw;
        }
    }

    // ------------------------------------------------------------------ export

    public async Task<JsonElement> StartExportAsync(
        JsonElement request,
        string targetPath,
        CancellationToken cancellationToken = default)
    {
        var (format, extension) = HostIssuer.ValidateExportRequest(request);
        var fullTarget = Path.GetFullPath(targetPath);
        // AC2/AC3: the Host never accepts an arbitrary user path as an export target. Destinations
        // are confined to the Host-owned exports directory (or a directory the Host itself granted).
        EnsureWithinRoot(Path.GetDirectoryName(fullTarget)!, "EXPORT_PATH_UNAVAILABLE");
        var session = await EnsureSessionAsync(cancellationToken).ConfigureAwait(false);
        var grant = HostIssuer.MintExportGrant(
            targetPath, format, extension, session.HostSessionId, "grant_" + HostIssuer.NewToken(), session.SigningKey);

        JsonElement? registeredEvidence = null;
        var completed = false;
        try
        {
            var registration = await _core.SendHostControlAsync(
                    "RegisterExportTarget",
                    writer => WriteMembers(writer, grant.Payload),
                    _timeout,
                    session,
                    cancellationToken)
                .ConfigureAwait(false);
            var registrationResult = registration.Result ?? default;
            var ok = registrationResult.ValueKind == JsonValueKind.Object &&
                     registrationResult.TryGetProperty("registered", out var flag) &&
                     flag.ValueKind == JsonValueKind.True;
            if (!ok)
            {
                throw new HostIssuerException("REF_MALFORMED", "Core did not register the export grant");
            }

            registeredEvidence = BuildJson(writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("grant_id", grant.GrantId);
                writer.WriteString("target_path", Path.GetFullPath(targetPath));
                writer.WriteString("format", format);
                writer.WriteBoolean("registered", true);
                writer.WriteString("target_ref", grant.Reference);
                writer.WriteEndObject();
            });
            RecordExportDirectory(Path.GetDirectoryName(Path.GetFullPath(targetPath)));

            var result = await _core.SendAsync(
                    "StartExport",
                    CoreProtocol.DefaultMinor,
                    writer =>
                    {
                        writer.WriteStartObject();
                        WriteMembers(writer, request);
                        // target_ref is appended by the Host after validation; the legacy six-field
                        // request never carries it (HostIssuer.ValidateExportRequest enforces that).
                        writer.WriteString("target_ref", grant.Reference);
                        writer.WriteEndObject();
                    },
                    _timeout,
                    cancellationToken)
                .ConfigureAwait(false);
            var resultElement = result.Result ?? BuildJson(_ => { });
            WriteEvidence("export", null, format, new[] { registeredEvidence.Value }, resultElement);
            completed = true;
            return BuildJson(writer => resultElement.WriteTo(writer));
        }
        finally
        {
            if (!completed)
            {
                WriteEvidenceError(
                    "export",
                    null,
                    format,
                    registeredEvidence is { } evidence ? new[] { evidence } : Array.Empty<JsonElement>(),
                    new HostIssuerException("REF_MALFORMED", "export start failed"));
                await RevokeGrantsAsync(session, new[] { grant.GrantId }, "export", cancellationToken)
                    .ConfigureAwait(false);
            }
        }
    }

    // ------------------------------------------------------------------ shell actions

    public async Task<JsonElement> RevealExportFolderAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(exportId))
        {
            throw new HostCommandInvalidArgumentsException("library_reveal_export_folder", "export_id is required");
        }

        var history = await _core.SendAsync(
                "GetExportHistory",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _timeout,
                cancellationToken)
            .ConfigureAwait(false);
        var directory = ResolveExportDirectory(history.Result, exportId);
        _openDirectory(directory);
        return BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteBoolean("revealed", true);
            writer.WriteEndObject();
        });
    }

    public Task<JsonElement> OpenPluginsDirectoryAsync(CancellationToken cancellationToken = default)
    {
        _ = cancellationToken;
        var rawDirectory = Path.Combine(_dataRoot, "plugins");
        try
        {
            Directory.CreateDirectory(rawDirectory);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            throw new ShellActionException("PLUGIN_DIRECTORY_UNAVAILABLE", "cannot create the plugin directory");
        }

        var directory = EnsureWithinRoot(rawDirectory, "PLUGIN_DIRECTORY_UNAVAILABLE");
        RejectReparseComponents(directory, "PLUGIN_DIRECTORY_UNAVAILABLE");
        _openDirectory(directory);
        return Task.FromResult(BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteBoolean("opened", true);
            writer.WriteEndObject();
        }));
    }

    /// <summary>Dispatcher bridge: HostLocal commands only; every other name is a programming error.</summary>
    public async Task<HostCommandResult> HandleCommandAsync(
        string name,
        JsonElement args,
        CancellationToken cancellationToken)
    {
        var descriptor = HostCommandRegistry.Get(name);
        JsonElement value;
        switch (name)
        {
            case "library_import_file":
            {
                var chapterId = RequireString(name, args, "chapter_id");
                var paths = RequireStringArray(name, args, "paths");
                var policy = OptionalString(args, "duplicate_policy");
                value = await ImportAsync(chapterId, paths, "file", policy, cancellationToken).ConfigureAwait(false);
                break;
            }

            case "library_import_folder":
            {
                var chapterId = RequireString(name, args, "chapter_id");
                var path = RequireString(name, args, "path");
                var policy = OptionalString(args, "duplicate_policy");
                value = await ImportAsync(chapterId, new[] { path }, "directory", policy, cancellationToken)
                    .ConfigureAwait(false);
                break;
            }

            case "library_reveal_export_folder":
                value = await RevealExportFolderAsync(RequireString(name, args, "export_id"), cancellationToken)
                    .ConfigureAwait(false);
                break;

            case "plugins_open_directory":
                value = await OpenPluginsDirectoryAsync(cancellationToken).ConfigureAwait(false);
                break;

            default:
                throw new HostCommandNotSupportedException(descriptor);
        }

        return new HostCommandResult(name, descriptor.Status, descriptor.Channel, value);
    }

    // ------------------------------------------------------------------ helpers

    private string ResolveExportDirectory(JsonElement? history, string exportId)
    {
        if (history is not { ValueKind: JsonValueKind.Object } root ||
            !root.TryGetProperty("exports", out var exports) ||
            exports.ValueKind != JsonValueKind.Array)
        {
            throw new ShellActionException("EXPORT_PATH_UNAVAILABLE", "export history is unavailable");
        }

        foreach (var entry in exports.EnumerateArray())
        {
            if (entry.ValueKind != JsonValueKind.Object ||
                !entry.TryGetProperty("export_id", out var idElement) ||
                idElement.ValueKind != JsonValueKind.String ||
                !string.Equals(idElement.GetString(), exportId, StringComparison.Ordinal))
            {
                continue;
            }

            var outputPath = entry.TryGetProperty("output_path", out var pathElement) &&
                             pathElement.ValueKind == JsonValueKind.String
                ? pathElement.GetString()
                : null;
            if (string.IsNullOrEmpty(outputPath))
            {
                throw new ShellActionException("EXPORT_PATH_UNAVAILABLE", "export has no output path");
            }

            var fullPath = Path.GetFullPath(outputPath);
            var directory = Path.GetDirectoryName(fullPath);
            if (string.IsNullOrEmpty(directory))
            {
                throw new ShellActionException("EXPORT_PATH_UNAVAILABLE", "export output has no directory");
            }

            var allowed = _sessionExportDirectories.Any(recorded =>
                string.Equals(recorded, directory, StringComparison.OrdinalIgnoreCase));
            if (!allowed)
            {
                // A user-chosen export path (via the save dialog) is recorded only when this Host
                // minted its grant; anything else is not a Host-authorized reveal target.
                throw new ShellActionException("EXPORT_PATH_UNAVAILABLE", "export directory is not Host-authorized");
            }

            return EnsureWithinRoot(directory, "EXPORT_PATH_UNAVAILABLE");
        }

        throw new ShellActionException("EXPORT_PATH_UNAVAILABLE", "export id is unknown to the Core history");
    }

    private void RecordExportDirectory(string? directory)
    {
        if (string.IsNullOrEmpty(directory))
        {
            return;
        }

        var full = Path.GetFullPath(directory);
        if (!_sessionExportDirectories.Any(recorded =>
                string.Equals(recorded, full, StringComparison.OrdinalIgnoreCase)))
        {
            _sessionExportDirectories.Add(full);
        }
    }

    /// <summary>Whitelist: only a directory inside the Host data root may be opened.</summary>
    public string EnsureWithinRoot(string candidate, string code)
    {
        var root = Path.GetFullPath(_dataRoot);
        var full = Path.GetFullPath(candidate);
        var comparison = StringComparison.OrdinalIgnoreCase;
        if (!string.Equals(full, root, comparison) &&
            !full.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, comparison))
        {
            throw new ShellActionException(code, "path is outside the Host data root");
        }

        RejectReparseComponents(full, code);
        return full;
    }

    private static void RejectReparseComponents(string path, string code = "EXPORT_PATH_UNAVAILABLE")
    {
        var current = Path.GetPathRoot(path) ?? string.Empty;
        foreach (var part in path[current.Length..].Split(
                     new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                     StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, part);
            if (!Directory.Exists(current) && !File.Exists(current))
            {
                throw new ShellActionException(code, "directory component does not exist");
            }

            if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0)
            {
                throw new ShellActionException(code, "directory contains a reparse point");
            }
        }
    }

    private async Task RevokeGrantsAsync(
        HostSessionInfo session,
        IEnumerable<string> grantIds,
        string kind,
        CancellationToken cancellationToken)
    {
        var command = kind == "import" ? "RevokeImportSource" : "RevokeExportTarget";
        foreach (var id in grantIds)
        {
            try
            {
                await _core.SendHostControlAsync(
                        command,
                        writer => writer.WriteString("grant_id", id),
                        _timeout,
                        session,
                        cancellationToken)
                    .ConfigureAwait(false);
            }
            catch (Exception)
            {
                // revoke is best effort on the failure path; the grant also expires in 300 s
            }
        }
    }

    private void WriteEvidence(
        string operation,
        string? chapterId,
        string kind,
        IEnumerable<JsonElement> grants,
        JsonElement result)
    {
        lock (_evidenceGate)
        {
            var record = BuildJson(writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("operation", operation);
                writer.WriteString("kind", kind);
                if (chapterId is not null)
                {
                    writer.WriteString("chapter_id", chapterId);
                }

                writer.WritePropertyName("grants");
                writer.WriteStartArray();
                foreach (var grant in grants)
                {
                    grant.WriteTo(writer);
                }

                writer.WriteEndArray();
                writer.WritePropertyName("result");
                result.WriteTo(writer);
                writer.WriteString("generated_at_utc", DateTimeOffset.UtcNow.ToString("o"));
                writer.WriteEndObject();
            });
            File.WriteAllText(
                Path.Combine(_evidenceDirectory, $"{operation}-{DateTime.UtcNow:yyyyMMddTHHmmssfff}.json"),
                record.GetRawText());
        }
    }

    private void WriteEvidenceError(
        string operation,
        string? chapterId,
        string kind,
        IEnumerable<JsonElement> grants,
        Exception error)
    {
        lock (_evidenceGate)
        {
            var code = error switch
            {
                CoreOperationException core => core.Code,
                HostIssuerException issuer => issuer.Code,
                _ => error.GetType().Name,
            };
            var record = BuildJson(writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("operation", operation);
                writer.WriteString("kind", kind);
                writer.WriteString("error_code", code);
                if (chapterId is not null)
                {
                    writer.WriteString("chapter_id", chapterId);
                }

                writer.WritePropertyName("grants");
                writer.WriteStartArray();
                foreach (var grant in grants)
                {
                    grant.WriteTo(writer);
                }

                writer.WriteEndArray();
                writer.WriteString("generated_at_utc", DateTimeOffset.UtcNow.ToString("o"));
                writer.WriteEndObject();
            });
            File.WriteAllText(
                Path.Combine(_evidenceDirectory, $"{operation}-error-{DateTime.UtcNow:yyyyMMddTHHmmssfff}.json"),
                record.GetRawText());
        }
    }

    private static void DefaultOpenDirectory(string directory)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = "explorer.exe",
            Arguments = $"\"{directory}\"",
            UseShellExecute = false,
        };
        using var process = Process.Start(startInfo);
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

    private static IReadOnlyList<string> RequireStringArray(string command, JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new HostCommandInvalidArgumentsException(command, $"missing required string[] argument '{property}'");
        }

        var result = new List<string>();
        foreach (var item in value.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.String || item.GetString() is not { Length: > 0 } text)
            {
                throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' contains an invalid path");
            }

            result.Add(text);
        }

        if (result.Count == 0)
        {
            throw new HostCommandInvalidArgumentsException(command, $"argument '{property}' is empty");
        }

        return result;
    }

    private static string? OptionalString(JsonElement args, string property)
    {
        if (!args.TryGetProperty(property, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        return value.ValueKind == JsonValueKind.String ? value.GetString() : null;
    }

    private static JsonElement ProjectImportSummary(JsonElement result)
    {
        var imported = 0;
        var skipped = 0;
        var rejected = 0;
        var pending = 0;
        if (result.ValueKind == JsonValueKind.Object &&
            result.TryGetProperty("sources", out var sources) &&
            sources.ValueKind == JsonValueKind.Array)
        {
            foreach (var source in sources.EnumerateArray())
            {
                if (source.ValueKind != JsonValueKind.Object ||
                    !source.TryGetProperty("files", out var files) ||
                    files.ValueKind != JsonValueKind.Array)
                {
                    continue;
                }

                foreach (var file in files.EnumerateArray())
                {
                    var outcome = file.ValueKind == JsonValueKind.Object &&
                                  file.TryGetProperty("outcome", out var value) &&
                                  value.ValueKind == JsonValueKind.String
                        ? value.GetString()
                        : null;
                    switch (outcome)
                    {
                        case "imported":
                            imported++;
                            break;
                        case "skipped":
                            skipped++;
                            break;
                        case "rejected":
                        case "partial":
                            rejected++;
                            break;
                        case "pending":
                            pending++;
                            break;
                    }
                }
            }
        }

        var chapterId = result.ValueKind == JsonValueKind.Object &&
                        result.TryGetProperty("chapter_id", out var id) &&
                        id.ValueKind == JsonValueKind.String
            ? id.GetString() ?? string.Empty
            : string.Empty;
        var cancelled = result.ValueKind == JsonValueKind.Object &&
                        result.TryGetProperty("cancelled", out var cancelledValue) &&
                        cancelledValue.ValueKind == JsonValueKind.True;
        return BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("chapter_id", chapterId);
            writer.WriteBoolean("cancelled", cancelled);
            writer.WriteNumber("imported_files", imported);
            writer.WriteNumber("skipped_files", skipped);
            writer.WriteNumber("rejected_files", rejected);
            writer.WriteNumber("pending_files", pending);
            writer.WriteEndObject();
        });
    }

    private static void WriteMembers(Utf8JsonWriter writer, JsonElement element)
    {
        foreach (var property in element.EnumerateObject())
        {
            property.WriteTo(writer);
        }
    }

    private static JsonElement BuildJson(Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream(256);
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = false }))
        {
            write(writer);
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }
}
