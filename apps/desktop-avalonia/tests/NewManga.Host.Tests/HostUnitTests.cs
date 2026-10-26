namespace NewManga.Host.Tests;

public sealed class SingleInstanceTests
{
    [Fact]
    public void SecondAcquire_OnAnotherThread_ReportsAlreadyRunning()
    {
        var name = @"Local\NewManga.Host.Tests." + Guid.NewGuid().ToString("N");
        Assert.True(SingleInstanceGuard.TryAcquire(name, out var first));
        try
        {
            var secondAcquired = SingleInstanceGuard.TryAcquire(name, out var second);
            Assert.False(secondAcquired);
            Assert.Null(second);
        }
        finally
        {
            first!.Dispose();
        }

        Assert.True(SingleInstanceGuard.TryAcquire(name, out var third));
        third!.Dispose();
    }

    [Fact]
    public void FakeBackend_CanReportAlreadyRunning()
    {
        var backend = new ScripedBackend(acquire: false, recovered: false);
        Assert.False(SingleInstanceGuard.TryAcquire("fake", out var guard, _ => backend));
        Assert.Null(guard);
        Assert.True(backend.Disposed);
    }

    [Fact]
    public void FakeBackend_ReportsAbandonedRecovery()
    {
        var backend = new ScripedBackend(acquire: true, recovered: true);
        Assert.True(SingleInstanceGuard.TryAcquire("fake", out var guard, _ => backend));
        Assert.NotNull(guard);
        Assert.True(guard!.RecoveredAbandoned);
        guard.Dispose();
        Assert.True(backend.Released);
    }

    [Fact]
    public void DefaultGlobalName_IsPinnedByAdr()
    {
        Assert.Equal(@"Global\NewManga.Host", SingleInstanceGuard.DefaultMutexName);
    }

    private sealed class ScripedBackend : ISingleInstanceBackend
    {
        private readonly bool _acquire;
        private readonly bool _recovered;

        public ScripedBackend(bool acquire, bool recovered)
        {
            _acquire = acquire;
            _recovered = recovered;
        }

        public bool Released { get; private set; }

        public bool Disposed { get; private set; }

        public bool TryAcquire(out bool recoveredAbandoned)
        {
            recoveredAbandoned = _recovered;
            return _acquire;
        }

        public void Release() => Released = true;

        public void Dispose() => Disposed = true;
    }
}

public sealed class CoexistenceTests
{
    [Theory]
    [InlineData(false, false, HostMode.ReadOnlyUntilParity)]
    [InlineData(false, true, HostMode.ReadWrite)]
    [InlineData(true, false, HostMode.ReadOnlyLegacyShellRunning)]
    [InlineData(true, true, HostMode.ReadOnlyLegacyShellRunning)]
    public void Decide_Table(bool legacyRunning, bool parityReached, HostMode expected)
    {
        Assert.Equal(expected, CoexistenceRules.Decide(legacyRunning, parityReached).Mode);
    }

    [Fact]
    public void LegacyDetector_UsesInjectedProbe()
    {
        var detected = new LegacyShellDetector(new FakeProbe(new[] { 4321, 4322 })).Detect();
        Assert.True(detected.Detected);
        Assert.Equal(new[] { 4321, 4322 }, detected.ProcessIds);

        var absent = new LegacyShellDetector(new FakeProbe(Array.Empty<int>())).Detect();
        Assert.False(absent.Detected);
    }

    [Fact]
    public void ModeDescription_IsHumanReadable()
    {
        Assert.Contains("只读", CoexistenceRules.Describe(HostMode.ReadOnlyUntilParity), StringComparison.Ordinal);
        Assert.Contains("只读", CoexistenceRules.Describe(HostMode.ReadOnlyLegacyShellRunning), StringComparison.Ordinal);
        Assert.Contains("读写", CoexistenceRules.Describe(HostMode.ReadWrite), StringComparison.Ordinal);
    }

    private sealed class FakeProbe : IProcessNameProbe
    {
        private readonly IReadOnlyList<int> _ids;

        public FakeProbe(IReadOnlyList<int> ids) => _ids = ids;

        public IReadOnlyList<int> FindProcessIds(string processName) => _ids;
    }
}

public sealed class DataSafetyTests
{
    [Theory]
    [InlineData(HostMode.ReadOnlyUntilParity, false)]
    [InlineData(HostMode.ReadOnlyLegacyShellRunning, false)]
    [InlineData(HostMode.ReadWrite, true)]
    public void DataRootPolicy_OnlyWritableAfterParity(HostMode mode, bool expected)
    {
        Assert.Equal(expected, DataRootPolicy.For("root", mode).WritesAllowed);
    }

    [Fact]
    public void FirstRunBackup_CopiesOnce_AndStaysIdempotent()
    {
        var dataRoot = Path.Combine(Path.GetTempPath(), "newmanga-host-backup-" + Guid.NewGuid().ToString("N")[..10]);
        var catalogDirectory = Path.Combine(dataRoot, "catalog");
        Directory.CreateDirectory(catalogDirectory);
        var catalog = Path.Combine(catalogDirectory, "catalog.sqlite");
        File.WriteAllText(catalog, "sqlite-header");
        try
        {
            var first = FirstRunBackup.EnsureBackup(dataRoot, Path.Combine(dataRoot, "backups"));
            Assert.True(first.Created);
            Assert.NotNull(first.FileName);
            var backupPath = Path.Combine(dataRoot, "backups", first.FileName!);
            Assert.True(File.Exists(backupPath));
            Assert.Equal("sqlite-header", File.ReadAllText(backupPath));

            var second = FirstRunBackup.EnsureBackup(dataRoot, Path.Combine(dataRoot, "backups"));
            Assert.False(second.Created);
            Assert.Contains("already", second.SkippedReason!, StringComparison.OrdinalIgnoreCase);
        }
        finally
        {
            try
            {
                Directory.Delete(dataRoot, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // best effort
            }
        }
    }

    [Fact]
    public void FirstRunBackup_SkipsWhenNoCatalog()
    {
        var dataRoot = Path.Combine(Path.GetTempPath(), "newmanga-host-backup-empty-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(dataRoot);
        try
        {
            var result = FirstRunBackup.EnsureBackup(dataRoot, Path.Combine(dataRoot, "backups"));
            Assert.False(result.Created);
        }
        finally
        {
            try
            {
                Directory.Delete(dataRoot, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // best effort
            }
        }
    }
}
