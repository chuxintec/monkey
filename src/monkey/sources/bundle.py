"""Explicit 2.4.15 bundle config, compiled-v1 / pack-v1 subset."""
import re
from pathlib import Path
from .. import __version__
from ..io import safe, inside, read, load, sha, new_output, write_json, finish, diagnostic
from .compiled import asset_key, decode_document, ADAPTERS, fail, at, array, ParseError

PROFILE = 'cocos-2.4.15-bundle'


def pairs(values, location):
    values = array(values, location)
    if len(values) % 2:
        fail('INVALID_PAIRS', location, 'Expected key/version pairs')
    result = {}
    for key, value in zip(values[::2], values[1::2]):
        if type(key) not in (int, str) or not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', value):
            fail('INVALID_VERSION', location, 'Invalid key or version token')
        tag = (type(key).__name__, key)
        if tag in result:
            fail('DUPLICATE_VERSION', location, str(key))
        result[tag] = value
    return result


class Bundle:
    def __init__(self, config):
        self.config_path = safe(config)
        self.root = self.config_path.parent
        self.inputs = {}
        self.config = self.json(self.config_path)
        c = self.config
        if not isinstance(c, dict) or not isinstance(c.get('name'), str):
            fail('INVALID_CONFIG', '$', 'Expected named bundle config')
        if c.get('engineVersion', '2.4.15') != '2.4.15':
            fail('UNSUPPORTED_VERSION', '$.engineVersion', 'Profile requires 2.4.15')
        for field,expected in [('packs',dict),('paths',dict),('types',list),('versions',dict),('deps',list)]:
            if field in c and not isinstance(c[field],expected):
                fail('INVALID_CONFIG','$. '+field,'Unexpected table shape')
        self.keys, self.invalid_keys = [], {}
        for i,v in enumerate(array(c.get('uuids'),'$.uuids')):
            try:
                self.keys.append(asset_key(v,f'$.uuids[{i}]'))
            except ParseError as error:
                # An unrelated malformed identity must not erase the selected slice.
                if not isinstance(v,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',v):
                    raise
                self.keys.append(v)
                self.invalid_keys[i] = str(error)
        if len(self.keys) > 50000 or len(set(self.keys)) != len(self.keys):
            fail('INVALID_IDENTITIES', '$.uuids', 'Duplicate IDs or asset budget exceeded')
        self.lookup = {key: i for i, key in enumerate(self.keys)}
        self.members = {}
        for pack, indices in c.get('packs', {}).items():
            if not re.fullmatch(r'[A-Za-z0-9_-]+', pack):
                fail('INVALID_PACK', '$.packs', pack)
            for ordinal, index in enumerate(array(indices, '$.packs.' + pack)):
                at(self.keys, index, '$.packs.' + pack)
                if index in self.members:
                    fail('AMBIGUOUS_PACK', '$.packs', str(index))
                self.members[index] = (pack, ordinal, len(indices))
        self.versions = {kind: pairs(c.get('versions', {}).get(kind, []), '$.versions.' + kind)
                         for kind in ('import', 'native')}
        redirects = array(c.get('redirect', []),'$.redirect')
        if len(redirects)%2:
            fail('INVALID_REDIRECT','$.redirect','Expected index/dependency pairs')
        self.redirects = {}
        for index,ordinal in zip(redirects[::2],redirects[1::2]):
            at(self.keys,index,'$.redirect.index')
            at(c.get('deps',[]),ordinal,'$.redirect.dependency')
            if index in self.redirects:
                fail('DUPLICATE_REDIRECT','$.redirect',str(index))
            self.redirects[index] = c['deps'][ordinal]
        self.cache = {}

    def record(self, path):
        path = safe(path)
        if not path.is_relative_to(self.root):
            fail('UNSAFE_PATH', str(path), 'Source outside bundle')
        raw = read(path)
        key = path.relative_to(self.root).as_posix()
        info = dict(path=key, sha256=sha(raw), bytes=len(raw))
        if key in self.inputs and self.inputs[key] != info:
            fail('SOURCE_CHANGED', key, 'Source changed during inspection')
        self.inputs[key] = info
        if sum(v['bytes'] for v in self.inputs.values()) > 128 * 1024 * 1024:
            fail('BYTE_BUDGET', '$', 'Selected source closure exceeds 128 MiB')
        return raw

    def json(self, path):
        return load(self.record(path))

    def version(self, kind, index, identity):
        versions = self.versions[kind]
        tags = [('str', identity)] if index is None else [('int', index), ('str', identity)]
        found = {versions[t] for t in tags if t in versions}
        if len(found) > 1:
            fail('AMBIGUOUS_VERSION', '$.versions.' + kind, identity)
        return next(iter(found), None)

    def select(self, kind, identity, version, extension):
        folder = inside(self.root, f'{kind}/{identity[:2]}')
        stem = identity + ('.' + version if version else '')
        if extension:
            candidates = [folder / (stem + extension)]
        else:
            candidates = sorted(folder.glob(stem + '.*'))
            # With no declared version only single-extension native files are valid.
            if version is None:
                candidates = [p for p in candidates if p.name.count('.') == 1]
        if len(candidates) != 1 or not candidates[0].is_file():
            fail('MISSING_OR_AMBIGUOUS_FILE', str(folder / stem), 'Exactly one configured file is required')
        return safe(candidates[0])

    def asset(self, index):
        key = at(self.keys, index, '$.selection')
        if index in self.invalid_keys:
            fail('INVALID_SELECTED_IDENTITY', f'$.uuids[{index}]', self.invalid_keys[index])
        source_id = self.config['name'] + ':' + key
        paths = self.config.get('paths', {}).get(str(index))
        kind = at(self.config.get('types', []), paths[1], '$.paths.type') if paths else None
        if paths and (not isinstance(paths,list) or len(paths)<2 or not isinstance(paths[0],str)):
            fail('INVALID_PATH_TABLE','$.paths','Expected [logicalPath,typeIndex]')
        entry = dict(sourceId=source_id, key=key, index=index, kind=kind,
                     logicalPath=paths[0] if paths else None, references=[], native=None)
        if index in self.redirects:
            entry.update(kind='redirect', document=None,redirectBundle=self.redirects[index],
                         redirectTarget=self.redirects[index]+':'+key)
            return entry
        member = self.members.get(index)
        identity, ordinal, count = member if member else (key, None, None)
        version = self.version('import', None if member else index, identity)
        path = self.select('import', identity, version, '.json')
        if path not in self.cache:
            self.cache[path] = self.json(path)
        raw = self.cache[path]
        if member and isinstance(raw, dict) and raw.get('type') == 'cc.Texture2D':
            sections = decode_document(raw, ADAPTERS[2])['sections']
            if len(sections) != count:
                fail('PACK_MEMBERSHIP_MISMATCH',str(path),'Texture pack count differs from config')
            section = sections[ordinal]
            decoded = dict(root=0,instances=[{'__type__':section['type'],'data':section['data']}])
        elif member:
            if not isinstance(raw,list) or len(raw)!=6 or not isinstance(raw[5],list) or len(raw[5])!=count:
                fail('PACK_MEMBERSHIP_MISMATCH',str(path),'Pack shape/count differs from config')
            # Decode selected section only: unrelated scripts do not expand this scope.
            decoded = decode_document(raw[:5]+array(raw[5][ordinal],f'$.sections[{ordinal}]'),ADAPTERS[0])
        else:
            decoded = decode_document(raw,ADAPTERS[0])
        entry.update(document=decoded, importPath=path.relative_to(self.root).as_posix(),
                     pack=identity if member else None, packOrdinal=ordinal)
        if kind is None:
            root_object=decoded['instances'][decoded['root']]
            if not isinstance(root_object,dict):
                fail('UNSUPPORTED_ASSET_ROOT',str(path),'Expected typed asset object')
            entry['kind'] = root_object.get('__type__')
        pending = [decoded]
        refs = set()
        while pending:
            value = pending.pop()
            if isinstance(value, dict):
                if '__uuid__' in value:
                    refs.add(asset_key(value['__uuid__']))
                pending.extend(value.values())
            elif isinstance(value, list):
                pending.extend(value)
        entry['references'] = sorted(refs)
        return entry


def inspect(config, selection, output, dependency_sources=(), evidence_sources=()):
    if len(dependency_sources)>15:
        fail('BUNDLE_BUDGET','$','At most 16 explicit bundles')
    primary = Bundle(config)
    bundles = {primary.config['name']:primary}
    for path in dependency_sources:
        dep = Bundle(path)
        if dep.config['name'] in bundles:
            fail('DUPLICATE_BUNDLE',str(path),'Bundle names must be unique')
        bundles[dep.config['name']] = dep
    # Explicit indices prevent accidentally parsing an entire private game.
    if not selection:
        fail('EMPTY_SELECTION', '$.selection', 'At least one --asset-index is required')
    pending = [(primary.config['name'],i) for i in selection]
    seen = set()
    assets, diagnostics = [], [diagnostic('INVALID_CONFIG_IDENTITY', name+f':$.uuids[{i}]',message) for name,b in bundles.items() for i,message in b.invalid_keys.items()]
    while pending:
        name,index = pending.pop(0)
        bundle = bundles[name]
        if sum(v['bytes'] for b in bundles.values() for v in b.inputs.values())>128*1024*1024:
            fail('BYTE_BUDGET','$','Combined bundle closure exceeds 128 MiB')
        if (name,index) in seen:
            continue
        seen.add((name,index))
        if len(seen) > 2048:
            fail('ASSET_BUDGET', '$', 'Selected dependency closure exceeds 2048 assets')
        key = at(bundle.keys, index, '$.selection')
        sid = bundle.config['name'] + ':' + key
        try:
            entry = bundle.asset(index)
        except (ParseError, FileNotFoundError) as error:
            entry = dict(sourceId=sid, key=key, index=index, references=[], document=None, native=None, kind=None)
            diagnostics.append(diagnostic(getattr(error, 'code', 'MISSING_IMPORT'),
                                          getattr(error, 'location', str(config)), str(error), sid))
        entry['bundle'] = name
        if entry.get('redirectTarget'):
            target = bundles.get(entry['redirectBundle'])
            if target is not None and key in target.lookup:
                pending.append((entry['redirectBundle'],target.lookup[key]))
            else:
                diagnostics.append(diagnostic('REDIRECT_UNRESOLVED',sid,'Supply exact dependency bundle config: '+entry['redirectBundle'],sid))
            assets.append(entry)
            continue
        # Native-only texture keys can legitimately have no import document.
        try:
            native_version = bundle.version('native', index, key)
            folder = bundle.root / 'native' / key[:2]
            if native_version is not None or any(folder.glob(key + '.*')):
                native_name=None
                if entry.get('document'):
                    native_name=entry['document']['instances'][entry['document']['root']].get('_native')
                if native_name and not native_name.startswith('.'):
                    if Path(native_name).name!=native_name:
                        fail('UNSAFE_NATIVE_NAME',sid,'Native basename must not contain directories')
                    stem=key+('.'+native_version if native_version else '')
                    directory=inside(bundle.root,f'native/{key[:2]}/{stem}')
                    native_path=inside(directory,native_name)
                    if not native_path.is_file():
                        # Some source profiles publish a direct versioned file instead.
                        native_path=bundle.select('native',key,native_version,None)
                else:
                    native_path = bundle.select('native', key, native_version, None)
                bundle.record(native_path)
                entry['native'] = native_path.relative_to(bundle.root).as_posix()
                if entry['document'] is None:
                    # Preserve missing-import diagnostic: native existence is not proof of metadata.
                    entry['kind'] = 'native'
        except (ParseError, FileNotFoundError) as error:
            diagnostics.append(diagnostic(getattr(error, 'code', 'MISSING_NATIVE'), str(folder), str(error), sid))
        for ref in entry['references']:
            if ref in bundle.lookup:
                pending.append((name,bundle.lookup[ref]))
            else:
                diagnostics.append(diagnostic('EXTERNAL_REFERENCE', entry.get('importPath', '$'),
                                              'Reference absent from selected bundle: ' + ref, sid))
        assets.append(entry)
    # Detect mutation of any observed source before publishing the manifest.
    inputs = []
    for name,bundle in bundles.items():
        for relative, info in bundle.inputs.items():
            if sha(read(inside(bundle.root, relative))) != info['sha256']:
                fail('SOURCE_CHANGED', relative, 'Source changed during inspection')
            inputs.append(dict(bundle=name,**info))
    if len(evidence_sources)>8:fail('EVIDENCE_BUDGET','$','At most eight explicit source evidence files')
    evidence=[]
    for path in evidence_sources:
        path=safe(path);raw=read(path)
        evidence.append(dict(path=str(path),sha256=sha(raw),bytes=len(raw)))
    out = new_output(output, [*[b.root for b in bundles.values()],*[safe(p) for p in evidence_sources]])
    report = dict(schemaVersion=1, toolVersion=__version__, sourceProfile=PROFILE,
                  sourceVersion='2.4.15', versionEvidence='explicit profile declaration; compiled header validated',
                  sourceRoot=str(primary.root), sourceRoots={name:str(b.root) for name,b in bundles.items()},
                  bundle=primary.config['name'], selection=selection,evidenceFiles=evidence,
                  inputs=sorted(inputs, key=lambda x: (x['bundle'],x['path'])),
                  assets=sorted(assets, key=lambda x: x['sourceId']), diagnostics=diagnostics)
    write_json(out / 'source-manifest.json', report)
    return finish(out, report)
