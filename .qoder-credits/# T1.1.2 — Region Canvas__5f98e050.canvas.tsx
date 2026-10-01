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
const REPORT = {"schemaVersion":3.2,"generatedAt":"2026-09-22T10:09:21.757Z","source":"desktop-rich","usageSource":"transcript-ratio","availability":{"credits":"measured","roundTrips":"measured","contextRatio":"measured","tokens":"derived","outputTokens":"unavailable","cachedTokens":"unavailable","categoryShare":"derived","toolShare":"derived","fileShare":"derived","systemPrompt":"derived","contextWindow":"measured","compactions":"measured","compactionCost":"measured","model":"measured","title":"measured","toolCalls":"measured","fileReads":"measured","userTurns":"measured","userContextLimit":"fallback"},"session":{"id":"5f98e050-07f7-425e-a755-9000567ac78d","title":"# T1.1.2 — Region Canvas","titleSource":"first-user","model":"qfmodel","modelSource":"runtime-config","cwd":"G:\\CODEX\\New Manga","turns":6,"roundTrips":471,"compactions":1,"startedAt":"2026-09-21T07:39:47.635Z","endedAt":"2026-09-22T10:09:21.453Z"},"context":{"contextWindow":400000,"contextWindowSource":"runtime-config","systemPromptTokens":19300,"netContextTokens":271680,"peakContextTokens":271680,"peakContextRatio":0.6792,"peakSessionTokens":360993,"peakSessionRatio":0.9024825,"peakSessionNotable":true,"peakAdvice":{"level":"sweet","tone":"success","text":"正处性价比区间（65–85%）。此时压一次每轮省得最多，且第一轮就回本"},"userContextLimit":200000,"userContextLimitSource":"default","peakUserRatio":1.3584,"peakUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"currentContextTokens":271680,"netUserRatio":1.3584,"netUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"netWindowRatio":0.6792,"observedAutoCompactions":1,"observedAutoTriggerTokens":361231,"autoTriggerRatio":0.9030775,"thresholdNotEnforced":true},"totals":{"billedInputTokens":84983322,"netContextTokens":271680,"peakContextTokens":271680,"amplification":312.81,"attributedTokens":84983322,"coverage":1,"credits":246.011,"originalCredits":246.011,"outputTokens":0,"cachedTokens":0,"cachedTrips":0,"cachedShare":0,"toolCalls":578,"fileReads":245},"creditsCoverage":{"trips":471,"roundTrips":471,"tokens":84983322,"tokenShare":1,"full":true},"compactionCost":{"count":1,"items":[{"index":1,"at":"2026-09-22T08:55:36.281Z","trigger":"auto","preTokens":361231,"postTokens":5260,"messagesSummarized":956,"nextRequestIndex":232,"nextInputTokens":42525,"savedTokens":318706,"proxy":null,"effectiveInputTokens":361231,"effectiveOutputTokens":5260}],"totals":{"preTokens":361231,"postTokens":5260,"savedTokens":318706,"measured":0}},"proxy":{"matched":0,"requests":471,"breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":471},"logPath":"C:\\Users\\49745\\.qoder-credits-proxy\\usage.jsonl","logExists":false,"logRecords":0,"configured":false,"enabled":true,"port":49787,"lastRecordAt":null,"dormant":false,"status":null,"statusSuperseded":false},"byCategory":[{"key":"tool_result","label":"工具返回","tokens":21710875,"share":0.2554721910678794},{"key":"system","label":"系统提示词","tokens":9090300,"share":0.10696569380989837},{"key":"compact_summary","label":"压缩摘要","tokens":1243628,"share":0.014633784544951203},{"key":"assistant_thinking","label":"模型思考","tokens":17771291,"share":0.20911504543712478},{"key":"assistant_tool_use","label":"工具调用","tokens":13422790,"share":0.15794616283099971},{"key":"assistant_text","label":"模型回复","tokens":1028737,"share":0.012105168042934409},{"key":"user_input","label":"用户输入","tokens":2666713,"share":0.03137925091602665},{"key":"attachment","label":"附件/技能","tokens":18048988,"share":0.21238270335017922}],"byCategoryDetail":[{"key":"tool_result","label":"工具返回","tokens":21710875,"share":0.2554721910678794,"children":[{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":10181189,"share":0.11980220055947169,"catShare":0.46894419333351256,"trips":34513},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/tasks/TASK-013.md","kind":"read","tokens":5073946,"share":0.05970520016319196,"catShare":0.23370528085120695,"trips":898},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/viewmodels/workbench/viewmodel.py","kind":"read","tokens":957281,"share":0.0112643352741752,"catShare":0.044092216953594957,"trips":882},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/qml/workbench/WorkbenchView.qml","kind":"read","tokens":627346,"share":0.007381992993359697,"catShare":0.028895485502757872,"trips":212},{"tool":"Read","label":"doc/STATUS.md","kind":"read","tokens":454993,"share":0.0053539050990682275,"catShare":0.020956899757616616,"trips":76},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/workbench_helpers.py","kind":"read","tokens":432432,"share":0.005088432643378618,"catShare":0.019917755518159753,"trips":216},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/handoffs/T1.1.2-qoder-release-b985d9c.md","kind":"read","tokens":398883,"share":0.004693664476607124,"catShare":0.01837250644380315,"trips":229},{"tool":"Grep","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/doc/design/ui-reference.html","kind":"search","tokens":393226,"share":0.004627099927303476,"catShare":0.018111951472925866,"trips":656},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/STATUS.md","kind":"read","tokens":273123,"share":0.0032138437615453065,"catShare":0.012580014083377798,"trips":229},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/qml/workbench/ViewerPanel.qml","kind":"read","tokens":266308,"share":0.0031336553869193203,"catShare":0.012266131095602114,"trips":213},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/RegionInspector.qml","kind":"read","tokens":258664,"share":0.0030437051480426713,"catShare":0.011914037043796887,"trips":182},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_tokens.py","kind":"read","tokens":208524,"share":0.002453706388927813,"catShare":0.009604592886103441,"trips":110},{"tool":"Grep","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml","kind":"search","tokens":161652,"share":0.0019021588590261188,"catShare":0.007445659157950041,"trips":219},{"tool":"Read","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/shared-worktree-overwrite-hazard.md","kind":"read","tokens":151185,"share":0.0017789926620587228,"catShare":0.006963547204971682,"trips":222},{"tool":"Read","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/verification-environment.md","kind":"read","tokens":144449,"share":0.0016997306127590774,"catShare":0.006653290151284827,"trips":222},{"tool":null,"label":"其他 87 项","kind":null,"tokens":1727674,"share":0.020329567112055042,"catShare":0.07957643854337729,"trips":30340}]},{"key":"system","label":"系统提示词","tokens":9090300,"share":0.10696569380989837,"children":[]},{"key":"compact_summary","label":"压缩摘要","tokens":1243628,"share":0.014633784544951203,"children":[]},{"key":"assistant_thinking","label":"模型思考","tokens":17771291,"share":0.20911504543712478,"children":[]},{"key":"assistant_tool_use","label":"工具调用","tokens":13422790,"share":0.15794616283099971,"children":[{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":4111436,"share":0.04837932321300726,"catShare":0.30630261822044064,"trips":34513},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_workbench_viewmodel.py","kind":"write","tokens":740369,"share":0.008711937047684843,"catShare":0.05515763657396666,"trips":1135},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_qml_workbench.py","kind":"write","tokens":636985,"share":0.007495409417411315,"catShare":0.04745547016188866,"trips":1759},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/viewmodels/workbench/viewmodel.py","kind":"write","tokens":547801,"share":0.006445986204119428,"catShare":0.04081128714102759,"trips":1677},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_f_applied.py","kind":"write","tokens":466298,"share":0.0054869297890865875,"catShare":0.03473924083206459,"trips":1661},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/qml/workbench/RegionOverlay.qml","kind":"write","tokens":441752,"share":0.005198105210368813,"catShare":0.032910614080132586,"trips":155},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_f_applied.py","kind":"write","tokens":432543,"share":0.00508974520245323,"catShare":0.03222455747721576,"trips":99},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/handoffs/TASK-013-t112-region-canvas.md","kind":"write","tokens":421961,"share":0.004965217822319039,"catShare":0.03143614085536067,"trips":95},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_region_create_persistence.py","kind":"write","tokens":365878,"share":0.004305295699750917,"catShare":0.027257994892585808,"trips":167},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_tokens.py","kind":"write","tokens":290089,"share":0.0034134821677275274,"catShare":0.02161168151568144,"trips":167},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_region_canvas.py","kind":"write","tokens":290023,"share":0.003412704666970127,"catShare":0.021606758947488175,"trips":208},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/RegionInspector.qml","kind":"write","tokens":277263,"share":0.0032625552997433364,"catShare":0.020656122575350103,"trips":1247},{"tool":"Write","label":"C:/Users/49745/AppData/Local/Temp/t112_mutate.py","kind":"write","tokens":274588,"share":0.003231078738562744,"catShare":0.020456835928454653,"trips":134},{"tool":"Edit","label":"C:/Users/49745/AppData/Local/Temp/t112_mutate.py","kind":"write","tokens":268464,"share":0.003159022743933749,"catShare":0.020000629881169452,"trips":835},{"tool":"Edit","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/ViewerPanel.qml","kind":"write","tokens":268228,"share":0.0031562485507525486,"catShare":0.019983065711635502,"trips":1780},{"tool":null,"label":"其他 87 项","kind":null,"tokens":3589111,"share":0.042233121057107734,"catShare":0.2673893452055344,"trips":23787}]},{"key":"assistant_text","label":"模型回复","tokens":1028737,"share":0.012105168042934409,"children":[]},{"key":"user_input","label":"用户输入","tokens":2666713,"share":0.03137925091602665,"children":[]},{"key":"attachment","label":"附件/技能","tokens":18048988,"share":0.21238270335017922,"children":[]}],"byTool":[{"tool":"Bash","tokens":14292625,"calls":292,"perCall":48947,"share":0.1681815237724797},{"tool":"Read","tokens":10117387,"calls":38,"perCall":266247,"share":0.11905144322418384},{"tool":"Edit","tokens":6456609,"calls":182,"perCall":35476,"share":0.07597501487064982},{"tool":"Write","tokens":3424325,"calls":21,"perCall":163063,"share":0.04029408199123878},{"tool":"Grep","tokens":598957,"calls":4,"perCall":149739,"share":0.007047933032879396},{"tool":"TaskCreate","tokens":174788,"calls":14,"perCall":12485,"share":0.0020567387601245967},{"tool":"TaskUpdate","tokens":62519,"calls":26,"perCall":2405,"share":0.0007356646307716543},{"tool":"Skill","tokens":6455,"calls":1,"perCall":6455,"share":0.00007595361656160078}],"byFile":[{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\doc\\tasks\\TASK-013.md","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/tasks/TASK-013.md","kind":"read","tool":"Read","selfTokens":20196,"reads":4,"trips":1796,"billed":5102208,"perRead":1275552,"share":0.06003775931196632},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\src\\ui\\viewmodels\\workbench\\viewmodel.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/viewmodels/workbench/viewmodel.py","kind":"read","tool":"Read","selfTokens":6929,"reads":13,"trips":5118,"billed":1596996,"perRead":122846,"share":0.018791873867051535},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\tests\\ui_shell\\test_design_f_applied.py","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_f_applied.py","kind":"write","tool":"Write","selfTokens":11088,"reads":21,"trips":3520,"billed":990292,"perRead":47157,"share":0.011652779463908145},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\tests\\workbench\\test_workbench_viewmodel.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_workbench_viewmodel.py","kind":"write","tool":"Edit","selfTokens":3732,"reads":6,"trips":2270,"billed":782242,"perRead":130374,"share":0.009204648934973622},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\tests\\workbench\\workbench_helpers.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/workbench_helpers.py","kind":"read","tool":"Read","selfTokens":3139,"reads":4,"trips":1600,"billed":728007,"perRead":182002,"share":0.008566471624000432},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\tests\\workbench\\test_qml_workbench.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_qml_workbench.py","kind":"write","tool":"Edit","selfTokens":4221,"reads":12,"trips":3518,"billed":697522,"perRead":58127,"share":0.008207756719084592},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\src\\ui\\qml\\workbench\\RegionOverlay.qml","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/qml/workbench/RegionOverlay.qml","kind":"write","tool":"Write","selfTokens":4025,"reads":2,"trips":610,"billed":685111,"perRead":342556,"share":0.008061715808690478},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\src\\ui\\qml\\workbench\\WorkbenchView.qml","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/qml/workbench/WorkbenchView.qml","kind":"read","tool":"Read","selfTokens":2944,"reads":2,"trips":728,"billed":680973,"perRead":340487,"share":0.008013024480033942},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\RegionInspector.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/RegionInspector.qml","kind":"read","tool":"Read","selfTokens":3394,"reads":8,"trips":2858,"billed":604089,"perRead":75511,"share":0.0071083215908322546},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\tests\\ui_shell\\test_design_tokens.py","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_tokens.py","kind":"write","tool":"Write","selfTokens":8418,"reads":7,"trips":826,"billed":595597,"perRead":85085,"share":0.007008402813918936},{"attr":"file:C:\\Users\\49745\\AppData\\Local\\Temp\\t112_mutate.py","label":"C:/Users/49745/AppData/Local/Temp/t112_mutate.py","kind":"write","tool":"Write","selfTokens":4145,"reads":8,"trips":1938,"billed":583909,"perRead":72989,"share":0.006870861648688338},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\src\\ui\\viewmodels\\workbench\\region_canvas.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/viewmodels/workbench/region_canvas.py","kind":"write","tool":"Write","selfTokens":3611,"reads":8,"trips":1976,"billed":547388,"perRead":68423,"share":0.006441118826382254},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\doc\\handoffs\\TASK-013-t112-region-canvas.md","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/handoffs/TASK-013-t112-region-canvas.md","kind":"write","tool":"Write","selfTokens":4579,"reads":3,"trips":540,"billed":476229,"perRead":158743,"share":0.005603790483305031},{"attr":"file:G:\\CODEX\\New Manga\\doc\\STATUS.md","label":"doc/STATUS.md","kind":"read","tool":"Read","selfTokens":5440,"reads":1,"trips":152,"billed":456083,"perRead":456083,"share":0.005366730005330966},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\doc\\handoffs\\T1.1.2-qoder-release-b985d9c.md","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/handoffs/T1.1.2-qoder-release-b985d9c.md","kind":"read","tool":"Read","selfTokens":1955,"reads":3,"trips":828,"billed":444318,"perRead":148106,"share":0.005228292614297463},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\tests\\workbench\\test_region_canvas.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_region_canvas.py","kind":"write","tool":"Write","selfTokens":2404,"reads":4,"trips":1104,"billed":441050,"perRead":110262,"share":0.005189840951309711},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\tests\\workbench\\test_region_create_persistence.py","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/tests/workbench/test_region_create_persistence.py","kind":"write","tool":"Write","selfTokens":2343,"reads":3,"trips":996,"billed":434964,"perRead":144988,"share":0.005118227380065658},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\doc\\design\\ui-reference.html","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/doc/design/ui-reference.html","kind":"search","tool":"Grep","selfTokens":1956,"reads":3,"trips":1312,"billed":426644,"perRead":142215,"share":0.005020328973190717},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\src\\ui\\qml\\workbench\\ViewerPanel.qml","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/src/ui/qml/workbench/ViewerPanel.qml","kind":"read","tool":"Read","selfTokens":1723,"reads":3,"trips":1040,"billed":371797,"perRead":123932,"share":0.004374938421114098},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\ViewerPanel.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/ViewerPanel.qml","kind":"write","tool":"Edit","selfTokens":1674,"reads":9,"trips":3560,"billed":326564,"perRead":36285,"share":0.0038426869325777035},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\doc\\STATUS.md","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/STATUS.md","kind":"read","tool":"Read","selfTokens":1081,"reads":1,"trips":458,"billed":278010,"perRead":278010,"share":0.003271341907938299},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\WorkbenchToolbar.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/WorkbenchToolbar.qml","kind":"read","tool":"Read","selfTokens":1604,"reads":3,"trips":934,"billed":248021,"perRead":82674,"share":0.002918466962041972},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\RegionOverlay.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/RegionOverlay.qml","kind":"write","tool":"Edit","selfTokens":1898,"reads":8,"trips":2446,"billed":235419,"perRead":29427,"share":0.0027701753909043225},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\doc\\handoffs\\T2.1.1-qoder-handoff.md","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/doc/handoffs/T2.1.1-qoder-handoff.md","kind":"write","tool":"Write","selfTokens":8597,"reads":15,"trips":662,"billed":234777,"perRead":15652,"share":0.0027626201992486544},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\Main.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/Main.qml","kind":"read","tool":"Read","selfTokens":1365,"reads":4,"trips":1150,"billed":194331,"perRead":48583,"share":0.0022866931563874267},{"attr":"file:C:\\Users\\49745\\AppData\\Local\\Temp\\t112_regress.py","label":"C:/Users/49745/AppData/Local/Temp/t112_regress.py","kind":"write","tool":"Write","selfTokens":1367,"reads":2,"trips":476,"billed":185304,"perRead":92652,"share":0.0021804763204974612},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml","kind":"search","tool":"Grep","selfTokens":792,"reads":1,"trips":438,"billed":172313,"perRead":172313,"share":0.002027604059688675},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\TaskProgressPanel.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/TaskProgressPanel.qml","kind":"read","tool":"Read","selfTokens":7289,"reads":12,"trips":1410,"billed":170407,"perRead":14201,"share":0.002005180856784424},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\shared-worktree-overwrite-hazard.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/shared-worktree-overwrite-hazard.md","kind":"read","tool":"Read","selfTokens":636,"reads":1,"trips":444,"billed":158669,"perRead":158669,"share":0.0018670616057249948},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\verification-environment.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/verification-environment.md","kind":"read","tool":"Read","selfTokens":607,"reads":1,"trips":444,"billed":151434,"perRead":151434,"share":0.001781928293514265},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\bookshelf\\BookCard.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/bookshelf/BookCard.qml","kind":"read","tool":"Read","selfTokens":2103,"reads":3,"trips":536,"billed":117946,"perRead":39315,"share":0.0013878729918640413},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\common\\EmptyState.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/common/EmptyState.qml","kind":"read","tool":"Read","selfTokens":780,"reads":2,"trips":578,"billed":110135,"perRead":55067,"share":0.0012959567996528195},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\WorkbenchView.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/WorkbenchView.qml","kind":"write","tool":"Edit","selfTokens":775,"reads":7,"trips":2048,"billed":107925,"perRead":15418,"share":0.0012699594158079321},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\shell\\AppShell.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/shell/AppShell.qml","kind":"read","tool":"Read","selfTokens":713,"reads":3,"trips":858,"billed":101832,"perRead":33944,"share":0.0011982534898116565},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\windows\\ExportWindow.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/windows/ExportWindow.qml","kind":"write","tool":"Edit","selfTokens":772,"reads":3,"trips":778,"billed":99319,"perRead":33106,"share":0.0011686912179787227},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\shell\\NavBadge.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/shell/NavBadge.qml","kind":"read","tool":"Read","selfTokens":697,"reads":3,"trips":862,"billed":98919,"perRead":32973,"share":0.0011639842806196055},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\shell\\PrimaryNavigationRail.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/shell/PrimaryNavigationRail.qml","kind":"read","tool":"Read","selfTokens":662,"reads":3,"trips":856,"billed":95022,"perRead":31674,"share":0.0011181310047833062},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\verification\\T2.1.1\\generate_tokens.py","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/verification/T2.1.1/generate_tokens.py","kind":"write","tool":"Write","selfTokens":1820,"reads":2,"trips":158,"billed":79261,"perRead":39630,"share":0.0009326595838643778},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\common\\CanvasCaption.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/common/CanvasCaption.qml","kind":"write","tool":"Write","selfTokens":377,"reads":2,"trips":806,"billed":75536,"perRead":37768,"share":0.0008888365807164157},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\MEMORY.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"read","tool":"Read","selfTokens":1547,"reads":4,"trips":350,"billed":72945,"perRead":18236,"share":0.0008583455400281716},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\bookshelf\\ChapterList.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/bookshelf/ChapterList.qml","kind":"read","tool":"Read","selfTokens":2386,"reads":3,"trips":156,"billed":68294,"perRead":22765,"share":0.0008036113618086222},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\reader\\ReaderView.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/reader/ReaderView.qml","kind":"write","tool":"Edit","selfTokens":481,"reads":5,"trips":1354,"billed":64541,"perRead":12908,"share":0.0007594506392565993},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\workbench\\PageListPanel.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/workbench/PageListPanel.qml","kind":"write","tool":"Edit","selfTokens":2237,"reads":6,"trips":848,"billed":55453,"perRead":9242,"share":0.0006525107765368276},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\bookshelf\\BookGrid.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/bookshelf/BookGrid.qml","kind":"read","tool":"Read","selfTokens":1645,"reads":2,"trips":116,"billed":51381,"perRead":25691,"share":0.0006046031881796805},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T1.1.2-qoder\\doc\\templates\\HANDOFF.md","label":"G:/CODEX/New Manga.worktrees/T1.1.2-qoder/doc/templates/HANDOFF.md","kind":"read","tool":"Read","selfTokens":474,"reads":1,"trips":196,"billed":51324,"perRead":51324,"share":0.0006039352186975987},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\bookshelf\\BookDetailPanel.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/bookshelf/BookDetailPanel.qml","kind":"read","tool":"Read","selfTokens":2270,"reads":3,"trips":120,"billed":49942,"perRead":16647,"share":0.0005876713286091501},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\windows-crlf-byte-exact-rewrite.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/windows-crlf-byte-exact-rewrite.md","kind":"write","tool":"Write","selfTokens":1348,"reads":3,"trips":190,"billed":48294,"perRead":16098,"share":0.0005682777894964069},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\memory\\MEMORY.md","label":"C:/Users/49745/.qoder-cn/memory/MEMORY.md","kind":"read","tool":"Read","selfTokens":581,"reads":2,"trips":262,"billed":42090,"perRead":21045,"share":0.000495275478584004},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\git-diff-check-scope-for-evidence-logs.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/git-diff-check-scope-for-evidence-logs.md","kind":"write","tool":"Write","selfTokens":437,"reads":1,"trips":164,"billed":39551,"perRead":39551,"share":0.00046540259386788007},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\memory\\copyable-instructions.md","label":"C:/Users/49745/.qoder-cn/memory/copyable-instructions.md","kind":"write","tool":"Write","selfTokens":476,"reads":1,"trips":134,"billed":35089,"perRead":35089,"share":0.000412890542855503},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\doc\\templates\\HANDOFF.md","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/doc/templates/HANDOFF.md","kind":"read","tool":"Read","selfTokens":663,"reads":1,"trips":100,"billed":33219,"perRead":33219,"share":0.00039088531483375596},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\verification\\T2.1.1\\mutation-discrimination-bc49ef9.md","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/verification/T2.1.1/mutation-discrimination-bc49ef9.md","kind":"write","tool":"Write","selfTokens":1025,"reads":2,"trips":110,"billed":32258,"perRead":16129,"share":0.0003795845448464022},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\bookshelf\\BookshelfView.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/bookshelf/BookshelfView.qml","kind":"write","tool":"Edit","selfTokens":584,"reads":4,"trips":178,"billed":14207,"perRead":3552,"share":0.00016717144205752378},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\tests\\workbench\\test_qml_workbench.py","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/tests/workbench/test_qml_workbench.py","kind":"write","tool":"Edit","selfTokens":178,"reads":1,"trips":154,"billed":13670,"perRead":13670,"share":0.00016085239110798526},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\memory\\feedback-copyable-instructions.md","label":"C:/Users/49745/.qoder-cn/memory/feedback-copyable-instructions.md","kind":"write","tool":"Edit","selfTokens":180,"reads":1,"trips":130,"billed":12866,"perRead":12866,"share":0.00015139057726517725},{"attr":"file:G:\\CODEX.New Manga.worktrees\\T2.1.1-design-f-qml\\tests\\ui_shell\\test_design_tokens.py","label":"G:/CODEX.New Manga.worktrees/T2.1.1-design-f-qml/tests/ui_shell/test_design_tokens.py","kind":"write","tool":"Edit","selfTokens":209,"reads":1,"trips":94,"billed":10745,"perRead":10745,"share":0.00012643253132456797},{"attr":"file:G:\\CODEX\\New Manga.worktrees\\T2.1.1-design-f-qml\\src\\ui\\qml\\bookshelf\\BookshelfToolbar.qml","label":"G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml/src/ui/qml/bookshelf/BookshelfToolbar.qml","kind":"write","tool":"Edit","selfTokens":263,"reads":1,"trips":42,"billed":5996,"perRead":5996,"share":0.00007055266358775198},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\t211-delivery-state.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/t211-delivery-state.md","kind":"write","tool":"Write","selfTokens":787,"reads":2,"trips":24,"billed":5965,"perRead":2983,"share":0.00007019157328514485},{"attr":"file:C:\\Users\\49745\\AppData\\Local\\Temp\\qoder-cli-cn\\G--CODEX-New-Manga\\abab2d9a-d09a-4b0a-b85c-cef2a68c2c70\\tasks\\bbu6tl5s2.output","label":"C:/Users/49745/AppData/Local/Temp/qoder-cli-cn/G--CODEX-New-Manga/abab2d9a-d09a-4b0a-b85c-cef2a68c2c70/tasks/bbu6tl5s2.output","kind":"read","tool":"Read","selfTokens":60,"reads":1,"trips":96,"billed":2887,"perRead":2887,"share":0.000033972654171889516}],"byAttr":[{"attr":"attachment","tokens":18048988,"share":0.21238270335017922},{"attr":"assistant_thinking","tokens":17771291,"share":0.20911504543712478},{"attr":"tool_result|Bash","tokens":10181189,"share":0.11980220055947169},{"attr":"tool_result|Read","tokens":9963020,"share":0.11723500547660344},{"attr":"system","tokens":9090300,"share":0.10696569380989837},{"attr":"tool_use|Edit","tokens":5573052,"share":0.06557818867019918},{"attr":"tool_use|Bash","tokens":4111436,"share":0.04837932321300726},{"attr":"tool_use|Write","tokens":3364843,"share":0.03959416039141966},{"attr":"user_input","tokens":2666713,"share":0.03137925091602665},{"attr":"compact_summary","tokens":1243628,"share":0.014633784544951203},{"attr":"assistant_text","tokens":1028737,"share":0.012105168042934409},{"attr":"tool_result|Edit","tokens":883557,"share":0.010396826200450618},{"attr":"tool_result|Grep","tokens":554878,"share":0.006529258786329591},{"attr":"tool_use|Read","tokens":154367,"share":0.0018164377475810554},{"attr":"tool_use|TaskCreate","tokens":134194,"share":0.0015790583802850373},{"attr":"tool_result|Write","tokens":59482,"share":0.0006999215998191998},{"attr":"tool_use|Grep","tokens":44079,"share":0.0005186742465498013},{"attr":"tool_result|TaskCreate","tokens":40595,"share":0.00047768037983956125},{"attr":"tool_use|TaskUpdate","tokens":37721,"share":0.0004438624460076957},{"attr":"tool_result|TaskUpdate","tokens":24798,"share":0.0002918021847639538},{"attr":"tool_result|Skill","tokens":3356,"share":0.00003949588061203236},{"attr":"tool_use|Skill","tokens":3098,"share":0.00003645773594956834}],"byRequest":[{"index":1,"time":"15:39","ratio":0.086888,"inputTokens":34755,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.986,"originalCredits":0.986,"afterCompact":false},{"index":2,"time":"15:40","ratio":0.09426,"inputTokens":37704,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.173,"originalCredits":0.173,"afterCompact":false},{"index":3,"time":"15:40","ratio":0.102955,"inputTokens":41182,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.198,"originalCredits":0.198,"afterCompact":false},{"index":4,"time":"15:40","ratio":0.104725,"inputTokens":41890,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.123,"originalCredits":0.123,"afterCompact":false},{"index":5,"time":"15:40","ratio":0.10691,"inputTokens":42764,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.127,"originalCredits":0.127,"afterCompact":false},{"index":6,"time":"15:40","ratio":0.130123,"inputTokens":52049,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.364,"originalCredits":0.364,"afterCompact":false},{"index":7,"time":"15:40","ratio":0.14446,"inputTokens":57784,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.28,"originalCredits":0.28,"afterCompact":false},{"index":8,"time":"15:40","ratio":0.156977,"inputTokens":62791,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.274,"originalCredits":0.274,"afterCompact":false},{"index":9,"time":"15:41","ratio":0.171245,"inputTokens":68498,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.352,"originalCredits":0.352,"afterCompact":false},{"index":10,"time":"15:41","ratio":0.179975,"inputTokens":71990,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.263,"originalCredits":0.263,"afterCompact":false},{"index":11,"time":"15:41","ratio":0.183367,"inputTokens":73347,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.219,"originalCredits":0.219,"afterCompact":false},{"index":12,"time":"15:42","ratio":0.192018,"inputTokens":76807,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.363,"originalCredits":0.363,"afterCompact":false},{"index":13,"time":"15:42","ratio":0.19677,"inputTokens":78708,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.239,"originalCredits":0.239,"afterCompact":false},{"index":14,"time":"15:42","ratio":0.201805,"inputTokens":80722,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.245,"originalCredits":0.245,"afterCompact":false},{"index":15,"time":"15:42","ratio":0.20489,"inputTokens":81956,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.224,"originalCredits":0.224,"afterCompact":false},{"index":16,"time":"15:42","ratio":0.210778,"inputTokens":84311,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.261,"originalCredits":0.261,"afterCompact":false},{"index":17,"time":"15:42","ratio":0.213105,"inputTokens":85242,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.223,"originalCredits":0.223,"afterCompact":false},{"index":18,"time":"15:43","ratio":0.216902,"inputTokens":86761,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.247,"originalCredits":0.247,"afterCompact":false},{"index":19,"time":"15:43","ratio":0.22045,"inputTokens":88180,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.251,"originalCredits":0.251,"afterCompact":false},{"index":20,"time":"15:43","ratio":0.228258,"inputTokens":91303,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.39,"originalCredits":0.39,"afterCompact":false},{"index":21,"time":"15:43","ratio":0.235645,"inputTokens":94258,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.308,"originalCredits":0.308,"afterCompact":false},{"index":22,"time":"15:44","ratio":0.23689,"inputTokens":94756,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.236,"originalCredits":0.236,"afterCompact":false},{"index":23,"time":"15:45","ratio":0.237575,"inputTokens":95030,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.539,"originalCredits":0.539,"afterCompact":false},{"index":24,"time":"15:45","ratio":0.251095,"inputTokens":100438,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.377,"originalCredits":0.377,"afterCompact":false},{"index":25,"time":"15:45","ratio":0.25227,"inputTokens":100908,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.307,"originalCredits":0.307,"afterCompact":false},{"index":26,"time":"15:45","ratio":0.255365,"inputTokens":102146,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.273,"originalCredits":0.273,"afterCompact":false},{"index":27,"time":"15:46","ratio":0.256105,"inputTokens":102442,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.262,"originalCredits":0.262,"afterCompact":false},{"index":28,"time":"15:46","ratio":0.257427,"inputTokens":102971,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.251,"originalCredits":0.251,"afterCompact":false},{"index":29,"time":"15:46","ratio":0.258153,"inputTokens":103261,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.318,"originalCredits":0.318,"afterCompact":false},{"index":30,"time":"15:47","ratio":0.263735,"inputTokens":105494,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.334,"originalCredits":0.334,"afterCompact":false},{"index":31,"time":"15:47","ratio":0.265738,"inputTokens":106295,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.273,"originalCredits":0.273,"afterCompact":false},{"index":32,"time":"15:47","ratio":0.266565,"inputTokens":106626,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.306,"originalCredits":0.306,"afterCompact":false},{"index":33,"time":"15:47","ratio":0.26921,"inputTokens":107684,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.283,"originalCredits":0.283,"afterCompact":false},{"index":34,"time":"15:47","ratio":0.270827,"inputTokens":108331,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.277,"originalCredits":0.277,"afterCompact":false},{"index":35,"time":"15:47","ratio":0.2718,"inputTokens":108720,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.275,"originalCredits":0.275,"afterCompact":false},{"index":36,"time":"15:48","ratio":0.272917,"inputTokens":109167,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.276,"originalCredits":0.276,"afterCompact":false},{"index":37,"time":"15:48","ratio":0.273958,"inputTokens":109583,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.269,"originalCredits":0.269,"afterCompact":false},{"index":38,"time":"15:48","ratio":0.274725,"inputTokens":109890,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.263,"originalCredits":0.263,"afterCompact":false},{"index":39,"time":"15:49","ratio":0.275832,"inputTokens":110333,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.345,"originalCredits":0.345,"afterCompact":false},{"index":40,"time":"15:49","ratio":0.279747,"inputTokens":111899,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.322,"originalCredits":0.322,"afterCompact":false},{"index":41,"time":"15:49","ratio":0.28132,"inputTokens":112528,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.282,"originalCredits":0.282,"afterCompact":false},{"index":42,"time":"15:49","ratio":0.282112,"inputTokens":112845,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.348,"originalCredits":0.348,"afterCompact":false},{"index":43,"time":"15:50","ratio":0.28594,"inputTokens":114376,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.315,"originalCredits":0.315,"afterCompact":false},{"index":44,"time":"15:50","ratio":0.28746,"inputTokens":114984,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.303,"originalCredits":0.303,"afterCompact":false},{"index":45,"time":"15:50","ratio":0.288932,"inputTokens":115573,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.295,"originalCredits":0.295,"afterCompact":false},{"index":46,"time":"15:51","ratio":0.290042,"inputTokens":116017,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.338,"originalCredits":0.338,"afterCompact":false},{"index":47,"time":"15:51","ratio":0.293065,"inputTokens":117226,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.308,"originalCredits":0.308,"afterCompact":false},{"index":48,"time":"15:51","ratio":0.29448,"inputTokens":117792,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.286,"originalCredits":0.286,"afterCompact":false},{"index":49,"time":"15:52","ratio":0.294973,"inputTokens":117989,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.349,"originalCredits":0.349,"afterCompact":false},{"index":50,"time":"15:52","ratio":0.298582,"inputTokens":119433,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.32,"originalCredits":0.32,"afterCompact":false},{"index":51,"time":"15:52","ratio":0.299733,"inputTokens":119893,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.295,"originalCredits":0.295,"afterCompact":false},{"index":52,"time":"15:52","ratio":0.300555,"inputTokens":120222,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.285,"originalCredits":0.285,"afterCompact":false},{"index":53,"time":"15:52","ratio":0.301353,"inputTokens":120541,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.306,"originalCredits":0.306,"afterCompact":false},{"index":54,"time":"15:52","ratio":0.302745,"inputTokens":121098,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.299,"originalCredits":0.299,"afterCompact":false},{"index":55,"time":"15:53","ratio":0.303567,"inputTokens":121427,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.287,"originalCredits":0.287,"afterCompact":false},{"index":56,"time":"15:53","ratio":0.304013,"inputTokens":121605,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.332,"originalCredits":0.332,"afterCompact":false},{"index":57,"time":"15:53","ratio":0.30657,"inputTokens":122628,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.31,"originalCredits":0.31,"afterCompact":false},{"index":58,"time":"15:53","ratio":0.307495,"inputTokens":122998,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.317,"originalCredits":0.317,"afterCompact":false},{"index":59,"time":"15:53","ratio":0.309053,"inputTokens":123621,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.308,"originalCredits":0.308,"afterCompact":false},{"index":60,"time":"15:54","ratio":0.309968,"inputTokens":123987,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.306,"originalCredits":0.306,"afterCompact":false},{"index":61,"time":"15:54","ratio":0.312412,"inputTokens":124965,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.327,"originalCredits":0.327,"afterCompact":false},{"index":62,"time":"15:54","ratio":0.316173,"inputTokens":126469,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.399,"originalCredits":0.399,"afterCompact":false},{"index":63,"time":"15:54","ratio":0.31984,"inputTokens":127936,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.33,"originalCredits":0.33,"afterCompact":false},{"index":64,"time":"15:55","ratio":0.321985,"inputTokens":128794,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.525,"originalCredits":0.525,"afterCompact":false},{"index":65,"time":"15:55","ratio":0.331203,"inputTokens":132481,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.447,"originalCredits":0.447,"afterCompact":false},{"index":66,"time":"15:55","ratio":0.333815,"inputTokens":133526,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.343,"originalCredits":0.343,"afterCompact":false},{"index":67,"time":"15:56","ratio":0.334782,"inputTokens":133913,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.32,"originalCredits":0.32,"afterCompact":false},{"index":68,"time":"15:56","ratio":0.335437,"inputTokens":134175,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.328,"originalCredits":0.328,"afterCompact":false},{"index":69,"time":"15:56","ratio":0.33667,"inputTokens":134668,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.318,"originalCredits":0.318,"afterCompact":false},{"index":70,"time":"15:56","ratio":0.337473,"inputTokens":134989,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.372,"originalCredits":0.372,"afterCompact":false},{"index":71,"time":"15:56","ratio":0.340813,"inputTokens":136325,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.381,"originalCredits":0.381,"afterCompact":false},{"index":72,"time":"15:57","ratio":0.343365,"inputTokens":137346,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.35,"originalCredits":0.35,"afterCompact":false},{"index":73,"time":"15:57","ratio":0.344282,"inputTokens":137713,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.332,"originalCredits":0.332,"afterCompact":false},{"index":74,"time":"15:57","ratio":0.345442,"inputTokens":138177,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.446,"originalCredits":0.446,"afterCompact":false},{"index":75,"time":"15:57","ratio":0.350855,"inputTokens":140342,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.384,"originalCredits":0.384,"afterCompact":false},{"index":76,"time":"15:58","ratio":0.3519,"inputTokens":140760,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.568,"originalCredits":0.568,"afterCompact":false},{"index":77,"time":"15:58","ratio":0.362223,"inputTokens":144889,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.442,"originalCredits":0.442,"afterCompact":false},{"index":78,"time":"15:59","ratio":0.36299,"inputTokens":145196,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.373,"originalCredits":0.373,"afterCompact":false},{"index":79,"time":"15:59","ratio":0.364945,"inputTokens":145978,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.359,"originalCredits":0.359,"afterCompact":false},{"index":80,"time":"15:59","ratio":0.365743,"inputTokens":146297,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.366,"originalCredits":0.366,"afterCompact":false},{"index":81,"time":"16:00","ratio":0.367815,"inputTokens":147126,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.567,"originalCredits":0.567,"afterCompact":false},{"index":82,"time":"16:00","ratio":0.377092,"inputTokens":150837,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.494,"originalCredits":0.494,"afterCompact":false},{"index":83,"time":"16:01","ratio":0.380163,"inputTokens":152065,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.516,"originalCredits":0.516,"afterCompact":false},{"index":84,"time":"16:01","ratio":0.386425,"inputTokens":154570,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.434,"originalCredits":0.434,"afterCompact":false},{"index":85,"time":"16:02","ratio":0.38766,"inputTokens":155064,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.551,"originalCredits":0.551,"afterCompact":false},{"index":86,"time":"16:02","ratio":0.39588,"inputTokens":158352,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.466,"originalCredits":0.466,"afterCompact":false},{"index":87,"time":"16:02","ratio":0.398365,"inputTokens":159346,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.432,"originalCredits":0.432,"afterCompact":false},{"index":88,"time":"16:02","ratio":0.401593,"inputTokens":160637,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.425,"originalCredits":0.425,"afterCompact":false},{"index":89,"time":"16:03","ratio":0.403197,"inputTokens":161279,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.416,"originalCredits":0.416,"afterCompact":false},{"index":90,"time":"16:03","ratio":0.405055,"inputTokens":162022,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.4,"originalCredits":0.4,"afterCompact":false},{"index":91,"time":"16:03","ratio":0.40605,"inputTokens":162420,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.435,"originalCredits":0.435,"afterCompact":false},{"index":92,"time":"16:03","ratio":0.408853,"inputTokens":163541,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.405,"originalCredits":0.405,"afterCompact":false},{"index":93,"time":"16:03","ratio":0.40953,"inputTokens":163812,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.382,"originalCredits":0.382,"afterCompact":false},{"index":94,"time":"16:04","ratio":0.410923,"inputTokens":164369,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.418,"originalCredits":0.418,"afterCompact":false},{"index":95,"time":"16:04","ratio":0.41325,"inputTokens":165300,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.402,"originalCredits":0.402,"afterCompact":false},{"index":96,"time":"16:04","ratio":0.413847,"inputTokens":165539,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.387,"originalCredits":0.387,"afterCompact":false},{"index":97,"time":"16:05","ratio":0.414595,"inputTokens":165838,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.648,"originalCredits":0.648,"afterCompact":false},{"index":98,"time":"16:05","ratio":0.426013,"inputTokens":170405,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.507,"originalCredits":0.507,"afterCompact":false},{"index":99,"time":"16:05","ratio":0.42712,"inputTokens":170848,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.425,"originalCredits":0.425,"afterCompact":false},{"index":100,"time":"16:06","ratio":0.42928,"inputTokens":171712,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.432,"originalCredits":0.432,"afterCompact":false},{"index":101,"time":"16:06","ratio":0.431145,"inputTokens":172458,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.466,"originalCredits":0.466,"afterCompact":false},{"index":102,"time":"16:06","ratio":0.43396,"inputTokens":173584,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.464,"originalCredits":0.464,"afterCompact":false},{"index":103,"time":"16:07","ratio":0.436185,"inputTokens":174474,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.438,"originalCredits":0.438,"afterCompact":false},{"index":104,"time":"16:07","ratio":0.4375,"inputTokens":175000,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.41,"originalCredits":0.41,"afterCompact":false},{"index":105,"time":"16:07","ratio":0.43795,"inputTokens":175180,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.404,"originalCredits":0.404,"afterCompact":false},{"index":106,"time":"16:07","ratio":0.439595,"inputTokens":175838,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.494,"originalCredits":0.494,"afterCompact":false},{"index":107,"time":"16:08","ratio":0.443292,"inputTokens":177317,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.447,"originalCredits":0.447,"afterCompact":false},{"index":108,"time":"16:35","ratio":0.444493,"inputTokens":177797,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.977,"originalCredits":4.977,"afterCompact":false},{"index":109,"time":"16:35","ratio":0.465143,"inputTokens":186057,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.651,"originalCredits":0.651,"afterCompact":false},{"index":110,"time":"16:36","ratio":0.466832,"inputTokens":186733,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.623,"originalCredits":0.623,"afterCompact":false},{"index":111,"time":"16:36","ratio":0.474935,"inputTokens":189974,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.525,"originalCredits":0.525,"afterCompact":false},{"index":112,"time":"16:36","ratio":0.476102,"inputTokens":190441,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.456,"originalCredits":0.456,"afterCompact":false},{"index":113,"time":"16:36","ratio":0.477162,"inputTokens":190865,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.455,"originalCredits":0.455,"afterCompact":false},{"index":114,"time":"16:36","ratio":0.478195,"inputTokens":191278,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.483,"originalCredits":0.483,"afterCompact":false},{"index":115,"time":"16:37","ratio":0.480355,"inputTokens":192142,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.462,"originalCredits":0.462,"afterCompact":false},{"index":116,"time":"16:37","ratio":0.481652,"inputTokens":192661,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.464,"originalCredits":0.464,"afterCompact":false},{"index":117,"time":"16:37","ratio":0.483812,"inputTokens":193525,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.465,"originalCredits":0.465,"afterCompact":false},{"index":118,"time":"16:38","ratio":0.48449,"inputTokens":193796,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.462,"originalCredits":0.462,"afterCompact":false},{"index":119,"time":"16:38","ratio":0.485645,"inputTokens":194258,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.455,"originalCredits":0.455,"afterCompact":false},{"index":120,"time":"16:39","ratio":0.48673,"inputTokens":194692,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.651,"originalCredits":0.651,"afterCompact":false},{"index":121,"time":"16:39","ratio":0.495563,"inputTokens":198225,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.601,"originalCredits":0.601,"afterCompact":false},{"index":122,"time":"16:39","ratio":0.498677,"inputTokens":199471,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.485,"originalCredits":0.485,"afterCompact":false},{"index":123,"time":"16:39","ratio":0.49927,"inputTokens":199708,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.459,"originalCredits":0.459,"afterCompact":false},{"index":124,"time":"16:39","ratio":0.502543,"inputTokens":201017,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.497,"originalCredits":0.497,"afterCompact":false},{"index":125,"time":"16:40","ratio":0.50338,"inputTokens":201352,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.487,"originalCredits":0.487,"afterCompact":false},{"index":126,"time":"16:40","ratio":0.504822,"inputTokens":201929,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.488,"originalCredits":0.488,"afterCompact":false},{"index":127,"time":"16:40","ratio":0.505997,"inputTokens":202399,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.484,"originalCredits":0.484,"afterCompact":false},{"index":128,"time":"16:41","ratio":0.507088,"inputTokens":202835,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.482,"originalCredits":0.482,"afterCompact":false},{"index":129,"time":"16:41","ratio":0.508065,"inputTokens":203226,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.473,"originalCredits":0.473,"afterCompact":false},{"index":130,"time":"16:41","ratio":0.50876,"inputTokens":203504,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.475,"originalCredits":0.475,"afterCompact":false},{"index":131,"time":"16:41","ratio":0.509563,"inputTokens":203825,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.481,"originalCredits":0.481,"afterCompact":false},{"index":132,"time":"16:41","ratio":0.511545,"inputTokens":204618,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.487,"originalCredits":0.487,"afterCompact":false},{"index":133,"time":"17:05","ratio":0.512602,"inputTokens":205041,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.714,"originalCredits":5.714,"afterCompact":false},{"index":134,"time":"17:05","ratio":0.51585,"inputTokens":206340,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.515,"originalCredits":0.515,"afterCompact":false},{"index":135,"time":"17:06","ratio":0.51709,"inputTokens":206836,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.49,"originalCredits":0.49,"afterCompact":false},{"index":136,"time":"17:07","ratio":0.517975,"inputTokens":207190,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.78,"originalCredits":0.78,"afterCompact":false},{"index":137,"time":"17:07","ratio":0.531645,"inputTokens":212658,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.667,"originalCredits":0.667,"afterCompact":false},{"index":138,"time":"17:07","ratio":0.53511,"inputTokens":214044,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.533,"originalCredits":0.533,"afterCompact":false},{"index":139,"time":"17:07","ratio":0.53622,"inputTokens":214488,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.501,"originalCredits":0.501,"afterCompact":false},{"index":140,"time":"17:08","ratio":0.53697,"inputTokens":214788,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.515,"originalCredits":0.515,"afterCompact":false},{"index":141,"time":"17:08","ratio":0.53981,"inputTokens":215924,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.528,"originalCredits":0.528,"afterCompact":false},{"index":142,"time":"17:08","ratio":0.540715,"inputTokens":216286,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.528,"originalCredits":0.528,"afterCompact":false},{"index":143,"time":"17:08","ratio":0.542485,"inputTokens":216994,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.544,"originalCredits":0.544,"afterCompact":false},{"index":144,"time":"17:10","ratio":0.544628,"inputTokens":217851,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.541,"originalCredits":0.541,"afterCompact":false},{"index":145,"time":"17:11","ratio":0.54683,"inputTokens":218732,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.527,"originalCredits":0.527,"afterCompact":false},{"index":146,"time":"17:11","ratio":0.54778,"inputTokens":219112,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.509,"originalCredits":0.509,"afterCompact":false},{"index":147,"time":"17:11","ratio":0.549382,"inputTokens":219753,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.518,"originalCredits":0.518,"afterCompact":false},{"index":148,"time":"17:11","ratio":0.551485,"inputTokens":220594,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.537,"originalCredits":0.537,"afterCompact":false},{"index":149,"time":"17:12","ratio":0.554028,"inputTokens":221611,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.589,"originalCredits":0.589,"afterCompact":false},{"index":150,"time":"17:12","ratio":0.557218,"inputTokens":222887,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.533,"originalCredits":0.533,"afterCompact":false},{"index":151,"time":"17:12","ratio":0.5584,"inputTokens":223360,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.53,"originalCredits":0.53,"afterCompact":false},{"index":152,"time":"17:12","ratio":0.56113,"inputTokens":224452,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.533,"originalCredits":0.533,"afterCompact":false},{"index":153,"time":"17:13","ratio":0.561453,"inputTokens":224581,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.677,"originalCredits":0.677,"afterCompact":false},{"index":154,"time":"15:47","ratio":0.576115,"inputTokens":230446,"outputTokens":null,"usageSource":"transcript-ratio","credits":6.551,"originalCredits":6.551,"afterCompact":false},{"index":155,"time":"15:48","ratio":0.59809,"inputTokens":239236,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.826,"originalCredits":0.826,"afterCompact":false},{"index":156,"time":"15:48","ratio":0.62073,"inputTokens":248292,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.861,"originalCredits":0.861,"afterCompact":false},{"index":157,"time":"15:48","ratio":0.62904,"inputTokens":251616,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.686,"originalCredits":0.686,"afterCompact":false},{"index":158,"time":"15:49","ratio":0.631898,"inputTokens":252759,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.64,"originalCredits":0.64,"afterCompact":false},{"index":159,"time":"15:49","ratio":0.63886,"inputTokens":255544,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.691,"originalCredits":0.691,"afterCompact":false},{"index":160,"time":"15:49","ratio":0.64192,"inputTokens":256768,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.641,"originalCredits":0.641,"afterCompact":false},{"index":161,"time":"15:50","ratio":0.645455,"inputTokens":258182,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.647,"originalCredits":0.647,"afterCompact":false},{"index":162,"time":"15:50","ratio":0.64848,"inputTokens":259392,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.711,"originalCredits":0.711,"afterCompact":false},{"index":163,"time":"15:51","ratio":0.653317,"inputTokens":261327,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.79,"originalCredits":0.79,"afterCompact":false},{"index":164,"time":"15:54","ratio":0.663898,"inputTokens":265559,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.788,"originalCredits":0.788,"afterCompact":false},{"index":165,"time":"15:54","ratio":0.668432,"inputTokens":267373,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.654,"originalCredits":0.654,"afterCompact":false},{"index":166,"time":"15:54","ratio":0.6691,"inputTokens":267640,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.612,"originalCredits":0.612,"afterCompact":false},{"index":167,"time":"15:54","ratio":0.67025,"inputTokens":268100,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.62,"originalCredits":0.62,"afterCompact":false},{"index":168,"time":"15:55","ratio":0.67177,"inputTokens":268708,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.719,"originalCredits":0.719,"afterCompact":false},{"index":169,"time":"16:23","ratio":0.680647,"inputTokens":272259,"outputTokens":null,"usageSource":"transcript-ratio","credits":7.698,"originalCredits":7.698,"afterCompact":false},{"index":170,"time":"16:23","ratio":0.690418,"inputTokens":276167,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.751,"originalCredits":0.751,"afterCompact":false},{"index":171,"time":"16:24","ratio":0.700135,"inputTokens":280054,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.801,"originalCredits":0.801,"afterCompact":false},{"index":172,"time":"16:24","ratio":0.707015,"inputTokens":282806,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.736,"originalCredits":0.736,"afterCompact":false},{"index":173,"time":"16:25","ratio":0.71071,"inputTokens":284284,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.801,"originalCredits":0.801,"afterCompact":false},{"index":174,"time":"16:27","ratio":0.718155,"inputTokens":287262,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.983,"originalCredits":0.983,"afterCompact":false},{"index":175,"time":"16:27","ratio":0.72948,"inputTokens":291792,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.874,"originalCredits":0.874,"afterCompact":false},{"index":176,"time":"16:28","ratio":0.734187,"inputTokens":293675,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.842,"originalCredits":0.842,"afterCompact":false},{"index":177,"time":"16:29","ratio":0.740285,"inputTokens":296114,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.834,"originalCredits":0.834,"afterCompact":false},{"index":178,"time":"16:29","ratio":0.745147,"inputTokens":298059,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.724,"originalCredits":0.724,"afterCompact":false},{"index":179,"time":"16:29","ratio":0.746672,"inputTokens":298669,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.702,"originalCredits":0.702,"afterCompact":false},{"index":180,"time":"16:30","ratio":0.74777,"inputTokens":299108,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.711,"originalCredits":0.711,"afterCompact":false},{"index":181,"time":"16:30","ratio":0.749305,"inputTokens":299722,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.711,"originalCredits":0.711,"afterCompact":false},{"index":182,"time":"16:30","ratio":0.750637,"inputTokens":300255,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.708,"originalCredits":0.708,"afterCompact":false},{"index":183,"time":"16:30","ratio":0.75198,"inputTokens":300792,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.713,"originalCredits":0.713,"afterCompact":false},{"index":184,"time":"16:31","ratio":0.753875,"inputTokens":301550,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.737,"originalCredits":0.737,"afterCompact":false},{"index":185,"time":"16:31","ratio":0.75691,"inputTokens":302764,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.719,"originalCredits":0.719,"afterCompact":false},{"index":186,"time":"16:32","ratio":0.757725,"inputTokens":303090,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.693,"originalCredits":0.693,"afterCompact":false},{"index":187,"time":"16:33","ratio":0.759082,"inputTokens":303633,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.767,"originalCredits":0.767,"afterCompact":false},{"index":188,"time":"16:34","ratio":0.76253,"inputTokens":305012,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.85,"originalCredits":0.85,"afterCompact":false},{"index":189,"time":"16:34","ratio":0.76875,"inputTokens":307500,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.789,"originalCredits":0.789,"afterCompact":false},{"index":190,"time":"16:34","ratio":0.771015,"inputTokens":308406,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.753,"originalCredits":0.753,"afterCompact":false},{"index":191,"time":"16:35","ratio":0.774175,"inputTokens":309670,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.889,"originalCredits":0.889,"afterCompact":false},{"index":192,"time":"16:35","ratio":0.781353,"inputTokens":312541,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.786,"originalCredits":0.786,"afterCompact":false},{"index":193,"time":"16:36","ratio":0.782295,"inputTokens":312918,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.719,"originalCredits":0.719,"afterCompact":false},{"index":194,"time":"16:36","ratio":0.784277,"inputTokens":313711,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.73,"originalCredits":0.73,"afterCompact":false},{"index":195,"time":"16:36","ratio":0.785602,"inputTokens":314241,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.722,"originalCredits":0.722,"afterCompact":false},{"index":196,"time":"16:37","ratio":0.786675,"inputTokens":314670,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.771,"originalCredits":0.771,"afterCompact":false},{"index":197,"time":"16:37","ratio":0.809662,"inputTokens":323865,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.968,"originalCredits":0.968,"afterCompact":false},{"index":198,"time":"16:37","ratio":0.810368,"inputTokens":324147,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.747,"originalCredits":0.747,"afterCompact":false},{"index":199,"time":"16:38","ratio":0.81142,"inputTokens":324568,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.754,"originalCredits":0.754,"afterCompact":false},{"index":200,"time":"16:38","ratio":0.81275,"inputTokens":325100,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.747,"originalCredits":0.747,"afterCompact":false},{"index":201,"time":"16:39","ratio":0.815512,"inputTokens":326205,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.827,"originalCredits":0.827,"afterCompact":false},{"index":202,"time":"16:40","ratio":0.820865,"inputTokens":328346,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.928,"originalCredits":0.928,"afterCompact":false},{"index":203,"time":"16:40","ratio":0.827963,"inputTokens":331185,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.875,"originalCredits":0.875,"afterCompact":false},{"index":204,"time":"16:41","ratio":0.830895,"inputTokens":332358,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.779,"originalCredits":0.779,"afterCompact":false},{"index":205,"time":"16:42","ratio":0.837228,"inputTokens":334891,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.921,"originalCredits":0.921,"afterCompact":false},{"index":206,"time":"16:42","ratio":0.842032,"inputTokens":336813,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.812,"originalCredits":0.812,"afterCompact":false},{"index":207,"time":"16:43","ratio":0.842827,"inputTokens":337131,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.776,"originalCredits":0.776,"afterCompact":false},{"index":208,"time":"16:43","ratio":0.844325,"inputTokens":337730,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.783,"originalCredits":0.783,"afterCompact":false},{"index":209,"time":"16:44","ratio":0.845175,"inputTokens":338070,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.802,"originalCredits":0.802,"afterCompact":false},{"index":210,"time":"16:44","ratio":0.848245,"inputTokens":339298,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.807,"originalCredits":0.807,"afterCompact":false},{"index":211,"time":"16:44","ratio":0.852387,"inputTokens":340955,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.82,"originalCredits":0.82,"afterCompact":false},{"index":212,"time":"16:45","ratio":0.853387,"inputTokens":341355,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.806,"originalCredits":0.806,"afterCompact":false},{"index":213,"time":"16:45","ratio":0.855105,"inputTokens":342042,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.791,"originalCredits":0.791,"afterCompact":false},{"index":214,"time":"16:46","ratio":0.85585,"inputTokens":342340,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.799,"originalCredits":0.799,"afterCompact":false},{"index":215,"time":"16:46","ratio":0.857293,"inputTokens":342917,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.789,"originalCredits":0.789,"afterCompact":false},{"index":216,"time":"16:46","ratio":0.859115,"inputTokens":343646,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.824,"originalCredits":0.824,"afterCompact":false},{"index":217,"time":"16:47","ratio":0.861868,"inputTokens":344747,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.806,"originalCredits":0.806,"afterCompact":false},{"index":218,"time":"16:47","ratio":0.864478,"inputTokens":345791,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.806,"originalCredits":0.806,"afterCompact":false},{"index":219,"time":"16:47","ratio":0.866315,"inputTokens":346526,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.849,"originalCredits":0.849,"afterCompact":false},{"index":220,"time":"16:47","ratio":0.873123,"inputTokens":349249,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.889,"originalCredits":0.889,"afterCompact":false},{"index":221,"time":"16:49","ratio":0.877675,"inputTokens":351070,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.952,"originalCredits":0.952,"afterCompact":false},{"index":222,"time":"16:49","ratio":0.88306,"inputTokens":353224,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.906,"originalCredits":0.906,"afterCompact":false},{"index":223,"time":"16:49","ratio":0.886903,"inputTokens":354761,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.871,"originalCredits":0.871,"afterCompact":false},{"index":224,"time":"16:50","ratio":0.88884,"inputTokens":355536,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.833,"originalCredits":0.833,"afterCompact":false},{"index":225,"time":"16:50","ratio":0.89005,"inputTokens":356020,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.822,"originalCredits":0.822,"afterCompact":false},{"index":226,"time":"16:50","ratio":0.891075,"inputTokens":356430,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.817,"originalCredits":0.817,"afterCompact":false},{"index":227,"time":"16:50","ratio":0.891877,"inputTokens":356751,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.819,"originalCredits":0.819,"afterCompact":false},{"index":228,"time":"16:51","ratio":0.893463,"inputTokens":357385,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.856,"originalCredits":0.856,"afterCompact":false},{"index":229,"time":"16:51","ratio":0.897857,"inputTokens":359143,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.932,"originalCredits":0.932,"afterCompact":false},{"index":230,"time":"16:51","ratio":0.901818,"inputTokens":360727,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.85,"originalCredits":0.85,"afterCompact":false},{"index":231,"time":"16:51","ratio":0.902482,"inputTokens":360993,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.821,"originalCredits":0.821,"afterCompact":false},{"index":232,"time":"16:55","ratio":0.106313,"inputTokens":42525,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.672,"originalCredits":0.672,"afterCompact":true},{"index":233,"time":"16:55","ratio":0.107408,"inputTokens":42963,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.118,"originalCredits":0.118,"afterCompact":false},{"index":234,"time":"16:56","ratio":0.108063,"inputTokens":43225,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.118,"originalCredits":0.118,"afterCompact":false},{"index":235,"time":"16:56","ratio":0.109007,"inputTokens":43603,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.115,"originalCredits":0.115,"afterCompact":false},{"index":236,"time":"16:56","ratio":0.11153,"inputTokens":44612,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.146,"originalCredits":0.146,"afterCompact":false},{"index":237,"time":"16:56","ratio":0.113537,"inputTokens":45415,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.134,"originalCredits":0.134,"afterCompact":false},{"index":238,"time":"16:56","ratio":0.117047,"inputTokens":46819,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.17,"originalCredits":0.17,"afterCompact":false},{"index":239,"time":"16:56","ratio":0.118435,"inputTokens":47374,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.136,"originalCredits":0.136,"afterCompact":false},{"index":240,"time":"16:57","ratio":0.122057,"inputTokens":48823,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.154,"originalCredits":0.154,"afterCompact":false},{"index":241,"time":"16:57","ratio":0.122957,"inputTokens":49183,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.135,"originalCredits":0.135,"afterCompact":false},{"index":242,"time":"16:57","ratio":0.12471,"inputTokens":49884,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.147,"originalCredits":0.147,"afterCompact":false},{"index":243,"time":"16:57","ratio":0.12553,"inputTokens":50212,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.129,"originalCredits":0.129,"afterCompact":false},{"index":244,"time":"16:57","ratio":0.126007,"inputTokens":50403,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.126,"originalCredits":0.126,"afterCompact":false},{"index":245,"time":"16:57","ratio":0.127067,"inputTokens":50827,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.135,"originalCredits":0.135,"afterCompact":false},{"index":246,"time":"16:58","ratio":0.128755,"inputTokens":51502,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.147,"originalCredits":0.147,"afterCompact":false},{"index":247,"time":"16:58","ratio":0.130032,"inputTokens":52013,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.137,"originalCredits":0.137,"afterCompact":false},{"index":248,"time":"16:58","ratio":0.130578,"inputTokens":52231,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.134,"originalCredits":0.134,"afterCompact":false},{"index":249,"time":"16:58","ratio":0.133365,"inputTokens":53346,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.186,"originalCredits":0.186,"afterCompact":false},{"index":250,"time":"16:58","ratio":0.139377,"inputTokens":55751,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.222,"originalCredits":0.222,"afterCompact":false},{"index":251,"time":"16:59","ratio":0.143085,"inputTokens":57234,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.226,"originalCredits":0.226,"afterCompact":false},{"index":252,"time":"17:00","ratio":0.15082,"inputTokens":60328,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.321,"originalCredits":0.321,"afterCompact":false},{"index":253,"time":"17:00","ratio":0.158665,"inputTokens":63466,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.241,"originalCredits":0.241,"afterCompact":false},{"index":254,"time":"17:01","ratio":0.160573,"inputTokens":64229,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.178,"originalCredits":0.178,"afterCompact":false},{"index":255,"time":"17:01","ratio":0.162483,"inputTokens":64993,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.22,"originalCredits":0.22,"afterCompact":false},{"index":256,"time":"17:02","ratio":0.1656,"inputTokens":66240,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.188,"originalCredits":0.188,"afterCompact":false},{"index":257,"time":"17:02","ratio":0.166795,"inputTokens":66718,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.175,"originalCredits":0.175,"afterCompact":false},{"index":258,"time":"17:03","ratio":0.168602,"inputTokens":67441,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.195,"originalCredits":0.195,"afterCompact":false},{"index":259,"time":"17:03","ratio":0.17139,"inputTokens":68556,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.285,"originalCredits":0.285,"afterCompact":false},{"index":260,"time":"17:04","ratio":0.176245,"inputTokens":70498,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.231,"originalCredits":0.231,"afterCompact":false},{"index":261,"time":"17:04","ratio":0.179235,"inputTokens":71694,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.231,"originalCredits":0.231,"afterCompact":false},{"index":262,"time":"17:04","ratio":0.181295,"inputTokens":72518,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.209,"originalCredits":0.209,"afterCompact":false},{"index":263,"time":"17:05","ratio":0.18268,"inputTokens":73072,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.21,"originalCredits":0.21,"afterCompact":false},{"index":264,"time":"17:05","ratio":0.184408,"inputTokens":73763,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.224,"originalCredits":0.224,"afterCompact":false},{"index":265,"time":"17:06","ratio":0.186485,"inputTokens":74594,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.288,"originalCredits":0.288,"afterCompact":false},{"index":266,"time":"17:06","ratio":0.19117,"inputTokens":76468,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.233,"originalCredits":0.233,"afterCompact":false},{"index":267,"time":"17:07","ratio":0.19367,"inputTokens":77468,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.273,"originalCredits":0.273,"afterCompact":false},{"index":268,"time":"17:08","ratio":0.196975,"inputTokens":78790,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.295,"originalCredits":0.295,"afterCompact":false},{"index":269,"time":"17:08","ratio":0.200747,"inputTokens":80299,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.241,"originalCredits":0.241,"afterCompact":false},{"index":270,"time":"17:08","ratio":0.201868,"inputTokens":80747,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.204,"originalCredits":0.204,"afterCompact":false},{"index":271,"time":"17:08","ratio":0.202577,"inputTokens":81031,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.206,"originalCredits":0.206,"afterCompact":false},{"index":272,"time":"17:08","ratio":0.203615,"inputTokens":81446,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.212,"originalCredits":0.212,"afterCompact":false},{"index":273,"time":"17:09","ratio":0.20569,"inputTokens":82276,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.221,"originalCredits":0.221,"afterCompact":false},{"index":274,"time":"17:09","ratio":0.206657,"inputTokens":82663,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.206,"originalCredits":0.206,"afterCompact":false},{"index":275,"time":"17:09","ratio":0.20733,"inputTokens":82932,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.201,"originalCredits":0.201,"afterCompact":false},{"index":276,"time":"17:09","ratio":0.209315,"inputTokens":83726,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.256,"originalCredits":0.256,"afterCompact":false},{"index":277,"time":"17:09","ratio":0.211505,"inputTokens":84602,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.237,"originalCredits":0.237,"afterCompact":false},{"index":278,"time":"17:10","ratio":0.212755,"inputTokens":85102,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.217,"originalCredits":0.217,"afterCompact":false},{"index":279,"time":"17:10","ratio":0.213523,"inputTokens":85409,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.217,"originalCredits":0.217,"afterCompact":false},{"index":280,"time":"17:10","ratio":0.214595,"inputTokens":85838,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.224,"originalCredits":0.224,"afterCompact":false},{"index":281,"time":"17:10","ratio":0.217473,"inputTokens":86989,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.258,"originalCredits":0.258,"afterCompact":false},{"index":282,"time":"17:11","ratio":0.219213,"inputTokens":87685,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.247,"originalCredits":0.247,"afterCompact":false},{"index":283,"time":"17:11","ratio":0.220892,"inputTokens":88357,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.231,"originalCredits":0.231,"afterCompact":false},{"index":284,"time":"17:11","ratio":0.221865,"inputTokens":88746,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.223,"originalCredits":0.223,"afterCompact":false},{"index":285,"time":"17:11","ratio":0.222755,"inputTokens":89102,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.228,"originalCredits":0.228,"afterCompact":false},{"index":286,"time":"17:12","ratio":0.223782,"inputTokens":89513,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.242,"originalCredits":0.242,"afterCompact":false},{"index":287,"time":"17:12","ratio":0.226115,"inputTokens":90446,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.251,"originalCredits":0.251,"afterCompact":false},{"index":288,"time":"17:12","ratio":0.227318,"inputTokens":90927,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.23,"originalCredits":0.23,"afterCompact":false},{"index":289,"time":"17:13","ratio":0.229185,"inputTokens":91674,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.23,"originalCredits":0.23,"afterCompact":false},{"index":290,"time":"17:13","ratio":0.233245,"inputTokens":93298,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.347,"originalCredits":0.347,"afterCompact":false},{"index":291,"time":"17:14","ratio":0.238212,"inputTokens":95285,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.299,"originalCredits":0.299,"afterCompact":false},{"index":292,"time":"17:14","ratio":0.240053,"inputTokens":96021,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.257,"originalCredits":0.257,"afterCompact":false},{"index":293,"time":"17:14","ratio":0.241407,"inputTokens":96563,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.24,"originalCredits":0.24,"afterCompact":false},{"index":294,"time":"17:14","ratio":0.242012,"inputTokens":96805,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.266,"originalCredits":0.266,"afterCompact":false},{"index":295,"time":"17:15","ratio":0.244993,"inputTokens":97997,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.284,"originalCredits":0.284,"afterCompact":false},{"index":296,"time":"17:15","ratio":0.246805,"inputTokens":98722,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.25,"originalCredits":0.25,"afterCompact":false},{"index":297,"time":"17:15","ratio":0.248337,"inputTokens":99335,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.295,"originalCredits":0.295,"afterCompact":false},{"index":298,"time":"17:16","ratio":0.251095,"inputTokens":100438,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.288,"originalCredits":0.288,"afterCompact":false},{"index":299,"time":"17:16","ratio":0.252798,"inputTokens":101119,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.26,"originalCredits":0.26,"afterCompact":false},{"index":300,"time":"17:16","ratio":0.25385,"inputTokens":101540,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.252,"originalCredits":0.252,"afterCompact":false},{"index":301,"time":"17:17","ratio":0.254675,"inputTokens":101870,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.247,"originalCredits":0.247,"afterCompact":false},{"index":302,"time":"17:17","ratio":0.255445,"inputTokens":102178,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.25,"originalCredits":0.25,"afterCompact":false},{"index":303,"time":"17:17","ratio":0.256223,"inputTokens":102489,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.253,"originalCredits":0.253,"afterCompact":false},{"index":304,"time":"17:17","ratio":0.259472,"inputTokens":103789,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.309,"originalCredits":0.309,"afterCompact":false},{"index":305,"time":"17:18","ratio":0.263087,"inputTokens":105235,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.346,"originalCredits":0.346,"afterCompact":false},{"index":306,"time":"17:19","ratio":0.266465,"inputTokens":106586,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.376,"originalCredits":0.376,"afterCompact":false},{"index":307,"time":"17:19","ratio":0.271093,"inputTokens":108437,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.334,"originalCredits":0.334,"afterCompact":false},{"index":308,"time":"17:20","ratio":0.273247,"inputTokens":109299,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.282,"originalCredits":0.282,"afterCompact":false},{"index":309,"time":"17:20","ratio":0.274987,"inputTokens":109995,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.286,"originalCredits":0.286,"afterCompact":false},{"index":310,"time":"17:20","ratio":0.276125,"inputTokens":110450,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.267,"originalCredits":0.267,"afterCompact":false},{"index":311,"time":"17:20","ratio":0.277925,"inputTokens":111170,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.301,"originalCredits":0.301,"afterCompact":false},{"index":312,"time":"17:20","ratio":0.279653,"inputTokens":111861,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.281,"originalCredits":0.281,"afterCompact":false},{"index":313,"time":"17:21","ratio":0.28054,"inputTokens":112216,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.286,"originalCredits":0.286,"afterCompact":false},{"index":314,"time":"17:21","ratio":0.281935,"inputTokens":112774,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.272,"originalCredits":0.272,"afterCompact":false},{"index":315,"time":"17:21","ratio":0.284602,"inputTokens":113841,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.301,"originalCredits":0.301,"afterCompact":false},{"index":316,"time":"17:21","ratio":0.286608,"inputTokens":114643,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.318,"originalCredits":0.318,"afterCompact":false},{"index":317,"time":"17:22","ratio":0.28871,"inputTokens":115484,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.3,"originalCredits":0.3,"afterCompact":false},{"index":318,"time":"17:22","ratio":0.289812,"inputTokens":115925,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.322,"originalCredits":0.322,"afterCompact":false},{"index":319,"time":"17:23","ratio":0.29261,"inputTokens":117044,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.342,"originalCredits":0.342,"afterCompact":false},{"index":320,"time":"17:23","ratio":0.314465,"inputTokens":125786,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.555,"originalCredits":0.555,"afterCompact":false},{"index":321,"time":"17:23","ratio":0.336735,"inputTokens":134694,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.536,"originalCredits":0.536,"afterCompact":false},{"index":322,"time":"17:24","ratio":0.338353,"inputTokens":135341,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.339,"originalCredits":0.339,"afterCompact":false},{"index":323,"time":"17:24","ratio":0.34013,"inputTokens":136052,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.338,"originalCredits":0.338,"afterCompact":false},{"index":324,"time":"17:24","ratio":0.342133,"inputTokens":136853,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.358,"originalCredits":0.358,"afterCompact":false},{"index":325,"time":"17:24","ratio":0.344635,"inputTokens":137854,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.37,"originalCredits":0.37,"afterCompact":false},{"index":326,"time":"17:24","ratio":0.346423,"inputTokens":138569,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.347,"originalCredits":0.347,"afterCompact":false},{"index":327,"time":"17:25","ratio":0.349125,"inputTokens":139650,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.418,"originalCredits":0.418,"afterCompact":false},{"index":328,"time":"17:25","ratio":0.353625,"inputTokens":141450,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.397,"originalCredits":0.397,"afterCompact":false},{"index":329,"time":"17:25","ratio":0.35546,"inputTokens":142184,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.365,"originalCredits":0.365,"afterCompact":false},{"index":330,"time":"17:25","ratio":0.357052,"inputTokens":142821,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.369,"originalCredits":0.369,"afterCompact":false},{"index":331,"time":"17:26","ratio":0.358845,"inputTokens":143538,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.361,"originalCredits":0.361,"afterCompact":false},{"index":332,"time":"17:26","ratio":0.360148,"inputTokens":144059,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.371,"originalCredits":0.371,"afterCompact":false},{"index":333,"time":"17:26","ratio":0.361878,"inputTokens":144751,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.351,"originalCredits":0.351,"afterCompact":false},{"index":334,"time":"17:26","ratio":0.365187,"inputTokens":146075,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.397,"originalCredits":0.397,"afterCompact":false},{"index":335,"time":"17:26","ratio":0.36706,"inputTokens":146824,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.369,"originalCredits":0.369,"afterCompact":false},{"index":336,"time":"17:27","ratio":0.368215,"inputTokens":147286,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.359,"originalCredits":0.359,"afterCompact":false},{"index":337,"time":"17:27","ratio":0.369295,"inputTokens":147718,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.347,"originalCredits":0.347,"afterCompact":false},{"index":338,"time":"17:27","ratio":0.37059,"inputTokens":148236,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.386,"originalCredits":0.386,"afterCompact":false},{"index":339,"time":"17:27","ratio":0.37301,"inputTokens":149204,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.368,"originalCredits":0.368,"afterCompact":false},{"index":340,"time":"17:27","ratio":0.375613,"inputTokens":150245,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.388,"originalCredits":0.388,"afterCompact":false},{"index":341,"time":"17:28","ratio":0.376937,"inputTokens":150775,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.47,"originalCredits":0.47,"afterCompact":false},{"index":342,"time":"17:28","ratio":0.382242,"inputTokens":152897,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.41,"originalCredits":0.41,"afterCompact":false},{"index":343,"time":"17:28","ratio":0.383035,"inputTokens":153214,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.356,"originalCredits":0.356,"afterCompact":false},{"index":344,"time":"17:28","ratio":0.383873,"inputTokens":153549,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.373,"originalCredits":0.373,"afterCompact":false},{"index":345,"time":"17:28","ratio":0.38555,"inputTokens":154220,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.396,"originalCredits":0.396,"afterCompact":false},{"index":346,"time":"17:29","ratio":0.387115,"inputTokens":154846,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.371,"originalCredits":0.371,"afterCompact":false},{"index":347,"time":"17:29","ratio":0.387645,"inputTokens":155058,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.363,"originalCredits":0.363,"afterCompact":false},{"index":348,"time":"17:29","ratio":0.389253,"inputTokens":155701,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.369,"originalCredits":0.369,"afterCompact":false},{"index":349,"time":"17:29","ratio":0.389842,"inputTokens":155937,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.373,"originalCredits":0.373,"afterCompact":false},{"index":350,"time":"17:30","ratio":0.392178,"inputTokens":156871,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.401,"originalCredits":0.401,"afterCompact":false},{"index":351,"time":"17:30","ratio":0.394775,"inputTokens":157910,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.42,"originalCredits":0.42,"afterCompact":false},{"index":352,"time":"17:30","ratio":0.39693,"inputTokens":158772,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.39,"originalCredits":0.39,"afterCompact":false},{"index":353,"time":"17:30","ratio":0.398645,"inputTokens":159458,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.383,"originalCredits":0.383,"afterCompact":false},{"index":354,"time":"17:31","ratio":0.40038,"inputTokens":160152,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.422,"originalCredits":0.422,"afterCompact":false},{"index":355,"time":"17:31","ratio":0.403745,"inputTokens":161498,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.433,"originalCredits":0.433,"afterCompact":false},{"index":356,"time":"17:31","ratio":0.406265,"inputTokens":162506,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.446,"originalCredits":0.446,"afterCompact":false},{"index":357,"time":"17:31","ratio":0.40892,"inputTokens":163568,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.427,"originalCredits":0.427,"afterCompact":false},{"index":358,"time":"17:32","ratio":0.411058,"inputTokens":164423,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.417,"originalCredits":0.417,"afterCompact":false},{"index":359,"time":"17:32","ratio":0.41313,"inputTokens":165252,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.408,"originalCredits":0.408,"afterCompact":false},{"index":360,"time":"17:33","ratio":0.41415,"inputTokens":165660,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.406,"originalCredits":0.406,"afterCompact":false},{"index":361,"time":"17:33","ratio":0.415413,"inputTokens":166165,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.462,"originalCredits":0.462,"afterCompact":false},{"index":362,"time":"17:33","ratio":0.425625,"inputTokens":170250,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.548,"originalCredits":0.548,"afterCompact":false},{"index":363,"time":"17:34","ratio":0.429345,"inputTokens":171738,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.493,"originalCredits":0.493,"afterCompact":false},{"index":364,"time":"17:34","ratio":0.43256,"inputTokens":173024,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.457,"originalCredits":0.457,"afterCompact":false},{"index":365,"time":"17:35","ratio":0.434727,"inputTokens":173891,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.524,"originalCredits":0.524,"afterCompact":false},{"index":366,"time":"17:35","ratio":0.440553,"inputTokens":176221,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.458,"originalCredits":0.458,"afterCompact":false},{"index":367,"time":"17:36","ratio":0.443352,"inputTokens":177341,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.524,"originalCredits":0.524,"afterCompact":false},{"index":368,"time":"17:36","ratio":0.447767,"inputTokens":179107,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.474,"originalCredits":0.474,"afterCompact":false},{"index":369,"time":"17:36","ratio":0.449205,"inputTokens":179682,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.462,"originalCredits":0.462,"afterCompact":false},{"index":370,"time":"17:37","ratio":0.451597,"inputTokens":180639,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.514,"originalCredits":0.514,"afterCompact":false},{"index":371,"time":"17:37","ratio":0.456945,"inputTokens":182778,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.597,"originalCredits":0.597,"afterCompact":false},{"index":372,"time":"17:38","ratio":0.46272,"inputTokens":185088,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.744,"originalCredits":0.744,"afterCompact":false},{"index":373,"time":"17:38","ratio":0.47424,"inputTokens":189696,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.576,"originalCredits":0.576,"afterCompact":false},{"index":374,"time":"17:39","ratio":0.477948,"inputTokens":191179,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.564,"originalCredits":0.564,"afterCompact":false},{"index":375,"time":"17:39","ratio":0.48235,"inputTokens":192940,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.516,"originalCredits":0.516,"afterCompact":false},{"index":376,"time":"17:39","ratio":0.484457,"inputTokens":193783,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.494,"originalCredits":0.494,"afterCompact":false},{"index":377,"time":"17:40","ratio":0.486577,"inputTokens":194631,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.477,"originalCredits":0.477,"afterCompact":false},{"index":378,"time":"17:40","ratio":0.488822,"inputTokens":195529,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.485,"originalCredits":0.485,"afterCompact":false},{"index":379,"time":"17:40","ratio":0.49155,"inputTokens":196620,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.504,"originalCredits":0.504,"afterCompact":false},{"index":380,"time":"17:40","ratio":0.493963,"inputTokens":197585,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.522,"originalCredits":0.522,"afterCompact":false},{"index":381,"time":"17:41","ratio":0.496547,"inputTokens":198619,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.532,"originalCredits":0.532,"afterCompact":false},{"index":382,"time":"17:41","ratio":0.49954,"inputTokens":199816,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.523,"originalCredits":0.523,"afterCompact":false},{"index":383,"time":"17:41","ratio":0.50175,"inputTokens":200700,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.518,"originalCredits":0.518,"afterCompact":false},{"index":384,"time":"17:41","ratio":0.505117,"inputTokens":202047,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.5,"originalCredits":0.5,"afterCompact":false},{"index":385,"time":"17:42","ratio":0.509443,"inputTokens":203777,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.514,"originalCredits":0.514,"afterCompact":false},{"index":386,"time":"17:42","ratio":0.51033,"inputTokens":204132,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.471,"originalCredits":0.471,"afterCompact":false},{"index":387,"time":"17:42","ratio":0.511123,"inputTokens":204449,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.509,"originalCredits":0.509,"afterCompact":false},{"index":388,"time":"17:42","ratio":0.513402,"inputTokens":205361,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.503,"originalCredits":0.503,"afterCompact":false},{"index":389,"time":"17:42","ratio":0.515373,"inputTokens":206149,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.486,"originalCredits":0.486,"afterCompact":false},{"index":390,"time":"17:43","ratio":0.515872,"inputTokens":206349,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.49,"originalCredits":0.49,"afterCompact":false},{"index":391,"time":"17:43","ratio":0.517918,"inputTokens":207167,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.498,"originalCredits":0.498,"afterCompact":false},{"index":392,"time":"17:43","ratio":0.519035,"inputTokens":207614,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.497,"originalCredits":0.497,"afterCompact":false},{"index":393,"time":"17:43","ratio":0.521508,"inputTokens":208603,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.506,"originalCredits":0.506,"afterCompact":false},{"index":394,"time":"17:43","ratio":0.52235,"inputTokens":208940,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.49,"originalCredits":0.49,"afterCompact":false},{"index":395,"time":"17:44","ratio":0.523218,"inputTokens":209287,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.493,"originalCredits":0.493,"afterCompact":false},{"index":396,"time":"17:44","ratio":0.52414,"inputTokens":209656,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.5,"originalCredits":0.5,"afterCompact":false},{"index":397,"time":"17:45","ratio":0.525565,"inputTokens":210226,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.556,"originalCredits":0.556,"afterCompact":false},{"index":398,"time":"17:45","ratio":0.529142,"inputTokens":211657,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.589,"originalCredits":0.589,"afterCompact":false},{"index":399,"time":"17:46","ratio":0.533837,"inputTokens":213535,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.564,"originalCredits":0.564,"afterCompact":false},{"index":400,"time":"17:46","ratio":0.535793,"inputTokens":214317,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.541,"originalCredits":0.541,"afterCompact":false},{"index":401,"time":"17:46","ratio":0.538765,"inputTokens":215506,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.52,"originalCredits":0.52,"afterCompact":false},{"index":402,"time":"17:47","ratio":0.539362,"inputTokens":215745,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.498,"originalCredits":0.498,"afterCompact":false},{"index":403,"time":"17:48","ratio":0.5401,"inputTokens":216040,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.519,"originalCredits":0.519,"afterCompact":false},{"index":404,"time":"17:48","ratio":0.541655,"inputTokens":216662,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.527,"originalCredits":0.527,"afterCompact":false},{"index":405,"time":"17:48","ratio":0.543223,"inputTokens":217289,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.539,"originalCredits":0.539,"afterCompact":false},{"index":406,"time":"17:49","ratio":0.545195,"inputTokens":218078,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.517,"originalCredits":0.517,"afterCompact":false},{"index":407,"time":"17:49","ratio":0.545815,"inputTokens":218326,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.511,"originalCredits":0.511,"afterCompact":false},{"index":408,"time":"17:50","ratio":0.547837,"inputTokens":219135,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.532,"originalCredits":0.532,"afterCompact":false},{"index":409,"time":"17:50","ratio":0.549192,"inputTokens":219677,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.532,"originalCredits":0.532,"afterCompact":false},{"index":410,"time":"17:51","ratio":0.550955,"inputTokens":220382,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.553,"originalCredits":0.553,"afterCompact":false},{"index":411,"time":"17:51","ratio":0.553077,"inputTokens":221231,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.567,"originalCredits":0.567,"afterCompact":false},{"index":412,"time":"17:52","ratio":0.55549,"inputTokens":222196,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.533,"originalCredits":0.533,"afterCompact":false},{"index":413,"time":"17:52","ratio":0.556292,"inputTokens":222517,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.534,"originalCredits":0.534,"afterCompact":false},{"index":414,"time":"17:52","ratio":0.557915,"inputTokens":223166,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.577,"originalCredits":0.577,"afterCompact":false},{"index":415,"time":"17:52","ratio":0.561913,"inputTokens":224765,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.548,"originalCredits":0.548,"afterCompact":false},{"index":416,"time":"17:52","ratio":0.56264,"inputTokens":225056,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.53,"originalCredits":0.53,"afterCompact":false},{"index":417,"time":"17:53","ratio":0.56376,"inputTokens":225504,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.55,"originalCredits":0.55,"afterCompact":false},{"index":418,"time":"17:53","ratio":0.565945,"inputTokens":226378,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.544,"originalCredits":0.544,"afterCompact":false},{"index":419,"time":"17:53","ratio":0.56696,"inputTokens":226784,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.546,"originalCredits":0.546,"afterCompact":false},{"index":420,"time":"17:53","ratio":0.569255,"inputTokens":227702,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.555,"originalCredits":0.555,"afterCompact":false},{"index":421,"time":"17:54","ratio":0.57343,"inputTokens":229372,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.576,"originalCredits":0.576,"afterCompact":false},{"index":422,"time":"17:54","ratio":0.575913,"inputTokens":230365,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.547,"originalCredits":0.547,"afterCompact":false},{"index":423,"time":"17:54","ratio":0.579357,"inputTokens":231743,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.568,"originalCredits":0.568,"afterCompact":false},{"index":424,"time":"17:54","ratio":0.580175,"inputTokens":232070,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.544,"originalCredits":0.544,"afterCompact":false},{"index":425,"time":"17:54","ratio":0.583248,"inputTokens":233299,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.576,"originalCredits":0.576,"afterCompact":false},{"index":426,"time":"17:55","ratio":0.584995,"inputTokens":233998,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.552,"originalCredits":0.552,"afterCompact":false},{"index":427,"time":"17:55","ratio":0.586908,"inputTokens":234763,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.591,"originalCredits":0.591,"afterCompact":false},{"index":428,"time":"17:55","ratio":0.589845,"inputTokens":235938,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.563,"originalCredits":0.563,"afterCompact":false},{"index":429,"time":"17:55","ratio":0.590975,"inputTokens":236390,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.556,"originalCredits":0.556,"afterCompact":false},{"index":430,"time":"17:56","ratio":0.592055,"inputTokens":236822,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.56,"originalCredits":0.56,"afterCompact":false},{"index":431,"time":"17:56","ratio":0.59324,"inputTokens":237296,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.558,"originalCredits":0.558,"afterCompact":false},{"index":432,"time":"17:56","ratio":0.594087,"inputTokens":237635,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.566,"originalCredits":0.566,"afterCompact":false},{"index":433,"time":"17:56","ratio":0.595465,"inputTokens":238186,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.583,"originalCredits":0.583,"afterCompact":false},{"index":434,"time":"17:57","ratio":0.597315,"inputTokens":238926,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.607,"originalCredits":0.607,"afterCompact":false},{"index":435,"time":"17:57","ratio":0.599827,"inputTokens":239931,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.58,"originalCredits":0.58,"afterCompact":false},{"index":436,"time":"17:57","ratio":0.601818,"inputTokens":240727,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.568,"originalCredits":0.568,"afterCompact":false},{"index":437,"time":"17:58","ratio":0.602487,"inputTokens":240995,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.579,"originalCredits":0.579,"afterCompact":false},{"index":438,"time":"17:58","ratio":0.60644,"inputTokens":242576,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.59,"originalCredits":0.59,"afterCompact":false},{"index":439,"time":"18:01","ratio":0.608625,"inputTokens":243450,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.903,"originalCredits":0.903,"afterCompact":false},{"index":440,"time":"18:01","ratio":0.622938,"inputTokens":249175,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.767,"originalCredits":0.767,"afterCompact":false},{"index":441,"time":"18:02","ratio":0.626015,"inputTokens":250406,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.641,"originalCredits":0.641,"afterCompact":false},{"index":442,"time":"18:02","ratio":0.628487,"inputTokens":251395,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.63,"originalCredits":0.63,"afterCompact":false},{"index":443,"time":"18:02","ratio":0.630652,"inputTokens":252261,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.599,"originalCredits":0.599,"afterCompact":false},{"index":444,"time":"18:02","ratio":0.63201,"inputTokens":252804,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.605,"originalCredits":0.605,"afterCompact":false},{"index":445,"time":"18:03","ratio":0.634552,"inputTokens":253821,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.615,"originalCredits":0.615,"afterCompact":false},{"index":446,"time":"18:03","ratio":0.635968,"inputTokens":254387,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.609,"originalCredits":0.609,"afterCompact":false},{"index":447,"time":"18:03","ratio":0.637387,"inputTokens":254955,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.617,"originalCredits":0.617,"afterCompact":false},{"index":448,"time":"18:03","ratio":0.639273,"inputTokens":255709,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.621,"originalCredits":0.621,"afterCompact":false},{"index":449,"time":"18:04","ratio":0.64102,"inputTokens":256408,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.61,"originalCredits":0.61,"afterCompact":false},{"index":450,"time":"18:04","ratio":0.642127,"inputTokens":256851,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.64,"originalCredits":0.64,"afterCompact":false},{"index":451,"time":"18:04","ratio":0.644863,"inputTokens":257945,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.626,"originalCredits":0.626,"afterCompact":false},{"index":452,"time":"18:04","ratio":0.647338,"inputTokens":258935,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.622,"originalCredits":0.622,"afterCompact":false},{"index":453,"time":"18:05","ratio":0.648435,"inputTokens":259374,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.617,"originalCredits":0.617,"afterCompact":false},{"index":454,"time":"18:05","ratio":0.649865,"inputTokens":259946,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.624,"originalCredits":0.624,"afterCompact":false},{"index":455,"time":"18:05","ratio":0.65182,"inputTokens":260728,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.632,"originalCredits":0.632,"afterCompact":false},{"index":456,"time":"18:05","ratio":0.653388,"inputTokens":261355,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.605,"originalCredits":0.605,"afterCompact":false},{"index":457,"time":"18:06","ratio":0.65481,"inputTokens":261924,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.642,"originalCredits":0.642,"afterCompact":false},{"index":458,"time":"18:06","ratio":0.656902,"inputTokens":262761,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.623,"originalCredits":0.623,"afterCompact":false},{"index":459,"time":"18:06","ratio":0.658358,"inputTokens":263343,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.62,"originalCredits":0.62,"afterCompact":false},{"index":460,"time":"18:06","ratio":0.659405,"inputTokens":263762,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.627,"originalCredits":0.627,"afterCompact":false},{"index":461,"time":"18:07","ratio":0.662045,"inputTokens":264818,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.678,"originalCredits":0.678,"afterCompact":false},{"index":462,"time":"18:07","ratio":0.664793,"inputTokens":265917,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.636,"originalCredits":0.636,"afterCompact":false},{"index":463,"time":"18:07","ratio":0.666013,"inputTokens":266405,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.61,"originalCredits":0.61,"afterCompact":false},{"index":464,"time":"18:07","ratio":0.667493,"inputTokens":266997,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.621,"originalCredits":0.621,"afterCompact":false},{"index":465,"time":"18:07","ratio":0.66908,"inputTokens":267632,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.658,"originalCredits":0.658,"afterCompact":false},{"index":466,"time":"18:08","ratio":0.672875,"inputTokens":269150,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.645,"originalCredits":0.645,"afterCompact":false},{"index":467,"time":"18:08","ratio":0.673358,"inputTokens":269343,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.631,"originalCredits":0.631,"afterCompact":false},{"index":468,"time":"18:08","ratio":0.67489,"inputTokens":269956,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.634,"originalCredits":0.634,"afterCompact":false},{"index":469,"time":"18:08","ratio":0.675848,"inputTokens":270339,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.642,"originalCredits":0.642,"afterCompact":false},{"index":470,"time":"18:08","ratio":0.67828,"inputTokens":271312,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.644,"originalCredits":0.644,"afterCompact":false},{"index":471,"time":"18:09","ratio":0.6792,"inputTokens":271680,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.715,"originalCredits":0.715,"afterCompact":false}],"identity":{"sumAttributed":84983322,"billedInputTokens":84983322,"absDiff":0,"ok":true},"pluginVersion":"2.7.4","selfCmd":"\"C:\\Users\\49745\\.qoder-cn\\plugins\\cache\\qoder-marketplace\\qoder-credits-inspector\\2.7.4\\bin\\credits-inspector.cmd\" cli","linkHealth":{"matched":0,"requests":471,"coverage":0,"usageSource":"transcript-ratio","breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":471},"logRecords":0,"lastRecordAt":null,"recentRequests":0,"proxyErrors":null,"clientAbort":null,"clientAbortMaxMs":null,"upstreamRejected":null,"aborted":null,"truncated":null,"noUsage":null,"slowestMs":null,"supersededFailure":null},"subagents":{"scanned":false,"dir":null,"probedPaths":["C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\5f98e050-07f7-425e-a755-9000567ac78d\\subagents","C:\\Users\\49745\\.qoder-cn\\projects\\5f98e050-07f7-425e-a755-9000567ac78d\\subagents"],"reason":"no-dir","count":0,"items":[],"totals":{"roundTrips":0,"billedInputTokens":0,"credits":0,"originalCredits":0},"combined":{"roundTrips":471,"billedInputTokens":84983322,"credits":246.011,"originalCredits":246.011}},"manual":null,"artifacts":{"report":"report.json","canvas":"# T1.1.2 — Region Canvas__5f98e050.canvas.tsx"}} as unknown as Report;

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
