using Avalonia;
using Avalonia.Animation;
using Avalonia.Animation.Easings;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using NewManga.App.ViewModels.Fluent;

namespace NewManga.App.Views.Fluent;

/// <summary>Fluent-only inherited configuration: new logical/template children receive current feedback.</summary>
internal sealed class FluentMotionScope : AvaloniaObject
{
    internal sealed record Configuration(MotionTimingProfile? Timings, IFluentMotionClock Clock);
    internal static readonly AttachedProperty<Configuration?> ConfigurationProperty =
        AvaloniaProperty.RegisterAttached<FluentMotionScope, Control, Configuration?>("Configuration", inherits: true);

    static FluentMotionScope() => ConfigurationProperty.Changed.AddClassHandler<Control>((control, _) =>
        Apply(control, control.GetValue(ConfigurationProperty)));

    internal static void Apply(Control control, Configuration? configuration)
    {
        if (configuration is null) return;
        var timings = configuration.Timings;
        // Template RepeatButtons (Slider tracks) own their visual-state updates; applying the
        // outer button tween here can freeze a template binding at its previous token colour.
        if (control is Button button && button is not RepeatButton)
        {
            button.Transitions = timings?.FeedbackHoverMilliseconds > 0
                ? new Transitions { new BrushTransition
                {
                    Property = TemplatedControl.BackgroundProperty,
                    Duration = TimeSpan.FromMilliseconds(timings.FeedbackHoverMilliseconds),
                    Easing = new SplineEasing(0.4, 0, 0.2, 1),
                } }
                : null;
            FluentFeedbackMotion.Configure(button, timings?.FeedbackPressedMilliseconds ?? 0, configuration.Clock);
        }
        else if (control.Classes.Contains("fluent-feedback-badge"))
            FluentFeedbackMotion.Configure(control, timings?.FeedbackBadgeMilliseconds ?? 0, configuration.Clock, badge: true);
    }
}
