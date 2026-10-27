using System.Globalization;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using NewManga.CoreClient.Commands;

namespace NewManga.CoreClient.Issuer;

/// <summary>GRANT-ISSUER-1: one open host-control session (HOST-ISSUER-1 envelope).</summary>
public sealed record HostSessionInfo(
    string HostSessionId,
    string Credential,
    string CoreSessionId,
    byte[] SigningKey);

/// <summary>Typed issuer refusal; codes mirror the frozen Core grant vocabulary.</summary>
public sealed class HostIssuerException : Exception
{
    public HostIssuerException(string code, string detail)
        : base($"[{code}] {detail}")
    {
        Code = code;
    }

    public string Code { get; }
}

/// <summary>Host-issued, one-use ImportPages source grant (payload goes to RegisterImportSource).</summary>
public sealed record ImportGrant(string GrantId, JsonElement Payload, JsonElement Reference);

/// <summary>Host-issued, one-use export destination grant (reference goes to StartExport.target_ref).</summary>
public sealed record ExportGrant(string GrantId, JsonElement Payload, string Reference);

/// <summary>
/// C# port of the legacy Rust <c>host_issuer.rs</c> chain (GRANT-ISSUER-1):
/// mints signed import/export grants that the frozen Core registers through the
/// host-control envelope. The signing bytes are pinned to the Core's verifier
/// (<c>import_source_refs._signed_fields/_sign</c>, <c>export/target_refs._signature</c>):
///   - import: HMAC-SHA256 over compact, sorted-key UTF-8 JSON of the signed fields;
///   - export: HMAC-SHA256 over <c>grant_id\0session\0target_path\0format\0replace\0expires_at(%.6f)</c>.
/// Grants are only minted for authorized resources: caller-supplied chapter/export ids are never
/// trusted as paths, and every source/target path is validated (absolute, no <c>..</c>, no reparse,
/// extension whitelist) exactly like the legacy issuer.
/// </summary>
public static class HostIssuer
{
    public const string ImportOperation = "ImportPages";
    public const string ImportScopeClass = "user-source";
    public const string ImportAccess = "read-only";

    private static readonly HashSet<string> ImportExtensions = new(StringComparer.OrdinalIgnoreCase)
    {
        ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".pdf",
    };

    private static readonly HashSet<string> ImportImageExtensions = new(StringComparer.OrdinalIgnoreCase)
    {
        ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",
    };

    private static readonly Regex NumberPattern = new(@"(\d+)", RegexOptions.Compiled);

    // ------------------------------------------------------------------ tokens & signatures

    public static string NewToken()
    {
        Span<byte> bytes = stackalloc byte[32];
        RandomNumberGenerator.Fill(bytes);
        return Base64Url(bytes);
    }

    public static byte[] NewSigningKey()
    {
        var key = new byte[32];
        RandomNumberGenerator.Fill(key);
        return key;
    }

    public static string Base64Url(ReadOnlySpan<byte> bytes) =>
        Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_');

    public static string HmacSha256Base64Url(byte[] key, ReadOnlySpan<byte> message)
    {
        using var hmac = new HMACSHA256(key);
        return Base64Url(hmac.ComputeHash(message.ToArray()));
    }

    /// <summary>Python's <c>f"{value:.6f}"</c> for the integer-second expiry the issuer uses.</summary>
    public static string FormatExpiry(double value) => value.ToString("F6", CultureInfo.InvariantCulture);

    public static double NextExpiry()
    {
        // Rust: unix_seconds() + 299.0. Core requires now &lt; expires_at &lt;= now + 300. Using an
        // integral second keeps "%.6f" byte-identical on both sides (no double tie-rounding).
        var seconds = Math.Floor(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0);
        return seconds + 299.0;
    }

    // ------------------------------------------------------------------ import grant

