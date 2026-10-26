import { useState } from "react";
import type { PipelineCommand } from "./client";
import { DisabledFeature } from "./DisabledFeature";

const commands: { value: PipelineCommand; label: string }[] = [
  { value: "translate_all", label: "全章翻译" },
  { value: "translate_untranslated", label: "翻译未完成页" },
  { value: "translate_selected", label: "翻译选择页" },
  { value: "translate_single", label: "翻译当前页" },
  { value: "rerender_all", label: "重渲染全章" },
  { value: "rerender_selected", label: "重渲染选择页" },
  { value: "rerender_single", label: "重渲染当前页" },
  { value: "reinpaint_all", label: "重修复全章" },
  { value: "reinpaint_selected", label: "重修复选择页" },
  { value: "reinpaint_single", label: "重修复当前页" },
  { value: "reocr_all", label: "重新 OCR 全章" },
  { value: "reocr_selected", label: "重新 OCR 选择页" },
  { value: "reocr_single", label: "重新 OCR 当前页" },
  { value: "ocr_region", label: "OCR 当前 Region" },
  { value: "retranslate_region", label: "重翻译当前 Region" },
  { value: "retranslate_region_full", label: "重翻译当前 Region（全流程）" },
  { value: "reinpaint_region", label: "重修复当前 Region" },
  { value: "rerender_region", label: "重渲染当前 Region" },
];

export interface WorkbenchToolbarProps {
  contextInfo: string;
  regionCount: number;
  hasChapter: boolean;
  selectedPageCount: number;
  hasPage: boolean;
  hasRegion: boolean;
  runBusy: boolean;
  viewerMode: "view" | "pan" | "region";
  onStartRun: (command: PipelineCommand) => void;
  onOpenImport: () => void;
  onOpenExport: () => void;
  onSetViewerMode: (mode: "view" | "pan" | "region") => void;
}

export function WorkbenchToolbar({
  contextInfo, regionCount, hasChapter, selectedPageCount, hasPage, hasRegion, runBusy, viewerMode,
  onStartRun, onOpenImport, onOpenExport, onSetViewerMode,
}: WorkbenchToolbarProps) {
  const [command, setCommand] = useState<PipelineCommand>("translate_all");
  const needsPages = command.endsWith("_selected");
  const needsPage = command.endsWith("_single");
  const needsRegion = command.endsWith("_region") || command === "ocr_region" || command.startsWith("retranslate_region");
  const canStart = hasChapter && (!needsPages || selectedPageCount > 0) && (!needsPage || hasPage) && (!needsRegion || hasRegion);

  return (
    <section
      data-testid="workbench-toolbar"
      aria-label="工作台工具栏"
      style={{
        flex: "0 0 44px", minHeight: 44, display: "flex", alignItems: "center", gap: 8,
        borderBottom: "1px solid #d9d9d6", padding: "0 12px", background: "#f7f7f5", color: "#1f2328",
        overflowX: "auto", whiteSpace: "nowrap",
      }}
    >
      <strong data-testid="toolbar-context" style={{ fontSize: 12 }}>{contextInfo}</strong>
      <span data-testid="toolbar-region-count" style={{ fontSize: 11, color: "#6b7280" }}>Region：{regionCount}</span>
      <label style={{ display: "inline-flex", gap: 4, alignItems: "center", fontSize: 11 }}>
        批处理
        <select data-testid="run-command-select" value={command} onChange={(event) => setCommand(event.target.value as PipelineCommand)}>
          {commands.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
        </select>
      </label>
      <button data-testid="start-run" type="button" disabled={!canStart || runBusy} onClick={() => onStartRun(command)}>
        {runBusy ? "提交中…" : "启动"}
      </button>
      <button data-testid="workbench-import" type="button" disabled={!hasChapter} onClick={onOpenImport}>导入页面</button>
      <button data-testid="workbench-export" type="button" disabled={!hasChapter || selectedPageCount === 0} onClick={onOpenExport}>导出选择页</button>
      <label style={{ display: "inline-flex", gap: 4, alignItems: "center", fontSize: 11 }}>
        查看模式
        <select data-testid="viewer-mode" value={viewerMode} onChange={(event) => onSetViewerMode(event.target.value as "view" | "pan" | "region")}>
          <option value="view">查看</option><option value="pan">平移</option><option value="region">Region 选择</option>
        </select>
      </label>
      <DisabledFeature id="gap-g10-create-region" label="新建 Region" reason="等待 CreateRegion 能力接入。" />
      <DisabledFeature id="gap-g10-delete-region" label="删除 Region" reason="等待 DeleteRegion 能力接入。" />
      <DisabledFeature id="gap-g11-region-geometry" label="编辑 Region 几何" reason="移动、缩放、合并、拆分与顺序写入 wire 尚未冻结。" />
      <DisabledFeature id="gap-g16-core-availability" label="Core 状态" reason="Core 可用性查询/事件 wire 尚未冻结；此处不推断运行状态。" />
      <DisabledFeature id="gap-g26-import-progress" label="逐页导入进度" reason="当前只返回同步导入结果，细分进度 snapshot 尚未冻结。" />
    </section>
  );
}
