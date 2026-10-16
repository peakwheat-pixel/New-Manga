/**
 * jsdom event helpers for the mounted-component suites.
 *
 * React 18 tracks controlled inputs by overriding the node's `value`
 * property: a plain `el.value = x` assignment goes through React's tracker,
 * which then sees "no change" and silently drops the dispatched input
 * event. Setting the value through the NATIVE prototype descriptor (the
 * same trick @testing-library's fireEvent.change uses) leaves the tracker
 * stale, so React recognizes the change and fires onChange.
 */

type WindowLike = {
  HTMLInputElement?: typeof HTMLInputElement;
  HTMLTextAreaElement?: typeof HTMLTextAreaElement;
  HTMLSelectElement?: typeof HTMLSelectElement;
  Event: typeof Event;
};

function nativeValueDescriptor(win: WindowLike, el: HTMLElement): PropertyDescriptor | undefined {
  if (el instanceof (win.HTMLInputElement ?? HTMLInputElement)) {
    return Object.getOwnPropertyDescriptor(win.HTMLInputElement?.prototype ?? HTMLInputElement.prototype, "value");
  }
  if (el instanceof (win.HTMLTextAreaElement ?? HTMLTextAreaElement)) {
    return Object.getOwnPropertyDescriptor(win.HTMLTextAreaElement?.prototype ?? HTMLTextAreaElement.prototype, "value");
  }
  if (el instanceof (win.HTMLSelectElement ?? HTMLSelectElement)) {
    return Object.getOwnPropertyDescriptor(win.HTMLSelectElement?.prototype ?? HTMLSelectElement.prototype, "value");
  }
  return undefined;
}

/** Set a text input/textarea value and notify React.
 *
 * React's ChangeEventPlugin (the onChange polyfill for text inputs) listens
 * for the "change" top-level event on the delegated root, and its value
 * tracker must see a delta — so the value is set through the NATIVE
 * prototype descriptor (bypassing the tracker's instance setter) and BOTH
 * "input" and "change" events are dispatched. The plain "input"-only form
 * silently no-ops under jsdom (observed in this repo's suites; the
 * workbench search input works around it by also binding onInput). */
export function setNativeInputValue(win: WindowLike, el: HTMLInputElement | HTMLTextAreaElement, value: string) {
  const descriptor = nativeValueDescriptor(win, el);
  if (descriptor?.set) {
    descriptor.set.call(el, value);
  } else {
    el.value = value;
  }
  el.dispatchEvent(new (win.Event ?? Event)("input", { bubbles: true }));
  el.dispatchEvent(new (win.Event ?? Event)("change", { bubbles: true }));
}

/** Set a select value and notify React (change event). */
export function setNativeSelectValue(win: WindowLike, el: HTMLSelectElement, value: string) {
  const descriptor = Object.getOwnPropertyDescriptor(
    win.HTMLSelectElement?.prototype ?? HTMLSelectElement.prototype,
    "value",
  );
  if (descriptor?.set) {
    descriptor.set.call(el, value);
  } else {
    el.value = value;
  }
  el.dispatchEvent(new (win.Event ?? Event)("change", { bubbles: true }));
}
