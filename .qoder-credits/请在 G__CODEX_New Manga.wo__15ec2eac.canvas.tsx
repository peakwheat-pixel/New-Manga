import {
  BarChart,
  Callout,
  ChartComparisonGrid,
  ChartContainer,
  H1,
  LineChart,
  MetricsGrid,
  PieChart,
  ReportSection,
  ReportShell,
  Stack,
  Table,
  Text,
  type MetricItem,
} from "qoder/canvas";

// —— 报告数据契约（由 scripts/lib/breakdown.mjs 产出，plugin 注入）——
interface CatRow {
  key: string;
  label: string;
  tokens: number;
  share: number;
}
interface ToolRow {
  tool: string;
  tokens: number;
  calls: number;
  /** 平均每次调用带来的重发 token；无调用记录时 null（不给 0） */
  perCall?: number | null;
  share: number;
}
interface FileRow {
  attr: string;
  label: string;
  kind: string;
  tool: string | null;
  selfTokens: number;
  reads: number;
  trips: number;
  billed: number;
  /** 单次读取的总代价（含此后每一程重发）；reads=0 时 null */
  perRead?: number | null;
  share: number;
}
interface ReqRow {
  index: number;
  time: string | null;
  ratio: number;
  inputTokens: number;
  /** 代理或转录任一有真值即非 null；两者都没则 null（不写 0） */
  outputTokens?: number | null;
  /** proxy=代理实测 / transcript-tokens=转录 input_tokens / transcript-ratio=转录 ratio×window */
  usageSource?: "proxy" | "transcript-tokens" | "transcript-ratio" | "transcript";
  credits: number;
  originalCredits: number;
  afterCompact: boolean;
}
interface CatChild {
  tool: string | null;
  label: string;
  kind: string | null;
  tokens: number;
  share: number;
  catShare: number;
  trips: number;
}
interface CatDetail {
  key: string;
  label: string;
  tokens: number;
  share: number;
  children: CatChild[];
}
interface SubagentRow {
  agentId: string;
  agentType: string | null;
  description: string | null;
  toolUseId: string | null;
  roundTrips: number;
  billedInputTokens: number;
  peakContextRatio: number;
  credits: number;
  originalCredits: number;
  error: string | null;
}
interface SubagentTotals {
  roundTrips: number;
  billedInputTokens: number;
  credits: number;
  originalCredits: number;
}
interface Subagents {
  scanned: boolean;
  dir: string | null;
  /** 试过的候选目录；用于区分「真没子代理」与「路径没找对」。 */
  probedPaths?: string[];
  /** ok=已汇总 / no-dir=无子代理目录 / dir-empty=目录在但无 agent 文件 / no-usage=有文件但转录无 usage / error=读取抛错 */
  reason?: string;
  count: number;
  items: SubagentRow[];
  totals: SubagentTotals;
  combined: SubagentTotals;
}
/** 逐项可用性：报告里每个数字到底是模型上报的真值、按真值推导、回退默认、手工录入，还是本地根本没有。
 *  v2 旧报告没这个对象，故全部字段可选，读取时一律走默认值（旧报告只可能来自桌面端富转录）。 */
type Avail = "measured" | "derived" | "fallback" | "manual" | "unavailable";
interface Availability {
  credits?: Avail;
  roundTrips?: Avail;
  contextRatio?: Avail;
  tokens?: Avail;
  /** 输出 token：代理或转录 output_tokens 任一有真值即 measured */
  outputTokens?: Avail;
  /** 缓存命中 token：代理或转录 cache_read_input_tokens 任一有真值即 measured */
  cachedTokens?: Avail;
  categoryShare?: Avail;
  toolShare?: Avail;
  fileShare?: Avail;
  systemPrompt?: Avail;
  contextWindow?: Avail;
  compactions?: Avail;
  compactionCost?: Avail;
  model?: Avail;
  title?: Avail;
  toolCalls?: Avail;
  fileReads?: Avail;
  userTurns?: Avail;
  /** 用户压缩阈值：manual 覆盖 → manual；默认 200K → fallback */
  userContextLimit?: Avail;
}
/** 官方 UI 真值（手工录入，来自 .qoder-credits/overrides/<sessionId>.json）。
 *  IDE 端转录不含 usage，本地算不出 Credits，这是唯一的真值通道；绝不覆盖 totals，只并列展示。 */
interface ManualTruth {
  file?: string;
  credits: number | null;
  originalCredits: number | null;
  model: string | null;
  startedAt: string | null;
  endedAt: string | null;
  durationMin: number | null;
  note: string | null;
  /** 手工锁定模型窗口（如 qwen3-max=1000000），优先于 runtime-config / 反推 / fallback */
  contextWindow?: number | null;
  /** 手工指定 Qoder 压缩触发阈值（默认 200000），驱动 peakUserAdvice */
  userContextLimit?: number | null;
  /** 本地 credits ÷ 官方真值。有子代理时拿 combined 比（官方 UI 扣费 = 主链 + 子代理），
   *  否则覆盖率会被系统性低估（实测 ca2f7834：主链比 0.46、combined 比 0.89）。 */
  localCoverage?: number | null;
  /** main=只比主链 / combined=比主链+子代理 */
  localScope?: "main" | "combined";
  /** 参与对账的本地 credits（按 localScope 取 totals.credits 或 subagents.combined.credits） */
  localCredits?: number | null;
}
/** 峰值占比的「该不该压」结论。阈值算在数据层（breakdown.mjs peakAdvice），
 *  这里只管展示——否则 Canvas 与终端各持一套阈值迟早走偏。tone 直接喂 Callout。 */
interface PeakAdvice {
  level: "low" | "mid" | "sweet" | "high" | "over";
  tone: "info" | "success" | "warning" | "danger";
  text: string;
}
/** 一次压缩 = 一笔普通模型调用（整份上下文当 prompt、摘要当 completion），是会话里单笔最贵的开销。
 *  pre/post 是客户端自估口径；proxy 是能在代理日志里唯一对上时回填的供应商实测值，对不上就 null。 */
interface CompactionEvent {
  index: number;
  at: string | null;
  trigger: string | null;
  preTokens: number | null;
  postTokens: number | null;
  messagesSummarized: number | null;
  /** 压缩后首轮的往返序号与实测输入 = 压缩把上下文压到的地板 */
  nextRequestIndex: number | null;
  nextInputTokens: number | null;
  savedTokens: number | null;
  /** 数据层归一后的生效值：有代理实测就用实测，否则是客户端自估。
   *  渲染端直接取这两个，别自己按 proxy 分支——否则会与合计的口径分叉。 */
  effectiveInputTokens?: number | null;
  effectiveOutputTokens?: number | null;
  proxy?: {
    promptTokens: number;
    completionTokens: number;
    cachedTokens: number | null;
    ms: number | null;
    matchedBy: string;
  } | null;
}
interface CompactionCost {
  count: number;
  items: CompactionEvent[];
  /** measured = items 里有几笔拿到了供应商实测（其余为客户端自估） */
  totals: { preTokens: number; postTokens: number; savedTokens: number; measured?: number };
}
/** 链路健康度：代理覆盖率 + 最近记录时间 + 最近若干笔的三方归因计数。
 *  逐笔明细属于排障（CLI --request-log），报告只给一行结论。 */
