"""Beam Gothic's polygon drawing program, reconstructed from its design rules.

Widths and optical placement values belong to individual designs; stroke and
cut dimensions always come from params. Shapes are drawn at x=0 and spaced last.
"""
from dataclasses import dataclass
from shapely.geometry import Polygon, MultiPolygon
from . import params as p
from .prims import (R, CR, P, diag, union, cut, translate, shear_top,
                    shear_bottom, spur_left, spur_right, corner, inner_corner, mirror, rot180)


@dataclass
class Glyph:
    geom: Polygon | MultiPolygon
    advance: int


def spaced(geom, width, bearing=None, right=None):
    """Place a drawing between its specified side bearings."""
    bearing = p.SB if bearing is None else bearing
    right = bearing if right is None else right
    return Glyph(translate(geom, bearing).simplify(1e-9), int(width+bearing+right))


def stem(x=0, y0=0, y1=None, *, top=True, bottom=True):
    y1 = p.CAP if y1 is None else y1
    g = R(x,y0,x+p.V,y1)
    if top: g = shear_top(g,x,x+p.V,y1)
    if bottom: g = shear_bottom(g,x,x+p.V,y0)
    return g


def arm(x0,x1,y0,y1,*,left=False,right=False,up=True):
    g = R(x0,y0,x1,y1)
    if left: g = spur_left(g,x0,y0,y1,up=up)
    if right: g = spur_right(g,x1,y0,y1,up=up)
    return g


def ring(w, h=None, *, outer=None, inner=None):
    h = p.CAP if h is None else h
    return cut(CR(0,0,w,h,c=outer),CR(p.V,p.T,w-p.V,h-p.T,c=p.CI if inner is None else inner))


def notdef():
    return Glyph(Polygon(),500)


def space():
    return Glyph(Polygon(),240)


def H():
    w=450
    return spaced(union(stem(),stem(w-p.V),R(0,p.BAR_Y0,w,p.BAR_Y1)),w)


def I():
    return spaced(stem(),p.V)


def E():
    w=370
    return spaced(union(R(0,0,p.V,p.CAP),arm(0,w,p.CAP-p.T,p.CAP,right=True),
                        arm(0,w-50,p.BAR_Y0,p.BAR_Y1,right=True),
                        arm(0,w,0,p.T,right=True,up=False)),w)


def F():
    w=360
    return spaced(union(stem(top=False),arm(0,w,p.CAP-p.T,p.CAP,right=True),
                        arm(0,w-50,p.BAR_Y0,p.BAR_Y1,right=True)),w)


def L():
    w=360
    return spaced(union(stem(bottom=False),arm(0,w,0,p.T,right=True,up=False)),w)


def T():
    w=440
    return spaced(union(stem((w-p.V)/2,top=False),arm(0,w,p.CAP-p.T,p.CAP,left=True,right=True)),w)


def B():
    w=430
    # Upper bowl is inset 36 units; only right corners are clipped.
    inset=p.C*.6
    lower=CR(0,0,w,p.BAR_Y1,c=p.C,bl=0,tl=0,tr=inset)
    upper=CR(0,p.BAR_Y0,w-inset,p.CAP,c=p.C,bl=0,tl=0,br=0)
    low_counter=CR(p.V,p.T,w-p.V,p.BAR_Y0,c=p.CI,bl=0,tl=0)
    high_counter=CR(p.V,p.BAR_Y1,w-inset-p.V,p.CAP-p.T,c=p.CI,bl=0,tl=0)
    return spaced(cut(union(lower,upper),low_counter,high_counter),w)


def p_bowl(w):
    """P/R bowl, 410 high, with its lower counter bar 100 units thick."""
    bottom=290  # Bowl bottom, deliberately below the nominal middle bar.
    bowl=CR(0,bottom,w,p.CAP,c=p.C,bl=0,tl=0)
    counter=CR(p.V,bottom+p.BAR,w-p.V,p.CAP-p.T,c=p.CI,bl=0,tl=0)
    return cut(union(bowl,stem(top=False)),counter)


def P_():
    return spaced(p_bowl(420),420)


def R_():
    w=460  # Revised drawing width; bowl was narrowed to 436.
    # Leg has a 132-unit horizontal stroke, slightly less than the stem.
    leg=diag(394,0,232,300,p.V-4)
    leg=shear_bottom(leg,328,328+p.V)
    return spaced(union(p_bowl(436),leg),w,bearing=p.SB,right=p.SBD)


