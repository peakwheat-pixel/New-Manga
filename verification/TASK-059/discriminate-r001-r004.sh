#!/usr/bin/env bash
# TASK-059 R-001/R-004 判别力验证（Q-009：判别证据必须是 artefact）。
# 从当前 ui-reference.html 派生两个临时判别副本，在无头 Chrome 中验证：
#  D1（R-001）：把 A 亮色 --st-warn-t 回退到修前值 #9a6700 → 徽标对 badge-warn/st-warn-t 应 FAIL（约 4.22:1）
#  D2（R-004）：向 states 页注入两个相交徽标 → layout.overlap 应 ≥1 并输出相交元素对
#  D3（R3-001，ND-1 组合稿 F）：把 --st-skip 注入低对比回归值 → F 专属对 st-skip-direct/panel 应 FAIL
# 本脚本不修改仓库文件；判别副本写入系统临时目录。
# 判定通过 = 两个检测各至少报出一次 FAIL；审计全绿矩阵另见 run-reference-audit.sh。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
REF="$ROOT/doc/design/ui-reference.html"
CHROME="${CHROME:-C:/Program Files/Google/Chrome/Application/chrome.exe}"
NODE="${NODE:-node}"
PYTHON="${PYTHON:-python}"

REF_WIN="$(cygpath -m "$REF" 2>/dev/null || echo "$REF")"
REF_URL="file:///$(echo "$REF_WIN" | sed 's|\\|/|g; s|^\(/\+\)\?||; s| |%20|g')"

TMPDIR_OUT="$("$PYTHON" - "$REF" <<'EOF'
# -*- coding: utf-8 -*-
import re, sys, tempfile
from pathlib import Path
src = Path(sys.argv[1]).read_text(encoding="utf-8")
tmp = Path(tempfile.gettempdir()) / "t059-discrim"
tmp.mkdir(exist_ok=True)

NEW_ROW = ("--st-ok:#1a7f37; --st-ok-t:#116329; --st-run:#0550ae; "
           "--st-warn:#9a6700; --st-warn-t:#7d5200;")
OLD_ROW = ("--st-ok:#1a7f37; --st-ok-t:#116329; --st-run:#0550ae; "
           "--st-warn:#9a6700; --st-warn-t:#9a6700;")
d1 = src.replace(NEW_ROW, OLD_ROW, 1)
assert d1 != src, "A-light warn row not found; token fix absent or altered"
(tmp / "discrim-oldwarn.html").write_text(d1, encoding="utf-8")

inject = ('<span class="badge" style="position:absolute;left:10px;top:10px;z-index:9;'
          'background:var(--warn-soft);color:var(--st-warn-t)">&#9888; OV-A</span>'
          '<span class="badge" style="position:absolute;left:30px;top:16px;z-index:9;'
          'background:var(--ok-soft);color:var(--st-ok-t)">&#10003; OV-B</span>')
idx = src.find('<section class="page" id="page-states"')
assert idx >= 0, "states section not found"
gt = src.find(">", idx)
(tmp / "discrim-overlap.html").write_text(src[:gt+1] + inject + src[gt+1:], encoding="utf-8")

d3 = src.replace("--st-skip:#a5b0c0;", "--st-skip:#6b6b76;")
assert d3 != src, "F dark skip token row not found"
(tmp / "discrim-oldskip.html").write_text(d3, encoding="utf-8")
print(tmp.as_posix())
EOF
)"
BASE_URL_DIR="file:///$(echo "$TMPDIR_OUT" | sed 's|^/\+||')"

run1() { # url-file
  "$CHROME" --headless=new --disable-gpu --dump-dom --virtual-time-budget=3500 "$1" 2>/dev/null | "$NODE" -e "
let d='';process.stdin.on('data',x=>d+=x).on('end',()=>{
  const m=d.match(/<pre id=\"auditOutput\">([\s\S]*?)<\/pre>/);
  if(!m){console.log('NOAUDIT');process.exit(0)}
  const t=m[1].replace(/&quot;/g,'\"').replace(/&amp;/g,'&');
  try{const o=JSON.parse(t);
    const f=o.contrast.filter(r=>!r.pass);
    const ov=o.layout.overlap||0;
    const parts=[(f.length||o.layout.outside||o.layout.clipped||ov)?'FAIL':'PASS',
      'contrast='+(o.contrast.length-f.length)+'/'+o.contrast.length,
      'overlap='+ov,
      f.length?('fails:'+f.map(x=>x.name+'='+x.cr).join(',')):'',
      ov?('overlaps:'+(o.layout.overlapPairs||[]).slice(0,6).join('; ')):''].filter(Boolean);
    console.log(parts.join(' '));
  }catch(e){console.log('FAIL parse-error')}
});"
}

d1_out="$(run1 "${BASE_URL_DIR}/discrim-oldwarn.html?cand=a&mode=light&page=states&audit=1&win=none")"
echo "  D1 old-warn-token (expect FAIL with badge-warn/st-warn-t): $d1_out"
d2_out="$(run1 "${BASE_URL_DIR}/discrim-overlap.html?cand=a&mode=dark&page=states&audit=1&win=none")"
echo "  D2 injected-overlap (expect FAIL with overlap>=1):          $d2_out"
d3_out="$(run1 "${BASE_URL_DIR}/discrim-oldskip.html?cand=f&mode=dark&page=states&audit=1&win=none")"
echo "  D3 f-skip-direct-regression (expect FAIL st-skip-direct):   $d3_out"

fail=0
case "$d1_out" in *badge-warn/st-warn-t=*) ;; *) echo "  D1 NOT discriminative"; fail=1 ;; esac
case "$d2_out" in *"overlap=1"*|*"overlap=2"*) ;; *) echo "  D2 NOT discriminative"; fail=1 ;; esac
case "$d3_out" in *st-skip-direct/panel=*) ;; *) echo "  D3 NOT discriminative"; fail=1 ;; esac
rm -f "$TMPDIR_OUT/discrim-oldwarn.html" "$TMPDIR_OUT/discrim-overlap.html" "$TMPDIR_OUT/discrim-oldskip.html"
if [ "$fail" -eq 0 ]; then echo "DISCRIMINATION: OK"; else echo "DISCRIMINATION: FAILED"; exit 1; fi
