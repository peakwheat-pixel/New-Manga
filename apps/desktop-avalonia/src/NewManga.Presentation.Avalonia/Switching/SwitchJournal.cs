using System.Text.Json;
using System.Text.Json.Serialization;

namespace NewManga.Presentation.Avalonia.Switching;

/// <summary>One durable switch-journal entry (FEA-07 / proposal §7.1 crash recovery).</summary>
public sealed record SwitchJournalEntry(
    string TargetFrontendId,
    string? PreviousFrontendId,
    SwitchStage Stage,
    DateTimeOffset StartedAt,
    DateTimeOffset UpdatedAt,
    string? Failure);

/// <summary>
/// Restart-safe switch journal. The file is rewritten atomically on every stage change, so an
/// interrupted switch is always observable on the next start and can be rolled back.
/// </summary>
public sealed class SwitchJournal
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
        Converters = { new JsonStringEnumConverter() },
    };

    private readonly string _path;

    public SwitchJournal(string path)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        _path = Path.GetFullPath(path);
    }

    /// <summary>Absolute journal file path (diagnostics/tests).</summary>
    public string FilePath => _path;

    /// <summary>Starts (or restarts) a switch attempt for <paramref name="targetFrontendId"/>.</summary>
    public SwitchJournalEntry Begin(string targetFrontendId, string? previousFrontendId = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(targetFrontendId);
        var now = DateTimeOffset.UtcNow;
        var entry = new SwitchJournalEntry(targetFrontendId, previousFrontendId, SwitchStage.Preparing, now, now, Failure: null);
        Write(entry);
        return entry;
    }

    /// <summary>Moves the current attempt forward; never moves backwards.</summary>
    public SwitchJournalEntry Advance(SwitchStage stage)
    {
        if (stage is SwitchStage.Idle or SwitchStage.RolledBack or SwitchStage.Committed)
        {
            throw new ArgumentOutOfRangeException(nameof(stage), stage, "stage is terminal and cannot be advanced to");
        }

        var current = ReadRequired();
        if (stage <= current.Stage)
        {
            throw new InvalidOperationException($"switch stage cannot move backwards ({current.Stage} -> {stage})");
        }

        var next = current with { Stage = stage, UpdatedAt = DateTimeOffset.UtcNow };
        Write(next);
        return next;
    }

    /// <summary>Marks the attempt as failed and rolls the journal back; the entry is kept for diagnostics.</summary>
    public SwitchJournalEntry Rollback(string failure)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(failure);
        var current = ReadRequired();
        var next = current with
        {
            Stage = SwitchStage.RolledBack,
            Failure = failure,
            UpdatedAt = DateTimeOffset.UtcNow,
        };
        Write(next);
        return next;
    }

    /// <summary>Marks the attempt as committed and removes the journal file.</summary>
    public void Commit()
    {
        var current = ReadRequired();
        var next = current with { Stage = SwitchStage.Committed, UpdatedAt = DateTimeOffset.UtcNow };
        Write(next);
        TryDelete();
    }

    /// <summary>
    /// Reads the last entry. Returns false when the journal is absent or unreadable (a corrupt file is
    /// treated as no in-flight switch and surfaced through <paramref name="error"/>).
    /// </summary>
    public bool TryRead(out SwitchJournalEntry? entry, out string? error)
    {
        entry = null;
        error = null;
        if (!File.Exists(_path))
        {
            return false;
        }

        try
        {
            var json = File.ReadAllText(_path);
            entry = JsonSerializer.Deserialize<SwitchJournalEntry>(json, JsonOptions);
            if (entry is null)
            {
                error = "switch journal contained an empty entry";
                return false;
            }

            return true;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException)
        {
            error = ex.Message;
            return false;
        }
    }

    /// <summary>True when the journal still records an in-flight (not committed/rolled back) switch.</summary>
    public bool HasInterruptedSwitch(out SwitchJournalEntry? entry)
    {
        if (!TryRead(out entry, out _) || entry is null)
        {
            return false;
        }

        return entry.Stage is not (SwitchStage.Committed or SwitchStage.RolledBack or SwitchStage.Idle);
    }

    private SwitchJournalEntry ReadRequired()
    {
        if (!TryRead(out var entry, out var error) || entry is null)
        {
            throw new InvalidOperationException("switch journal has no active entry", new IOException(error ?? "missing journal"));
        }

        return entry;
    }

    private void Write(SwitchJournalEntry entry)
    {
        var directory = Path.GetDirectoryName(_path);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var temp = _path + ".tmp";
        File.WriteAllText(temp, JsonSerializer.Serialize(entry, JsonOptions));
        File.Move(temp, _path, overwrite: true);
    }

    private void TryDelete()
    {
        try
        {
            File.Delete(_path);
        }
        catch (IOException)
        {
            // A committed journal left behind is harmless: HasInterruptedSwitch treats Committed as terminal.
        }
        catch (UnauthorizedAccessException)
        {
            // Same as above; recovery never blocks startup on a stale terminal journal.
        }
    }
}