def D():
    w=450
    outer=CR(0,0,w,p.CAP,c=p.C*1.4,bl=0,tl=0)
    inner=CR(p.V,p.T,w-p.V,p.CAP-p.T,c=p.CI+13,bl=0,tl=0)
    return spaced(cut(outer,inner),w)


def O():
    return spaced(ring(460),460)


def Q():
    # The tail is an irregular optical polygon, revised to pull its tip inward.
    tail=P([(230,190),(334,190),(466,-90),(362,-90)])
    return spaced(union(ring(460),tail),430,bearing=p.SB,right=p.SB+p.SBD)


def open_round(w):
    """C-shaped open bowl with spurred top and bottom terminals."""
    outer=CR(0,0,w,p.CAP,tr=0,br=0)
    counter=CR(p.V,p.T,w+p.V,p.CAP-p.T,c=p.CI,tr=0,br=0)
    g=cut(outer,counter)
    g=spur_right(g,w,p.CAP-p.T,p.CAP)
    return spur_right(g,w,0,p.T,up=False)


def C():
    return spaced(open_round(410),410)


def G():
    w=440
    # Right return rises to 340; its inset shelf is 90 units thick.
    g=union(open_round(w),R(w-p.V,p.T,w,340),R(202,340-(p.BAR-10),w,340))
    # The lower right corner is clipped after joining the return to the bowl.
    g=union(g,R(w-p.V,0,w,p.T))
    return spaced(corner(g,w,0,'br'),w)


def J():
    w=370
    g=union(stem(w-p.V,bottom=False),arm(0,w,0,p.T,left=True,up=False))
    return spaced(corner(g,w,0,'br'),w)


def K():
    w=440
    upper=diag(180,280,378,p.CAP,p.D-4)
    upper=shear_top(upper,304,440)
    leg_run=(376-220)/340  # Centerline passes through the 340-unit junction.
    lower=diag(376,0,376-leg_run*p.BAR_Y1,p.BAR_Y1,p.D)
    lower=shear_bottom(lower,312,448)
    # Optical filler closes the gap between the diagonal junction and the stem.
    filler=P([(p.V,250),(230,250),(280,386),(p.V,439)])
    return spaced(union(stem(),upper,lower,filler),w,bearing=p.SB,right=p.SBD)


def m_diagonals(w,depth):
    """The two equal-width diagonals meet on the central V's flat foot."""
    return union(diag(p.D/2,p.CAP,w/2,depth,p.D),
                 diag(w-p.D/2,p.CAP,w/2,depth,p.D))


def M_shape(w,depth=180):
    diagonals=m_diagonals(w,depth)
    diagonals=shear_top(diagonals,0,p.V)
    diagonals=shear_top(diagonals,w-p.V,w)
    return union(stem(),stem(w-p.V),diagonals)


def M():
    return spaced(M_shape(560),560)


def N():
    w=480
    diagonal=diag(p.D/2,p.CAP,w-p.D/2,0,p.D)
    diagonal=shear_top(diagonal,0,p.V)
    diagonal=shear_bottom(diagonal,w-p.V,w)
    return spaced(union(stem(),stem(w-p.V),diagonal),w)


def A():
    w=520
    # Leg centerlines converge above the cap; the crossbar is T minus 18
    # for optical balance in the narrow triangular counter.
    g=union(diag(p.V/2,0,216,p.CAP,p.V),diag(452,0,304,p.CAP,p.V),
            R(140,190,390,190+p.T-18))
    g=shear_top(g,124,372)
    g=shear_bottom(g,0,p.V)
    g=shear_bottom(g,384,520)
    return spaced(g,w,bearing=p.SBD)


def V():
    w=500
    g=union(diag(p.V/2,p.CAP,206,0,p.V),diag(w-p.V/2,p.CAP,294,0,p.V))
    g=shear_top(g,0,p.V)
    g=shear_bottom(g,138,384)
    return spaced(g,w,bearing=p.SBD)


def W():
    w=670
    # Invert M's diagonal skeleton, then give its free ends rising cuts.
    core=rot180(m_diagonals(w,180),w)
    core=shear_bottom(core,0,p.V)
    core=shear_bottom(core,w-p.V,w)
    return spaced(union(stem(),stem(w-p.V),core),w)


def X():
    w=490
    rising=diag(p.V/2,0,w-p.V/2,p.CAP,p.V)
    falling=diag(w-p.V/2,0,p.V/2,p.CAP,p.V)
    falling=shear_top(falling,0,p.V)
    falling=shear_bottom(falling,w-p.V,w)
    return spaced(union(rising,falling),w,bearing=p.SBD)