interface LinkHealth {
  matched: number;
  requests: number;
  coverage: number;
  /** proxy / transcript-tokens / transcript-ratio / mixed / transcript（v3 旧报告）/ null */
  usageSource?: "proxy" | "transcript-tokens" | "transcript-ratio" | "mixed" | "transcript" | null;
  /** 三档拆分：代理实测 / 转录 input_tokens / 转录 ratio×window */
  breakdown?: { proxy: number; transcriptTokens: number; transcriptRatio: number };
  logRecords?: number;
  lastRecordAt?: string | null;
  /** 参与归因的最近笔数；0 = 运行中的代理是旧版或还没记到诊断 */
  recentRequests?: number;
  proxyErrors?: number | null;
  upstreamRejected?: number | null;
  aborted?: number | null;
  truncated?: number | null;
  noUsage?: number | null;
  slowestMs?: number | null;
  /** 被更新流量推翻的那条陈旧拉起失败记录；null = 没有 */
  supersededFailure?: { error: string; port?: number; at?: string | null } | null;
}
interface Report {
  schemaVersion: number;
  generatedAt: string;
  pluginVersion?: string;
  /** 转录来自哪一代客户端：桌面端富转录有 usage 真值，IDE 端精简转录没有。v2 旧报告无此字段。 */
  source?: "desktop-rich" | "ide-lite" | "unknown";
  /** usage 数字的来源：proxy=代理实测 / transcript-tokens=转录 input_tokens 真值 /
   *  transcript-ratio=转录 ratio×window 推导 / mixed=多档混合 / transcript=v3 旧报告兼容。无 usage 时 null。 */
  usageSource?: "proxy" | "transcript-tokens" | "transcript-ratio" | "mixed" | "transcript" | null;
  /** 可直接粘贴执行的插件入口命令（generate.mjs 用 proxy.mjs 的 selfCmd() 注入）。
   *  Windows 上是插件自带启动器的绝对路径，不要求用户装 Node；模板是静态文本，拿不到就只能硬编码。 */
  selfCmd?: string | null;
  /** 链路健康度一行结论（逐笔明细留给 CLI --request-log） */
  linkHealth?: LinkHealth | null;
  /** 代理 join 诊断（lib/proxylog.mjs）+ 配置/状态（generate.mjs 注入） */
  proxy?: {
    matched: number;
    requests: number;
    /** 三档拆分：代理实测 / 转录 input_tokens / 转录 ratio×window */
    breakdown?: { proxy: number; transcriptTokens: number; transcriptRatio: number };
    logPath?: string;
    logExists?: boolean;
    logRecords?: number;
    /** config.json 里 upstream 合法 = 用户已配置代理 */
    configured?: boolean;
    enabled?: boolean;
    port?: number;
    /** 最近一条代理记录的时间；null = 从无流量 */
    lastRecordAt?: string | null;
    /** 已配置但长期零流量（多半已改回官方模型）——软提示可 --stop-proxy */
    dormant?: boolean;
    /** 最近一次自动拉起失败（如端口被占）；ok 时为 null */
    status?: { error: string; port?: number; at?: string | null } | null;
    /** status 那条失败记录是否已被更新的流量推翻（代理在它之后还记到了流量）。
     *  status.json 只写不清，陈旧失败会把用户推去改本来正确的 Base URL，故必须判掉。 */
    statusSuperseded?: boolean;
  };
  availability?: Availability;
  manual?: ManualTruth | null;
  session: {
    id: string | null;
    title: string | null;
    /** custom-title / first-user / session-id —— 令产物文件名可解释 */
    titleSource?: string;
    model: string | null;
    /** runtime-config / manual / unavailable */
    modelSource?: string;
    cwd: string | null;
    turns: number;
    roundTrips: number;
    compactions: number;
    startedAt: string | null;
    endedAt: string | null;
  };
  context: {
    contextWindow: number;
    /** runtime-config=实测 / derived-from-usage=从 usage 反推 / manual=ManualTruth 手工锁定 /
     *  fallback=读不到静默回退 200000 / caller=调用方传入（旧枚举，兼容）。
     *  报告里每个 token 数字都要乘它，回退时必须标出来。 */
    contextWindowSource?: string;
    systemPromptTokens: number;
    netContextTokens: number;
    /** 峰值 = 当前窗口口径：自最近一次压缩起算，压缩边界处归零重新累积 */
    peakContextTokens: number;
    peakContextRatio: number;
    /** 本场历史峰值（跨压缩）；整场没压缩过时与上面相等 */
    peakSessionTokens?: number;
    peakSessionRatio?: number;
    /** 历史峰值是否值得单独交代（与当前窗口峰值相差 ≥1 个百分点），渲染端直接取用不再自判 */
    peakSessionNotable?: boolean;
    /** 峰值占比的「该不该压」结论（对模型窗口）；无有效占比时 null */
    peakAdvice?: PeakAdvice | null;
    /** 用户压缩阈值（Qoder 自动触发点），与模型窗口独立。默认 200000，ManualTruth 可覆盖 */
    userContextLimit?: number;
    /** default=内置 200K / manual=overrides 手写 / config=插件配置 / derived=实测反推 */
    userContextLimitSource?: "default" | "manual" | "config" | "derived";
    /** peakContextTokens ÷ userContextLimit */
    peakUserRatio?: number;
    /** 对用户阈值的「快自动压缩了吗」结论；与 peakAdvice 可矛盾（模型窗口未满但用户阈值已超） */
    peakUserAdvice?: PeakAdvice | null;
    /** v3.2 当前占用头条口径：段内单调递增 ⇒ 峰值≡当前，故以 netContextTokens 作头条，peak 退灰字 */
    currentContextTokens?: number;
    netUserRatio?: number;
    netUserAdvice?: PeakAdvice | null;
    netWindowRatio?: number;
    /** v3.2 自动压缩自校准：本场 trigger=auto 的实际触发点（无需外部配置）与「阈值是否被强制」判定 */
    observedAutoCompactions?: number;
    observedAutoTriggerTokens?: number | null;
    autoTriggerRatio?: number | null;
    thresholdNotEnforced?: boolean;
  };
  totals: {
    billedInputTokens: number;
    netContextTokens: number;
    peakContextTokens: number;
    amplification: number;
    attributedTokens: number;
    coverage: number;
    credits: number;
    originalCredits: number;
    /** 输出 token 总量：仅代理路径有真值，否则 0 且 availability.outputTokens=unavailable */
    outputTokens?: number;
    /** 供应商上下文缓存命中的那部分 prompt：仅代理路径有真值 */
    cachedTokens?: number;
    cachedTrips?: number;
    /** 缓存命中 ÷ 计费输入总量（全局实测约 91.5%：重复叠加的前缀正是缓存的命中对象） */
    cachedShare?: number;
    /** 两个不依赖 usage 的计数，IDE 端占比全缺时仍有可展示的真值 */
    toolCalls?: number;
    fileReads?: number;
  };
  /** credits 的分子到底覆盖了多少：与计费输入总量并排展示时，部分覆盖不说就等于把局部真值当全量。 */
  creditsCoverage?: {
    /** 真正累加进 totals.credits 的往返数 */
    trips: number;
    roundTrips: number;
    /** 这些往返的计费输入之和 */
    tokens: number;
    tokenShare: number;
    /** trips === roundTrips：全覆盖时不必再啰嗦覆盖范围 */
    full: boolean;
  };
  /** 压缩单笔成本（此前只显示「压缩 N 次」，而它是会话里单笔最贵的调用） */
  compactionCost?: CompactionCost;
  byCategory: CatRow[];
  byCategoryDetail: CatDetail[];
  byTool: ToolRow[];
  byFile: FileRow[];
  byRequest: ReqRow[];
  subagents?: Subagents;
  identity: { sumAttributed: number; billedInputTokens: number; absDiff: number; ok: boolean | null };
}

