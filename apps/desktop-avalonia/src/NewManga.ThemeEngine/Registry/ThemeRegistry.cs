using System.Text;

namespace NewManga.ThemeEngine;

/// <summary>
/// Catalog of built-in packages plus user themes installed under
/// <c>%APPDATA%/NewManga/themes/{id}.nmtheme</c> (contract §4/§5). The registry owns file discovery,
/// install/uninstall/export and never exposes a corrupt file as a theme: unreadable or invalid files
/// are quarantined in <see cref="Diagnostics"/> and skipped, so a broken user theme can never block
/// startup. Built-in ids are reserved and cannot be shadowed or uninstalled.
/// </summary>
public sealed class ThemeRegistry : IThemeRegistry
{
    private readonly object _gate = new();
    private readonly IThemeValidator _validator;
    private readonly SortedDictionary<string, UserThemeEntry> _userEntries = new(StringComparer.Ordinal);
    private readonly IReadOnlyList<ThemeDescriptor> _builtInDescriptors;
    private readonly IReadOnlyList<ThemeValidationIssue> _builtInIssues;
    private IReadOnlyList<ThemeValidationIssue> _diagnostics;

    /// <summary>
    /// Creates a registry. <paramref name="userThemeDirectory"/> defaults to
    /// <see cref="DefaultUserThemeDirectory"/>; the constructor performs the initial directory scan.
    /// </summary>
    public ThemeRegistry(string? userThemeDirectory = null, IThemeValidator? validator = null)
    {
        _validator = validator ?? ThemeValidator.Default;
        UserThemeDirectory = string.IsNullOrWhiteSpace(userThemeDirectory)
            ? DefaultUserThemeDirectory
            : Path.GetFullPath(userThemeDirectory);

        var builtInIssues = new List<ThemeValidationIssue>();
        var descriptors = new List<ThemeDescriptor>();
        foreach (var package in BuiltInThemes.All)
        {
            descriptors.Add(package.Descriptor);
        }

        builtInIssues.AddRange(BuiltInThemes.DefaultLoadIssues);
        _builtInDescriptors = descriptors.OrderBy(static descriptor => descriptor.Id, StringComparer.Ordinal).ToArray();
        _builtInIssues = builtInIssues;

        var scanIssues = Scan(CancellationToken.None);
        _diagnostics = [.. _builtInIssues, .. scanIssues];
    }

    /// <summary>Roaming application-data theme directory (<c>%APPDATA%/NewManga/themes</c>).</summary>
    public static string DefaultUserThemeDirectory { get; } =
        Path.Combine(ThemeSettingsStore.DefaultDirectory, ThemeDefaults.ThemeDirectoryName);

    /// <summary>Directory scanned for user themes.</summary>
    public string UserThemeDirectory { get; }

    /// <summary>Findings from the last scan (quarantined files, duplicate ids, reserved ids).</summary>
    public IReadOnlyList<ThemeValidationIssue> Diagnostics
    {
        get
        {
            lock (_gate)
            {
                return _diagnostics;
            }
        }
    }

    /// <summary>Built-in descriptors (shipped packages).</summary>
    public IReadOnlyList<ThemeDescriptor> BuiltIn => _builtInDescriptors;

    /// <inheritdoc />
    public IReadOnlyList<ThemeDescriptor> All
    {
        get
        {
            lock (_gate)
            {
                var all = new List<ThemeDescriptor>(_builtInDescriptors.Count + _userEntries.Count);
                all.AddRange(_builtInDescriptors);
                all.AddRange(_userEntries.Values.Select(static entry => entry.Descriptor));
                return all;
            }
        }
    }

