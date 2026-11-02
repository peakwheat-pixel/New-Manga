"""Read-only audit of captured PNGs/TRX. Writes only the requested Markdown report."""
import argparse
from collections import Counter
from pathlib import Path
import hashlib
import re
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('--results', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
root = Path.cwd()
visuals = root / 'verification/FEA-06-RESIDUAL-2/visuals'
inventory = (visuals / 'visual-inventory.md').read_text(encoding='utf-8-sig')
ns = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
lines = ['# R2R3 自动化与像素审计（实施者自测）', '',
         '本报告不提供独立视觉签署。PNG 原文件不做调色、重绘或尺寸修改。', '',
         '## 无过滤全量（TRX 实读）', '', '| assembly | passed | failed | skipped | total |', '|---|---|---|---|---|']
total = Counter()
skips = []
regressions = []
for file in sorted(Path(a.results).glob('*.trx')):
    doc = ET.parse(file).getroot()
    results = doc.findall('t:Results/t:UnitTestResult', ns)
    c = Counter(r.attrib['outcome'] for r in results)
    method = doc.find('t:TestDefinitions/t:UnitTest/t:TestMethod', ns)
    assembly = Path(method.attrib['codeBase']).name
    lines.append(f"| {assembly} | {c['Passed']} | {c['Failed']} | {c['NotExecuted']} | {len(results)} |")
    total.update(c)
    for result in results:
        name = result.attrib['testName']
        if result.attrib['outcome'] == 'NotExecuted':
            reason = result.findtext('t:Output/t:ErrorInfo/t:Message', '', ns)
            skips.append((name, reason))
        if any(word in name for word in ('InactiveNavigation', 'DisablingPolicy')):
            regressions.append((name, result.attrib['outcome']))
lines += [f"| TOTAL | {total['Passed']} | {total['Failed']} | {total['NotExecuted']} | {sum(total.values())} |", '',
          f"相对1281/0/57：+{total['Passed'] - 1281}/+{total['Failed']}/+{total['NotExecuted'] - 57}。", '',
          '## 新增生命周期回归', '', '| test | outcome |', '|---|---|']
lines += [f'| `{name}` | {outcome} |' for name, outcome in regressions]
lines += ['', '## 逐条 skip 原因', '', '| test | actual reason |', '|---|---|']
lines += [f'| `{name}` | {reason} |' for name, reason in sorted(skips)]
assert total['Passed'] >= 1281 and total['Failed'] == 0 and total['NotExecuted'] == 57, total
assert len(regressions) == 8 and all(o == 'Passed' for _, o in regressions), regressions

old_text = subprocess.check_output(['git', 'show', '9c6a2b474:verification/FEA-06-RESIDUAL-2/visuals/visual-inventory.md'], text=True, encoding='utf-8')
def hashes(text):
    return dict(re.findall(r'\| `([^`]+\.png)` \|[^\n]*?\| ([A-Fa-f0-9]{64}) \|', text))
old = {n: h.lower() for n, h in hashes(old_text).items()}
new = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in visuals.glob('*.png')}
listed = {n: h.lower() for n, h in hashes(inventory).items()}
assert new == listed
assert len(set(new.values())) == len(new)
same = sorted(n for n in old.keys() & new.keys() if old[n] == new[n])
changed = sorted(n for n in old.keys() & new.keys() if old[n] != new[n])
added = sorted(new.keys() - old.keys())
removed = sorted(old.keys() - new.keys())
lines += ['', '## 图数与旧签署的字节对应', '',
          f'旧图 {len(old)}；本轮 {len(new)} PNG / {len(listed)} 清单行 / {len(set(new.values()))} 唯一 SHA。',
          f'同名同字节 {len(same)}；同名改字节 {len(changed)}；新增文件名 {len(added)}；移除旧误标签文件名 {len(removed)}。',
          '原 impl-r3 的158 PASS/6 REJECT只签其旧SHA；本轮清单全部NOT_RUN，不将实施者自测充作复审。', '',
          '| file | byte change | old SHA256 | new SHA256 |', '|---|---|---|---|']
for name in sorted(old.keys() | new.keys()):
    state = 'UNCHANGED' if name in same else 'CHANGED' if name in changed else 'ADDED' if name in added else 'REMOVED'
    lines.append(f"| `{name}` | {state} | {old.get(name, '—')} | {new.get(name, '—')} |")

lines += ['', '## 纯背景渐变像素（RGB 最大通道差）', '',
          'crop相对窗口(216,95,1048,720)；纯背景横带窗口(250,740,1000,60)，换成crop坐标(34,645,1000,60)。', '',
          '| theme | pair | max RGB delta (whole crop) | pixels >8 (whole crop) | pixels >8 (plain strip/60000) | mean abs RGB (strip) |',
          '|---|---|---|---|---|---|']
for theme in ('light', 'dark'):
    def load(state, mode):
        return np.asarray(Image.open(visuals / f'decor--shelf-gradient--{state}--{mode}--{theme}.png').convert('RGB'), dtype=np.int16)
    first = load('first', 'full')
    for name, other in [('first→mid(3000ms)', load('mid', 'full')), ('first→reduce', load('static', 'reduce'))]:
        delta = np.abs(first - other)
        strip = delta[645:705, 34:1034]
        count = int((strip.max(axis=2) > 8).sum())
        assert count > 5000
        lines.append(f'| {theme} | {name} | {delta.max()} | {int((delta.max(axis=2) > 8).sum())} | {count} | {strip.mean():.4f} |')

def luminance(rgb):
    v = np.array(rgb, dtype=float) / 255
    v = np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)
    return float(v @ [.2126, .7152, .0722])
lines += ['', '## Danger pressed 原图实色像素', '',
          '中心按钮内部区域(195,155,130,30)统计：背景为最多的实色；文字为前景侧亮度极值（抗锯齿边缘不可能比其本色更极端）。属性断言另读实际PART_Root/ContentPresenter。', '',
          '| theme | background RGB/count | foreground RGB/count | contrast |', '|---|---|---|---|']
for theme in ('light', 'dark'):
    image = np.asarray(Image.open(visuals / f'components--danger-button--pressed--full--{theme}.png').convert('RGB'))
    colors = Counter(map(tuple, image[155:185, 195:325].reshape(-1, 3).tolist()))
    bg, bg_count = colors.most_common(1)[0]
    fg = (max if theme == 'light' else min)(colors, key=luminance)
    aa, bb = sorted((luminance(bg), luminance(fg)))
    contrast = (bb + .05) / (aa + .05)
    assert contrast >= 4.5, (theme, bg, fg, contrast)
    lines.append(f'| {theme} | {bg}/{bg_count} | {fg}/{colors[fg]} | {contrast:.4f}:1 |')

Path(a.output).write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f"total={total['Passed']}/{total['Failed']}/{total['NotExecuted']}; PNG={len(new)} same={len(same)} changed={len(changed)} added={len(added)} removed={len(removed)}; EXIT=0")
