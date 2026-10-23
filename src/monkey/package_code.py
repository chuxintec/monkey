"""Source-bound code emission and typed component projection for package conversion."""
import shutil
from .io import safe,read,load,sha,write_json,new_output,stage_manifest,stage_document,inside,finish,diagnostic
from .sources.compiled import fail


def declaration(path, language='ts'):
    path=safe(path);raw=read(path);data=load(raw)
    if data.get('schemaVersion')!=1 or data.get('kind')!='numeric-call-subdomain-v1':
        fail('PACKAGE_CODE_CONTRACT',str(path),'Expected numeric-call-subdomain-v1 schema 1')
    if language!='ts':fail('PACKAGE_CODE_JS_PENDING',str(path),'Package binding currently requires verified TypeScript importer metadata')
    if set(data)!={'schemaVersion','kind','moduleName','registrationId','moduleSha256','numericField'}:
        fail('PACKAGE_CODE_CONTRACT',str(path),'Unknown or missing contract fields')
    if any(not isinstance(data[k],str)or not data[k]for k in ('moduleName','registrationId','moduleSha256','numericField')):
        fail('PACKAGE_CODE_CONTRACT',str(path),'Expected explicit nonempty source identity and field')
    return dict(path=str(path),sha256=sha(raw),data=data)


def prepare(recovered, spec, namespace, output):
    from .code_model import inspect
    from .code_emit import emit
    data=spec['data']
    matches=[m for m in recovered if m.get('name')==data['moduleName'] and any(r.get('identity')==data['registrationId'] for r in m.get('rf',[]))]
    if len(matches)!=1:fail('PACKAGE_CODE_MODULE',data['moduleName'],'Expected one exact original RF module; duplicates are ambiguous')
    module=matches[0];raw=module['source'].encode()
    if sha(raw)!=module.get('sha256') or sha(raw)!=data['moduleSha256']:
        fail('PACKAGE_CODE_SOURCE_CHANGED',module['sourceId'],'Source module differs from numeric contract')
    declaration_raw=read(safe(spec['path']))
    if sha(declaration_raw)!=spec['sha256']:fail('PACKAGE_CODE_CONTRACT_CHANGED',spec['path'],'Declaration changed before emission')
    out=new_output(output);source=out/'OriginalModule.js';source.write_bytes(raw);(out/'OriginalContract.json').write_bytes(declaration_raw)
    inspect(source,out/'Model',data['moduleName'])
    emit(source,out/'Model/code-model.json',out/'Emitted',[data['numericField']],'ts',namespace)
    contract=load(read(out/'Emitted/Analysis/code-contract.json'))
    if contract['presentation']['kind']!='label-adapter' or contract['presentation']['sourceRegistration']['identity']!=data['registrationId']:
        fail('PACKAGE_CODE_BASE',module['sourceId'],'Only source-proven native Label adapters currently bind automatically')
    methods=contract['methods'];setters=[m['name']for m in methods if m['semantic']['kind']=='write-instance-field'];getters=[m['name']for m in methods if m['semantic']['kind']=='read-instance-field']
    if len(setters)!=1 or len(getters)!=1:
        fail('PACKAGE_CODE_METHOD_PAIR',module['sourceId'],'Native numeric exercise requires one evidenced setter and getter')
    report=dict(schemaVersion=1,sourceModule=module['sourceId'],sourceModuleSha256=sha(raw),declarationSha256=spec['sha256'],
                contractSha256=sha(read(out/'Emitted/Analysis/code-contract.json')),numericMethods=dict(setter=setters[0],getter=getters[0]),
                implementedMethods=contract['implementedMethods'],pendingMethods=len(contract['pendingMethods']),binding='not_run',sourceExecuted=False)
    write_json(out/'package-code.json',report)
    return out


