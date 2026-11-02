using Avalonia.Automation;
using Avalonia.Automation.Peers;
using Avalonia.Automation.Provider;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-4 (disabled command zero-trigger cell): a disabled Fluent button must not invoke
/// its action through the automation Invoke pattern, and a command that reports CanExecute=false must not
/// fire. This is the headless-verifiable half of the "disabled ⇒ command zero-trigger" assertion.
/// </summary>
public sealed class FluentDisabledAutomationTests
{
    [AvaloniaFact]
    public void DisabledFluentButton_DoesNotInvokeThroughAutomation_AndCommandStaysUnexecuted()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var clicks = 0;
        var commandRuns = 0;
        var canExecute = false;
        var button = new Button
        {
            Content = "主操作",
            Classes = { "fluent-primary" },
            IsEnabled = false,
            Command = new TestCommand(() => canExecute, () => commandRuns++),
        };
        button.Click += (_, _) => clicks++;

        var window = new Window { Width = 320, Height = 160, Content = button };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.False(button.IsEffectivelyEnabled);
        Assert.False(button.Command!.CanExecute(null));

        var peer = new ButtonAutomationPeer(button);
        var invoke = Assert.IsAssignableFrom<IInvokeProvider>(peer);
        Assert.Throws<ElementNotEnabledException>(() => invoke.Invoke());
        Assert.Equal(0, clicks);
        Assert.Equal(0, commandRuns);

        window.Close();
    }

    private sealed class TestCommand(Func<bool> canExecute, Action execute) : System.Windows.Input.ICommand
    {
        public event EventHandler? CanExecuteChanged { add { } remove { } }

        public bool CanExecute(object? parameter) => canExecute();

        public void Execute(object? parameter) => execute();
    }
}
