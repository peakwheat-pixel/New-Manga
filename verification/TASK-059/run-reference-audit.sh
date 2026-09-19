#!/usr/bin/env bash
# TASK-059 视觉参考自检：
#  1) JS 语法门（无头加载前置）
#  2) 全矩阵审计：6 候选 × 2 主题 × 5 视图 —— 对比度(≥4.5 文本/≥3 非文本，含徽标真实 *-soft 合成底) + 溢出/裁切/重叠
#  3) 无头截图（关键组合，含 DPI 150/200）
# 口径：全部结果为 HTML/Chromium 呈现，非 Qt；不构成任何 D08 AC 的 PASS。
# 标准重跑（R-005 证据纪律：环境头 + 命令 + 输出 + EXIT 同一日志入库）：
#   { echo "== env =="; uname -s; bash --version | head -1; node -v; "$CHROME" --version; \
#     echo "== cmd =="; echo 'bash verification/TASK-059/run-reference-audit.sh'; \
#     echo "== out =="; bash verification/TASK-059/run-reference-audit.sh; \
#     echo "EXIT=$?"; } > verification/TASK-059/audit-result.txt 2>&1
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
REF="$ROOT/doc/design/ui-reference.html"
SHOTS="$HERE/screenshots"
CHROME="${CHROME:-C:/Program Files/Google/Chrome/Application/chrome.exe}"
NODE="${NODE:-node}"
REF_WIN="$(cygpath -m "$REF" 2>/dev/null || echo "$REF")"
REF_URL="file:///$(echo "$REF_WIN" | sed 's|\\|/|g; s|^\(/\+\)\?||; s| |%20|g')"
mkdir -p "$SHOTS"
fail=0

echo "== 1) JS 语法门 =="
"$NODE" -e "
const fs=require('fs');const html=fs.readFileSync(process.argv[1],'utf8');
const m=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if(!m.length){console.error('NO SCRIPT');process.exit(1)}
try{new Function(m[m.length-1][1]);console.log('syntax OK');}catch(e){console.error('SYNTAX ERROR:',e.message);process.exit(1)}
" "$REF" || fail=1

echo "== 2) 全矩阵审计 =="
audit() { # cand mode page
  local out
  out=$("$CHROME" --headless=new --disable-gpu --dump-dom --virtual-time-budget=3500 \
    "${REF_URL}?cand=$1&mode=$2&page=$3&audit=1&win=none" 2>/dev/null | "$NODE" -e "
let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{
  const m=d.match(/<pre id=\"auditOutput\">([\s\S]*?)<\/pre>/);
  if(!m){console.log('NOAUDIT');process.exit(0)}
  const t=m[1].replace(/&quot;/g,'\"').replace(/&amp;/g,'&');
  try{const o=JSON.parse(t);
    const f=o.contrast.filter(r=>!r.pass);
    const ov=o.layout.overlap||0;
    console.log((f.length||o.layout.outside||o.layout.clipped||ov)?'FAIL':'PASS',
      'contrast='+ (o.contrast.length-f.length)+'/'+o.contrast.length,
      'outside='+o.layout.outside,'clipped='+o.layout.clipped,'overlap='+ov,
      f.length?('fails:'+f.map(x=>x.name+'='+x.cr).join(',')):'',
      ov?('overlaps:'+(o.layout.overlapPairs||[]).slice(0,5).join('; ')):'');
  }catch(e){console.log('FAIL parse-error')}
});")
  echo "  $1/$2/$3: $(printf '%s' "$out" | sed 's/[[:space:]]*$//')"
  case "$out" in PASS*) ;; *) fail=1 ;; esac
}
for c in a b c d e f; do for m in dark light; do for p in bookshelf workbench reader settings states; do
  audit "$c" "$m" "$p"
done; done; done

echo "== 3) 无头截图 =="
shot() { # name cand mode page dpi extra
  local q="cand=$2&mode=$3&page=$4"
  [ -n "${5:-}" ] && q="$q&dpi=$5"
  [ -n "${6:-}" ] && q="$q&$6"
  "$CHROME" --headless=new --disable-gpu --screenshot="$SHOTS/$1.png" \
    --window-size=1280,860 --hide-scrollbars --virtual-time-budget=4500 \
    "${REF_URL}?$q" 2>/dev/null
  echo "  $1.png"
}
# 每候选默认主题 × 五视图
shot a-dark-bookshelf  a dark bookshelf
shot a-dark-workbench  a dark workbench
shot a-dark-reader     a dark reader
shot a-dark-settings   a dark settings
shot a-dark-states     a dark states
shot b-light-bookshelf b light bookshelf
shot b-light-workbench b light workbench
shot b-light-reader    b light reader
shot b-light-settings  b light settings
shot b-light-states    b light states
shot c-light-bookshelf c light bookshelf
shot c-light-workbench c light workbench
shot c-light-reader    c light reader
shot c-light-settings  c light settings
shot c-light-states    c light states
# 第二主题代表视图（每候选）
shot a-light-workbench a light workbench
shot b-dark-workbench  b dark workbench
shot c-dark-workbench  c dark workbench
# 玻璃开关对照（C）
shot c-glass-off-bookshelf c light bookshelf "" "glass=off"
shot c-glass-off-workbench c dark workbench "" "glass=off"
# DPI 检查（A dark workbench：150/200 应暴露 frame 容量压力）
shot a-dark-workbench-dpi150 a dark workbench 150
shot a-dark-workbench-dpi200 a dark workbench 200
# 工具窗（TaskDetail 叠开 + 危险确认）
shot a-dark-workbench-taskdetail a dark workbench "" "win=detail"
shot c-glass-taskdetail          c dark workbench "" "win=detail"
shot b-light-danger              b light settings "" "win=danger"
shot c-glass-both                c dark workbench 125 "win=both"
# 候选 D（Vermilion，默认亮色）：五视图 + 第二主题 + 工具窗
shot d-light-bookshelf d light bookshelf
shot d-light-workbench d light workbench
shot d-light-reader    d light reader
shot d-light-settings  d light settings
shot d-light-states    d light states
shot d-dark-workbench  d dark workbench
shot d-light-workbench-taskdetail d light workbench "" "win=detail"
# 候选 E（Amber，默认暗色）：五视图 + 第二主题 + 命令面板
shot e-dark-bookshelf e dark bookshelf
shot e-dark-workbench e dark workbench
shot e-dark-reader    e dark reader
shot e-dark-settings  e dark settings
shot e-dark-states    e dark states
shot e-light-workbench e light workbench
shot e-dark-palette    e dark workbench "" "pal=1"
shot e-dark-workbench-dpi150 e dark workbench 150
# 候选 F（Graphite Atelier，ND-1 组合稿，默认暗色）：五视图 + 第二主题 + DPI + 工具窗
shot f-dark-bookshelf f dark bookshelf
shot f-dark-workbench f dark workbench
shot f-dark-reader    f dark reader
shot f-dark-settings  f dark settings
shot f-dark-states    f dark states
shot f-light-workbench f light workbench
shot f-dark-workbench-dpi150 f dark workbench 150
shot f-dark-workbench-taskdetail f dark workbench "" "win=detail"

echo "== 汇总 =="
if [ "$fail" -eq 0 ]; then echo "AUDIT RESULT: ALL PASS"; else echo "AUDIT RESULT: FAILURES PRESENT"; exit 1; fi