    public static ImportGrant MintImportGrant(
        IReadOnlyList<string> paths,
        string sourceKind,
        string sessionId,
        string grantId,
        byte[] signingKey)
    {
        if (string.IsNullOrEmpty(sessionId) || string.IsNullOrEmpty(grantId))
        {
            throw new HostIssuerException("REF_MALFORMED", "session/grant id is empty");
        }

        if (sourceKind == "file")
        {
            if (paths.Count == 0)
            {
                throw new HostIssuerException("INVALID_REQUEST", "no import source path");
            }
        }
        else if (sourceKind == "directory")
        {
            if (paths.Count != 1)
            {
                throw new HostIssuerException("INVALID_REQUEST", "directory import takes exactly one folder");
            }
        }
        else
        {
            throw new HostIssuerException("INVALID_REQUEST", "unsupported source_kind");
        }

        var (entries, scopeIdentity, sourcePath) = CollectImportEntries(paths, sourceKind);
        var expiresAt = NextExpiry();
        var signed = BuildImportSignedFields(
            grantId, sessionId, sourcePath, sourceKind, scopeIdentity, entries, expiresAt);
        var signature = HmacSha256Base64Url(signingKey, Encoding.UTF8.GetBytes(signed));
        var payload = BuildImportPayload(
            grantId, sessionId, sourcePath, sourceKind, scopeIdentity, entries, expiresAt, signingKey, signature);
        var reference = BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("grant_id", grantId);
            writer.WriteString("host_signature", signature);
            writer.WriteEndObject();
        });
        return new ImportGrant(grantId, payload, reference);
    }

    private static (List<ImportEntry> Entries, (ulong Volume, ulong Index)? ScopeIdentity, string SourcePath)
        CollectImportEntries(IReadOnlyList<string> paths, string sourceKind)
    {
        var entries = new List<ImportEntry>();
        if (sourceKind == "file")
        {
            foreach (var raw in paths)
            {
                var path = ValidateAbsolutePath(raw, "INVALID_REQUEST");
                entries.Add(ReadEntry(path, ImportExtensions));
            }

            if (entries.Count == 0)
            {
                throw new HostIssuerException("REF_SCOPE_DENIED", "no file to import");
            }

            return (entries, null, entries[0].Path);
        }

        var directory = ValidateAbsolutePath(paths[0], "INVALID_REQUEST");
        RejectReparseComponents(directory);
        if (!Directory.Exists(directory))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "import folder does not exist");
        }

        var identity = DirectoryIdentity(directory);
        var children = Directory.EnumerateFiles(directory)
            .Where(child => ImportImageExtensions.Contains(Path.GetExtension(child)))
            .Select(Path.GetFullPath)
            .ToList();
        children.Sort((left, right) =>
            NaturalCompare(Path.GetFileName(left), Path.GetFileName(right)));
        if (children.Count == 0)
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "import folder has no supported images");
        }

        foreach (var child in children)
        {
            RejectReparseComponents(child);
            entries.Add(ReadEntry(child, ImportImageExtensions));
        }

        return (entries, identity, directory);
    }

    private static ImportEntry ReadEntry(string path, HashSet<string> allowedExtensions)
    {
        if (!File.Exists(path))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", $"import source does not exist: {path}");
        }

        RejectReparseComponents(path);
        var extension = Path.GetExtension(path);
        if (!allowedExtensions.Contains(extension))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", $"unsupported import extension: {extension}");
        }

        var before = FileIdentity(path);
        if (before.Reparse)
        {
            throw new HostIssuerException("REF_REPARSE_POINT", "import source is a reparse point");
        }

        using var stream = new FileStream(
            path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
        var length = stream.Length;
        using var sha = SHA256.Create();
        var digest = sha.ComputeHash(stream);
        var after = FileIdentity(path);
        if (before.Volume != after.Volume || before.Index != after.Index || length != after.Size)
        {
            throw new HostIssuerException("FILE_IDENTITY_CHANGED", "import source changed while hashing");
        }

        return new ImportEntry(path, before.Volume, before.Index, length, Convert.ToHexString(digest).ToLowerInvariant());
    }

    private static string BuildImportSignedFields(
        string grantId,
        string sessionId,
        string sourcePath,
        string sourceKind,
        (ulong Volume, ulong Index)? scopeIdentity,
        IReadOnlyList<ImportEntry> entries,
        double expiresAt)
    {
        // Sorted-key compact JSON is the Core's verifier contract. Keys are sorted
        // lexicographically and the same escaping as json.dumps(ensure_ascii=False) is used.
        var builder = new StringBuilder(1024);
        builder.Append('{');
        AppendMember(builder, "access", "read-only", first: true);
        builder.Append(",\"entries\":[");
        for (var index = 0; index < entries.Count; index++)
        {
            if (index > 0)
            {
                builder.Append(',');
            }

            var entry = entries[index];
            builder.Append("{\"facts\":{\"file_index\":");
            builder.Append(entry.FileIndex.ToString(CultureInfo.InvariantCulture));
            builder.Append(",\"sha256\":");
            AppendString(builder, entry.Sha256);
            builder.Append(",\"size\":");
            builder.Append(entry.Size.ToString(CultureInfo.InvariantCulture));
            builder.Append(",\"volume_serial\":");
            builder.Append(entry.VolumeSerial.ToString(CultureInfo.InvariantCulture));
            builder.Append("},\"path\":");
            AppendString(builder, entry.Path);
            builder.Append('}');
        }

        builder.Append(']');
        builder.Append(",\"expires_at\":");
        AppendString(builder, FormatExpiry(expiresAt));
        builder.Append(",\"grant_id\":");
        AppendString(builder, grantId);
        builder.Append(",\"operation\":");
        AppendString(builder, ImportOperation);
        builder.Append(",\"scope_class\":");
        AppendString(builder, ImportScopeClass);
        builder.Append(",\"scope_identity\":");
        if (scopeIdentity is { } identity)
        {
            builder.Append('[')
                .Append(identity.Volume.ToString(CultureInfo.InvariantCulture))
                .Append(',')
                .Append(identity.Index.ToString(CultureInfo.InvariantCulture))
                .Append(']');
        }
        else
        {
            builder.Append("null");
        }

        builder.Append(",\"session_id\":");
        AppendString(builder, sessionId);
        builder.Append(",\"source_kind\":");
        AppendString(builder, sourceKind);
        builder.Append(",\"source_path\":");
        AppendString(builder, sourcePath);
        builder.Append('}');
        return builder.ToString();
    }

    private static JsonElement BuildImportPayload(
        string grantId,
        string sessionId,
        string sourcePath,
        string sourceKind,
        (ulong Volume, ulong Index)? scopeIdentity,
        IReadOnlyList<ImportEntry> entries,
        double expiresAt,
        byte[] signingKey,
        string signature)
    {
        return BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("grant_id", grantId);
            writer.WriteString("session_id", sessionId);
            writer.WriteString("scope_class", ImportScopeClass);
            writer.WriteString("operation", ImportOperation);
            writer.WriteString("access", ImportAccess);
            writer.WriteString("source_path", sourcePath);
            writer.WriteString("source_kind", sourceKind);
            if (scopeIdentity is { } identity)
            {
                writer.WriteStartArray("scope_identity");
                writer.WriteNumberValue(identity.Volume);
                writer.WriteNumberValue(identity.Index);
                writer.WriteEndArray();
            }
            else
            {
                writer.WriteNull("scope_identity");
            }

            writer.WriteStartArray("entries");
            foreach (var entry in entries)
            {
                writer.WriteStartObject();
                writer.WriteString("path", entry.Path);
                writer.WriteStartObject("facts");
                writer.WriteNumber("volume_serial", entry.VolumeSerial);
                writer.WriteNumber("file_index", entry.FileIndex);
                writer.WriteNumber("size", entry.Size);
                writer.WriteString("sha256", entry.Sha256);
                writer.WriteEndObject();
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteNumber("expires_at", expiresAt);
            writer.WriteString("signing_key", Base64Url(signingKey));
            writer.WriteString("signature", signature);
            writer.WriteEndObject();
        });
    }

    // ------------------------------------------------------------------ export grant

    /// <summary>Mirrors <c>host_issuer::validate_export_request</c>: the six legacy request fields.</summary>
    public static (string Format, string Extension) ValidateExportRequest(JsonElement request)
    {
        if (request.ValueKind != JsonValueKind.Object)
        {
            throw new HostIssuerException("INVALID_REQUEST", "export request must be an object");
        }

        var properties = request.EnumerateObject().Select(property => property.Name).ToList();
        string[] expected = { "book_id", "chapter_ids", "ordered_page_ids", "format", "format_options", "stale_policy" };
        if (properties.Count != expected.Length || expected.Any(name => !properties.Contains(name)))
        {
            throw new HostIssuerException("INVALID_REQUEST", "export request fields do not match");
        }

        if (ReadRequiredString(request, "book_id") is not { Length: > 0 })
        {
            throw new HostIssuerException("INVALID_REQUEST", "book_id is invalid");
        }

        var chapters = ReadUniqueStrings(request, "chapter_ids");
        _ = ReadUniqueStrings(request, "ordered_page_ids");
        var format = ReadRequiredString(request, "format");
        var stalePolicy = ReadRequiredString(request, "stale_policy");
        if (stalePolicy is not ("abort" or "continue_existing"))
        {
            throw new HostIssuerException("INVALID_REQUEST", "stale_policy is invalid");
        }

        if (!request.TryGetProperty("format_options", out var options) || options.ValueKind != JsonValueKind.Object)
        {
            throw new HostIssuerException("INVALID_REQUEST", "format_options must be an object");
        }

        var optionNames = options.EnumerateObject().Select(property => property.Name).ToHashSet(StringComparer.Ordinal);
        string? extension = format switch
        {
            "png" when options.EnumerateObject().Any() == false => "png",
            "cbz" when options.EnumerateObject().Any() == false => "cbz",
            "zip" when optionNames.SetEquals(new[] { "compression" }) &&
                       ReadRequiredString(options, "compression") is "standard" or "fast" or "store" => "zip",
            "pdf" when optionNames.SetEquals(new[] { "pdf_content" }) &&
                       ReadRequiredString(options, "pdf_content") is "image_only" or "searchable_dual_layer" => "pdf",
            "text" when optionNames.SetEquals(new[] { "text_representation" }) =>
                ReadRequiredString(options, "text_representation") switch
                {
                    "txt" => "txt",
                    "json" => "json",
                    "markdown" => "md",
                    _ => null,
                },
            _ => null,
        };
        if (extension is null)
        {
            throw new HostIssuerException("INVALID_REQUEST", "format/format_options are invalid");
        }

        _ = chapters;
        return (format, extension);
    }

    public static ExportGrant MintExportGrant(
        string targetPath,
        string format,
        string extension,
        string sessionId,
        string grantId,
        byte[] signingKey)
    {
        if (string.IsNullOrEmpty(sessionId) ||
            format is not ("png" or "zip" or "cbz" or "pdf" or "text"))
        {
            throw new HostIssuerException("REF_MALFORMED", "export grant arguments are invalid");
        }

        var target = ValidateAbsolutePath(targetPath, "REF_SCOPE_DENIED");
        var parent = Path.GetDirectoryName(target);
        if (string.IsNullOrEmpty(parent))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "export target has no parent folder");
        }

        RejectReparseComponents(parent);
        if (!Directory.Exists(parent))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "export parent folder does not exist");
        }

        if (!string.Equals(Path.GetExtension(target), "." + extension, StringComparison.OrdinalIgnoreCase))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "export target extension does not match format");
        }

        bool replaceExisting;
        if (File.Exists(target))
        {
            var attributes = File.GetAttributes(target);
            if ((attributes & FileAttributes.ReparsePoint) != 0 || Directory.Exists(target))
            {
                throw new HostIssuerException("REF_REPARSE_POINT", "export target is not a regular file");
            }

            replaceExisting = true;
        }
        else
        {
            replaceExisting = false;
        }

        var expiresAt = NextExpiry();
        var signatureInput = string.Join(
            '\0',
            grantId,
            sessionId,
            target,
            format,
            replaceExisting ? "1" : "0",
            FormatExpiry(expiresAt));
        var signature = HmacSha256Base64Url(signingKey, Encoding.UTF8.GetBytes(signatureInput));
        var payload = BuildJson(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("grant_id", grantId);
            writer.WriteString("session_id", sessionId);
            writer.WriteString("target_path", target);
            writer.WriteString("format", format);
            writer.WriteBoolean("replace_existing", replaceExisting);
            writer.WriteNumber("expires_at", expiresAt);
            writer.WriteString("signing_key", Base64Url(signingKey));
            writer.WriteString("signature", signature);
            writer.WriteEndObject();
        });
        return new ExportGrant(grantId, payload, $"etref1.{grantId}.{signature}");
    }

    // ------------------------------------------------------------------ path & file facts

    private static string ValidateAbsolutePath(string raw, string code)
    {
        if (string.IsNullOrWhiteSpace(raw))
        {
            throw new HostIssuerException(code, "path is empty");
        }

        var parts = raw.Split(new[] { '\\', '/' }, StringSplitOptions.None);
        if (parts.Any(part => part is "." or ".."))
        {
            throw new HostIssuerException(code, "path contains a relative segment");
        }

        if (!Path.IsPathFullyQualified(raw))
        {
            throw new HostIssuerException(code, "path is not absolute");
        }

        return Path.GetFullPath(raw);
    }

    private static void RejectReparseComponents(string path)
    {
        var full = Path.GetFullPath(path);
        var root = Path.GetPathRoot(full) ?? string.Empty;
        var probe = root;
        foreach (var part in full[root.Length..].Split(
                     new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                     StringSplitOptions.RemoveEmptyEntries))
        {
            probe = Path.Combine(probe, part);
            if (!File.Exists(probe) && !Directory.Exists(probe))
            {
                throw new HostIssuerException("REF_SCOPE_DENIED", "path component does not exist");
            }

            var attributes = File.GetAttributes(probe);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
            {
                throw new HostIssuerException("REF_REPARSE_POINT", "path contains a reparse point");
            }
        }
    }

    private static (ulong Volume, ulong Index, long Size, bool Reparse) FileIdentity(string path)
    {
        var handle = CreateFileW(
            path,
            0x80,
            0x1 | 0x2 | 0x4,
            IntPtr.Zero,
            3,
            0x02000000 | 0x80,
            IntPtr.Zero);
        if (handle == new IntPtr(-1))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "cannot open import source for identity");
        }

        try
        {
            if (!GetFileInformationByHandle(handle, out var info))
            {
                throw new HostIssuerException("REF_SCOPE_DENIED", "cannot read import source identity");
            }

            ulong index = ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow;
            var size = ((long)info.FileSizeHigh << 32) | info.FileSizeLow;
            var reparse = (info.FileAttributes & 0x400) != 0;
            return (info.VolumeSerialNumber, index, size, reparse);
        }
        finally
        {
            CloseHandle(handle);
        }
    }

    private static (ulong Volume, ulong Index) DirectoryIdentity(string directory)
    {
        var handle = CreateFileW(
            directory,
            0x80,
            0x1 | 0x2 | 0x4,
            IntPtr.Zero,
            3,
            0x02000000,
            IntPtr.Zero);
        if (handle == new IntPtr(-1))
        {
            throw new HostIssuerException("REF_SCOPE_DENIED", "cannot open import folder for identity");
        }

        try
        {
            if (!GetFileInformationByHandle(handle, out var info))
            {
                throw new HostIssuerException("REF_SCOPE_DENIED", "cannot read import folder identity");
            }

            return (info.VolumeSerialNumber, ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow);
        }
        finally
        {
            CloseHandle(handle);
        }
    }

    private static int NaturalCompare(string left, string right)
    {
        var leftParts = SplitNatural(left);
        var rightParts = SplitNatural(right);
        for (var index = 0; index < Math.Min(leftParts.Count, rightParts.Count); index++)
        {
            var (leftIsNumber, leftNumber, leftText) = leftParts[index];
            var (rightIsNumber, rightNumber, rightText) = rightParts[index];
            if (leftIsNumber && rightIsNumber)
            {
                var compare = leftNumber.CompareTo(rightNumber);
                if (compare != 0)
                {
                    return compare;
                }
            }
            else
            {
                var compare = string.CompareOrdinal(leftText.ToLowerInvariant(), rightText.ToLowerInvariant());
                if (compare != 0)
                {
                    return compare;
                }
            }
        }

        return leftParts.Count.CompareTo(rightParts.Count);
    }

    private static List<(bool IsNumber, long Number, string Text)> SplitNatural(string value)
    {
        var parts = new List<(bool, long, string)>();
        foreach (var part in NumberPattern.Split(value))
        {
            if (part.Length == 0)
            {
                continue;
            }

            parts.Add(long.TryParse(part, NumberStyles.None, CultureInfo.InvariantCulture, out var number)
                ? (true, number, part)
                : (false, 0, part));
        }

        return parts;
    }

    // ------------------------------------------------------------------ JSON helpers

    private static string ReadRequiredString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString() ?? string.Empty
            : throw new HostIssuerException("INVALID_REQUEST", $"{property} must be a string");

    private static IReadOnlyList<string> ReadUniqueStrings(JsonElement element, string property)
    {
        if (!element.TryGetProperty(property, out var value) ||
            value.ValueKind != JsonValueKind.Array ||
            value.GetArrayLength() == 0)
        {
            throw new HostIssuerException("INVALID_REQUEST", $"{property} must be a non-empty array");
        }

        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var item in value.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.String ||
                item.GetString() is not { Length: > 0 } text ||
                !seen.Add(text))
            {
                throw new HostIssuerException("INVALID_REQUEST", $"{property} contains an invalid id");
            }
        }

        return seen.ToList();
    }

    private static JsonElement BuildJson(Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream(256);
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions
               {
                   Indented = false,
                   Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
               }))
        {
            write(writer);
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }

    private static void AppendMember(StringBuilder builder, string name, string value, bool first = false)
    {
        if (!first)
        {
            builder.Append(',');
        }

        AppendString(builder, name);
        builder.Append(':');
        AppendString(builder, value);
    }

    private static void AppendString(StringBuilder builder, string value)
    {
        builder.Append('"');
        foreach (var ch in value)
        {
            switch (ch)
            {
                case '"':
                    builder.Append("\\\"");
                    break;
                case '\\':
                    builder.Append("\\\\");
                    break;
                case '\b':
                    builder.Append("\\b");
                    break;
                case '\f':
                    builder.Append("\\f");
                    break;
                case '\n':
                    builder.Append("\\n");
                    break;
                case '\r':
                    builder.Append("\\r");
                    break;
                case '\t':
                    builder.Append("\\t");
                    break;
                default:
                    if (ch < 0x20)
                    {
                        builder.Append("\\u").Append(((int)ch).ToString("x4", CultureInfo.InvariantCulture));
                    }
                    else
                    {
                        builder.Append(ch);
                    }

                    break;
            }
        }

        builder.Append('"');
    }

    private sealed record ImportEntry(
        string Path, ulong VolumeSerial, ulong FileIndex, long Size, string Sha256);

    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation
    {
        public uint FileAttributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
        public uint VolumeSerialNumber;
        public uint FileSizeHigh;
        public uint FileSizeLow;
        public uint NumberOfLinks;
        public uint FileIndexHigh;
        public uint FileIndexLow;
    }

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern IntPtr CreateFileW(
        string fileName,
        uint desiredAccess,
        uint shareMode,
        IntPtr securityAttributes,
        uint creationDisposition,
        uint flagsAndAttributes,
        IntPtr templateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetFileInformationByHandle(
        IntPtr file, out ByHandleFileInformation information);

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool CloseHandle(IntPtr handle);
}
