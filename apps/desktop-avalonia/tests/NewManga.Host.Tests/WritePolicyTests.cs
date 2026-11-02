using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// V11R-A-5 (P0 write policy): the shipped GUI must be writable by default. The migration-era
/// "read-only until S2 parity" default made import / create book / create chapter / Run fail for every
/// release user (the installer shortcut passes no arguments). Read-only is now reserved for real
/// preconditions: legacy Tauri shell detected, explicit <c>--parity=false</c>, or the host not ready.
/// </summary>
public sealed class WritePolicyTests
{
    private static HostOptions Options(
        string label,
        string dataRoot,
        bool parity,
        string? sidecarDirectory = null,
        bool detectLegacyShell = false,
        IProcessNameProbe? processProbe = null)
    {
        return new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", label),
            SidecarDirectoryOverride = sidecarDirectory ?? HostFixture.SidecarDirectory,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            ParityReached = parity,
            DetectLegacyShell = detectLegacyShell,
            ProcessProbe = processProbe,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(90),
        };
    }

    [Fact]
    public void HostOptions_DefaultParity_IsWritable()
    {
        var defaults = new HostOptions
        {
            DataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a5-unit"),
            LogDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a5-unit-logs"),
        };

        Assert.True(defaults.ParityReached);
        Assert.Equal(HostMode.ReadWrite, CoexistenceRules.Decide(false, defaults.ParityReached).Mode);
    }

    [Fact]
    public void LegacyShell_StillWins_OverDefaultParity()
    {
        // AC3: the legacy coexistence guard must never be weakened by the new writable default.
        var decision = CoexistenceRules.Decide(legacyShellRunning: true, parityReached: true);

        Assert.Equal(HostMode.ReadOnlyLegacyShellRunning, decision.Mode);
    }

    [HostSidecarFact]
    public async Task DefaultStart_IsReadWrite_AndCanCreateBook()
    {
        var dataRoot = HostFixture.NewDataRoot("write-policy-default");
        var options = Options("write-policy-default", dataRoot, parity: true);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadWrite, runtime.Mode);
            Assert.True(runtime.Policy.WritesAllowed, runtime.Policy.Reason);

            // AC1: a real write against the isolated root actually commits through the Core.
            var book = await runtime.CreateBookAsync("V11R-A-5 默认可写夹具");
            Assert.False(string.IsNullOrWhiteSpace(book.BookId));
            var books = await runtime.ListBooksAsync();
            Assert.Contains(books, candidate => candidate.BookId == book.BookId);

            HostFixture.WriteEvidenceJson("write-policy/default-start.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1");
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("created_book_id", book.BookId);
                writer.WriteNumber("listed_books", books.Count);
                writer.WriteBoolean("host_ready", runtime.Result.IsReady);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [HostSidecarFact]
    public async Task ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError()
    {
        var dataRoot = HostFixture.NewDataRoot("write-policy-readonly");
        var options = Options("write-policy-readonly", dataRoot, parity: false);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadOnlyUntilParity, runtime.Mode);
            Assert.False(runtime.Policy.WritesAllowed);

            var refused = await Assert.ThrowsAsync<ReadOnlyHostException>(
                () => runtime.CreateBookAsync("V11R-A-5 只读夹具"));
            Assert.Equal("HOST_READ_ONLY", refused.Code);

            HostFixture.WriteEvidenceJson("write-policy/parity-false.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2");
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("refusal_code", refused.Code);
                writer.WriteString("refusal_message", refused.Message);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [Fact]
    public async Task LegacyShellDetected_KeepsHostReadOnly_EvenWithDefaultParity()
    {
        var dataRoot = HostFixture.NewDataRoot("write-policy-legacy");
        var missingSidecars = Path.Combine(Path.GetTempPath(), "newmanga-a5-missing-sidecars-" + Guid.NewGuid().ToString("N")[..8]);
        var options = Options(
            "write-policy-legacy",
            dataRoot,
            parity: true,
            sidecarDirectory: missingSidecars,
            detectLegacyShell: true,
            processProbe: new ScriptedProcessProbe(new[] { 4321, 4322 }));
        try
        {
            // Sidecars are intentionally absent: the runtime must still settle its policy first, then
            // fail closed on the sidecar lookup.
            await using var runtime = await HostRuntime.StartAsync(options);

            Assert.Equal(HostMode.ReadOnlyLegacyShellRunning, runtime.Mode);
            Assert.False(runtime.Policy.WritesAllowed);
            Assert.True(runtime.LegacyShell.Detected);
            Assert.False(runtime.Result.IsReady);

            var refused = await Assert.ThrowsAsync<ReadOnlyHostException>(
                () => runtime.CreateBookAsync("V11R-A-5 旧壳只读夹具"));
            Assert.Equal("HOST_READ_ONLY", refused.Code);

            HostFixture.WriteEvidenceJson("write-policy/legacy-shell.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3");
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteBoolean("legacy_shell_detected", runtime.LegacyShell.Detected);
                writer.WriteString("refusal_code", refused.Code);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
            HostFixture.TryDeleteDirectory(missingSidecars);
        }
    }

    [HostSidecarFact]
    public async Task FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog()
    {
        var dataRoot = HostFixture.NewDataRoot("write-policy-backup");
        var backupDirectory = Path.Combine(dataRoot, "backups");
        try
        {
            // Session 1: writable default; the Core creates catalog/catalog.sqlite during this run, so
            // the pre-start backup legitimately has nothing to copy yet.
            await using (var first = await HostRuntime.StartAsync(Options("write-policy-backup-a", dataRoot, parity: true)))
            {
                Assert.True(first.Result.IsReady, first.Result.ErrorCode);
                Assert.Equal(HostMode.ReadWrite, first.Mode);
                Assert.True(first.Backup is null || !first.Backup.Created);
            }

            Assert.True(File.Exists(Path.Combine(dataRoot, "catalog", "catalog.sqlite")));
            Assert.False(Directory.Exists(backupDirectory) &&
                         Directory.EnumerateFiles(backupDirectory, "*.nmbak").Any());

            // Session 2: the first-run backup now copies the real catalog before the Core starts.
            await using (var second = await HostRuntime.StartAsync(Options("write-policy-backup-b", dataRoot, parity: true)))
            {
                Assert.True(second.Result.IsReady, second.Result.ErrorCode);
                Assert.Equal(HostMode.ReadWrite, second.Mode);
                Assert.NotNull(second.Backup);
                Assert.True(second.Backup!.Created, second.Backup.SkippedReason);
                Assert.False(string.IsNullOrWhiteSpace(second.Backup.FileName));

                var backupPath = Path.Combine(backupDirectory, second.Backup.FileName!);
                Assert.True(File.Exists(backupPath), backupPath);
                var size = new FileInfo(backupPath).Length;
                Assert.True(size > 0, $"backup file is empty: {backupPath}");

                // The data root is a disposable temp directory; keep a byte copy of the real backup in
                // the evidence directory so the AC4 artifact survives the cleanup.
                var evidenceCopy = Path.Combine(
                    HostFixture.EvidenceDirectory, "write-policy", "first-run-backup.nmbak");
                Directory.CreateDirectory(Path.GetDirectoryName(evidenceCopy)!);
                File.Copy(backupPath, evidenceCopy, overwrite: true);

                HostFixture.WriteEvidenceJson("write-policy/first-run-backup.json", writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("ac", "AC4");
                    writer.WriteString("mode", second.Mode.ToString());
                    writer.WriteBoolean("writes_allowed", second.Policy.WritesAllowed);
                    writer.WriteString("backup_file_name", second.Backup.FileName);
                    writer.WriteString("backup_file_path", backupPath);
                    writer.WriteNumber("backup_file_bytes", size);
                    writer.WriteString("backup_evidence_copy", evidenceCopy);
                    writer.WriteNumber("backup_evidence_copy_bytes", new FileInfo(evidenceCopy).Length);
                    writer.WriteString("data_root", dataRoot);
                    writer.WriteEndObject();
                });
            }
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    private sealed class ScriptedProcessProbe : IProcessNameProbe
    {
        private readonly IReadOnlyList<int> _processIds;

        public ScriptedProcessProbe(IReadOnlyList<int> processIds) => _processIds = processIds;

        public IReadOnlyList<int> FindProcessIds(string processName) => _processIds;
    }
}
