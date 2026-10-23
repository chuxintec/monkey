"""Embedded TypeTree -> named C# serialized fields. Asset bundles contain no method bodies."""
import re
from pathlib import Path
from .io import safe,read,load,sha,new_output,write_json
from .sources.compiled import fail

CORE_FIELDS={'m_GameObject','m_Enabled','m_Script','m_Name','m_EditorHideFlags','m_EditorClassIdentifier','m_ObjectHideFlags','m_CorrespondingSourceObject','m_PrefabInstance','m_PrefabAsset'}
PRIMITIVES={'bool':'bool','char':'byte','SInt8':'sbyte','UInt8':'byte','short':'short','SInt16':'short','UInt16':'ushort',
            'unsigned short':'ushort','int':'int','SInt32':'int','UInt32':'uint','unsigned int':'uint','SInt64':'long',
            'long long':'long','UInt64':'ulong','unsigned long long':'ulong','float':'float','double':'double','string':'string'}
UNITY_TYPES={'Sprite','Texture2D','Texture','GameObject','Transform','RectTransform','MonoBehaviour','Component','Object',
             'AudioClip','AnimationClip','RuntimeAnimatorController','Material','Shader','Mesh','Font','Canvas'}
VALUE_TYPES={'Vector2f':'Vector2','Vector3f':'Vector3','Vector4f':'Vector4','Quaternionf':'Quaternion','ColorRGBA':'Color','Color32':'Color32'}


def identifier(value):
    # @ escapes all C# keywords while preserving the reflected source name.
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',value):
        fail('CSHARP_NAME_UNSUPPORTED',str(value),'Source identifier needs explicit name mapping')
    return '@'+value


def field_type(node):
    typ=node['type']
    if typ in PRIMITIVES:return PRIMITIVES[typ]
    if typ in VALUE_TYPES:return 'UnityEngine.'+VALUE_TYPES[typ]
    match=re.fullmatch(r'PPtr<([^<>]+)>',typ)
    if match:
        name={'$Sprite':'Sprite'}.get(match[1],match[1])
        if name in UNITY_TYPES:return 'UnityEngine.'+name
    if typ=='vector':
        arrays=[n for n in node.get('children',[]) if n['type']=='Array']
        if len(arrays)==1:
            values=[n for n in arrays[0].get('children',[]) if n['name']=='data']
            if len(values)==1:return field_type(values[0])+'[]'
    fail('CSHARP_FIELD_UNSUPPORTED',node.get('name','?'),'No proven C# mapping for embedded type '+str(typ))


def model(inspection,output):
    inspection=safe(inspection);receipt=load(read(inspection/'inspection.json'))
    raw=read(inspection/'typed-objects.json',max_bytes=128*1024*1024)
    if sha(raw)!=receipt.get('typedObjectsSha256'):fail('UNITY_TYPED_CHANGED',str(inspection),'Typed snapshot differs from receipt')
    data=load(raw,max_nodes=8_000_000);out=new_output(output,[inspection])
    objects={(o['file'],o['pathId']):o for o in data['objects']};schemas=data.get('embeddedSchemas',{});classes={};gaps=[]
    for obj in data['objects']:
        if obj['type']!='MonoBehaviour' or obj.get('status')!='parsed':continue
        shape=schemas.get(obj.get('embeddedSchemaId'));ptr=obj['data'].get('m_Script',{})
        script=objects.get((obj['file'],ptr.get('pathId'))) if ptr.get('fileId')=='0' else None
        if shape is None or script is None or script.get('status')!='parsed':
            gaps.append(dict(object=dict(file=obj['file'],pathId=obj['pathId']),reason='embedded schema or same-file MonoScript unavailable'));continue
        info=script['data'];name=info.get('m_ClassName');namespace=info.get('m_Namespace') or '';assembly=info.get('m_AssemblyName') or 'UnknownAssembly'
        try:
            cs_name=identifier(name);parts=[identifier(p) for p in namespace.split('.')] if namespace else []
            fields=[dict(name=n['name'],csName=identifier(n['name']),csType=field_type(n),sourceType=n['type']) for n in shape['children'] if n['name'] not in CORE_FIELDS]
        except ValueError as error:
            gaps.append(dict(object=dict(file=obj['file'],pathId=obj['pathId']),reason=getattr(error,'code','unsupported'),detail=getattr(error,'message',str(error))));continue
        if not fields:
            gaps.append(dict(object=dict(file=obj['file'],pathId=obj['pathId']),reason='No recoverable fields or method bodies; no empty class emitted'));continue
        key=(script['file'],script['pathId'])
        record=dict(name=name,namespace=namespace,assembly=assembly,sourceScript=dict(file=key[0],pathId=key[1]),
                    fields=fields,instances=[],methodRecovery='unavailable-in-asset-bundle',status='schema_only',business='not_run')
        if key in classes:
            if classes[key]['fields']!=fields:fail('UNITY_SCHEMA_CONFLICT',name,'Same script identity has differing embedded schemas')
        else:classes[key]=record
        classes[key]['instances'].append(dict(file=obj['file'],pathId=obj['pathId'],rawSha256=obj['rawSha256'],references=obj['references']))
    occupied=set()
    for (file_id,path_id),c in classes.items():
        if not re.fullmatch(r'[A-Za-z0-9_.-]+',c['assembly']):fail('CSHARP_ASSEMBLY_PATH',c['name'],'Unsafe assembly name')
        relative=Path('CSharp')/c['assembly'].removesuffix('.dll')/Path(*c['namespace'].split('.'))/(c['name']+'.cs')
        if str(relative).casefold() in occupied:fail('CSHARP_CLASS_COLLISION',str(relative),'Distinct script identities collide; assembly repair required')
        occupied.add(str(relative).casefold());path=out/relative;path.parent.mkdir(parents=True,exist_ok=True)
        lines=['// Embedded TypeTree fields only. Original method bodies are unavailable.',
               '// Source container SHA256: '+data['source']['sha256'],
               '// Source MonoScript file/pathID: '+file_id+'/'+path_id]
        if c['namespace']:lines+=['namespace '+'.'.join(identifier(p) for p in c['namespace'].split('.'))+' {']
        lines+=['public class '+identifier(c['name'])+' : UnityEngine.MonoBehaviour {']
        lines+=['    public '+f['csType']+' '+f['csName']+';' for f in c['fields']]
        lines+=['}']
        if c['namespace']:lines+=['}']
        path.write_text('\n'.join(lines)+'\n');c['target']=relative.as_posix();c['targetSha256']=sha(read(path))
    report=dict(schemaVersion=1,sourceSha256=data['source']['sha256'],typedSnapshotSha256=sha(raw),
                status='partial',classes=list(classes.values()),gaps=gaps,compiled='not_run',native='not_run',
                summary=dict(classes=len(classes),fields=sum(len(c['fields']) for c in classes.values()),methodsImplemented=0,instances=sum(len(c['instances']) for c in classes.values())))
    write_json(out/'unity-code-model.json',report)
    return dict(status='partial',summary=report['summary'],compiled='not_run',business='not_run',report=str(out/'unity-code-model.json'))
