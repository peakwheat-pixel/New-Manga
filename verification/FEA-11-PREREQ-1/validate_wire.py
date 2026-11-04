"""Compile/check C-17 field tables and exercise isolated DTO shape negatives."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOC = ROOT / 'doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md'
STATES = ['started','host-authorized','core-committed','acknowledged','failed','recovered']
STALE = ['expired','source','binding','authorization','scope','manual','decision','cancelled']


def compile_tables():
    text = DOC.read_text(encoding='utf-8')
    dto_text = text.split('### 5.2 DTO 字段表',1)[1].split('OperationState 六值',1)[0]
    dtos = {}
    for name, body in re.findall(r'^\| (\w+) \| (.+) \|$',dto_text,re.M):
        if name == 'DTO':
            continue
        fields = {}
        for field in body.replace('\\|','|').split('; '):
            match = re.fullmatch(r'(\w+)([!?]) (.+)',field)
            assert match, (name,field)
            key, null, typ = match.groups()
            fields[key] = {'nullable':null=='?', 'type':typ}
        dtos[name] = fields
    command_text = text.split('### 5.1 命令表',1)[1].split('Dispatch 是接受响应',1)[0]
    commands = {}
    for line in command_text.splitlines():
        if not line.startswith('| ') or ' / ' not in line:
            continue
        # Escaped pipes inside enum types are not Markdown column boundaries.
        columns = re.split(r'(?<!\\)\|',line)[1:-1]
        assert len(columns)==4, columns
        names, req, resp, _ = [c.strip() for c in columns]
        core, host = names.split(' / ')
        if core == 'Core':
            continue
        if req == '{}':
            reqname = 'Empty'
            dtos.setdefault(reqname,{})
        elif re.fullmatch(r'\w+',req):
            reqname = req
        else:
            reqname = core+'Request'
            fields = {}
            for field in req.replace('\\|','|').split('; '):
                key, null, typ = re.fullmatch(r'(\w+)([!?]) (.+)',field).groups()
                fields[key]={'nullable':null=='?','type':typ}
            dtos[reqname]=fields
        assert reqname in dtos and resp in dtos, (core,reqname,resp)
        control={'ScanSourceSync','ApplySourceSyncPlan','RelinkSource','RepointSource','ResyncSource','AcknowledgeSourceOperation','CompleteSourceOperationRecovery','RecordSourceOperationFailure'}
        commands[core]={'host':host,'request':reqname,'response':resp,'minor':3,'transport':'host-local' if core=='GetSourceSyncCapabilities' else 'host-control' if core in control else 'stdio'}
    error_text = text.split('## 8. 局部错误闭集',1)[1].split('## 9.',1)[0]
    errors = {}
    for code,category,retry in re.findall(r'^\| ([A-Z][A-Z_0-9]+) \| (\w+) \| (true|false) \|',error_text,re.M):
        errors[code]={'category':category,'retryable':retry=='true'}
    return {'format':'c17-field-tables/1','dtos':dtos,'commands':commands,'errors':errors,
            'operation_states':STATES,'stale_reasons':STALE}


def classify(typ, schema):
    if typ in schema['dtos']:
        return 'object',typ
    if typ in ('ExistingSourceCode','FailureCode'):
        if typ=='FailureCode':
            return 'enum', list(schema['errors'])
        return 'enum',[c for c in schema['errors'] if c.startswith(('SOURCE_','FILE_')) and c not in ('SOURCE_SYNC_STATE_CONFLICT','SOURCE_SYNC_UNSTABLE','SOURCE_SYNC_CANCELLED','SOURCE_SYNC_STORAGE_FAILED')]
    if typ=='OperationState':
        return 'enum',STATES
    if typ=='StaleReason':
        return 'enum',STALE
    if '[' in typ:
        base,limit=typ.split('[',1)
        min_n,max_n=0,10000
        if limit.startswith('1..20'):
            min_n,max_n=1,20
        elif limit.startswith('1..10000'):
            min_n=1
        elif limit.startswith('恰好7'):
            min_n,max_n=7,7
        return 'array',(base,min_n,max_n)
    if '|' in typ:
        return 'enum',[int(x) if x.isdecimal() else x for x in typ.split('|')]
    if typ in ('true','false'):
        return 'const',typ=='true'
    if typ=='boolean':
        return 'bool',None
    if typ in ('N','G','I'):
        return 'integer',-(2**53-1) if typ=='I' else 0 if typ=='N' else 1
    if typ=='H':
        return 'hash',None
    if typ=='T':
        return 'time',None
    if typ=='ID':
        return 'id',None
    if typ.startswith('string('):
        m=re.search(r'1\.\.(\d+)',typ)
        return 'string',int(m.group(1))
    # All other single tokens in the table are literal format identifiers.
    assert typ in ('source-sync-plan/1','pixel-digest/1','source-operation/1'), typ
    return 'const',typ


def check_type(value, typ, schema):
    kind,arg=classify(typ,schema)
    if kind=='object':
        check(value,arg,schema)
    elif kind=='array':
        elem,minimum,maximum=arg
        assert type(value) is list and minimum<=len(value)<=maximum
        for item in value:
            check_type(item,elem,schema)
    elif kind=='enum':
        assert any(type(value) is type(x) and value==x for x in arg)
    elif kind=='const':
        assert type(value) is type(arg) and value==arg
    elif kind=='integer':
        assert type(value) is int and arg<=value<=2**53-1
    elif kind=='bool':
        assert type(value) is bool
    elif kind=='hash':
        assert type(value) is str and re.fullmatch('[0-9a-f]{64}',value)
    elif kind=='time':
        assert type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',value)
    elif kind in ('id','string'):
        assert type(value) is str and 1<=len(value)<=(128 if kind=='id' else arg)
        assert not re.search(r'[\x00-\x1f\x7f]',value)
        if kind=='id':
            assert not any(x in value for x in ('/', '\\', ':'))


def check(value, name, schema):
    assert type(value) is dict
    fields=schema['dtos'][name]
    assert set(value)==set(fields), (name,'missing/unknown fields')
    for key, spec in fields.items():
        if value[key] is None:
            assert spec['nullable'], (name,key,'null')
        else:
            check_type(value[key],spec['type'],schema)


def sample_type(typ,schema):
    kind,arg=classify(typ,schema)
    if kind=='object': return sample(arg,schema)
    if kind=='array': return [sample_type(arg[0],schema) for _ in range(arg[1])]
    if kind=='enum': return arg[0]
    if kind=='const': return arg
    if kind=='integer': return arg
    if kind=='bool': return False
    if kind=='hash': return 'a'*64
    if kind=='time': return '2026-11-04T00:00:00.000Z'
    return 'synthetic'


def sample(name,schema):
    return {k:None if s['nullable'] else sample_type(s['type'],schema) for k,s in schema['dtos'][name].items()}


def reject(value,name,schema):
    try:
        check(value,name,schema)
    except (AssertionError,TypeError,ValueError):
        return
    raise AssertionError(('negative accepted',name,value))


def main():
    print('COMMAND: python -B verification/FEA-11-PREREQ-1/validate_wire.py')
    print(f'ENV: shell=PowerShell; interpreter={sys.executable}; Python={platform.python_version()}; no DB/filesystem I/O except contract evidence')
    schema=compile_tables()
    target=HERE/'wire-schema.json'
    if '--write-schema' in sys.argv:
        target.write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert json.loads(target.read_text(encoding='utf-8'))==schema, 'table/schema drift'
    negatives=0
    for name,fields in schema['dtos'].items():
        value=sample(name,schema)
        check(value,name,schema)
        reject({**value,'unknown':1},name,schema)
        negatives+=1
        for key,spec in fields.items():
            missing=copy.deepcopy(value)
            del missing[key]
            reject(missing,name,schema)
            negatives+=1
            if not spec['nullable']:
                reject({**value,key:None},name,schema)
                negatives+=1
            else:
                nonnull={**value,key:sample_type(spec['type'],schema)}
                check(nonnull,name,schema)
            reject({**value,key:3.14},name,schema)
            negatives+=1
            kind,_=classify(spec['type'],schema)
            if kind in ('enum','const'):
                reject({**value,key:'UNKNOWN'},name,schema)
                negatives+=1
            if kind=='integer':
                reject({**value,key:True},name,schema)
                reject({**value,key:2**53},name,schema)
                negatives+=2
        print(f'PASS DTO {name}: {len(fields)} required fields / nullable positives / missing-null-type-enum-unknown negatives')
    for name,c in schema['commands'].items():
        check(sample(c['request'],schema),c['request'],schema)
        check(sample(c['response'],schema),c['response'],schema)
        reject({**sample(c['request'],schema),'unknown':1},c['request'],schema)
        negatives+=1
        print(f'PASS COMMAND {name}: {c["request"]} -> {c["response"]}; minor={c["minor"]}; transport={c["transport"]}')
    assert len(schema['commands'])==15
    assert len(schema['errors'])==28
    sys.path.insert(0,str(ROOT/'src'))
    from application.importing.referenced.errors import SOURCE_ERROR_TABLE
    for code, spec in schema['errors'].items():
        if code in SOURCE_ERROR_TABLE:
            assert (spec['category'],spec['retryable'])==SOURCE_ERROR_TABLE[code],code
    print('PASS existing Source error category/retryable triples match read-only production table')
    print(f'RESULT: {len(schema["dtos"])} DTOs / 15 commands (14 Core + 1 Host-local) / 28 errors / {negatives} shape negatives passed; 0 skipped')
    print('LIMIT: structural contract validation; cross-field/domain guards and real IPC are NOT_RUN here')
    print('WIRE_SCHEMA_SHA256: '+hashlib.sha256(target.read_bytes()).hexdigest())


if __name__=='__main__':
    try:
        main()
    except Exception:
        print('EXIT: 1')
        raise
    print('EXIT: 0')
