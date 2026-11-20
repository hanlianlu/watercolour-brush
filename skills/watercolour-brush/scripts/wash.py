#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy==2.5.5", "opencv-python-headless==5.1.0.95"]
# ///
"""Watercolour brush: pencil-and-wash picture-book illustration, painted from pen paths.

A picture is a sheet of cold-press paper and a stack of layers. Paint is transparent: every wash multiplies the light
coming back from the paper (glazing), so two washes over each other are darker than either and nothing is ever covered;
light things are places the paint was kept away from ("out") or taken off again ("lift"). Pigment settles in the
valleys of the paper (granulation), gathers along a drying edge (rim), runs where the paper was wet (wet nodes, bleed)
and skips over the tooth when the brush is dry. Pencil is graphite on the peaks of the same paper.

A drawing is a dict:

    {"frame": (x0, y0, size) | (x0, y0, w, h),   # the part of your authoring grid that becomes the picture
     "out": 512,                                 # output width in px (height follows the frame's aspect)
     "paper": "#F5F1E7",                         # paper colour (default warm off-white)
     "tooth": 1.0,                               # how visible the paper tooth is on bare paper, 0 = none (1 is this look's
                                                 # quiet tooth: `look.py texture` reads about 1.5 on bare paper)
     "weave": 1.0,                               # size of the paper's grain, and
     "fine": 1.0,                                # size of the brush's own marks (rim, pooling, bristles, pencil grain). Both are
                                                 # sized against the picture: 1 suits a 512 portrait whatever "out" is. Elsewhere:
                                                 # head height in output px (hair top to chin) / 330 x 512 / out, at most 1
                                                 # (0.65 for a half-length at 1024). "study" / "hatch" sizes shrink with "fine"
     "seed": 1,                                  # paper and hand: same seed, same pixels
     "mirror": False,                            # flip left-right at the end
     "eyes": ((x, y), (x, y)),                   # optional, for faces: sets the head's own axes (see "head" and "part")
     "under": IMAGE, "masks": {"skin": MASK},    # optional: an underdrawing the brush looks at (a picture on this paper colour,
                                                 # a file or an array, any size) and named areas for "clip" / "out"
     "layers": [...]}                            # painted in order

A layer is one of

    {"name": "face", "path": NODES}                                       a reserved shape: no paint, only remembered as "face" (it takes
                                                                          "clip" / "out" / "holes" and every edge option: "soft", "miss", ...)
    {"path": NODES, "wash": "#E9C3A2"}                                    a wash: the colour it has on bare paper at full strength
    {... "alpha": 0.6}                                                    thinner (or above 1: heavier) paint
    {... "clip": "face", "out": ["eye_l", "eye_r"]}                       kept inside / kept off other shapes (a name or a list)
    {... "wet": 6}                                                        edges near nodes tagged "w" run soft over this distance
    {... "soft": 10}                                                      every edge soft (a glaze laid on damp paper)
    {... "bleed": 8}                                                      wet-in-wet: the outline wanders by this much and blooms
    {... "fade": ((x, y), (x, y))}                                        full strength at the first point, gone at the second
    {... "grade": [((x, y), 1.0), ((x, y), 0.4), ((x, y), 0.1)]}          a wet gradient INSIDE one shape: the wash's strength at a few points,
                                                                          flowing from one to the next with no edge (loaded at the armpit,
                                                                          thin at the elbow); the outline keeps its own edges
    {... "rim": 0.25, "grain": 0.1, "pool": 0.08}                        edge darkening, granulation, unevenness of the wash
    {... "wobble": 0.35}                                                  how far the hand strays from the path (0 for exact shapes)
    {... "miss": 2.5}                                                     the wash strays from the drawing, slowly: short of it here, over it there
                                                                          (the same on every shape with the same "miss": name the missed shape, clip to it)
    {... "ragged": 2.5}                                                   unevenly damp paper: the edge crawls by about this much, and a wet edge
                                                                          ("w" nodes, "soft", "bleed") dries hard after all along some stretches
    {... "dry": 0.6}                                                      a brush not fully loaded: a hard edge crumbles on the tooth, a wet one
                                                                          breaks up at its thin end (0..1)
    {... "settle": 0.3}                                                   drying paint gathers: a broad darker band inside the edges, here more, there
                                                                          none, and a few big pools
    {... "sediment": 0.25}                                                a pigment that granulates (the heavy, dark ones): fine specks in the paper's pits
    {... "broken": 0.4}                                                   the rim comes and goes along the edge (0..1)
    {... "seed": 2}                                                       another throw of the dice for this one layer (where it crawls, pools, dries hard)
    {"path": NODES, "bloom": 0.4}                                         a backrun in the paint already there: lighter inside, its pigment pushed into a
                                                                          crinkled line at the edge ("w" nodes leave it open; takes "ragged", "rim", "broken")
    {"path": NODES, "sparkle": 0.3}                                       paper left dry: specks on the peaks of the tooth, in patches (also on a "stroke")
    {"path": NODES, "lift": 0.8}                                          takes paint off again (a highlight), same edge options
    {"stroke": NODES, "w": (0.6, 1.4, 0.6), "lift": 0.8}                  the same along a line: a sharp thread of light (the edge of a lapel on a
                                                                          dark, the silver inside a metal rim). A BAND of light is reserved instead:
                                                                          {"name": "edge", "stroke": beside(EDGE, 2.4), "w": 4.2, "soft": 0.9}, and
                                                                          the half-tone kept "out" of "edge"
    {"stroke": NODES, "w": (1, 4, 0.5), "color": "#6E6862"}               a brush stroke, widths spread along it (or at "at")
    {... "dry": 0.6}                                                      a dry brush: bristle streaks that skip on the tooth
    {... "soft": 0.5}                                                     a soft brush line (the ribs of a knit); not with "dry" or "feather"
    {... "feather": 1}                                                    a fold or a crease: hard along the path, dying away over
                                                                          the width "w" to one side. 1: the right hand of someone
                                                                          walking along the path (drawn down the page: the viewer's
                                                                          left; drawn left to right: below), -1: the other side
    {"brush": STROKES, "wash": "#A79386"}                                 a wet session: loaded brush strokes laid beside and over each other while the
                                                                          paint is wet. The way to paint a LARGE AREA (a coat, a cardigan, a skirt).
                                                                          STROKES: node lists, or dicts {"path": NODES, "w": .., "load": .., "press": ..}
                                                                          with a stroke's own values (strokes_along() and hem() make them)
        "w": (6, 22, 16)                 the pressure: widths along each stroke (set down, swell, lift), spread evenly or placed at "at"
        "load": 1.6                      how far the paint lasts, in stroke lengths. 1.6 and more: wet to its round end; about 1: it runs dry at its
                                         end (the bristles break up on the tooth, clump by clump, the sides first); 0.6: from a third of the way
        "dries": 0.35, "fall": 0.2       the share of its length over which a stroke runs out; how much less paint its end gets than its start
        "bristle": 0.12                  the streaks of the bristles in the paint, along the stroke (more as the brush empties)
        "wet": 6                         the strokes run into each other over this distance: their boundaries melt, a sliver of paper between two
                                         wet strokes closes, wet over wet levels out (it does not glaze); the session's OUTER boundary stays one
                                         hard edge with one rim. 0: each stroke dried before the next (they glaze, each keeps its edge and rim)
        "soft": 8, "damp": "name"        the whole session was laid into damp paint (all edges soft), or only where the named area is
        "press" (in a stroke's dict), "vary": 0.12      a stroke's strength, or strengths along it ((1, 1, 0.3): its end dissolves); how much
                                         strength differs from stroke to stroke
        "cut": (25, -35)                 a flat brush set down and lifted askew: the ends are cut at these degrees off square instead of round (one
                                         number: both ends alike; positive: the right-hand corner trails)
        "melt": 0.5, "drag": -0.4        ONE side of the stroke gives way, over this share of its width: "melt": it was laid against damp paint and
                                         thins away to nothing, no edge; "drag": that side of the brush hardly touched and leaves streaks on the
                                         tooth. Positive: the right hand of someone walking along the stroke (as "feather"), negative: the left.
                                         The other side keeps its edge. A DARK is a session of such strokes with "wet" 1-2 (a charged brush: much
                                         pigment, little water: where strokes meet they are one dark, nothing levels out, nothing glazes), laid when
                                         the half-tone is dry and in one pass: the alpha that takes the half-tone straight to the dark (need())
        and, as on a wash: "alpha", "clip", "out", "name", "grade", "fade", "ragged", "rim", "broken", "settle", "pool", "grain", "sediment", "lift"
    {"knit": (A, B), "color": "#A0A98E", "pitch": 8.5, "stitch": 5}       the stitches of a knit, put in with a small brush AFTER the form is painted: grooves
                                                                          down the field between two guide lines (as runs(); or a list of fields), one about
                                                                          every "pitch", each a chain of short marks a "stitch" long that lean to and fro
        "tones": (180, 125), "faint": 0.5, "thin": 0.8      it looks at the paint already there: full strength where the form is as dark as the second
                                         luminance, "faint" (a share of it) where it is as light as the first; "thin": the share of the marks left there
        "w": (0.5, 1.1), "lean": 0.5, "loops": 0.4, "body": 0.25      a mark's width in the light and in the dark; how far the marks lean (0: plain dashes);
                                         the share of stitches with a faint soft tick across (the foot of the loop); the soft side of every groove
        "dry": 0.35, "jit": 1.0, "skip": 0.08      how much the tooth breaks the marks; how unequal distances, lengths and angles are; the share left out
        and "alpha", "clip", "out". Its colour is a glaze, the source's own: `look.py glaze GROUND GROOVE`; "pitch" and "stitch" are read off the
        source at 4x. Grooves stand at unequal distances, wander, thin out and start again: it is a hand's texture, never a ruled pattern
    {"cable": [MID, MID], "width": 34, "cross": 16, "color": "#DCC8B0"}   the plaits of a CABLE knit, after the form like "knit": down every middle line a
                                                                          braid "width" wide with a crossing about every "cross" (both read off the source
                                                                          at 4x): the shadow under each strand, a short wedge leaning in from the cable's
                                                                          side to its middle, left and right in turn, and a broken soft groove along both sides
        "w": (3, 6), "tones": (215, 150), "faint": 0.6      a wedge's width in the light and in the dark; the form's light and shadow under it; its strength in
                                         the light as a share of that in the shadow (a cable shows in the light too: 0.6)
        "sides": 0.5, "jit": 1.0, "skip": 0.06, "dry": 0.3      the side grooves' strength (0: none); how unequal the wedges are (0: a printed
                                         herringbone, the failure); the share left out; how much the tooth breaks them. And "alpha", "clip", "out".
                                         Between the cables the plain knitting is a "knit" layer, kept "out" of a reserved band along each cable
    {"pencil": NODES, "w": 0.9, "p": (0.3, 1, 0.4)}                       a graphite line: pressure along it, grain, small breaks
                                                                          ("color" for a coloured pencil, "broken": 0..1)
    {"part": ("set", "eye_l"), "wash": "#3A2A22", "scale": 1.1}           a reusable face part from parts.py next to the drawings file
                                                                          (also "turn" degrees, "shift" / "at" in head units;
                                                                          "stroke": True / "pencil": True draws it as a line)
    {"head": True, ...}                                                   nodes and sizes on the head's axes: x along the eye line,
                                                                          y down the face, unit = half the eye distance

Painted from the underdrawing (each takes "clip" / "out"; put them in the order a painter works):

    {"study": True, "sizes": (40, 20, 10, 5, 2.5, 1.2)}                   washes, one pass per size (width of a touch in px at 512), big and
                                                                          pale first: every touch lays the palest tone still missing in it,
                                                                          painted round the lights, hard at a step of tone or on one side
        "long": 3, "bands": 0.1          touches run this many widths along the form; a step of tone this big cuts a new one
        "hard": 0.5, "wet": 0.45, "rim": 0.3, "vary": 0.12, "tint": 0.05     how many touches dry with a hard side, how far wet edges run (in
                                                                          touch widths, at most "run" px), strength and colour from touch to touch
        "skip": 0.5                      dark lines thinner than this are left to the pencil
        "over": 0.15, "least": 0.025     how far a touch may go darker than the underdrawing; smaller differences are not painted
        "finish": 0.9                    after the last pass a small brush puts in this share of what is still missing (exact features)
        "pool": 0.1, "grain": 0.1, "wobble": 0.5, "run": 4, "depth": 0.85, "light": 0.03     unevenness and granulation of the touches, how far
                                         the hand strays, the widest a wet edge runs (px), how full the first pass is, the tone left as paper
    {"hatch": True, "length": (8, 26), "density": 1.0}                    dry-brush strokes along the form, where the underdrawing is darker
                                                                          than around it, in the tones found there (hair, cloth)
        "see": 3                         the size (px at 512) at which the form is read: small follows each curl, large the big lie
        "deeper": 1.25                   how much darker than the tones found there (1.3-1.5 grey hair, to 1.9 on a pale source)
        "w": (0.4, 1.4, 0.4), "alpha": 0.6, "dry": 0.45, "vary": 0.6     the strokes themselves, as for any "stroke"
    {"trace": True, "skip": 1.2, "color": "#7A5646"}                      pencil over the thin dark lines of the underdrawing, pressed by their
                                                                          darkness ("over": how dark a line must be, "full": darkness of full pressure;
                                                                          "only": NODES / "drop": NODES keep the lines inside / outside shapes you draw)
        "w": 0.9, "p": (0.5, 1, 1, 0.6), "broken": 0.2, "wobble": 0.15, "shortest": 3     the pencil lines themselves, and the shortest kept

NODES is a list of (x, y) for a point the curve flows through, (x, y, "c") for a corner and (x, y, "w") for a point
where the edge is wet (both tags may be given). "path", "stroke" and "pencil" may also be a list of such lists
(several pieces, one layer; strokes and pencil lines then differ in strength from piece to piece by "vary", 0.25 unless
given, 0 for exact things; or take "press": one strength per piece); pieces listed under "holes" are cut out of a path.
Several layers with the same "name" add up into one mask, and so do a "name" and a mask of the underdrawing.

How the paint behaves (what the options above do not say):
  - A wash multiplies: light = paper x (colour / paper) ^ alpha per channel. Over other paint its colour is a multiplier; the
    same wash twice is colour ^ 2. A lighter or warmer thing cannot be painted over a darker wash: "lift" there first.
  - Edges: a hard edge gets a rim. Near "w" nodes the edge runs soft in a band about 3 x "wet" wide; "soft" and "bleed"
    soften every edge. "clip" / "out" cut hard and leave no rim. "fade" works on any path layer (a cross-fade).
  - What the water does ("miss", "ragged", "dry", "settle", "sediment", "broken", "bloom", "sparkle") is off unless asked for,
    and belongs to a kind of wash rather than to a layer: write it once (POOL = dict(ragged=3, dry=0.5, ...)) and pass it on.
    "miss" and "sparkle" use fields fixed on the sheet (every wash misses the same way, every dry patch is in the same place);
    the others are the layer's own throw.
  - A named layer is remembered with its own edges: a reserved shape with "soft" or "wet" is a soft mask ("out" on it
    keeps paint off gradually). A wash with a "name" is both paint and area. "masks" takes arrays or PNG paths.
  - "wobble" moves an edge by a field fixed on the sheet: two shapes that share an edge and the same "wobble" stay together.
  - Sizes ("w", "wet", "soft", "bleed", "wobble") are grid units. Rim, pooling, bristles and pencil grain are sized against
    the picture ("fine"), the paper's grain too ("weave"). The paper depends on seed, weave, frame and "out": the same four
    give the same paper pixels, another frame height another paper.
  - Sessions of "brush" strokes are washes like any other: a later session glazes the dry earlier one. A glaze alone on bare paper is
    only its cold multiplier colour: clip later sessions to the first one's "name", and strokes that leave the garment (the fingers
    at a hem) are laid in the dark's own mixed colour, read off the source. A stroke's ends are round only as far as it is wet.
  - A stroke's widths "w" are spread evenly along it, or placed at "at": (0, 0.2, 1). A pencil line through a sharp turn
    loops unless the node there is a corner ("c").
  - In a drawings file: `from wash import flow, resample, nodes_of, runs, ribs, ring, arc, ladder, need, toned, step_to, beside,
    scallop, strokes_along, hem`: the curve through nodes, even steps along it, the nodes of a mask (to rough a SILHOUETTE; never a shadow
    shape: those are drawn by hand); marks a painter repeats (`uv run wash.py helpers [NAME …]` prints what every argument means):
    runs(a, b, pitch, seed, lo, hi, skip, jit) the ribs of a knit between two guide lines; ribs(mid, width, gap, seed, lean,
    skip, jit) ribbing across a band; ring(c, r, n, squash) a button; arc(c, rx, ry, a0, a1, n) part of an oval;
    beside(nodes, d) a line moved sideways (a stitch line, a rim's inner line); scallop(nodes, lobe, depth, seed) the outline
    of a wash that dried as a puddle. Strokes for a "brush" layer: strokes_along(guide, spacing, seed, to, within, length, angle, load,
    w, lap, ends, skip) fills a field or a shape you drew with strokes that follow the form; hem(line, n, lengths, angles, seed, w, load,
    back, press, way, reach) the unequal stroke ends a garment stops in (a wet end is a lobe, broader than long: never a drip).
  - A garment's values: ladder(lit, shadow, dark, on, rich, paper) its local colour and glazes from the source's own colours;
    need(glaze, frm, to, paper) the alpha that takes a measured tone to the next; toned(kind, tone, paper, speck) a kind's water
    ("grain", "pool", "settle", "sediment") for the tone a wash arrives at: scaled to the speck MEASURED on the source there
    (`look.py speck`), or, unmeasured, cut back as for smooth cloth; step_to(glaze, frm, to, kind, paper, speck) both at once. `paper` is the sheet's own (hex or RGB) wherever it is not the engine's.
  - From Python: `wash.draw(drawing)` returns the picture (BGR; `only={12, 13}`: those layers alone, the others keep their names
    and lay no paint, which is what `look.py layers` does); or step by step: `Sheet(frame, out, ...)`, `.pin(under,
    masks)`, `.paint(layer)` for each layer, `.finish()`.

    uv run wash.py DRAWINGS.py OUT_DIR [name ...]       # paints DRAWINGS.py's DRAWINGS dict to OUT_DIR/<name>.png
    uv run wash.py nodes MASK.png [scale] [eps]         # prints pen nodes for the white shape(s) in a mask: a starting point
                                                        # (eps: how far, in mask px, the path may cut a bend; smooth the mask first)
    uv run wash.py helpers [NAME ...]                   # the helpers' own manuals: every argument of strokes_along, hem, ribs, toned, …
"""
import importlib.util
import sys
import zlib
from pathlib import Path

