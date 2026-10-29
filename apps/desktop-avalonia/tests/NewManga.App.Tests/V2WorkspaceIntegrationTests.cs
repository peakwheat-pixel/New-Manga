using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Shell;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-INT-0 / B-1 review item 2: the contract §6.1 workspace seam. Proves that the shell deactivates
/// the outgoing workspace and activates the incoming one on space/mode switches, that an active
/// workspace gets first refusal on keys (R-17 Tab/Esc/…), and that unregistered spaces render honest
/// placeholder copy instead of fake content.
/// </summary>
public sealed class V2WorkspaceIntegrationTests
{
    private sealed class RecordingWorkspace : IWorkspaceView
    {
        private Control? _content;

        public RecordingWorkspace(SpaceId space) => Space = space;

        public SpaceId Space { get; }

        public int Activations { get; private set; }

        public int Deactivations { get; private set; }

        public bool HandlesTab { get; set; }

        public ShellSelection? LastSelection { get; private set; }

        public Control CreateContent() => _content ??= new Canvas();

        public void OnActivated(ShellState state)
        {
            Activations++;
            LastSelection = state.Selection;
        }

        public void OnDeactivated(ShellState state) => Deactivations++;

        public bool TryHandleKey(KeyEventArgs e, ShellState state) => HandlesTab && e.Key == Key.Tab;
    }

    [AvaloniaFact]
    public void ShellState_RegistersAndUnregistersWorkspaces_AndExposesThem()
    {
        var state = new ShellState();
        var library = new RecordingWorkspace(SpaceId.Library);
        var console = new RecordingWorkspace(SpaceId.Console);

        Assert.True(state.RegisterWorkspace(library));
        Assert.True(state.RegisterWorkspace(console));
        Assert.False(state.RegisterWorkspace(library)); // duplicate slot refused
        Assert.True(state.IsWorkspaceRegistered(SpaceId.Library));
        Assert.False(state.IsWorkspaceRegistered(SpaceId.Studio));
        Assert.Equal(SpaceId.Library, state.GetWorkspace(SpaceId.Library)!.Space);
        Assert.Equal(2, state.Workspaces.Count);

        Assert.True(state.UnregisterWorkspace(SpaceId.Console));
        Assert.False(state.IsWorkspaceRegistered(SpaceId.Console));
        Assert.False(state.UnregisterWorkspace(SpaceId.Console));
    }

    [AvaloniaFact]
    public void SwitchSpace_AndSetStudioMode_CallDeactivateThenActivateHooks()
    {
        var shell = new AppShellViewModel(new FakeHostController(FakeHostController.ReadySnapshot("夜光列车")));
        var library = new RecordingWorkspace(SpaceId.Library);
        var studio = new RecordingWorkspace(SpaceId.Studio);
        Assert.True(shell.RegisterWorkspace(library));
        Assert.True(shell.RegisterWorkspace(studio));

        // Registration activates the workspace whose space is already current (Library at startup).
        Assert.Equal(1, library.Activations);
        Assert.Equal(0, library.Deactivations);

        shell.SwitchSpace(SpaceId.Studio);
        Assert.Equal(1, library.Deactivations);
        Assert.Equal(1, studio.Activations);

        shell.SetStudioMode(StudioMode.Batch);
        Assert.Equal(2, studio.Activations);
        Assert.Equal(1, studio.Deactivations);
        Assert.Equal(StudioMode.Batch, shell.State.StudioMode);

        shell.SwitchSpace(SpaceId.Library);
        Assert.Equal(2, studio.Deactivations);
        Assert.Equal(2, library.Activations);
    }

    [AvaloniaFact]
    public void ActiveWorkspace_GetsFirstRefusalOnKeys_BeforeTheShellKeyMap()
    {
        var shell = new AppShellViewModel(new FakeHostController(FakeHostController.ReadySnapshot("夜光列车")));
        var studio = new RecordingWorkspace(SpaceId.Studio) { HandlesTab = true };
        Assert.True(shell.RegisterWorkspace(studio));
        shell.SwitchSpace(SpaceId.Studio);
        Assert.Equal(StudioMode.Page, shell.State.StudioMode);

        // Workspace accepts Tab → shell must not toggle the Studio mode.
        Assert.True(shell.HandleKey(Key.Tab, KeyModifiers.None, isTextInputFocused: false));
        Assert.Equal(StudioMode.Page, shell.State.StudioMode);

        // Workspace declines → the shell KeyMap now handles Tab and toggles the mode.
        studio.HandlesTab = false;
        Assert.True(shell.HandleKey(Key.Tab, KeyModifiers.None, isTextInputFocused: false));
        Assert.Equal(StudioMode.Batch, shell.State.StudioMode);
    }

    [AvaloniaFact]
    public void UnregisteredWorkspaces_ShowHonestPlaceholderCopy_AndNoContent()
    {
        var shell = new AppShellViewModel(new FakeHostController(FakeHostController.ReadySnapshot("夜光列车")));
        Assert.False(shell.IsStudioWorkspaceRegistered);
        Assert.False(shell.IsConsoleWorkspaceRegistered);
        Assert.Null(shell.StudioWorkspaceContent);

        shell.SwitchSpace(SpaceId.Studio);
        Assert.True(shell.IsStudioPlaceholderVisible);
        Assert.Contains("尚未注册", shell.StudioPlaceholderDetail, StringComparison.Ordinal);

        shell.SwitchSpace(SpaceId.Console);
        Assert.True(shell.IsConsolePlaceholderVisible);
        Assert.Contains("尚未注册", shell.ConsolePlaceholderDetail, StringComparison.Ordinal);

        // Registering the workspace mid-session swaps the placeholder for the real content and activates it.
        var studio = new RecordingWorkspace(SpaceId.Studio);
        Assert.True(shell.RegisterWorkspace(studio));
        Assert.True(shell.IsStudioWorkspaceRegistered);
        Assert.NotNull(shell.StudioWorkspaceContent);
        Assert.False(shell.IsStudioPlaceholderVisible);
    }
}
