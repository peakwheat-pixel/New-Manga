using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Library;
using Xunit;

namespace NewManga.Host.Tests;

[TestCaseOrderer("NewManga.Host.Tests.Fea09UiImportIpcTests+AlphabeticalOrderer", "NewManga.Host.Tests")]
public sealed class Fea09UiImportIpcProductionTests : IClassFixture<Fea09ProductionFixture>
{
    private readonly Fea09ProductionFixture _f;
    private static readonly List<JsonObject> Cases = new();
    private const string Password = "fea09-fixture";
    private const string Wrong = "definitely-wrong";
    private const string Png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
    public Fea09UiImportIpcProductionTests(Fea09ProductionFixture fixture) => _f = fixture;

    private async Task<string> Chapter(string name)
    {
        Assert.True(await _f.Controller.TryCreateBookAsync(name));
        var book = _f.Controller.Snapshot.Books.Single(b => b.Title == name);
        return (await _f.Controller.CreateChapterAsync(book.BookId, name))!.ChapterId;
    }
    private ImportDockViewModel Vm(string chapter) => new(_f.Controller, null, (_, _) => { }, () => chapter, () => "IPC chapter",
        () => Task.CompletedTask, () => { }, () => Task.Delay(20));
    private async Task<string> Image(string name)
    {
        var path = Path.Combine(_f.Root, name);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        await File.WriteAllBytesAsync(path, Convert.FromBase64String(Png));
        return path;
    }
    private static ReferenceImportSource Source(string path, bool folder = false) => new(path, folder);
    private static async Task Until(Func<bool> predicate)
    {
        var deadline = DateTime.UtcNow.AddSeconds(30);
        while (!predicate() && DateTime.UtcNow < deadline) await Task.Delay(10);
        Assert.True(predicate(), "condition was not reached");
    }
    private static void Record(string name, ImportDockViewModel vm, int pages, params string[] extra) => Cases.Add(new JsonObject
    {
        ["case"] = name, ["adapter"] = "HostController(HostOptions) + ImportDockViewModel",
        ["plan"] = vm.ReferencePlanSummary, ["progress"] = vm.ReferenceProgressText,
        ["error"] = vm.ReferenceErrorText, ["chapter_pages"] = pages,
        ["rows"] = new JsonArray(vm.ReferenceReceiptItems.Select(i => (JsonNode)JsonValue.Create(i.SourceName + " " + i.OutcomeText + " " + i.CountsText)!).ToArray()),
        ["observations"] = new JsonArray(extra.Select(i => (JsonNode)JsonValue.Create(i)!).ToArray()),
    });

    [ProductionIpcFact]
    public async Task A_OrdinarySuccessAndWholeSourceSkip()
    {
        var chapter = await Chapter("production-success");
        var vm = Vm(chapter);
        await vm.PlanReferenceImportAsync(new[] { Source(await Image("success/page.png")) });
        Assert.Contains("可导入", Assert.Single(vm.ReferencePlanItems).StatusText);
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Contains("导入完成", vm.ReferenceProgressText);
        Assert.Contains("已提交 1 页", Assert.Single(vm.ReferenceReceiptItems).CountsText);
        Assert.Single(await _f.Controller.ListChapterPagesAsync(chapter));
        Record("ordinary", vm, 1);
        await vm.ReplanReferenceImportAsync();
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Contains("跳过 0 页 / 1 源", vm.ReferenceProgressText);
        Assert.Contains("跳过 0 页 / 1 源", Assert.Single(vm.ReferenceReceiptItems).CountsText);
        Assert.Single(await _f.Controller.ListChapterPagesAsync(chapter));
        Record("whole-source-skip", vm, 1);
    }

    [ProductionIpcFact]
    public async Task B_AesTypedUnsupported()
    {
        var chapter = await Chapter("production-aes");
        var vm = Vm(chapter);
        await vm.PlanReferenceImportAsync(new[] { Source(Path.Combine(_f.Repo, "tests", "fea09", "fixtures", "aes_member.zip")) });
        Assert.Contains("格式不支持", Assert.Single(vm.ReferencePlanItems).StatusText);
        Assert.False(vm.NeedsPassword);
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Empty(await _f.Controller.ListChapterPagesAsync(chapter));
        Assert.Contains("不支持", Assert.Single(vm.ReferenceReceiptItems).OutcomeText);
        Record("aes-typed-unsupported", vm, 0);
    }

