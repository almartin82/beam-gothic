"""Straight-edged drawing primitives; all coordinates are font units."""
import numpy as np
from shapely import affinity, transform
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from . import params as p


def P(points):
    """Make a free straight-sided polygon (for genuinely irregular parts)."""
    return Polygon(points)


def R(x0, y0, x1, y1):
    """Make an axis-aligned rectangle."""
    return box(x0, y0, x1, y1)


def CR(x0, y0, x1, y1, c=None, *, bl=None, br=None, tr=None, tl=None):
    """Rectangle with independently adjustable corner chamfers; zero is square."""
    c = p.C if c is None else c
    bl, br, tr, tl = [c if v is None else v for v in (bl, br, tr, tl)]
    return P([(x0+bl,y0),(x1-br,y0),(x1,y0+br),(x1,y1-tr),
              (x1-tr,y1),(x0+tl,y1),(x0,y1-tl),(x0,y0+bl)])


def diag(x0, y0, x1, y1, width=None):
    """Parallelogram between two centerline endpoints, measured horizontally."""
    w = p.D if width is None else width
    return P([(x0-w/2,y0),(x0+w/2,y0),(x1+w/2,y1),(x1-w/2,y1)])


def union(*parts):
    """Join strokes while retaining polygon holes."""
    return unary_union(parts)


def cut(geom, *parts):
    """Subtract one or more counter shapes."""
    return geom.difference(union(*parts))


def translate(geom, x=0, y=0):
    """Move a shape by a font-unit offset."""
    return affinity.translate(geom, xoff=x, yoff=y)


def shear_top(geom, x0, x1, y=None):
    """Cut above the rising S-line whose high point is (x1,y)."""
    y = p.CAP if y is None else y
    a, b = x0-p.SHEAR_PAD, x1+p.SHEAR_PAD
    return cut(geom, P([(a,y+p.S*(a-x1)),(b,y+p.S*(b-x1)),(b,y+2*p.UPM),(a,y+2*p.UPM)]))


def shear_bottom(geom, x0, x1, y=0):
    """Cut below the rising S-line whose low point is (x0,y)."""
    a, b = x0-p.SHEAR_PAD, x1+p.SHEAR_PAD
    return cut(geom, P([(a,y+p.S*(a-x0)),(b,y+p.S*(b-x0)),(b,y-2*p.UPM),(a,y-2*p.UPM)]))


def spur_right(geom, x, y0, y1, *, up=True):
    """Cut a right arm end, retaining K more length at its outer edge."""
    edge0, edge1 = (x-p.K,x) if up else (x,x-p.K)
    return cut(geom, P([(edge0,y0),(edge1,y1),(x+p.UPM,y1),(x+p.UPM,y0)]))


def spur_left(geom, x, y0, y1, *, up=True):
    """Cut a left arm end, retaining K more length at its outer edge."""
    edge0, edge1 = (x+p.K,x) if up else (x,x+p.K)
    return cut(geom, P([(x-p.UPM,y0),(edge0,y0),(edge1,y1),(x-p.UPM,y1)]))


def corner(geom, x, y, which, size=None):
    """Clip a convex corner at (x,y): bl, br, tr, or tl."""
    c = p.C if size is None else size
    dx = c if 'l' in which else -c
    dy = c if 'b' in which else -c
    return cut(geom, P([(x,y),(x+dx,y),(x,y+dy)]))


def inner_corner(geom, x, y, which, size=None):
    """Bevel a concave corner by filling a CI-sized triangle into its cavity.

    ``which`` names the quadrant of the cavity, as for rectangle corners.
    """
    c = p.CI if size is None else size
    dx = -c if 'l' in which else c
    dy = -c if 'b' in which else c
    return union(geom, P([(x,y),(x+dx,y),(x,y+dy)]))


def mirror(geom, width):
    """Reflect horizontally about the center of a width-sized drawing box."""
    return affinity.scale(geom, xfact=-1, yfact=1, origin=(width/2,0))


def rot180(geom, width, height=None):
    """Rotate about the drawing box center (used for six/nine)."""
    height = p.CAP if height is None else height
    return affinity.rotate(geom, 180, origin=(width/2,height/2))


def snap(geom):
    """Round each constructed vertex to the compiler's one-unit grid."""
    # Python round matches the original compile pass, including half-to-even ties.
    # GEOS overlays can leave almost-collinear vertices at shared cut lines.
    # Remove only floating-point noise before rounding so it cannot become a kink.
    return transform(geom.simplify(1e-9), lambda xy: np.rint(xy))