def Y():
    w=500
    joint=320  # Fork height.
    arms=union(diag(p.V/2,p.CAP,w/2,joint,p.V),diag(w-p.V/2,p.CAP,w/2,joint,p.V))
    arms=shear_top(arms,0,p.V)
    return spaced(union(arms,stem((w-p.V)/2,y1=joint,top=False)),w,bearing=p.SBD)


def Z():
    w=420
    g=union(arm(0,w,p.CAP-p.T,p.CAP,left=True),
            arm(0,w,0,p.T,right=True,up=False),diag(80,p.T,w-80,p.CAP-p.T,p.V+12))
    return spaced(g,w)


def U():
    w=450
    outer=union(R(0,0,w,p.T+p.CI),stem(bottom=False),stem(w-p.V,bottom=False))
    outer=corner(corner(outer,0,0,'bl'),w,0,'br')
    inner=CR(p.V,p.T,w-p.V,p.CAP+p.T,c=p.CI,tl=0,tr=0)
    return spaced(cut(outer,inner),w)


def s_shape(square=False):
    w=410
    top=arm(0,w,p.CAP-p.T,p.CAP,right=True)
    bottom=arm(0,w,0,p.T,left=True,up=False)
    g=union(top,bottom,R(0,p.BAR_Y0,p.V,p.CAP),
            R(w-p.V,0,w,p.BAR_Y1),R(0,p.BAR_Y0,w,p.BAR_Y1))
    if not square:
        g=corner(g,0,p.CAP,'tl')
        g=corner(g,0,p.BAR_Y0,'bl',p.C*.6)
        g=inner_corner(g,p.V,p.CAP-p.T,'br')
    g=corner(g,w,p.BAR_Y1,'tr',p.C*.6)
    g=corner(g,w,0,'br')
    g=inner_corner(g,w-p.V,p.T,'tl')
    return g


def S():
    return spaced(s_shape(),410)


def zero():
    return spaced(ring(410),410)


def one():
    # The flag is an irregular, deliberately narrow numeral-one shoulder.
    flag=P([(10,480),(10,590),(100,p.CAP),(150,p.CAP),(150,620)])
    return spaced(union(flag,stem(150,top=False)),286,right=p.SB+20)


def two():
    return spaced(mirror(s_shape(),410),410)


def five():
    return spaced(s_shape(square=True),410)


def three():
    w=400
    g=union(R(w-p.V,0,w,p.CAP),arm(0,w,0,p.T,left=True,up=False),
            arm(0,w,p.CAP-p.T,p.CAP,left=True),
            arm(110,w,p.BAR_Y0,p.BAR_Y1,left=True))
    return spaced(corner(corner(g,w,0,'br'),w,p.CAP,'tr'),w)


def four():
    w=460
    bar_bottom=200  # Numeral's low crossbar.
    g=union(stem(0,y0=bar_bottom,bottom=False),stem(284),
            arm(0,w,bar_bottom,bar_bottom+p.BAR))
    return spaced(spur_right(g,w,bar_bottom,bar_bottom+p.BAR),w)


def six():
    w=410
    g=union(R(0,0,p.V,p.CAP),arm(0,w,p.CAP-p.T,p.CAP,right=True),CR(0,0,w,p.BAR_Y1,c=p.C,tl=0,tr=p.C*.6))
    g=corner(corner(g,0,p.CAP,'tl'),0,0,'bl')
    hole=CR(p.V,p.T,w-p.V,p.BAR_Y0,c=p.CI,tl=0,tr=0)
    return spaced(cut(g,hole),w)


def nine():
    return spaced(rot180(translate(six().geom,-p.SB),410),410)


def seven():
    w=400
    leg=diag(180,0,w-p.D/2,p.CAP-p.T+10,p.D)
    leg=shear_bottom(leg,116,116+p.D)
    return spaced(union(leg,arm(0,w,p.CAP-p.T,p.CAP,left=True)),w,right=p.SBD)


def eight():
    w=420
    inset=18  # Upper bowl inset, corresponding to its smaller 48-unit chamfer.
    g=union(CR(0,0,w,358,c=p.C,tl=inset,tr=inset),
            CR(inset,p.BAR_Y0,w-inset,p.CAP,c=p.C*.8,bl=0,br=0))
    return spaced(cut(g,CR(p.V,p.T,w-p.V,p.BAR_Y0,c=p.CI),
                      CR(p.V+inset,p.BAR_Y1,w-p.V-inset,p.CAP-p.T,c=p.CI)),w)


