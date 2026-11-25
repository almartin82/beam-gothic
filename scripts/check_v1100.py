#!/usr/bin/env python3
"""Compare reconstructed geometry and metrics with the surviving font outlines."""
import argparse
import importlib
import json
from pathlib import Path
import sys

from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'sources'))
from beam import params, glyphs_v1
from beam.prims import snap


def reference(contours):
    """Build clockwise shells minus their counter-clockwise counters."""
    shells, holes = [], []
    for points in contours:
        area2 = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
        (shells if area2 < 0 else holes).append(Polygon(points))
    return unary_union(shells).difference(unary_union(holes))


def vertices(geom):
    """Return all vertices except exactly collinear intermediate points."""
    result=set()
    if geom.is_empty: return result
    polys = [geom] if geom.geom_type == 'Polygon' else geom.geoms
    for poly in polys:
        for ring in [poly.exterior,*poly.interiors]:
            points=[]
            for point in list(ring.coords)[:-1]:
                if not points or points[-1] != point: points.append(point)
            if len(points)>1 and points[0]==points[-1]: points.pop()
            for i,b in enumerate(points):
                a,c=points[i-1],points[(i+1)%len(points)]
                if (b[0]-a[0])*(c[1]-b[1]) != (b[1]-a[1])*(c[0]-b[0]):
                    result.add(b)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--params-probe',action='store_true',help='also rebuild with V increased by four')
    args=parser.parse_args()
    data=json.loads((ROOT/'sources/reference/v1100.json').read_text())['glyphs']
    passed=0
    baseline={}
    for name,record in data.items():
        glyph=glyphs_v1.GLYPHS[name]
        mine=snap(glyph.geom)
        baseline[name]=mine
        ref=reference(record['contours'])
        area=ref.symmetric_difference(mine).area
        vd=len(vertices(ref)^vertices(mine))
        ok=glyph.advance==record['advance'] and area==0 and vd==0
        passed+=ok
        print(f'{"PASS" if ok else "FAIL"} {name}: advance={glyph.advance}/{record["advance"]} sym-diff area={area:g} vertex diff={vd}')
    print(f'{passed}/{len(data)} PASS')
    if args.params_probe:
        original=params.V
        try:
            params.V+=4
            importlib.reload(glyphs_v1)
            unchanged=[]
            for name,glyph in glyphs_v1.GLYPHS.items():
                changed=not baseline[name].equals(snap(glyph.geom))
                print(f'PROBE {name}: {"CHANGED" if changed else "UNCHANGED"}')
                if not changed: unchanged.append(name)
            print('Unchanged by V + 4: '+', '.join(unchanged))
        finally:
            params.V=original
            importlib.reload(glyphs_v1)
    return 0 if passed==len(data) else 1


if __name__=='__main__':
    sys.exit(main())
