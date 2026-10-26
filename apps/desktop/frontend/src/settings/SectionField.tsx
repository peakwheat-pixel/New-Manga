import type {
  CSSProperties,
  ChangeEventHandler,
  Dispatch,
  FormEventHandler,
  ReactNode,
  SetStateAction,
} from "react";
import { tokens } from "../theme/tokens";

/**
 * SETTINGS-OPEN-A-1 batch A field primitives: one label/control/error row
 * shape shared by the four new panels so the value domains (and their inline
 * validation messages) render identically. Core remains the write authority;
 * these messages are UI affordances only.
 */

/**
 * 令牌主题可切换后，**模块级** `const style = { ...tokens.x }` 会被冻结在
 * import 那一刻的主题（当初是深色）。浅色主题下这些控件仍会是深色底，
 * 与页面其余部分打架——UIUX-V2-RUNTIME-1 的真机自查就抓到了这个问题。
 *
 * 这里把这类常量换成"按当前主题现算"的**访问器属性对象**（不用 Proxy：
 * React 遍历行内样式时会做 ownKeys 一致性检查，Proxy 在某些路径下会抛
 * "'ownKeys' trap returned extra keys but proxy target is non-extensible"）。
 * 键集合由工厂首次求值决定（两套主题的键完全相同），每次读取属性再按当前
 * 主题现算值；调用点零改动（各 panel 仍然 `style={settingsSelectStyle}`）。
 */
function themeStyle(factory: () => CSSProperties): CSSProperties {
  const style: Record<string, unknown> = {};
  for (const key of Object.keys(factory())) {
    Object.defineProperty(style, key, {
      enumerable: true,
      configurable: true,
      get: () => (factory() as Record<string, unknown>)[key],
    });
  }
  return style as CSSProperties;
}

export const settingsInputStyle: CSSProperties = themeStyle(() => ({
  width: "100%",
  maxWidth: 220,
  boxSizing: "border-box",
  padding: "4px 8px",
  fontSize: tokens.typography.size.base,
  border: `1px solid ${tokens.color.border.default}`,
  borderRadius: tokens.radius.button,
  background: tokens.color.surface.card,
  color: tokens.color.text.primary,
}));

export const settingsSelectStyle: CSSProperties = themeStyle(() => ({
  width: "100%",
  maxWidth: 260,
  boxSizing: "border-box",
  padding: "4px 8px",
  fontSize: tokens.typography.size.base,
  border: `1px solid ${tokens.color.border.default}`,
  borderRadius: tokens.radius.button,
  background: tokens.color.surface.card,
  color: tokens.color.text.primary,
}));

/**
 * Twin-handler pattern for free-text / number inputs (same rule already used
 * by ProviderProfilePanel and BookshelfToolbar): the jsdom suites drive value
 * changes through the native value setter + an `input` event, where React's
 * polyfilled onChange does not fire — `onInput` is the reliable path there,
 * `onChange` stays for real WebView input. Both write the same draft field.
 */
export function textFieldHandlers<T extends object>(
  setDraft: Dispatch<SetStateAction<T>>,
  field: keyof T,
): {
  onChange: ChangeEventHandler<HTMLInputElement>;
  onInput: FormEventHandler<HTMLInputElement>;
} {
  const apply = (value: string) =>
    setDraft((previous) => ({ ...previous, [field]: value }) as T);
  return {
    onChange: (event) => apply(event.target.value),
    onInput: (event) => apply(event.currentTarget.value),
  };
}

export function SettingsField({
  id,
  label,
  hint,
  error,
  children,
}: {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "190px minmax(0, 1fr)",
        gap: tokens.spacing.sm,
        alignItems: "start",
      }}
    >
      <label
        htmlFor={id}
        data-testid={`${id}-label`}
        style={{
          paddingTop: 4,
          fontSize: tokens.typography.size.base,
          color: tokens.color.text.primary,
        }}
      >
        {label}
      </label>
      <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {children}
        {hint && (
          <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
            {hint}
          </span>
        )}
        {error && (
          <span
            data-testid={`${id}-error`}
            role="alert"
            style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.state.failed }}
          >
            {error}
          </span>
        )}
      </div>
    </div>
  );
}