def dot():
    # Both edges have the same shear; the dot's vertical thickness is V.
    height=p.V+p.S*p.V
    g=R(0,0,p.V,height)
    return shear_top(shear_bottom(g,0,p.V),0,p.V,height)


def period():
    return spaced(dot(),p.V)


def comma():
    # Irregular flag-like tail, joined to the period at its sheared edge.
    tail=P([(44,20),(p.V,p.S*p.V),(70,-140),(6,-140)])
    return spaced(union(dot(),tail),p.V)


def colon():
    return spaced(union(dot(),translate(dot(),y=330)),p.V)


def semicolon():
    return Glyph(union(comma().geom,translate(period().geom,y=330)),period().advance)


def hyphen():
    return spaced(spur_right(arm(0,280,280,280+p.BAR,left=True,up=False),280,280,280+p.BAR),280,bearing=p.SB+4)


def emdash():
    return spaced(spur_right(arm(0,700,280,280+p.BAR,left=True,up=False),700,280,280+p.BAR),700)


def exclam():
    return spaced(union(dot(),stem(y0=220)),p.V)


def question():
    w=400
    # The squared question hook has no bowl rule: a stepped polygon skeleton.
    hook=union(arm(0,w,p.CAP-p.T,p.CAP,left=True),R(w-p.V,330,w,p.CAP),
               R(132,330,w,330+p.BAR),stem(132,y0=220,y1=430,top=False))
    return spaced(union(hook,translate(dot(),132)),w)


def quote_shape():
    # Quotes taper optically: the head and foot have separate lighter weights.
    # This tapered quadrilateral is an irregular part, then cut by the stem rule.
    center=48
    g=P([(center-(p.V-p.QUOTE_FOOT_LIGHTENING)/2,480),(center+(p.V-p.QUOTE_FOOT_LIGHTENING)/2,480),
         (center+(p.V-p.QUOTE_HEAD_LIGHTENING)/2,p.CAP),(center-(p.V-p.QUOTE_HEAD_LIGHTENING)/2,p.CAP)])
    return shear_top(g,center-(p.V-p.QUOTE_HEAD_LIGHTENING)/2,center+(p.V-p.QUOTE_HEAD_LIGHTENING)/2)


def quotesingle():
    return spaced(quote_shape(),96)


def quoteright():
    return quotesingle()


def quotedbl():
    return spaced(union(quote_shape(),translate(quote_shape(),140)),236)


def slash():
    return spaced(diag(62,-60,342,760,p.D-4),404,bearing=p.SBD-6)


def parenleft():
    # Angular bracket: lighter stroke with 110-unit offsets at its ends.
    h=(p.V-p.BRACKET_LIGHTENING)
    return spaced(union(R(10,120,10+h,580),diag(10+h/2,580,120+h/2,770,h),
                        diag(10+h/2,120,120+h/2,-70,h)),214)


def parenright():
    return spaced(mirror(translate(parenleft().geom,-p.SB),214),214)


def dollar():
    center=205  # Center of the narrow vertical overstrike.
    width=p.V-76  # Optical reduction of the standard stem.
    return spaced(union(s_shape(),R(center-width/2,-90,center+width/2,790)),410)


def plus():
    w=380
    return spaced(union(R(0,290,w,290+p.BAR),R(w/2-(p.V-p.PLUS_LIGHTENING)/2,150,w/2+(p.V-p.PLUS_LIGHTENING)/2,530)),w)


# Production order is the order of the compiled font, including its empty slots.
_BUILDERS = [('.notdef',notdef),('space',space),('H',H),('I',I),('E',E),('F',F),
             ('L',L),('T',T),('B',B),('P',P_),('R',R_),('D',D),('O',O),('Q',Q),
             ('C',C),('G',G),('J',J),('K',K),('M',M),('N',N),('A',A),('V',V),
             ('W',W),('X',X),('Y',Y),('Z',Z),('U',U),('S',S),('zero',zero),
             ('one',one),('two',two),('five',five),('three',three),('four',four),
             ('six',six),('nine',nine),('seven',seven),('eight',eight),
             ('period',period),('comma',comma),('colon',colon),('semicolon',semicolon),
             ('hyphen',hyphen),('emdash',emdash),('exclam',exclam),('question',question),
             ('quotesingle',quotesingle),('quoteright',quoteright),('quotedbl',quotedbl),
             ('slash',slash),('parenleft',parenleft),('parenright',parenright),
             ('dollar',dollar),('plus',plus)]
GLYPHS: dict[str, Glyph] = {name: builder() for name,builder in _BUILDERS}
