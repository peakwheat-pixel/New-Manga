using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-AI-1 (PREQ AI P21-P25): the five prompt-template ports must degrade
/// safely on the null host and be observable on the headless fake. The fake is
/// stricter where it matters: builtin rows cannot be overwritten or deleted.
/// </summary>
public sealed class PromptTemplatePortTests
{
    [Fact]
    public async Task NullHost_PromptTemplatePorts_DegradeWithoutThrowing()
    {
        IHostController host = NullHostController.Instance;
        Assert.Empty(await host.ListPromptTemplatesAsync(CancellationToken.None));
        Assert.Null(await host.SavePromptTemplateAsync("n", "b", cancellationToken: CancellationToken.None));
        Assert.False((await host.DeletePromptTemplateAsync("t", "r", CancellationToken.None)).Deleted);
        Assert.Null(await host.CopyBuiltinPromptTemplateAsync("builtin", cancellationToken: CancellationToken.None));
        Assert.Empty(await host.GetPromptTemplateReferencesAsync("t", CancellationToken.None));
    }

    [Fact]
    public async Task FakeHost_SaveCreateAndUpdateBumpTheVersion()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        Assert.Single(await host.ListPromptTemplatesAsync(CancellationToken.None));

        var created = await host.SavePromptTemplateAsync("Mine", "body", cancellationToken: CancellationToken.None);
        Assert.NotNull(created);
        Assert.Equal(1, created!.Version);
        Assert.False(created.Builtin);

        var updated = await host.SavePromptTemplateAsync(
            "Mine v2", "body2", created.TemplateId, CancellationToken.None);
        Assert.NotNull(updated);
        Assert.Equal(2, updated!.Version);
        Assert.Equal(created.TemplateId, updated.TemplateId);
        Assert.Equal(1, host.PromptTemplates.Count(template => !template.Builtin));
    }

    [Fact]
    public async Task FakeHost_BuiltinsAreReadOnlyAndCopyable()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var builtin = Assert.Single(host.PromptTemplates);

        Assert.Null(await host.SavePromptTemplateAsync(
            "Hijack", "body", builtin.TemplateId, CancellationToken.None));
        Assert.False((await host.DeletePromptTemplateAsync(
            builtin.TemplateId, "replacement", CancellationToken.None)).Deleted);

        var copy = await host.CopyBuiltinPromptTemplateAsync(builtin.TemplateId, cancellationToken: CancellationToken.None);
        Assert.NotNull(copy);
        Assert.False(copy!.Builtin);
        Assert.Equal($"{builtin.Name} (copy)", copy.Name);
        Assert.Equal((builtin.TemplateId, (string?)null), host.LastCopiedPromptTemplate);
    }

    [Fact]
    public async Task FakeHost_DeleteRecordsTheReplacementAndHidesTheTemplate()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var created = await host.SavePromptTemplateAsync("Del", "body", cancellationToken: CancellationToken.None);
        var replacement = await host.SavePromptTemplateAsync("Keep", "body", cancellationToken: CancellationToken.None);

        var result = await host.DeletePromptTemplateAsync(
            created!.TemplateId, replacement!.TemplateId, CancellationToken.None);
        Assert.True(result.Deleted);
        Assert.Equal((created.TemplateId, replacement.TemplateId), host.LastDeletedPromptTemplate);
        Assert.DoesNotContain(host.PromptTemplates, template => template.TemplateId == created.TemplateId);

        host.PromptTemplateReferences.Add(new PromptTemplateReference("translation", "owner-1", "Chapter 1"));
        var references = await host.GetPromptTemplateReferencesAsync(created.TemplateId, CancellationToken.None);
        Assert.Equal(new PromptTemplateReference("translation", "owner-1", "Chapter 1"), Assert.Single(references));
    }
}
