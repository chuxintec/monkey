"""Static production-area check (PROJECT-SPEC 8): source traces never enter Assets/ or assets/."""
import re
from pathlib import PurePosixPath
from ..io import diagnostic
from . import semantic,standard

TRACE_DIRS=semantic.TRACE_WORDS
SOURCE_DIRS=semantic.SOURCE_ONLY_WORDS
LOCALE_DIRS=set(semantic.LOCALES)-{'zh-hans','zh-hant'}
TYPE_DIRS={v.rsplit('/',1)[-1].lower() for v in [*standard.UNITY_TYPES.values(),*standard.CREATOR_TYPES.values()]}
EXEMPT=('assets/game/editor/conversion/','assets/plugins/','assets/thirdparty/','assets/textmesh pro/','assets/game/scripts/')
_HEX=re.compile(r'[0-9a-f]{32}')
_HASHED_CODE=re.compile(r'-[0-9a-f]{6,}\.(cs|ts|js)$')
_CLASS=re.compile(r'\b(class|namespace)\s+(Original|Source|Recovered|Monkey|Generated)[A-Z_.]',re.M)


def scan(paths,texts=None):
    """Diagnostics for production paths; texts optionally maps .cs/.ts paths to source for class-name checks."""
    gaps=[]
    for path in sorted(paths):
        if not path.startswith(('Assets/','assets/')) or path.endswith('.meta') or path.casefold().startswith(EXEMPT):continue
        parts=path.split('/');folders=parts[1:-1];name=parts[-1]
        for i,folder in enumerate(folders):
            low=folder.lower()
            parent=folders[i-1].lower() if i else ''
            if low=='resources':break  # Resources.Load keys keep their source spelling (PROJECT-SPEC 4.2)
            if parent=='audio' and low in ('music','sfx','voice'):continue
            # A locale bundle directly under a type folder is the legacy bundle-as-folder layout.
            if low in TRACE_DIRS or low in SOURCE_DIRS or (low in LOCALE_DIRS and parent in TYPE_DIRS):
                gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Source trace folder in production area: '+folder));break
        stem=PurePosixPath(name).stem
        if _HEX.search(stem.lower()):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'GUID-shaped file name'))
        if _HASHED_CODE.search(name):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Hash-suffixed code file'))
        if name.endswith(('.animationclip.anim','.original.png')) or name.startswith('unknown--'):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Legacy derived/unknown name'))
        if path.startswith('Assets/') and name.endswith('.js'):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Source script in Unity production area'))
        text=(texts or {}).get(path)
        if text and _CLASS.search(text):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Source-trace class or namespace prefix'))
    return gaps
