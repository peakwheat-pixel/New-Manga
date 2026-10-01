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
const REPORT = {"schemaVersion":3.2,"generatedAt":"2026-09-20T08:06:43.236Z","source":"desktop-rich","usageSource":"transcript-ratio","availability":{"credits":"measured","roundTrips":"measured","contextRatio":"measured","tokens":"derived","outputTokens":"unavailable","cachedTokens":"unavailable","categoryShare":"derived","toolShare":"derived","fileShare":"derived","systemPrompt":"derived","contextWindow":"measured","compactions":"measured","compactionCost":"measured","model":"measured","title":"measured","toolCalls":"measured","fileReads":"measured","userTurns":"measured","userContextLimit":"fallback"},"session":{"id":"91b88c8d-cb11-4e01-b83f-bf79144dcc0b","title":"接下来的任务不要保存在项目目录，另存在项目之外，","titleSource":"first-user","model":"qfmodel","modelSource":"runtime-config","cwd":"G:\\CODEX\\New Manga","turns":6,"roundTrips":109,"compactions":0,"startedAt":"2026-09-20T06:50:41.661Z","endedAt":"2026-09-20T08:06:42.973Z"},"context":{"contextWindow":400000,"contextWindowSource":"runtime-config","systemPromptTokens":19640,"netContextTokens":249539,"peakContextTokens":249539,"peakContextRatio":0.6238475,"peakSessionTokens":249539,"peakSessionRatio":0.6238475,"peakSessionNotable":false,"peakAdvice":{"level":"mid","tone":"info","text":"已过盈亏线（39%）但还没进性价比区间，压缩有净收益但不大；不急着压"},"userContextLimit":200000,"userContextLimitSource":"default","peakUserRatio":1.247695,"peakUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"currentContextTokens":249539,"netUserRatio":1.247695,"netUserAdvice":{"level":"over","tone":"danger","text":"已经超过上下文窗口本身，随时可能被截断或由客户端在最糟的时机自动压缩，立刻手动压一次"},"netWindowRatio":0.6238475,"observedAutoCompactions":0,"observedAutoTriggerTokens":null,"autoTriggerRatio":null,"thresholdNotEnforced":true},"totals":{"billedInputTokens":17325075,"netContextTokens":249539,"peakContextTokens":249539,"amplification":69.43,"attributedTokens":17325075,"coverage":1,"credits":57.879,"originalCredits":57.879,"outputTokens":0,"cachedTokens":0,"cachedTrips":0,"cachedShare":0,"toolCalls":124,"fileReads":49},"creditsCoverage":{"trips":109,"roundTrips":109,"tokens":17325075,"tokenShare":1,"full":true},"compactionCost":{"count":0,"items":[],"totals":{"preTokens":0,"postTokens":0,"savedTokens":0,"measured":0}},"proxy":{"matched":0,"requests":109,"breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":109},"logPath":"C:\\Users\\49745\\.qoder-credits-proxy\\usage.jsonl","logExists":false,"logRecords":0,"configured":false,"enabled":true,"port":49787,"lastRecordAt":null,"dormant":false,"status":null,"statusSuperseded":false},"byCategory":[{"key":"tool_result","label":"工具返回","tokens":5689888,"share":0.3284192369478835},{"key":"system","label":"系统提示词","tokens":2140760,"share":0.12356425585459226},{"key":"assistant_thinking","label":"模型思考","tokens":2670150,"share":0.15412052154925165},{"key":"assistant_tool_use","label":"工具调用","tokens":2731971,"share":0.15768883601082345},{"key":"assistant_text","label":"模型回复","tokens":354189,"share":0.020443729426248548},{"key":"user_input","label":"用户输入","tokens":37945,"share":0.002190166707209335},{"key":"attachment","label":"附件/技能","tokens":3700173,"share":0.2135732535039918}],"byCategoryDetail":[{"key":"tool_result","label":"工具返回","tokens":5689888,"share":0.3284192369478835,"children":[{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":2737560,"share":0.1580114120770549,"catShare":0.48112715182432986,"trips":3822},{"tool":"Read","label":"doc/tasks/README.md","kind":"read","tokens":760884,"share":0.043918100492129984,"catShare":0.13372572477872025,"trips":70},{"tool":"Read","label":"doc/00_INDEX.md","kind":"read","tokens":484492,"share":0.02796480687842549,"catShare":0.08514972246544496,"trips":74},{"tool":"Read","label":"doc/12_ROADMAP.md","kind":"read","tokens":470076,"share":0.027132723708735096,"catShare":0.08261612188399535,"trips":74},{"tool":"Read","label":"C:/Users/49745/Downloads/03_STAGE3_Sol_Final_Project_Rebaseline.md","kind":"read","tokens":445923,"share":0.025738579582709798,"catShare":0.07837110828801488,"trips":99},{"tool":"Read","label":"C:/Users/49745/Downloads/01_STAGE1_Luna_Repository_Reality_Inventory.md","kind":"read","tokens":245286,"share":0.014157858170463807,"catShare":0.04310910134874499,"trips":99},{"tool":"Read","label":"C:/Users/49745/Downloads/02_STAGE2_Sol_Task_Closure_Dependency_Audit.md","kind":"read","tokens":240287,"share":0.013869323775141714,"catShare":0.042230546249465345,"trips":99},{"tool":"Grep","label":"doc/09_COLLABORATION.md","kind":"search","tokens":76859,"share":0.004436307101197977,"catShare":0.013508061045467838,"trips":108},{"tool":"Agent","label":"（无路径）","kind":"other","tokens":66700,"share":0.003849919722253623,"catShare":0.01172257678335865,"trips":341},{"tool":"Read","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/01_STAGE1_Repository_Reality_Inventory.md","kind":"read","tokens":42477,"share":0.002451779091794835,"catShare":0.007465394276474448,"trips":93},{"tool":"Read","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"read","tokens":36800,"share":0.0021240829069086187,"catShare":0.006467595889474913,"trips":109},{"tool":"Edit","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/01_STAGE1_Repository_Reality_Inventory.md","kind":"write","tokens":30052,"share":0.001734624417898067,"catShare":0.00528173816497032,"trips":662},{"tool":"AskUserQuestion","label":"（无路径）","kind":"other","tokens":10182,"share":0.0005877312731663186,"catShare":0.0017895762703437042,"trips":101},{"tool":"TaskCreate","label":"（无路径）","kind":"other","tokens":7736,"share":0.0004465400568167399,"catShare":0.0013596647412209926,"trips":285},{"tool":"Edit","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/02_STAGE2_Task_Closure_Dependency_Drift_Audit.md","kind":"write","tokens":7710,"share":0.0004450407595849247,"catShare":0.0013550995481289292,"trips":119},{"tool":null,"label":"其他 16 项","kind":null,"tokens":26861,"share":0.0015504069336017168,"catShare":0.004720816441844876,"trips":942}]},{"key":"system","label":"系统提示词","tokens":2140760,"share":0.12356425585459226,"children":[]},{"key":"assistant_thinking","label":"模型思考","tokens":2670150,"share":0.15412052154925165,"children":[]},{"key":"assistant_tool_use","label":"工具调用","tokens":2731971,"share":0.15768883601082345,"children":[{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/01_STAGE1_Repository_Reality_Inventory.md","kind":"write","tokens":602149,"share":0.034755910846971785,"catShare":0.22040818948391633,"trips":57},{"tool":"Bash","label":"（无路径）","kind":"shell","tokens":500376,"share":0.028881597670484774,"catShare":0.18315562725380508,"trips":3822},{"tool":"Edit","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/01_STAGE1_Repository_Reality_Inventory.md","kind":"write","tokens":415585,"share":0.023987460064549108,"catShare":0.15211894939032117,"trips":662},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/02_STAGE2_Task_Closure_Dependency_Drift_Audit.md","kind":"write","tokens":333662,"share":0.01925891671687512,"catShare":0.12213240457652452,"trips":29},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/03_STAGE3_Final_Project_Rebaseline.md","kind":"write","tokens":220629,"share":0.012734651177005814,"catShare":0.08075810247043572,"trips":22},{"tool":"Agent","label":"（无路径）","kind":"other","tokens":190887,"share":0.01101793265679065,"catShare":0.06987135510363209,"trips":341},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/00_BASELINE.md","kind":"write","tokens":95350,"share":0.005503594463642285,"catShare":0.0349016113180297,"trips":79},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/_evidence/qml-binding-dead-ends.md","kind":"write","tokens":53728,"share":0.0031011753747506115,"catShare":0.01966642314829284,"trips":64},{"tool":"Write","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/output-outside-repo.md","kind":"write","tokens":45351,"share":0.002617641339473675,"catShare":0.01660004224581888,"trips":105},{"tool":"Edit","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/02_STAGE2_Task_Closure_Dependency_Drift_Audit.md","kind":"write","tokens":40109,"share":0.0023150820994264493,"catShare":0.014681331652847933,"trips":119},{"tool":"TaskCreate","label":"（无路径）","kind":"other","tokens":38682,"share":0.0022327002840837004,"catShare":0.01415889888318062,"trips":285},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/_evidence/slot_binding_audit.py","kind":"write","tokens":38170,"share":0.0022031748620004723,"catShare":0.013971660377081169,"trips":67},{"tool":"AskUserQuestion","label":"（无路径）","kind":"other","tokens":36796,"share":0.0021238471007601063,"catShare":0.013468595206158599,"trips":101},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/00_README_交付与自检.md","kind":"write","tokens":32281,"share":0.0018632304038673725,"catShare":0.01181586757187734,"trips":10},{"tool":"Write","label":"G:/CODEX/New Manga.qoder-output/README.md","kind":"write","tokens":29050,"share":0.0016767474717111134,"catShare":0.01063326684455978,"trips":106},{"tool":null,"label":"其他 16 项","kind":null,"tokens":59168,"share":0.003415173478430828,"catShare":0.02165767447352086,"trips":1228}]},{"key":"assistant_text","label":"模型回复","tokens":354189,"share":0.020443729426248548,"children":[]},{"key":"user_input","label":"用户输入","tokens":37945,"share":0.002190166707209335,"children":[]},{"key":"attachment","label":"附件/技能","tokens":3700173,"share":0.2135732535039918,"children":[]}],"byTool":[{"tool":"Bash","tokens":3237935,"calls":62,"perCall":52225,"share":0.18689300974753925},{"tool":"Read","tokens":2746197,"calls":11,"perCall":249654,"share":0.15850995658228623},{"tool":"Write","tokens":1470415,"calls":10,"perCall":147042,"share":0.08487208928254503},{"tool":"Edit","tokens":524917,"calls":26,"perCall":20189,"share":0.030298104981933853},{"tool":"Agent","tokens":257587,"calls":4,"perCall":64397,"share":0.014867852379044231},{"tool":"Grep","tokens":88451,"calls":2,"perCall":44225,"share":0.005105372759077626},{"tool":"AskUserQuestion","tokens":46978,"calls":1,"perCall":46978,"share":0.0027115783739264255},{"tool":"TaskCreate","tokens":46418,"calls":3,"perCall":15473,"share":0.0026792403409004375},{"tool":"TaskUpdate","tokens":2960,"calls":5,"perCall":592,"share":0.00017086851145367183}],"byFile":[{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\01_STAGE1_Repository_Reality_Inventory.md","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/01_STAGE1_Repository_Reality_Inventory.md","kind":"write","tool":"Write","selfTokens":19138,"reads":19,"trips":1624,"billed":1095923,"perRead":57680,"share":0.06325647390772524},{"attr":"file:G:\\CODEX\\New Manga\\doc\\tasks\\README.md","label":"doc/tasks/README.md","kind":"read","tool":"Read","selfTokens":9552,"reads":1,"trips":140,"billed":762081,"perRead":762081,"share":0.04398717583106066},{"attr":"file:G:\\CODEX\\New Manga\\doc\\00_INDEX.md","label":"doc/00_INDEX.md","kind":"read","tool":"Read","selfTokens":5761,"reads":1,"trips":148,"billed":485673,"perRead":485673,"share":0.028032930646704247},{"attr":"file:G:\\CODEX\\New Manga\\doc\\12_ROADMAP.md","label":"doc/12_ROADMAP.md","kind":"read","tool":"Read","selfTokens":5590,"reads":1,"trips":148,"billed":471257,"perRead":471257,"share":0.027200847477013852},{"attr":"file:C:\\Users\\49745\\Downloads\\03_STAGE3_Sol_Final_Project_Rebaseline.md","label":"C:/Users/49745/Downloads/03_STAGE3_Sol_Final_Project_Rebaseline.md","kind":"read","tool":"Read","selfTokens":3947,"reads":1,"trips":198,"billed":448422,"perRead":448422,"share":0.02588284678037084},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\02_STAGE2_Task_Closure_Dependency_Drift_Audit.md","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/02_STAGE2_Task_Closure_Dependency_Drift_Audit.md","kind":"write","tool":"Write","selfTokens":11970,"reads":6,"trips":296,"billed":382569,"perRead":63761,"share":0.022081790785568253},{"attr":"file:C:\\Users\\49745\\Downloads\\01_STAGE1_Luna_Repository_Reality_Inventory.md","label":"C:/Users/49745/Downloads/01_STAGE1_Luna_Repository_Reality_Inventory.md","kind":"read","tool":"Read","selfTokens":2182,"reads":1,"trips":198,"billed":247899,"perRead":247899,"share":0.014308682968018542},{"attr":"file:C:\\Users\\49745\\Downloads\\02_STAGE2_Sol_Task_Closure_Dependency_Audit.md","label":"C:/Users/49745/Downloads/02_STAGE2_Sol_Task_Closure_Dependency_Audit.md","kind":"read","tool":"Read","selfTokens":2138,"reads":1,"trips":198,"billed":242900,"perRead":242900,"share":0.014020148572696447},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\03_STAGE3_Final_Project_Rebaseline.md","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/03_STAGE3_Final_Project_Rebaseline.md","kind":"write","tool":"Write","selfTokens":8852,"reads":1,"trips":44,"billed":221379,"perRead":221379,"share":0.012777956497263146},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\00_BASELINE.md","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/00_BASELINE.md","kind":"write","tool":"Write","selfTokens":1083,"reads":1,"trips":158,"billed":97603,"perRead":97603,"share":0.005633641591800182},{"attr":"file:G:\\CODEX\\New Manga\\doc\\09_COLLABORATION.md","label":"doc/09_COLLABORATION.md","kind":"search","tool":"Grep","selfTokens":663,"reads":1,"trips":216,"billed":81663,"perRead":81663,"share":0.004713576295022852},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\MEMORY.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/MEMORY.md","kind":"read","tool":"Read","selfTokens":1151,"reads":4,"trips":428,"billed":66618,"perRead":16655,"share":0.003845201004376356},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\_evidence\\qml-binding-dead-ends.md","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/_evidence/qml-binding-dead-ends.md","kind":"write","tool":"Write","selfTokens":767,"reads":1,"trips":128,"billed":55915,"perRead":55915,"share":0.0032274104646319124},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\output-outside-repo.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/output-outside-repo.md","kind":"write","tool":"Write","selfTokens":406,"reads":1,"trips":210,"billed":48710,"perRead":48710,"share":0.002811540697953206},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\_evidence\\slot_binding_audit.py","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/_evidence/slot_binding_audit.py","kind":"write","tool":"Write","selfTokens":529,"reads":1,"trips":134,"billed":40384,"perRead":40384,"share":0.0023309590039965007},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\REBASELINE-2026-09-20\\00_README_交付与自检.md","label":"G:/CODEX/New Manga.qoder-output/REBASELINE-2026-09-20/00_README_交付与自检.md","kind":"write","tool":"Write","selfTokens":3187,"reads":3,"trips":50,"billed":35395,"perRead":11798,"share":0.0020429976712163928},{"attr":"file:G:\\CODEX\\New Manga.qoder-output\\README.md","label":"G:/CODEX/New Manga.qoder-output/README.md","kind":"write","tool":"Write","selfTokens":258,"reads":1,"trips":212,"billed":31229,"perRead":31229,"share":0.0018025035320894474},{"attr":"file:G:\\CODEX\\New Manga\\doc","label":"doc","kind":"search","tool":"Grep","selfTokens":61,"reads":1,"trips":194,"billed":6788,"perRead":6788,"share":0.00039179646405477245},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\verification-environment.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/verification-environment.md","kind":"read","tool":"Read","selfTokens":988,"reads":2,"trips":14,"billed":3921,"perRead":1960,"share":0.0002263036929156476},{"attr":"file:C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\memory\\rebaseline-audit-2026-09-20.md","label":"C:/Users/49745/.qoder-cn/projects/G--CODEX-New-Manga/memory/rebaseline-audit-2026-09-20.md","kind":"write","tool":"Write","selfTokens":534,"reads":1,"trips":12,"billed":3651,"perRead":3651,"share":0.0002107397213649066}],"byAttr":[{"attr":"attachment","tokens":3700173,"share":0.2135732535039918},{"attr":"tool_result|Bash","tokens":2737560,"share":0.1580114120770549},{"attr":"tool_result|Read","tokens":2728273,"share":0.15747537145441684},{"attr":"assistant_thinking","tokens":2670150,"share":0.15412052154925165},{"attr":"system","tokens":2140760,"share":0.12356425585459226},{"attr":"tool_use|Write","tokens":1453815,"share":0.08391394306747414},{"attr":"tool_use|Bash","tokens":500376,"share":0.028881597670484774},{"attr":"tool_use|Edit","tokens":480569,"share":0.02773833491002265},{"attr":"assistant_text","tokens":354189,"share":0.020443729426248548},{"attr":"tool_use|Agent","tokens":190887,"share":0.01101793265679065},{"attr":"tool_result|Grep","tokens":77304,"share":0.004461998672611405},{"attr":"tool_result|Agent","tokens":66700,"share":0.003849919722253623},{"attr":"tool_result|Edit","tokens":44348,"share":0.002559770071911162},{"attr":"tool_use|TaskCreate","tokens":38682,"share":0.0022327002840837004},{"attr":"user_input","tokens":37945,"share":0.002190166707209335},{"attr":"tool_use|AskUserQuestion","tokens":36796,"share":0.0021238471007601063},{"attr":"tool_use|Read","tokens":17924,"share":0.0010345851278694314},{"attr":"tool_result|Write","tokens":16600,"share":0.0009581462150708774},{"attr":"tool_use|Grep","tokens":11147,"share":0.0006433740864662185},{"attr":"tool_result|AskUserQuestion","tokens":10182,"share":0.0005877312731663186},{"attr":"tool_result|TaskCreate","tokens":7736,"share":0.0004465400568167399},{"attr":"tool_use|TaskUpdate","tokens":1776,"share":0.00010252110687220303},{"attr":"tool_result|TaskUpdate","tokens":1184,"share":0.00006834740458146883}],"byRequest":[{"index":1,"time":"14:51","ratio":0.079007,"inputTokens":31603,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.933,"originalCredits":0.933,"afterCompact":false},{"index":2,"time":"14:51","ratio":0.092198,"inputTokens":36879,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.263,"originalCredits":0.263,"afterCompact":false},{"index":3,"time":"14:51","ratio":0.094253,"inputTokens":37701,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.123,"originalCredits":0.123,"afterCompact":false},{"index":4,"time":"14:51","ratio":0.09511,"inputTokens":38044,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.118,"originalCredits":0.118,"afterCompact":false},{"index":5,"time":"14:53","ratio":0.096547,"inputTokens":38619,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.09,"originalCredits":0.09,"afterCompact":false},{"index":6,"time":"14:53","ratio":0.09739,"inputTokens":38956,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.114,"originalCredits":0.114,"afterCompact":false},{"index":7,"time":"14:54","ratio":0.099187,"inputTokens":39675,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.139,"originalCredits":0.139,"afterCompact":false},{"index":8,"time":"14:56","ratio":0.10448,"inputTokens":41792,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.216,"originalCredits":0.216,"afterCompact":false},{"index":9,"time":"14:59","ratio":0.107772,"inputTokens":43109,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.16,"originalCredits":0.16,"afterCompact":false},{"index":10,"time":"15:00","ratio":0.113202,"inputTokens":45281,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.176,"originalCredits":0.176,"afterCompact":false},{"index":11,"time":"15:01","ratio":0.144803,"inputTokens":57921,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.566,"originalCredits":0.566,"afterCompact":false},{"index":12,"time":"15:02","ratio":0.172937,"inputTokens":69175,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.192,"originalCredits":0.192,"afterCompact":false},{"index":13,"time":"15:04","ratio":0.176292,"inputTokens":70517,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.448,"originalCredits":0.448,"afterCompact":false},{"index":14,"time":"15:13","ratio":0.191165,"inputTokens":76466,"outputTokens":null,"usageSource":"transcript-ratio","credits":2.228,"originalCredits":2.228,"afterCompact":false},{"index":15,"time":"15:13","ratio":0.195722,"inputTokens":78289,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.244,"originalCredits":0.244,"afterCompact":false},{"index":16,"time":"15:13","ratio":0.197963,"inputTokens":79185,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.252,"originalCredits":0.252,"afterCompact":false},{"index":17,"time":"15:14","ratio":0.212613,"inputTokens":85045,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.441,"originalCredits":0.441,"afterCompact":false},{"index":18,"time":"15:14","ratio":0.21894,"inputTokens":87576,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.279,"originalCredits":0.279,"afterCompact":false},{"index":19,"time":"15:14","ratio":0.221608,"inputTokens":88643,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.247,"originalCredits":0.247,"afterCompact":false},{"index":20,"time":"15:14","ratio":0.223337,"inputTokens":89335,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.226,"originalCredits":0.226,"afterCompact":false},{"index":21,"time":"15:15","ratio":0.224545,"inputTokens":89818,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.236,"originalCredits":0.236,"afterCompact":false},{"index":22,"time":"15:16","ratio":0.226062,"inputTokens":90425,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.245,"originalCredits":0.245,"afterCompact":false},{"index":23,"time":"15:16","ratio":0.227575,"inputTokens":91030,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.291,"originalCredits":0.291,"afterCompact":false},{"index":24,"time":"15:17","ratio":0.232242,"inputTokens":92897,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.304,"originalCredits":0.304,"afterCompact":false},{"index":25,"time":"15:17","ratio":0.235797,"inputTokens":94319,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.292,"originalCredits":0.292,"afterCompact":false},{"index":26,"time":"15:17","ratio":0.238278,"inputTokens":95311,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.272,"originalCredits":0.272,"afterCompact":false},{"index":27,"time":"15:18","ratio":0.242297,"inputTokens":96919,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.3,"originalCredits":0.3,"afterCompact":false},{"index":28,"time":"15:18","ratio":0.244693,"inputTokens":97877,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.276,"originalCredits":0.276,"afterCompact":false},{"index":29,"time":"15:18","ratio":0.247048,"inputTokens":98819,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.275,"originalCredits":0.275,"afterCompact":false},{"index":30,"time":"15:19","ratio":0.249163,"inputTokens":99665,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.34,"originalCredits":0.34,"afterCompact":false},{"index":31,"time":"15:19","ratio":0.253327,"inputTokens":101331,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.29,"originalCredits":0.29,"afterCompact":false},{"index":32,"time":"15:19","ratio":0.257362,"inputTokens":102945,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.299,"originalCredits":0.299,"afterCompact":false},{"index":33,"time":"15:20","ratio":0.259018,"inputTokens":103607,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.286,"originalCredits":0.286,"afterCompact":false},{"index":34,"time":"15:22","ratio":0.281652,"inputTokens":112661,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.503,"originalCredits":0.503,"afterCompact":false},{"index":35,"time":"15:23","ratio":0.288315,"inputTokens":115326,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.355,"originalCredits":0.355,"afterCompact":false},{"index":36,"time":"15:23","ratio":0.319603,"inputTokens":127841,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.65,"originalCredits":0.65,"afterCompact":false},{"index":37,"time":"15:24","ratio":0.322605,"inputTokens":129042,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.357,"originalCredits":0.357,"afterCompact":false},{"index":38,"time":"15:24","ratio":0.32591,"inputTokens":130364,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.356,"originalCredits":0.356,"afterCompact":false},{"index":39,"time":"15:25","ratio":0.340373,"inputTokens":136149,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.469,"originalCredits":0.469,"afterCompact":false},{"index":40,"time":"15:25","ratio":0.372435,"inputTokens":148974,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.698,"originalCredits":0.698,"afterCompact":false},{"index":41,"time":"15:25","ratio":0.375128,"inputTokens":150051,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.392,"originalCredits":0.392,"afterCompact":false},{"index":42,"time":"15:25","ratio":0.376968,"inputTokens":150787,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.411,"originalCredits":0.411,"afterCompact":false},{"index":43,"time":"15:26","ratio":0.379462,"inputTokens":151785,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.383,"originalCredits":0.383,"afterCompact":false},{"index":44,"time":"15:26","ratio":0.381877,"inputTokens":152751,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.389,"originalCredits":0.389,"afterCompact":false},{"index":45,"time":"15:26","ratio":0.383655,"inputTokens":153462,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.436,"originalCredits":0.436,"afterCompact":false},{"index":46,"time":"15:26","ratio":0.38701,"inputTokens":154804,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.41,"originalCredits":0.41,"afterCompact":false},{"index":47,"time":"15:27","ratio":0.3889,"inputTokens":155560,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.386,"originalCredits":0.386,"afterCompact":false},{"index":48,"time":"15:27","ratio":0.39212,"inputTokens":156848,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.418,"originalCredits":0.418,"afterCompact":false},{"index":49,"time":"15:28","ratio":0.394377,"inputTokens":157751,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.396,"originalCredits":0.396,"afterCompact":false},{"index":50,"time":"15:28","ratio":0.395788,"inputTokens":158315,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.387,"originalCredits":0.387,"afterCompact":false},{"index":51,"time":"15:28","ratio":0.399685,"inputTokens":159874,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.449,"originalCredits":0.449,"afterCompact":false},{"index":52,"time":"15:31","ratio":0.402805,"inputTokens":161122,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.097,"originalCredits":1.097,"afterCompact":false},{"index":53,"time":"15:31","ratio":0.43779,"inputTokens":175116,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.827,"originalCredits":0.827,"afterCompact":false},{"index":54,"time":"15:31","ratio":0.441933,"inputTokens":176773,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.473,"originalCredits":0.473,"afterCompact":false},{"index":55,"time":"15:32","ratio":0.445792,"inputTokens":178317,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.466,"originalCredits":0.466,"afterCompact":false},{"index":56,"time":"15:33","ratio":0.448965,"inputTokens":179586,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.495,"originalCredits":0.495,"afterCompact":false},{"index":57,"time":"15:33","ratio":0.45182,"inputTokens":180728,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.542,"originalCredits":0.542,"afterCompact":false},{"index":58,"time":"15:33","ratio":0.456675,"inputTokens":182670,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.465,"originalCredits":0.465,"afterCompact":false},{"index":59,"time":"15:34","ratio":0.45769,"inputTokens":183076,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.439,"originalCredits":0.439,"afterCompact":false},{"index":60,"time":"15:34","ratio":0.46041,"inputTokens":184164,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.562,"originalCredits":0.562,"afterCompact":false},{"index":61,"time":"15:34","ratio":0.465757,"inputTokens":186303,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.513,"originalCredits":0.513,"afterCompact":false},{"index":62,"time":"15:34","ratio":0.467747,"inputTokens":187099,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.462,"originalCredits":0.462,"afterCompact":false},{"index":63,"time":"15:35","ratio":0.468958,"inputTokens":187583,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.459,"originalCredits":0.459,"afterCompact":false},{"index":64,"time":"15:35","ratio":0.470753,"inputTokens":188301,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.449,"originalCredits":0.449,"afterCompact":false},{"index":65,"time":"15:35","ratio":0.472135,"inputTokens":188854,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.472,"originalCredits":0.472,"afterCompact":false},{"index":66,"time":"15:35","ratio":0.473863,"inputTokens":189545,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.447,"originalCredits":0.447,"afterCompact":false},{"index":67,"time":"15:35","ratio":0.474765,"inputTokens":189906,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.479,"originalCredits":0.479,"afterCompact":false},{"index":68,"time":"15:36","ratio":0.476913,"inputTokens":190765,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.466,"originalCredits":0.466,"afterCompact":false},{"index":69,"time":"15:36","ratio":0.477895,"inputTokens":191158,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.45,"originalCredits":0.45,"afterCompact":false},{"index":70,"time":"15:37","ratio":0.478693,"inputTokens":191477,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.496,"originalCredits":0.496,"afterCompact":false},{"index":71,"time":"15:37","ratio":0.481442,"inputTokens":192577,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.489,"originalCredits":0.489,"afterCompact":false},{"index":72,"time":"15:37","ratio":0.482973,"inputTokens":193189,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.476,"originalCredits":0.476,"afterCompact":false},{"index":73,"time":"15:37","ratio":0.48442,"inputTokens":193768,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.502,"originalCredits":0.502,"afterCompact":false},{"index":74,"time":"15:37","ratio":0.487355,"inputTokens":194942,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.491,"originalCredits":0.491,"afterCompact":false},{"index":75,"time":"15:38","ratio":0.48866,"inputTokens":195464,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.502,"originalCredits":0.502,"afterCompact":false},{"index":76,"time":"15:38","ratio":0.493053,"inputTokens":197221,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.529,"originalCredits":0.529,"afterCompact":false},{"index":77,"time":"15:45","ratio":0.500008,"inputTokens":200003,"outputTokens":null,"usageSource":"transcript-ratio","credits":5.582,"originalCredits":5.582,"afterCompact":false},{"index":78,"time":"15:46","ratio":0.503885,"inputTokens":201554,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.547,"originalCredits":0.547,"afterCompact":false},{"index":79,"time":"15:46","ratio":0.507912,"inputTokens":203165,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.556,"originalCredits":0.556,"afterCompact":false},{"index":80,"time":"15:51","ratio":0.510922,"inputTokens":204369,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.175,"originalCredits":1.175,"afterCompact":false},{"index":81,"time":"15:51","ratio":0.539855,"inputTokens":215942,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.796,"originalCredits":0.796,"afterCompact":false},{"index":82,"time":"15:52","ratio":0.54155,"inputTokens":216620,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.532,"originalCredits":0.532,"afterCompact":false},{"index":83,"time":"15:52","ratio":0.543138,"inputTokens":217255,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.543,"originalCredits":0.543,"afterCompact":false},{"index":84,"time":"15:52","ratio":0.54515,"inputTokens":218060,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.526,"originalCredits":0.526,"afterCompact":false},{"index":85,"time":"15:52","ratio":0.54621,"inputTokens":218484,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.508,"originalCredits":0.508,"afterCompact":false},{"index":86,"time":"15:53","ratio":0.546878,"inputTokens":218751,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.585,"originalCredits":0.585,"afterCompact":false},{"index":87,"time":"15:56","ratio":0.550772,"inputTokens":220309,"outputTokens":null,"usageSource":"transcript-ratio","credits":1.075,"originalCredits":1.075,"afterCompact":false},{"index":88,"time":"15:56","ratio":0.573645,"inputTokens":229458,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.776,"originalCredits":0.776,"afterCompact":false},{"index":89,"time":"15:57","ratio":0.575295,"inputTokens":230118,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.628,"originalCredits":0.628,"afterCompact":false},{"index":90,"time":"15:58","ratio":0.584475,"inputTokens":233790,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.665,"originalCredits":0.665,"afterCompact":false},{"index":91,"time":"15:58","ratio":0.587313,"inputTokens":234925,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.561,"originalCredits":0.561,"afterCompact":false},{"index":92,"time":"15:58","ratio":0.588442,"inputTokens":235377,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.587,"originalCredits":0.587,"afterCompact":false},{"index":93,"time":"16:00","ratio":0.59087,"inputTokens":236348,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.57,"originalCredits":0.57,"afterCompact":false},{"index":94,"time":"16:00","ratio":0.592032,"inputTokens":236813,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.571,"originalCredits":0.571,"afterCompact":false},{"index":95,"time":"16:00","ratio":0.594045,"inputTokens":237618,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.573,"originalCredits":0.573,"afterCompact":false},{"index":96,"time":"16:01","ratio":0.595352,"inputTokens":238141,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.598,"originalCredits":0.598,"afterCompact":false},{"index":97,"time":"16:01","ratio":0.598535,"inputTokens":239414,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.581,"originalCredits":0.581,"afterCompact":false},{"index":98,"time":"16:01","ratio":0.599775,"inputTokens":239910,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.563,"originalCredits":0.563,"afterCompact":false},{"index":99,"time":"16:02","ratio":0.602087,"inputTokens":240835,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.752,"originalCredits":0.752,"afterCompact":false},{"index":100,"time":"16:03","ratio":0.610275,"inputTokens":244110,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.647,"originalCredits":0.647,"afterCompact":false},{"index":101,"time":"16:03","ratio":0.611635,"inputTokens":244654,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.579,"originalCredits":0.579,"afterCompact":false},{"index":102,"time":"16:03","ratio":0.612707,"inputTokens":245083,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.577,"originalCredits":0.577,"afterCompact":false},{"index":103,"time":"16:04","ratio":0.613765,"inputTokens":245506,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.611,"originalCredits":0.611,"afterCompact":false},{"index":104,"time":"16:04","ratio":0.616235,"inputTokens":246494,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.579,"originalCredits":0.579,"afterCompact":false},{"index":105,"time":"16:04","ratio":0.617275,"inputTokens":246910,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.572,"originalCredits":0.572,"afterCompact":false},{"index":106,"time":"16:05","ratio":0.618953,"inputTokens":247581,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.598,"originalCredits":0.598,"afterCompact":false},{"index":107,"time":"16:05","ratio":0.620413,"inputTokens":248165,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.587,"originalCredits":0.587,"afterCompact":false},{"index":108,"time":"16:06","ratio":0.622378,"inputTokens":248951,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.584,"originalCredits":0.584,"afterCompact":false},{"index":109,"time":"16:06","ratio":0.623847,"inputTokens":249539,"outputTokens":null,"usageSource":"transcript-ratio","credits":0.639,"originalCredits":0.639,"afterCompact":false}],"identity":{"sumAttributed":17325075,"billedInputTokens":17325075,"absDiff":0,"ok":true},"pluginVersion":"2.7.4","selfCmd":"\"C:\\Users\\49745\\.qoder-cn\\plugins\\cache\\qoder-marketplace\\qoder-credits-inspector\\2.7.4\\bin\\credits-inspector.cmd\" cli","linkHealth":{"matched":0,"requests":109,"coverage":0,"usageSource":"transcript-ratio","breakdown":{"proxy":0,"transcriptTokens":0,"transcriptRatio":109},"logRecords":0,"lastRecordAt":null,"recentRequests":0,"proxyErrors":null,"clientAbort":null,"clientAbortMaxMs":null,"upstreamRejected":null,"aborted":null,"truncated":null,"noUsage":null,"slowestMs":null,"supersededFailure":null},"subagents":{"scanned":true,"dir":"C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\91b88c8d-cb11-4e01-b83f-bf79144dcc0b\\subagents","probedPaths":["C:\\Users\\49745\\.qoder-cn\\projects\\G--CODEX-New-Manga\\91b88c8d-cb11-4e01-b83f-bf79144dcc0b\\subagents","C:\\Users\\49745\\.qoder-cn\\projects\\91b88c8d-cb11-4e01-b83f-bf79144dcc0b\\subagents"],"reason":"ok","count":4,"items":[{"agentId":"aExplore-36dbc41025129c79","agentType":"Explore","description":"Map translation pipeline closure","toolUseId":"call_9a6388e8bcd740cf8d982867","roundTrips":37,"billedInputTokens":1210287,"peakContextRatio":0.2376,"credits":8.459,"originalCredits":8.459,"error":null},{"agentId":"aExplore-b6ba2514b9c1f9d5","agentType":"Explore","description":"Map library import reader closure","toolUseId":"call_a19bfa976d334030ac984bb0","roundTrips":23,"billedInputTokens":666870,"peakContextRatio":0.2036,"credits":5.397,"originalCredits":5.397,"error":null},{"agentId":"aExplore-098e97da290a5077","agentType":"Explore","description":"Map settings db packaging closure","toolUseId":"call_632355c4bd3d454d864f77e2","roundTrips":20,"billedInputTokens":361242,"peakContextRatio":0.1261,"credits":3.333,"originalCredits":3.333,"error":null},{"agentId":"aExplore-72d1b06fe8b24f97","agentType":"Explore","description":"Audit docs layer claims","toolUseId":"call_ac633e5adb764ba1b3a6fabd","roundTrips":5,"billedInputTokens":67456,"peakContextRatio":0.1048,"credits":1.228,"originalCredits":1.228,"error":null}],"totals":{"roundTrips":85,"billedInputTokens":2305855,"credits":18.417,"originalCredits":18.417},"combined":{"roundTrips":194,"billedInputTokens":19630930,"credits":76.296,"originalCredits":76.296}},"manual":null,"artifacts":{"report":"report.json","canvas":"接下来的任务不要保存在项目目录，另存在项目之外，__91b88c8d.canvas.tsx"}} as unknown as Report;

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
