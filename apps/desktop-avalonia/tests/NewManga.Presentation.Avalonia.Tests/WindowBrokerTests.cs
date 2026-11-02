using NewManga.Presentation.Avalonia.Windows;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>FEA-07 window broker: one stable main window, tracked secondary windows (§7.3).</summary>
public sealed class WindowBrokerTests
{
    [Fact]
    public void RegisterMain_IsSingle()
    {
        var broker = new WindowBroker();
        var main = broker.RegisterMain("main");

        Assert.Equal(WindowRole.Main, main.Role);
        Assert.Equal(main, broker.Main);
        Assert.Throws<InvalidOperationException>(() => broker.RegisterMain("second-main"));
    }

    [Fact]
    public void SecondaryBeforeMain_IsRejected()
    {
        var broker = new WindowBroker();
        Assert.Throws<InvalidOperationException>(() => broker.RegisterSecondary(WindowRole.Inspector, "inspector"));
    }

    [Fact]
    public void SecondaryWindows_AreTrackedAndRemoved()
    {
        var broker = new WindowBroker();
        broker.RegisterMain("main");
        broker.RegisterSecondary(WindowRole.Inspector, "inspector");
        broker.RegisterSecondary(WindowRole.Floating, "floating");

        Assert.Equal(2, broker.SecondaryCount);
        Assert.True(broker.Unregister("inspector"));
        Assert.Equal(1, broker.SecondaryCount);
        Assert.False(broker.Unregister("inspector"));
    }

    [Fact]
    public void MainWindow_CannotBeUnregistered()
    {
        var broker = new WindowBroker();
        broker.RegisterMain("main");
        Assert.Throws<InvalidOperationException>(() => broker.Unregister("main"));
    }

    [Fact]
    public void DuplicateToken_IsRejected()
    {
        var broker = new WindowBroker();
        broker.RegisterMain("main");
        broker.RegisterSecondary(WindowRole.Inspector, "inspector");
        Assert.Throws<InvalidOperationException>(() => broker.RegisterSecondary(WindowRole.Floating, "inspector"));
    }

    [Fact]
    public void RegisterSecondary_RequiresNonNullRole()
    {
        var broker = new WindowBroker();
        broker.RegisterMain("main");
        Assert.Throws<ArgumentOutOfRangeException>(() => broker.RegisterSecondary(WindowRole.Main, "x"));
    }
}