// 注入点：下一行的 REPORT 初值会被 render-canvas.mjs 按整行替换为真实报告 JSON。
const REPORT = {"schemaVersion":3.2,"generatedAt":"2026-09-25T10:36:40.519Z","source":"desktop-rich","usageSource":"transcript-ratio","availability":{"credits":"measured","roundTrips":"measured","contextRatio":"measured","tokens":"derived","outputTokens":"unavailable","cachedTokens":"unavailable","categoryShare":"derived","toolShare":"derived","fileShare":"derived","systemPrompt":"derived","contextWindow":"measured","compactions":"measured","compactionCost":"measured","model":"measured","title":"measured","toolCalls":"measured","fileReads":"measured","userTurns":"measured","userContextLimit":"fallback"},"session":{"id":"15ec2eac-3921-4109-9c61-2e4640955956","title":"请在 G:/CODEX/New Manga.wo","titleSource":"first-user","model":"qfmodel","modelSource":"runtime-config","cwd":"G:\\CODEX\\New Manga","turns":2,"roundTrips":77,"compactions":0,"startedAt":"2026-09-25T09:47:44.258Z","endedAt":"2026-09-25T10:35:50.064Z"},"context":{"contextWindow":400000,"contextWindowSource":"runtime-config","systemPromptTokens":52578,"netContextTokens":204629,"peakContextTokens":320058,"peakContextRatio":0.800145,"peakSessionTokens":320058,"peakSessionRatio":0.800145,"peakSessionNotable":false,"peakAdvice":{"level":"sweet","tone":"success","text":"正处性价比区间（65–85%）。此时压一次每轮省得最多，且第一轮就回本"},"userContextLimit":200000,"userContextLimitSource":"default","peakUserRatio":1.60029,"peakUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"currentContextTokens":204629,"netUserRatio":1.023145,"netUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"netWindowRatio":0.5115725,"observedAutoCompactions":0,"observedAutoTriggerTokens":null,"autoTriggerRatio":null,"thresholdNotEnforced":true},"totals":{"billedInputTokens":16962380,"netContextTokens":204629,"peakContextTokens":320058,"amplification":82.89,"attributedTokens":16962380,"coverage":1,"credits":301.715,"originalCredits":301.715,"outputTokens":0,"cachedTokens":0,"cachedTrips":0,"cachedShare":0,"toolCalls":118,"fileReads":57},"creditsCoverage":{"trips":77,"roundTrips":77,"tokens":16962380,"tokenShare":1,"full":true},"compactionCost":{"count":0,"items":[],"totals":{"preTokens":0,"postTokens":0,"savedTokens":0,"measured":0}},"proxy":{"matched":0,"requests":77,"breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":77},"logPath":"C:\\Users\\49745\\.qoder-credits-proxy\\usage.jsonl","logExists":false,"logRecords":0,"configured":false,"enabled":true,"port":49787,"lastRecordAt":null,"dormant":false,"status":null,"statusSuperseded":false},"byCategory":[{"key":"tool_result","label":"工具返回","tokens":9257687,"share":0.5457776100347017},{"key":"system","label":"系统提示词","tokens":4048506,"share":0.23867558679855067},{"key":"assistant_thinking","label":"模型思考","tokens":1139300,"share":0.06716628076658927},{"key":"assistant_tool_use","label":"工具调用","tokens":771936,"share":0.04550871404636285},{"key":"assistant_text","label":"模型回复","tokens":46954,"share":0.0027681160055389774},{"key":"user_input","label":"用户输入","tokens":32567,"share":0.0019199521818208532},{"key":"attachment","label":"附件/技能","tokens":1665430,"share":0.0981837401664375}],"byCategoryDetail":[{"key":"tool_result","label":"工具返回","tokens":9257687,"share":0.5457776100347017,"children":[{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/contracts/UI_UX_GUI_DESIGN.md","kind":"read","tokens":1964711,"share":0.11582755698047276,"catShare":0.21222482353775599,"trips":70},{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":1883852,"share":0.11106061596195108,"catShare":0.20349060481775647,"trips":1965},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/settings/SettingsView.qml","kind":"read","tokens":721552,"share":0.042538377421725934,"catShare":0.07794086206471763,"trips":61},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/reader/ReaderView.qml","kind":"read","tokens":395710,"share":0.023328671855713745,"catShare":0.042743915152969464,"trips":62},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/TaskProgressPanel.qml","kind":"read","tokens":387806,"share":0.02286272807236076,"catShare":0.04189019053183053,"trips":62},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/WorkbenchView.qml","kind":"read","tokens":316285,"share":0.018646284849817726,"catShare":0.03416462036365353,"trips":65},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/RegionOverlay.qml","kind":"read","tokens":315199,"share":0.01858225673269854,"catShare":0.03404730496642587,"trips":63},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/theme/Tokens.qml","kind":"read","tokens":304289,"share":0.017939045017127113,"catShare":0.03286878150971879,"trips":71},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/05_UI_MAPPING.md","kind":"read","tokens":301692,"share":0.017785960791030824,"catShare":0.03258829322423094,"trips":168},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/windows/ExportWindow.qml","kind":"read","tokens":290717,"share":0.017138919240067926,"catShare":0.03140275255882739,"trips":61},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/ChapterPicker.qml","kind":"read","tokens":199356,"share":0.011752809844733586,"catShare":0.02153406374436342,"trips":65},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/PageListPanel.qml","kind":"read","tokens":178582,"share":0.010528100222259657,"catShare":0.019290091840869505,"trips":64},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/RegionInspector.qml","kind":"read","tokens":178326,"share":0.010513054464926787,"catShare":0.019262524280280288,"trips":63},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookDetailPanel.qml","kind":"read","tokens":168058,"share":0.009907681219501483,"catShare":0.01815333028936737,"trips":66},{"tool":"Read","label":"doc/tasks/M2-UI1.md","kind":"read","tokens":166678,"share":0.009826329251714627,"catShare":0.018004273299320302,"trips":76},{"tool":null,"label":"其他 32 项","kind":null,"tokens":1484873,"share":0.0875392181085973,"catShare":0.16039356781790914,"trips":2166}]},{"key":"system","label":"系统提示词","tokens":4048506,"share":0.23867558679855067,"children":[]},{"key":"assistant_thinking","label":"模型思考","tokens":1139300,"share":0.06716628076658927,"children":[]},{"key":"assistant_tool_use","label":"工具调用","tokens":771936,"share":0.04550871404636285,"children":[{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":324052,"share":0.019104186179535167,"catShare":0.4197918262439238,"trips":1965},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md","kind":"write","tokens":200904,"share":0.011844101619104257,"catShare":0.2602600813338267,"trips":17},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/capture_baseline.py","kind":"write","tokens":63636,"share":0.0037516070977673182,"catShare":0.08243711509723828,"trips":260},{"tool":"TaskCreate","label":"（无路径）","kind":"other","tokens":41949,"share":0.0024730706123203806,"catShare":0.054342792674846714,"trips":300},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/tasks/M2-UI1.md","kind":"write","tokens":21176,"share":0.001248410507246362,"catShare":0.027432339792649835,"trips":46},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/handoffs/M2-UI1-8031173.md","kind":"write","tokens":21162,"share":0.0012475906560160308,"catShare":0.02741432453452815,"trips":9},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/05_UI_MAPPING.md","kind":"read","tokens":7295,"share":0.00043007617868376315,"catShare":0.00945041378768943,"trips":168},{"tool":"TaskUpdate","label":"（无路径）","kind":"other","tokens":4036,"share":0.00023796390429743297,"catShare":0.005228974478492247,"trips":274},{"tool":"Grep","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/tests","kind":"search","tokens":3483,"share":0.00020535767989019192,"catShare":0.004512491380903007,"trips":57},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/PrimaryNavigationRail.qml","kind":"read","tokens":2965,"share":0.00017479491344874298,"catShare":0.003840910847770109,"trips":68},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookshelfToolbar.qml","kind":"read","tokens":2917,"share":0.00017195377239578345,"catShare":0.0037784801438379987,"trips":67},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookDetailPanel.qml","kind":"read","tokens":2868,"share":0.00016907305835326775,"catShare":0.0037151798704094657,"trips":66},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/contracts/UI_UX_GUI_DESIGN.md","kind":"read","tokens":2815,"share":0.0001659627342730422,"catShare":0.003646834188809743,"trips":70},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookshelfView.qml","kind":"read","tokens":2800,"share":0.00016507562149995205,"catShare":0.0036273409380844775,"trips":67},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/WorkbenchToolbar.qml","kind":"read","tokens":2770,"share":0.0001632769885586176,"catShare":0.0035878181130821704,"trips":64},{"tool":null,"label":"其他 32 项","kind":null,"tokens":67107,"share":0.003956212522972519,"catShare":0.08693307657390746,"trips":1650}]},{"key":"assistant_text","label":"模型回复","tokens":46954,"share":0.0027681160055389774,"children":[]},{"key":"user_input","label":"用户输入","tokens":32567,"share":0.0019199521818208532,"children":[]},{"key":"attachment","label":"附件/技能","tokens":1665430,"share":0.0981837401664375,"children":[]}],"byTool":[{"tool":"Read","tokens":7284777,"calls":38,"perCall":191705,"share":0.42946669051280034},{"tool":"Bash","tokens":2207905,"calls":50,"perCall":44158,"share":0.13016480214148593},{"tool":"Write","tokens":225366,"calls":4,"perCall":56342,"share":0.013286232293429396},{"tool":"Grep","tokens":149107,"calls":1,"perCall":149107,"share":0.0087904495752996},{"tool":"Edit","tokens":98902,"calls":14,"perCall":7064,"share":0.00583068502987062},{"tool":"TaskCreate","tokens":56839,"calls":4,"perCall":14210,"share":0.0033508580210143417},{"tool":"TaskUpdate","tokens":6727,"calls":7,"perCall":961,"share":0.0003966065071623883}],"byFile":[{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/contracts/UI_UX_GUI_DESIGN.md","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/contracts/UI_UX_GUI_DESIGN.md","kind":"read","tool":"Read","selfTokens":16075,"reads":1,"trips":140,"billed":1967526,"perRead":1967526,"share":0.11599351971474577},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/settings/SettingsView.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/settings/SettingsView.qml","kind":"read","tool":"Read","selfTokens":6909,"reads":1,"trips":122,"billed":724067,"perRead":724067,"share":0.042686659347379},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/reader/ReaderView.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/reader/ReaderView.qml","kind":"read","tool":"Read","selfTokens":3728,"reads":1,"trips":124,"billed":398166,"perRead":398166,"share":0.023473492220809942},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/TaskProgressPanel.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/TaskProgressPanel.qml","kind":"read","tool":"Read","selfTokens":3656,"reads":1,"trips":124,"billed":390476,"perRead":390476,"share":0.02302014151268272},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/WorkbenchView.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/WorkbenchView.qml","kind":"read","tool":"Read","selfTokens":2829,"reads":1,"trips":130,"billed":318992,"perRead":318992,"share":0.01880582525494985},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/RegionOverlay.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/RegionOverlay.qml","kind":"read","tool":"Read","selfTokens":2921,"reads":1,"trips":126,"billed":317811,"perRead":317811,"share":0.01873620017818861},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/05_UI_MAPPING.md","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/05_UI_MAPPING.md","kind":"read","tool":"Read","selfTokens":3273,"reads":3,"trips":336,"billed":308987,"perRead":102996,"share":0.018216036969714598},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/theme/Tokens.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/theme/Tokens.qml","kind":"read","tool":"Read","selfTokens":2474,"reads":1,"trips":142,"billed":306894,"perRead":306894,"share":0.01809262020887586},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/windows/ExportWindow.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/windows/ExportWindow.qml","kind":"read","tool":"Read","selfTokens":2797,"reads":1,"trips":122,"billed":293127,"perRead":293127,"share":0.017281022752152125},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/ChapterPicker.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/ChapterPicker.qml","kind":"read","tool":"Read","selfTokens":1791,"reads":1,"trips":130,"billed":201949,"perRead":201949,"share":0.011905702732985211},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md","kind":"write","tool":"Write","selfTokens":12727,"reads":1,"trips":34,"billed":201411,"perRead":201411,"share":0.011873956778758556},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/PageListPanel.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/PageListPanel.qml","kind":"read","tool":"Read","selfTokens":1636,"reads":1,"trips":128,"billed":181240,"perRead":181240,"share":0.010684846131275929},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/RegionInspector.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/RegionInspector.qml","kind":"read","tool":"Read","selfTokens":1664,"reads":1,"trips":126,"billed":181046,"perRead":181046,"share":0.01067341222064562},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookDetailPanel.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookDetailPanel.qml","kind":"read","tool":"Read","selfTokens":1490,"reads":1,"trips":132,"billed":170926,"perRead":170926,"share":0.01007675427785475},{"attr":"file:G:/CODEX/New Manga/doc/tasks/M2-UI1.md","label":"doc/tasks/M2-UI1.md","kind":"read","tool":"Read","selfTokens":1290,"reads":1,"trips":152,"billed":168507,"perRead":168507,"share":0.009934141641623716},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/design/tokens-cand-f.json","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/design/tokens-cand-f.json","kind":"read","tool":"Read","selfTokens":1245,"reads":1,"trips":140,"billed":152384,"perRead":152384,"share":0.008983634963910329},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookshelfView.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookshelfView.qml","kind":"read","tool":"Read","selfTokens":1290,"reads":1,"trips":134,"billed":150504,"perRead":150504,"share":0.008872814655622424},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/ViewerPanel.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/ViewerPanel.qml","kind":"read","tool":"Read","selfTokens":1351,"reads":1,"trips":128,"billed":149667,"perRead":149667,"share":0.008823488461707696},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/tests","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/tests","kind":"search","tool":"Grep","selfTokens":1541,"reads":1,"trips":114,"billed":149107,"perRead":149107,"share":0.0087904495752996},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/ChapterList.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/ChapterList.qml","kind":"read","tool":"Read","selfTokens":1173,"reads":1,"trips":132,"billed":134561,"perRead":134561,"share":0.00793290789793532},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookCard.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookCard.qml","kind":"read","tool":"Read","selfTokens":1095,"reads":1,"trips":134,"billed":127753,"perRead":127753,"share":0.007531575230935312},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/WorkbenchToolbar.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/WorkbenchToolbar.qml","kind":"read","tool":"Read","selfTokens":953,"reads":1,"trips":128,"billed":105576,"perRead":105576,"share":0.006224118803854497},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/capture_baseline.py","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/capture_baseline.py","kind":"read","tool":"Read","selfTokens":2062,"reads":9,"trips":592,"billed":95539,"perRead":10615,"share":0.00563241609370834},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookshelfToolbar.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookshelfToolbar.qml","kind":"read","tool":"Read","selfTokens":780,"reads":1,"trips":134,"billed":91002,"perRead":91002,"share":0.0053649576987484385},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookGrid.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/bookshelf/BookGrid.qml","kind":"read","tool":"Read","selfTokens":702,"reads":1,"trips":134,"billed":81902,"perRead":81902,"share":0.004828461928873598},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/AppShell.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/AppShell.qml","kind":"read","tool":"Read","selfTokens":526,"reads":1,"trips":136,"billed":62382,"perRead":62382,"share":0.0036776849789615525},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/Main.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/Main.qml","kind":"read","tool":"Read","selfTokens":523,"reads":1,"trips":136,"billed":62026,"perRead":62026,"share":0.0036567095893477023},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/PrimaryNavigationRail.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/PrimaryNavigationRail.qml","kind":"read","tool":"Read","selfTokens":452,"reads":1,"trips":136,"billed":53606,"perRead":53606,"share":0.003160292035153272},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/DirtyConfirmDialog.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/workbench/DirtyConfirmDialog.qml","kind":"read","tool":"Read","selfTokens":340,"reads":1,"trips":126,"billed":36993,"perRead":36993,"share":0.0021808654777761504},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/EmptyState.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/EmptyState.qml","kind":"read","tool":"Read","selfTokens":270,"reads":1,"trips":132,"billed":30973,"perRead":30973,"share":0.0018259890302152904},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/CanvasCaption.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/common/CanvasCaption.qml","kind":"read","tool":"Read","selfTokens":227,"reads":1,"trips":132,"billed":26040,"perRead":26040,"share":0.0015351833698476708},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/tests/ui_shell/helpers.py","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/tests/ui_shell/helpers.py","kind":"read","tool":"Read","selfTokens":274,"reads":1,"trips":108,"billed":24830,"perRead":24830,"share":0.001463815022409963},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/NavBadge.qml","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/src/ui/qml/shell/NavBadge.qml","kind":"read","tool":"Read","selfTokens":196,"reads":1,"trips":136,"billed":23245,"perRead":23245,"share":0.0013703921214381445},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/handoffs/M2-UI1-8031173.md","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/handoffs/M2-UI1-8031173.md","kind":"write","tool":"Write","selfTokens":2677,"reads":2,"trips":34,"billed":22439,"perRead":11219,"share":0.0013228439104831808},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/tasks/M2-UI1.md","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/tasks/M2-UI1.md","kind":"write","tool":"Edit","selfTokens":1613,"reads":4,"trips":92,"billed":22336,"perRead":5584,"share":0.0013167669462927543},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/baseline-6a68fde/screenshots/11-workbench.png","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/baseline-6a68fde/screenshots/11-workbench.png","kind":"read","tool":"Read","selfTokens":229,"reads":2,"trips":110,"billed":7978,"perRead":3989,"share":0.0004703166445914542},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/templates/HANDOFF.md","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/doc/templates/HANDOFF.md","kind":"read","tool":"Read","selfTokens":660,"reads":1,"trips":24,"billed":7403,"perRead":7403,"share":0.0004364492283950643},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/baseline-6a68fde/screenshots/05-chapter-selected.png","label":"G:/CODEX/New Manga.worktrees/M2-UI1-qoder/verification/M2-UI1/baseline-6a68fde/screenshots/05-chapter-selected.png","kind":"read","tool":"Read","selfTokens":118,"reads":1,"trips":60,"billed":4749,"perRead":4749,"share":0.0002799968025729428},{"attr":"file:C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/qt-gui-capture-environment.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/qt-gui-capture-environment.md","kind":"write","tool":"Write","selfTokens":535,"reads":1,"trips":6,"billed":1508,"perRead":1508,"share":0.00008892931076108707},{"attr":"file:C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"read","tool":"Read","selfTokens":888,"reads":2,"trips":6,"billed":1456,"perRead":728,"share":0.00008583339184513364},{"attr":"file:C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/m2ui1-delivery-state.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/m2ui1-delivery-state.md","kind":"write","tool":"Write","selfTokens":378,"reads":1,"trips":6,"billed":1066,"perRead":1066,"share":0.00006283229807045029}],"byAttr":[{"attr":"tool_result|Read","tokens":7196527,"share":0.4242639675150645},{"attr":"system","tokens":4048506,"share":0.23867558679855067},{"attr":"tool_result|Bash","tokens":1883852,"share":0.11106061596195108},{"attr":"attachment","tokens":1665430,"share":0.0981837401664375},{"attr":"assistant_thinking","tokens":1139300,"share":0.06716628076658927},{"attr":"tool_use|Bash","tokens":324052,"share":0.019104186179535167},{"attr":"tool_use|Write","tokens":224477,"share":0.013233812949327255},{"attr":"tool_result|Grep","tokens":145624,"share":0.008585091895409411},{"attr":"tool_use|Read","tokens":88251,"share":0.005202722997735811},{"attr":"tool_use|Edit","tokens":85687,"share":0.005051599723256576},{"attr":"assistant_text","tokens":46954,"share":0.0027681160055389774},{"attr":"tool_use|TaskCreate","tokens":41949,"share":0.0024730706123203806},{"attr":"user_input","tokens":32567,"share":0.0019199521818208532},{"attr":"tool_result|TaskCreate","tokens":14889,"share":0.0008777874086939623},{"attr":"tool_result|Edit","tokens":13215,"share":0.0007790853066140481},{"attr":"tool_use|TaskUpdate","tokens":4036,"share":0.00023796390429743297},{"attr":"tool_use|Grep","tokens":3483,"share":0.00020535767989019192},{"attr":"tool_result|TaskUpdate","tokens":2691,"share":0.00015864260286495497},{"attr":"tool_result|Write","tokens":889,"share":0.00005241934410213988}],"byRequest":[{"index":1,"time":"17:47","ratio":0.15855,"inputTokens":63420,"outputTokens":null,"usageSource":"transcript-ratio","credits":10.781,"originalCredits":10.781,"afterCompact":false},{"index":2,"time":"17:48","ratio":0.16715,"inputTokens":66860,"outputTokens":null,"usageSource":"transcript-ratio","credits":2.079,"originalCredits":2.079,"afterCompact":false},{"index":3,"time":"17:48","ratio":0.17194,"inputTokens":68776,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.517,"originalCredits":1.517,"afterCompact":false},{"index":4,"time":"17:48","ratio":0.185435,"inputTokens":74174,"outputTokens":null,"usageSource":"transcript-ratio","credits":2.072,"originalCredits":2.072,"afterCompact":false},{"index":5,"time":"17:48","ratio":0.18935,"inputTokens":75740,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.395,"originalCredits":1.395,"afterCompact":false},{"index":6,"time":"17:48","ratio":0.19187,"inputTokens":76748,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.454,"originalCredits":1.454,"afterCompact":false},{"index":7,"time":"17:49","ratio":0.212175,"inputTokens":84870,"outputTokens":null,"usageSource":"transcript-ratio","credits":2.697,"originalCredits":2.697,"afterCompact":false},{"index":8,"time":"17:49","ratio":0.309275,"inputTokens":123710,"outputTokens":null,"usageSource":"transcript-ratio","credits":8.034,"originalCredits":8.034,"afterCompact":false},{"index":9,"time":"17:49","ratio":0.312345,"inputTokens":124938,"outputTokens":null,"usageSource":"transcript-ratio","credits":2.187,"originalCredits":2.187,"afterCompact":false},{"index":10,"time":"17:49","ratio":0.32355,"inputTokens":129420,"outputTokens":null,"usageSource":"transcript-ratio","credits":2.588,"originalCredits":2.588,"afterCompact":false},{"index":11,"time":"17:49","ratio":0.34518,"inputTokens":138072,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.346,"originalCredits":3.346,"afterCompact":false},{"index":12,"time":"17:49","ratio":0.362945,"inputTokens":145178,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.141,"originalCredits":3.141,"afterCompact":false},{"index":13,"time":"17:49","ratio":0.38797,"inputTokens":155188,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.835,"originalCredits":3.835,"afterCompact":false},{"index":14,"time":"17:50","ratio":0.40884,"inputTokens":163536,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.609,"originalCredits":3.609,"afterCompact":false},{"index":15,"time":"17:50","ratio":0.435955,"inputTokens":174382,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.087,"originalCredits":4.087,"afterCompact":false},{"index":16,"time":"17:50","ratio":0.475875,"inputTokens":190350,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.083,"originalCredits":5.083,"afterCompact":false},{"index":17,"time":"17:50","ratio":0.521185,"inputTokens":208474,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.924,"originalCredits":5.924,"afterCompact":false},{"index":18,"time":"17:50","ratio":0.535055,"inputTokens":214022,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.957,"originalCredits":3.957,"afterCompact":false},{"index":19,"time":"17:50","ratio":0.53991,"inputTokens":215964,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.513,"originalCredits":3.513,"afterCompact":false},{"index":20,"time":"17:50","ratio":0.551565,"inputTokens":220626,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.815,"originalCredits":3.815,"afterCompact":false},{"index":21,"time":"17:50","ratio":0.56182,"inputTokens":224728,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.816,"originalCredits":3.816,"afterCompact":false},{"index":22,"time":"17:51","ratio":0.56625,"inputTokens":226500,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.58,"originalCredits":3.58,"afterCompact":false},{"index":23,"time":"17:51","ratio":0.58237,"inputTokens":232948,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.807,"originalCredits":4.807,"afterCompact":false},{"index":24,"time":"17:51","ratio":0.597065,"inputTokens":238826,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.223,"originalCredits":4.223,"afterCompact":false},{"index":25,"time":"17:51","ratio":0.603035,"inputTokens":241214,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.005,"originalCredits":4.005,"afterCompact":false},{"index":26,"time":"17:52","ratio":0.609135,"inputTokens":243654,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.427,"originalCredits":4.427,"afterCompact":false},{"index":27,"time":"17:52","ratio":0.62185,"inputTokens":248740,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.639,"originalCredits":4.639,"afterCompact":false},{"index":28,"time":"17:52","ratio":0.626515,"inputTokens":250606,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.794,"originalCredits":3.794,"afterCompact":false},{"index":29,"time":"17:53","ratio":0.631885,"inputTokens":252754,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.999,"originalCredits":3.999,"afterCompact":false},{"index":30,"time":"17:53","ratio":0.656365,"inputTokens":262546,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.733,"originalCredits":5.733,"afterCompact":false},{"index":31,"time":"17:53","ratio":0.66157,"inputTokens":264628,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.067,"originalCredits":4.067,"afterCompact":false},{"index":32,"time":"17:53","ratio":0.665,"inputTokens":266000,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.908,"originalCredits":3.908,"afterCompact":false},{"index":33,"time":"17:53","ratio":0.666925,"inputTokens":266770,"outputTokens":null,"usageSource":"transcript-ratio","credits":3.785,"originalCredits":3.785,"afterCompact":false},{"index":34,"time":"17:53","ratio":0.685475,"inputTokens":274190,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.013,"originalCredits":5.013,"afterCompact":false},{"index":35,"time":"17:54","ratio":0.68841,"inputTokens":275364,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.533,"originalCredits":4.533,"afterCompact":false},{"index":36,"time":"17:54","ratio":0.692875,"inputTokens":277150,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.092,"originalCredits":4.092,"afterCompact":false},{"index":37,"time":"17:54","ratio":0.699085,"inputTokens":279634,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.575,"originalCredits":4.575,"afterCompact":false},{"index":38,"time":"17:55","ratio":0.708945,"inputTokens":283578,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.012,"originalCredits":5.012,"afterCompact":false},{"index":39,"time":"17:55","ratio":0.71433,"inputTokens":285732,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.164,"originalCredits":5.164,"afterCompact":false},{"index":40,"time":"17:56","ratio":0.721865,"inputTokens":288746,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.905,"originalCredits":4.905,"afterCompact":false},{"index":41,"time":"17:56","ratio":0.725705,"inputTokens":290282,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.293,"originalCredits":4.293,"afterCompact":false},{"index":42,"time":"17:56","ratio":0.728895,"inputTokens":291558,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.394,"originalCredits":4.394,"afterCompact":false},{"index":43,"time":"17:57","ratio":0.73109,"inputTokens":292436,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.768,"originalCredits":4.768,"afterCompact":false},{"index":44,"time":"17:57","ratio":0.73759,"inputTokens":295036,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.527,"originalCredits":4.527,"afterCompact":false},{"index":45,"time":"17:57","ratio":0.739055,"inputTokens":295622,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.637,"originalCredits":4.637,"afterCompact":false},{"index":46,"time":"17:57","ratio":0.74334,"inputTokens":297336,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.503,"originalCredits":4.503,"afterCompact":false},{"index":47,"time":"17:58","ratio":0.75138,"inputTokens":300552,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.449,"originalCredits":5.449,"afterCompact":false},{"index":48,"time":"17:58","ratio":0.762345,"inputTokens":304938,"outputTokens":null,"usageSource":"transcript-ratio","credits":44.851,"originalCredits":44.851,"afterCompact":false},{"index":49,"time":"17:59","ratio":0.769225,"inputTokens":307690,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.733,"originalCredits":5.733,"afterCompact":false},{"index":50,"time":"17:59","ratio":0.77722,"inputTokens":310888,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.12,"originalCredits":5.12,"afterCompact":false},{"index":51,"time":"18:00","ratio":0.784265,"inputTokens":313706,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.733,"originalCredits":4.733,"afterCompact":false},{"index":52,"time":"18:00","ratio":0.79008,"inputTokens":316032,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.948,"originalCredits":4.948,"afterCompact":false},{"index":53,"time":"18:00","ratio":0.793305,"inputTokens":317322,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.608,"originalCredits":4.608,"afterCompact":false},{"index":54,"time":"18:00","ratio":0.794705,"inputTokens":317882,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.415,"originalCredits":4.415,"afterCompact":false},{"index":55,"time":"18:00","ratio":0.795735,"inputTokens":318294,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.423,"originalCredits":4.423,"afterCompact":false},{"index":56,"time":"18:00","ratio":0.79705,"inputTokens":318820,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.494,"originalCredits":4.494,"afterCompact":false},{"index":57,"time":"18:01","ratio":0.800145,"inputTokens":320058,"outputTokens":null,"usageSource":"transcript-ratio","credits":6.866,"originalCredits":6.866,"afterCompact":false},{"index":58,"time":"18:29","ratio":0.413363,"inputTokens":165345,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.776,"originalCredits":4.776,"afterCompact":false},{"index":59,"time":"18:30","ratio":0.421345,"inputTokens":168538,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.717,"originalCredits":0.717,"afterCompact":false},{"index":60,"time":"18:32","ratio":0.432565,"inputTokens":173026,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.346,"originalCredits":1.346,"afterCompact":false},{"index":61,"time":"18:33","ratio":0.46799,"inputTokens":187196,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.898,"originalCredits":0.898,"afterCompact":false},{"index":62,"time":"18:33","ratio":0.473208,"inputTokens":189283,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.492,"originalCredits":0.492,"afterCompact":false},{"index":63,"time":"18:33","ratio":0.476875,"inputTokens":190750,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.492,"originalCredits":0.492,"afterCompact":false},{"index":64,"time":"18:33","ratio":0.478343,"inputTokens":191337,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.455,"originalCredits":0.455,"afterCompact":false},{"index":65,"time":"18:33","ratio":0.484308,"inputTokens":193723,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.5,"originalCredits":0.5,"afterCompact":false},{"index":66,"time":"18:33","ratio":0.486127,"inputTokens":194451,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.489,"originalCredits":0.489,"afterCompact":false},{"index":67,"time":"18:34","ratio":0.488023,"inputTokens":195209,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.469,"originalCredits":0.469,"afterCompact":false},{"index":68,"time":"18:34","ratio":0.488787,"inputTokens":195515,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.614,"originalCredits":0.614,"afterCompact":false},{"index":69,"time":"18:34","ratio":0.49607,"inputTokens":198428,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.541,"originalCredits":0.541,"afterCompact":false},{"index":70,"time":"18:34","ratio":0.49743,"inputTokens":198972,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.47,"originalCredits":0.47,"afterCompact":false},{"index":71,"time":"18:34","ratio":0.498785,"inputTokens":199514,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.475,"originalCredits":0.475,"afterCompact":false},{"index":72,"time":"18:35","ratio":0.50018,"inputTokens":200072,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.478,"originalCredits":0.478,"afterCompact":false},{"index":73,"time":"18:35","ratio":0.501498,"inputTokens":200599,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.488,"originalCredits":0.488,"afterCompact":false},{"index":74,"time":"18:35","ratio":0.50412,"inputTokens":201648,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.556,"originalCredits":0.556,"afterCompact":false},{"index":75,"time":"18:35","ratio":0.507777,"inputTokens":203111,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.495,"originalCredits":0.495,"afterCompact":false},{"index":76,"time":"18:35","ratio":0.509565,"inputTokens":203826,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.488,"originalCredits":0.488,"afterCompact":false},{"index":77,"time":"18:35","ratio":0.511572,"inputTokens":204629,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.522,"originalCredits":0.522,"afterCompact":false}],"identity":{"sumAttributed":16962380,"billedInputTokens":16962380,"absDiff":0,"ok":true},"pluginVersion":"2.7.4","selfCmd":"\"C:\\Users\\49745\\.qoder-cn\\plugins\\cache\\qoder-marketplace\\qoder-credits-inspector\\2.7.4\\bin\\credits-inspector.cmd\" cli","linkHealth":{"matched":0,"requests":77,"coverage":0,"usageSource":"transcript-ratio","breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":77},"logRecords":0,"lastRecordAt":null,"recentRequests":0,"proxyErrors":null,"clientAbort":null,"clientAbortMaxMs":null,"upstreamRejected":null,"aborted":null,"truncated":null,"noUsage":null,"slowestMs":null,"supersededFailure":null},"subagents":{"scanned":false,"dir":null,"probedPaths":["C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\a8a07087-7317-4957-80eb-e88a4eed2f8a\\subagents","C:\\Users\\49745\\.qoder-cn\\projects\\a8a07087-7317-4957-80eb-e88a4eed2f8a\\subagents"],"reason":"no-dir","count":0,"items":[],"totals":{"roundTrips":0,"billedInputTokens":0,"credits":0,"originalCredits":0},"combined":{"roundTrips":77,"billedInputTokens":16962380,"credits":301.715,"originalCredits":301.715}},"manual":null,"artifacts":{"report":"report.json","canvas":"请在 G__CODEX_New Manga.wo__15ec2eac.canvas.tsx"}} as unknown as Report;

