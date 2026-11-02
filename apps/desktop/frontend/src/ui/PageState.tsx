import type { ReactNode } from "react";
import { Icon, type IconName } from "../components/Icon";
import { StatusMark, type StatusState } from "../components/StatusMark";
import "./ui.css";

/**
 * v2 页面级状态面（加载 / 空 / 错误 / 阻塞）。
 *
 * 硬规则：状态永远是「颜色 + 符号 + 文字」三重编码，符号来自 StatusMark 的
 * 固定七态字形，不使用 emoji；错误面必须显示可复制的错误码，否则用户与
 * 支持方无法区分「Core 不可用」和「参数非法」。
 *
 * 这组组件是四页共用的唯一状态表达，页面不得自绘第二套。
 */

export interface PageLoadingProps {
  label?: string;
  detail?: string;
  /** 骨架块数量；0 表示不画骨架（用于已知高度的列表）。 */
  skeletonRows?: number;
  testId?: string;
}

export function PageLoading({
  label = "正在加载",
  detail,
  skeletonRows = 3,
  testId = "page-loading",
}: PageLoadingProps) {
  return (
    <div className="nm-state" data-testid={testId} role="status" aria-live="polite">
      <StatusMark state="running" />
      <p className="nm-state__title">{label}</p>
      {detail ? <p className="nm-state__detail">{detail}</p> : null}
      {skeletonRows > 0 ? (
        <div className="nm-state__skeleton" aria-hidden="true">
          {Array.from({ length: skeletonRows }, (_, index) => (
            <span key={index} className="nm-state__skeleton-row" />
          ))}
        </div>
      ) : null}
    </div>
  );
}

export interface PageEmptyProps {
  title: string;
  description?: string;
  icon?: IconName;
  /** 空态是"还没开始"还是"筛选后无结果"，决定状态符号。 */
  kind?: "empty" | "filtered";
  action?: ReactNode;
  testId?: string;
}

export function PageEmpty({
  title,
  description,
  icon = "book",
  kind = "empty",
  action,
  testId = "page-empty",
}: PageEmptyProps) {
  const state: StatusState = kind === "filtered" ? "skipped" : "notStarted";
  return (
    <div className="nm-state" data-testid={testId} role="status">
      <span className="nm-state__icon" aria-hidden="true">
        <Icon name={icon} size={22} />
      </span>
      <StatusMark state={state} />
      <p className="nm-state__title">{title}</p>
      {description ? <p className="nm-state__detail">{description}</p> : null}
      {action ? <div className="nm-state__actions">{action}</div> : null}
    </div>
  );
}

export interface PageErrorProps {
  title: string;
  message?: string;
  code?: string;
  retryable?: boolean;
  onRetry?: () => void;
  retryLabel?: string;
  testId?: string;
}

export function PageError({
  title,
  message,
  code,
  retryable = false,
  onRetry,
  retryLabel = "重试",
  testId = "page-error",
}: PageErrorProps) {
  return (
    <div className="nm-state nm-state--error" data-testid={testId} role="alert">
      <StatusMark state="failed" />
      <p className="nm-state__title">{title}</p>
      {message ? <p className="nm-state__detail">{message}</p> : null}
      {code ? (
        <p className="nm-state__code nm-data" data-testid="page-error-code">
          错误代码：{code}
        </p>
      ) : null}
      {retryable && onRetry ? (
        <div className="nm-state__actions">
          <button type="button" className="nm-btn" onClick={onRetry} data-testid="page-error-retry">
            <Icon name="refresh" size={14} />
            {retryLabel}
          </button>
        </div>
      ) : null}
    </div>
  );
}

export interface PageBlockedProps {
  title: string;
  message?: string;
  detail?: string;
  testId?: string;
}

/**
 * 阻塞面：这不是错误，而是「前置条件未满足，功能按设计不可用」。
 * 与错误面分开，是因为二者的用户可行动作不同（重试 vs 去设置页补前置）。
 */
export function PageBlocked({
  title,
  message,
  detail,
  testId = "page-blocked",
}: PageBlockedProps) {
  return (
    <div className="nm-state nm-state--blocked" data-testid={testId} role="status">
      <StatusMark state="blocked" />
      <p className="nm-state__title">{title}</p>
      {message ? <p className="nm-state__detail">{message}</p> : null}
      {detail ? <p className="nm-state__code nm-data">{detail}</p> : null}
    </div>
  );
}
