"""Word splitting and the three casings of monkey-project/1 (PROJECT-SPEC 5.1). No transliteration."""
import re
import unicodedata
from ..io import sha

ACRONYMS={'ui','hud','bgm','sfx','vfx','fx','npc','ai','id','vip','pvp','pve','sdk','2d','3d'}
_UNSAFE=re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_DEVICE=re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',re.I)
SEGMENT_BYTES=64


def _kind(ch):
    if ch.isdigit() and ch.isascii():return 'digit'
    if ch.isascii() and ch.isalpha():return 'upper' if ch.isupper() else 'lower'
    return 'other'


def words(text):
    """Split on separators and case changes; letters and following digits stay together (Room7, Area01)."""
    out=[]
    for chunk in re.split(r'[_\-.\s]+',unicodedata.normalize('NFC',_UNSAFE.sub('_',str(text)))):
        current=''
        for i,ch in enumerate(chunk):
            if not current:current=ch;continue
            prev,kind=_kind(current[-1]),_kind(ch)
            nxt=_kind(chunk[i+1]) if i+1<len(chunk) else None
            split=(kind=='other')!=(prev=='other')
            split=split or (kind=='upper' and (prev=='lower' or prev=='digit' and nxt=='lower'))
            split=split or (kind=='upper' and prev=='upper' and nxt=='lower')
            if split:out.append(current);current=ch
            else:current+=ch
        if current:out.append(current)
    return out


def _cap(word):
    if word.lower() in ACRONYMS and word.isascii():return word.upper()
    return word[:1].upper()+word[1:] if word[:1].isascii() else word


def _joined(parts,separator):
    """Digit-only words attach to the previous word unless that word already ends with a digit."""
    out=[]
    for word in parts:
        if out and word.isdigit() and not out[-1][-1:].isdigit():out[-1]+=word
        elif out and word.isdigit():out[-1]+=(separator or '_')+word
        else:out.append(word)
    return separator.join(out)


def pascal(text):
    return _limit(_joined([_cap(w) for w in words(text)],'') or 'Unnamed')


def kebab(text):
    return _limit(_joined([w.lower() for w in words(text)],'-') or 'unnamed')


def snake(text):
    return _limit('_'.join(w.lower() for w in words(text)) or 'unnamed')


def _limit(value):
    if _DEVICE.match(value):value+='_'
    if len(value.encode())>SEGMENT_BYTES:
        raw=value.encode()[:SEGMENT_BYTES-7].decode('utf-8',errors='ignore')
        value=raw.rstrip('_-')+'_'+sha(value.encode())[:6]
    return value


def folder(text,engine):
    return kebab(text) if engine=='creator' else pascal(text)
