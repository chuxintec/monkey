"""LayoutPlanner: the only allocator of generated asset paths (PROJECT-SPEC 4-5). Identity GUIDs stay path-independent."""
import re
import unicodedata
from collections import Counter
from ..io import sha
from . import casing,classify,semantic,standard

PASCAL_TYPES={'prefab','scene','config','strings','data','atlas','controller','font-asset'}
VARIANTS={'original':'untrimmed','atlas':'page0'}
MAX_PATH_BYTES=180
_HASHED=re.compile(r'[0-9a-f]{32}|[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}')


def _fold(path):return unicodedata.normalize('NFC',path).casefold()


class LayoutPlanner:
    def __init__(self,engine,metadata=None,overrides=None):
        if engine not in ('unity','creator'):raise ValueError('Unknown layout engine')
        self.engine=engine;self.metadata=metadata or {};self.overrides=overrides or {}
        self.default_locale=self.overrides.get('defaultLocale') or 'zh-Hans'
        self.types=standard.UNITY_TYPES if engine=='unity' else standard.CREATOR_TYPES
        self.roots=standard.ROOTS[engine]
        self.records=[];self._claims={};self._allocated={};self._dirs={};self._pending={};self._by_key={}

    # -- naming -------------------------------------------------------------------------------------------
    def _meta(self,sid,metadata):
        base=sid;variant=''
        if metadata is None and base not in self.metadata:
            for ending in ('@original','@atlas'):
                if base.endswith(ending):base=base[:-len(ending)];variant=ending[1:];break
        return base,variant,dict(metadata if metadata is not None else self.metadata.get(base,{}))

    def _stem(self,typ,stem):
        return casing.pascal(stem) if typ in PASCAL_TYPES else casing.snake(stem)

    def _folders(self,parts):
        return [casing.folder(p,self.engine) for p in parts]

    def describe(self,sid,kind,suffix,variant='',metadata=None,root=None):
        """Base (uncollided) target and its naming evidence."""
        base,implicit,meta=self._meta(sid,metadata);variant=variant or implicit
        d=semantic.derive(meta,self.overrides);folders=list(d['folders']);stem=d['stem'];reasons=list(d['reasons'])
        if d['locale'] and self.engine=='creator':d['locale']=d['locale'].lower()
        rename=(self.overrides.get('renames') or {}).get(base)
        if isinstance(rename,str) and rename:stem=rename;reasons.append('layout-rename')
        typ=classify.target_type(kind,suffix)
        if typ=='audio':typ,folders=classify.audio_category(folders,stem)
        if typ=='json':typ='strings' if classify.is_strings(stem,d['locale']) else 'config'
        if kind=='controller':typ='controller'
        if kind=='font-asset':typ='font-asset'
        if stem is None or d['provenance'] in ('unknown','input-relative-path'):
            stem=(typ.replace('-','_'))+'_'+sha(base.encode())[:6];folders=[self.roots['unsorted']];reasons.append('no-safe-source-name')
            raw_folders=folders
        else:raw_folders=None
        if _HASHED.search(stem.lower()):
            # A content hash is not a name (PROJECT-SPEC 5.5): keep any readable remainder and the module, else name by type.
            stem=re.sub(r'[0-9a-fA-F]{32,}','',stem).strip('_-. ') if not _HASHED.fullmatch(stem.lower()) else ''
            stem=stem or (typ.replace('-','_'))+'_'+sha(base.encode())[:6];reasons.append('hash-source-name')
        name=self._stem(typ,stem)
        if typ=='config':
            lowered=name.lower()
            for tail in ('table','config','conf','cfg','data'):
                if lowered.endswith(tail) and len(name)>len(tail):name=name[:-len(tail)]+'Table';reasons.append('config-table-name');break
        if variant:name+='_'+VARIANTS.get(variant,casing.snake(variant));reasons.append('derived-'+VARIANTS.get(variant,variant))
        if root is None:root=self.roots['content']
        type_dir={'controller':self.types['animation'],'font-asset':self.types['font']}.get(typ,self.types.get(typ))
        module=raw_folders if raw_folders is not None else (folders or ['Common'])
        if typ in ('font','font-asset'):
            module=[casing.folder(stem,self.engine)]
        if typ=='strings':
            locale=d['locale'] or (self.default_locale.lower() if self.engine=='creator' else self.default_locale)
            parts=[root,self.roots['localization'],locale,self.types['strings']]
        elif typ=='scene':
            scenes=self.roots['scenes'] if root==self.roots['content'] else root+'/'+('Scenes' if self.engine=='unity' else 'scenes')
            test='test' in stem.lower().replace('-','_').split('_') or stem.lower().endswith('test')
            parts=[scenes]+([('Tests' if self.engine=='unity' else 'tests')] if test else [])
            if d['minigame']:parts=[root,self.roots['minigames'],casing.folder(d['minigame'],self.engine),'Scenes' if self.engine=='unity' else 'scenes']
        else:
            parts=[root]
            if d['minigame']:parts+=[self.roots['minigames'],casing.folder(d['minigame'],self.engine)]
            elif d['locale']:parts+=[self.roots['localization'],d['locale']]
            parts+=[type_dir]+(module if raw_folders is not None or typ in ('font','font-asset') else self._folders(module))
        ext=('.unity' if self.engine=='unity' else '.scene') if typ=='scene' and not suffix else suffix
        target='/'.join(parts)+'/'+name+(ext or '')
        if len(target.encode())>MAX_PATH_BYTES:
            keep='/'.join(parts[:3])
            target=keep+'/'+casing._limit(name+'_'+sha(target.encode())[:6])+(ext or '');reasons.append('long-path')
        cased=module if raw_folders is not None or typ in ('font','font-asset') else self._folders(module)
        record=dict(sourceId=meta.get('sourceId',base),identity=sid,kind=kind,type=typ,bundle=d['bundle'],originalPath=meta.get('logicalPath'),
            sourceName=meta.get('sourceName'),provenance=d['provenance'],locale=d['locale'],minigame=d['minigame'],
            module=([casing.folder(d['minigame'],self.engine)] if d['minigame'] else [])+cased,stem=stem,reasons=reasons)
        return target,record

    def module_of(self,sid,kind='prefab',metadata=None):
        """Cased module folders an object would live under, e.g. the prefab module that binds a script."""
        return self.describe(sid,kind,'.prefab' if kind=='prefab' else '',metadata=metadata)[1]['module']

    # -- allocation ---------------------------------------------------------------------------------------
    def claim(self,path,owner='existing'):
        """Mark a path written by another stage so later allocations never reuse it."""
        self._claims.setdefault(_fold(path),owner)

    def _canonical_dirs(self,target):
        parts=target.split('/');out=[]
        for part in parts[:-1]:
            key=_fold('/'.join(out+[part]))
            spelled=self._dirs.setdefault(key,'/'.join(out+[part]))
            out=spelled.split('/')
        return '/'.join(out+[parts[-1]])

    def _suffixed(self,target,token):
        slash=target.rfind('/');dot=target.find('.',slash+1)
        dot=len(target) if dot<0 else dot
        return target[:dot]+'_'+token+target[dot:]

    def reserve(self,requests):
        """requests: [(identity,kind,suffix,variant,metadata,qualifier)]. Collision winners are the smallest identities."""
        described=[]
        for sid,kind,suffix,variant,metadata,qualifier in requests:
            key=(sid,kind,suffix,variant)
            if key in self._allocated or key in self._pending:continue
            target,record=self.describe(sid,kind,suffix,variant,metadata)
            self._pending[key]=(target,record,qualifier);described.append(key)
        groups={}
        for key in described:groups.setdefault(_fold(self._pending[key][0]),[]).append(key)
        for folded,keys in sorted(groups.items()):
            for index,key in enumerate(sorted(keys,key=lambda k:(k[0],k[1],k[2],k[3]))):
                target,record,qualifier=self._pending.pop(key)
                self._allocate(key,target,record,qualifier,winner=index==0)

    def _allocate(self,key,target,record,qualifier,winner=True):
        target=self._canonical_dirs(target)
        if not winner or _fold(target) in self._claims:
            alternatives=([self._suffixed(target,casing.snake(qualifier))] if qualifier else [])+[self._suffixed(target,sha(key[0].encode())[:6])]
            for alternative in alternatives:
                if _fold(alternative) not in self._claims:target=alternative;break
            else:raise ValueError('Unresolved deterministic name collision: '+target)
            record['reasons']=sorted(set(record['reasons'])|{'name-collision'})
        self._claims[_fold(target)]=key;self._allocated[key]=target
        record['target']=target;self.records.append(record);self._by_key[key]=record
        return target

    def record(self,sid,kind,suffix,variant=''):
        return self._by_key.get((sid,kind,suffix,variant))

    def path(self,sid,kind,suffix,variant='',metadata=None,qualifier=None):
        key=(sid,kind,suffix,variant)
        if key in self._allocated:return self._allocated[key]
        target,record=self.describe(sid,kind,suffix,variant,metadata)
        return self._allocate(key,target,record,qualifier)

    def folder(self,sid,kind='spine',metadata=None,root=None):
        """A closure folder (Spine skeleton): canonical folder, file names inside are kept by the caller."""
        key=(sid,kind,'','folder')
        if key in self._allocated:return self._allocated[key]
        target,record=self.describe(sid,kind,'','',metadata,root=root)
        slash=target.rfind('/');target=target[:slash]+'/'+casing.folder(target[slash+1:],self.engine)
        return self._allocate(key,target,record,None)

    def report(self):
        logical={r['sourceId']:r['provenance'] for r in self.records}
        return dict(schemaVersion=2,layout=standard.VERSION,engine=self.engine,logicalAssets=len(logical),targetPaths=len(self.records),
            logicalProvenance=dict(Counter(logical.values())),types=dict(Counter(r['type'] for r in self.records)),
            collisionPaths=sum('name-collision' in r['reasons'] for r in self.records),
            overriddenPaths=sum(any(x.startswith('layout-') for x in r['reasons']) for r in self.records),
            unsortedPaths=sum('no-safe-source-name' in r['reasons'] for r in self.records),records=self.records)
