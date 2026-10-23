"""Select native uGUI alignment only when every source child can retain its position."""


def widget_geometry_matches(widget, node, parent):
    if parent is None:
        return False
    left,bottom,right,top=widget['margins']
    size=[parent['size'][0]-left-right,parent['size'][1]-bottom-top]
    position=[left+node['anchor'][0]*size[0]-parent['anchor'][0]*parent['size'][0],
              bottom+node['anchor'][1]*size[1]-parent['anchor'][1]*parent['size'][1]]
    return (all(abs(a-b)<.001 for a,b in zip(size,node['size'])) and
            all(abs(a-b)<.001 for a,b in zip(position,node['position'])))


def cross_axis_mapping(layout, parent, children):
    # Creator linear layouts leave the other axis untouched. uGUI drives both axes;
    # only a shared, representable alignment is safe to emit as a standard group.
    axis = 1 if layout['layoutType'] == 1 else 0
    children = [child for child in children if child['active']]
    before, after = ((layout['padding'][1], layout['padding'][3]) if axis == 1
                     else (layout['padding'][0], layout['padding'][2]))
    extent = parent['size'][axis]
    for scaled in (False, True):
        if scaled and any(child['scale'][axis] <= 0 for child in children):
            continue
        for alignment in (.5, 0., 1.):
            def matches(child):
                size = child['size'][axis] * (child['scale'][axis] if scaled else 1.)
                position = (-parent['anchor'][axis] * extent + before
                            + (extent - before - after - size) * alignment
                            + child['anchor'][axis] * size)
                return abs(position - child['position'][axis]) < .001
            if all(matches(child) for child in children):
                return dict(crossAxisScale=scaled, crossAxisAlignment=alignment)
    return None
