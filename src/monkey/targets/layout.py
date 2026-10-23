"""Deterministic first-generation path mapping, preserving GUIDs and typed plans."""
import re
import posixpath
from pathlib import Path
from ..io import read,load,write_json,sha,finish,stage_manifest
from . import unity,cocos

_COMPILED={}


def mappings(profile, plan):
    if profile==unity.PROFILE:
        pairs={'Assets/Generated/Art/':'Assets/Game/Content/Images/',
               'Assets/Generated/Art':'Assets/Game/Content/Images',
               'Assets/Generated/Animations':'Assets/Game/Content/Animations',
               'Assets/Generated/Controllers':'Assets/Game/Content/Animations/Controllers',
               'Assets/Generated/Views/MonkeyCandidateView.cs':'Assets/Game/Presentation/Recovery/MonkeyCandidateView.cs',
               'Assets/Generated/Views/':'Assets/Game/Content/Prefabs/Recovery/',
               'Assets/Generated/Views':'Assets/Game/Content/Prefabs/Recovery',
               'Assets/Generated/Scenes/':'Assets/Game/Scenes/',
               'Assets/Generated/Scenes':'Assets/Game/Scenes',
               'Assets/Monkey/Editor':'Assets/Game/Editor/Conversion',
               'Assets/Monkey':'Assets/Game/Editor/Conversion',
               'Assets/Manual':'Assets/Game/Gameplay/Recovery',
               'Assets/Generated':'Assets/Game'}
        for copy in plan['copies']:
            old=copy['target'];suffix=Path(old).suffix.lower()
            folder={'.ttf':'Fonts','.otf':'Fonts','.fnt':'Fonts','.mp3':'Audio','.ogg':'Audio','.wav':'Audio','.json':'Config/Recovered'}.get(suffix,'Images')
            pairs[old]='Assets/Game/Content/'+folder+'/'+old.removeprefix('Assets/Generated/Art/')
            if suffix in ('.ttf','.otf'):
                pairs[str(Path(old).with_suffix('.asset'))]=str(Path(pairs[old]).with_suffix('.asset'))
        for asset in plan['assets']:
            if asset.get('fontAssetPath'):pairs[asset['fontAssetPath']]='Assets/Game/Content/Fonts/'+asset['fontAssetPath'].removeprefix('Assets/Generated/Art/')
        for font in plan.get('bitmapFonts',[]):pairs[font['fontPath']]='Assets/Game/Content/Fonts/'+font['fontPath'].removeprefix('Assets/Generated/Art/')
    else:
        pairs={'assets/generated/art/':'assets/art/images/','assets/generated/animations':'assets/art/animations',
               'assets/generated/views/':'assets/scenes/','assets/generated':'assets',
               'assets/manual':'assets/scripts/gameplay/recovery'}
        for a in plan['assets']:
            folder={'ttf':'assets/fonts','bitmap':'assets/fonts','json':'assets/config/recovered'}.get(a['kind'],'assets/art/images')
            pairs[a['path']]=folder+'/'+a['path'].removeprefix('assets/generated/art/')
    return pairs


def translate(value, pairs):
    # Single pass: a replacement must never be processed again by a shorter prefix.
    key=id(pairs);cached=_COMPILED.get(key)
    if cached is None or cached[0] is not pairs:
        if len(_COMPILED)>=8:_COMPILED.clear()
        cached=(pairs,re.compile('|'.join(re.escape(k) for k in sorted(pairs,key=len,reverse=True))))
        _COMPILED[key]=cached
    pattern=cached[1]
    def change(v):
        if isinstance(v,str):
            if v in pairs:return pairs[v]
            if v.endswith('.meta') and v[:-5] in pairs:return pairs[v[:-5]]+'.meta'
            return pattern.sub(lambda match:pairs[match[0]],v) if pairs else v
        if isinstance(v,list):return [change(x) for x in v]
        if isinstance(v,dict):return {k:(x if k in ('text','name','sourceId','sourceRefs','moduleName','type','logicalPath','originalPath','sourceName') else change(x)) for k,x in v.items()}
        return v
    return change(value)


