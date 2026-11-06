using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

public sealed class SourceRegistryTests
{
    // ------------------------------------------------------------------
    // FEA-11-RUN-GRANT-1 (R-8/L-G7): the Run authorization ledger is bounded
    // ------------------------------------------------------------------

    [Fact]
    public void RunGrantLedgerIsBoundedAndPrunesExpiredGrants()
    {
        var now = 1000.0;
        var root = Path.Combine(FindRepository(), ".workspace", "FEA-11-RUN-GRANT-1",
            "fixtures", "ledger-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var registry = new SourceAccessRegistry(root);
        var coordinator = new SourceReadCoordinator(null!, registry, () => true, () => now);

        // Mint far more tracked ids than the frozen cap. ``Track`` is the same
        // accounting path every real issuance uses.
        for (var index = 0; index < SourceReadCoordinator.MaxTrackedPayloads * 2 + 7; index++)
        {
            coordinator.Track("source-" + index.ToString("D32"), "reg-run-grant", now + 300);
        }

        Assert.Equal(SourceReadCoordinator.MaxTrackedPayloads, coordinator.TrackedGrantCount);

        // Expiry prune: nothing survives the frozen 300s window.
        now += 301;
        Assert.True(coordinator.PruneExpired() > 0);
        Assert.Equal(0, coordinator.TrackedGrantCount);
        Assert.Equal(0, coordinator.TrackedPayloadCount);
        Assert.Empty(coordinator.IssuedGrantIds);
    }

    // ------------------------------------------------------------------
    // FEA-11-RUN-GRANT-1 (R-4/R-5): the Run authorization hook runs BEFORE
    // dispatch and only for the Run commands that trigger step execution.
    // ------------------------------------------------------------------

    [Fact]
    public async Task RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns()
    {
        var invoked = new List<string>();
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, _, _) =>
            {
                invoked.Add(name);
                throw new CoreOperationException(
                    "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null);
            });

        var startRun = JsonSerializer.SerializeToElement(new
        {
            command = "reocr_all",
            scope = new { kind = "page", page_id = "p1" },
            idempotency_key = "run-grant-hook",
        });
        var authorization = await Assert.ThrowsAsync<CoreOperationException>(
            () => dispatcher.InvokeAsync("library_start_run", startRun));
        // R-5: the authorization's own code is returned and the Run command is
        // never dispatched (a dispatched call would fail on the null Core with
        // a SidecarException instead).
        Assert.Equal("SOURCE_ACCESS_DENIED", authorization.Code);
        Assert.Equal(["library_start_run"], invoked);

        // Read-only Run commands never trigger the authorization hook.
        invoked.Clear();
        await Assert.ThrowsAnyAsync<Exception>(() => dispatcher.InvokeAsync(
            "library_get_run_snapshot", JsonSerializer.SerializeToElement(new { run_id = "run-1" })));
        await Assert.ThrowsAnyAsync<Exception>(() => dispatcher.InvokeAsync(
            "library_get_task_projection", JsonSerializer.SerializeToElement(new { run_id = "run-1" })));
        Assert.Empty(invoked);

        // The remaining step-triggering Run commands do call it (R-4).
        foreach (var (name, payload) in new (string, object)[]
                 {
                     ("library_control_run", new { run_id = "run-1", action = "restart", idempotency_key = "k" }),
                     ("library_resume_blocked_run", new { run_id = "run-1" }),
                     ("library_retry_failed_targets", new { run_id = "run-1", idempotency_key = "k" }),
                 })
        {
            invoked.Clear();
            var error = await Assert.ThrowsAsync<CoreOperationException>(
                () => dispatcher.InvokeAsync(name, JsonSerializer.SerializeToElement(payload)));
            Assert.Equal("SOURCE_ACCESS_DENIED", error.Code);
            Assert.Equal([name], invoked);
        }
    }

    [Fact]
    public async Task RunAuthorizationHookWithoutARefusalLetsTheRunCommandReachDispatch()
    {
        var invoked = new List<string>();
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, _, _) =>
            {
                invoked.Add(name);
                return Task.CompletedTask;
            });
        // No Core is wired: a hook that admits the Run must reach the real
        // dispatch path, which fails typed (not with the authorization code).
        var error = await Assert.ThrowsAsync<SidecarException>(() => dispatcher.InvokeAsync(
            "library_start_run",
            JsonSerializer.SerializeToElement(new
            {
                command = "reocr_all",
                scope = new { kind = "page", page_id = "p1" },
                idempotency_key = "run-grant-hook-ok",
            })));
        Assert.Equal(SidecarErrorCode.ProcessExited, error.Code);
        Assert.Equal(["library_start_run"], invoked);
    }

    [Fact]
    public void NativeDpapiCurrentUserRoundTripAndTamperRefusal()
    {
        var protector = new DpapiSecretProtector();
        var plaintext = Encoding.UTF8.GetBytes("synthetic-registry-payload");
        var ciphertext = protector.Protect(plaintext);
        Assert.False(ciphertext.SequenceEqual(plaintext));
        Assert.Equal(plaintext, protector.Unprotect(ciphertext));
        ciphertext[^1] ^= 0x42;
        Assert.Throws<SourceAccessException>(() => protector.Unprotect(ciphertext));
    }

    [Fact]
    public void EncryptedPersistenceGenerationCorruptionAndExplicitReset()
    {
        // This retained fixture is canonical evidence, not a production data root.
        var repo = FindRepository();
        var evidence = Path.Combine(repo, "verification", "FEA-09", "native-registry", Guid.NewGuid().ToString("N"));
        var source = Path.Combine(evidence, "synthetic-source");
        Directory.CreateDirectory(source);
        File.WriteAllText(Path.Combine(source, "page.txt"), "synthetic source bytes");
        var registry = new SourceAccessRegistry(Path.Combine(evidence, "isolated-data"));
        var entry = registry.Register("synthetic", [source]);
        Assert.Equal(1, entry.Generation);
        var reopened = new SourceAccessRegistry(Path.Combine(evidence, "isolated-data"));
        Assert.Equal(entry.RegistryId, Assert.Single(reopened.List()).RegistryId);
        Assert.Equal(1, reopened.Authorize(entry.RegistryId, 1, [Path.Combine(source, "page.txt")]).Generation);
        var revoked = reopened.Revoke(entry.RegistryId);
        Assert.Equal(2, revoked.Generation);
        Assert.Equal("SOURCE_GRANT_REVOKED", Assert.Throws<SourceAccessException>(() => reopened.Authorize(entry.RegistryId, 2, [source])).Code);
        var bytes = File.ReadAllBytes(registry.RegistryPath);
        Assert.StartsWith("NMSAR1", Encoding.ASCII.GetString(bytes, 0, 6));
        Assert.DoesNotContain(source, Encoding.UTF8.GetString(bytes));
        File.WriteAllBytes(registry.RegistryPath, [1, 2, 3]);
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", Assert.Throws<SourceAccessException>(() => reopened.List()).Code);
        Assert.Equal(new byte[] { 1, 2, 3 }, File.ReadAllBytes(registry.RegistryPath));
        Assert.NotEmpty(Directory.GetFiles(Path.GetDirectoryName(registry.RegistryPath)!, "*.corrupt-*"));
        Assert.Equal("INVALID_REQUEST", Assert.Throws<SourceAccessException>(() => reopened.Reset(false)).Code);
        Assert.True(Directory.Exists(reopened.Reset(true)));
        Assert.Empty(reopened.List());
    }

    private static string FindRepository()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git"))) directory = directory.Parent;
        return directory?.FullName ?? throw new InvalidOperationException("isolated repository not found");
    }
}