    /// <inheritdoc />
    public ThemeDescriptor? Find(string id)
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            return null;
        }

        lock (_gate)
        {
            if (_userEntries.TryGetValue(id, out var user))
            {
                return user.Descriptor;
            }

            return _builtInDescriptors.FirstOrDefault(
                descriptor => string.Equals(descriptor.Id, id, StringComparison.Ordinal));
        }
    }

    /// <inheritdoc />
    public ThemePackage Load(string id)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);

        lock (_gate)
        {
            if (_userEntries.TryGetValue(id, out var user))
            {
                return user.Package;
            }

            foreach (var builtIn in BuiltInThemes.All)
            {
                if (string.Equals(builtIn.Descriptor.Id, id, StringComparison.Ordinal))
                {
                    return builtIn;
                }
            }
        }

        throw new ThemePackageException(
            $"theme '{id}' is not installed",
            [ThemeValidationIssue.Error(ThemeIssueCodes.ThemeNotFound, $"theme '{id}' is not installed", id)]);
    }

    /// <inheritdoc />
    public Task RefreshAsync(CancellationToken ct = default)
    {
        ct.ThrowIfCancellationRequested();

        lock (_gate)
        {
            var scanIssues = Scan(ct);
            _diagnostics = [.. _builtInIssues, .. scanIssues];
        }

        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public Task<ThemeValidationResult> InstallAsync(Stream packageJson, CancellationToken ct = default)
    {
        ArgumentNullException.ThrowIfNull(packageJson);
        ct.ThrowIfCancellationRequested();

        string json;
        try
        {
            var bytes = ReadLimited(packageJson);
            json = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true)
                .GetString(bytes);
        }
        catch (InstallReadException exception)
        {
            return Task.FromResult(ThemeValidationResult.From([exception.Issue]));
        }
        catch (DecoderFallbackException exception)
        {
            return Task.FromResult(ThemeValidationResult.From(
            [
                ThemeValidationIssue.Error(
                    ThemeIssueCodes.JsonInvalid,
                    $"theme package is not valid UTF-8: {exception.Message}"),
            ]));
        }

        var read = ThemePackageJson.Read(json);
        if (read.Package is null)
        {
            return Task.FromResult(ThemeValidationResult.From(read.Issues));
        }

        var package = read.Package;
        var issues = new List<ThemeValidationIssue>(read.Issues);
        if (package.Descriptor.Kind != ThemeKind.User)
        {
            package = package with
            {
                Descriptor = package.Descriptor with { Kind = ThemeKind.User },
            };
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.InstallKindNormalized,
                "installed themes are always of kind 'user'; the declared kind was normalized",
                "descriptor.kind"));
        }

        // Validate with the reader findings attached so forbidden declarations remain errors.
        var validation = _validator.Validate(package with
        {
            Metadata = package.Metadata with { LoadWarnings = issues },
        });
        if (!validation.IsValid)
        {
            return Task.FromResult(validation);
        }

        if (_builtInDescriptors.Any(descriptor =>
                string.Equals(descriptor.Id, package.Descriptor.Id, StringComparison.Ordinal)))
        {
            return Task.FromResult(ThemeValidationResult.From(
            [
                ThemeValidationIssue.Error(
                    ThemeIssueCodes.RegistryIdReserved,
                    $"theme id '{package.Descriptor.Id}' is reserved by a built-in theme",
                    "descriptor.id"),
            ]));
        }

        var filePath = Path.Combine(UserThemeDirectory, package.Descriptor.Id + ThemeDefaults.ThemeFileExtension);
        try
        {
            Directory.CreateDirectory(UserThemeDirectory);
            var tempPath = filePath + ".tmp";
            // Persist the canonical document (kind normalized to user, unknown fields dropped) so the
            // installed file is a stable round-trip of the validated package rather than raw input.
            var canonicalJson = ThemePackageJson.Write(package);
            try
            {
                File.WriteAllText(tempPath, canonicalJson, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
                File.Move(tempPath, filePath, overwrite: true);
            }
            catch
            {
                TryDelete(tempPath);
                throw;
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            return Task.FromResult(ThemeValidationResult.From(
            [
                ThemeValidationIssue.Error(
                    ThemeIssueCodes.RegistryIoFailed,
                    $"theme '{package.Descriptor.Id}' could not be written: {exception.Message}",
                    filePath),
            ]));
        }

        lock (_gate)
        {
            _userEntries[package.Descriptor.Id] = new UserThemeEntry(package.Descriptor, package, filePath);
        }

        return Task.FromResult(validation);
    }

    /// <inheritdoc />
    public Task<bool> UninstallAsync(string id)
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            return Task.FromResult(false);
        }

        UserThemeEntry? entry;
        lock (_gate)
        {
            if (!_userEntries.TryGetValue(id, out entry))
            {
                return Task.FromResult(false);
            }
        }

        try
        {
            if (File.Exists(entry.FilePath))
            {
                File.Delete(entry.FilePath);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            lock (_gate)
            {
                _diagnostics =
                [
                    .. _diagnostics,
                    ThemeValidationIssue.Warning(
                        ThemeIssueCodes.RegistryIoFailed,
                        $"theme '{id}' could not be deleted: {exception.Message}",
                        entry.FilePath),
                ];
            }

            return Task.FromResult(false);
        }

        lock (_gate)
        {
            _userEntries.Remove(id);
        }

        return Task.FromResult(true);
    }

    /// <inheritdoc />
    public Task<string> ExportAsync(string id) => Task.FromResult(ThemePackageJson.Write(Load(id)));

    private IReadOnlyList<ThemeValidationIssue> Scan(CancellationToken ct)
    {
        var issues = new List<ThemeValidationIssue>();
        _userEntries.Clear();

        if (!Directory.Exists(UserThemeDirectory))
        {
            return issues;
        }

        string[] files;
        try
        {
            files = Directory.EnumerateFiles(UserThemeDirectory)
                .Where(static path => IsThemeFile(path))
                .OrderBy(static path => ExtensionPriority(path))
                .ThenBy(static path => path, StringComparer.Ordinal)
                .ToArray();
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.RegistryIoFailed,
                $"theme directory '{UserThemeDirectory}' could not be enumerated: {exception.Message}",
                UserThemeDirectory));
            return issues;
        }

        foreach (var path in files)
        {
            ct.ThrowIfCancellationRequested();

            string json;
            try
            {
                var info = new FileInfo(path);
                if (info.Length > ThemePackageJson.MaxDocumentBytes)
                {
                    issues.Add(ThemeValidationIssue.Warning(
                        ThemeIssueCodes.RegistryFileInvalid,
                        $"theme file is {info.Length} bytes, above the {ThemePackageJson.MaxDocumentBytes} byte limit; skipped",
                        path));
                    continue;
                }

                json = File.ReadAllText(path, Encoding.UTF8);
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.RegistryFileUnreadable,
                    $"theme file could not be read ({exception.Message}); skipped",
                    path));
                continue;
            }

            var read = ThemePackageJson.Read(json);
            if (read.Package is null)
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.RegistryFileInvalid,
                    $"theme file is not a usable package ({Describe(read.Issues)}); skipped",
                    path));
                continue;
            }

            var package = read.Package with
            {
                Descriptor = read.Package.Descriptor with { Kind = ThemeKind.User },
            };

            var validation = _validator.Validate(package);
            if (!validation.IsValid)
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.RegistryFileInvalid,
                    $"theme file failed validation ({Describe(validation.Errors)}); skipped",
                    path));
                continue;
            }

            var id = package.Descriptor.Id;
            if (_builtInDescriptors.Any(descriptor => string.Equals(descriptor.Id, id, StringComparison.Ordinal)))
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.RegistryIdReserved,
                    $"theme id '{id}' is reserved by a built-in theme; file skipped",
                    path));
                continue;
            }

            if (_userEntries.ContainsKey(id))
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.RegistryDuplicateId,
                    $"another theme file already declares id '{id}'; this file is skipped",
                    path));
                continue;
            }

            _userEntries[id] = new UserThemeEntry(package.Descriptor, package, path);
        }

        return issues;
    }

    private static bool IsThemeFile(string path)
    {
        var extension = Path.GetExtension(path);
        return string.Equals(extension, ThemeDefaults.ThemeFileExtension, StringComparison.OrdinalIgnoreCase) ||
               string.Equals(extension, ThemeDefaults.ThemeJsonExtension, StringComparison.OrdinalIgnoreCase);
    }

    private static int ExtensionPriority(string path) =>
        string.Equals(Path.GetExtension(path), ThemeDefaults.ThemeFileExtension, StringComparison.OrdinalIgnoreCase) ? 0 : 1;

    private static string Describe(IReadOnlyList<ThemeValidationIssue> issues)
    {
        var first = issues.FirstOrDefault();
        return first is null ? "no details" : $"{first.Code}: {first.Message}";
    }

    private static byte[] ReadLimited(Stream stream)
    {
        using var buffer = new MemoryStream(capacity: 4096);
        var chunk = new byte[8192];
        int read;
        while ((read = stream.Read(chunk, 0, chunk.Length)) > 0)
        {
            if (buffer.Length + read > ThemePackageJson.MaxDocumentBytes)
            {
                throw new InstallReadException(ThemeValidationIssue.Error(
                    ThemeIssueCodes.InstallTooLarge,
                    $"theme package exceeds the {ThemePackageJson.MaxDocumentBytes} byte limit"));
            }

            buffer.Write(chunk, 0, read);
        }

        return buffer.ToArray();
    }

    private static void TryDelete(string path)
    {
        try
        {
            if (File.Exists(path))
            {
                File.Delete(path);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            // The temporary file is harmless; the real write failure is already propagating.
        }
    }

    private sealed record UserThemeEntry(ThemeDescriptor Descriptor, ThemePackage Package, string FilePath);

    private sealed class InstallReadException : Exception
    {
        public InstallReadException(ThemeValidationIssue issue)
            : base(issue.Message)
        {
            Issue = issue;
        }

        public ThemeValidationIssue Issue { get; }
    }
}
