"""Version-proven Creator 2.1.2 resources; legacy scene graphs stay evidence."""
import copy
import re
from pathlib import Path
from .. import __version__
from ..io import read, load, sha, write_json, new_output, finish, diagnostic, inside
from .compiled import asset_key, fail
from .engine_facts import inspect as engine_facts

PROFILE = 'cocos-2.1.2-resource'


def identity(value, uuids):
    if type(value) is int:
        if not 0 <= value < len(uuids):fail('LEGACY_UUID_INDEX',str(value),'Index outside original UUID table')
        value=uuids[value]
    return asset_key(value)


def version_table(values, uuids):
    if not isinstance(values,list) or len(values)%2:fail('LEGACY_VERSION_TABLE','$','Expected identity/version pairs')
    result={}
    for value,version in zip(values[::2],values[1::2]):
        key=identity(value,uuids)
        if key in result or not isinstance(version,str) or not re.fullmatch('[a-zA-Z0-9_-]+',version):fail('LEGACY_VERSION_TABLE',key,'Duplicate or invalid version')
        result[key]=version
    return result


def document(value):
    value=copy.deepcopy(value)
    if isinstance(value,list):
        if not value or not isinstance(value[0],dict):fail('LEGACY_DOCUMENT','$','Expected serialized object array')
        return dict(root=0,instances=value)
    if not isinstance(value,dict) or not isinstance(value.get('__type__'),str):fail('LEGACY_DOCUMENT','$','Expected typed object')
    if value['__type__']=='cc.SpriteFrame':
        content=value.get('content')
        if not isinstance(content,dict) or set(content)-{'name','texture','rect','offset','originalSize','capInsets','rotated'}:
            fail('LEGACY_FRAME_FIELDS','$','Unknown source geometry fields')
        if any(k not in content for k in ('texture','rect','offset','originalSize','capInsets')):fail('LEGACY_FRAME_FIELDS','$','Incomplete original geometry')
        content['texture']=asset_key(content['texture'])
        rotated=content.get('rotated',False)
        if type(rotated)not in (int,bool) or rotated not in (0,1):fail('LEGACY_FRAME_ROTATION','$','Unknown source rotation')
        content['rotated']=int(rotated)
        value=dict(__type__='cc.SpriteFrame',data=content)
    return dict(root=0,instances=[value])


