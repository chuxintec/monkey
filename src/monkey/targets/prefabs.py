"""One source graph per native Prefab, with explicit graph and reference boundaries."""
from collections import defaultdict
from ..io import sha,diagnostic


def plan_prefabs(ir,components):
    groups=defaultdict(list)
    for node in ir['nodes']:groups[node['sourceId'].split('#')[0]].append(node)
    plans=[];gaps=[]
    for source,nodes in sorted(groups.items()):
        if any(n.get('sourceType')=='cc.Scene' for n in nodes):continue
        ids={n['sourceId'] for n in nodes};roots=[n for n in nodes if n['parent'] is None]
        if len(roots)!=1 or any(n['parent'] and n['parent'] not in ids for n in nodes):
            gaps.append(diagnostic('PREFAB_ROOT_BOUNDARY',source,'Source graph must have exactly one internal root',source));continue
        crossing=[c['sourceId'] for c in components if c.get('node') in ids and
                  any(c.get(k) and c[k] not in ids for k in ('target','content'))]
        if crossing:
            gaps.append(diagnostic('PREFAB_EXTERNAL_NODE_REFERENCE',source,'Native node references cross source graph: '+','.join(crossing),source));continue
        plans.append(dict(sourceId=source,root=roots[0]['sourceId'],nodes=sorted(ids),nodeCount=len(ids),
                          path='Assets/Generated/Views/Sources/'+sha(source.encode())[:24]+'.prefab',
                          nativeValidation='not_run'))
    return plans,gaps
