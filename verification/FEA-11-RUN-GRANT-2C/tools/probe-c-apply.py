import hashlib, subprocess, sys
from pathlib import Path
p=Path('apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs')
raw=p.read_bytes(); text=raw.decode('utf-8'); nl='\r\n' if '\r\n' in text else '\n'; norm=text.replace('\r\n','\n')
old="    private void StartRunGrantRenewal()\n    {\n        _runGrantRenewal = CreateRunGrantRenewal();\n    }\n"
new="    private void StartRunGrantRenewal()\n    {\n        // PROBE-C: the Host installation line is removed (reviewer reproduction).\n    }\n"
assert norm.count(old)==1, norm.count(old)
print('sha256_before='+hashlib.sha256(raw).hexdigest())
p.write_text(norm.replace(old,new).replace('\n',nl), encoding='utf-8', newline='')
print('PROBE_C_APPLIED')
