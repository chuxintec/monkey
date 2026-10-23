"""Finite conversion-time AnimationClip subset. No source callbacks or runtime evaluation."""
import math
from ..io import diagnostic, sha
from ..sources.compiled import fail, ParseError

SCHEMA=1


def finite(value,location):
    if type(value) not in (int,float) or not math.isfinite(value):fail('ANIMATION_INVALID_NUMBER',location,'Expected finite numeric value')
    return value


def normalize_clip(value,sid,location):
    gaps=[];tracks=[];events=[]
    def gap(code,loc,msg):gaps.append(diagnostic(code,loc,msg,sid))
    duration=finite(value.get('_duration',0),location+'/_duration');sample=finite(value.get('sample',60),location+'/sample')
    speed=finite(value.get('speed',1),location+'/speed');wrap=value.get('wrapMode',1)
    timing=0<duration<=600 and 0<sample<=240 and speed==1 and type(wrap) is int and wrap in (1,2)
    if not timing:gap('ANIMATION_TIMING_UNSUPPORTED',location,'Only positive duration <=600s, sample <=240, speed=1 and explicit/default Normal or Loop')
    known={'__type__','_name','_objFlags','_duration','sample','speed','wrapMode','curveData','events','_native'}
    for key in value.keys()-known:gap('ANIMATION_FIELD_UNSUPPORTED',location+'/'+key,'Unknown clip field')
    curve=value.get('curveData',{})
    if not isinstance(curve,dict):fail('ANIMATION_INVALID_CURVES',location,'Expected curveData object')
    sections=[('',curve,location+'/curveData')]
    paths=curve.get('paths',{})
    if not isinstance(paths,dict) or len(paths)>128:fail('ANIMATION_TRACK_BUDGET',location,'Invalid or excessive paths')
    sections += [(path,body,location+'/curveData/paths/'+path) for path,body in paths.items()]
    for path,body,loc in sections:
        if not isinstance(path,str) or (path and any(p in ('','..','.') for p in path.split('/'))) or not isinstance(body,dict):
            gap('ANIMATION_PATH_UNSUPPORTED',loc,'Expected canonical node path');continue
        for key in body.keys()-({'props','comps','paths'} if path=='' else {'props','comps'}):
            gap('ANIMATION_CURVE_GROUP_UNSUPPORTED',loc+'/'+key,'Unknown curve group')
        if body.get('comps'):gap('ANIMATION_COMPONENT_CURVES_UNSUPPORTED',loc+'/comps','Component curves need a separate reviewed mapping')
        props=body.get('props',{})
        if not isinstance(props,dict):fail('ANIMATION_INVALID_CURVES',loc,'Expected props object')
        for prop,frames in props.items():
            tloc=loc+'/props/'+prop
            if not isinstance(frames,list) or len(frames)>8192:fail('ANIMATION_KEY_BUDGET',tloc,'Invalid/excessive key list')
            if not frames:continue
            channels={'x':['position.x'],'y':['position.y'],'z':['position.z'],
                      'scaleX':['scale.x'],'scaleY':['scale.y'],'scaleZ':['scale.z'],'opacity':['opacity']}.get(prop)
            if prop not in ('position','scale') and channels is None:
                gap('ANIMATION_PROPERTY_UNSUPPORTED',tloc,'Unsupported property '+prop);continue
            try:
                keys=[];dimensions=None;last=-1
                for i,f in enumerate(frames):
                    kloc=tloc+'/'+str(i)
                    if not isinstance(f,dict):fail('ANIMATION_INVALID_KEY',kloc,'Expected frame object')
                    unknown=f.keys()-{'frame','value','curve'}
                    if unknown:fail('ANIMATION_KEY_FIELD_UNSUPPORTED',kloc,'Unknown key fields: '+','.join(sorted(unknown)))
                    time=finite(f.get('frame'),kloc+'/frame')
                    if time<=last or time<0 or time>duration+1e-9:fail('ANIMATION_TIME_ORDER',kloc,'Times must strictly increase within duration')
                    if i==0 and time!=0:fail('ANIMATION_START_UNSUPPORTED',kloc,'First subset requires key at time zero')
                    last=time;mode=f.get('curve')
                    if mode in (None,'linear'):interpolation='linear'
                    elif mode=='constant':interpolation='step'
                    else:fail('ANIMATION_INTERPOLATION_UNSUPPORTED',kloc+'/curve','Only linear and constant(step) are verified; no easing approximation')
                    raw=f.get('value')
                    if prop in ('position','scale'):
                        if isinstance(raw,dict) and raw.get('__value_type__') in (0,1):raw=raw.get('values')
                        if not isinstance(raw,list) or len(raw) not in (2,3):fail('ANIMATION_VECTOR_UNSUPPORTED',kloc,'Expected 2D/3D vector')
                        vals=[finite(v,kloc+'/value') for v in raw]
                    else:vals=[finite(raw,kloc+'/value')]
                    if dimensions is not None and dimensions!=len(vals):fail('ANIMATION_VECTOR_UNSUPPORTED',kloc,'Vector dimensions changed')
                    dimensions=len(vals)
                    if prop=='opacity' and not 0<=vals[0]<=255:fail('ANIMATION_OPACITY_BOUNDS',kloc,'Opacity must be 0..255')
                    keys.append(dict(time=time,values=vals,interpolation=interpolation,sourceLocation=kloc))
                names=[prop+'.'+axis for axis in 'xyz'[:dimensions]] if prop in ('position','scale') else channels
                for axis,name in enumerate(names):
                    scalar=[dict(time=k['time'],value=k['values'][axis],interpolation=k['interpolation']) for k in keys]
                    if scalar[-1]['time']<duration:scalar.append(dict(time=duration,value=scalar[-1]['value'],interpolation='linear'))
                    tracks.append(dict(sourceId=sid+'@'+path+'/'+name,nodePath=path,property=name,keys=scalar,sourceLocation=tloc))
            except ParseError as e:gap(e.code,e.location,e.message)
    if len(tracks)>256:fail('ANIMATION_TRACK_BUDGET',location,'Too many scalar channels')
    raw_events=value.get('events',[])
    if not isinstance(raw_events,list) or len(raw_events)>1024:fail('ANIMATION_EVENT_BUDGET',location,'Invalid/excessive events')
    for i,e in enumerate(raw_events):
        eloc=location+'/events/'+str(i)
        if not isinstance(e,dict) or not isinstance(e.get('func'),str) or not isinstance(e.get('params',[]),list):
            gap('ANIMATION_EVENT_UNSUPPORTED',eloc,'Expected frame, function name and JSON params');continue
        time=finite(e.get('frame'),eloc+'/frame')
        if time<0 or time>duration:gap('ANIMATION_EVENT_TIME_INVALID',eloc,'Event outside duration');continue
        events.append(dict(time=time,function=e['func'],parameters=e.get('params',[]),sourceLocation=eloc,binding='manual-only',executed=False))
        gap('ANIMATION_EVENT_BINDING_REQUIRED',eloc,'Event is a source contract only; no native callback generated')
    return dict(sourceId=sid,name=value.get('_name','Animation'),duration=duration,sample=sample,wrap='loop' if wrap==2 else 'normal',
                timingSupported=timing,tracks=tracks,events=events,sourceLocation=location,partial=bool(gaps)),gaps


