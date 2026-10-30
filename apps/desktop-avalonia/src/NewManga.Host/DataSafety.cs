namespace NewManga.Host;

/// <summary>Raised when a write is attempted while the host is read-only (S2 parity / legacy shell).</summary>
public sealed class ReadOnlyHostException : Exception
{
    public ReadOnlyHostException(string message)
        : base(message)
    {
    }

    public string Code => "HOST_READ_ONLY";
}

/// <summary>Data-root write policy derived from the coexistence mode.</summary>
public sealed record DataRootPolicy(string DataRoot, HostMode Mode, bool WritesAllowed, string Reason)
{
    public static DataRootPolicy For(string dataRoot, HostMode mode)
    {
        var writesAllowed = mode == HostMode.ReadWrite;
        var reason = writesAllowed
            ? "parity reached and no legacy shell running"
            : CoexistenceRules.Describe(mode);
        return new DataRootPolicy(dataRoot, mode, writesAllowed, reason);
    }
}

public sealed record FirstRunBackupResult(bool Created, string? FileName, string? SkippedReason);

/// <summary>
/// First-run safety backup (ADR-0001 D3): copy the catalog SQLite once into a backups directory
/// before the new host ever touches shared state. Idempotent — existing backups are never replaced.
/// </summary>
public static class FirstRunBackup
{
    public static FirstRunBackupResult EnsureBackup(string dataRoot, string backupDirectory)
    {
        var catalog = Path.Combine(dataRoot, "catalog", "catalog.sqlite");
        if (!File.Exists(catalog))
        {
            return new FirstRunBackupResult(false, null, "catalog database not present yet");
        }

        if (Directory.Exists(backupDirectory))
        {
            // REALUSE-DATA-SAFETY-5 AC1 (audit MA-18): this used to skip on ANY *.nmbak, but
            // .nmbak belongs to the Core's package format (a zip). One Core backup package in the
            // same directory silently disabled the first-run catalog backup forever. Only files we
            // wrote ourselves count, including the legacy suffix so existing installs stay idempotent.
            foreach (var pattern in new[] { "catalog.*.sqlite-backup", "*.sqlite.nmbak" })
            {
                foreach (var existing in Directory.EnumerateFiles(backupDirectory, pattern))
                {
                    return new FirstRunBackupResult(false, Path.GetFileName(existing), "backup already exists");
                }
            }
        }

        Directory.CreateDirectory(backupDirectory);
        // A distinct suffix: the Core owns *.nmbak and the two formats must never share a name space.
        var fileName = $"catalog.{DateTimeOffset.UtcNow:yyyyMMddTHHmmssZ}.sqlite-backup";
        var destination = Path.Combine(backupDirectory, fileName);
        File.Copy(catalog, destination);
        return new FirstRunBackupResult(true, fileName, null);
    }
}
