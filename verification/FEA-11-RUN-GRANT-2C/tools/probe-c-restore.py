import hashlib
from pathlib import Path
p=Path('apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs')
raw=p.read_bytes(); text=raw.decode('utf-8'); nl='\r\n' if '\r\n' in text else '\n'; norm=text.replace('\r\n','\n')
new="    private void StartRunGrantRenewal()\n    {\n        // PROBE-C: the Host installation line is removed (reviewer reproduction).\n    }\n"
old="    private void StartRunGrantRenewal()\n    {\n        _runGrantRenewal = CreateRunGrantRenewal();\n    }\n"
assert norm.count(new)==1
p.write_text(norm.replace(new,old).replace('\n',nl), encoding='utf-8', newline='')
print('sha256_after='+hashlib.sha256(p.read_bytes()).hexdigest())
print('PROBE_C_RESTORED')
