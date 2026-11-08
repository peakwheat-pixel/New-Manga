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

    /// <summary>
    /// FEA-12-UI-RESIDUAL-2: drains command-triggered async work deterministically (the restore command is
    /// fire-and-forget by design). Never returns silently: a missed condition fails the test.
    /// </summary>
    private static async Task WaitUntilAsync(Func<bool> condition, string because, int timeoutMs = 5000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (DateTime.UtcNow < deadline)
        {
            if (condition())
            {
                return;
            }

            await Task.Delay(10);
        }

        Assert.True(condition(), because + "（等待超时）");
    }

    /// <summary>Records every raised <see cref="System.ComponentModel.INotifyPropertyChanged"/> name.</summary>
    private static List<string> TrackPropertyChanges(NewManga.App.Shell.V2.ObservableObject source)
    {
        var names = new List<string>();
        source.PropertyChanged += (_, args) =>
        {
            if (!string.IsNullOrEmpty(args.PropertyName))
            {
                names.Add(args.PropertyName);
            }
        };
        return names;
    }

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

    // ── FEA-12-UI-RESIDUAL-1: P3 residual edges (defensive invariant / refresh / cleanup retry /
    //    two independent causes) ────────────────────────────────────────────────────────────────

    /// <summary>
    /// AC-R1 / I-1 (defensive invariant only): a delete-time <c>CORE_CAPABILITY_MISSING</c> result is
    /// NOT a page-level READ capability verdict. The already-loaded list must stay real and the result
    /// panel must carry the typed code; no new probe, no success notice, no extra frame. The branch is
    /// production-unreachable today (the Host does not gate <c>library_delete_book_permanently</c>);
    /// this test pins the invariant, it does not claim a fixed user-visible defect.
    /// </summary>
    [Fact]
    public async Task Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        Assert.True(trash.CanConfirmDelete);
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.CapabilityMissing, TrashErrorCodes.CapabilityMissing, "delete is not advertised"));

        trash.ConfirmDeleteCommand.Execute(null);

        // Exactly the one confirm frame; the list stays real and the page-level READ state is untouched.
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.DeletePermanently));
        Assert.Equal(1, fake.TrashProbeGolden); // no re-probe
        Assert.Equal(2, trash.Items.Count);
        Assert.True(trash.ShowList);
        Assert.False(trash.IsCapabilityMissing);
        Assert.False(trash.ShowCapabilityState);
        Assert.True(trash.CanWrite);   // capability booleans unchanged (no inference)
        Assert.True(trash.CanPreview);
        Assert.False(trash.HasCapabilityGap);
        // Typed result stays visible; the same preview can never be confirmed again.
        Assert.Equal("CORE_CAPABILITY_MISSING", trash.DeleteOutcomeCode);
        Assert.Equal("删除被拒绝", trash.DeleteResultTitle);
        Assert.Contains("CORE_CAPABILITY_MISSING", trash.DeleteOutcomeText, StringComparison.Ordinal);
        Assert.Contains("未删除任何内容", trash.DeleteOutcomeText, StringComparison.Ordinal);
        Assert.True(trash.IsPreviewOpen);
        Assert.False(trash.CanConfirmDelete);
        Assert.False(trash.IsCleanupPending);
        Assert.DoesNotContain(notices, notice =>
            notice.Contains("已彻底删除", StringComparison.Ordinal) ||
            notice.Contains("清理重试成功", StringComparison.Ordinal));
    }

    /// <summary>
    /// AC-R2 / I-2: a preview-time <c>BOOK_NOT_FOUND</c> (the row is gone, no longer returned by the
    /// list) must notify, close the disclosure panel and reload exactly once: two list frames (initial
    /// + refresh), zero delete frames, a second probe from the reload, and no ghost row.
    /// </summary>
    [Fact]
    public async Task Preview_BookNotFound_ClosesPanel_AndReloadsTheList()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        Assert.Equal(2, trash.Items.Count);
        // The refreshed page no longer contains book-0 (the ghost row).
        fake.ScriptedTrashPages.Enqueue(new TrashListResult(true, null, null, new[] { TrashBook1 }, null));
        fake.ScriptedTrashPreviews.Enqueue(TrashPreviewResult.Failure(TrashErrorCodes.BookNotFound, "gone"));

        await trash.BeginPermanentDeleteAsync(trash.Items[0]);

        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.ListTrash));
        Assert.Equal(2, fake.TrashProbeGolden); // initial probe + ReloadAsync probe
        Assert.Equal(0, fake.TrashFrames.Count(frame => frame == TrashWireCommands.DeletePermanently));
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.PreviewPermanentDelete));
        Assert.Single(trash.Items);
        Assert.Equal("book-1", trash.Items[0].BookId);
        Assert.True(trash.ShowList);
        Assert.False(trash.IsPreviewOpen);
        Assert.False(trash.HasPreviewError);
        Assert.Contains(notices, notice =>
            notice.Contains("BOOK_NOT_FOUND", StringComparison.Ordinal) &&
            notice.Contains("已刷新", StringComparison.Ordinal));
    }

    /// <summary>
    /// AC-R3 / I-3: preview → cleanup-pending → retry → retry → <c>BOOK_NOT_FOUND</c>. All three
    /// delete frames carry the FIRST per-book digest byte-for-byte, there is only one preview frame,
    /// and the not-found notice actually reaches the user (the old implementation set result text that
    /// <c>ResetPreview</c> then cleared, so it was invisible), while the list is reloaded.
    /// </summary>
    [Fact]
    public async Task CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest()
    {
        var (trash, fake, notices) = NewTrash();
        await trash.EnterAsync();
        await trash.BeginPermanentDeleteAsync(trash.Items[0]);
        trash.UnderstandIrrecoverable = true;
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.CleanupPending, TrashErrorCodes.CleanupPending, "pending"));
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.CleanupPending, TrashErrorCodes.CleanupPending, "still pending"));
        fake.ScriptedTrashDeletes.Enqueue(new TrashDeleteResult(
            TrashDeleteOutcome.NotFound, TrashErrorCodes.BookNotFound, "gone"));

        trash.ConfirmDeleteCommand.Execute(null);
        Assert.True(trash.CanRetryCleanup);
        trash.RetryCleanupCommand.Execute(null);
        Assert.True(trash.CanRetryCleanup);
        trash.RetryCleanupCommand.Execute(null);

        var digestPayloads = fake.TrashFramePayloads
            .Where(payload => payload.TryGetProperty("inventory_digest", out _))
            .ToArray();
        Assert.Equal(3, digestPayloads.Length);
        var firstDigest = digestPayloads[0].GetProperty("inventory_digest").GetString();
        Assert.False(string.IsNullOrEmpty(firstDigest));
        Assert.Equal(firstDigest, digestPayloads[1].GetProperty("inventory_digest").GetString());
        Assert.Equal(firstDigest, digestPayloads[2].GetProperty("inventory_digest").GetString());
        Assert.Equal(1, fake.TrashFrames.Count(frame => frame == TrashWireCommands.PreviewPermanentDelete));
        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.ListTrash));
        Assert.Contains(notices, notice =>
            notice.Contains("BOOK_NOT_FOUND", StringComparison.Ordinal) &&
            notice.Contains("已不存在", StringComparison.Ordinal));
        Assert.False(trash.IsCleanupPending);
        Assert.False(trash.CanRetryCleanup);
        Assert.False(trash.IsPreviewOpen);
        Assert.DoesNotContain(notices, notice =>
            notice.Contains("清理重试成功", StringComparison.Ordinal) ||
            notice.Contains("已彻底删除", StringComparison.Ordinal));
    }

    /// <summary>
    /// AC-R4 / I-4 (a): Host read-only and a write/preview capability gap are two INDEPENDENT causes.
    /// Both banners are visible and neither text impersonates the other's typed code.
    /// </summary>
    [Fact]
    public async Task HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses()
    {
        var (trash, fake, _) = NewTrash(f =>
        {
            f.TrashCapabilities = new TrashCapabilityState(true, true, false, true,
                TrashErrorCodes.CapabilityMissing, "缺 library.trash.write/1");
            f.Snapshot = f.Snapshot with { WritesAllowed = false };
        });

        await trash.EnterAsync();

        Assert.True(trash.IsHostReadOnly);
        Assert.True(trash.ShowHostReadOnlyBanner);
        Assert.True(trash.ShowCapabilityDegraded);
        Assert.True(trash.ShowList);
        Assert.Equal(2, trash.Items.Count);
        Assert.False(trash.CanWrite);
        Assert.Contains(TrashWireCommands.ListTrash, fake.TrashFrames); // the list is real
        Assert.Contains("HOST_READ_ONLY", trash.HostReadOnlyBannerText, StringComparison.Ordinal);
        Assert.DoesNotContain("CORE_CAPABILITY_MISSING", trash.HostReadOnlyBannerText, StringComparison.Ordinal);
        Assert.Contains("CORE_CAPABILITY_MISSING", trash.CapabilityGapMessage, StringComparison.Ordinal);
        Assert.Contains("library.trash.write/1", trash.CapabilityGapMessage, StringComparison.Ordinal);
        Assert.DoesNotContain("HOST_READ_ONLY", trash.CapabilityGapMessage, StringComparison.Ordinal);
    }

    /// <summary>
    /// AC-R4 / I-4 (b): Host read-only + READ capability missing. The capability state replaces the
    /// list, and the REAL read-only reason is still shown independently — but its copy must not claim
    /// the recycle bin is browsable while reading is provably unavailable.
    /// </summary>
    [Fact]
    public async Task HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason()
    {
        var (trash, _, _) = NewTrash(f =>
        {
            f.TrashCapabilities = new TrashCapabilityState(true, false, true, true,
                TrashErrorCodes.CapabilityMissing, "缺 library.trash.read/1");
            f.Snapshot = f.Snapshot with { WritesAllowed = false };
        });

        await trash.EnterAsync();

        Assert.True(trash.ShowCapabilityState);
        Assert.True(trash.IsCapabilityMissing);
        Assert.True(trash.ShowHostReadOnlyBanner);
        Assert.Contains("HOST_READ_ONLY", trash.HostReadOnlyBannerText, StringComparison.Ordinal);
        Assert.DoesNotContain("可浏览", trash.HostReadOnlyBannerText, StringComparison.Ordinal);
        Assert.Contains("library.trash.read/1", trash.CapabilityMessage, StringComparison.Ordinal);
        Assert.Contains("CORE_CAPABILITY_MISSING", trash.CapabilityMessage, StringComparison.Ordinal);
        Assert.DoesNotContain("HOST_READ_ONLY", trash.CapabilityMessage, StringComparison.Ordinal);
        Assert.False(trash.ShowList);
        Assert.False(trash.ShowEmptyState);
    }

    // ── FEA-12-UI-RESIDUAL-2: A (restore → shelf), B (empty state / cursor honesty), A′ (bar copy) ──

    /// <summary>
    /// AC-R1 / I-1 (defect A): the REAL entry chain — shelf → 回收站 → select → the restore button's
    /// own <c>Trash.RestoreCommand</c> → back to the shelf. The restored book must reappear in the shelf
    /// ViewModel (<c>Books</c> / <c>AllBooks</c> / <c>BookCountText</c>), not merely in the fake's snapshot:
    /// a frame-count-only (or Snapshot.Books-only) assertion stays green even when the shelf never re-reads
    /// the Core. The default-OFF fake repopulate switch is turned on AND the snapshot is pre-seeded
    /// WITHOUT the book, so the assertion can only pass through a real shelf refresh.
    /// </summary>
    [Fact]
    public async Task RestoreFromRecycleBin_ThroughTheRealCommands_ReputsTheBookOnTheShelf()
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        fake.RestoreRepopulatesSnapshot = true;
        // Pre-seed BEFORE any recovery trigger: book-0 already sits in the recycle bin, so the startup
        // snapshot does not list it (the shelf must learn about it from the post-restore refresh).
        fake.Snapshot = fake.Snapshot with
        {
            Books = fake.Snapshot.Books.Where(book => book.BookId != "book-0").ToArray(),
        };
        var library = new LibraryViewModel(fake, new ShellState(), (_, _) => { }, _ => { });

        await library.InitializeAsync();
        Assert.DoesNotContain(library.AllBooks, book => book.BookId == "book-0");
        Assert.Equal(0, fake.RefreshCalls);
        Assert.Equal("3 / 3 作品", library.BookCountText);

        library.ShowRecycleBinCommand.Execute(null);
        await WaitUntilAsync(() => library.Trash.Items.Count == 2, "回收站首帧未加载");
        Assert.True(library.IsRecycleBinView);

        library.Trash.Items.First(row => row.BookId == "book-0").IsSelected = true;
        Assert.True(library.Trash.CanRestore);

        library.Trash.RestoreCommand.Execute(null); // the real 恢复 button binding
        await WaitUntilAsync(
            () => fake.RefreshCalls == 1 && library.Trash.Items.Count == 1,
            "恢复成功后书架未刷新，或回收站行未移除");
        Assert.DoesNotContain(library.Trash.Items, row => row.BookId == "book-0");

        library.CloseRecycleBinCommand.Execute(null);

        Assert.False(library.IsRecycleBinView);
        Assert.Contains(library.Books, book => book.BookId == "book-0");
        Assert.Contains(library.AllBooks, book => book.BookId == "book-0");
        Assert.Equal(4, library.Books.Count);
        Assert.Equal(4, library.AllBooks.Count);
        Assert.Equal("4 / 4 作品", library.BookCountText);
        Assert.DoesNotContain("回收站", library.BookCountText, StringComparison.Ordinal);
    }

    /// <summary>
    /// AC-R2 / I-1 (defect A boundary): only a restore with at least one succeeded item refreshes the
    /// shelf. A full failure must not re-read (RefreshCalls unchanged), must not claim success and must
    /// keep the rows with their per-item reasons; a partial success refreshes exactly once and keeps BOTH
    /// numbers in the status copy.
    /// </summary>
    [Fact]
    public async Task RestoreFailureBoundary_OnlySuccessRefreshes_AndBothCountsStayHonest()
    {
        // (a) ALL FAILED: no shelf read, no success claim, rows retained with reasons.
        var failing = V2Fixture.Create();
        failing.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var failNotices = new List<(string Text, NmStatus Status)>();
        var failLibrary = new LibraryViewModel(
            failing, new ShellState(), (text, status) => failNotices.Add((text, status)), _ => { });
        await failLibrary.InitializeAsync();
        failLibrary.ShowRecycleBinCommand.Execute(null);
        await WaitUntilAsync(() => failLibrary.Trash.Items.Count == 2, "回收站首帧未加载");
        failLibrary.Trash.Items[0].IsSelected = true;
        failLibrary.Trash.Items[1].IsSelected = true;
        failing.ScriptedRestores.Enqueue(new TrashWriteResult(
            false,
            TrashErrorCodes.TrashEntryNotFound,
            "all conflicts",
            Array.Empty<string>(),
            new[]
            {
                new TrashItemIssue("book-0", "TRASH_ENTRY_NOT_FOUND", TrashCopy.RestoreReason("TRASH_ENTRY_NOT_FOUND")),
                new TrashItemIssue("book-1", "TRASH_ENTRY_NOT_FOUND", TrashCopy.RestoreReason("TRASH_ENTRY_NOT_FOUND")),
            }));

        failLibrary.Trash.RestoreCommand.Execute(null);
        await WaitUntilAsync(() => failLibrary.Trash.HasStatus, "全失败恢复未结束");

        Assert.Equal(0, failing.RefreshCalls); // full failure never refreshes the shelf
        Assert.Equal(2, failLibrary.Trash.Items.Count); // rows are retained
        Assert.All(failLibrary.Trash.Items, row => Assert.True(row.HasConflict));
        Assert.StartsWith("已恢复 0 项", failLibrary.Trash.StatusMessage, StringComparison.Ordinal);
        Assert.Contains("2 项未恢复", failLibrary.Trash.StatusMessage, StringComparison.Ordinal);
        Assert.DoesNotContain(failNotices, notice => notice.Status == NmStatus.Done);
        Assert.Contains(failNotices, notice =>
            notice.Status == NmStatus.Failed && notice.Text.Contains("未恢复", StringComparison.Ordinal));

        // (b) PARTIAL: one restored + one conflict → exactly one shelf read, both numbers present.
        var partial = V2Fixture.Create();
        partial.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var partialLibrary = new LibraryViewModel(partial, new ShellState(), (_, _) => { }, _ => { });
        await partialLibrary.InitializeAsync();
        partialLibrary.ShowRecycleBinCommand.Execute(null);
        await WaitUntilAsync(() => partialLibrary.Trash.Items.Count == 2, "回收站首帧未加载");
        partialLibrary.Trash.Items[0].IsSelected = true;
        partialLibrary.Trash.Items[1].IsSelected = true;
        partial.ScriptedRestores.Enqueue(new TrashWriteResult(
            false,
            TrashErrorCodes.TrashEntryNotFound,
            "partial",
            new[] { "book-1" },
            new[]
            {
                new TrashItemIssue("book-0", "TRASH_ENTRY_NOT_FOUND", TrashCopy.RestoreReason("TRASH_ENTRY_NOT_FOUND")),
            }));

        partialLibrary.Trash.RestoreCommand.Execute(null);
        await WaitUntilAsync(() => partial.RefreshCalls == 1, "部分成功后书架未刷新");

        Assert.Equal(1, partial.RefreshCalls); // partial success refreshes exactly once
        Assert.Single(partialLibrary.Trash.Items);
        Assert.Equal("book-0", partialLibrary.Trash.Items[0].BookId);
        Assert.Contains("已恢复 1 项", partialLibrary.Trash.StatusMessage, StringComparison.Ordinal);
        Assert.Contains("1 项未恢复", partialLibrary.Trash.StatusMessage, StringComparison.Ordinal);
    }

    /// <summary>
    /// AC-R3 / AC-R4 (defect B, RESTORE path): page 1 carries an opaque cursor. Restoring every loaded
    /// row empties the page but does NOT empty the recycle bin — the list container (which owns the
    /// 加载更多 button) must stay visible and LoadMore must replay the very same cursor as a second frame.
    /// </summary>
    [Fact]
    public async Task RestoreEmptyingTheFirstPage_KeepsTheListAndTheCursorHonest()
    {
        var (trash, fake, _) = NewTrash();
        fake.DefaultTrashCursor = "cursor-opaque-1";

        await trash.EnterAsync();
        Assert.Equal(2, trash.Items.Count);
        Assert.True(trash.HasMore);

        // The second page is queued only now: the scripted queue feeds the NEXT list call (LoadMore).
        fake.ScriptedTrashPages.Enqueue(new TrashListResult(
            true, null, null, new[] { new TrashEntry("book-2", "汉江之夜", "2026-10-30T10:00:00Z") }, null));

        trash.Items[0].IsSelected = true;
        trash.Items[1].IsSelected = true;
        await trash.RestoreSelectedAsync();

        Assert.Empty(trash.Items);
        Assert.True(trash.HasMore);
        Assert.False(trash.IsEmpty);
        Assert.False(trash.ShowEmptyState);
        Assert.True(trash.ShowList);
        Assert.False(trash.HasError);

        await trash.LoadMoreAsync();

        Assert.Equal(new string?[] { null, "cursor-opaque-1" }, fake.TrashListCursors);
        Assert.Single(trash.Items);
        Assert.Equal("book-2", trash.Items[0].BookId);
        Assert.False(trash.HasMore);
    }

    /// <summary>
    /// AC-R4 (defect B, PERMANENT-DELETE path): the same two-page script, but the rows leave one by one
    /// through the single-book permanent-delete flow (<c>ConfirmDeleteCommand</c> → <c>RemoveDeletedRow</c>).
    /// Emptying the first page must not pretend the recycle bin is empty there either.
    /// </summary>
    [Fact]
    public async Task PermanentDeleteEmptyingTheFirstPage_KeepsTheListAndTheCursorHonest()
    {
        var (trash, fake, _) = NewTrash();
        fake.DefaultTrashCursor = "cursor-opaque-1";

        await trash.EnterAsync();
        Assert.Equal(2, trash.Items.Count);
        Assert.True(trash.HasMore);
        Assert.True(trash.ShowList);

        // The second page is queued only now: the scripted queue feeds the NEXT list call (LoadMore).
        fake.ScriptedTrashPages.Enqueue(new TrashListResult(
            true, null, null, new[] { new TrashEntry("book-2", "汉江之夜", "2026-10-30T10:00:00Z") }, null));

        foreach (var bookId in new[] { "book-0", "book-1" })
        {
            await trash.BeginPermanentDeleteAsync(trash.Items.Single(row => row.BookId == bookId));
            trash.UnderstandIrrecoverable = true;
            Assert.True(trash.CanConfirmDelete);
            trash.ConfirmDeleteCommand.Execute(null);
            await WaitUntilAsync(
                () => trash.Items.All(row => row.BookId != bookId),
                "彻底删除未移除该行");
        }

        Assert.Empty(trash.Items);
        Assert.True(trash.HasMore);
        Assert.False(trash.IsEmpty);
        Assert.False(trash.ShowEmptyState);
        Assert.True(trash.ShowList);
        Assert.Equal(2, fake.TrashFrames.Count(frame => frame == TrashWireCommands.DeletePermanently));

        await trash.LoadMoreAsync();

        Assert.Equal(new string?[] { null, "cursor-opaque-1" }, fake.TrashListCursors);
        Assert.Single(trash.Items);
        Assert.Equal("book-2", trash.Items[0].BookId);
        Assert.False(trash.HasMore);
    }

    /// <summary>
    /// AC-R3: the empty state is honest ONLY with "0 rows AND no cursor"; the capability-missing and
    /// probe-failure states keep their short-circuit order (they own the surface, never the empty state).
    /// </summary>
    [Fact]
    public async Task EmptyStateIsHonestOnlyWhenThereIsNeitherRowNorCursor()
    {
        // (a) 0 rows + no cursor → the empty state is real.
        var (emptyTrash, _, _) = NewTrash(fake => fake.DefaultTrashEntries = Array.Empty<TrashEntry>());
        await emptyTrash.EnterAsync();
        Assert.True(emptyTrash.IsEmpty);
        Assert.True(emptyTrash.ShowEmptyState);
        Assert.False(emptyTrash.ShowList);
        Assert.False(emptyTrash.HasMore);

        // (b) READ capability missing → typed capability state; no list, no empty state (regression fence).
        var (capabilityTrash, _, _) = NewTrash(fake => fake.TrashCapabilities = new TrashCapabilityState(
            true, false, false, false, TrashErrorCodes.CapabilityMissing, "缺 library.trash.read/1"));
        await capabilityTrash.EnterAsync();
        Assert.True(capabilityTrash.ShowCapabilityState);
        Assert.False(capabilityTrash.ShowList);
        Assert.False(capabilityTrash.ShowEmptyState);
        Assert.False(capabilityTrash.IsEmpty);

        // (c) probe failed → independent failure state; no list, no empty state (regression fence).
        var (probeTrash, _, _) = NewTrash(fake => fake.TrashCapabilities =
            TrashCapabilityState.Unavailable(TrashErrorCodes.CoreUnavailable, "Core 通道不可用"));
        await probeTrash.EnterAsync();
        Assert.True(probeTrash.IsProbeFailed);
        Assert.False(probeTrash.ShowList);
        Assert.False(probeTrash.ShowEmptyState);
        Assert.False(probeTrash.IsEmpty);
    }

    /// <summary>
    /// AC-R6 (A′): the resident library bar copy follows the recycle-bin view in BOTH directions. Entering
    /// shows 回收站 (with a PropertyChanged on both bar properties); leaving restores "N / M 作品" whose
    /// numbers match the refreshed Books/AllBooks. The shell-level Esc path is covered in V2ShellUiTests.
    /// </summary>
    [Fact]
    public async Task BookCountText_FollowsTheRecycleBinView_BothWays()
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var library = new LibraryViewModel(fake, new ShellState(), (_, _) => { }, _ => { });
        await library.InitializeAsync();
        var changes = TrackPropertyChanges(library);
        Assert.Equal("4 / 4 作品", library.BookCountText);

        library.ShowRecycleBinCommand.Execute(null);

        Assert.Equal("回收站", library.BookCountText);
        Assert.Contains(nameof(LibraryViewModel.BookCountText), changes);
        Assert.Contains(nameof(LibraryViewModel.ListStatusText), changes);
        await WaitUntilAsync(() => library.Trash.Items.Count == 2, "回收站首帧未加载");

        changes.Clear();
        library.CloseRecycleBinCommand.Execute(null);

        Assert.False(library.IsRecycleBinView);
        Assert.Equal($"{library.Books.Count} / {library.AllBooks.Count} 作品", library.BookCountText);
        Assert.Equal("4 / 4 作品", library.BookCountText);
        Assert.Contains(nameof(LibraryViewModel.BookCountText), changes);
        Assert.DoesNotContain("回收站", library.BookCountText, StringComparison.Ordinal);
    }

    /// <summary>
    /// AC-R1 + AC-R6 interlock (A′ regression fence): the post-restore refresh happens WHILE the recycle
    /// bin is open — the exact sequence that used to freeze the resident bar on 回收站 after returning to
    /// the shelf. The bar must never keep the recycle-bin copy once the shelf is back.
    /// </summary>
    [Fact]
    public async Task ReturningToTheShelfAfterAnInRecycleBinRefresh_NeverLeavesTheRecycleBinCopy()
    {
        var fake = V2Fixture.Create();
        fake.DefaultTrashEntries = new[] { TrashBook0, TrashBook1 };
        var library = new LibraryViewModel(fake, new ShellState(), (_, _) => { }, _ => { });
        await library.InitializeAsync();
        library.ShowRecycleBinCommand.Execute(null);
        await WaitUntilAsync(() => library.Trash.Items.Count == 2, "回收站首帧未加载");

        library.Trash.Items[0].IsSelected = true;
        library.Trash.RestoreCommand.Execute(null);
        await WaitUntilAsync(() => fake.RefreshCalls == 1, "回收站内的书架刷新未发生");

        // The shelf refresh ran inside the recycle bin: the resident bar must say 回收站 right now.
        Assert.Equal("回收站", library.BookCountText);

        var changes = TrackPropertyChanges(library);
        library.CloseRecycleBinCommand.Execute(null);

        // The bar is bound to PropertyChanged, not re-read on demand: leaving MUST re-raise the property.
        Assert.Contains(nameof(LibraryViewModel.BookCountText), changes);
        Assert.Equal($"{library.Books.Count} / {library.AllBooks.Count} 作品", library.BookCountText);
        Assert.Equal("4 / 4 作品", library.BookCountText);
        Assert.DoesNotContain("回收站", library.BookCountText, StringComparison.Ordinal);
        Assert.DoesNotContain("回收站", library.ListStatusText, StringComparison.Ordinal);
    }
}