def standardize(root,profile,plan,source_roots):
    root=Path(root);pairs=mappings(profile,plan)
    # Remove maintenance-machine paths from emitted evidence/glue, not from input snapshots.
    portable={str(path):'source://'+name for name,path in source_roots.items()}
    text_suffixes={'.json','.md','.cs','.js','.fnt','.txt'}
    originals=[p for p in sorted(root.rglob('*')) if p.is_file() and p!=root/'manifest.json']
    copied={c['target'] for c in plan['copies']}|{translate(c['target'],pairs) for c in plan['copies']}
    for path in originals:
        relative=path.relative_to(root).as_posix();dest=root/translate(relative,pairs)
        raw=read(path,max_bytes=128*1024*1024)
        if relative in copied and profile==cocos.PROFILE and path.suffix=='.fnt':
            asset=next(a for a in plan['assets'] if a['path']==relative or translate(a['path'],pairs)==relative)
            atlas=next(a for a in plan['assets'] if a['sourceId']==asset['atlas'])
            atlas_path=translate(atlas['path'],pairs)
            page=posixpath.relpath(atlas_path,str(Path(translate(relative,pairs)).parent))
            raw=raw.replace(('file="'+Path(atlas['path']).name+'"').encode(),('file="'+page+'"').encode())
        elif path.suffix.lower() in text_suffixes and relative not in copied:
            text=raw.decode('utf-8')
            if path.suffix.lower()=='.json':
                data=translate(load(raw,max_nodes=8_000_000),pairs)
                # Absolute stage/receipt paths are evidence IDs; the package ledger resolves originals.
                def scrub(v,key=None):
                    if isinstance(v,str):
                        if key in ('text','name'):return v
                        for base,logical in portable.items():v=v.replace(base,logical)
                        if Path(v).is_absolute() and key in ('path','sourceManifestPath'):
                            return 'conversion-evidence://'+Path(v).name
                        return v
                    if isinstance(v,list):return [scrub(x,key) for x in v]
                    if isinstance(v,dict):return {k:scrub(x,k) for k,x in v.items()}
                    return v
                raw=(__import__('json').dumps(scrub(data),ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
            else:
                text=text.replace('"Assets/Generated/Art/"+spec.nativeId+".mat"','"Assets/Game/Content/Materials/"+spec.nativeId+".mat"')
                raw=translate(text,pairs).encode()
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest!=path:
            if dest.exists():raise ValueError('Layout collision: '+str(dest))
            path.unlink()
        dest.write_bytes(raw)
    for path in sorted((p for p in root.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
        if not any(path.iterdir()):path.rmdir()
    if profile==cocos.PROFILE:
        # Bitmap page references changed relative to the preserved font directory.
        # Rebind typed asset receipts to final bytes, never edit source JsonAsset payloads.
        instruction=root/'extensions/monkey-import/import-plan.json'
        data=load(read(instruction,max_bytes=128*1024*1024),max_nodes=8_000_000)
        for asset in data['assets']:
            path=root/asset['path']
            if path.is_file():asset['sha256']=sha(read(path))
        write_json(instruction,data)
        candidate=root/'Analysis/candidate.json'
        if candidate.exists():
            data=load(read(candidate,max_bytes=128*1024*1024),max_nodes=8_000_000)
            for asset in data.get('assets',[]):
                path=root/asset['path']
                if path.is_file() and 'sha256' in asset:asset['sha256']=sha(read(path))
            write_json(candidate,data)
    required=(['Assets/Game/Content/Prefabs/Recovery','Assets/Game/Scenes','Assets/Game/Content/Animations/Controllers',
               'Assets/Game/Content/Materials'] if profile==unity.PROFILE else ['assets/scenes','assets/art/animations'])
    for relative in required:(root/relative).mkdir(parents=True,exist_ok=True)
    manifest=translate(stage_manifest(root),pairs)
    if profile==cocos.PROFILE:
        for asset in manifest.get('assets',[]):
            path=root/asset['path']
            if path.is_file() and 'sha256' in asset:asset['sha256']=sha(read(path))
    manifest.update(layout='game-standard-v1',pathMap=pairs,sourceRoots={})
    manifest['files']=[]
    finish(root,manifest)
    return manifest
