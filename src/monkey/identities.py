"""Seal IDs that already exist before native import; distinguish first-generation IDs."""
import re
from .sources.compiled import fail


def assigned(root,manifest):
    from .io import inside,read,load
    profile=manifest.get('targetProfile');prefix='Assets/'if profile=='unity-6000.6.2f1-ugui'else'assets/'if profile=='cocos-3.8.8'else None
    if prefix is None:return manifest
    entries=[]
    for row in manifest.get('files',[]):
        path=row['path']
        if not path.startswith(prefix)or not path.endswith('.meta'):continue
        raw=read(inside(root,path))
        if prefix=='Assets/':
            values=re.findall(rb'^guid: ([0-9a-f]{32})$',raw,re.M)
            if len(values)!=1:fail('ASSET_META_IDENTITY',path,'Expected one assigned Unity GUID')
            value=values[0].decode()
        else:
            value=load(raw).get('uuid')
            if not isinstance(value,str)or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',value):fail('ASSET_META_IDENTITY',path,'Expected canonical assigned Creator UUID')
        entries.append(dict(path=path[:-5],id=value))
    manifest['assignedAssetIdentities']=entries;return manifest


def verify(root,manifest):
    from .io import inside,read,load,diagnostic
    errors=[];unity=manifest.get('targetProfile')=='unity-6000.6.2f1-ugui'
    for entry in manifest.get('assignedAssetIdentities',[]):
        path=entry['path']+'.meta'
        try:
            raw=read(inside(root,path));value=None
            if unity:
                values=re.findall(rb'^guid: ([0-9a-f]{32})$',raw,re.M);value=values[0].decode()if len(values)==1 else None
            else:value=load(raw).get('uuid')
            if value!=entry['id']:errors.append(diagnostic('ASSIGNED_NATIVE_IDENTITY_CHANGED',path,'Pre-existing resource/script identity changed'))
        except (OSError,ValueError):errors.append(diagnostic('ASSIGNED_NATIVE_IDENTITY_CHANGED',path,'Pre-existing meta missing or invalid'))
    return errors