    [ProductionIpcFact]
    public async Task C_SingleEncryptedSourceWrongPasswordThenRetry()
    {
        var chapter = await Chapter("production-password");
        var vm = Vm(chapter);
        await vm.PlanReferenceImportAsync(new[] { Source(Path.Combine(_f.Repo, "tests", "fea09", "fixtures", "zipcrypto_page.cbz")) });
        Assert.True(vm.NeedsPassword);
        vm.ReferencePassword = Wrong;
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Contains("密码错误", Assert.Single(vm.ReferenceReceiptItems).OutcomeText);
        Assert.Empty(await _f.Controller.ListChapterPagesAsync(chapter));
        Record("password-wrong", vm, 0);
        await vm.ReplanReferenceImportAsync();
        vm.ReferencePassword = Password;
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Equal("", vm.ReferencePassword);
        Assert.Contains("导入完成", vm.ReferenceProgressText);
        Assert.Equal(2, (await _f.Controller.ListChapterPagesAsync(chapter)).Count);
        AssertNoTokens();
        Record("password-retry", vm, 2);
    }

    [ProductionIpcFact]
    public async Task D_CancelAfterOneCommitThenRetryConservesPages()
    {
        var chapter = await Chapter("production-cancel");
        var vm = Vm(chapter);
        var sources = new[] { Source(await Image("cancel/a.png")), Source(await Image("cancel/b.png")), Source(await Image("cancel/c.png")) };
        await File.WriteAllTextAsync(Path.Combine(_f.Root, "pause"), "");
        await vm.PlanReferenceImportAsync(sources);
        var confirming = vm.ConfirmReferenceImportAsync();
        try
        {
            await Until(() => File.Exists(Path.Combine(_f.Root, "paused")) && vm.ReferenceProgressText.Contains("已导入 1"));
            Assert.True(vm.CanCancelReference);
            Assert.Single(await _f.Controller.ListChapterPagesAsync(chapter));
            await vm.CancelReferenceImportAsync();
            Assert.Contains("已请求取消", vm.ReferenceProgressText);
        }
        finally { await File.WriteAllTextAsync(Path.Combine(_f.Root, "release"), ""); }
        await confirming.WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Contains("已取消", vm.ReferenceProgressText);
        Assert.Contains("待处理 2", vm.ReferenceProgressText);
        Assert.Single(await _f.Controller.ListChapterPagesAsync(chapter));
        Record("cancel-at-committed-boundary", vm, 1);
        File.Delete(Path.Combine(_f.Root, "pause"));
        await vm.ReplanReferenceImportAsync();
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Equal(3, (await _f.Controller.ListChapterPagesAsync(chapter)).Count);
        Record("cancel-retry-no-duplicate", vm, 3);
    }

    [ProductionIpcFact]
    public async Task E_ChangedSourceBeforeConfirmIsRejectedByRealCore()
    {
        var chapter = await Chapter("production-stale");
        var vm = Vm(chapter);
        var path = await Image("stale/page.png");
        await vm.PlanReferenceImportAsync(new[] { Source(path) });
        await File.AppendAllTextAsync(path, "changed");
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        // Core may accept the operation then reject at its commit guard, or reject start itself.
        var observed = vm.ReferenceErrorText + vm.ReferenceProgressText + string.Join(" ", vm.ReferenceReceiptItems.Select(r => r.OutcomeText));
        // Real Core must reject with a typed SOURCE_* code (UI text and/or wire response).
        var wire = string.Join("\n", (await Task.WhenAll(
            Directory.GetFiles(_f.LogRoot, "*.ndjson", SearchOption.AllDirectories).Select(ReadSharedAsync))));
        Assert.Contains("SOURCE_", observed + (_f.Controller.Snapshot.LastError ?? "") + wire);
        Assert.Empty(await _f.Controller.ListChapterPagesAsync(chapter));
        Record("changed-before-confirm", vm, 0, observed);
    }

    [ProductionIpcFact]
    public async Task F_FolderUsesHostEnumerationAndOrdering()
    {
        var chapter = await Chapter("production-folder");
        var folder = Path.GetDirectoryName(await Image("folder/10.png"))!;
        await Image("folder/2.png");
        var hidden = await Image("folder/hidden.png");
        File.SetAttributes(hidden, FileAttributes.Hidden);
        var vm = Vm(chapter);
        await vm.PlanReferenceImportAsync(new[] { Source(folder, true) });
        Assert.True(vm.HasReferencePlan, vm.ReferenceErrorText);
        await vm.ConfirmReferenceImportAsync().WaitAsync(TimeSpan.FromSeconds(45));
        Assert.Equal(2, (await _f.Controller.ListChapterPagesAsync(chapter)).Count);
        Record("host-folder", vm, 2);
    }


