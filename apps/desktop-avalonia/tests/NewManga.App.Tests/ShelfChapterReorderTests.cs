using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// CHAPTER-MANUAL-SORT AC4/AC8/AC9: the shelf VM owns every decision about a drag, so the view
/// can stay a thin gesture adapter. These facts pin the two things a drag must never do: show an
/// order that was not persisted, and interleave two whole-book rewrites.
/// </summary>
public sealed class ShelfChapterReorderTests
{
    private static readonly ChapterSummary[] ThreeChapters =
    {
        new("ch-1", "第 1 章", "1", 1),
        new("ch-2", "第 2 章", "2", 2),
        new("ch-3", "第 3 章", "3", 3),
    };

    private static async Task<(FakeHostController Host, ShelfViewModel Vm)> LoadedAsync(
        bool readOnly = false)
    {
        var host = new FakeHostController(readOnly
            ? FakeHostController.ReadOnlySnapshot("书一")
            : FakeHostController.ReadySnapshot("书一"));
        host.ChaptersByBook["book-0"] = ThreeChapters;
        var vm = new ShelfViewModel(host);
        await vm.SelectBookAsync(host.Snapshot.Books[0]);
        Assert.Equal(3, vm.Chapters.Count);
        return (host, vm);
    }

    private static string[] VisibleOrder(ShelfViewModel vm) =>
        vm.Chapters.Select(chapter => chapter.ChapterId).ToArray();

    [Fact]
    public async Task ReorderChapter_MovesTheItemAndPersistsTheNewOrder()
    {
        var (host, vm) = await LoadedAsync();

        var moved = await vm.ReorderChapterAsync(0, 2);

        Assert.True(moved);
        Assert.True(host.LastReorderCalled);
        Assert.Equal(new[] { "ch-2", "ch-3", "ch-1" }, host.LastReorderIds);
        Assert.Equal(new[] { "ch-2", "ch-3", "ch-1" }, VisibleOrder(vm));
    }

    [Fact]
    public async Task ReorderChapter_WhenTheWriteFails_KeepsTheVisibleOrderAndSaysSo()
    {
        var (host, vm) = await LoadedAsync();
        host.ReorderResult = false;

        var moved = await vm.ReorderChapterAsync(0, 2);

        Assert.False(moved);
        // AC8: a failed write must not leave the pending order visible.
        Assert.Equal(new[] { "ch-1", "ch-2", "ch-3" }, VisibleOrder(vm));
        Assert.Contains("失败", vm.ViewStatus, StringComparison.Ordinal);
    }

    [Theory]
    [InlineData(-1, 1)]
    [InlineData(0, 3)]
    [InlineData(3, 0)]
    public async Task ReorderChapter_OutOfRange_DoesNotTouchTheHost(int fromIndex, int toIndex)
    {
        var (host, vm) = await LoadedAsync();

        Assert.False(await vm.ReorderChapterAsync(fromIndex, toIndex));
        Assert.False(host.LastReorderCalled);
        Assert.Equal(new[] { "ch-1", "ch-2", "ch-3" }, VisibleOrder(vm));
    }

    [Fact]
    public async Task ReorderChapter_SameIndex_IsANoOpWithoutWireTraffic()
    {
        var (host, vm) = await LoadedAsync();

        Assert.True(await vm.ReorderChapterAsync(1, 1));
        Assert.False(host.LastReorderCalled);
        Assert.Equal(new[] { "ch-1", "ch-2", "ch-3" }, VisibleOrder(vm));
    }

    [Fact]
    public async Task ReorderChapter_ReadOnly_RefusesWithoutWriting()
    {
        var (host, vm) = await LoadedAsync(readOnly: true);

        Assert.False(await vm.ReorderChapterAsync(0, 1));
        Assert.False(host.LastReorderCalled);
        Assert.Contains("只读", vm.ViewStatus, StringComparison.Ordinal);
    }

    [Fact]
    public async Task ReorderChapter_WhileAWriteIsInFlight_RefusesTheSecondDrag()
    {
        var (host, vm) = await LoadedAsync();
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        host.ReorderOverride = (_, _) => gate.Task;

        var first = vm.ReorderChapterAsync(0, 2);
        for (var spin = 0; spin < 200 && !vm.IsReordering; spin++)
        {
            await Task.Delay(5);
        }
        Assert.True(vm.IsReordering);

        // AC9: the second drag must not start a second whole-book rewrite.
        Assert.False(await vm.ReorderChapterAsync(1, 0));
        Assert.Contains("稍后", vm.ViewStatus, StringComparison.Ordinal);
        Assert.Equal(1, host.ReorderCallCount);

        gate.SetResult(true);
        Assert.True(await first);
        Assert.False(vm.IsReordering);
        Assert.Equal(new[] { "ch-2", "ch-3", "ch-1" }, VisibleOrder(vm));
    }
}