def project_ir(ir_path, inspected, emission, output):
    from .code_presentation import label_components
    ir=stage_document(ir_path/'ir.json');contract=load(read(emission/'Emitted/Analysis/code-contract.json'));report=load(read(emission/'package-code.json'))
    identity=contract['presentation']['sourceRegistration']['identity']
    expected={c['sourceId'] for c in ir['components']if c['type']==identity}
    if not expected:fail('PACKAGE_CODE_BINDINGS',identity,'No matching serialized original components in supplied object graphs')
    asset_ids={sid.split('#')[0]for sid in expected};replacements={}
    for asset in inspected['assets']:
        sid=asset.get('sourceId',asset.get('id'))
        if sid not in asset_ids:continue
        for c in label_components(asset['document'],sid,contract):
            if c['sourceId']in replacements:fail('PACKAGE_CODE_BINDINGS',c['sourceId'],'Repeated source component')
            c.update(codeClassName=contract['className'],codeScriptGuid=contract['nativeIdentity']['unityScriptGuid'],numericMethods=report['numericMethods'])
            replacements[c['sourceId']]=c
    if set(replacements)!=expected:fail('PACKAGE_CODE_BINDINGS',identity,'Projection must cover every original matching component exactly once')
    out=new_output(output,[ir_path,emission])
    for row in stage_manifest(ir_path)['files']:
        if row['path']=='ir.json':continue
        raw=read(inside(ir_path,row['path']),max_bytes=128*1024*1024)
        if sha(raw)!=row['sha256']:fail('PACKAGE_CODE_IR_CHANGED',row['path'],'Normalized resource identity differs')
        dest=inside(out,row['path']);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    ir['components']=[replacements.get(c['sourceId'],c)for c in ir['components']]
    ir['diagnostics']=[d for d in ir['diagnostics']if not(d['code']=='UNSUPPORTED_COMPONENT_SEMANTIC'and d.get('sourceId')in expected)]
    ir['diagnostics'].extend(diagnostic('CODE_NUMERIC_SUBDOMAIN_HANDOFF',sid,'Only explicit Number setter/getter calls and static Label presentation; original pending methods remain unavailable',sid)for sid in sorted(expected))
    ir['codeProjection']=dict(report,sourceIrSha256=sha(read(ir_path/'ir.json',max_bytes=128*1024*1024)),sourceBindings=sorted(expected),binding='planned_native_import')
    write_json(out/'ir.json',ir);finish(out,ir)
    return out,ir


def install(emission, project, profile, manifest, plan):
    from .targets import unity
    contract_path=emission/'Emitted/Analysis/code-contract.json';contract=load(read(contract_path));prefix='Unity/'if profile==unity.PROFILE else'Cocos/'
    script=None
    for row in contract['files']:
        original=row['path'].startswith('SourceRecovery/Original/')
        if not row['path'].startswith(prefix)and not original:continue
        source=emission/'Emitted'/row['path'];raw=read(source)
        if sha(raw)!=row['sha256']:fail('PACKAGE_CODE_EMIT_CHANGED',str(source),'Generated source/meta differs')
        rel=row['path']if original else row['path'].removeprefix(prefix);dest=inside(project,rel)
        if dest.exists():fail('PACKAGE_CODE_COLLISION',rel,'Refuse to replace an existing generated asset')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if not original and not rel.endswith('.meta'):script=rel
    shutil.copy2(contract_path,project/'Analysis/code-contract.json')
    binding_report=load(read(emission/'package-code.json'))
    binding_report['sourceBindings']=[dict(sourceId=c['sourceId'],node=c['node'],state='planned_native_import'if c['convertible']else'blocked_presentation_adapter')for c in plan['components']if c.get('codeClassName')==contract['className']]
    write_json(project/'Analysis/package-code.json',binding_report)
    shutil.copy2(emission/'OriginalContract.json',project/'Analysis/numeric-code-declaration.json')
    manifest['codeEmission']=dict(language='csharp'if profile==unity.PROFILE else'ts',sourceContractSha256=sha(read(contract_path)),
        scriptPath=script,scriptGuid=contract['nativeIdentity']['unityScriptGuid']if profile==unity.PROFILE else None,
        scriptUuid=contract['nativeIdentity']['creatorScriptUuid']if profile!=unity.PROFILE else None,sourceRegistration=contract['presentation']['sourceRegistration'])