def sample(keys,time):
    """Offline QA reference for finite scalar tracks; never emitted to a Player."""
    if time<=keys[0]['time']:return keys[0]['value']
    for a,b in zip(keys,keys[1:]):
        if time<b['time']:
            return a['value'] if a['interpolation']=='step' else a['value']+(b['value']-a['value'])*(time-a['time'])/(b['time']-a['time'])
    return keys[-1]['value']


def plan_clips(ir,namespace,profile,selection=None):
    clips=ir.get('animationClips',[])
    if ('animationSchemaVersion' in ir or clips) and ir.get('animationSchemaVersion')!=SCHEMA:fail('UNSUPPORTED_ANIMATION_IR','$','Expected animation schema 1')
    known={c['sourceId'] for c in clips};selection=set(selection or known)
    if selection-known:fail('UNKNOWN_ANIMATION_SELECTION','$',str(sorted(selection-known)))
    nodes={n['sourceId']:n for n in ir['nodes']};out=[];gaps=[]
    for clip in clips:
        if clip['sourceId'] not in selection:continue
        owners=[c for c in ir['components'] if c['type']=='cc.Animation' and clip['sourceId'] in c.get('clips',[]) and c.get('node') in nodes]
        if not owners:gaps.append(diagnostic('ANIMATION_OWNER_MISSING',clip['sourceLocation'],'No source Animation component binding',clip['sourceId']))
        for owner in owners:
            root=nodes[owner['node']];tracks=[]
            for track in clip['tracks']:
                current=root;valid=True
                for part in track['nodePath'].split('/') if track['nodePath'] else []:
                    matches=[nodes[k] for k in current['children'] if nodes[k]['name']==part]
                    if len(matches)!=1:valid=False;break
                    current=matches[0]
                if not valid:
                    gaps.append(diagnostic('ANIMATION_TARGET_MISSING_OR_AMBIGUOUS',track['sourceLocation'],'Target path does not resolve uniquely',clip['sourceId']));continue
                if any('/' in n['name'] for n in [root,current]):
                    gaps.append(diagnostic('ANIMATION_TARGET_PATH_UNSUPPORTED',track['sourceLocation'],'Node names contain hierarchy separator',clip['sourceId']));continue
                if track['property'].startswith('position.') and any(c.get('enabled') and ((c['type']=='cc.Widget' and c['node']==current['sourceId'] and c.get('flags')) or (c['type']=='cc.Layout' and c['node']==current['parent'])) for c in ir['components']):
                    gaps.append(diagnostic('ANIMATION_LAYOUT_CONFLICT',track['sourceLocation'],'Layout/Widget owns animated position',clip['sourceId']));continue
                t=dict(track,node=current['sourceId'],path=track['nodePath'])
                if profile.startswith('unity-'):
                    prop=track['property'];t['valueScale']=1/255 if prop=='opacity' else 1
                    t['nativeType']='CanvasGroup' if prop=='opacity' else ('RectTransform' if prop.startswith('position.') else 'Transform')
                    t['nativeProperty']={'position.x':'m_AnchoredPosition.x','position.y':'m_AnchoredPosition.y','position.z':'m_LocalPosition.z','opacity':'m_Alpha'}.get(prop,'m_LocalScale.'+prop[-1])
                else:t.update(valueScale=1,nativeType='UIOpacity' if track['property']=='opacity' else 'Node',nativeProperty=track['property'])
                t['keys']=[dict(k,value=k['value']*t['valueScale']) for k in track['keys']]
                times=sorted(set([k['time'] for k in t['keys']]+[(a['time']+b['time'])/2 for a,b in zip(t['keys'],t['keys'][1:])]))
                t['probes']=[dict(time=time,value=sample(t['keys'],time)) for time in times];tracks.append(t)
            counts={}
            for t in tracks:counts[(t['node'],t['property'])]=counts.get((t['node'],t['property']),0)+1
            if any(n>1 for n in counts.values()):
                gaps.append(diagnostic('ANIMATION_CHANNEL_COLLISION',clip['sourceLocation'],'Overlapping source properties target the same native channel',clip['sourceId']))
                tracks=[t for t in tracks if counts[(t['node'],t['property'])]==1]
            identity=sha((namespace+'/'+clip['sourceId']+'/'+owner['sourceId']).encode())[:24]
            out.append(dict(id=clip['sourceId']+'@'+owner['sourceId'],name=clip['name'],root=owner['node'],duration=clip['duration'],sample=clip['sample'],
                wrap=clip['wrap'],tracks=tracks,convertible=bool(tracks) and clip['timingSupported'],partial=clip['partial'] or len(tracks)!=len(clip['tracks']),
                events=clip['events'],path=('Assets/Generated/Animations/' if profile.startswith('unity-') else 'assets/generated/animations/')+identity+'.anim',autoPlay=False))
    from ..names import Names
    naming=Names(ir.get('sourceNames'))
    for item in out:
        source=item['id'].split('@',1)[0]
        meta=dict(ir.get('sourceNames',{}).get(source,{}));meta['sourceId']=source
        if not meta.get('sourceName'):meta['sourceName']=item['name']
        item['path']=naming.path(item['id'],'.anim','Assets/Generated/Animations' if profile.startswith('unity-') else 'assets/generated/animations',metadata=meta)
        item['nameEvidence']=naming.records[-1]
    return out,gaps


