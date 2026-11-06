using System.Text.Json;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Library;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-12-UI L2 evidence: headless UI-level tests for the recycle-bin slice. They drive the real
/// <see cref="TrashViewModel"/> / <see cref="LibraryViewModel"/> against the scriptable trash port and
/// assert the OBSERVABLE contract: frame counts/order, payload closed shapes (digest binding), typed
/// states and per-item reasons. No fake UI data is injected into production types.
/// </summary>
public sealed class TrashUiTests
{
    private static readonly TrashEntry TrashBook0 = new("book-0", "夜光列车", "2026-11-01T10:00:00Z");
    private static readonly TrashEntry TrashBook1 = new("book-1", "雨の停車場", "2026-11-01T09:00:00Z");

    private static (TrashViewModel Trash, FakeHostController Fake, List<string> Notices) NewTrash(
        Action<FakeHostController>? configure = null)
    {
        var fake = new FakeHostController(FakeHostController.ReadySnapshot()) { DefaultTrashEntries = new[] { TrashBook0, TrashBook1 } };
        configure?.Invoke(fake);
        var notices = new List<string>();
        var trash = new TrashViewModel(fake, () => fake.Snapshot.WritesAllowed, (text, _) => notices.Add(text));
        return (trash, fake, notices);
    }

    private static (LibraryViewModel Library, FakeHostController Fake, List<string> Notices) NewLibrary(
        Action<FakeHostController>? configure = null)
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        configure?.Invoke(fake);
        var notices = new List<string>();
        var library = new LibraryViewModel(fake, new ShellState(), (text, _) => notices.Add(text), _ => { });
        return (library, fake, notices);
    }

    private static string[] PayloadKeys(JsonElement payload) =>
        payload.ValueKind == JsonValueKind.Object
            ? payload.EnumerateObject().Select(property => property.Name).ToArray()
            : Array.Empty<string>();

    // ── AC1: single data source, capability-first, one list frame, no total ────────────────

    [Fact]
    public async Task Enter_ProbesOnceThenSendsExactlyOneListFrame_LabelsLoadedCountNotTotal()
    {
        var (trash, fake, _) = NewTrash();

        await trash.EnterAsync();

        Assert.Equal(new[] { TrashWireCommands.CapabilityProbe, TrashWireCommands.ListTrash }, fake.TrashFrames);
        Assert.Equal(1, fake.TrashProbeGolden);
        Assert.Equal(2, trash.Items.Count);
        Assert.Equal("已加载 2 项", trash.LoadedCountText);
        Assert.DoesNotContain("总数", trash.LoadedCountText, StringComparison.Ordinal);
        Assert.Null(fake.TrashListCursors[0]); // first page has no cursor
    }

    [Fact]
    public async Task LoadMore_ReplaysTheOpaqueCursorVerbatim_AndStopsWhenExhausted()
    {
        var (trash, fake, _) = NewTrash();
        fake.ScriptedTrashPages.Enqueue(new TrashListResult(true, null, null, new[] { TrashBook0 }, "cursor-opaque-1"));
        fake.ScriptedTrashPages.Enqueue(new TrashListResult(true, null, null, new[] { TrashBook1 }, null));

        await trash.EnterAsync();
        Assert.True(trash.HasMore);

        await trash.LoadMoreAsync();
        Assert.Equal(new string?[] { null, "cursor-opaque-1" }, fake.TrashListCursors);
        Assert.False(trash.HasMore);
        Assert.Equal(2, trash.Items.Count);
        Assert.Equal("已加载 2 项", trash.LoadedCountText);
    }

    [Fact]
    public async Task ListFailure_IsTypedAndDoesNotRenderAnEmptyRecycleBin()
    {
        var (trash, fake, _) = NewTrash();
        fake.ScriptedTrashPages.Enqueue(TrashListResult.Failure("CORE_UNAVAILABLE", "Core 不可用"));

        await trash.EnterAsync();

        Assert.True(trash.ShowErrorState);
        Assert.False(trash.ShowEmptyState);
        Assert.Empty(trash.Items);
        Assert.Equal("CORE_UNAVAILABLE", trash.ErrorCode);
    }

    [Fact]
    public async Task LateListResponse_AfterExit_IsIsolated()
    {
        var (trash, fake, _) = NewTrash();
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        fake.TrashListGate = gate.Task;
        var entering = trash.EnterAsync();
        await fake.TrashListGateStarted.Task.WaitAsync(TimeSpan.FromSeconds(5));

        trash.Exit();
        gate.SetResult(true);
        await entering;

        Assert.Empty(trash.Items);
        Assert.Equal("已加载 0 项", trash.LoadedCountText);
    }

    [Fact]
    public async Task Exit_ClearsPreviewDigestAndUnderstoodState()
    {
        var (trash, fake, _) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        Assert.True(trash.CanConfirmDelete);

        trash.Exit();
        Assert.False(trash.IsPreviewOpen);
        Assert.Empty(trash.Items);

        await trash.EnterAsync();
        Assert.False(trash.IsPreviewOpen);
        Assert.False(trash.CanConfirmDelete);
        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.ListTrash));
    }

    // ── AC7: capability/read-only/fail-closed ─────────────────────────────────────────────

    [Fact]
    public async Task CapabilityMissing_FailsClosed_WithNoListFrame()
    {
        var (trash, fake, _) = NewTrash();
        fake.TrashCapabilities = new TrashCapabilityState(true, false, false, false, TrashErrorCodes.CapabilityMissing, "缺 library.trash.read/1");

        await trash.EnterAsync();

        Assert.True(trash.IsCapabilityMissing);
        Assert.Equal(new[] { TrashWireCommands.CapabilityProbe }, fake.TrashFrames);
        Assert.Empty(trash.Items);
        Assert.False(trash.CanWrite);
    }

    [Fact]
    public async Task OldCoreWithoutCapabilityList_IsTreatedAsMissing_NotAsComplete()
    {
        var (trash, fake, _) = NewTrash();
        // Old Core that cannot describe capabilities: probe succeeded but READ is not advertised,
        // so it is a capability verdict (not the independent probe-failure state).
        fake.TrashCapabilities = new TrashCapabilityState(
            true, false, false, false, TrashErrorCodes.CapabilityMissing, "Core 未公布能力");

        await trash.EnterAsync();

        Assert.True(trash.IsCapabilityMissing);
        Assert.False(trash.IsProbeFailed);
        Assert.DoesNotContain(TrashWireCommands.ListTrash, fake.TrashFrames);
    }

    [Fact]
    public async Task HostReadOnly_BrowsesButBlocksRestoreAndDelete()
    {
        var (trash, fake, _) = NewTrash(fake =>
        {
            fake.Snapshot = fake.Snapshot with { WritesAllowed = false };
        });

        await trash.EnterAsync();
        trash.Items[0].IsSelected = true;
        await trash.RestoreSelectedAsync();

        // r2 P1: Host read-only is its own state (never derived from a capability) and the typed
        // HOST_READ_ONLY literal is visible; no capability gap is claimed.
        Assert.True(trash.IsHostReadOnly);
        Assert.True(trash.ShowHostReadOnlyBanner);
        Assert.Contains("HOST_READ_ONLY", trash.HostReadOnlyBannerText, StringComparison.Ordinal);
        Assert.False(trash.HasCapabilityGap);
        Assert.False(trash.ShowCapabilityDegraded);
        Assert.False(trash.CanWrite);
        Assert.Contains(TrashWireCommands.ListTrash, fake.TrashFrames);
        Assert.DoesNotContain(TrashWireCommands.RestoreFromTrash, fake.TrashFrames);
    }

    // ── AC4/AC5: disclosure, hard gate, digest binding, fail-closed independent of readiness ─

    [Fact]
    public async Task Preview_DisclosesAllPd01Items_AndCannotConfirmBeforeUnderstood()
    {
        var (trash, _, _) = NewTrash();
        await trash.EnterAsync();

        await trash.BeginPermanentDeleteAsync(trash.Items[0]);

        Assert.True(trash.IsPreviewOpen);
        Assert.Contains("人工修改区域", trash.PreviewProtectionText, StringComparison.Ordinal);
        Assert.Contains("活动草稿页", trash.PreviewProtectionText, StringComparison.Ordinal);
        Assert.Contains("删除文件", trash.PreviewProtectionText, StringComparison.Ordinal);
        Assert.Contains("region 0 个 / artifact 0 个", trash.PreviewCurrentText, StringComparison.Ordinal);
        Assert.Contains("章节", trash.PreviewContentText, StringComparison.Ordinal);
        Assert.False(trash.CanConfirmDelete); // unchecked hard gate

        trash.UnderstandIrrecoverable = true;
        Assert.True(trash.CanConfirmDelete);
    }

    [Fact]
    public async Task OldCoreMissingCurrentSets_FailsClosedEvenAfterUnderstood_NoDeleteFrame()
    {
        var (trash, fake, notices) = NewTrash();
        fake.ScriptedTrashPreviews.Enqueue(FakeHostController.OldCorePreview("book-0"));
        await trash.EnterAsync();

        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        trash.ConfirmDeleteCommand.Execute(null);

        Assert.True(trash.IsPreviewBlocked);
        Assert.Contains("currentRegionRevisionIds", trash.PreviewBlockedReason, StringComparison.Ordinal);
        Assert.False(trash.CanConfirmDelete);
        Assert.DoesNotContain(TrashWireCommands.DeletePermanently, fake.TrashFrames);
        Assert.Contains(notices, notice => notice.Contains("fail-closed", StringComparison.Ordinal));
    }

    [Fact]
    public async Task BusyTarget_IsPreBlocked_NoDeleteFrame()
    {
        var (trash, fake, notices) = NewTrash();
        fake.ScriptedTrashPreviews.Enqueue(FakeHostController.BusyPreview("book-0"));
        await trash.EnterAsync();

        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        trash.ConfirmDeleteCommand.Execute(null);

        Assert.Contains("BOOK_BUSY", trash.PreviewBlockedReason!, StringComparison.Ordinal);
        Assert.False(trash.CanConfirmDelete);
        Assert.DoesNotContain(TrashWireCommands.DeletePermanently, fake.TrashFrames);
        Assert.Contains(notices, notice => notice.Contains("BOOK_BUSY", StringComparison.Ordinal));
    }

    [Fact]
    public async Task Delete_SendsExactlyOneFrame_WithExactlyTheFrozenPayloadKeys()
    {
        var (trash, fake, _) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;

        trash.ConfirmDeleteCommand.Execute(null);

        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.DeletePermanently));
        var deletePayload = fake.TrashFramePayloads[^1];
        Assert.Equal(
            new[] { "book_id", "confirm_permanent_delete", "inventory_digest" },
            PayloadKeys(deletePayload).OrderBy(key => key, StringComparer.Ordinal));
        Assert.Equal("book-0", deletePayload.GetProperty("book_id").GetString());
        Assert.True(deletePayload.GetProperty("confirm_permanent_delete").GetBoolean());
        // r2 P2-2a: the fake now returns DIFFERENT collection vs per-book digests, so this asserts the
        // binding choice (inventoryDigests[bookId]) instead of a value both digests happen to share.
        Assert.Equal("sha256:" + new string('d', 64), deletePayload.GetProperty("inventory_digest").GetString());
        Assert.NotEqual("sha256:" + new string('a', 64), deletePayload.GetProperty("inventory_digest").GetString());
        Assert.DoesNotContain("bookIds", PayloadKeys(deletePayload));
        Assert.DoesNotContain(TrashWireCommands.BatchDeletePermanently, fake.TrashFrames);
        Assert.DoesNotContain(TrashWireCommands.PurgeTrash, fake.TrashFrames);

        // One committed delete removes exactly that row and closes the panel; no fake "still there".
        Assert.Single(trash.Items);
        Assert.False(trash.IsPreviewOpen);
    }

    [Fact]
    public async Task StalePreview_ClearsConfirmation_RePreviewsAndNeverResendsTheDelete()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.Stale, TrashErrorCodes.StalePreview, "stale"));

        trash.ConfirmDeleteCommand.Execute(null);

        Assert.False(trash.UnderstandIrrecoverable);
        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.PreviewPermanentDelete));
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.DeletePermanently));
        Assert.Contains(notices, notice => notice.Contains("BOOK_DELETE_STALE_PREVIEW", StringComparison.Ordinal));
        // The automatic re-preview restored a fresh disclosure panel, still gated by the checkbox.
        Assert.True(trash.IsPreviewOpen);
        Assert.False(trash.CanConfirmDelete);
        Assert.Contains(TrashWireCommands.PreviewPermanentDelete, fake.TrashFrames);
        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.PreviewPermanentDelete));
    }

    [Fact]
    public async Task CleanupPending_RetryUsesTheSameDigest_WithoutANewPreview()
    {
        var (trash, fake, _) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.CleanupPending, TrashErrorCodes.CleanupPending, "pending"));
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(TrashDeleteOutcome.Deleted, null, null));

        trash.ConfirmDeleteCommand.Execute(null);
        Assert.True(trash.IsCleanupPending);
        Assert.True(trash.CanRetryCleanup);

        trash.RetryCleanupCommand.Execute(null);

        var deletes = fake.TrashFramePayloads
            .Where(payload => payload.TryGetProperty("inventory_digest", out _))
            .ToArray();
        Assert.Equal(2, deletes.Length);
        Assert.Equal(
            deletes[0].GetProperty("inventory_digest").GetString(),
            deletes[1].GetProperty("inventory_digest").GetString());
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.PreviewPermanentDelete));
        Assert.Single(trash.Items);
        Assert.Equal("book-1", trash.Items[0].BookId);
        Assert.False(trash.IsPreviewOpen);
    }

    [Fact]
    public async Task BookNotFound_RefreshesTheListInsteadOfLeavingAGhostRow()
    {
        var (trash, fake, _) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.NotFound, TrashErrorCodes.BookNotFound, "gone"));

        trash.ConfirmDeleteCommand.Execute(null);

        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.ListTrash));
        Assert.False(trash.IsPreviewOpen);
        Assert.True(trash.ShowList);
    }

    // ── AC3: restore 1..N with per-item reasons ──────────────────────────────────────────

    [Fact]
    public async Task Restore_SendsTheSelectionInClickOrder_AndReportsPerItemConflicts()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        trash.Items[1].IsSelected = true;
        trash.Items[0].IsSelected = true; // click order: book-1 then book-0
        fake.ScriptedRestores.Enqueue(new TrashWriteResult(
            true, null, null,
            new[] { "book-1" },
            new[] { new TrashItemIssue("book-0", "TRASH_ENTRY_NOT_FOUND", TrashCopy.RestoreReason("TRASH_ENTRY_NOT_FOUND")) }));

        await trash.RestoreSelectedAsync();

        var restorePayload = fake.TrashFramePayloads[^1];
        var entries = restorePayload.GetProperty("entries").EnumerateArray()
            .Select(entry => entry.GetProperty("book_id").GetString()).ToArray();
        Assert.Equal(new[] { "book-1", "book-0" }, entries);
        Assert.Single(trash.Items);
        Assert.Equal("book-0", trash.Items[0].BookId);
        Assert.Contains("不在回收站", trash.Items[0].ConflictReasonText, StringComparison.Ordinal);
        Assert.Contains(notices, notice => notice.Contains("1 项未恢复", StringComparison.Ordinal));
    }

    [Fact]
    public async Task Restore_DoesNotPretendWholeBatchSuccess_WhenNothingRestored()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        trash.Items[0].IsSelected = true;
        fake.ScriptedRestores.Enqueue(new TrashWriteResult(
            false, TrashErrorCodes.TrashEntryNotFound, "all conflicts",
            Array.Empty<string>(),
            new[] { new TrashItemIssue("book-0", "TRASH_ENTRY_NOT_FOUND", TrashCopy.RestoreReason("TRASH_ENTRY_NOT_FOUND")) }));

        await trash.RestoreSelectedAsync();

        Assert.Equal(2, trash.Items.Count);
        Assert.Contains("不在回收站", trash.Items[0].ConflictReasonText, StringComparison.Ordinal);
        Assert.Contains(notices, notice => notice.Contains("未恢复", StringComparison.Ordinal));
    }

    // ── AC10: forbidden flows never leave the UI ─────────────────────────────────────────

    [Fact]
    public async Task FullFlow_NeverEmitsPurgeOrBatchPermanentDeleteFrames()
    {
        var (trash, fake, _) = NewTrash();
        await trash.EnterAsync();
        trash.Items[0].IsSelected = true;
        await trash.RestoreSelectedAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        trash.ConfirmDeleteCommand.Execute(null);
        trash.Exit();

        var allowed = new HashSet<string>(StringComparer.Ordinal)
        {
            TrashWireCommands.CapabilityProbe, TrashWireCommands.ListTrash, TrashWireCommands.MoveToTrash,
            TrashWireCommands.RestoreFromTrash, TrashWireCommands.PreviewPermanentDelete,
            TrashWireCommands.DeletePermanently,
        };
        Assert.All(fake.TrashFrames, frame => Assert.Contains(frame, allowed));
        Assert.DoesNotContain(TrashWireCommands.PurgeTrash, fake.TrashFrames);
        Assert.DoesNotContain(TrashWireCommands.BatchDeletePermanently, fake.TrashFrames);
    }

    [Fact]
    public void Port_HasNoPurgeOrBatchMember_AtAll()
    {
        var methodNames = typeof(ITrashController).GetMethods().Select(method => method.Name).ToArray();
        Assert.DoesNotContain("PurgeTrashAsync", methodNames);
        Assert.DoesNotContain("DeleteBooksPermanentlyAsync", methodNames);
        // The frozen C-07 interface must not have been extended with a trash method either.
        var hostMethodNames = typeof(IHostController).GetMethods().Select(method => method.Name).ToArray();
        Assert.DoesNotContain("ListTrashAsync", hostMethodNames);
        Assert.DoesNotContain("MoveToTrashAsync", hostMethodNames);
    }

    // ── Library integration: shelf move + undo, view-state hiding, copy ──────────────────

    [Fact]
    public async Task EnterRecycleBin_HidesDetailAndBulkBar_AndSendsOneListFrame()
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var state = new ShellState();
        var library = new LibraryViewModel(fake, state, (_, _) => { }, _ => { });
        await library.InitializeAsync();
        await library.SelectBookAsync(library.AllBooks[0]);

        library.ShowRecycleBinCommand.Execute(null);

        Assert.True(library.IsRecycleBinView);
        Assert.False(library.ShowSideDetail);
        Assert.False(library.ShowOverlayDetail);
        Assert.False(library.ShowPageBulkBar);
        Assert.False(state.Selection.HasBook); // Q4: no ghost context behind the hidden detail
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.ListTrash));
        Assert.Equal(2, library.Trash.Items.Count);
    }

    [Fact]
    public async Task MoveToTrash_RequiresDangerConfirm_ThenRefreshesAndShowsUndo()
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var state = new ShellState();
        var notices = new List<string>();
        ConfirmRequest? request = null;
        var library = new LibraryViewModel(fake, state, (text, _) => notices.Add(text), captured => request = captured);
        await library.InitializeAsync();
        await library.SelectBookAsync(library.AllBooks[0]);

        library.MoveToTrashCommand.Execute(null);

        Assert.NotNull(request);
        Assert.True(request!.IsDanger);
        Assert.True(request.CanConfirm);
        Assert.Contains("移入回收站", request.Title, StringComparison.Ordinal);
        Assert.DoesNotContain(TrashWireCommands.MoveToTrash, fake.TrashFrames); // nothing before confirm

        request.OnConfirm();
        // Fake move completes synchronously; the shelf refresh is a real Host read.
        Assert.Contains(TrashWireCommands.MoveToTrash, fake.TrashFrames);
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.MoveToTrash));
        Assert.True(library.UndoBarVisible);
        Assert.False(state.Selection.HasBook);
        // r2 P3-9: the successful soft delete really removed the book from the refreshed shelf.
        Assert.DoesNotContain(library.AllBooks, book => book.BookId == "book-0");
        Assert.Contains(notices, notice => notice.Contains("已移入回收站", StringComparison.Ordinal));
    }

    [Fact]
    public async Task UndoMoveToTrash_RestoresThroughFromTrash_AndClearsTheBar()
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var state = new ShellState();
        var notices = new List<string>();
        ConfirmRequest? request = null;
        var library = new LibraryViewModel(fake, state, (text, _) => notices.Add(text), captured => request = captured);
        await library.InitializeAsync();
        await library.SelectBookAsync(library.AllBooks[0]);
        library.MoveToTrashCommand.Execute(null);
        request!.OnConfirm();

        library.UndoMoveToTrashCommand.Execute(null);

        Assert.Contains(TrashWireCommands.RestoreFromTrash, fake.TrashFrames);
        Assert.False(library.UndoBarVisible);
        Assert.Contains(notices, notice => notice.Contains("撤销", StringComparison.Ordinal));
    }

    [Fact]
    public void PageLevelDeleteCopy_NoLongerClaimsAMissingCommand_ButNamesTheRealScope()
    {
        var fake = V2Fixture.Create();
        var notices = new List<string>();
        var library = new LibraryViewModel(fake, new ShellState(), (text, _) => notices.Add(text), _ => { });

        library.DeleteSelectionCommand.Execute(null);

        Assert.Contains("页面级删除无命令", notices[^1], StringComparison.Ordinal);
        Assert.Contains("作品级", notices[^1], StringComparison.Ordinal);
        Assert.Empty(fake.TrashFrames);
    }
    // ── r2 P1: capability / Host-read-only / probe-failure are three independent states ───────

    [Fact]
    public async Task ReadCapabilityMissing_ShowsTypedGap_FailsClosed_NoReadOnlyBanner()
    {
        var (trash, fake, _) = NewTrash(f =>
            f.TrashCapabilities = new TrashCapabilityState(true, false, true, true,
                TrashErrorCodes.CapabilityMissing, "缺 library.trash.read/1"));

        await trash.EnterAsync();

        Assert.True(trash.ShowCapabilityState);
        Assert.True(trash.IsCapabilityMissing);
        Assert.Contains("CORE_CAPABILITY_MISSING", trash.CapabilityMessage, StringComparison.Ordinal);
        Assert.Contains("library.trash.read/1", trash.CapabilityMessage, StringComparison.Ordinal);
        Assert.DoesNotContain(TrashWireCommands.ListTrash, fake.TrashFrames);
        // r2 P1: a missing READ capability is not a Host read-only state and must not fake its banner.
        Assert.False(trash.IsHostReadOnly);
        Assert.False(trash.ShowHostReadOnlyBanner);
        Assert.False(trash.ShowCapabilityDegraded);
        Assert.False(trash.ShowEmptyState);
    }

    [Fact]
    public async Task WriteCapabilityMissing_ListsForReal_RestoreAndDeleteDisabled_TypedDegraded()
    {
        var (trash, fake, notices) = NewTrash(f =>
            f.TrashCapabilities = new TrashCapabilityState(true, true, false, true,
                TrashErrorCodes.CapabilityMissing, "缺 library.trash.write/1"));

        await trash.EnterAsync();
        trash.Items[0].IsSelected = true;
        await trash.RestoreSelectedAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);

        // Read still works and the list is real (AC7⑤: per-operation gating, not all-or-nothing).
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.ListTrash));
        Assert.Equal(2, trash.Items.Count);
        Assert.True(trash.ShowCapabilityDegraded);
        Assert.Contains("library.trash.write/1", trash.CapabilityGapMessage, StringComparison.Ordinal);
        Assert.Contains("CORE_CAPABILITY_MISSING", trash.CapabilityGapMessage, StringComparison.Ordinal);
        Assert.False(trash.IsHostReadOnly);
        Assert.False(trash.ShowHostReadOnlyBanner);
        Assert.False(trash.CanRestore);
        Assert.DoesNotContain(TrashWireCommands.RestoreFromTrash, fake.TrashFrames);
        Assert.DoesNotContain(TrashWireCommands.PreviewPermanentDelete, fake.TrashFrames);
        Assert.Contains(notices, notice => notice.Contains("CORE_CAPABILITY_MISSING", StringComparison.Ordinal));
    }

    [Fact]
    public async Task PreviewCapabilityMissing_RestoreStillAllowed_DeleteBlocked()
    {
        var (trash, fake, notices) = NewTrash(f =>
            f.TrashCapabilities = new TrashCapabilityState(true, true, true, false,
                TrashErrorCodes.CapabilityMissing, "缺 library.delete.preview/1"));

        await trash.EnterAsync();
        trash.Items[0].IsSelected = true;
        await trash.RestoreSelectedAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);

        // AC7⑤: a missing PREVIEW face must not disable restore (write is available).
        Assert.Contains(TrashWireCommands.RestoreFromTrash, fake.TrashFrames);
        Assert.False(trash.IsCapabilityMissing);
        Assert.True(trash.ShowCapabilityDegraded);
        Assert.Contains("library.delete.preview/1", trash.CapabilityGapMessage, StringComparison.Ordinal);
        Assert.False(trash.IsHostReadOnly);
        Assert.False(trash.ShowHostReadOnlyBanner);
        Assert.DoesNotContain(TrashWireCommands.PreviewPermanentDelete, fake.TrashFrames);
        Assert.DoesNotContain(TrashWireCommands.DeletePermanently, fake.TrashFrames);
        Assert.Contains(notices, notice => notice.Contains("library.delete.preview/1", StringComparison.Ordinal));
    }

    [Fact]
    public async Task ProbeFailure_CoreUnavailable_IsIndependentFailureState_NotCapabilityMissing()
    {
        var (trash, fake, _) = NewTrash(f =>
            f.TrashCapabilities = TrashCapabilityState.Unavailable(TrashErrorCodes.CoreUnavailable, "Core 通道不可用"));

        await trash.EnterAsync();

        Assert.True(trash.IsProbeFailed);
        Assert.True(trash.ShowProbeErrorState);
        Assert.Equal(TrashErrorCodes.CoreUnavailable, trash.ProbeErrorCode);
        Assert.Contains("CORE_UNAVAILABLE", trash.ProbeErrorMessage, StringComparison.Ordinal);
        Assert.False(trash.ShowCapabilityState);
        Assert.False(trash.ShowEmptyState);
        Assert.False(trash.IsHostReadOnly);
        Assert.False(trash.ShowHostReadOnlyBanner);
        Assert.DoesNotContain(TrashWireCommands.ListTrash, fake.TrashFrames);
    }

    // ── r2 P2-1: closing a cleanup-pending result states the truth (retry is lost) ───────────

    [Fact]
    public async Task CloseResult_AfterCleanupPending_SaysRetryIsLost_AndDisablesRetry()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.CleanupPending, TrashErrorCodes.CleanupPending, "pending"));
        trash.ConfirmDeleteCommand.Execute(null);
        Assert.True(trash.CanRetryCleanup);

        trash.CloseResultCommand.Execute(null);

        Assert.False(trash.CanRetryCleanup);
        Assert.False(trash.IsCleanupPending);
        Assert.False(trash.IsPreviewOpen);
        Assert.Contains(notices, notice => notice.Contains("无法再重试清理", StringComparison.Ordinal));
    }

    // ── r2 P2-2: discriminating projections (mutations "per-book -> collection digest" and
    // "missing current arrays -> empty/fail-open" now turn red) ────────────────────────────────

    private static System.Text.Json.JsonElement PreviewJson(string extraProtection)
    {
        var json = "{\"inventoryDigest\":\"sha256:" + new string('a', 64) + "\"," +
                   "\"inventoryDigests\":{\"book-0\":\"sha256:" + new string('d', 64) + "\"}," +
                   "\"items\":[{\"bookId\":\"book-0\",\"title\":\"旧 Core 作品\"," +
                   "\"protection\":{\"lockCount\":0,\"currentRevisionId\":null," +
                   "\"pinnedRevisionIds\":[],\"activeRunIds\":[],\"draftPageCount\":0,\"manualRegionCount\":0" +
                   extraProtection + "}," +
                   "\"contentSummary\":{\"chapters\":1,\"pages\":1,\"artifacts\":0,\"deletedFiles\":0,\"deletedBytes\":0}," +
                   "\"sharedFileRefs\":[]}]}";
        return System.Text.Json.JsonDocument.Parse(json).RootElement.Clone();
    }

    [Theory]
    [InlineData("")]
    [InlineData(",\"currentRegionRevisionIds\":null,\"currentArtifactRevisionIds\":null")]
    [InlineData(",\"currentRegionRevisionIds\":\"not-an-array\",\"currentArtifactRevisionIds\":[]")]
    public async Task OldCoreProjection_UnknownCurrentSet_FailsClosed_ZeroDeleteFrames(string extraProtection)
    {
        var (trash, fake, _) = NewTrash();
        fake.TrashPreviewFactory = _ => HostController.ProjectPreviewResponse(PreviewJson(extraProtection));

        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        trash.ConfirmDeleteCommand.Execute(null);

        Assert.True(trash.IsPreviewBlocked);
        Assert.Contains("currentRegionRevisionIds", trash.PreviewBlockedReason, StringComparison.Ordinal);
        Assert.False(trash.CanConfirmDelete);
        Assert.DoesNotContain(TrashWireCommands.DeletePermanently, fake.TrashFrames);
    }

    [Fact]
    public async Task OldCoreProjection_EmptyCurrentArrays_AreKnown_AndAllowExactlyOneDelete()
    {
        var (trash, fake, _) = NewTrash();
        fake.TrashPreviewFactory = _ => HostController.ProjectPreviewResponse(
            PreviewJson(",\"currentRegionRevisionIds\":[],\"currentArtifactRevisionIds\":[]"));

        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        trash.ConfirmDeleteCommand.Execute(null);

        Assert.False(trash.IsPreviewBlocked);
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.DeletePermanently));
        Assert.Equal(
            "sha256:" + new string('d', 64),
            fake.TrashFramePayloads[^1].GetProperty("inventory_digest").GetString());
    }

    [Fact]
    public void TrashWriteProjection_EmptyObject_IsTypedFailure_NotSilentSuccess()
    {
        var empty = HostController.ProjectTrashWriteResult(false, System.Text.Json.JsonDocument.Parse("{}").RootElement);
        Assert.False(empty.Ok);
        Assert.Equal(TrashErrorCodes.Unknown, empty.Code);
        Assert.Contains("moved", empty.Message, StringComparison.Ordinal);

        var skippedOnly = HostController.ProjectTrashWriteResult(false, System.Text.Json.JsonDocument.Parse(
            "{\"moved\":[],\"skipped\":[{\"ref\":{\"book_id\":\"b1\"},\"reason\":\"TRASH_ENTRY_NOT_FOUND\"}]}").RootElement);
        Assert.False(skippedOnly.Ok);
        Assert.Single(skippedOnly.FailedItems);

        var ok = HostController.ProjectTrashWriteResult(false, System.Text.Json.JsonDocument.Parse(
            "{\"moved\":[{\"book_id\":\"b1\"}],\"skipped\":[]}").RootElement);
        Assert.True(ok.Ok);
        Assert.Contains("b1", ok.SucceededIds);
    }

    // ── r2 P3: copy / path-leak / move-refresh assertions ────────────────────────────────────

    [Fact]
    public async Task PreviewText_ContainsNoPathsOrSourceFileNames()
    {
        var (trash, _, _) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);

        foreach (var text in new[]
                 {
                     trash.PreviewTitle, trash.PreviewProtectionText, trash.PreviewCurrentText,
                     trash.PreviewContentText, trash.PreviewSharedRefsText, trash.PreviewDigestShortText,
                 })
        {
            Assert.DoesNotContain(":\\", text, StringComparison.Ordinal);
            Assert.DoesNotContain(":/", text, StringComparison.Ordinal);
            Assert.DoesNotMatch(@"[A-Za-z]:[\\/]|/(Users|home|mnt|tmp|var)/", text);
            Assert.DoesNotContain("%APPDATA%", text, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(".png", text, StringComparison.OrdinalIgnoreCase);
        }
    }

    [Fact]
    public void RestoreReason_UnknownAndNull_UseUnclassifiedConflictWording()
    {
        Assert.Contains("恢复冲突（未分类）", TrashCopy.RestoreReason(null), StringComparison.Ordinal);
        Assert.Contains("恢复冲突（未分类：WEIRD_CODE）", TrashCopy.RestoreReason("WEIRD_CODE"), StringComparison.Ordinal);
    }
}
