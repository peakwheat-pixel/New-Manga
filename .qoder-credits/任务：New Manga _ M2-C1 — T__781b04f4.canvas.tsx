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
const REPORT = {"schemaVersion":3.2,"generatedAt":"2026-09-26T03:53:08.824Z","source":"desktop-rich","usageSource":"transcript-ratio","availability":{"credits":"measured","roundTrips":"measured","contextRatio":"measured","tokens":"derived","outputTokens":"unavailable","cachedTokens":"unavailable","categoryShare":"derived","toolShare":"derived","fileShare":"derived","systemPrompt":"derived","contextWindow":"measured","compactions":"measured","compactionCost":"measured","model":"measured","title":"measured","toolCalls":"measured","fileReads":"measured","userTurns":"measured","userContextLimit":"fallback"},"session":{"id":"781b04f4-4f2d-4e23-8cd1-38da35646197","title":"任务：New Manga / M2-C1 — T","titleSource":"first-user","model":"qfmodel","modelSource":"runtime-config","cwd":"G:\\CODEX\\New Manga","turns":2,"roundTrips":133,"compactions":0,"startedAt":"2026-09-25T18:43:41.787Z","endedAt":"2026-09-26T03:53:08.463Z"},"context":{"contextWindow":400000,"contextWindowSource":"runtime-config","systemPromptTokens":20918,"netContextTokens":253979,"peakContextTokens":253979,"peakContextRatio":0.6349475,"peakSessionTokens":253979,"peakSessionRatio":0.6349475,"peakSessionNotable":false,"peakAdvice":{"level":"mid","tone":"info","text":"已过盈亏线（39%）但还没进性价比区间，压缩有净收益但不大；不急着压"},"userContextLimit":200000,"userContextLimitSource":"default","peakUserRatio":1.269895,"peakUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"currentContextTokens":253979,"netUserRatio":1.269895,"netUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"netWindowRatio":0.6349475,"observedAutoCompactions":0,"observedAutoTriggerTokens":null,"autoTriggerRatio":null,"thresholdNotEnforced":true},"totals":{"billedInputTokens":21727640,"netContextTokens":253979,"peakContextTokens":253979,"amplification":85.55,"attributedTokens":21727640,"coverage":1,"credits":65.832,"originalCredits":65.832,"outputTokens":0,"cachedTokens":0,"cachedTrips":0,"cachedShare":0,"toolCalls":157,"fileReads":36},"creditsCoverage":{"trips":133,"roundTrips":133,"tokens":21727640,"tokenShare":1,"full":true},"compactionCost":{"count":0,"items":[],"totals":{"preTokens":0,"postTokens":0,"savedTokens":0,"measured":0}},"proxy":{"matched":0,"requests":133,"breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":133},"logPath":"C:\\Users\\49745\\.qoder-credits-proxy\\usage.jsonl","logExists":false,"logRecords":0,"configured":false,"enabled":true,"port":49787,"lastRecordAt":null,"dormant":false,"status":null,"statusSuperseded":false},"byCategory":[{"key":"tool_result","label":"工具返回","tokens":8152033,"share":0.37519182796877654},{"key":"system","label":"系统提示词","tokens":2782094,"share":0.128044002938193},{"key":"assistant_thinking","label":"模型思考","tokens":3477360,"share":0.16004314189718638},{"key":"assistant_tool_use","label":"工具调用","tokens":3912036,"share":0.1800488345299579},{"key":"assistant_text","label":"模型回复","tokens":419373,"share":0.019301341346881655},{"key":"user_input","label":"用户输入","tokens":250831,"share":0.011544321460393686},{"key":"attachment","label":"附件/技能","tokens":2733914,"share":0.12582652985861276}],"byCategoryDetail":[{"key":"tool_result","label":"工具返回","tokens":8152033,"share":0.37519182796877654,"children":[{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":6297480,"share":0.2898372881391722,"catShare":0.7725042672392439,"trips":7339},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md","kind":"read","tokens":1072748,"share":0.04937251597568384,"catShare":0.13159272749350132,"trips":118},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/handoffs/M2-C1-4d66523.md","kind":"read","tokens":240841,"share":0.011084535563919995,"catShare":0.029543648708794508,"trips":102},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/verification/M2-C1/review-remediation-r3.md","kind":"read","tokens":186750,"share":0.008595041755341313,"catShare":0.022908392759707425,"trips":110},{"tool":"Read","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/templates/REVIEW.md","kind":"read","tokens":157705,"share":0.007258286940751233,"catShare":0.019345535802435622,"trips":97},{"tool":"Read","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"read","tokens":56038,"share":0.002579097576211404,"catShare":0.006874077162538936,"trips":74},{"tool":"TaskCreate","label":"（无路径）","kind":"other","tokens":23230,"share":0.0010691622858356232,"catShare":0.0028496417196074934,"trips":817},{"tool":"mcp_call","label":"（无路径）","kind":"other","tokens":21937,"share":0.001009634961520595,"catShare":0.0026909833484022923,"trips":59},{"tool":"mcp_get","label":"（无路径）","kind":"other","tokens":20012,"share":0.0009210195189916149,"catShare":0.002454796321065559,"trips":60},{"tool":"Edit","label":"G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/M2-C1-4d66523-r3-qoder.md","kind":"write","tokens":14050,"share":0.000646658160157348,"catShare":0.0017235400985630286,"trips":235},{"tool":"AskUserQuestion","label":"（无路径）","kind":"other","tokens":9014,"share":0.0004148469712373429,"catShare":0.0011056929823958384,"trips":99},{"tool":"Edit","label":"G:/CODEX/qoder-tmp/m2c1-r3/genlogs2.sh","kind":"write","tokens":8054,"share":0.0003706758806480653,"catShare":0.000987963630910727,"trips":177},{"tool":"TaskUpdate","label":"（无路径）","kind":"other","tokens":6594,"share":0.0003034850275494769,"catShare":0.0008088796315007504,"trips":918},{"tool":"Edit","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part2.sh","kind":"write","tokens":5627,"share":0.00025897354051561346,"catShare":0.0006902430202641973,"trips":101},{"tool":"Edit","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"write","tokens":3955,"share":0.00018204385109241034,"catShare":0.0004852020687069976,"trips":72},{"tool":null,"label":"其他 18 项","kind":null,"tokens":27997,"share":0.0012885618201470372,"catShare":0.0034344080123575376,"trips":936}]},{"key":"system","label":"系统提示词","tokens":2782094,"share":0.128044002938193,"children":[]},{"key":"assistant_thinking","label":"模型思考","tokens":3477360,"share":0.16004314189718638,"children":[]},{"key":"assistant_tool_use","label":"工具调用","tokens":3912036,"share":0.1800488345299579,"children":[{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":1665459,"share":0.07665162065774554,"catShare":0.4257268360434272,"trips":7339},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/M2-C1-4d66523-r3-qoder.md","kind":"write","tokens":593296,"share":0.027306030354107055,"catShare":0.15165902309444645,"trips":84},{"tool":"Write","label":"G:/CODEX/qoder-tmp/m2c1-r3/genlogs2.sh","kind":"write","tokens":246257,"share":0.011333826140770146,"catShare":0.06294862263540138,"trips":93},{"tool":"Write","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part3.sh","kind":"write","tokens":152885,"share":0.007036440612220252,"catShare":0.03908073401635641,"trips":46},{"tool":"Write","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part1.sh","kind":"write","tokens":141953,"share":0.006533276007890469,"catShare":0.03628613328681898,"trips":58},{"tool":"Write","label":"G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-r3-4d66523/doc/reviews/M2-C1-4d66523-r3.md","kind":"write","tokens":135328,"share":0.006228397713339967,"catShare":0.03459282438345158,"trips":16},{"tool":"Write","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part2.sh","kind":"write","tokens":128679,"share":0.005922341557491728,"catShare":0.03289297358104433,"trips":52},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/README.md","kind":"write","tokens":123548,"share":0.005686227925338111,"catShare":0.031581586963241315,"trips":75},{"tool":"TaskCreate","label":"（无路径）","kind":"other","tokens":114452,"share":0.005267580058730693,"catShare":0.029256396313158208,"trips":817},{"tool":"Write","label":"G:/CODEX/qoder-tmp/m2c1-r3/genlogs3.sh","kind":"write","tokens":92987,"share":0.004279672717963667,"catShare":0.023769510805978483,"trips":77},{"tool":"Edit","label":"G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/M2-C1-4d66523-r3-qoder.md","kind":"write","tokens":85052,"share":0.0039144648054127386,"catShare":0.021741128264628783,"trips":235},{"tool":"Write","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part4.sh","kind":"write","tokens":70323,"share":0.0032365851875156807,"catShare":0.01797615183661271,"trips":31},{"tool":"Edit","label":"G:/CODEX/qoder-tmp/m2c1-r3/genlogs2.sh","kind":"write","tokens":66189,"share":0.0030463058070038912,"catShare":0.016919330885738243,"trips":177},{"tool":"AskUserQuestion","label":"（无路径）","kind":"other","tokens":56572,"share":0.002603710595792271,"catShare":0.014461135516870262,"trips":99},{"tool":"Write","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/m2c1-r3-review-state.md","kind":"write","tokens":51957,"share":0.0023912935734168137,"catShare":0.013281361024411029,"trips":76},{"tool":null,"label":"其他 18 项","kind":null,"tokens":187098,"share":0.008611060815218397,"catShare":0.04782625134841194,"trips":2039}]},{"key":"assistant_text","label":"模型回复","tokens":419373,"share":0.019301341346881655,"children":[]},{"key":"user_input","label":"用户输入","tokens":250831,"share":0.011544321460393686,"children":[]},{"key":"attachment","label":"附件/技能","tokens":2733914,"share":0.12582652985861276,"children":[]}],"byTool":[{"tool":"Bash","tokens":7962939,"calls":97,"perCall":82092,"share":0.36648890879691715},{"tool":"Write","tokens":1844236,"calls":15,"perCall":122949,"share":0.08487973648034071},{"tool":"Read","tokens":1730075,"calls":6,"perCall":288346,"share":0.0796255171464535},{"tool":"Edit","tokens":262987,"calls":15,"perCall":17532,"share":0.012103783907275558},{"tool":"TaskCreate","tokens":137682,"calls":8,"perCall":17210,"share":0.006336742344566315},{"tool":"AskUserQuestion","tokens":65586,"calls":1,"perCall":65586,"share":0.0030185575670296123},{"tool":"mcp_call","tokens":23207,"calls":1,"perCall":23207,"share":0.0010680704255314336},{"tool":"mcp_get","tokens":20872,"calls":1,"perCall":20872,"share":0.0009606332617439421},{"tool":"TaskUpdate","tokens":16485,"calls":13,"perCall":1268,"share":0.0007587125688736904}],"byFile":[{"attr":"file:G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md","kind":"read","tool":"Read","selfTokens":7616,"reads":1,"trips":236,"billed":1076849,"perRead":1076849,"share":0.04956123390942508},{"attr":"file:G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/M2-C1-4d66523-r3-qoder.md","label":"G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/M2-C1-4d66523-r3-qoder.md","kind":"write","tool":"Write","selfTokens":7004,"reads":4,"trips":638,"billed":695312,"perRead":173828,"share":0.03200127846877418},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/genlogs2.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/genlogs2.sh","kind":"write","tool":"Write","selfTokens":2927,"reads":3,"trips":540,"billed":322395,"perRead":107465,"share":0.014837991106428009},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/handoffs/M2-C1-4d66523.md","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/handoffs/M2-C1-4d66523.md","kind":"read","tool":"Read","selfTokens":1997,"reads":1,"trips":204,"billed":244018,"perRead":244018,"share":0.01123075470377891},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/verification/M2-C1/review-remediation-r3.md","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/verification/M2-C1/review-remediation-r3.md","kind":"read","tool":"Read","selfTokens":1447,"reads":1,"trips":220,"billed":190704,"perRead":190704,"share":0.00877701158784677},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/r3part1.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part1.sh","kind":"write","tool":"Write","selfTokens":2471,"reads":2,"trips":230,"billed":170870,"perRead":85435,"share":0.007864177811472492},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/r3part3.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part3.sh","kind":"write","tool":"Write","selfTokens":2931,"reads":2,"trips":182,"billed":161028,"perRead":80514,"share":0.007411216977669967},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/templates/REVIEW.md","label":"G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract/doc/templates/REVIEW.md","kind":"read","tool":"Read","selfTokens":1382,"reads":1,"trips":194,"billed":160611,"perRead":160611,"share":0.007392006302224175},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/r3part2.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part2.sh","kind":"write","tool":"Write","selfTokens":2342,"reads":3,"trips":306,"billed":145199,"perRead":48400,"share":0.0066826947262708025},{"attr":"file:G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-r3-4d66523/doc/reviews/M2-C1-4d66523-r3.md","label":"G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-r3-4d66523/doc/reviews/M2-C1-4d66523-r3.md","kind":"write","tool":"Write","selfTokens":7151,"reads":1,"trips":32,"billed":135899,"perRead":135899,"share":0.006254637276800183},{"attr":"file:G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/README.md","label":"G:/CODEX/New Manga.qoder-output/M2-C1-R3-REVIEW-2026-09-26/README.md","kind":"write","tool":"Write","selfTokens":1403,"reads":1,"trips":150,"billed":125790,"perRead":125790,"share":0.00578938880932465},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/genlogs3.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/genlogs3.sh","kind":"write","tool":"Write","selfTokens":1027,"reads":1,"trips":154,"billed":94552,"perRead":94552,"share":0.0043517068132165205},{"attr":"file:C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"read","tool":"Read","selfTokens":1890,"reads":4,"trips":292,"billed":83573,"perRead":20893,"share":0.003846373542388709},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/r3part4.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part4.sh","kind":"write","tool":"Write","selfTokens":2291,"reads":4,"trips":224,"billed":82851,"perRead":20713,"share":0.0038131414156388},{"attr":"file:C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/m2c1-r3-review-state.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/m2c1-r3-review-state.md","kind":"write","tool":"Write","selfTokens":1330,"reads":2,"trips":152,"billed":54516,"perRead":27258,"share":0.0025090727928095036},{"attr":"file:C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/reviewer-routing-before-review.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/reviewer-routing-before-review.md","kind":"write","tool":"Write","selfTokens":1276,"reads":2,"trips":146,"billed":50519,"perRead":25259,"share":0.002325100878200407},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/r3part5.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/r3part5.sh","kind":"write","tool":"Write","selfTokens":850,"reads":1,"trips":44,"billed":22261,"perRead":22261,"share":0.0010245633053225795},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/fix06.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/fix06.sh","kind":"write","tool":"Write","selfTokens":250,"reads":1,"trips":72,"billed":10744,"perRead":10744,"share":0.0004944639227087932},{"attr":"file:G:/CODEX/qoder-tmp/m2c1-r3/fixws.sh","label":"G:/CODEX/qoder-tmp/m2c1-r3/fixws.sh","kind":"write","tool":"Write","selfTokens":578,"reads":1,"trips":28,"billed":9608,"perRead":9608,"share":0.00044222318376921485}],"byAttr":[{"attr":"tool_result|Bash","tokens":6297480,"share":0.2898372881391722},{"attr":"assistant_thinking","tokens":3477360,"share":0.16004314189718638},{"attr":"system","tokens":2782094,"share":0.128044002938193},{"attr":"attachment","tokens":2733914,"share":0.12582652985861276},{"attr":"tool_use|Write","tokens":1824664,"share":0.08397892019254967},{"attr":"tool_result|Read","tokens":1714082,"share":0.07888947781190775},{"attr":"tool_use|Bash","tokens":1665459,"share":0.07665162065774554},{"attr":"assistant_text","tokens":419373,"share":0.019301341346881655},{"attr":"user_input","tokens":250831,"share":0.011544321460393686},{"attr":"tool_use|Edit","tokens":222875,"share":0.010257686942506058},{"attr":"tool_use|TaskCreate","tokens":114452,"share":0.005267580058730693},{"attr":"tool_use|AskUserQuestion","tokens":56572,"share":0.002603710595792271},{"attr":"tool_result|Edit","tokens":40111,"share":0.0018460969647694982},{"attr":"tool_result|TaskCreate","tokens":23230,"share":0.0010691622858356232},{"attr":"tool_result|mcp_call","tokens":21937,"share":0.001009634961520595},{"attr":"tool_result|mcp_get","tokens":20012,"share":0.0009210195189916149},{"attr":"tool_result|Write","tokens":19573,"share":0.0009008162877909715},{"attr":"tool_use|Read","tokens":15992,"share":0.0007360393345457837},{"attr":"tool_use|TaskUpdate","tokens":9891,"share":0.00045522754132421375},{"attr":"tool_result|AskUserQuestion","tokens":9014,"share":0.0004148469712373429},{"attr":"tool_result|TaskUpdate","tokens":6594,"share":0.0003034850275494769},{"attr":"tool_use|mcp_call","tokens":1270,"share":0.0000584354640108383},{"attr":"tool_use|mcp_get","tokens":861,"share":0.00003961374275232752}],"byRequest":[{"index":1,"time":"02:43","ratio":0.080665,"inputTokens":32266,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.96,"originalCredits":0.96,"afterCompact":false},{"index":2,"time":"02:44","ratio":0.101358,"inputTokens":40543,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.359,"originalCredits":0.359,"afterCompact":false},{"index":3,"time":"02:44","ratio":0.105197,"inputTokens":42079,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.169,"originalCredits":0.169,"afterCompact":false},{"index":4,"time":"02:44","ratio":0.10743,"inputTokens":42972,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.141,"originalCredits":0.141,"afterCompact":false},{"index":5,"time":"02:44","ratio":0.109272,"inputTokens":43709,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.139,"originalCredits":0.139,"afterCompact":false},{"index":6,"time":"02:44","ratio":0.119182,"inputTokens":47673,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.235,"originalCredits":0.235,"afterCompact":false},{"index":7,"time":"02:45","ratio":0.133095,"inputTokens":53238,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.307,"originalCredits":0.307,"afterCompact":false},{"index":8,"time":"02:45","ratio":0.145162,"inputTokens":58065,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.389,"originalCredits":0.389,"afterCompact":false},{"index":9,"time":"02:46","ratio":0.151218,"inputTokens":60487,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.27,"originalCredits":0.27,"afterCompact":false},{"index":10,"time":"02:46","ratio":0.155938,"inputTokens":62375,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.212,"originalCredits":0.212,"afterCompact":false},{"index":11,"time":"02:46","ratio":0.161675,"inputTokens":64670,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.274,"originalCredits":0.274,"afterCompact":false},{"index":12,"time":"02:47","ratio":0.16986,"inputTokens":67944,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.326,"originalCredits":0.326,"afterCompact":false},{"index":13,"time":"02:47","ratio":0.17459,"inputTokens":69836,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.264,"originalCredits":0.264,"afterCompact":false},{"index":14,"time":"02:47","ratio":0.177783,"inputTokens":71113,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.204,"originalCredits":0.204,"afterCompact":false},{"index":15,"time":"02:47","ratio":0.178457,"inputTokens":71383,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.172,"originalCredits":0.172,"afterCompact":false},{"index":16,"time":"02:47","ratio":0.19697,"inputTokens":78788,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.386,"originalCredits":0.386,"afterCompact":false},{"index":17,"time":"02:47","ratio":0.20009,"inputTokens":80036,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.256,"originalCredits":0.256,"afterCompact":false},{"index":18,"time":"02:48","ratio":0.209728,"inputTokens":83891,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.345,"originalCredits":0.345,"afterCompact":false},{"index":19,"time":"02:48","ratio":0.214463,"inputTokens":85785,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.325,"originalCredits":0.325,"afterCompact":false},{"index":20,"time":"02:48","ratio":0.21873,"inputTokens":87492,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.292,"originalCredits":0.292,"afterCompact":false},{"index":21,"time":"02:49","ratio":0.2212,"inputTokens":88480,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.281,"originalCredits":0.281,"afterCompact":false},{"index":22,"time":"02:49","ratio":0.223928,"inputTokens":89571,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.255,"originalCredits":0.255,"afterCompact":false},{"index":23,"time":"02:49","ratio":0.227967,"inputTokens":91187,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.313,"originalCredits":0.313,"afterCompact":false},{"index":24,"time":"02:50","ratio":0.24568,"inputTokens":98272,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.478,"originalCredits":0.478,"afterCompact":false},{"index":25,"time":"02:50","ratio":0.249105,"inputTokens":99642,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.294,"originalCredits":0.294,"afterCompact":false},{"index":26,"time":"02:50","ratio":0.254575,"inputTokens":101830,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.338,"originalCredits":0.338,"afterCompact":false},{"index":27,"time":"02:50","ratio":0.259433,"inputTokens":103773,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.315,"originalCredits":0.315,"afterCompact":false},{"index":28,"time":"02:51","ratio":0.26445,"inputTokens":105780,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.395,"originalCredits":0.395,"afterCompact":false},{"index":29,"time":"02:51","ratio":0.272832,"inputTokens":109133,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.399,"originalCredits":0.399,"afterCompact":false},{"index":30,"time":"02:51","ratio":0.276065,"inputTokens":110426,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.311,"originalCredits":0.311,"afterCompact":false},{"index":31,"time":"02:51","ratio":0.2797,"inputTokens":111880,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.312,"originalCredits":0.312,"afterCompact":false},{"index":32,"time":"02:52","ratio":0.286605,"inputTokens":114642,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.393,"originalCredits":0.393,"afterCompact":false},{"index":33,"time":"02:52","ratio":0.291117,"inputTokens":116447,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.34,"originalCredits":0.34,"afterCompact":false},{"index":34,"time":"02:52","ratio":0.2927,"inputTokens":117080,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.312,"originalCredits":0.312,"afterCompact":false},{"index":35,"time":"02:53","ratio":0.294357,"inputTokens":117743,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.29,"originalCredits":0.29,"afterCompact":false},{"index":36,"time":"02:53","ratio":0.295393,"inputTokens":118157,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.284,"originalCredits":0.284,"afterCompact":false},{"index":37,"time":"02:53","ratio":0.299418,"inputTokens":119767,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.475,"originalCredits":0.475,"afterCompact":false},{"index":38,"time":"02:54","ratio":0.307198,"inputTokens":122879,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.361,"originalCredits":0.361,"afterCompact":false},{"index":39,"time":"02:54","ratio":0.311443,"inputTokens":124577,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.51,"originalCredits":0.51,"afterCompact":false},{"index":40,"time":"02:55","ratio":0.319997,"inputTokens":127999,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.575,"originalCredits":0.575,"afterCompact":false},{"index":41,"time":"02:55","ratio":0.328562,"inputTokens":131425,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.389,"originalCredits":0.389,"afterCompact":false},{"index":42,"time":"02:55","ratio":0.329943,"inputTokens":131977,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.316,"originalCredits":0.316,"afterCompact":false},{"index":43,"time":"02:55","ratio":0.337282,"inputTokens":134913,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.391,"originalCredits":0.391,"afterCompact":false},{"index":44,"time":"02:55","ratio":0.34366,"inputTokens":137464,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.442,"originalCredits":0.442,"afterCompact":false},{"index":45,"time":"02:56","ratio":0.346788,"inputTokens":138715,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.374,"originalCredits":0.374,"afterCompact":false},{"index":46,"time":"02:56","ratio":0.348347,"inputTokens":139339,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.339,"originalCredits":0.339,"afterCompact":false},{"index":47,"time":"02:56","ratio":0.350482,"inputTokens":140193,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.344,"originalCredits":0.344,"afterCompact":false},{"index":48,"time":"02:56","ratio":0.352498,"inputTokens":140999,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.399,"originalCredits":0.399,"afterCompact":false},{"index":49,"time":"02:58","ratio":0.355287,"inputTokens":142115,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.755,"originalCredits":0.755,"afterCompact":false},{"index":50,"time":"02:58","ratio":0.372553,"inputTokens":149021,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.582,"originalCredits":0.582,"afterCompact":false},{"index":51,"time":"02:58","ratio":0.376085,"inputTokens":150434,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.397,"originalCredits":0.397,"afterCompact":false},{"index":52,"time":"02:58","ratio":0.378022,"inputTokens":151209,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.376,"originalCredits":0.376,"afterCompact":false},{"index":53,"time":"02:58","ratio":0.379088,"inputTokens":151635,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.372,"originalCredits":0.372,"afterCompact":false},{"index":54,"time":"02:58","ratio":0.38029,"inputTokens":152116,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.399,"originalCredits":0.399,"afterCompact":false},{"index":55,"time":"02:59","ratio":0.383155,"inputTokens":153262,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.404,"originalCredits":0.404,"afterCompact":false},{"index":56,"time":"02:59","ratio":0.384777,"inputTokens":153911,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.45,"originalCredits":0.45,"afterCompact":false},{"index":57,"time":"02:59","ratio":0.38869,"inputTokens":155476,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.405,"originalCredits":0.405,"afterCompact":false},{"index":58,"time":"03:00","ratio":0.391672,"inputTokens":156669,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.485,"originalCredits":0.485,"afterCompact":false},{"index":59,"time":"03:00","ratio":0.39623,"inputTokens":158492,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.443,"originalCredits":0.443,"afterCompact":false},{"index":60,"time":"03:00","ratio":0.39829,"inputTokens":159316,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.391,"originalCredits":0.391,"afterCompact":false},{"index":61,"time":"03:00","ratio":0.400058,"inputTokens":160023,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.393,"originalCredits":0.393,"afterCompact":false},{"index":62,"time":"03:00","ratio":0.402635,"inputTokens":161054,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.46,"originalCredits":0.46,"afterCompact":false},{"index":63,"time":"03:00","ratio":0.406552,"inputTokens":162621,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.41,"originalCredits":0.41,"afterCompact":false},{"index":64,"time":"03:00","ratio":0.408465,"inputTokens":163386,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.407,"originalCredits":0.407,"afterCompact":false},{"index":65,"time":"03:01","ratio":0.410815,"inputTokens":164326,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.399,"originalCredits":0.399,"afterCompact":false},{"index":66,"time":"03:01","ratio":0.41166,"inputTokens":164664,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.503,"originalCredits":0.503,"afterCompact":false},{"index":67,"time":"11:37","ratio":0.426893,"inputTokens":170757,"outputTokens":null,"usageSource":"transcript-ratio","credits":4.804,"originalCredits":4.804,"afterCompact":false},{"index":68,"time":"11:37","ratio":0.429907,"inputTokens":171963,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.445,"originalCredits":0.445,"afterCompact":false},{"index":69,"time":"11:38","ratio":0.437412,"inputTokens":174965,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.533,"originalCredits":0.533,"afterCompact":false},{"index":70,"time":"11:38","ratio":0.440468,"inputTokens":176187,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.448,"originalCredits":0.448,"afterCompact":false},{"index":71,"time":"11:38","ratio":0.442873,"inputTokens":177149,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.443,"originalCredits":0.443,"afterCompact":false},{"index":72,"time":"11:38","ratio":0.450185,"inputTokens":180074,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.523,"originalCredits":0.523,"afterCompact":false},{"index":73,"time":"11:38","ratio":0.452263,"inputTokens":180905,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.435,"originalCredits":0.435,"afterCompact":false},{"index":74,"time":"11:39","ratio":0.453365,"inputTokens":181346,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.42,"originalCredits":0.42,"afterCompact":false},{"index":75,"time":"11:39","ratio":0.454867,"inputTokens":181947,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.604,"originalCredits":0.604,"afterCompact":false},{"index":76,"time":"11:39","ratio":0.462655,"inputTokens":185062,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.536,"originalCredits":0.536,"afterCompact":false},{"index":77,"time":"11:40","ratio":0.465377,"inputTokens":186151,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.449,"originalCredits":0.449,"afterCompact":false},{"index":78,"time":"11:40","ratio":0.46636,"inputTokens":186544,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.433,"originalCredits":0.433,"afterCompact":false},{"index":79,"time":"11:40","ratio":0.471905,"inputTokens":188762,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.496,"originalCredits":0.496,"afterCompact":false},{"index":80,"time":"11:40","ratio":0.476428,"inputTokens":190571,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.507,"originalCredits":0.507,"afterCompact":false},{"index":81,"time":"11:41","ratio":0.479475,"inputTokens":191790,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.629,"originalCredits":0.629,"afterCompact":false},{"index":82,"time":"11:41","ratio":0.486768,"inputTokens":194707,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.52,"originalCredits":0.52,"afterCompact":false},{"index":83,"time":"11:41","ratio":0.487463,"inputTokens":194985,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.458,"originalCredits":0.458,"afterCompact":false},{"index":84,"time":"11:41","ratio":0.488345,"inputTokens":195338,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.456,"originalCredits":0.456,"afterCompact":false},{"index":85,"time":"11:41","ratio":0.489088,"inputTokens":195635,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.457,"originalCredits":0.457,"afterCompact":false},{"index":86,"time":"11:41","ratio":0.49474,"inputTokens":197896,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.524,"originalCredits":0.524,"afterCompact":false},{"index":87,"time":"11:42","ratio":0.496895,"inputTokens":198758,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.698,"originalCredits":0.698,"afterCompact":false},{"index":88,"time":"11:42","ratio":0.506777,"inputTokens":202711,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.633,"originalCredits":0.633,"afterCompact":false},{"index":89,"time":"11:42","ratio":0.510345,"inputTokens":204138,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.496,"originalCredits":0.496,"afterCompact":false},{"index":90,"time":"11:43","ratio":0.511685,"inputTokens":204674,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.482,"originalCredits":0.482,"afterCompact":false},{"index":91,"time":"11:43","ratio":0.51316,"inputTokens":205264,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.503,"originalCredits":0.503,"afterCompact":false},{"index":92,"time":"11:43","ratio":0.517678,"inputTokens":207071,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.543,"originalCredits":0.543,"afterCompact":false},{"index":93,"time":"11:43","ratio":0.522153,"inputTokens":208861,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.569,"originalCredits":0.569,"afterCompact":false},{"index":94,"time":"11:43","ratio":0.52571,"inputTokens":210284,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.524,"originalCredits":0.524,"afterCompact":false},{"index":95,"time":"11:44","ratio":0.528872,"inputTokens":211549,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.548,"originalCredits":0.548,"afterCompact":false},{"index":96,"time":"11:44","ratio":0.531915,"inputTokens":212766,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.521,"originalCredits":0.521,"afterCompact":false},{"index":97,"time":"11:44","ratio":0.533258,"inputTokens":213303,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.51,"originalCredits":0.51,"afterCompact":false},{"index":98,"time":"11:44","ratio":0.534273,"inputTokens":213709,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.492,"originalCredits":0.492,"afterCompact":false},{"index":99,"time":"11:44","ratio":0.536795,"inputTokens":214718,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.516,"originalCredits":0.516,"afterCompact":false},{"index":100,"time":"11:44","ratio":0.538547,"inputTokens":215419,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.527,"originalCredits":0.527,"afterCompact":false},{"index":101,"time":"11:44","ratio":0.54048,"inputTokens":216192,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.515,"originalCredits":0.515,"afterCompact":false},{"index":102,"time":"11:45","ratio":0.541802,"inputTokens":216721,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.659,"originalCredits":0.659,"afterCompact":false},{"index":103,"time":"11:45","ratio":0.548745,"inputTokens":219498,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.582,"originalCredits":0.582,"afterCompact":false},{"index":104,"time":"11:45","ratio":0.551385,"inputTokens":220554,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.549,"originalCredits":0.549,"afterCompact":false},{"index":105,"time":"11:45","ratio":0.552952,"inputTokens":221181,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.515,"originalCredits":0.515,"afterCompact":false},{"index":106,"time":"11:46","ratio":0.55343,"inputTokens":221372,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.514,"originalCredits":0.514,"afterCompact":false},{"index":107,"time":"11:46","ratio":0.555005,"inputTokens":222002,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.528,"originalCredits":0.528,"afterCompact":false},{"index":108,"time":"11:46","ratio":0.55593,"inputTokens":222372,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.512,"originalCredits":0.512,"afterCompact":false},{"index":109,"time":"11:46","ratio":0.55666,"inputTokens":222664,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.51,"originalCredits":0.51,"afterCompact":false},{"index":110,"time":"11:46","ratio":0.560137,"inputTokens":224055,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.577,"originalCredits":0.577,"afterCompact":false},{"index":111,"time":"11:47","ratio":0.564248,"inputTokens":225699,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.634,"originalCredits":0.634,"afterCompact":false},{"index":112,"time":"11:47","ratio":0.568102,"inputTokens":227241,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.556,"originalCredits":0.556,"afterCompact":false},{"index":113,"time":"11:47","ratio":0.568765,"inputTokens":227506,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.522,"originalCredits":0.522,"afterCompact":false},{"index":114,"time":"11:47","ratio":0.569518,"inputTokens":227807,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.527,"originalCredits":0.527,"afterCompact":false},{"index":115,"time":"11:47","ratio":0.574603,"inputTokens":229841,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.587,"originalCredits":0.587,"afterCompact":false},{"index":116,"time":"11:47","ratio":0.57659,"inputTokens":230636,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.55,"originalCredits":0.55,"afterCompact":false},{"index":117,"time":"11:49","ratio":0.577388,"inputTokens":230955,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.98,"originalCredits":0.98,"afterCompact":false},{"index":118,"time":"11:49","ratio":0.59666,"inputTokens":238664,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.785,"originalCredits":0.785,"afterCompact":false},{"index":119,"time":"11:50","ratio":0.602167,"inputTokens":240867,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.686,"originalCredits":0.686,"afterCompact":false},{"index":120,"time":"11:50","ratio":0.606222,"inputTokens":242489,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.603,"originalCredits":0.603,"afterCompact":false},{"index":121,"time":"11:50","ratio":0.608225,"inputTokens":243290,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.585,"originalCredits":0.585,"afterCompact":false},{"index":122,"time":"11:50","ratio":0.609783,"inputTokens":243913,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.575,"originalCredits":0.575,"afterCompact":false},{"index":123,"time":"11:50","ratio":0.61117,"inputTokens":244468,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.601,"originalCredits":0.601,"afterCompact":false},{"index":124,"time":"11:51","ratio":0.61391,"inputTokens":245564,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.598,"originalCredits":0.598,"afterCompact":false},{"index":125,"time":"11:51","ratio":0.616683,"inputTokens":246673,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.611,"originalCredits":0.611,"afterCompact":false},{"index":126,"time":"11:51","ratio":0.619483,"inputTokens":247793,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.629,"originalCredits":0.629,"afterCompact":false},{"index":127,"time":"11:51","ratio":0.62317,"inputTokens":249268,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.619,"originalCredits":0.619,"afterCompact":false},{"index":128,"time":"11:52","ratio":0.624947,"inputTokens":249979,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.637,"originalCredits":0.637,"afterCompact":false},{"index":129,"time":"11:52","ratio":0.627737,"inputTokens":251095,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.598,"originalCredits":0.598,"afterCompact":false},{"index":130,"time":"11:52","ratio":0.630065,"inputTokens":252026,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.604,"originalCredits":0.604,"afterCompact":false},{"index":131,"time":"11:52","ratio":0.632888,"inputTokens":253155,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.626,"originalCredits":0.626,"afterCompact":false},{"index":132,"time":"11:52","ratio":0.634493,"inputTokens":253797,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.59,"originalCredits":0.59,"afterCompact":false},{"index":133,"time":"11:53","ratio":0.634947,"inputTokens":253979,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.7,"originalCredits":0.7,"afterCompact":false}],"identity":{"sumAttributed":21727640,"billedInputTokens":21727640,"absDiff":0,"ok":true},"pluginVersion":"2.7.4","selfCmd":"\"C:\\Users\\49745\\.qoder-cn\\plugins\\cache\\qoder-marketplace\\qoder-credits-inspector\\2.7.4\\bin\\credits-inspector.cmd\" cli","linkHealth":{"matched":0,"requests":133,"coverage":0,"usageSource":"transcript-ratio","breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":133},"logRecords":0,"lastRecordAt":null,"recentRequests":0,"proxyErrors":null,"clientAbort":null,"clientAbortMaxMs":null,"upstreamRejected":null,"aborted":null,"truncated":null,"noUsage":null,"slowestMs":null,"supersededFailure":null},"subagents":{"scanned":false,"dir":null,"probedPaths":["C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\781b04f4-4f2d-4e23-8cd1-38da35646197\\subagents","C:\\Users\\49745\\.qoder-cn\\projects\\781b04f4-4f2d-4e23-8cd1-38da35646197\\subagents"],"reason":"no-dir","count":0,"items":[],"totals":{"roundTrips":0,"billedInputTokens":0,"credits":0,"originalCredits":0},"combined":{"roundTrips":133,"billedInputTokens":21727640,"credits":65.832,"originalCredits":65.832}},"manual":null,"artifacts":{"report":"report.json","canvas":"任务：New Manga _ M2-C1 — T__781b04f4.canvas.tsx"}} as unknown as Report;

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