def module_report(animations):
    return dict(schemaVersion=SCHEMA,module='finite-ui-animation',nativeValidation='not_run',callbacksGenerated=False,
        clips=animations,allowedPaths=['Assets/Manual/','assets/manual/'],requirements=['Bind playback explicitly in native code','Review unsupported source channels','Wire events only after business implementation'])


def handoff_task(animations,diagnostics):
    return dict(taskId='finite-ui-animation',module='finite-ui-animation',moduleName='Finite UI animation',rootCause='animation-module',
        sourceRefs=([a['id'] for a in animations] or sorted({d['sourceId'] for d in diagnostics if d['code'].startswith('ANIMATION_') and d.get('sourceId')})),generatedTargets=[a['path'] for a in animations],allowedPaths=['Assets/Manual/','assets/manual/'],
        gaps=[d for d in diagnostics if d['code'].startswith('ANIMATION_')],verificationScope=['Native clip re-load, bindings, keys and midpoint probes','Unsupported channels and explicit playback/event wiring'])


def verify_native(specs,actual,native_files):
    gaps=[];actual=actual or [];by_id={a['id']:a for a in actual};expected={a['id']:a for a in specs if a['convertible']}
    def near(a,b):return type(a) in (int,float) and math.isfinite(a) and abs(a-b)<1e-4
    def numbers_equal(a,b):return isinstance(a,list) and len(a)==len(b) and all(near(x,y) for x,y in zip(a,b))
    if set(by_id)!=set(expected) or len(by_id)!=len(actual):
        gaps.append(diagnostic('ANIMATION_READBACK_MISMATCH','animations','Native clip identity set differs'))
    for sid,spec in expected.items():
        a=by_id.get(sid,{})
        good=a.get('path')==spec['path'] and spec['path'] in native_files and bool(a.get('guid') or a.get('uuid'))
        good=good and near(a.get('duration'),spec['duration']) and a.get('wrap')==spec['wrap'] and a.get('eventCount')==0 and a.get('curveCount')==len(spec['tracks'])
        tracks={(t['path'],t['nativeType'],t['nativeProperty']):t for t in spec['tracks']}
        observed={(t.get('path'),t.get('nativeType'),t.get('property')):t for t in a.get('tracks',[])}
        good=good and set(tracks)==set(observed) and len(observed)==len(a.get('tracks',[]))
        for key,t in tracks.items():
            n=observed.get(key,{})
            good=good and numbers_equal(n.get('times'),[k['time'] for k in t['keys']]) and numbers_equal(n.get('values'),[k['value'] for k in t['keys']])
            good=good and n.get('interpolations')==[k['interpolation'] for k in t['keys']]
            good=good and numbers_equal(n.get('probeTimes'),[p['time'] for p in t['probes']]) and numbers_equal(n.get('probeValues'),[p['value'] for p in t['probes']])
        if not good:gaps.append(diagnostic('ANIMATION_READBACK_MISMATCH',spec['path'],'Saved binding/time/value/interpolation/probes/events differ',sid))
    return gaps