import cv2
import numpy as np

OUT = 512        # default output width
SS = 2           # painted at twice the size, then reduced
PAPER = (245, 241, 231)
GRAPHITE = "#5B544F"


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def flow(nodes, closed=True, per=20):
    """The curve through a list of nodes: cubic segments, tangent-continuous at plain nodes, broken at corners."""
    P = np.array([n[:2] for n in nodes], float)
    corner = ["c" in n[2:] for n in nodes]
    n = len(P)
    if n < 3:
        return P
    idx = lambda i: i % n if closed else min(max(i, 0), n - 1)
    def tangent(i, towards):
        a, b, c = P[idx(i - 1)], P[i], P[idx(i + 1)]
        end = not closed and (i == 0 or i == n - 1)
        if corner[i] or end:
            v = (c - b) if (towards > 0 and not (end and i == n - 1)) else (b - a)
        else:
            d0, d1 = np.linalg.norm(b - a) + 1e-9, np.linalg.norm(c - b) + 1e-9
            v = (b - a) / d0 * d1 + (c - b) / d1 * d0             # leans on the shorter neighbour less
        return v / (np.linalg.norm(v) + 1e-9)
    out = []
    for i in range(n if closed else n - 1):
        j = idx(i + 1)
        a, b = P[i], P[j]
        d = np.linalg.norm(b - a)
        c1, c2 = a + tangent(i, +1) * d / 3, b - tangent(j, -1) * d / 3
        t = np.linspace(0, 1, per, endpoint=False)[:, None]
        out.append((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * b)
    if not closed:
        out.append(P[-1:])
    return np.vstack(out)


def noise(rng, h, w, sigma):
    """A smooth random field with unit variance and features about `sigma` px across."""
    s = max(1, int(sigma / 2))
    hh, ww = h // s + 4, w // s + 4
    g = cv2.GaussianBlur(rng.standard_normal((hh, ww)).astype(np.float32), (0, 0), max(sigma / s, 0.5))
    if s > 1:
        g = cv2.resize(g, (ww * s, hh * s), interpolation=cv2.INTER_CUBIC)
    g = g[:h, :w]
    return (g - g.mean()) / (g.std() + 1e-9)


def along(rng, n, sigma):
    """The same in one dimension: a value that drifts along a stroke of n samples."""
    return noise(rng, 1, max(n, 2), sigma)[0][:n]


def resample(pts, step):
    """A polyline at even steps of arc length."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], max(int(s[-1] / step) + 1, 2))
    return np.stack([np.interp(t, s, pts[:, 0]), np.interp(t, s, pts[:, 1])], 1)


def normals(pts):
    d = np.gradient(pts, axis=0)
    return np.stack([-d[:, 1], d[:, 0]], 1) / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)


def taper(img, pts, widths, values):
    """A line whose width and strength (0..1) change from sample to sample, with round ends."""
    for i in range(len(pts) - 1):
        v = int(255 * min(max(min(values[i], values[i + 1]), 0), 1))
        if v == 0:
            continue
        a, b = pts[i], pts[i + 1]
        d = b - a
        nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        quad = np.array([a + nrm * widths[i] / 2, b + nrm * widths[i + 1] / 2, b - nrm * widths[i + 1] / 2, a - nrm * widths[i] / 2])
        cv2.fillConvexPoly(img, np.round(quad * 16).astype(np.int32), v, cv2.LINE_AA, 4)
        cv2.circle(img, (int(a[0] * 16), int(a[1] * 16)), int(max(widths[i], 0.5) * 8), v, -1, cv2.LINE_AA, 4)


def step(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def thin(m):
    """A mask of lines reduced to lines one pixel wide (Zhang-Suen)."""
    m = m.astype(np.uint8)
    while True:
        changed = False
        for it in (0, 1):
            P = np.pad(m, 1)
            n = [P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:], P[2:, 2:], P[2:, 1:-1], P[2:, :-2], P[1:-1, :-2], P[:-2, :-2]]
            B = sum(n)
            A = sum((n[i] == 0) & (n[(i + 1) % 8] == 1) for i in range(8))
            c = (n[0] * n[2] * n[4] == 0) & (n[2] * n[4] * n[6] == 0) if it == 0 else (n[0] * n[2] * n[6] == 0) & (n[0] * n[4] * n[6] == 0)
            kill = (m == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if kill.any():
                m[kill], changed = 0, True
        if not changed:
            return m


def chains(skel, shortest=4):
    """One-pixel lines as lists of (x, y), each followed from an end, going straight on where lines cross."""
    pts = set(zip(*np.nonzero(skel)))
    near = lambda p: [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (p[0] + dy, p[1] + dx) in pts]
    order = sorted(pts, key=lambda p: (len(near(p)) != 1, p))
    done, out = set(), []
    for start in order:
        if start in done:
            continue
        chain = [start]
        done.add(start)
        while True:
            nxt = [q for q in near(chain[-1]) if q not in done]
            if not nxt:
                break
            if len(chain) > 3:
                d = (chain[-1][0] - chain[-4][0], chain[-1][1] - chain[-4][1])
                nxt.sort(key=lambda q: -((q[0] - chain[-1][0]) * d[0] + (q[1] - chain[-1][1]) * d[1]))
            chain.append(nxt[0])
            done.add(nxt[0])
        if len(chain) >= shortest:
            out.append(np.array([(x, y) for y, x in chain], float))
    return out


class Sheet:
    """The sheet being painted: grid points go in, paint lands on a canvas twice the final size."""

    def __init__(self, frame, out=OUT, paper=PAPER, seed=1, parts=None, weave=1.0, fine=1.0):
        x0, y0, *wh = frame
        fw, fh = (wh[0], wh[0]) if len(wh) == 1 else wh
        self.W, self.H = int(out), int(round(out * fh / fw))
        self.k = self.W * SS / fw                                 # grid unit -> canvas pixel
        self.o = np.array([x0, y0], float)
        self.nw, self.nh = self.W * SS, self.H * SS
        self.px = self.nw / 512                                   # textures are sized against the picture, not the grid
        self.paper = np.array(paper, np.float32)
        self.seed = seed
        self.T = np.ones((self.nh, self.nw, 3), np.float32)       # what the paint lets through, per channel
        rng = np.random.default_rng(seed)
        f = lambda s: noise(rng, self.nh, self.nw, s * self.px)
        z = 0.5 * f(0.7 * weave) + 0.4 * f(1.6 * weave) + 0.35 * f(4.0 * weave)
        self.weave = weave
        self.tooth = 0.5 + 0.5 * np.tanh(z / z.std() * 0.9)       # paper height: 0 valley .. 1 peak
        self.cloud = f(14)                                        # slow unevenness of the sheet
        self.hand = np.stack([f(5), f(5)], -1)                    # where the hand strays from a path
        self.run = np.stack([f(11), f(11)], -1)                   # where wet paint wanders
        self.drift = np.stack([f(40), f(40)], -1)                 # where a wash misses the drawing: slow, the same for every wash
        self.damp = f(22)                                         # where the brush ran dry (the same places for every wash)
        pits = (0.6 * f(0.6 * weave) + 0.4 * f(1.3 * weave)) * (1 + 0.35 * f(3.5 * weave))
        self.pits = step(pits / pits.std(), -0.4, 1.8)             # the small pits of the paper, where heavy pigment comes to rest
        self.masks = {}
        self.watch = None                                         # a list: every "brush" session's (layer, coverage, kept area) is put in it (look.py holes)
        self.parts = parts
        self.eyes = None
        self.grainpx = self.px                                    # the paper keeps its size; the brush's marks may be finer
        self.px *= fine

    def to(self, pts):
        return (np.asarray(pts, float) - self.o) * self.k

    # ---- the head's own axes

    def axes(self):
        el, er = (np.array(v, float) for v in self.eyes)
        c, d = (el + er) / 2, er - el
        u = np.linalg.norm(d) / 2
        return c, u, d / (2 * u), np.array([-d[1], d[0]]) / (2 * u)

    def part(self, layer):
        """A face part from parts.py set on this head: same place on the head's axes, then scaled about its own
        middle, turned and nudged (in units of half the eye distance). Returns nodes in head units."""
        src, name = layer["part"]
        nodes = self.parts[src][name]["nodes"]
        P = np.array([n[:2] for n in nodes], float)
        mid = P.mean(0)
        s = layer.get("scale", 1)
        sx, sy = (s, s) if np.isscalar(s) else s
        r = np.radians(layer.get("turn", 0))
        Q = (P - mid) * (sx, sy)
        Q = Q @ np.array([[np.cos(r), np.sin(r)], [-np.sin(r), np.cos(r)]]) + mid + np.array(layer.get("shift", (0, 0)))
        if layer.get("at"):
            Q = Q - mid + np.array(layer["at"])
        return [(q[0], q[1]) + tuple(n[2:]) for q, n in zip(Q, nodes)]

    def place(self, layer):
        """Parts and head-unit layers -> a plain layer on the grid."""
        if "part" in layer:
            key = next((k for k in ("stroke", "pencil") if k in layer and layer[k] is True), "path")
            layer = dict(layer, head=True, **{key: self.part(layer)})
        if not layer.get("head"):
            return layer
        c, u, ax, ay = self.axes()
        on = lambda nodes: [tuple(c + u * (p[0] * ax + p[1] * ay)) + tuple(p[2:]) for p in nodes]
        each = lambda v: [on(piece) for piece in v] if isinstance(v[0], list) else on(v)
        layer = dict(layer)
        for key in ("path", "stroke", "pencil", "holes"):
            if key in layer:
                layer[key] = each(layer[key]) if key != "holes" else [on(p) for p in layer[key]]
        for key in ("w", "soft", "wet", "bleed", "wobble"):
            if key in layer:
                v = layer[key]
                layer[key] = v * u if np.isscalar(v) else tuple(x * u for x in v)
        if "fade" in layer:
            layer["fade"] = tuple(tuple(c + u * (p[0] * ax + p[1] * ay)) for p in layer["fade"])
        return layer

    # ---- coverage of a layer, inside its own box

    def box(self, pts, pad):
        lo, hi = np.floor(pts.min(0) - pad).astype(int), np.ceil(pts.max(0) + pad).astype(int)
        x0, y0, x1, y1 = max(lo[0], 0), max(lo[1], 0), min(hi[0], self.nw), min(hi[1], self.nh)
        return (slice(y0, y1), slice(x0, x1)) if x1 > x0 and y1 > y0 else None

    def warp(self, m, f, amp):
        h, w = m.shape
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)            # the box ends in empty margin, or at the frame: there the shape goes on
        return cv2.remap(m, xx + f[..., 0] * np.float32(amp), yy + f[..., 1] * np.float32(amp), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    def shape(self, layer, rng):
        """A wash: the filled path, its edges made hard, wet or wandering, and the marks drying paint leaves."""
        pieces = layer["path"] if isinstance(layer["path"][0], list) else [layer["path"]]
        k = self.k
        wet, soft, bleed = layer.get("wet", 5) * k, layer.get("soft", 0) * k, layer.get("bleed", 0) * k
        wobble, miss, ragged = layer.get("wobble", 0.35) * k, layer.get("miss", 0) * k, layer.get("ragged", 0) * k
        curves = [self.to(flow(p)) for p in pieces]
        has_wet = any("w" in n[2:] for p in pieces for n in p)
        box = self.box(np.vstack(curves), 3 * (soft + bleed + (wet if has_wet else 0) + miss + ragged) + wobble + 6)
        if box is None:
            return None, None, None
        o = np.array([box[1].start, box[0].start], float)
        m = np.zeros((box[0].stop - box[0].start, box[1].stop - box[1].start), np.uint8)
        for c in curves:
            cv2.fillPoly(m, [np.round((c - o) * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
        for hole in layer.get("holes", ()):
            cv2.fillPoly(m, [np.round((self.to(flow(hole)) - o) * 16).astype(np.int32)], 0, cv2.LINE_AA, 4)
        m = m.astype(np.float32) / 255
        if wobble:
            m = self.warp(m, self.hand[box], wobble)
        if miss:                                                  # the wash strays from the drawing: short of it here, over it there
            m = self.warp(m, self.drift[box], miss)
        lobes = lambda size: noise(rng, m.shape[0], m.shape[1], size) + 0.4 * noise(rng, m.shape[0], m.shape[1], size / 3)
        # with "ragged" the paper is unevenly damp: stretches of a wet edge dry hard after all (0), others run (1)
        damp = step(lobes(max(1.6 * max(wet, soft, bleed), 8 * self.px)), -0.8, 0.0) if ragged else 1.0
        hard = np.ones_like(m)                                    # 1 where the edge dried hard: only there a rim forms
        if bleed:
            run = cv2.GaussianBlur(self.warp(m, self.run[box], bleed), (0, 0), bleed * 0.45)
            m, hard = m * (1 - damp) + run * damp, hard * (1 - damp)
        if soft:
            m, hard = m * (1 - damp) + cv2.GaussianBlur(m, (0, 0), soft) * damp, hard * (1 - damp)
        if has_wet:                                               # only the stretch of edge near a wet node runs
            wmap = np.zeros(m.shape, np.uint8)
            for piece, c in zip(pieces, curves):
                per = len(c) // len(piece)
                wn = np.array([1.0 if "w" in n[2:] else 0.0 for n in piece])
                wv = np.interp(np.arange(len(c)) / per, np.arange(len(piece) + 1), np.append(wn, wn[0]))
                for i in range(len(c)):
                    if wv[i] > 0:
                        a, b = c[i] - o, c[(i + 1) % len(c)] - o
                        cv2.line(wmap, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), int(255 * wv[i]), max(int(wet * 3), 1))
            wmap = np.clip(cv2.GaussianBlur(wmap.astype(np.float32) / 255, (0, 0), wet * 0.7) * 1.25, 0, 1) * damp
            m = m * (1 - wmap) + cv2.GaussianBlur(m, (0, 0), wet) * wmap
            hard *= 1 - wmap
        if ragged:                                                # the edge crawls in lobes of two sizes, hard and wet stretches alike
            crawl = np.stack([lobes(max(5 * ragged, 6 * self.px)), lobes(max(5 * ragged, 6 * self.px))], -1)
            m, hard = self.warp(m, crawl, ragged), self.warp(hard, crawl, ragged)
        px, dry = self.px, layer.get("dry", 0)
        if dry:                                                   # a brush not fully loaded: along its edges the wash catches the valleys
            mb = cv2.GaussianBlur(m, (0, 0), 1.5 * dry * px)      # of the paper and misses the peaks, so a hard edge crumbles and a wet
            m = np.clip(mb + 10.8 * dry * mb * (1 - mb) ** 2 * (0.5 - self.tooth[box]), 0, 1)          # one breaks up at its thin end
        m = self.thinned(m, layer, box)
        return m, self.dried(m, hard, layer, rng, lobes, box), box

    def thinned(self, m, layer, box):
        """A wash loaded more here and less there: "fade" and "grade"."""
        o = np.array([box[1].start, box[0].start], float)
        if layer.get("fade"):                                     # thinned with water along the way: no edge of its own
            p, q = (self.to(v) - o for v in layer["fade"])
            yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]].astype(np.float32)
            t = ((xx - p[0]) * (q[0] - p[0]) + (yy - p[1]) * (q[1] - p[1])) / (np.sum((q - p) ** 2) + 1e-9)
            m = m * (1 - step(t, 0, 1))
        if layer.get("grade"):                                    # one wet wash, loaded more here and less there: its strength at a few
            G = [(self.to(q) - o, float(v)) for q, v in layer["grade"]]            # points, flowing from one to the next with no edge
            far = np.mean([np.linalg.norm(a - b) for a, _ in G for b, _ in G if a is not b]) if len(G) > 1 else 0.0
            yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]].astype(np.float32)
            xx, yy = xx + self.run[box][..., 0] * np.float32(0.1 * far), yy + self.run[box][..., 1] * np.float32(0.1 * far)   # the front wanders
            near = [1 / ((xx - q[0]) ** 2 + (yy - q[1]) ** 2 + 1.0) for q, _ in G]
            m = m * sum(n * v for n, (_, v) in zip(near, G)) / sum(near)
        return m

    def dried(self, m, hard, layer, rng, lobes, box):
        """How much pigment lies on a coverage `m` once it has dried: a rim along the edges that dried hard (`hard`: 1
        there), paint gathered inside the edges, unevenness, granulation, sediment. `lobes(size)` is the layer's own noise."""
        rim, px, d = layer.get("rim", 0.25), self.px, m           # m stays the clean coverage; d is how much pigment lies there
        if rim and hard.any():
            line = m * (1 - cv2.GaussianBlur(m, (0, 0), 1.3 * px)) * 2 * hard
            if layer.get("broken"):                               # a dried edge that comes and goes along its length
                at = -1.3 + 2.2 * layer["broken"]
                line = line * step(lobes(10 * px), at - 0.35, at + 0.35) * (1 + layer["broken"])
            d = d + rim * line
        pool, grain, settle = layer.get("pool", 0.08), layer.get("grain", 0.1), layer.get("settle", 0)
        if settle:                                                # drying paint gathers: in a broad band inside the edges (here more,
            inner = m * (1 - cv2.GaussianBlur(m, (0, 0), 5 * px)) * 2           # there none) and in a few big pools with a visible front
            d = d * (1 + settle * (1.6 * inner * step(lobes(18 * px), -1.0, 1.0) + 0.5 * np.tanh(1.6 * lobes(28 * px))))
        if pool:
            d = d * (1 + pool * noise(rng, m.shape[0], m.shape[1], 9 * self.px))
        if grain:
            d = d * (1 + grain * (1 - 2 * self.tooth[box]))
        if layer.get("sediment"):                                 # a pigment that granulates: fine dark specks in the pits
            d = d * (1 + layer["sediment"] * (2.2 * self.pits[box] - 0.75))
        return np.clip(d, 0, None)

    def lines(self, layer, rng):
        """Brush strokes or pencil lines: one coverage map for all the pieces of the layer."""
        pencil = "pencil" in layer
        pieces = layer["pencil" if pencil else "stroke"]
        pieces = pieces if isinstance(pieces[0], list) else [pieces]
        k, px = self.k, self.px
        w = layer.get("w", 0.9 if pencil else 3)
        w = np.array([w] if np.isscalar(w) else w, float) * k
        dry, vary = layer.get("dry", 0), layer.get("vary", 0.25 if len(pieces) > 1 else 0)
        curves = [resample(self.to(flow(p, closed=False)), 2.0) for p in pieces]
        box = self.box(np.vstack(curves), w.max() + 6)
        if box is None:
            return None, None, None
        o = np.array([box[1].start, box[0].start], float)
        m = np.zeros((box[0].stop - box[0].start, box[1].stop - box[1].start), np.uint8)
        feather = layer.get("feather", 0)
        near, far = np.full(m.shape, 255, np.uint8), np.full(m.shape, 255, np.uint8)
        for i, c in enumerate(curves):
            n = len(c)
            t = np.linspace(0, 1, n)
            width = np.interp(t, layer.get("at", np.linspace(0, 1, len(w))), w)
            strength = (1 + vary * rng.uniform(-1, 1)) * (layer["press"][i] if "press" in layer else 1)
            c = c - o
            if feather:                                           # a band beside the path; its two edges are kept for the falloff
                other = c + normals(c) * (width * feather)[:, None]
                cv2.fillPoly(m, [np.round(np.vstack([c, other[::-1]]) * 16).astype(np.int32)], int(255 * min(strength, 1.0)), cv2.LINE_AA, 4)
                cv2.polylines(near, [np.round(c).astype(np.int32)], False, 0)
                cv2.polylines(far, [np.round(other).astype(np.int32)], False, 0)
            elif pencil:
                p = layer.get("p", (0.45, 1, 0.5))
                p = np.interp(t, np.linspace(0, 1, len(p)), p) if not np.isscalar(p) else np.full(n, p)
                g = along(rng, n, 9 * px)
                p = p * np.clip(1 + 0.4 * along(rng, n, 5 * px), 0.2, 1.4) * strength
                p = p * step(g, -2.1 + 1.6 * layer.get("broken", 0.3) - 0.25, -2.1 + 1.6 * layer.get("broken", 0.3) + 0.25)
                c = c + normals(c) * (along(rng, n, 12 * px) * layer.get("wobble", 0.3) * k)[:, None]
                taper(m, c, width * (0.6 + 0.4 * np.clip(p, 0, 1)), p)
            elif dry:                                             # each bristle leaves its own streak, with gaps
                nb = max(3, int(width.max() / (1.4 * px)))
                nrm = normals(c)
                for f in (np.arange(nb) + rng.uniform(0.2, 0.8, nb)) / nb - 0.5:
                    v = rng.uniform(0.35, 1.0) * strength * step(along(rng, n, 8 * px), -1.4 + 1.9 * dry - 0.3, -1.4 + 1.9 * dry + 0.3)
                    v = v * np.clip(width / (1.2 * px), 0, 1)     # a bristle fades out where the stroke thins to a point
                    taper(m, c + nrm * (width * f)[:, None], np.maximum(width / nb * 1.5, 1.0 * px), v)
            else:
                taper(m, c, width, np.full(n, min(strength, 1.0)))
        m = m.astype(np.float32) / 255
        if feather:                                               # hard on the path, dying away towards the other edge
            d1, d2 = cv2.distanceTransform(near, cv2.DIST_L2, 3), cv2.distanceTransform(far, cv2.DIST_L2, 3)
            m = m * (1 - step(d1 / (d1 + d2 + 1e-6), 0, 1))
        if pencil:
            d = m * (0.4 + 0.8 * step(self.tooth[box], 0.15, 0.75))                 # graphite sits on the peaks
        elif dry:
            d = m * step(self.tooth[box], 0.6 * dry - 0.25, 0.6 * dry + 0.25)       # a dry brush skips the valleys
        else:
            if layer.get("soft"):
                m = cv2.GaussianBlur(m, (0, 0), layer["soft"] * k)
            d = m * (1 + layer.get("grain", 0.1) * (1 - 2 * self.tooth[box]))
        return m, d, box

    def brush(self, layer, rng):
        """A wet session: brush strokes laid beside and over each other while the paint is wet. Each stroke is a brush's
        footprint dragged along its path: as wide as it is pressed ("w"), leaving less paint the further it goes ("fall")
        and, when its load runs out ("load", "dries"), breaking up bristle by bristle on the tooth of the paper. Inside the
        session the wet paint of one stroke runs into the next over "wet"; the session's outer boundary is one edge."""
        k, px = self.k, self.px
        S = [s if isinstance(s, dict) else {"path": s} for s in layer["brush"]]
        opt = lambda s, key, default: s.get(key, layer.get(key, default))
        wet, soft, ragged = layer.get("wet", 6) * k, layer.get("soft", 0) * k, layer.get("ragged", 0) * k
        rim, vary = layer.get("rim", 0.25), layer.get("vary", 0.12)
        blur = lambda a, sigma: cv2.GaussianBlur(a, (0, 0), max(sigma, 0.3))
        sway = lambda n, knots: blur(np.interp(np.linspace(0, knots - 1, n), np.arange(knots), rng.standard_normal(knots)).astype(np.float32)[None], n / knots / 2)[0]
        laid = []
        for s in S:                                               # the hand: pressure and path drift a little along every stroke
            c = resample(self.to(flow(s["path"], closed=False)), 0.5)
            n = len(c)
            w = np.atleast_1d(np.asarray(opt(s, "w", 12), float)) * k
            width = np.interp(np.linspace(0, 1, n), opt(s, "at", np.linspace(0, 1, len(w))), w) * (1 + 0.07 * sway(n, 5))
            laid.append((s, c + normals(c) * (sway(n, 4) * opt(s, "wobble", 0.5) * k)[:, None], width))
        box = self.box(np.vstack([c for _, c, _ in laid]), max(w.max() for *_, w in laid) / 2 + 3 * (wet + soft + ragged) + 6)
        if box is None:
            return None, None, None
        by, bx = box[0].start, box[1].start
        size = (box[0].stop - by, box[1].stop - bx)
        A, dryp, U, cover, sn, sd = (np.zeros(size, np.float32) for _ in range(6))   # wet pigment, dry pigment, wet area, all area, streaks
        for s, c, width in laid:
            sb = self.box(c, width.max() / 2 + 3)
            if sb is None:
                continue
            o = np.array([sb[1].start, sb[0].start], float)
            h_, w_ = sb[0].stop - sb[0].start, sb[1].stop - sb[1].start
            q = np.round(c - o).astype(int)
            ok = (q[:, 0] >= 0) & (q[:, 0] < w_) & (q[:, 1] >= 0) & (q[:, 1] < h_)
            if not ok.any():
                continue
            src = np.ones((h_, w_), np.uint8)                     # every pixel finds the nearest point of the stroke's middle line: how far
            src[q[ok, 1], q[ok, 0]] = 0                           # along the stroke it is (i), and how far across (side)
            _, lab = cv2.distanceTransformWithLabels(src, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
            lut = np.zeros(int(lab.max()) + 1, np.int32)
            lut[lab[q[ok, 1], q[ok, 0]]] = np.nonzero(ok)[0]
            i = lut[lab]
            yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
            nrm = normals(c).astype(np.float32)
            dx, dy = xx + np.float32(o[0]) - c[i, 0].astype(np.float32), yy + np.float32(o[1]) - c[i, 1].astype(np.float32)
            side, on = dx * nrm[i, 0] + dy * nrm[i, 1], dx * nrm[i, 1] - dy * nrm[i, 0]                 # across the stroke, and along it
            dist = np.hypot(side, on)                             # to the nearest point itself, not to its pixel: no staircase along the edge
            half = np.maximum(width[i] / 2, 0.3).astype(np.float32)
            v = np.clip(side / half, -1, 1)                       # -1 .. 1 across the brush
            t = (i / max(len(c) - 1, 1)).astype(np.float32)        # 0 .. 1 along the stroke
            # the bristles: each leaves its own streak (fine), and they hold together in a few clumps (coarse)
            nb, ns = max(4, int(width.max() / (3 * px))), max(4, int(len(c) / (10 * px)))
            fine = cv2.GaussianBlur(rng.standard_normal((nb, ns)).astype(np.float32), (0, 0), sigmaX=6, sigmaY=0.6)
            coarse = cv2.resize(cv2.GaussianBlur(rng.standard_normal((max(nb // 5, 2) + 2, ns)).astype(np.float32), (0, 0), sigmaX=9, sigmaY=0.5), (ns, nb), interpolation=cv2.INTER_CUBIC)
            streak = 0.7 * fine / (fine.std() + 1e-6) + 0.7 * coarse / (coarse.std() + 1e-6)
            f = cv2.remap(streak, t * (ns - 1), (v * 0.5 + 0.5) * (nb - 1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            half = half * (1 + 0.05 * f * (np.abs(v) > 0.6))       # the brush's edge is its outer bristles, never a ruled line
            cov = 1 - step(dist, half - 0.8, half + 0.8)
            cut = opt(s, "cut", None)
            if cut is not None:                                   # a flat brush set down and lifted askew: the ends are cut, not round
                u, far = i * np.float32(0.5) + on, (len(c) - 1) * 0.5                 # how far along the stroke, also beyond its ends
                g0, g1 = (np.float32(np.tan(np.radians(a))) for a in ((cut, cut) if np.isscalar(cut) else cut))
                cov = cov * step(u - (abs(g0) * half + g0 * side) - 1.5 * f, -0.8, 0.8) * (1 - step(u - (far - abs(g1) * half + g1 * side) - 1.5 * f, -0.8, 0.8))
            # the load: the middle of the brush holds more paint than its sides, each clump runs out in its own place, and
            # over the last "dries" of its way a bristle skips more and more of the paper's valleys
            load, dries, fall = opt(s, "load", 1.6), max(opt(s, "dries", 0.35), 1e-3), opt(s, "fall", 0.2)
            clump = blur(rng.standard_normal((1, 48)).astype(np.float32), 5)[0]
            end = load * (1 - 0.15 * v * v + 0.12 * (clump / (clump.std() + 1e-6))[((v * 0.5 + 0.5) * 47).astype(np.int32)])
            out = np.clip((t - end) / dries + 0.5, 0, 1)           # 0: wet paint .. 1: nothing left (half gone at `end`)
            melt, drag, press = opt(s, "melt", 0), opt(s, "drag", 0), opt(s, "press", 1.0)
            if drag:                                              # one side of the brush hardly touched the paper: there it leaves
                out = np.maximum(out, 0.95 * np.clip((v * np.sign(drag) - (1 - 2 * abs(drag))) / (2 * abs(drag)) + 0.1 * f, 0, 1))    # streaks on the tooth
            at = -2.6 + 5.2 * out
            hold = np.where(out <= 0, 1.0, step(1.1 * f + 1.4 * (self.tooth[sb] - 0.5), at - 0.35, at + 0.35)) * (out < 1)
            press = press if np.isscalar(press) else np.interp(t, np.linspace(0, 1, len(press)), press).astype(np.float32)
            d = cov * hold * (1 + fall * (0.5 - t)) * press * (1 + vary * rng.uniform(-1, 1))
            if melt:                                              # one side was laid into water: the paint thins away to it, no edge
                d = d * (1 - step(v * np.sign(melt) + 0.1 * f * (1 - v * v), 1 - 2 * abs(melt), 1.0))
            wetness = 1 - step(out, 0.05, 0.5)
            sl = (slice(sb[0].start - by, sb[0].stop - by), slice(sb[1].start - bx, sb[1].stop - bx))
            if wet:
                A[sl] = np.maximum(A[sl], d * wetness)         # wet paint over wet paint levels out: it does not glaze
                dryp[sl] = np.maximum(dryp[sl], d * (1 - wetness))
                U[sl] = np.maximum(U[sl], cov * hold * wetness)
            else:                                                 # each stroke dried before the next: its own rim, and they glaze
                A[sl] += d * (1 + rim * 2 * (1 - blur(cov * hold, 1.3 * px)))
            cover[sl] = np.maximum(cover[sl], cov * hold)
            sn[sl] += d * f * opt(s, "bristle", 0.12) * (0.35 + 0.65 * np.clip(t / max(load, 0.3), 0, 1))
            sd[sl] += d
        lobes = lambda size_: noise(rng, size[0], size[1], size_) + 0.4 * noise(rng, size[0], size[1], size_ / 3)
        if wet:                                                   # wet paint levels out, but only as far as the wet reaches: nothing runs
            r = int(0.35 * wet)                                   # over the session's own edge; and a sliver of paper between two wet
            shut = cv2.morphologyEx(U, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) if r else U    # strokes closes
            A, U = blur(A, 0.5 * wet) / (blur(U, 0.5 * wet) + 1e-3) * shut, shut
            cover = np.maximum(cover, U)
            A = np.maximum(A, dryp)
        else:
            U = cover
        A = self.thinned(A * (1 + sn / (sd + 1e-3)), layer, box)  # the streaks of the bristles stay in the paint
        if ragged:                                                # unevenly damp paper: the session's edge crawls
            crawl = np.stack([lobes(max(5 * ragged, 6 * px)), lobes(max(5 * ragged, 6 * px))], -1)
            A, U, cover = (self.warp(a, crawl, ragged) for a in (A, U, cover))
        hard = np.ones_like(A)
        if soft:                                                  # laid into damp paint: everywhere, or where the named area is
            damp = self.masks[layer["damp"]][box] if layer.get("damp") else np.ones_like(A)
            A, cover, hard = A * (1 - damp) + blur(A, soft) * damp, cover * (1 - damp) + blur(cover, soft) * damp, 1 - damp
        gain = self.dried(U, hard, dict(layer, rim=rim if wet else 0), rng, lobes, box) / (U + 1e-3)
        return np.clip(cover, 0, 1), np.clip(A * np.where(U > 0.02, gain, 1.0), 0, None), box

    def knit(self, layer, rng):
        """The stitches of a knit, put in with a small brush AFTER the form is painted: grooves between two guide lines (a field,
        as for runs()), about one every "pitch", each a chain of short marks one "stitch" long that lean to and fro, now and
        then with the second leg of a V or a faint tick across (the foot of a loop). The painter looks at the form while doing
        it: where the paint under them is dark ("tones": the form's light and its shadow, as luminances) the marks are full and
        wide; towards the light they get thin and faint ("faint") and break off more often ("thin"). Grooves stand at unequal
        distances, wander, thin out and start again; every mark skips on the tooth."""
        k, px = self.k, self.px
        fields = layer["knit"] if not np.isscalar(layer["knit"][0][0][0]) else [layer["knit"]]
        pitch = layer.get("pitch", 9.0) * k
        stitch = layer.get("stitch", 0.7 * layer.get("pitch", 9.0)) * k
        lean, jit, faint, skip = layer.get("lean", 0.5), layer.get("jit", 1.0), layer.get("faint", 0.2), layer.get("skip", 0.08)
        thin, loops = layer.get("thin", 0.8), layer.get("loops", 0.4)
        w0, w1 = (v * k for v in layer.get("w", (0.6, 1.2)))
        light, dark = layer.get("tones", (170, 80))
        cols = []
        for a, b in fields:
            A, B = (resample(self.to(_even(g, 64)), 2.0) for g in (a, b))
            n_ = min(len(A), len(B))
            A, B = (g[np.round(np.linspace(0, len(g) - 1, n_)).astype(int)] for g in (A, B))
            n = max(int(round(np.linalg.norm(A - B, axis=1).mean() / pitch)), 1)
            tau, at = [], rng.uniform(0.2, 0.8)
            while at < n:                                         # unequal distances between neighbours: a hand, not a ruler
                tau.append(at / n)
                at += rng.uniform(1 - 0.28 * jit, 1 + 0.28 * jit)
            cols += [A * (1 - t) + B * t for t in tau]
        if not cols:
            return None, None, None
        box = self.box(np.vstack(cols), pitch + 6)
        if box is None:
            return None, None, None
        o = np.array([box[1].start, box[0].start], float)
        h_, w_ = box[0].stop - box[0].start, box[1].stop - box[1].start
        tone = cv2.GaussianBlur((self.T[box] * self.paper) @ np.array([0.3, 0.59, 0.11], np.float32), (0, 0), 0.8 * pitch)
        shade = np.clip((light - tone) / max(light - dark, 1.0), 0, 1)             # 0 in the form's light .. 1 in its shadow
        hand = 1 + 0.3 * noise(rng, h_, w_, 4 * pitch)             # the hand presses more here, less there
        m, rungs = np.zeros((h_, w_), np.uint8), np.zeros((h_, w_), np.uint8)
        for c in cols:
            c = resample(c, 1.0) - o
            n = len(c)
            if n < 2 * stitch:
                continue
            c = c + normals(c) * (along(rng, n, 5 * stitch) * 0.2 * pitch * jit)[:, None]        # a column wanders a little
            nrm = normals(c)
            here = 0.5 * (1 + np.tanh(0.9 * along(rng, n, 1.5 * stitch)))             # 0..1: where it is low the groove is there, where high it breaks off
            at, zig, firm = rng.uniform(0, stitch), rng.choice((-1.0, 1.0)), rng.uniform(0.7, 1.1)      # one groove is fainter than the next
            while at < n - 2:
                run = stitch * rng.uniform(1 - 0.45 * jit, 1 + 0.7 * jit)
                i0, i1 = int(at), min(int(at + run), n - 1)
                at += run + stitch * rng.uniform(-0.15, 0.2) * jit
                zig = -zig if rng.uniform() < 0.7 else zig
                im = (i0 + i1) // 2
                x, y = int(c[im, 0]), int(c[im, 1])
                if i1 - i0 < 2 or not (0 <= x < w_ and 0 <= y < h_):
                    continue
                sh = float(shade[y, x])
                there = np.clip((thin + (1 - thin) * sh - here[im]) / 0.12, 0, 1)           # it thins out before a gap, it is not cut
                if there <= 0 or rng.uniform() < skip:
                    continue
                v = min((faint + (1 - faint) * sh) * float(hand[y, x]) * firm * rng.uniform(0.7, 1.15) * there, 1.0)
                wd = (w0 + (w1 - w0) * sh) * rng.uniform(0.8, 1.2)
                off = zig * lean * 0.16 * pitch * (rng.uniform(0.3, 1.4) if rng.uniform() > 0.25 * jit else 0.0)      # now and then a straight one
                p0, p1, p2 = c[i0] + nrm[i0] * (off + rng.normal(0, 0.03 * pitch * jit)), c[im] + nrm[im] * rng.normal(0, 0.04 * pitch * jit), c[i1] - nrm[i1] * off
                taper(m, np.array([p0, p1, p2]), (0.7 * wd, wd, 0.55 * wd), (v, v, v))
                if rng.uniform() < 0.25 * lean:                   # the other leg of the V, into the stitch beside it: short, now and then
                    q = c[i0 + (i1 - i0) // 2] - nrm[i0] * (off + zig * rng.uniform(0.15, 0.3) * pitch)
                    taper(m, np.array([p2, q]), (0.55 * wd, 0.35 * wd), (0.6 * v, 0.45 * v))
                if rng.uniform() < loops:                         # the foot of a loop: a faint, soft, sagging tick across the stitch beside the groove
                    side, sag = rng.choice((-1.0, 1.0)), c[i1] - c[im]
                    q0, q2 = p2 + nrm[i1] * side * rng.uniform(0.05, 0.25) * pitch, p2 + nrm[i1] * side * rng.uniform(0.55, 1.0) * pitch + sag * rng.uniform(-0.4, 0.4)
                    taper(rungs, np.array([q0, (q0 + q2) / 2 + sag * rng.uniform(0.1, 0.45), q2]), (wd, 1.2 * wd, 0.8 * wd), (0.35 * v, 0.3 * v, 0.2 * v))
        m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 0.45 * px)
        body, dry = layer.get("body", 0.25), layer.get("dry", 0.35)
        if body:                                                  # each groove has a soft side: the stitch beside it turning away
            sg = 0.2 * pitch
            m = m + body * np.clip(cv2.GaussianBlur(m, (0, 0), sg) * 2.5 * sg / max(0.5 * (w0 + w1), 1.0), 0, 1) * (0.4 + 0.6 * shade)
        m = m + cv2.GaussianBlur(rungs.astype(np.float32) / 255, (0, 0), 0.9 * px)
        d = m * (1 - 0.8 * dry + 0.8 * dry * step(self.tooth[box], 0.6 * dry - 0.25, 0.6 * dry + 0.25) * 1.6)
        return np.clip(m, 0, 1), d, box

    def cable(self, layer, rng):
        """The plaits of a cable knit, put in AFTER the form like "knit": down every middle line a braid "width" wide, a crossing
        about every "cross": the shadow under each strand as it goes under the next, a short wedge that leans in from the cable's
        side to its middle, left and right in turn, half a crossing apart (a wheat ear, never a printed herringbone: every wedge
        has its own length, lean, width and strength, some are left out, the column wanders); along both sides the groove that
        sets the cable off from the plain knitting, a broken soft line. Like "knit" it looks at the paint under it ("tones")."""
        k, px = self.k, self.px
        mids = layer["cable"] if not np.isscalar(layer["cable"][0][0]) else [layer["cable"]]
        width, cross = layer.get("width", 34.0) * k, layer.get("cross", 16.0) * k
        jit, faint, skip, sides = layer.get("jit", 1.0), layer.get("faint", 0.6), layer.get("skip", 0.06), layer.get("sides", 0.5)
        w0, w1 = (v * k for v in layer.get("w", (3.0, 6.0)))
        light, dark = layer.get("tones", (215, 150))
        cols = [resample(self.to(flow(c, closed=False)), 1.0) for c in mids]
        box = self.box(np.vstack(cols), width + 6)
        if box is None:
            return None, None, None
        o = np.array([box[1].start, box[0].start], float)
        h_, w_ = box[0].stop - box[0].start, box[1].stop - box[1].start
        tone = cv2.GaussianBlur((self.T[box] * self.paper) @ np.array([0.3, 0.59, 0.11], np.float32), (0, 0), 0.5 * cross)
        shade = np.clip((light - tone) / max(light - dark, 1.0), 0, 1)             # 0 in the form's light .. 1 in its shadow
        hand = 1 + 0.3 * noise(rng, h_, w_, 4 * cross)
        m, soft = np.zeros((h_, w_), np.uint8), np.zeros((h_, w_), np.uint8)
        for c in cols:
            c = c - o
            n = len(c)
            if n < 2 * cross:
                continue
            c = c + normals(c) * (along(rng, n, 6 * cross) * 0.05 * width * jit)[:, None]       # the column wanders a little
            nrm = normals(c)
            wide = width * (1 + 0.08 * jit * along(rng, n, 4 * cross))                # and the plait is fuller here, tighter there
            for side in (-1.0, 1.0):
                at = rng.uniform(0, cross) + (0.5 * cross if side > 0 else 0.0)       # the two sides half a crossing apart
                while at < n - 0.6 * cross:
                    run = cross * rng.uniform(0.75 - 0.2 * jit, 0.75 + 0.2 * jit)
                    i0, i1 = int(at), min(int(at + run), n - 1)
                    at += cross * rng.uniform(1 - 0.16 * jit, 1 + 0.16 * jit)
                    x, y = int(c[(i0 + i1) // 2, 0]), int(c[(i0 + i1) // 2, 1])
                    if i1 - i0 < 3 or not (0 <= x < w_ and 0 <= y < h_) or rng.uniform() < skip:
                        continue
                    sh = float(shade[y, x])
                    v = min((faint + (1 - faint) * sh) * float(hand[y, x]) * rng.uniform(0.7, 1.1), 1.0)
                    wd = (w0 + (w1 - w0) * sh) * rng.uniform(0.7, 1.25)
                    a, b = rng.uniform(0.28, 0.4) * wide[i0], rng.uniform(0.0, 0.1) * wide[i1]           # from the cable's side in towards its middle: steep, a strand, not a chevron
                    p0, p2 = c[i0] + nrm[i0] * side * a, c[i1] + nrm[i1] * side * b
                    p1 = (p0 + p2) / 2 + nrm[i0] * side * rng.uniform(-0.02, 0.07) * wide[i0]           # a strand bows
                    taper(m, np.array([p0, p1, p2]), (0.5 * wd, wd, 0.75 * wd), (0.8 * v, v, 0.9 * v))      # a teardrop, fuller towards the middle of the plait
                    if rng.uniform() < 0.3 * jit:                 # now and then the strand's own turn: a small soft touch beside the wedge
                        q = p1 - nrm[i0] * side * rng.uniform(0.1, 0.2) * wide[i0] + (c[i1] - c[i0]) * rng.uniform(-0.2, 0.2)
                        taper(soft, np.array([q, q + (p2 - p0) * rng.uniform(0.25, 0.45)]), (0.5 * wd, 0.3 * wd), (0.4 * v, 0.3 * v))
                # the groove beside the cable: short soft marks that come and go
                here, at = 0.5 * (1 + np.tanh(0.9 * along(rng, n, 2.0 * cross))), rng.uniform(0, cross)
                while sides and at < n - 2:
                    run = cross * rng.uniform(0.5, 1.2)
                    i0, i1 = int(at), min(int(at + run), n - 1)
                    at += run + cross * rng.uniform(0.05, 0.5)
                    x, y = int(c[(i0 + i1) // 2, 0]), int(c[(i0 + i1) // 2, 1])
                    if i1 - i0 < 3 or not (0 <= x < w_ and 0 <= y < h_) or here[(i0 + i1) // 2] > 0.72:
                        continue
                    sh = float(shade[y, x])
                    v = sides * (faint + (1 - faint) * sh) * float(hand[y, x]) * rng.uniform(0.6, 1.1)
                    off = side * (0.56 * wide[i0] + rng.normal(0, 0.02 * width * jit))
                    taper(soft, np.array([c[i0] + nrm[i0] * off, c[(i0 + i1) // 2] + nrm[i0] * (off + rng.normal(0, 0.015 * width)), c[i1] + nrm[i1] * off]), (0.3 * w1, 0.5 * w1, 0.3 * w1), (v, v, 0.8 * v))
        dry = layer.get("dry", 0.3)
        m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 0.5 * px) + cv2.GaussianBlur(soft.astype(np.float32) / 255, (0, 0), 1.1 * px)
        d = m * (1 - 0.8 * dry + 0.8 * dry * step(self.tooth[box], 0.6 * dry - 0.25, 0.6 * dry + 0.25) * 1.6)
        return np.clip(m, 0, 1), d, box

    # ---- painting from an underdrawing: a tone map of the picture, made beforehand, that the brush looks at

    def pin(self, under=None, masks=None):
        """Pin up the underdrawing (an image on this sheet's paper colour, or what the paint lets through as floats;
        any size) and the named areas that come with it (masks, usable in "clip" and "out")."""
        fit = lambda a: cv2.resize(a, (self.nw, self.nh), interpolation=cv2.INTER_AREA if a.shape[1] > self.nw else cv2.INTER_CUBIC)
        if under is not None:
            u = cv2.imread(under) if isinstance(under, str) else under
            u = u[..., ::-1].astype(np.float32) / self.paper if u.dtype == np.uint8 else u.astype(np.float32)
            self.under = np.clip(fit(u), 0.02, 1.0)
        for name, m in (masks or {}).items():
            m = cv2.imread(m, cv2.IMREAD_GRAYSCALE) if isinstance(m, str) else m
            self.masks[name] = np.clip(fit(m.astype(np.float32) / (255 if m.dtype == np.uint8 else 1)), 0, 1)

    def kept(self, layer):
        keep = np.ones((self.nh, self.nw), np.float32)
        names = lambda v: [v] if isinstance(v, str) else v or []
        for name in names(layer.get("clip")):
            keep *= self.masks[name]
        for name in names(layer.get("out")):
            keep *= 1 - self.masks[name]
        return keep

    def seen(self, skip=0.0):
        """How dark the underdrawing is, per channel (0 = bare paper); with `skip`, thin dark lines narrower than
        that are not seen: they are for the pencil."""
        u = self.under
        if skip:
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(skip * self.px) + 1,) * 2)
            u = cv2.erode(cv2.dilate(u, k), k)
        return -np.log(u)

    def form(self, dens, sigma):
        """Which way the form runs, seen at one size: unit vectors along the lines of equal tone."""
        g = cv2.GaussianBlur(dens, (0, 0), sigma * 0.5)
        gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
        jxx, jxy, jyy = (cv2.GaussianBlur(v, (0, 0), sigma * 1.5) for v in (gx * gx, gx * gy, gy * gy))
        th = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2
        return np.cos(th).astype(np.float32), np.sin(th).astype(np.float32)

    def drawn_out(self, rng, vx, vy, width, length):
        """Noise drawn out along the form: its blobs are the footprints of brush touches `width` across."""
        f = max(1.0, width / 5.0)                                 # worked small, the blobs are smooth anyway
        h, w = int(self.nh / f), int(self.nw / f)
        vx, vy = cv2.resize(vx, (w, h), interpolation=cv2.INTER_AREA), cv2.resize(vy, (w, h), interpolation=cv2.INTER_AREA)
        n = noise(rng, h, w, width / f * 0.5)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        acc, step = n.copy(), width / f * 0.5
        for sign in (1, -1):
            px, py, dx, dy = xx.copy(), yy.copy(), vx * sign, vy * sign
            for _ in range(max(1, int(round(length / width)))):
                px, py = px + dx * step, py + dy * step
                sx = cv2.remap(vx, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                sy = cv2.remap(vy, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                flip = np.where(sx * dx + sy * dy < 0, -1, 1).astype(np.float32)   # a direction has no sign: keep going the same way
                dx, dy = sx * flip, sy * flip
                acc += cv2.remap(n, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return cv2.resize(acc, (self.nw, self.nh), interpolation=cv2.INTER_CUBIC)

    def study(self, layer, rng):
        """Washes laid from the underdrawing, big and pale first, then smaller and darker. Every pass cuts the area
        into touches (a step of tone ends one, and so does the reach of the brush along the form), lays in each the
        palest tone still missing there, hard where the tone steps or on one side of the touch, wet elsewhere."""
        keep = self.kept(layer)
        ys, xs = np.where(keep > 0.02)
        if not len(ys):
            return
        box = (slice(max(ys.min() - 8, 0), min(ys.max() + 9, self.nh)), slice(max(xs.min() - 8, 0), min(xs.max() + 9, self.nw)))
        keep, px = keep[box], self.px
        want = self.seen(layer.get("skip", 0.5))
        tone = want.mean(-1)
        sizes = layer.get("sizes", (36, 18, 9, 4.5, 2.5))
        depth, wet, rim = layer.get("depth", 0.85), layer.get("wet", 0.45), layer.get("rim", 0.3)
        grain, pool, tint = layer.get("grain", 0.1), layer.get("pool", 0.1), layer.get("tint", 0.05)
        long, bands, light = layer.get("long", 3.0), layer.get("bands", 0.1), layer.get("light", 0.03)
        hard_side, least = layer.get("hard", 0.5), layer.get("least", 0.025)
        yy, xx = np.mgrid[box[0], box[1]].astype(np.float32)
        for i, size in enumerate(sizes):
            s = size * px
            last = 1 - i / max(len(sizes) - 1, 1)                                    # 1 for the first, loosest pass .. 0 for the last, exact one
            vx, vy = self.form(tone, s)
            blobs = self.drawn_out(rng, vx, vy, s, s * long)[box]
            seen = cv2.GaussianBlur(tone, (0, 0), s * 0.22)[box]
            key = (np.floor(seen / bands + rng.uniform()) * 2 + (blobs > 0)).astype(np.int32)
            key[keep < 0.02] = -1
            cells, n = np.zeros(key.shape, np.int32), 1
            for k in np.unique(key[key >= 0]):
                c, lab = cv2.connectedComponents((key == k).astype(np.uint8), connectivity=4)
                cells[lab > 0] = lab[lab > 0] + n - 1
                n += c - 1
            flat = cells.ravel()
            count = np.maximum(np.bincount(flat, minlength=n), 1).astype(np.float32)
            missing = np.clip(want[box] + np.log(self.T[box]), 0, None)              # pigment still to come, per channel
            a = np.stack([np.bincount(flat, weights=missing[..., ch].ravel(), minlength=n) / count for ch in range(3)], 1).astype(np.float32)
            m = cv2.GaussianBlur(missing.mean(-1), (0, 0), 0.4 * px).ravel()
            order = np.lexsort((m, flat))                                            # the palest tone missing in each touch: small lights inside it stay
            first = np.concatenate([[0], np.cumsum(np.bincount(flat, minlength=n))[:-1]])
            pale = m[order][np.minimum(first + ((0.5 - 0.4 * last) * (count - 1)).astype(np.int64), len(m) - 1)]
            a *= (pale / (a.mean(-1) + 1e-6)).clip(0, 1)[:, None]
            full = np.bincount(flat, weights=seen.ravel(), minlength=n) / count
            a *= ((1 - (1 - depth) * last) * (full > light) * (a.mean(-1) > least) * np.clip(1 + layer.get("vary", 0.12) * last * rng.standard_normal(n), 0.6, 1.4))[:, None]
            a *= np.clip(1 + tint * rng.standard_normal((n, 3)), 0.7, 1.3)           # broken colour: no two touches quite alike
            a[0] = 0
            P = a[cells]
            cx, cy = (np.bincount(flat, weights=v.ravel(), minlength=n) / count for v in (xx, yy))
            th = rng.uniform(0, 2 * np.pi, n)
            side = ((xx - cx[cells]) * np.cos(th)[cells] + (yy - cy[cells]) * np.sin(th)[cells]) / (0.5 * np.sqrt(count)[cells] + 1)
            dried = (rng.uniform(size=n) < hard_side).astype(np.float32)[cells] * step(side, -0.3, 0.3)   # one hard side, one wet
            jump = np.abs(P - cv2.GaussianBlur(P, (0, 0), 0.5 * s)).sum(-1)
            hard = np.maximum(dried, cv2.GaussianBlur(step(jump, 0.03, 0.12), (0, 0), 0.8 * px))
            soft = cv2.GaussianBlur(P, (0, 0), float(np.clip(wet * s, 0.8 * px, layer.get("run", 4) * px)))
            edge = np.clip(P - cv2.GaussianBlur(P, (0, 0), 1.3 * px), 0, None)       # pigment gathers inside a hard edge
            P = hard[..., None] * (cv2.GaussianBlur(P, (0, 0), 0.5 * px) + 2 * rim * edge) + (1 - hard[..., None]) * soft
            f = self.hand[box] * np.float32(min(layer.get("wobble", 0.5) * self.k, 0.12 * s))
            P = cv2.remap(P, (xx - box[1].start + f[..., 0]).astype(np.float32), (yy - box[0].start + f[..., 1]).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            room = cv2.GaussianBlur(missing, (0, 0), 0.5 * px)                       # the lights are painted round, not over
            over = layer.get("over", 0.15)
            P = np.minimum(P, room * (1 + over) + 0.15 * over)
            if i == len(sizes) - 1 and layer.get("finish", 0):                       # the smallest brush puts in what is still missing
                P = np.maximum(P, layer["finish"] * room * (room.mean(-1, keepdims=True) > least))
            P *= (1 + pool * noise(rng, P.shape[0], P.shape[1], 9 * px))[..., None]
            P *= (1 + grain * (1 - 2 * self.tooth[box]))[..., None]
            self.T[box] *= np.exp(-np.clip(P, 0, None) * keep[..., None])

    def trace(self, layer, rng):
        """Pencil over the thin dark lines of the underdrawing (the ones the washes do not see): followed by hand,
        pressed harder where the line is darker, broken like any pencil line."""
        keep, px = self.kept(layer), self.px
        r = max(layer.get("skip", 1.2), getattr(self, "line_skip", 0))
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(r * px) + 1,) * 2)
        seen = getattr(self, "lines_from", None)                                     # the lines may be read off another picture than the tones
        seen = self.under if seen is None else np.clip(cv2.resize(seen, (self.nw, self.nh), interpolation=cv2.INTER_CUBIC), 0.02, 1)
        tone = cv2.GaussianBlur(seen @ np.array([0.3, 0.59, 0.11], np.float32), (0, 0), 0.4 * px)
        for key, sign in (("only", 1), ("drop", -1)):                                # which of the source's lines to keep: inside / outside shapes you draw
            if key in layer:
                m = np.zeros((self.nh, self.nw), np.uint8)
                shapes = layer[key] if isinstance(layer[key][0], list) else [layer[key]]
                cv2.fillPoly(m, [np.round(self.to(flow(p))).astype(np.int32) for p in shapes], 1)
                keep = keep * (m if sign > 0 else 1 - m)
        dark = (cv2.erode(cv2.dilate(tone, k), k) - tone) * (keep > 0.5)             # how much darker than what is around it
        lo = layer.get("over", 0.035)
        skel = thin(cv2.morphologyEx((dark > lo).astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)))
        pieces, press = [], []
        for c in chains(skel, int(layer.get("shortest", 3) * px)):
            v = dark[c[:, 1].astype(int), c[:, 0].astype(int)].mean()
            c = cv2.GaussianBlur(np.pad(c, ((6, 6), (0, 0)), mode="edge").astype(np.float32), (1, 7), 0)[6:-6]
            n = max(3, int(len(c) / (3 * px)) + 1)
            pieces.append([tuple(q / self.k + self.o) for q in c[np.linspace(0, len(c) - 1, n).round().astype(int)]])
            press.append(float(np.clip(v / layer.get("full", 0.12), 0.25, 1.3)))
        if pieces:
            line = {key: v for key, v in layer.items() if key not in ("trace", "skip", "over", "shortest", "full", "head", "only", "drop")}
            self.paint(dict({"w": 0.9, "p": (0.5, 1, 1, 0.6), "broken": 0.2, "wobble": 0.15}, **line, pencil=pieces, press=press))

    def hatch(self, layer, rng):
        """Dry-brush strokes that follow the form of the underdrawing: strands of hair, the lie of a cloth. They go
        where the underdrawing is darker than its surroundings, in the tones found there."""
        keep, px = self.kept(layer), self.px
        want = self.seen()
        tone = want.mean(-1)
        vx, vy = self.form(tone, layer.get("see", 3) * px)
        ys, xs = np.where(keep > 0.5)
        if not len(ys):
            return
        lo, hi = (v * px for v in layer.get("length", (8, 28)))
        n = int(layer.get("density", 1.0) * len(ys) / (0.5 * (lo + hi) * 3 * px))
        pick = rng.choice(len(ys), n)
        local = cv2.GaussianBlur(tone, (0, 0), 1.0 * px) - cv2.GaussianBlur(tone, (0, 0), 6 * px)   # strands and furrows
        strokes = []
        for x0, y0 in zip(xs[pick].astype(float), ys[pick].astype(float)):
            if rng.uniform() > 0.25 + 6 * local[int(y0), int(x0)]:
                continue
            half, pts = rng.uniform(lo, hi) / 2, {}
            for sign in (1, -1):
                x, y, dx, dy, run = x0, y0, 0.0, 0.0, []
                while len(run) * 2.0 < half:
                    ix, iy = int(round(x)), int(round(y))
                    if not (0 <= ix < self.nw and 0 <= iy < self.nh) or keep[iy, ix] < 0.5:
                        break
                    ux, uy = vx[iy, ix] * sign, vy[iy, ix] * sign
                    if run and ux * dx + uy * dy < 0:
                        ux, uy = -ux, -uy
                    dx, dy = ux, uy
                    x, y = x + 2.0 * dx, y + 2.0 * dy
                    run.append((x, y))
                pts[sign] = run
            line = pts[-1][::-1] + [(x0, y0)] + pts[1]
            if len(line) * 2.0 >= lo:
                c = np.array(line)
                strokes.append((tone[int(y0), int(x0)], [tuple(q / self.k + self.o) for q in c[np.linspace(0, len(c) - 1, max(3, len(c) // 5)).round().astype(int)]]))
        if not strokes:
            return
        tones = np.array([t for t, _ in strokes])
        edges = np.quantile(tones, (0, 0.4, 0.75, 1.0))
        base = {key: v for key, v in layer.items() if key not in ("hatch", "see", "length", "density", "deeper", "head")}
        for i in range(3):                                                           # light, middle and dark strokes, each in its own tone
            sel = [p for t, p in strokes if edges[i] <= t <= edges[i + 1]]
            inside = (keep > 0.5) & (tone >= edges[i]) & (tone <= edges[i + 1])
            if not sel or not inside.any():
                continue
            c = np.exp(-want[inside].mean(0) * layer.get("deeper", 1.25)) * self.paper
            self.paint(dict({"w": (0.4, 1.4, 0.4), "dry": 0.45, "vary": 0.6, "alpha": 0.6}, **base, stroke=sel, color="#%02X%02X%02X" % tuple(int(v) for v in np.clip(c, 0, 255))))


    def paint(self, layer, show=True):
        """One layer. `show=False`: it is worked out and its "name" remembered (others clip to it), but no paint is laid."""
        rng = np.random.default_rng((self.seed, zlib.crc32(repr(layer).encode())))  # a layer keeps its own hand when others change
        layer = self.place(layer)
        for kind in ("study", "trace", "hatch"):
            if kind in layer:
                return getattr(self, kind)(layer, rng) if show else None
        if "bloom" in layer:                                      # its edge is a crinkled line unless told otherwise
            layer = dict({"ragged": 2.5, "rim": 2.0, "broken": 0.5, "pool": 0, "grain": 0}, **layer)
        m, a, box = self.brush(layer, rng) if "brush" in layer else self.cable(layer, rng) if "cable" in layer else self.knit(layer, rng) if "knit" in layer else self.lines(layer, rng) if ("stroke" in layer or "pencil" in layer) else self.shape(layer, rng)
        if m is None:                                             # wholly outside the frame: nothing to paint, but the name exists (empty)
            if layer.get("name"):
                self.masks.setdefault(layer["name"], np.zeros((self.nh, self.nw), np.float32))
            return
        names = lambda v: [v] if isinstance(v, str) else v or []
        keep = np.ones_like(m)
        for name in names(layer.get("clip")):
            keep *= self.masks[name][box]
        for name in names(layer.get("out")):
            keep *= 1 - self.masks[name][box]
        a = a * keep
        if layer.get("name"):                                     # the remembered shape is the clean coverage, not the pigment
            full = self.masks.setdefault(layer["name"], np.zeros((self.nh, self.nw), np.float32))
            full[box] = np.maximum(full[box], np.clip(m * keep, 0, 1))
        if self.watch is not None and "brush" in layer:           # over the whole sheet: a part of its clip that no stroke came near counts too
            cover, kept = np.zeros((self.nh, self.nw), np.float32), np.ones((self.nh, self.nw), np.float32)
            cover[box] = np.clip(m, 0, 1)
            for name in names(layer.get("clip")):
                kept *= self.masks[name]
            for name in names(layer.get("out")):
                kept *= 1 - self.masks[name]
            self.watch.append((layer, cover, kept if layer.get("clip") else cover))
        if not show:
            return
        if "bloom" in layer:                                      # a backrun: water ran back into a drying wash and pushed its pigment
            wash_out = m * (0.75 + 0.25 * np.tanh(noise(rng, m.shape[0], m.shape[1], 7 * self.px)))    # outwards, into a line at its edge
            self.T[box] = self.T[box] ** (1 + layer["bloom"] * keep * ((a - m) - 0.7 * wash_out))[..., None]
            return
        if "sparkle" in layer:                                    # paper that stayed dry under a fast brush: specks on the peaks of the
            at = 1.6 - 2.4 * layer["sparkle"]                     # tooth, in patches (the same patches for every layer)
            dry = step(self.damp[box], at - 0.4, at + 0.4) * step(self.tooth[box], 0.84, 0.93)
            self.T[box] = self.T[box] ** (1 - np.clip(m * keep * dry, 0, 1))[..., None]
            return
        if "lift" in layer:                                       # paint taken off: what is left lets more light through
            self.T[box] = self.T[box] ** (1 - np.clip(a * layer["lift"], 0, 1))[..., None]
            return
        color = layer.get("wash") or layer.get("color") or (GRAPHITE if "pencil" in layer else None)
        if color is None:
            return                                                # a reserved shape
        c = np.clip(np.array(hexrgb(color), np.float32) / self.paper, 0.02, 1.0)
        self.T[box] *= np.exp((a * layer.get("alpha", 1.0))[..., None] * np.log(c))

    def finish(self, tooth=1.0):
        h = cv2.GaussianBlur(self.tooth, (0, 0), 0.8 * self.grainpx * self.weave)
        light = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) + cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3)   # lit from the upper left
        shade = 1 + tooth * (0.0068 * light / (light.std() + 1e-9) + 0.003 * self.cloud)       # 0.0068: bare paper reads 1.5 (fine std), the look's quiet tooth
        img = self.paper * shade[..., None] * self.T
        img = cv2.resize(np.clip(img, 0, 255), (self.W, self.H), interpolation=cv2.INTER_AREA)
        return np.clip(img + 0.5, 0, 255).astype(np.uint8)[..., ::-1]


def draw(d, parts=None, only=None, watch=None):
    """One drawing dict -> BGR uint8 image (write it with cv2.imwrite). `only`: the numbers of the layers to paint (the others
    are worked out for their names, so "clip" / "out" hold, and lay nothing: one layer or one session ALONE, `look.py layers`);
    `watch`: a list that receives every "brush" session's (layer, coverage, kept area), both over the whole sheet at twice the
    output size (`look.py holes`; a session without a "clip" has nothing to leave open)."""
    paper = hexrgb(d["paper"]) if isinstance(d.get("paper"), str) else d.get("paper", PAPER)
    sheet = Sheet(d["frame"], d.get("out", OUT), paper, d.get("seed", 1), parts, d.get("weave", 1.0), d.get("fine", 1.0))
    sheet.eyes, sheet.watch = d.get("eyes"), watch
    sheet.pin(d.get("under"), d.get("masks"))
    for i, layer in enumerate(d["layers"]):
        sheet.paint(layer, only is None or i in only)
    img = sheet.finish(d.get("tooth", 1.0))
    return np.ascontiguousarray(img[:, ::-1]) if d.get("mirror") else img


# ---- marks a painter repeats: they return pieces for one "stroke" layer (`from wash import runs, ribs, ring`)

def _even(nodes, n=24):
    P = resample(flow(nodes, closed=False), 1.0)
    return P[np.round(np.linspace(0, len(P) - 1, n)).astype(int)]


def runs(a, b, pitch, seed=0, lo=0.45, hi=0.9, skip=0.12, jit=0.6):
    """Broken parallel lines filling the field between two guide lines `a` and `b` (open node lists drawn the same way),
    one line every `pitch`: the ribs of a knit, strands, planks. Each line is cut into stretches of lo..hi of the way
    with gaps between them, and now and then one is left out, so the field never becomes a ruled grid."""
    rng = np.random.default_rng(seed)
    A, B = _even(a), _even(b)
    n = max(int(np.linalg.norm(A - B, axis=1).mean() / pitch), 1)
    out = []
    for j in range(n + 1):
        t, s0 = (j + rng.uniform(-0.12, 0.12)) / n, 0.0
        while s0 < 0.95:
            s1 = min(s0 + rng.uniform(lo, hi), 1)
            if rng.uniform() > skip and s1 - s0 > 0.12:
                at, k = np.linspace(s0, s1, 5) * (len(A) - 1), np.arange(len(A))        # between the samples, not on the nearest: two nodes on one sample made a kink
                on = lambda G: np.stack([np.interp(at, k, G[:, 0]), np.interp(at, k, G[:, 1])], 1)
                out.append([tuple(q) for q in on(A) * (1 - t) + on(B) * t + rng.uniform(-jit, jit, (5, 2))])
            s0 = s1 + rng.uniform(0.04, 0.2)
    return out


def ribs(mid, width, gap, seed=0, lean=0.0, skip=0.12, jit=0.8):
    """Short strokes across a band whose middle line is `mid`, one every `gap`: the ribbing of a cuff, a hem, a placket.
    `lean` tilts them along the band (0.25: a V-neck band whose ribs run askew)."""
    rng = np.random.default_rng(seed)
    P = resample(flow(mid, closed=False), gap)
    d = np.gradient(P, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    out = []
    for q, t, n in zip(P, d, np.stack([-d[:, 1], d[:, 0]], 1)):
        if rng.uniform() < skip:
            continue
        h = width / 2 * rng.uniform(0.75, 1.0)
        a, b = q - n * h + t * lean * h, q + n * h - t * lean * h
        out.append([tuple(v + rng.uniform(-jit, jit, 2)) for v in (a, (a + b) / 2, b)])
    return out


def ring(c, r, n=8, squash=1.0):
    """Nodes of a small round shape (a button, a bead)."""
    return [(c[0] + r * np.cos(a), c[1] + r * squash * np.sin(a)) for a in np.linspace(0, 2 * np.pi, n, endpoint=False)]


def arc(c, rx, ry=None, a0=0.0, a1=360.0, n=10):
    """Nodes along an oval round `c`, from angle a0 to a1 in degrees (0: right, 90: below, 180: left, 270: above; a whole
    turn gives a closed shape's nodes): a lens, a rim in pieces with a gap where the light catches it, an eyelid."""
    ry = rx if ry is None else ry
    whole = abs(a1 - a0) >= 360
    return [(c[0] + rx * np.cos(a), c[1] + ry * np.sin(a)) for a in np.radians(np.linspace(a0, a1, n, endpoint=not whole))]


def _rgb(c):
    return np.array(hexrgb(c) if isinstance(c, str) else c, float)


def lum(c):
    """Luminance (0-255) of a hex colour or an RGB triple: the number `look.py values` prints."""
    return float(_rgb(c) @ (0.3, 0.59, 0.11))


def need(glaze, frm, to, paper=PAPER):
    """The alpha at which the wash `glaze` takes paint that reads `frm` down to `to` (luminances as `look.py values` prints
    them, or hex colours): washes multiply, so a nested step from one measured tone to the next is
    ln(to / frm) / ln(glaze / paper). `paper` is the sheet's. need(SHADE, 104, 64) -> 1.02; 0, and a line on stderr, if `to`
    is not darker (a glaze cannot lighten)."""
    f, t = (lum(v) if isinstance(v, (str, tuple, list)) else float(v) for v in (frm, to))
    if t >= f:                                                     # a step written the wrong way round would paint nothing, silently
        print(f"need: from {f:.0f} to {t:.0f} is not darker: this step paints nothing (alpha 0)", file=sys.stderr)
    return float(max(np.log(t / f) / np.log(min(lum(glaze) / lum(paper), 0.98)), 0.0))


SPECK = dict(grain=55.0, sediment=60.0, pool=36.0, settle=6.5)    # per cent of speck that 1.0 of each gives at density 1 (measured on flat squares)


def toned(kind=None, tone=150, paper=PAPER, speck=None, **more):
    """The water of a kind of wash (POOL = dict(settle=0.35, sediment=0.12, ...)) for a wash that ARRIVES at luminance `tone`.
    "grain", "pool", "settle" and "sediment" are shares of the pigment, so what the eye sees of them grows with the pigment's
    density D = ln(paper / tone): speck (fine std / mean luminance on a flat patch, per cent; `look.py speck`) is about
    D x sqrt((55 grain)^2 + (60 sediment)^2 + (36 pool)^2 + (6.5 settle)^2).
      speck=7.5   MEASURED on the source's flat patches at this tone (`look.py speck SRC mask=…` prints it per tone): the four are
                  scaled, up or down, so that the wash shows that much. This is the rule; measure before choosing the water.
      no speck    nothing was measured: the four are cut back by 0.43 / D (never raised), which keeps a mid-tone's look at every
                  value (x0.5 at tone 100, x0.33 at 64, x0.26 at 45): right for smooth cloth, too clean for a fabric that shows
                  the paper (a padded jacket reads 7-8 % where this gives 3-4).
    The engine's own defaults ("grain" 0.1, "pool" 0.08) are part of a wash's water, so they are written into the result and
    scaled with the rest. Edges ("ragged", "dry", "broken", "rim") are left as they are."""
    out = dict({"grain": 0.1, "pool": 0.08}, **(kind or {}), **more)
    D = max(np.log(lum(paper) / max(float(tone), 1.0)), 1e-3)
    if speck is None:
        k = min(1.0, 0.43 / D)
    else:
        k = float(speck) / max(D * np.sqrt(sum((SPECK[key] * out.get(key, 0)) ** 2 for key in SPECK)), 1e-6)
    return {key: (round(v * k, 4) if key in SPECK else v) for key, v in out.items()}


def step_to(glaze, frm, to, kind=None, paper=PAPER, speck=None, **more):
    """One nested step of a garment as layer options: the glaze, the alpha that takes `frm` to `to` (need) and the kind's
    water at that tone (toned; `speck`: as measured on the source there):  {"path": SHAPE, **step_to(SHADE, 104, 64, POOL), "clip": "paint"}."""
    return dict(toned(kind, lum(to) if isinstance(to, str) else to, paper, speck, **more), wash=glaze, alpha=round(need(glaze, frm, to, paper), 3))


def beside(nodes, d):
    """An open line of nodes moved sideways by `d` grid units (positive: to the right hand of someone walking along it;
    drawn clockwise round a shape: into it). The stitch line inside a lapel's edge, the silver line inside a metal rim."""
    P = np.array([n[:2] for n in nodes], float)
    return [tuple(q) + tuple(n[2:]) for q, n in zip(P + normals(P) * d, nodes)]


def scallop(nodes, lobe=40, depth=0.2, seed=0):
    """A closed outline redrawn as the edge a puddle of thin paint dries with: round lobes of very unequal width (0.4-2.2
    of `lobe`), some swelling out by `depth` of their width and some nearly flat, meeting in small bays of which most are
    sharp. Paint it pale and flat, with its rim (a pale wash needs a strong one to show its dried edge at all):
    {"path": scallop(BLOT, 44, seed=3), "wash": "#E2D8CA", "rim": 2, "broken": 0.3, "wobble": 0, "pool": 0.03}."""
    rng = np.random.default_rng(seed)
    P = resample(np.vstack([flow(nodes), flow(nodes)[:1]]), 1.0)[:-1]
    out_side = -1.0 if np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]) > 0 else 1.0
    cuts, s = [], 0.0
    while s < len(P) - 0.6 * lobe:
        cuts.append(int(s))
        s += lobe * rng.choice([rng.uniform(0.4, 0.8), rng.uniform(0.8, 1.4), rng.uniform(1.4, 2.2)])
    N, out = normals(P) * out_side, []
    for u, v in zip(cuts, cuts[1:] + [cuts[0] + len(P)]):
        wide = np.linalg.norm(P[v % len(P)] - P[u])
        swell = depth * wide * rng.uniform(0.25, 1.3)
        bay = tuple(P[u] - N[u] * min(0.3 * swell + 0.02 * lobe, 0.12 * lobe))
        out.append(bay + ("c",) if rng.uniform() < 0.7 else bay)
        lean = rng.uniform(0.35, 0.65)                                                # a lobe is fullest off its middle
        out += [tuple(P[i % len(P)] + N[i % len(P)] * swell * k) for i, k in ((u + int((v - u) * lean / 2), 0.75), (u + int((v - u) * lean), 1.0), (u + int((v - u) * (1 + lean) / 2), 0.7))]
    return out


def _lay(pts, wide, rng, spacing, length, angle, load, w, lap, ends, skip):
    """Strokes down one line (`pts`, a dense polyline; `wide`: the room each stroke has there): one load of the brush after the
    other, each set down over the end of the last."""
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    if s[-1] < 1.5 * spacing:                                                         # too short for a stroke: a crumb
        return []
    def at(u):                                                                        # a point of the line, straight on beyond its ends
        u = np.asarray(u, float)
        q = np.stack([np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])], -1)
        d0, d1 = (pts[1] - pts[0]) / (s[1] - s[0] + 1e-9), (pts[-1] - pts[-2]) / (s[-1] - s[-2] + 1e-9)
        return q + np.minimum(u, 0)[..., None] * d0 + np.maximum(u - s[-1], 0)[..., None] * d1
    ends = sorted(ends)                                                               # a range, whichever way round it was written
    a, stop, out = -rng.uniform(*ends) * spacing, s[-1] + rng.uniform(*ends) * spacing, []
    whole = stop - a
    while stop - a > 0.3 * spacing:
        b = min(a + rng.uniform(*length) * whole, stop)
        b = stop if stop - b < 0.8 * spacing else b
        u = np.linspace(a, b, 5)
        q = at(u)
        r = np.radians(rng.uniform(-angle, angle))                                    # the stroke turns a little off the form, and bows
        q = (q - q[2]) @ np.array([[np.cos(r), np.sin(r)], [-np.sin(r), np.cos(r)]]) + q[2]
        q[1:4] += normals(q)[1:4] * rng.normal(0, 0.015 * (b - a))
        room = np.interp(np.linspace(a, b, len(w)), s, wide) * (1 + lap) * rng.uniform(0.8, 1.25)
        if rng.uniform() >= skip:
            out.append({"path": [tuple(v) for v in q], "w": tuple(float(x) for x in np.asarray(w) * room), "load": float(rng.uniform(*load)) if b >= stop else float(max(rng.uniform(*load), 1.5))})
        if b >= stop:
            break
        a = b - rng.uniform(0.15, 0.35) * (b - a)
    return out


def strokes_along(guide, spacing, seed=0, to=None, within=None, length=(0.55, 1.0), angle=5.0, load=(1.0, 1.6), w=(0.25, 0.9, 1.0, 0.8), lap=0.35, ends=(-0.4, 0.8), skip=0.0):
    """Strokes for one "brush" layer, laid by decision instead of by coordinates: they follow `guide` (an open node list drawn
    the way the brush goes: down a sleeve, along a lapel, with the fall of the cloth), one about every `spacing` across it.
      to=LINE       they fill the field between `guide` and a second line drawn the same way (as runs() does): narrow where the
                    two lines close in, swelling where they open. Without it they are the guide moved sideways
      within=SHAPE  each is cut to the stretch that lies inside a closed shape you drew (a shadow shape keeps its start, its
                    swell and its end; its outline is now the sides and ends of strokes). With `to`: that part of the field
    `length`: the share of its line one load of the brush covers (shorter: the brush is loaded again, before it runs dry, and
    set down over the end of the last stroke); `angle`: how many degrees a stroke may turn off the form; `load`: the range of loads (below 1 a stroke runs
    dry before its end, see "brush"); `w`: the pressure along a stroke as shares of its width; `lap`: how far neighbours lap
    over each other (0.35: a stroke is 1.35 spacings wide); `ends`: how far short of the line's ends (negative) or beyond
    them a stroke starts and stops, in spacings; `skip`: the share left out. Each stroke draws its own values from these
    ranges by `seed`: unequal widths, loads, lengths and angles, never a comb. Throw again until the long ones fall well."""
    rng = np.random.default_rng(seed)
    lines = []
    shape = flow(within).astype(np.float32) if within is not None else None
    if to is not None:
        A, B = (resample(_even(g, 48), 2.0) for g in (guide, to))
        A, B = (g[np.round(np.linspace(0, len(g) - 1, 160)).astype(int)] for g in (A, B))
        gap = np.linalg.norm(A - B, axis=1)
        n = max(int(round(gap.mean() / spacing)), 1)
        lines = [(A * (1 - tau) + B * tau, gap / n) for tau in (np.arange(n) + 0.5 + rng.uniform(-0.3, 0.3, n)) / n]
    else:
        G = resample(flow(guide, closed=False), 2.0)
        far = float(np.linalg.norm(shape.max(0) - shape.min(0)))
        G = np.vstack([G[0] + (G[0] - G[1]) / 2.0 * np.arange(far, 0, -2.0)[:, None], G, G[-1] + (G[-1] - G[-2]) / 2.0 * np.arange(2.0, far + 2, 2.0)[:, None]])
        N = normals(G)
        near = np.argmin(np.linalg.norm(shape[:, None] - G[None, ::4], axis=2), axis=1) * 4
        off = np.sum((shape - G[near]) * N[near], axis=1)                             # how far the shape reaches to each side of the guide
        d = off.min() + spacing * rng.uniform(0.3, 0.7)
        while d < off.max():
            lines.append((G + N * d, np.full(len(G), float(spacing))))
            d += spacing * rng.uniform(0.7, 1.35)
    out = []
    for line, wide in lines:
        if shape is None:
            out += _lay(line, wide, rng, spacing, length, angle, load, w, lap, ends, skip)
            continue
        inside = np.array([cv2.pointPolygonTest(shape, (float(x), float(y)), False) >= 0 for x, y in line])
        edges = np.flatnonzero(np.diff(np.concatenate([[0], inside.astype(int), [0]])))
        for i0, i1 in zip(edges[::2], edges[1::2]):
            if i1 - i0 > 2:
                out += _lay(line[i0:i1], wide[i0:i1], rng, spacing, length, angle, load, w, lap, ends, skip)
    return out


def hem(line, n, lengths=(20, 70), angles=(-10, 10), seed=0, w=(14, 26), load=(0.75, 1.3), back=40, press=(0.8, 1.0, 0.9, 0.6), way=None, reach=1.0):
    """Where a garment ends because the brush left it (a hem, the bottom of a sleeve): `n` strokes for a "brush" layer, each set
    down about `back` inside the wash and dragged across `line` (where the solid paint stops; an open node list), going on
    `lengths` beyond it at `angles` degrees off `way` (a direction (dx, dy); unless given, the line's right-hand side: drawn
    left to right, downwards). They stand at
    unequal distances, neighbours often reach about as far and then one does not, each has its own width (`w`, a range),
    pressure (`press`, shares along it) and `load` (in stroke lengths: about 1 runs dry at its end, less breaks up before it,
    1.5 ends wet and round). The ends ARE the hem: the garment's area is open there, and nothing is drawn round them.
    `reach`: a WET end (load 1 or more) is a lobe, broader than it is long: it runs no further beyond the line than `reach` times
    its own end width, whatever `lengths` says (a narrow wet end hanging below its neighbours is a DRIP). Only a stroke that runs
    dry (load under 1) is dragged on as far as `lengths`. None: no such limit (a fringe, where thin strands are the point)."""
    rng = np.random.default_rng(seed)
    P = resample(flow(line, closed=False), 1.0)
    N = normals(P)
    gaps = rng.uniform(0.5, 1.6, n + 1)
    drift, out = rng.uniform(), []
    for u in np.cumsum(gaps)[:n] / gaps.sum():
        i = int(round(u * (len(P) - 1)))
        drift = float(np.clip(drift + rng.uniform(-0.45, 0.45), 0, 1))
        far = lengths[0] + (lengths[1] - lengths[0]) * (drift if rng.uniform() > 0.25 else rng.uniform())
        r = np.radians(rng.uniform(*angles))
        d = (N[i] if way is None else np.asarray(way, float) / np.linalg.norm(way)) @ np.array([[np.cos(r), np.sin(r)], [-np.sin(r), np.cos(r)]])
        side = np.array([-d[1], d[0]])
        a, bow, jog, wide, full = P[i] - d * back * rng.uniform(0.7, 1.2), rng.normal(0, 0.04), rng.normal(0, 1.0), rng.uniform(*w), float(rng.uniform(*load))
        if reach is not None and full >= 1:                                           # a wet end is a lobe, never a drip
            far = min(far, max(reach * press[-1] * wide, lengths[0]))
        b = P[i] + d * far
        out.append({"path": [tuple(a), tuple(P[i] + side * jog), tuple((P[i] + b) / 2 + side * bow * far), tuple(b)], "w": tuple(float(x) for x in np.asarray(press) * wide), "load": full})
    return out


def ladder(lit, shadow, dark=None, on=None, rich=1.0, paper=PAPER):
    """A garment's palette from the SOURCE's own colours (hex, read with `look.py values SRC at=x,y`): where the light
    falls on it, its shadow, and its deepest dark; `on` is the source's paper if it is not ours, `paper` the sheet's
    (hex or RGB; give both when the sheet is painted on the source's own paper). Returns six hex colours:
    LOCAL (the wash on bare paper) and the glazes TURN, SHADE, DEEP, DARK, RIB, which are multipliers: over LOCAL they give
    a half-tone, the source's shadow, a core half-way to its deepest dark, that dark (about x0.85, x0.65, x0.45, x0.3 of
    the light on a mid-tone garment), and the thin lines of a knit. The hue of every step is the source's own: a ladder
    copied from another garment drags this one towards that garment's colour (an olive sage goes teal).
    `rich` makes the local colour fuller without changing its tone (1.15 when the first render's chroma on the garment
    reads under the source's: pencil, knit lines and specks of paper grey a wash)."""
    P = _rgb(paper)
    t = lambda c: np.clip(_rgb(c) / (_rgb(on) if on else P), 0.02, 1.0)
    L, r = t(lit), np.clip(t(shadow) / t(lit), 0.05, 1.0)
    q = np.clip(t(dark) / L, 0.02, 1.0) if dark else r ** 2.8
    q = np.minimum(q, r ** 1.5)                                    # the deepest dark is deeper than the shadow, whatever was clicked
    d = -np.log(L)
    mid = np.array([0.3, 0.59, 0.11]) @ d                          # the channels spread about their weighted middle: the tone stays
    L = np.exp(-np.clip(mid + rich * (d - mid), 0, None))
    hexc = lambda v: "#%02X%02X%02X" % tuple(int(round(x)) for x in np.clip(P * v, 0, 255))
    return hexc(L), hexc(r ** 0.4), hexc(r), hexc(np.sqrt(r * q)), hexc(q), hexc(q ** 0.8)


# ---- from a flat shape to nodes: the starting point for a drawing

def nodes_of(mask, corner_deg=128, span=9, eps=2.2, scale=1.0):
    """The outline of a mask as pen nodes, to rough out a SILHOUETTE (a garment, a head of hair) before correcting it on
    `look.py grid`. Never for a shadow shape: thresholded tone traced into paths gave mud, airbrush clouds and contour
    steps in three attempts; a shadow is some twenty shapes you decide and draw. Corners where the edge really turns,
    and between them only as many points as the arc needs (`eps`: how far, in mask px, the path may leave the outline; 3 on a 1000 px figure gives
    about 50 nodes). Blur the mask a few px and threshold it first, or every crumb of its edge becomes a node.
    Coordinates are divided by `scale` (mask pixel -> grid)."""
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in sorted(cs, key=cv2.contourArea, reverse=True):
        c = c[:, 0, :].astype(float)
        if len(c) < 4 * span or cv2.contourArea(c.astype(np.float32)) < 60:
            continue
        sm = cv2.GaussianBlur(np.vstack([c[-span:], c, c[:span]]).astype(np.float32), (1, 5), 0)[span:-span]
        a, b = np.roll(sm, span, axis=0) - sm, np.roll(sm, -span, axis=0) - sm
        ang = np.degrees(np.arccos(np.clip(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9), -1, 1)))
        corners = sorted({i for i in range(len(c)) if ang[i] < corner_deg and ang[i] == ang[np.arange(i - span, i + span + 1) % len(c)].min()})
        plain = not corners
        if plain:
            corners = [0]
        nodes = []
        for u, v in zip(corners, corners[1:] + [corners[0] + len(c)]):
            run = c[np.arange(u, v + 1) % len(c)]
            keep = cv2.approxPolyDP(run.astype(np.float32)[:, None, :], eps, False)[:, 0, :]
            nodes.append((run[0][0], run[0][1]) if plain else (run[0][0], run[0][1], "c"))
            nodes += [(p[0], p[1]) for p in keep[1:-1]]
        out.append([(round(float(n[0]) / scale, 1), round(float(n[1]) / scale, 1)) + tuple(n[2:]) for n in nodes])
    return out


def load(path):
    """Import a drawings file (its folder goes on sys.path, so a parts.py beside it is found)."""
    path = Path(path).resolve()
    sys.path.insert(0, str(Path(__file__).resolve().parent))      # so drawings can `from wash import flow`
    sys.path.insert(0, str(path.parent))
    sys.modules.setdefault("wash", sys.modules["__main__"])
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        parts = __import__("parts").PARTS
    except ImportError:
        parts = None
    return mod.DRAWINGS, parts


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "helpers":
        import inspect
        for f in (strokes_along, hem, runs, ribs, ring, arc, beside, scallop, ladder, need, toned, step_to, nodes_of, flow, resample, draw):
            if not a[1:] or f.__name__ in a[1:]:
                print(f"{f.__name__}{inspect.signature(f)}\n    {inspect.getdoc(f).replace(chr(10), chr(10) + '    ')}\n")
    elif len(a) >= 2 and a[0] == "nodes":
        m = cv2.imread(a[1], cv2.IMREAD_GRAYSCALE) > 127
        for piece in nodes_of(m, scale=float(a[2]) if len(a) > 2 else 1.0, eps=float(a[3]) if len(a) > 3 else 2.2):
            print(piece)
    elif len(a) >= 2:
        drawings, parts = load(a[0])
        dst = Path(a[1])
        dst.mkdir(parents=True, exist_ok=True)
        for name in a[2:] or drawings:
            cv2.imwrite(str(dst / f"{name}.png"), draw(drawings[name], parts))
            print("painted", dst / f"{name}.png")
    else:
        sys.exit(__doc__)