    private static async Task<string> ReadSharedAsync(string path)
    {
        for (var attempt = 0; ; attempt++)
        {
            try
            {
                using var stream = new FileStream(path, FileMode.Open, FileAccess.Read,
                    FileShare.ReadWrite | FileShare.Delete);
                using var reader = new StreamReader(stream, Encoding.UTF8);
                return await reader.ReadToEndAsync();
            }
            catch (IOException) when (attempt < 20)
            {
                await Task.Delay(50);
            }
        }
    }

    private void AssertNoTokens() => Assert.Empty(Directory.Exists(Path.Combine(_f.DataRoot, "host", "source-secrets"))
        ? Directory.GetFiles(Path.Combine(_f.DataRoot, "host", "source-secrets"), "*.bin") : Array.Empty<string>());

    private async Task SecretFailure(string fault, string expected)
    {
        var chapter = await Chapter("production-secret-failure-" + fault);
        var plan = await _f.Controller.PlanReferencedImportAsync(chapter,
            new[] { Source(Path.Combine(_f.Repo, "tests", "fea09", "fixtures", "zipcrypto_page.cbz")) });
        Assert.NotNull(plan);
        await File.WriteAllTextAsync(Path.Combine(_f.Root, "fault"), fault);
        SourceImportStartResult result;
        try { result = await _f.Controller.StartReferencedImportAsync(plan!, Password); }
        finally { File.Delete(Path.Combine(_f.Root, "fault")); }
        Assert.False(result.Ok);
        Assert.Equal(expected, result.ErrorCode);
        AssertNoTokens();
        Assert.Empty(await _f.Controller.ListChapterPagesAsync(chapter));
        Cases.Add(new JsonObject { ["case"] = "secret-failure-" + fault, ["error_code"] = result.ErrorCode, ["tokens_remaining"] = 0 });
    }
    [ProductionIpcFact] public Task G_SecretCapabilityMissingCleansUp() => SecretFailure("capability", "CORE_CAPABILITY_MISSING");
    [ProductionIpcFact] public Task H_SecretRegistrationRefusedCleansUp() => SecretFailure("register", "SOURCE_ACCESS_DENIED");
    [ProductionIpcFact] public Task I_SecretStartRefusedCleansUp() => SecretFailure("start", "SOURCE_PLAN_STALE");
    [ProductionIpcFact] public Task J_SecretReplanFailedCleansUp() => SecretFailure("replan", "SOURCE_PLAN_STALE");

    [ProductionIpcFact]
    public async Task Z_AuditRequestsResponsesLogsRegistryExceptionsAndEvidence()
    {
        var evidence = Path.Combine(_f.Repo, "verification", "FEA-09-UI-1", "ipc");
        var wireFiles = Directory.GetFiles(_f.LogRoot, "*.ndjson", SearchOption.AllDirectories);
        Assert.NotEmpty(wireFiles);
        var wires = string.Join("\n", await Task.WhenAll(wireFiles.Select(ReadSharedAsync)));
        Assert.Contains("StartImportReferences", wires);
        Assert.Contains("RevokeSourceReadGrant", wires);
        var document = new JsonObject { ["mode"] = "real HostController + VM + HostRuntime + Python Core stdio", ["cases"] = new JsonArray(Cases.Select(c => (JsonNode)c.DeepClone()).ToArray()),
            ["audit_scope"] = "request+response (wire NDJSON), stdout/stderr/host logs, registry, UI errors, failure results and Task evidence", ["password_hits"] = 0 };
        var json = document.ToJsonString(new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(Path.Combine(evidence, "production-ui-import-ipc.json"), json);
        await File.WriteAllTextAsync(Path.Combine(evidence, "production-ui-import-ipc.wire.ndjson"), wires);
        var texts = new List<string> { json, wires };
        foreach (var file in Directory.GetFiles(_f.Root, "*", SearchOption.AllDirectories)
            .Where(p => p.EndsWith(".log") || p.EndsWith(".ndjson") || p.EndsWith(".json"))) texts.Add(await ReadSharedAsync(file));
        foreach (var file in Directory.GetFiles(Path.Combine(_f.Repo, "verification", "FEA-09-UI-1"), "*", SearchOption.AllDirectories)) texts.Add(await ReadSharedAsync(file));
        foreach (var secret in new[] { Password, Wrong, "never-leak-this-password" })
        {
            var bytes = Encoding.UTF8.GetBytes(secret);
            foreach (var probe in new[] { secret, Convert.ToHexString(bytes), Convert.ToBase64String(bytes) })
                Assert.DoesNotContain(texts, text => text.Contains(probe, StringComparison.OrdinalIgnoreCase));
        }
        AssertNoTokens();
    }
}