function human(n: number): string {
  if (!isFinite(n)) return "—";
  const abs = Math.abs(n);
  if (abs >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (abs >= 1e6) return (n / 1e6).toFixed(2) + "M";
  if (abs >= 1e3) return (n / 1e3).toFixed(1) + "K";
  return String(Math.round(n));
}

function pct(x: number): string {
  return (x * 100).toFixed(1) + "%";
}

// —— 可用性口径：把 report.availability 翻成人话，并决定某个数字该显示值、「≈」还是「—」——
const AVAIL_LABEL: Record<string, string> = {
  measured: "实测",
  derived: "推导",
  fallback: "回退",
  manual: "手工",
  unavailable: "不可用",
};

const SOURCE_LABEL: Record<string, string> = {
  "desktop-rich": "桌面端富转录",
  "ide-lite": "IDE 端精简转录",
  unknown: "来源未知",
};

function availOf(av: Availability | undefined, key: keyof Availability, dflt: Avail = "measured"): Avail {
  return (av?.[key] as Avail | undefined) ?? dflt;
}

/** 段标题旁的性质标注：实测不标（默认就是实测），其余标出来。 */
function availTag(av: Availability | undefined, key: keyof Availability, dflt: Avail = "measured"): string {
  const v = availOf(av, key, dflt);
  return v === "measured" ? "" : `（${AVAIL_LABEL[v]}）`;
}

/** 不可用的量显示「—」而不是 0：IDE 端的 0 是「读不到」，不是「没发生」。 */
function orDash(
  v: number,
  av: Availability | undefined,
  key: keyof Availability,
  fmt: (n: number) => string = String
): string {
  return availOf(av, key) === "unavailable" ? "—" : fmt(v);
}

function kindLabel(kind: string): string {
  switch (kind) {
    case "read":
      return "读取";
    case "write":
      return "写入";
    case "search":
      return "搜索";
    case "shell":
      return "命令";
    default:
      return "其他";
  }
}

function shortTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return String(iso);
  const p = (v: number) => String(v).padStart(2, "0");
  return `${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

export default function SessionTokensReport() {
  if (!REPORT) {
    return (
      <ReportShell width="wide" ariaLabel="会话 token 消耗截析">
        <Stack gap="component">
          <H1>会话 token 消耗截析</H1>
          <Text tone="secondary">报告数据尚未注入。请在会话中触发一次 Stop 钩子，或运行 CLI 生成 report.json。</Text>
        </Stack>
      </ReportShell>
    );
  }

  const r = REPORT;
  const s = r.session;
  const c = r.context;
  const t = r.totals;
  const av = r.availability;
  const manual = r.manual ?? null;
  const sourceLabel = SOURCE_LABEL[r.source ?? "unknown"] ?? "来源未知";
  // 有没有 usage 决定整份报告是「真值/推导」还是「一律 —」。手工回填的 credits 不算有 usage，
  // 否则下面按 ratio 推导的图表会照画一堆 0。
  const hasUsage = availOf(av, "roundTrips") === "measured";
  const manualCredits = manual?.credits ?? null;

  // 报告里出现的命令一律用数据层注入的插件入口（Windows 上是自带启动器的绝对路径，免装 Node）。
  // 旧报告没有这个字段时回退原写法，不比改动前更差。
  const CLI = r.selfCmd || "node scripts/cli.mjs";

  // credits 覆盖范围：credits 与「计费输入总量」并排放在头部，读者一除就得到单价。
  // 混合会话里 credits 只来自转录路径的那几笔（实测某会话 413 笔里只有 1 笔带 credits），
  // 部分覆盖不说出来 = 把局部真值当全量展示。
  const cov = r.creditsCoverage ?? null;
  const covPartial = !!(cov && !cov.full && cov.roundTrips > 0);
  const covNote = covPartial ? ` · 仅覆盖 ${cov!.trips}/${cov!.roundTrips} 笔往返（占计费输入 ${pct(cov!.tokenShare)}）` : "";

  // 缓存命中：代理记录里一直带着 cachedTokens，此前采集了却从不呈现。
  const cachedMeasured = availOf(av, "cachedTokens") === "measured";
  const cachedText = cachedMeasured
    ? `输入 ${human(t.billedInputTokens)}，其中缓存命中 ${human(t.cachedTokens ?? 0)}（${pct(t.cachedShare ?? 0)}，${t.cachedTrips ?? 0} 笔往返带缓存）——供应商对重复叠加的前缀打折，故按 token 数的节省大于按计费的节省。`
    : "";

  // 代理告警只在「失败记录仍然成立」时才报：status.json 只写不清，陈旧失败会把用户推去改
  // 本来正确的 Base URL，越修越坏；而同一份报告里的 lastRecordAt / matched 是它在跑的硬证据。
  const proxyAlarm = r.proxy?.status && !r.proxy.statusSuperseded ? r.proxy.status : null;
  const proxyAlive = !proxyAlarm && (r.proxy?.logRecords ?? 0) > 0;

  // 官方 UI 一场会话扣费 = 主链 + 子代理，故有子代理时 headline 必须给 combined，否则比 UI 少一截
  const creditScope =
    r.subagents && r.subagents.count > 0
      ? {
          credits: r.subagents.combined.credits,
          note: `主链 ${t.credits} + 子代理 ${r.subagents.totals.credits} · 原始 ${r.subagents.combined.originalCredits}`,
        }
      : { credits: t.credits, note: `原始 ${t.originalCredits}（实测）` };

  const headline: MetricItem[] = [
    {
      label: "计费输入总量",
      value: hasUsage ? human(t.billedInputTokens) : "—",
      description: hasUsage
        ? availOf(av, "tokens") === "measured"
          ? `Σ prompt_tokens（实测真值）${covPartial ? ` · 覆盖全部 ${cov!.roundTrips} 笔往返` : ""}`
          : `Σ 上下文 × 往返${availTag(av, "tokens", "derived")}${covPartial ? ` · 覆盖全部 ${cov!.roundTrips} 笔往返` : ""}`
        : "转录无 usage",
    },
    {
      label: "当前上下文",
      value: hasUsage ? human(t.netContextTokens) : "—",
      description: hasUsage
        ? `峰值 ${pct(c.peakContextRatio)}${s.compactions ? "（压缩后起算）" : ""}`
        : "转录无 usage",
    },
    {
      label: "重发放大",
      value: hasUsage ? `${t.amplification}×` : "—",
      description: `往返 ${hasUsage ? `${s.roundTrips} 次` : "—"}`,
    },
    {
      label: "Credits",
      // 代理路径（自定义模型）token 是实测真值但 credits 无来源：hasUsage 为真也要显示「—」，
      // 否则 t.credits=0 会被读成「这次没花钱」。
      value:
        manualCredits != null
          ? `${manualCredits}`
          : hasUsage && availOf(av, "credits") !== "unavailable"
            ? `${creditScope.credits}`
            : "—",
      description:
        manualCredits != null
          ? `官方 UI 手工录入 · 本地 ${creditScope.credits}`
          : hasUsage && availOf(av, "credits") !== "unavailable"
            ? `${creditScope.note}${covNote}`
            : r.usageSource === "proxy" || r.usageSource === "transcript-tokens" || r.usageSource === "mixed"
              ? "自定义模型（BYOK）不经 Qoder 计费网关，无 credits 真值"
              : hasUsage
                ? "转录带 usage 但没有 credits 字段，本地无计费真值"
                : "本地不可用，见下方告警",
    },
  ];

  const pieData = r.byCategory.map((x) => ({ label: x.label, value: x.tokens }));

  // 系统提示词是报告里少数「用户能直接动」的一项：它每轮被完整重发，总量 = 每请求规模 × 往返数，
  // 而它的大小由装了多少插件与技能决定。占比小时不必啰嗦。
  const sysCat = r.byCategory.find((x) => x.key === "system");
  const sysNote =
    hasUsage && sysCat && sysCat.share >= 0.1
      ? ` 系统提示词占 ${pct(sysCat.share)}（${human(c.systemPromptTokens)}/请求 × ${s.roundTrips} 次往返 = ${human(sysCat.tokens)}）：它每轮都被完整重发，大小由你装了多少插件与技能决定，精简技能能直接压低这一项——本插件自己的技能描述也常驻在里面（约 170 token）。`
      : "";

  const tools = r.byTool.slice(0, 8);
  const toolCategories = tools.map((x) => x.tool);
  const toolSeries = [{ name: "重发 tokens", data: tools.map((x) => x.tokens) }];
  // 「单次」= 平均每次调用带来的重发 token。总量榜会埋掉次数少但每次极贵的工具：
  // 实测 Read 只 29 次却吃 335 万，单次是 Edit 的 2.6 倍。
  const toolRows = tools.map((x) => [
    x.tool,
    human(x.tokens),
    pct(x.share),
    String(x.calls),
    x.perCall == null ? "—" : human(x.perCall),
  ]);

  const files = r.byFile.slice(0, 20);
  const fileRows = files.map((f) => [
    f.label,
    kindLabel(f.kind),
    human(f.billed),
    pct(f.share),
    f.perRead == null ? "—" : human(f.perRead),
    String(f.trips),
    String(f.reads),
  ]);

  const byReq = r.byRequest ?? [];
  const reqLabels = byReq.map((x, i) => x.time || `#${x.index ?? i + 1}`);
  const reqInputs = byReq.map((x) => x.inputTokens);
  const reqCredits = byReq.map((x) => x.credits);
  // credits 只在覆盖全部往返时才画曲线：部分覆盖（BYOK 混合会话实测 413 笔里 1 笔有 credits）
  // 画出来是一地零，既读不出形状，还会暗示「其余往返没花钱」。
  const showCreditsChart = hasUsage && !covPartial && availOf(av, "credits") !== "unavailable";

  // 按类别下钻：类别小计行（accent/neutral）+ 其工具/文件明细行（default），用 rowTone 分组着色。
  const catDetail = r.byCategoryDetail ?? [];
  const detailRows: string[][] = [];
  const detailTones: ("accent" | "neutral" | "default")[] = [];
  for (const cc of catDetail) {
    const hasKids = cc.children.length > 0;
    detailRows.push([cc.label, "—", hasKids ? "小计" : "（整体，无工具/文件归属）", human(cc.tokens), pct(cc.share), "100%", "—"]);
    detailTones.push(hasKids ? "accent" : "neutral");
    for (const k of cc.children) {
      detailRows.push(["", k.tool || "—", k.label, human(k.tokens), pct(k.share), pct(k.catShare), String(k.trips)]);
      detailTones.push("default");
    }
  }

  // 子代理账：Agent 派发的子代理消耗不在主链里，单独一段呈现（无子代理则整段不渲染）。
  const sub = r.subagents;
  const subItems = sub?.items ?? [];
  const subRows: string[][] = [];
  const subTones: ("accent" | "default")[] = [];
  for (const a of subItems) {
    subRows.push([
      a.description || a.agentId,
      a.agentType || "—",
      String(a.roundTrips),
      human(a.billedInputTokens),
      pct(a.peakContextRatio),
      String(a.credits),
      String(a.originalCredits),
      a.error || "—",
    ]);
    subTones.push("default");
  }
  if (sub && subItems.length > 0) {
    subRows.push([
      "合计（主链 + 子代理）",
      "—",
      String(sub.combined.roundTrips),
      human(sub.combined.billedInputTokens),
      "—",
      String(sub.combined.credits),
      String(sub.combined.originalCredits),
      `主链 ${t.credits} / 子代理 ${sub.totals.credits}`,
    ]);
    subTones.push("accent");
  }

  // 压缩单笔成本：输入/摘要一律取数据层归一后的生效值（有代理实测就是实测，否则是客户端自估），
  // 并用「口径」列把两者分开——混着显示会让自估值被当成实测。
  const ccost = r.compactionCost;
  const ccItems = ccost?.items ?? [];
  const compactRows: string[][] = ccItems.map((e) => [
    `#${e.index}`,
    shortTime(e.at),
    e.trigger || "—",
    e.effectiveInputTokens == null ? "—" : human(e.effectiveInputTokens),
    e.effectiveOutputTokens == null ? "—" : human(e.effectiveOutputTokens),
    e.nextInputTokens == null ? "—" : human(e.nextInputTokens),
    e.savedTokens == null ? "—" : human(e.savedTokens),
    e.proxy && e.proxy.ms != null ? `${Math.round(e.proxy.ms / 1000)}s` : "—",
    e.proxy ? "实测" : "自估",
  ]);

  // IDE 端仅剩的真值：工具调用次数与文件读取次数（不依赖 usage，两种转录都写 tool_use 块）。
  const residueRows: string[][] = [];
  if (!hasUsage) {
    for (const x of r.byTool.filter((v) => v.calls > 0).sort((a, b) => b.calls - a.calls).slice(0, 15)) {
      residueRows.push([x.tool, "工具", String(x.calls), "—", "—"]);
    }
    for (const f of r.byFile.filter((v) => v.reads > 0).sort((a, b) => b.reads - a.reads).slice(0, 15)) {
      residueRows.push([f.label, kindLabel(f.kind), "—", String(f.reads), String(f.trips)]);
    }
  }

  // A1 三值：一次带 usage 的往返都没有时 0 <= max(2,0) 恒成立，会把「没数据」判成「校验通过」，
  // 故 breakdown.mjs 在 reqCount===0 时给 null；这里必须显示「不适用」而不是绿色通过。
  const identityText =
    r.identity.ok == null
      ? "恒等式 A1 不适用（本转录没有一次带 usage 的往返）。"
      : r.identity.ok
        ? `归因覆盖 ${pct(t.coverage)}${availTag(av, "categoryShare", "derived")}，恒等式 A1 通过（|Δ|=${r.identity.absDiff}）。`
        : `归因覆盖 ${pct(t.coverage)}，恒等式 A1 未通过（|Δ|=${r.identity.absDiff}）。`;
  // 窗口读不到时是静默回退的 200000，而所有 token 数字都乘它 —— 必须显式标 ≈ 与来源。
  const cwIsFallback = availOf(av, "contextWindow") === "fallback";
  const cwText = cwIsFallback ? `≈${human(c.contextWindow)}（回退值）` : human(c.contextWindow);
  // 当前占用头条：以最新上下文（currentContextTokens）为准；段内单调递增 ⇒ 旧版峰值与当前恒等，故合并为一条。
  const curCtx = c.currentContextTokens ?? c.peakContextTokens;
  const netAdv = c.netUserAdvice || c.peakUserAdvice || c.peakAdvice || null;
  const limitSrcLabel =
    c.userContextLimitSource === "manual" ? "手工"
    : c.userContextLimitSource === "config" ? "配置"
    : c.userContextLimitSource === "derived" ? "实测反推"
    : "默认";
  // 阈值来源非 manual/config/derived ⇒ 用的是内置兜底 200K，不是用户在 Qoder 设的真值，需显式提示如何改。
  const limitIsDefault = c.userContextLimitSource !== "manual" && c.userContextLimitSource !== "config" && c.userContextLimitSource !== "derived";
  // 上下文对比表：把旧版挤成一段小字的「界面显示 / 自动压缩实况 / 历史高点」拆成可扫读的行，无数据不占位。
  const ctxRows: string[][] = [];
  if (c.userContextLimit != null && Number.isFinite(c.contextWindow)) {
    ctxRows.push(
      c.contextWindow > c.userContextLimit
        ? ["Qoder 界面进度条", pct(c.netWindowRatio ?? c.peakContextRatio), `按模型物理窗口 ${cwText} 算，比你真实占比低约 ${(c.contextWindow / c.userContextLimit).toFixed(1)} 倍——界面显得偏空、有迷惑性，别信它`]
        : ["Qoder 界面进度条", pct(c.netWindowRatio ?? c.peakContextRatio), `按模型窗口 ${cwText} 算，与你实设上限一致，显示无偏差`],
    );
  }
  if (c.observedAutoCompactions != null && c.observedAutoCompactions > 0 && c.observedAutoTriggerTokens != null) {
    ctxRows.push(["自动压缩实况", `自动 ${c.observedAutoCompactions} 次`, `触发点在 ~${human(c.observedAutoTriggerTokens)}（窗口的 ${pct(c.autoTriggerRatio ?? 0)}）`]);
  } else if (s.compactions > 0) {
    ctxRows.push(["压缩实况", `手动 ${s.compactions} 次`, "本场未见自动压缩，均为你手动触发"]);
  }
  if (c.peakSessionNotable) {
    ctxRows.push(["压缩前历史高点", `${pct(c.peakSessionRatio ?? 0)}（${human(c.peakSessionTokens ?? 0)}）`, "本场曾达到的最高占用"]);
  }

  // 链路健康度：把 --request-log 的逐笔归因压成一行结论（明细属于排障，留在 CLI）。
  // 分两档：本会话确实走在代理链路上（proxy/mixed）才印「最近 N 笔」的失败统计与排障命令；
  // token 全来自转录的会话里，那些统计说的是别的会话，印成 warning + 命令是噪音，只留覆盖率与最近记录时间。
  // 纯官方模型用户从没配过代理，整行不渲染。
  const lhRaw = r.linkHealth ?? null;
  const lh = lhRaw && (r.proxy?.configured || lhRaw.matched > 0) ? lhRaw : null;
  const lhOnPath = !!lh && (lh.matched > 0 || lh.usageSource === "proxy" || lh.usageSource === "mixed");
  const lhErrors = lh ? lh.proxyErrors ?? 0 : 0;
  const lhBad = lhOnPath && lhErrors > 0;
  const lhTone: "info" | "warning" = lhBad ? "warning" : "info";
  // 三档拆分一行说清：代理实测 / 转录 input_tokens / 转录 ratio×window 各多少笔。
  // 旧报告（v3）无 breakdown 字段时退回到只报 matched。
  const lhBd = lh?.breakdown ?? null;
  const lhBdText = lhBd
    ? `拆分：代理 ${lhBd.proxy} 笔 · 转录 input_tokens ${lhBd.transcriptTokens} 笔 · 转录 ratio×窗口 ${lhBd.transcriptRatio} 笔`
    : "";
  const lhSrcNote = !lh
    ? ""
    : lh.usageSource === "proxy"
      ? "：全部为供应商实测"
      : lh.usageSource === "transcript-tokens"
        ? "：本会话 token 全来自转录 input_tokens（BYOK，代理未在链路上）"
        : lh.usageSource === "transcript-ratio"
          ? "：本会话 token 由 ratio×窗口推导（官方模型）"
          : lh.usageSource === "mixed"
            ? "：多源混合，以下拆分列为准"
            : lh.usageSource === "transcript"
              ? "：本会话 token 全部来自转录，代理不在链路上"
              : "";
  const lhText = !lh
    ? ""
    : [
        lh.requests > 0
          ? `代理覆盖 ${lh.matched}/${lh.requests} 笔往返（${pct(lh.coverage)}）${lhSrcNote}`
          : "本会话没有带 usage 的往返，代理无从覆盖",
        lhBdText,
        lh.lastRecordAt ? `代理最近记录 ${shortTime(lh.lastRecordAt)}` : proxyAlive ? "代理有记录但无时间戳" : "代理从未记到流量",
        lhOnPath && lh.recentRequests
          ? `最近 ${lh.recentRequests} 笔：代理失败 ${lh.proxyErrors} · 上游报错 ${lh.upstreamRejected} · 客户端提前断开 ${lh.aborted} · 成功但无 usage ${lh.noUsage}${
              lh.slowestMs != null ? ` · 最慢 ${Math.round(lh.slowestMs / 1000)}s` : ""
            }`
          : lhOnPath
            ? "请求诊断日志为空（运行中的代理是旧版，或还没记到）"
            : "",
        lhBad ? `有「代理失败」= 请求没出得去或代理自己抛了，跑 ${CLI} --request-log 看归因` : "",
        !lhOnPath && lhErrors > 0 ? `代理另有 ${lhErrors} 笔失败，属于走代理的那些会话` : "",
        lh.supersededFailure
          ? `${shortTime(lh.supersededFailure.at ?? null)} 那条「拉起失败（${lh.supersededFailure.error}）」已被之后的流量推翻，无需处理`
          : "",
      ]
        .filter(Boolean)
        .join("。") + "。";

  return (
    <ReportShell width="wide" ariaLabel="会话 token 消耗截析">
      <Stack gap="sectionCompact">
        <header>
          <Stack gap="component">
            <H1>会话 token 消耗截析</H1>
            <Text tone="secondary">
              {s.model || "未知模型"}
              {s.modelSource === "manual" ? "（手工录入）" : ""} · {sourceLabel} · 会话{" "}
              {String(s.id || "").slice(0, 8)}
              {s.title ? `「${s.title}」` : ""} · {shortTime(s.startedAt)} →{" "}
              {shortTime(s.endedAt)} · 压缩{" "}
              {availOf(av, "compactions") === "unavailable" ? "—" : `${s.compactions} 次`}
              {r.usageSource ? ` · usage 来源 ${
                r.usageSource === "proxy"
                  ? "代理实测"
                  : r.usageSource === "transcript-tokens"
                    ? "转录 input_tokens"
                    : r.usageSource === "transcript-ratio"
                      ? "转录 ratio×窗口"
                      : r.usageSource === "mixed"
                        ? "多源混合"
                        : "转录"
              }` : ""}
              {r.pluginVersion ? ` · v${r.pluginVersion}` : ""} · schema v{r.schemaVersion}
            </Text>
            <MetricsGrid variant="header" columns={4} items={headline} />
          </Stack>
        </header>

        {!hasUsage && r.source === "desktop-rich" && (
          <Callout tone="danger" title="本报告数值不可用：自定义模型（BYOK）不经 Qoder 计费网关">
            转录是桌面端富布局，但 assistant entry 里没有 message.usage——自定义模型（如千问
            tokenplan）的响应不经 Qoder 计费网关，credits / context_usage_ratio 无来源，提供商返回的
            usage 客户端也不落盘（已实测扫过 ~/.qoder-cn、~/.qoder、~/.qoder-cli 与 %APPDATA%\QoderCN）。
            本地补救（改一个配置文件即可，免装 Node、之后全自动）：编辑 {"`~/.qoder-credits-proxy/config.json`"}，
            把 {"`upstream`"} 填成你的供应商根地址（= Base URL 去掉结尾 /v1），再把自定义模型 Base URL 的 host:port
            换成 {`127.0.0.1:${r.proxy?.port ?? 49787}`}（路径保留），新开一个会话即自动拉起代理、按 message.id
            精确 join 出实测 token（credits 仍无真值）。装了 Node 也可用 {"`--setup-proxy`"} / {"`--check-proxy`"} 一步到位。
            手工回填通道同样可用：
            {"`.qoder-credits/overrides/<sessionId>.json`"}。
          </Callout>
        )}

        {!hasUsage && r.source !== "desktop-rich" && (
          <Callout tone="danger" title="本报告数值不可用：转录不含 message.usage">
            这是 {sourceLabel}（IDE 端客户端）。它的转录只写 session_meta / user / assistant / progress 四种 entry，
            message.usage 整个字段不存在，也不落到本地任何其它文件（已实测扫过 ~/.qoder-cn、~/.qoder、
            ~/.qoder-cli 与 %APPDATA%\QoderCN）。因此 Credits、token 与各类占比一律显示「—」而不是 0 ——
            0 会被误读成「这次没花钱」。真值只有官方 UI 有：把它填进{" "}
            {"`.qoder-credits/overrides/<sessionId>.json`"} 后重跑，上方会出现「官方 UI 真值」一段并与本地并列对账。
          </Callout>
        )}

        {manual && (
          <Callout tone="success" title="官方 UI 真值（手工录入，未覆盖任何本地数字）">
            Credits {manual.credits ?? "—"} · 原价 {manual.originalCredits ?? "—"}
            {manual.model ? ` · 模型 ${manual.model}` : ""}
            {manual.durationMin != null ? ` · 时长 ${manual.durationMin} min` : ""}
            {manual.startedAt ? ` · ${shortTime(manual.startedAt)}` : ""}
            {manual.localCoverage != null
              ? ` · 本地${manual.localScope === "combined" ? "合计（主链+子代理）" : "主链"} ${manual.localCredits ?? t.credits}，覆盖 ${pct(manual.localCoverage)}`
              : " · 本地无 usage，无法对账"}
            {manual.note ? `。备注：${manual.note}` : ""}
          </Callout>
        )}

        {sub && sub.count === 0 && sub.reason && sub.reason !== "no-dir" && (
          <Callout tone="warning" title={`子代理账未汇总（${sub.reason}）`}>
            探测过的候选目录：{(sub.probedPaths ?? []).join("  |  ") || "（无）"}
          </Callout>
        )}

        {proxyAlarm && (
          <Callout tone="warning" title={`代理自动启动失败（${proxyAlarm.error}）`}>
            {proxyAlarm.error === "EADDRINUSE"
              ? `端口 ${proxyAlarm.port ?? "—"} 被占用，自定义模型将无法对话。请换一个空闲端口重启代理：${CLI} --setup-proxy --port <新端口>，并把模型 Base URL 改成新端口。`
              : `代理未就绪（${proxyAlarm.error}），自定义模型可能无法对话。请运行 ${CLI} --check-proxy 查看链路状态。`}
          </Callout>
        )}

        {r.proxy?.dormant && !proxyAlarm && (
          <Callout tone="info" title="代理长期空闲">
            代理已配置但超过 14 天没有记录到流量（可能你已改回官方模型）。如不再使用自定义模型，可运行{" "}
            {CLI} --stop-proxy 停用代理；保留也不影响官方模型。
          </Callout>
        )}

        {cwIsFallback && (
          <Callout tone="warning" title="上下文窗口为回退值 200K（未从 runtime-config / usage 反推 / ManualTruth 拿到真值）">
            本会话所有以窗口为分母的占比与「峰值建议」都可能偏大，而绝对 token 数（已改以 S 真值为底）不受影响。
            建议在 {"`.qoder-credits/overrides/<sessionId>.json`"} 里手工填 {"`contextWindow`"}（如 qwen3-max=1000000），或等一笔带 input_tokens+ratio 的往返写入转录后自动反推生效。
          </Callout>
        )}

        {hasUsage && netAdv && c.userContextLimit != null && (
          <Stack gap="component">
            <Callout
              tone={netAdv.tone}
              title={`你真实的上下文占用 ${pct(c.netUserRatio ?? c.peakUserRatio ?? 0)}（${human(curCtx)} / 阈值 ${human(c.userContextLimit)}・${limitSrcLabel}）`}
            >
              {netAdv.text}
              {limitIsDefault && (
                <Text tone="secondary">
                  {` ⚙ 这里的 ${human(c.userContextLimit)} 是插件内置默认值，不是你在 Qoder「模型管理」里设的真实上限（插件读不到那个设置）。想按真实阈值算：在 ~/.qoder-credits-proxy/config.json 填 "userContextLimit": <你的上限>（对所有会话生效），或对本会话在 .qoder-credits/overrides/<会话id>.json 填同名字段，重跑报告即生效。`}
                </Text>
              )}
            </Callout>
            {ctxRows.length > 0 && (
              <Table
                headers={["对比口径", "数值", "说明"]}
                rows={ctxRows}
                density="compact"
              />
            )}
          </Stack>
        )}

        {c.thresholdNotEnforced && (
          <Callout tone="warning" title="⚠ 自动压缩不会在你设的阈值触发（本条最重要）">
            你的模型物理窗口是 {cwText}，Qoder 的自动压缩要等上下文涨到窗口 ~85%（≈{human(Math.round(c.contextWindow * 0.85))}）才触发；
            你在模型管理里设的 {human(c.userContextLimit)} 上限远在其下，永远不会触发自动压缩。
            请照上面「你真实的上下文占用」那条，到点自己手动压缩，别等它自动压。
          </Callout>
        )}

        {lh && (
          <Callout tone={lhTone} title="链路健康度">
            {lhText}
          </Callout>
        )}

        <Callout tone="info" title="度量口径">
          计费输入总量逐笔锁定真值（优先级：代理 promptTokens &gt; 转录 usage.input_tokens &gt; ratio{availTag(av, "contextRatio")} × {cwText}
          {cwIsFallback ? "，未拿到真窗口、全部 token 数字随之带 ≈" : ""}）；各类别/文件按块估算规模比例分摊
          {availTag(av, "categoryShare", "derived")}。{identityText}
          {cachedText ? ` ${cachedText}` : ""}
          {covPartial
            ? ` Credits 只来自 ${cov!.trips}/${cov!.roundTrips} 笔往返（占计费输入 ${pct(cov!.tokenShare)}），其余往返走代理实测、不经 Qoder 计费，故不要拿 Credits 去除以计费输入总量算单价。`
            : ""}
        </Callout>

        {byReq.length > 0 && (
          <ReportSection
            title="逐请求明细（每一次往返）"
            description={
              showCreditsChart
                ? "每个 round-trip 的真实输入规模与 credits；曲线骤降处为上下文压缩重置（顶部四项为会话累计，此处为每一次）"
                : `每个 round-trip 的真实输入规模；曲线骤降处为上下文压缩重置。credits 曲线未画：本会话只有 ${cov?.trips ?? 0}/${cov?.roundTrips ?? byReq.length} 笔往返带 credits（其余走代理实测、不经 Qoder 计费），画出来是一地零。`
            }
            meta={`${byReq.length} 次往返 · 压缩 ${orDash(s.compactions, av, "compactions")} 次`}
            divided
          >
            {showCreditsChart ? (
              <ChartComparisonGrid>
                <ChartContainer title="每次输入 tokens" ariaLabel="每次输入 tokens">
                  <LineChart
                    categories={reqLabels}
                    series={[{ name: "输入 tokens", data: reqInputs, tone: "info" }]}
                    height={220}
                    valueFormatter={human}
                    ariaLabel="每次请求输入 tokens"
                  />
                </ChartContainer>
                <ChartContainer title="每次 credits" ariaLabel="每次 credits">
                  <LineChart
                    categories={reqLabels}
                    series={[{ name: "credits", data: reqCredits, tone: "warning" }]}
                    height={220}
                    ariaLabel="每次请求 credits"
                  />
                </ChartContainer>
              </ChartComparisonGrid>
            ) : (
              <ChartContainer title="每次输入 tokens" ariaLabel="每次输入 tokens">
                <LineChart
                  categories={reqLabels}
                  series={[{ name: "输入 tokens", data: reqInputs, tone: "info" }]}
                  height={220}
                  valueFormatter={human}
                  ariaLabel="每次请求输入 tokens"
                />
              </ChartContainer>
            )}
          </ReportSection>
        )}

        {hasUsage && ccItems.length > 0 && (
          <ReportSection
            title="压缩单笔成本（会话里最贵的那几笔调用）"
            description="每次压缩本身就是一笔普通模型调用：整份上下文当 prompt 进去、摘要当 completion 出来。此前报告只显示「压缩 N 次」，把单笔最贵的开销藏成了一个计数。「省下」= 压缩前规模 − 压缩后首轮实测输入（地板）。口径列：实测=能在代理日志里唯一对上的供应商真值；自估=客户端在压缩边界里写的前后规模。"
            meta={`${ccItems.length} 次 · 输入累计 ${human(ccost?.totals.preTokens ?? 0)} · 摘要累计 ${human(ccost?.totals.postTokens ?? 0)} · 累计省下 ${human(ccost?.totals.savedTokens ?? 0)} · 其中 ${ccost?.totals.measured ?? 0} 笔为供应商实测`}
            divided
          >
            <Table
              headers={["第几次", "时刻", "触发", "输入", "摘要输出", "压缩后首轮", "省下", "耗时", "口径"]}
              rows={compactRows}
              density="compact"
              stickyHeader
            />
          </ReportSection>
        )}

        {sub && subItems.length > 0 && (
          <ReportSection
            title="子代理账（Agent 派发）"
            description="子代理的每次往返只写进它自己的独立转录，不计入上方主链任何数字；官方 UI 的一场会话扣费 = 主链 + 各子代理。"
            meta={`${subItems.length} 个子代理 · 主链 ${t.credits} + 子代理 ${sub.totals.credits} = 合计 ${sub.combined.credits} Credits`}
            divided
          >
            <Table
              headers={["子代理", "类型", "往返", "计费输入", "峰值占比", "Credits", "原价", "备注"]}
              rows={subRows}
              rowTone={subTones}
              density="compact"
              stickyHeader
            />
          </ReportSection>
        )}

        {hasUsage && r.byCategory.length > 0 && (
          <ReportSection
            title="按类别占比"
            description={`会话计费输入 token 在各来源间的分布（完整划分，占比之和 = 100%）${sysNote}`}
            meta={human(t.billedInputTokens) + ` tokens${availTag(av, "categoryShare", "derived")}`}
            divided
          >
            <ChartContainer ariaLabel="按类别占比">
              <PieChart donut data={pieData} centerLabel="计费输入" valueFormatter={human} />
            </ChartContainer>
          </ReportSection>
        )}

        {hasUsage && catDetail.length > 0 && (
          <ReportSection
            title="按类别下钻（工具 / 文件路径）"
            description="每个类别的消耗再拆到工具与具体文件/路径：工具返回、工具调用可精确到路径，其余类别为整体（无文件归属）。数值均为重发计费 token。"
            meta={`占总额=占计费输入总量 · 占本类=占该类别 · 程数=存活往返累计${availTag(av, "fileShare", "derived")}`}
            divided
          >
            <Table
              headers={["类别", "工具", "文件 / 路径", "重发 tokens", "占总额", "占本类", "程数"]}
              rows={detailRows}
              rowTone={detailTones}
              density="compact"
              stickyHeader
            />
          </ReportSection>
        )}

        {hasUsage && tools.length > 0 && (
          <ReportSection
            title="按工具占比"
            description="各工具相关内容（调用参数 + 返回）重发累计的计费 token 占比（仅工具相关块，非完整划分，占比之和 < 100%）。「单次」= 平均每次调用带来的重发 token：总量榜会把「次数少但每次极贵」的工具埋掉，这一列专门把它捞出来。"
            meta={`token 占比${availTag(av, "toolShare", "derived")} · 调用次数为实测`}
            divided
          >
            <Stack gap="component">
              <ChartContainer ariaLabel="按工具占比">
                <BarChart horizontal categories={toolCategories} series={toolSeries} valueFormatter={human} ariaLabel="按工具占比" />
              </ChartContainer>
              <Table
                headers={["工具", "重发 tokens", "占比", "调用", "单次"]}
                rows={toolRows}
                density="compact"
                stickyHeader
              />
            </Stack>
          </ReportSection>
        )}

        {hasUsage && fileRows.length > 0 && (
          <ReportSection
            title="按文件占比"
            description="精确到路径/文件名：内容随上下文被重复发送累计的计费 token 占比（Top 20，仅可归因文件的块）。「单次读取」= 这个文件平均每次被读取最终烧掉多少（含此后每一程的重发）——读一次就烧掉十几万的文件，在按总量排序的榜上毫不起眼。"
            meta={`程数=存活往返累计 · 读取=返回次数（实测）${availTag(av, "fileShare", "derived")}`}
            divided
          >
            <Table
              headers={["文件", "种类", "重发 tokens", "占比", "单次读取", "程数", "读取"]}
              rows={fileRows}
              density="compact"
              stickyHeader
            />
          </ReportSection>
        )}

        {!hasUsage && residueRows.length > 0 && (
          <ReportSection
            title="工具调用与文件读取（计数为实测）"
            description="占比与 token 一律不可用，但 tool_use 块两种转录都写，所以「谁被调了几次、谁被读了几次」仍是真值 —— IDE 端不是一无所有。"
            meta={`${t.toolCalls ?? 0} 次工具调用${availTag(av, "toolCalls")} · ${t.fileReads ?? 0} 次文件读取${availTag(av, "fileReads")} · ${s.turns} 轮对话`}
            divided
          >
            <Table
              headers={["工具 / 文件", "种类", "调用", "读取", "程数"]}
              rows={residueRows}
              density="compact"
              stickyHeader
            />
          </ReportSection>
        )}
      </Stack>
    </ReportShell>
  );
}