def inspect(tree, output):
    tree=Path(tree).resolve();proofs=[]
    for path in sorted(tree.rglob('*.js')):
        raw=read(path)
        if b'_CCSettings'not in raw or b'ENGINE_VERSION'not in raw:continue
        proof=engine_facts(path,True)
        if {f['version']for f in proof['facts']}=={'2.1.2'} and len(proof.get('settings',[]))==1:
            proofs.append((path,proof))
    if len(proofs)!=1:fail('LEGACY_SETTINGS_PROOF','$','Exactly one original 2.1.2 engine/settings declaration required')
    source,proof=proofs[0];settings=proof['settings'][0]['data'];uuids=settings.get('uuids')
    if not isinstance(uuids,list) or not 1<=len(uuids)<=50000:fail('LEGACY_SETTINGS_UUIDS','$','Bounded original UUID table required')
    keys=[asset_key(v)for v in uuids]
    if len(set(keys))!=len(keys):fail('LEGACY_SETTINGS_UUIDS','$','Duplicate original identity')
    versions=settings.get('md5AssetsMap',{});imports=version_table(versions.get('import'),uuids);natives=version_table(versions.get('raw-assets'),uuids)
    packs=settings.get('packedAssets')
    if not isinstance(packs,dict) or len(packs)>50000:fail('LEGACY_PACK_TABLE','$','Expected bounded original pack map')
    members={asset_key(p):[identity(v,uuids)for v in values]for p,values in packs.items()}
    inputs={};assets={};diagnostics=[];observed=set()
    def record(path):
        relative=path.relative_to(tree).as_posix();raw=read(path)
        inputs[relative]=dict(bundle='legacy',path=relative,bytes=len(raw),sha256=sha(raw));return raw
    record(source)
    def add(key,doc,path,native=None):
        entry=dict(sourceId='legacy:'+key,key=key,index=None,bundle='legacy',kind=doc['instances'][doc['root']].get('__type__'),
            logicalPath=None,references=[],native=native,document=doc,importPath=path.relative_to(tree).as_posix())
        if entry['kind']=='cc.SpriteFrame':entry['references']=[doc['instances'][0]['data']['texture']]
        if native and key in assets and assets[key]['kind']==entry['kind']:
            if assets[key].get('native')not in (None,native):fail('LEGACY_NATIVE_CONFLICT',key,'Two different payload files')
            assets[key]['native']=native;return
        if key in assets and assets[key]['document']!=doc:fail('LEGACY_PACK_CONFLICT',key,'Different supplied documents claim the same original identity')
        assets.setdefault(key,entry);observed.add(key)
    for path in sorted(tree.rglob('*')):
        if not path.is_file():continue
        match=re.fullmatch(r'res-(import|raw-assets)-([0-9a-f]{2})-([0-9a-f-]+)\.([A-Za-z0-9_-]+)\.(json|png|jpg|jpeg|mp3|ttf|ogg|wav)',path.name)
        if not match:continue
        mode,prefix,key,version,extension=match.groups();key=asset_key(key)
        if prefix!=key[:2]:fail('LEGACY_CACHE_IDENTITY',path.name,'Prefix differs from original identity')
        table=imports if mode=='import'else natives
        if table.get(key)!=version:
            diagnostics.append(diagnostic('LEGACY_CACHE_VERSION_MISMATCH',path.name,'Cached version not selected by original settings','legacy:'+key));continue
        raw=record(path)
        if mode=='raw-assets':
            kinds={'png':'cc.Texture2D','jpg':'cc.Texture2D','jpeg':'cc.Texture2D','mp3':'cc.AudioClip','ttf':'cc.TTFFont','ogg':'cc.AudioClip','wav':'cc.AudioClip'}
            add(key,dict(root=0,instances=[dict(__type__=kinds[extension])]),path,path.relative_to(tree).as_posix());continue
        value=load(raw)
        if key in members:
            if not isinstance(value,list) or len(value)!=len(members[key]):fail('LEGACY_PACK_LENGTH',path.name,'Pack length differs from original membership')
            rows=zip(members[key],value)
        else:rows=[(key,value)]
        for member,value in rows:
            try:doc=document(value)
            except ValueError as error:
                diagnostics.append(diagnostic(getattr(error,'code','LEGACY_DOCUMENT_PENDING'),path.name,str(error),'legacy:'+member));continue
            add(member,doc,path)
    for entry in assets.values():
        for key in entry['references']:
            if key not in assets:diagnostics.append(diagnostic('EXTERNAL_REFERENCE',entry['importPath'],'Exact original texture not supplied: '+key,entry['sourceId']))
    declared=set(keys)|set(natives)|(set(imports)-set(members))|{key for values in members.values()for key in values}
    missing=sorted(declared-observed)
    diagnostics.append(diagnostic('LEGACY_RESOURCE_SUBSET','$','Legacy graphs, clips, materials and methods remain pending; absent declared assets: '+str(len(missing))))
    for relative,entry in inputs.items():
        if sha(read(inside(tree,relative)))!=entry['sha256']:fail('SOURCE_CHANGED',relative,'Observed input changed')
    out=new_output(output,[tree]);write_json(out/'settings-proof.json',proof)
    report=dict(schemaVersion=1,toolVersion=__version__,sourceProfile=PROFILE,sourceVersion='2.1.2',
        versionEvidence='original static AST assignment and settings',sourceRoot=str(tree),sourceRoots={'legacy':str(tree)},bundle='legacy',
        selection=[],inputs=list(inputs.values()),assets=sorted(assets.values(),key=lambda a:a['sourceId']),diagnostics=diagnostics,
        declaredAssets=len(declared),missingDeclaredAssets=missing,settingsProofSha256=sha(read(out/'settings-proof.json')),
        packageSelection=dict(allProvidedBundles=True,resourceSubset=True),sourceCodeExecuted=False)
    write_json(out/'source-manifest.json',report);return finish(out,report)
