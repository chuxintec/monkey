"""Static production-area check (PROJECT-SPEC 8): source traces never enter Assets/ or assets/."""
import re
from pathlib import PurePosixPath
from ..io import diagnostic
from . import semantic

TRACE_DIRS={'original','recovered','recovery','source','sources','generated','monkey','manual','bulkinitial','imported','sourcemedia','unformatted'}
SOURCE_DIRS={'texture','image','images','prefab','anim','anims','animationclip','spinecook','uispine','sound','sounds','music','font',
    'configs','material','shader','movieclip','uiraw','sprite','gameasset','remoteasset','spineasset','subpackages','raw-assets','minigameres',
    'texture2d','monobehaviour','textasset','animatorcontroller','audioclip','mesh'}
LOCALE_DIRS=set(semantic.LOCALES)-{'zh-hans','zh-hant'}
EXEMPT=('Assets/Game/Editor/Conversion/','Assets/Plugins/','Assets/ThirdParty/','Assets/TextMesh Pro/','Assets/Game/Scripts/')
_HEX=re.compile(r'[0-9a-f]{32}')
_HASHED_CODE=re.compile(r'-[0-9a-f]{6,}\.(cs|ts|js)$')
_CLASS=re.compile(r'\b(class|namespace)\s+(Original|Source|Recovered|Monkey|Generated)[A-Z_.]',re.M)


def scan(paths,texts=None):
    """Diagnostics for production paths; texts optionally maps .cs/.ts paths to source for class-name checks."""
    gaps=[]
    for path in sorted(paths):
        if not path.startswith(('Assets/','assets/')) or path.endswith('.meta') or path.startswith(EXEMPT):continue
        parts=path.split('/');folders=parts[1:-1];name=parts[-1]
        for i,folder in enumerate(folders):
            low=folder.lower()
            parent=folders[i-1].lower() if i else ''
            if parent=='audio' and low in ('music','sfx','voice'):continue
            if low in TRACE_DIRS or low in SOURCE_DIRS or (low in LOCALE_DIRS and parent!='localization'):
                gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Source trace folder in production area: '+folder));break
        stem=PurePosixPath(name).stem
        if _HEX.search(stem.lower()):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'GUID-shaped file name'))
        if _HASHED_CODE.search(name):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Hash-suffixed code file'))
        if name.endswith(('.animationclip.anim','.original.png')) or name.startswith('unknown--'):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Legacy derived/unknown name'))
        if name.endswith('.bytes') and not name.endswith('.skel.bytes'):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Raw source table in production area'))
        if path.startswith('Assets/') and name.endswith('.js'):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Source script in Unity production area'))
        text=(texts or {}).get(path)
        if text and _CLASS.search(text):gaps.append(diagnostic('LAYOUT_FORBIDDEN_NAME',path,'Source-trace class or namespace prefix'))
    return gaps
