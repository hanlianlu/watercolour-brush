# Engine: look.py

The painter's eyes: reads a source exactly and checks your own marks against it (`grid`, `tones`, `values`, `speck`, `diff`, `paths`, `layers`, `holes`, and more). Nothing in it paints. It imports `wash.py`.

Plain Python 3 (3.12 or newer); needs `numpy` and `opencv-python-headless`. It reads and writes local image files only: no network.

**Setup, once per project:** save the code block below, exactly as it is, as `look.py` in the project's engine folder (for example `art/watercolour/`), beside the other engine files (`wash.py`, `regions.py`, `look.py` and `selftest.py`; see "Engine setup" in `SKILL.md`). They import each other, so all four stay in one folder. Run it with `python3 look.py grid SRC OUT.png x0 y0 x1 y1`; with no arguments it prints its manual.

```python
"""The painter's eyes: read a source exactly, and check your own marks against it. Nothing here paints.

    python3 look.py grid   SRC OUT.png x0 y0 x1 y1 [scale=2] [step=20]
        A zoom of a region of the source with a coordinate grid (source pixels). Read node positions off it.

    python3 look.py shapes SRC OUT.png mask=MASK.png [x0 y0 x1 y1] [scale=1.5] [blur=1.5,7]
        Where the source put its light and shadow in one area (a garment's mask-NAME.png from `regions.py build`): the area
        in four flat values (light, half-tone, shadow, dark; the darkest eighth, then steps at 35 and 65 %), with the grid,
        at two scales side by side: nearly as painted (a light along an edge, a cast shadow and every hard edge survive)
        and blurred to the big shapes (where each shadow starts, swells and ends; which side of an overlap is the dark one).
        It is for LOOKING: the shadow shapes you then draw by hand, as nodes read off `grid`; never trace these blobs.

    python3 look.py paths  DRAWINGS.py NAME SRC OUT.png [x0 y0 x1 y1] [scale=2] [layers=12-30] [kinds=path,stroke,pencil,lift,area,brush]
        Your marks drawn over the source (the drawing's grid must be the source's pixels; default region: the frame).
        Washes blue, reserved areas white, lifts yellow, strokes orange, pencil magenta, the strokes of a "brush" layer green
        (both sides, a dot where the brush was set down); each carries its layer number.
        Round dot: plain node, square: corner, ring: wet node. A feather stroke shows ticks on the side it dies away to.

    python3 look.py values IMG [IMG ...] [box=x0,y0,x1,y1] [mask=MASK.png] [areas=masks.npz [frame=x0,y0,w,h]] | at=x,y/x,y/...
        How dark and what colour: luminance at the darkest 1 / 5 / 25 / 50 / 75 / 95 %, the mean colour and how strong that
        colour is (chroma), per image; with areas= (the masks of `regions.py build`) one line per area: the measurement
        that picks the row in references/starting-values.md. The pictures are then on the source's grid, or, with frame=,
        are that frame of it (a portrait). With at=, the colour and luminance at those points (pick wash colours so).

    python3 look.py tones  IMG [x0 y0 x1 y1] [step=24] [blur=5]
        The picture read in ROWS OF TONES: blurred luminance on a grid, source coordinates along the top and the side. Where a
        garment is dark, where it stays light, where a channel of quilting turns: read this before any shadow shape is drawn
        (by eye, on a zoomed grid, a fold lands 30 px out).

    python3 look.py diff   PAINTED SOURCE [x0 y0 x1 y1] [step=40] [blur=6] [frame=x0,y0,w,h] [areas=masks.npz] [mask=MASK.png]
        Your render against the source, cell by cell: painted minus source (blurred luminance; "." within 8; minus: yours is
        too dark there), and per area the share of points (every 20 px) within 15 and within 25 and the mean difference.
        PAINTED is on the source's grid, or is frame= of it (a body frame, a draft). This table steers a garment's rounds: a
        column of +20 is a dark you left out, a patch of -30 a shape drawn too big. It says nothing about how the paint looks.

    python3 look.py speck  IMG [IMG ...] mask=MASK.png | box=x0,y0,x1,y1 [paper=#HEX] [win=24]
        How much of the paper a wash shows, measured BEFORE choosing its water: speck (fine std of luminance / mean, per cent)
        on the area's flat patches (the calmest third of its windows, so folds and edges do not count), at three tones, with the
        line to paste: toned(KIND, tone, PAPER, speck=…). Speck / D says what kind of cloth it is: 2.5-4 a smooth coat (the
        water toned down as the value falls), 6-7 a fabric that shows the paper at every value (a padded jacket, a soft
        scarf: the engine's water left as it is). Run it on your render too: within 1.5 points of the source's.

    python3 look.py layers DRAWINGS.py NAME OUT.png only=12,14-16 | only=wash,half | upto=15
        One layer or one session ALONE, or the picture as it stood after layer 15: the others are worked out for their names
        (so "clip" and "out" hold) and lay no paint. only= takes layer numbers (as `paths` prints them) and names. Look at
        every local colour alone before anything goes over it. (A "knit", a "cable" or a "study" alone sees bare paper.)

    python3 look.py holes  DRAWINGS.py NAME [OUT.png] [layers=12,wash] [least=30]
        Paper left open inside a session of strokes: for every NAMED "brush" session (or the layers given) the share of its
        kept area ("clip" minus "out") that no stroke covered, and each hole of `least` grid units² or more with its middle
        and size. A hole that runs off the frame or is most of an open hem is marked "open": the others are white lenses,
        closed with one more stroke by hand. OUT.png: the render with the holes in red.

    python3 look.py frame  PORTRAIT SHEET_OR_SOURCE
        Where a finished portrait was cut from its sheet: the frame (x0, y0, size, on the sheet's grid) that matches it best,
        and how well (r over 0.9: found). A finished picture painted again takes this frame.

    python3 look.py ladder SRC lit=x,y shadow=x,y [dark=x,y] [paper=SHEET_PAPER]   or   look.py ladder LIT SHADOW [DARK] [on=SOURCE_PAPER] [paper=…]
        A garment's palette from the source's own colours: its local colour where the light falls, and the glazes (TURN,
        SHADE, DEEP, DARK, RIB) that take it to the source's shadow and to its deepest dark. Prints the line to paste into a
        drawings file (`wash.ladder` gives the same there). Never copy another garment's glazes: they carry its hue.
        paper=: the sheet's own paper when it is not the engine's (a finished picture painted again on its paper).

    python3 look.py glaze  FROM TO [PAPER]
        Washes multiply. Prints the wash colour that, laid at alpha 1 over paint that now reads FROM, makes it read TO
        (paper x TO / FROM), e.g. glaze "#98A281" "#44513E".

    python3 look.py over   UNDER UPPER [PAPER]
        May the lighter garment run under the darker one? Washes multiply: prints what UPPER comes out as with UNDER beneath it
        (paper x UNDER / paper x UPPER / paper), how many levels darker and how far off its hue that is, and the answer: under
        (the lower one is near paper, or the upper one is a dark and the hue holds) or shared nodes (references/winter-clothes.md 5).

    python3 look.py texture IMG [IMG ...] [box=x0,y0,x1,y1]
        The measures of style.md that are not values: detail (mean |Laplacian| of luminance after a 1 px and a 3 px
        blur; 512 portraits in this look read 2.1 / 0.45 for sleek hair and plain cloth to 4.3 / 0.65 for curls and knits:
        compare like with like) and the paper's tooth on bare paper (fine std of luminance in the box, default the top
        left corner; the look: 1.2-1.8). A garment's speck: `look.py speck`.

    python3 look.py setin  DRAWINGS.py NAME AREA[,AREA] PAINTED.png ACCEPTED.png OUT.png [soft=1.2]
        Keep accepted parts: inside the named area(s) of the drawing (reserved shapes or "masks", the same ones that kept
        the paint off) the accepted picture is laid over the painted one with a soft edge. Both pictures in the same frame.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wash                                                       # noqa: E402

sys.modules.setdefault("wash", wash)                              # so a drawings file can `from wash import ...`
BGR = {"path": (230, 120, 0), "area": (255, 255, 255), "lift": (0, 230, 255), "stroke": (0, 140, 255), "pencil": (220, 0, 220), "brush": (60, 200, 60)}


def split(args):
    """Positional arguments and key=value options."""
    pos = [a for a in args if "=" not in a]
    opt = dict(a.split("=", 1) for a in args if "=" in a)
    return pos, opt


def region(im, box, scale):
    x0, y0, x1, y1 = box
    c = im[max(y0, 0):y1, max(x0, 0):x1]
    return cv2.resize(c, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA)


def label(im, text, at, colour=(0, 0, 0)):
    cv2.putText(im, text, at, cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(im, text, at, cv2.FONT_HERSHEY_SIMPLEX, 0.36, colour, 1, cv2.LINE_AA)


def grid(src, out, box, scale=2.0, step=20):
    x0, y0, x1, y1 = box
    c = region(cv2.imread(src), box, scale)
    clean = c.copy()
    for v0, v1, horizontal in ((x0, x1, False), (y0, y1, True)):
        for v in range((v0 // step + 1) * step, v1, step):
            p = int((v - v0) * scale)
            major = v % (step * 5) == 0
            a, b = ((0, p), (c.shape[1], p)) if horizontal else ((p, 0), (p, c.shape[0]))
            cv2.line(c, a, b, (0, 0, 255) if major else (255, 200, 0), 1)
    c = cv2.addWeighted(c, 0.45, clean, 0.55, 0)                  # thin lines: the picture stays readable under them
    for v0, v1, horizontal in ((x0, x1, False), (y0, y1, True)):
        for v in range((v0 // step + 1) * step, v1, step):
            p = int((v - v0) * scale)
            if v % (step * 5) == 0 or scale * step >= 36:
                label(c, str(v), (2, p - 3) if horizontal else (p + 2, 11), (0, 0, 200) if v % (step * 5) == 0 else (110, 80, 0))
    cv2.imwrite(out, c)


def shapes(src, out, mask, box=None, scale=1.5, blurs=(1.5, 7.0)):
    im = cv2.imread(src).astype(np.float32)
    m = cv2.resize(cv2.imread(mask, cv2.IMREAD_GRAYSCALE), im.shape[1::-1]) > 127
    l = im @ np.array([0.11, 0.59, 0.3], np.float32)
    lev = np.percentile(cv2.GaussianBlur(l, (0, 0), max(blurs))[m], (12, 35, 65))            # one set of steps for every panel
    ys, xs = np.nonzero(m)
    box = box or (int(xs.min()) - 10, int(ys.min()) - 10, int(xs.max()) + 10, int(ys.max()) + 10)
    tmp, panels = str(Path(out).with_suffix(".flat.png")), []
    for blur in blurs:
        b = cv2.GaussianBlur(l, (0, 0), blur)
        flat = np.full(im.shape, 255, np.uint8)
        for i, c in enumerate(((45, 60, 45), (95, 120, 95), (150, 175, 145), (215, 228, 205))):
            flat[m & (np.digitize(b, lev) == i)] = c
        cv2.imwrite(tmp, flat)
        grid(tmp, tmp, box, scale)
        panels.append(cv2.imread(tmp))
        label(panels[-1], f"blur {blur:g}: " + ("the big shapes" if blur >= 4 else "edge lights, cast shadows, which edge is hard"), (6, panels[-1].shape[0] - 8), (0, 0, 160))
    Path(tmp).unlink()
    cv2.imwrite(out, np.hstack(panels))
    print("luminance steps at", " / ".join(str(int(v)) for v in lev))


def placed(d, parts):
    """The drawing's layers as plain grid layers (head units and parts resolved), with their numbers."""
    sheet = wash.Sheet(d["frame"], 64, parts=parts)
    sheet.eyes = d.get("eyes")
    return [(i, sheet.place(l)) for i, l in enumerate(d["layers"])]


def paths(drawings, name, src, out, box=None, scale=2.0, layers=None, kinds=None):
    ds, parts = wash.load(drawings)
    d = ds[name]
    if box is None:
        x0, y0, *wh = d["frame"]
        box = (int(x0), int(y0), int(x0 + wh[0]), int(y0 + wh[-1]))
    lo, hi = (int(v) for v in layers.split("-")) if layers else (0, 10 ** 9)
    kinds = set(kinds.split(",")) if kinds else set(BGR)
    im = region(cv2.imread(src), box, scale)
    to = lambda pts: (np.asarray(pts, float) - box[:2]) * scale
    for i, l in placed(d, parts):
        key = next((k for k in ("path", "stroke", "pencil", "brush") if k in l), None)
        if key is None or not lo <= i <= hi:
            continue
        if key == "brush":                                        # a wet session: every stroke's two sides, a dot where the brush was set down
            for st in l["brush"] if "brush" in kinds else ():
                st = st if isinstance(st, dict) else {"path": st}
                c = wash.resample(to(wash.flow(st["path"], closed=False)), 2.0)
                w = np.atleast_1d(st.get("w", l.get("w", 12)))
                half = np.interp(np.linspace(0, 1, len(c)), np.linspace(0, 1, len(w)), w)[:, None] * scale / 2 * wash.normals(c)
                cv2.polylines(im, [np.round((c + half) * 16).astype(np.int32), np.round((c - half) * 16).astype(np.int32)], False, BGR["brush"], 1, cv2.LINE_AA, 4)
                cv2.circle(im, tuple(np.round(c[0]).astype(int)), 3, BGR["brush"], -1, cv2.LINE_AA)
            if "brush" in kinds and l["brush"]:
                st = l["brush"][0]
                q = to((st["path"] if isinstance(st, dict) else st)[0][:2])
                label(im, str(i) + (" " + l["name"] if l.get("name") else ""), (int(q[0]) + 4, int(q[1]) - 4), tuple(int(v * 0.6) for v in BGR["brush"]))
            continue
        kind = "lift" if "lift" in l else key if (key != "path" or "wash" in l) else "area"
        if kind not in kinds:
            continue
        col = BGR[kind]
        pieces = l[key] if isinstance(l[key][0], list) else [l[key]]
        for piece in pieces:
            c = to(wash.flow(piece, closed=key == "path"))
            cv2.polylines(im, [np.round(c * 16).astype(np.int32)], key == "path", col, 1, cv2.LINE_AA, 4)
            if l.get("feather"):                                  # ticks towards the side the fold dies away to
                c = wash.resample(c, 1.0)
                w = l.get("w", 3)
                w = np.interp(np.linspace(0, 1, len(c)), l.get("at", np.linspace(0, 1, np.size(w))), np.atleast_1d(w)) * scale * l["feather"]
                n = wash.normals(c)
                for j in range(0, len(c), max(int(7 * scale), 1)):
                    cv2.line(im, tuple(np.round(c[j]).astype(int)), tuple(np.round(c[j] + n[j] * w[j]).astype(int)), col, 1, cv2.LINE_AA)
            if len(pieces) <= 12:
                for n in piece:
                    q = tuple(np.round(to(n[:2])).astype(int))
                    if "w" in n[2:]:
                        cv2.circle(im, q, 4, col, 1, cv2.LINE_AA)
                    elif "c" in n[2:]:
                        cv2.rectangle(im, (q[0] - 2, q[1] - 2), (q[0] + 2, q[1] + 2), col, -1)
                    else:
                        cv2.circle(im, q, 2, col, -1, cv2.LINE_AA)
        q = to(pieces[0][0][:2])
        label(im, str(i) + (" " + l["name"] if l.get("name") else ""), (int(q[0]) + 4, int(q[1]) - 4), tuple(int(v * 0.6) for v in col))
    cv2.imwrite(out, im)


def chroma(c):
    lab = cv2.cvtColor(np.float32([[np.asarray(c, np.float32) / 255]]), cv2.COLOR_RGB2Lab)[0, 0]
    return float(np.hypot(lab[1], lab[2]))


def values(images, box=None, mask=None, at=None, areas=None, frame=None):
    m = cv2.imread(mask, cv2.IMREAD_GRAYSCALE) > 127 if mask else None
    hexc = lambda c: "#%02X%02X%02X" % tuple(int(v) for v in c)
    lum = np.array([0.3, 0.59, 0.11], np.float32)
    tag = lambda f: "/".join(Path(f).resolve().parts[-2:])
    for f in images:
        im = cv2.imread(f)
        assert im is not None, f"cannot read {f}"
        im = im[..., 2::-1].astype(np.float32)
        if at:                                                    # the colour at points: a 9 px patch round each
            got = [im[max(y - 4, 0):y + 5, max(x - 4, 0):x + 5].reshape(-1, 3) for x, y in at]
            print(f"{tag(f)}: " + "  ".join(f"({x},{y}) " + (f"{hexc(c.mean(0))} {int(c.mean(0) @ lum)}" if len(c) else "outside") for (x, y), c in zip(at, got)))
            continue
        sel = np.ones(im.shape[:2], bool) if m is None else cv2.resize(m.astype(np.uint8), im.shape[1::-1]) > 0
        if box:
            keep = np.zeros_like(sel)
            keep[box[1]:box[3], box[0]:box[2]] = True
            sel &= keep
        cut = (lambda v: v[frame[1]:frame[1] + frame[-1], frame[0]:frame[0] + frame[2]]) if frame else (lambda v: v)
        for name, a in ([(n, cv2.resize(cut(v), im.shape[1::-1]) > 0.5) for n, v in np.load(areas).items()] if areas else [("", None)]):
            px = im[sel if a is None else sel & a]
            if not len(px):
                continue
            pct = np.percentile(px @ lum, (1, 5, 25, 50, 75, 95)).round().astype(int)
            print(f"{tag(f)}{' ' + name if name else ''}: luminance at 1/5/25/50/75/95 % = {' '.join(map(str, pct))}   mean {hexc(px.mean(0))} chroma {chroma(px.mean(0)):.0f}")


def texture(images, box=None):
    lum = np.array([0.11, 0.59, 0.3], np.float32)
    for f in images:
        l = cv2.imread(f).astype(np.float32) @ lum
        x0, y0, x1, y1 = box or (10, 10, 90, 90)
        c = l[y0:y1, x0:x1]
        d = [np.abs(cv2.Laplacian(cv2.GaussianBlur(l, (0, 0), s), cv2.CV_32F)).mean() for s in (1, 3)]
        print(f"{'/'.join(Path(f).resolve().parts[-2:])}: detail {d[0]:.2f} / {d[1]:.2f}   paper tooth in ({x0},{y0},{x1},{y1}): fine std {(c - cv2.GaussianBlur(c, (0, 0), 6)).std():.2f}, mean luminance {c.mean():.0f}")


LUM_BGR = np.array([0.11, 0.59, 0.3], np.float32)


def lum_of(f, blur=0.0):
    im = cv2.imread(str(f))
    assert im is not None, f"cannot read {f}"
    l = im.astype(np.float32) @ LUM_BGR
    return cv2.GaussianBlur(l, (0, 0), blur) if blur else l


def table(a, box, step, cell):
    """Rows of numbers on a grid over `box` of the array `a`, coordinates along the top and the side."""
    x0, y0, x1, y1 = box
    xs, ys = range(x0 + step // 2, min(x1, a.shape[1]), step), range(y0 + step // 2, min(y1, a.shape[0]), step)
    print("      " + "".join(f"{x:4d}" for x in xs))
    for y in ys:
        print(f"{y:5d} " + "".join(cell(a[y, x]) for x in xs))


def tones(img, box=None, step=24, blur=5.0):
    l = lum_of(img, blur)
    table(l, box or (0, 0, l.shape[1], l.shape[0]), step, lambda v: f"{int(v):4d}")


def on_grid(painted, source, frame, blur):
    """Painted and source luminance on the source's grid, cut to the frame the painted picture shows."""
    S = lum_of(source, blur)
    x0, y0, w, h = frame or (0, 0, S.shape[1], S.shape[0])
    P = cv2.imread(str(painted))
    assert P is not None, f"cannot read {painted}"
    assert abs(P.shape[1] / P.shape[0] - w / h) < 0.02, f"{painted} is {P.shape[1]} x {P.shape[0]}: not the frame {w} x {h} of the source (frame=x0,y0,w,h)"
    P = cv2.GaussianBlur(cv2.resize(P, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) @ LUM_BGR, (0, 0), blur)
    full = np.full(S.shape, np.nan, np.float32)
    full[y0:y0 + h, x0:x0 + w] = P[:S.shape[0] - y0, :S.shape[1] - x0]
    return full, S


def diff(painted, source, box=None, step=40, blur=6.0, frame=None, areas=None, mask=None):
    P, S = on_grid(painted, source, frame, blur)
    D = P - S
    x0, y0, w, h = frame or (0, 0, S.shape[1], S.shape[0])
    table(D, box or (x0, y0, x0 + w, y0 + h), step, lambda v: "    " if np.isnan(v) else f"{int(v):4d}" if abs(v) >= 8 else "   .")
    named = [(k, v) for k, v in np.load(areas).items()] if areas else []
    if mask:
        named.append((Path(mask).stem, cv2.imread(mask, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255))
    ys, xs = np.mgrid[10:S.shape[0]:20, 10:S.shape[1]:20]
    for name, m in named or [("the frame", np.ones(S.shape, np.float32))]:
        m = cv2.resize(m.astype(np.float32), S.shape[::-1])
        d = D[ys, xs][(m[ys, xs] > 0.5) & ~np.isnan(D[ys, xs])]
        if len(d) >= 5:
            print(f"{name:9s} {len(d):5d} points   within 15: {100 * (abs(d) < 15).mean():3.0f} %   within 25: {100 * (abs(d) < 25).mean():3.0f} %   painted - source {d.mean():+.0f}")


def speck(images, mask=None, box=None, paper=None, win=24):
    import regions
    for f in images:
        l = lum_of(f)
        pap = float(np.array(wash.hexrgb(paper) if paper else regions.read(f)[1], np.float32) @ (0.3, 0.59, 0.11))
        m = np.ones(l.shape, np.float32) if not mask else (cv2.resize(cv2.imread(mask, cv2.IMREAD_GRAYSCALE), l.shape[::-1]) > 127).astype(np.float32)
        if box:
            keep = np.zeros_like(m)
            keep[box[1]:box[3], box[0]:box[2]] = 1
            m *= keep
        fine, mid = l - cv2.GaussianBlur(l, (0, 0), 6), cv2.GaussianBlur(l, (0, 0), 3)
        rows = [(l[w].mean(), fine[w].std(), mid[w].std()) for y in range(0, l.shape[0] - win + 1, win // 2) for x in range(0, l.shape[1] - win + 1, win // 2)
                for w in [(slice(y, y + win), slice(x, x + win))] if m[w].mean() > 0.99]
        tag = "/".join(Path(f).resolve().parts[-2:])
        if len(rows) < 9:
            print(f"{tag}: the area holds only {len(rows)} windows of {win} px: give a bigger box, or win=12")
            continue
        r = np.array(rows)
        calm = r[r[:, 2] / r[:, 0] <= np.percentile(r[:, 2] / r[:, 0], 33)]            # the flat patches: no fold, no edge in the window
        print(f"{tag}: flat patches (the calmest third of {len(r)} windows of {win} px), paper {pap:.0f}")
        for lo, hi in ((0, 33), (33, 67), (67, 100)):
            a, b = np.percentile(calm[:, 0], (lo, hi))
            c = calm[(calm[:, 0] >= a) & (calm[:, 0] <= b)]
            tone, sp = float(np.median(c[:, 0])), float(100 * np.median(c[:, 1] / c[:, 0]))
            D = max(np.log(pap / tone), 1e-3)
            print(f"  at tone {tone:3.0f}: speck {sp:4.1f} %   speck / D {sp / D:4.1f}   toned(KIND, {tone:.0f}, PAPER, speck={sp:.1f})")


def chosen(d, only=None, upto=None):
    """Layer numbers from `only=12,14-16,wash` (numbers, ranges, names) or `upto=15`."""
    if upto is not None:
        return set(range(int(upto) + 1))
    pick = set()
    for part in only.split(","):
        if part.replace("-", "").isdigit():
            lo, hi = (int(v) for v in (part.split("-") + [part])[:2])
            pick |= set(range(lo, hi + 1))
        else:
            hit = {i for i, l in enumerate(d["layers"]) if l.get("name") == part}
            assert hit, f'no layer is named "{part}"'
            pick |= hit
    return pick


def layers(drawings, name, out, only=None, upto=None):
    ds, parts = wash.load(drawings)
    pick = chosen(ds[name], only, upto)
    cv2.imwrite(out, wash.draw(ds[name], parts, only=pick))
    print("painted layers", " ".join(str(i) for i in sorted(pick) if i < len(ds[name]["layers"])))


def holes(drawings, name, out=None, pick=None, least=30.0):
    ds, parts = wash.load(drawings)
    d, seen = ds[name], []
    img = wash.draw(d, parts, watch=seen)
    x0, y0, *wh = d["frame"]
    k = img.shape[1] / wh[0]                                      # output px per grid unit; the canvas is wash.SS times that
    want = chosen(d, pick) if pick else None
    marks = np.zeros((img.shape[0] * wash.SS, img.shape[1] * wash.SS), np.float32)
    H, W = marks.shape
    for i, (layer, m, keep) in zip([i for i, l in enumerate(d["layers"]) if "brush" in l], seen):
        if (want is None and not layer.get("name")) or (want is not None and i not in want):
            continue
        area, open_ = keep > 0.5, (keep > 0.5) & (m < 0.5)
        n, lab, stats, mids = cv2.connectedComponentsWithStats(open_.astype(np.uint8), connectivity=8)
        found = []
        for j in range(1, n):
            x, y, w, h, a = stats[j]
            size = a / (k * wash.SS) ** 2
            if size < least:
                continue
            edge = x <= 0 or y <= 0 or x + w >= W or y + h >= H
            found.append((size, mids[j][0], mids[j][1], w, h, edge or a > 0.25 * area.sum()))
            if not found[-1][-1]:
                marks[lab == j] = 1
        print(f'layer {i} "{layer.get("name", "")}": {100 * open_.sum() / max(area.sum(), 1):.1f} % of its area not covered' + ("" if found else "; no hole of that size"))
        for size, cx, cy, w, h, edge in sorted(found, reverse=True):
            to = lambda v, o: v / (k * wash.SS) + o
            print(f"    {'open (the frame, a hem)' if edge else 'HOLE':24s} at ({to(cx, x0):.0f}, {to(cy, y0):.0f})   {w / (k * wash.SS):.0f} x {h / (k * wash.SS):.0f}   {size:.0f} units²")
    if out:
        red = cv2.resize(marks, img.shape[1::-1], interpolation=cv2.INTER_AREA)[..., None]
        cv2.imwrite(out, np.clip(img * (1 - 0.75 * red) + np.array([40, 40, 255], np.float32) * 0.75 * red, 0, 255).astype(np.uint8))


def frame_of(portrait, sheet):
    p, s = cv2.imread(portrait, cv2.IMREAD_GRAYSCALE), cv2.imread(sheet, cv2.IMREAD_GRAYSCALE)
    assert p is not None and s is not None, "cannot read the pictures"
    f = 400 / max(s.shape)                                        # search small, then settle at full size
    small = cv2.resize(s, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    best = (-1, 0, 0, 0)
    for size in np.arange(0.25, 1.001, 0.01) * min(small.shape):
        t = cv2.resize(p, (int(size), int(size)), interpolation=cv2.INTER_AREA)
        r = cv2.matchTemplate(small, t, cv2.TM_CCOEFF_NORMED)
        _, v, _, at = cv2.minMaxLoc(r)
        best = max(best, (v, at[0] / f, at[1] / f, size / f))
    v, x, y, size = best
    for size2 in np.arange(size - 6, size + 6.5, 1):              # at full size, round the best
        t = cv2.resize(p, (int(size2), int(size2)), interpolation=cv2.INTER_AREA)
        xa, ya = max(int(x) - 8, 0), max(int(y) - 8, 0)
        win = s[ya:ya + int(size2) + 16, xa:xa + int(size2) + 16]
        if win.shape[0] < t.shape[0] or win.shape[1] < t.shape[1]:
            continue
        r = cv2.matchTemplate(win, t, cv2.TM_CCOEFF_NORMED)
        _, v2, _, at = cv2.minMaxLoc(r)
        best = max(best, (v2, xa + at[0], ya + at[1], int(size2)))
    v, x, y, size = best
    print(f'"frame": ({x:.0f}, {y:.0f}, {size:.0f})   r = {v:.3f}' + ("" if v > 0.9 else "   (under 0.9: not found; is this the portrait of that sheet?)"))


def ladder(pos, opt):
    hexc = lambda c: "#%02X%02X%02X" % tuple(int(round(float(v))) for v in c)
    if "lit" in opt:                                              # read off a source picture, on its own paper
        import regions
        rgb, paper = regions.read(pos[0])
        pick = lambda k: rgb[max(int(opt[k].split(",")[1]) - 4, 0):int(opt[k].split(",")[1]) + 5, max(int(opt[k].split(",")[0]) - 4, 0):int(opt[k].split(",")[0]) + 5].reshape(-1, 3).mean(0)
        cols, on = [hexc(pick(k)) for k in ("lit", "shadow", "dark") if k in opt], hexc(paper)
    else:
        cols, on = pos, opt.get("on")
    g = wash.ladder(*cols, on=on, paper=opt.get("paper", wash.PAPER))
    mult = lambda c: float(np.array(wash.hexrgb(c), float) @ (0.3, 0.59, 0.11) / (np.array(wash.PAPER, float) @ (0.3, 0.59, 0.11)))
    print(f"source: lit {cols[0]}, shadow {cols[1]}" + (f", dark {cols[2]}" if len(cols) > 2 else "") + (f", on paper {on}" if on else ""))
    print("LOCAL, TURN, SHADE, DEEP, DARK, RIB = ladder(" + ", ".join(f'"{c}"' for c in cols) + (f', on="{on}"' if on else "") + (f', paper="{opt["paper"]}"' if "paper" in opt else "") + ")     # from wash import ladder")
    print("  = " + ", ".join(f'"{c}"' for c in g))
    print("  LOCAL is the wash on bare paper; the others multiply what is under them: x " + ", ".join(f"{mult(c):.2f}" for c in g[1:]))


def area(drawings, name, areas):
    """The named area(s) of a drawing as one mask at the picture's size (only the layers that define names are run)."""
    ds, parts = wash.load(drawings)
    d = ds[name]
    paper = wash.hexrgb(d["paper"]) if isinstance(d.get("paper"), str) else d.get("paper", wash.PAPER)
    sheet = wash.Sheet(d["frame"], d.get("out", wash.OUT), paper, d.get("seed", 1), parts)
    sheet.eyes = d.get("eyes")
    sheet.pin(None, d.get("masks"))
    for l in d["layers"]:
        if l.get("name") and "path" in l:
            sheet.paint({k: v for k, v in l.items() if k not in ("wash", "lift")})
    m = np.clip(sum(sheet.masks[a] for a in areas.split(",")), 0, 1)
    return cv2.resize(m, (sheet.W, sheet.H), interpolation=cv2.INTER_AREA)


def setin(drawings, name, areas, painted, accepted, out, soft=1.2):
    a = cv2.GaussianBlur(area(drawings, name, areas), (0, 0), soft)[..., None]
    p, k = cv2.imread(painted).astype(np.float32), cv2.imread(accepted).astype(np.float32)
    assert p.shape == k.shape == a.shape[:2] + (3,), f"painted {p.shape}, accepted {k.shape} and the drawing {a.shape} must share one frame"
    cv2.imwrite(out, np.clip(p * (1 - a) + k * a + 0.5, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    cmd, (pos, opt) = (sys.argv[1] if len(sys.argv) > 1 else ""), split(sys.argv[2:])
    need = {"grid": 6, "shapes": 2, "paths": 4, "values": 1, "ladder": 1, "glaze": 2, "texture": 1, "setin": 6, "tones": 1, "diff": 2, "over": 2, "speck": 1, "layers": 3, "holes": 2, "frame": 2}
    if cmd not in need or len(pos) < need[cmd]:
        sys.exit(__doc__)
    num = lambda v: tuple(int(float(x)) for x in v)
    scale = float(opt.get("scale", 2))
    if cmd == "grid":
        grid(pos[0], pos[1], num(pos[2:6]), scale, int(opt.get("step", 20)))
    elif cmd == "shapes" and "mask" in opt:
        shapes(pos[0], pos[1], opt["mask"], num(pos[2:6]) if len(pos) >= 6 else None, float(opt.get("scale", 1.5)), tuple(float(v) for v in opt.get("blur", "1.5,7").split(",")))
    elif cmd == "shapes":
        sys.exit(__doc__)
    elif cmd == "paths":
        paths(pos[0], pos[1], pos[2], pos[3], num(pos[4:8]) if len(pos) >= 8 else None, scale, opt.get("layers"), opt.get("kinds"))
    elif cmd == "values":
        values(pos, num(opt["box"].split(",")) if "box" in opt else None, opt.get("mask"),
               [num(p.split(",")) for p in opt["at"].split("/")] if "at" in opt else None, opt.get("areas"),
               num(opt["frame"].split(",")) if "frame" in opt else None)
    elif cmd == "texture":
        texture(pos, num(opt["box"].split(",")) if "box" in opt else None)
    elif cmd == "tones":
        tones(pos[0], num(pos[1:5]) if len(pos) >= 5 else None, int(opt.get("step", 24)), float(opt.get("blur", 5)))
    elif cmd == "diff":
        diff(pos[0], pos[1], num(pos[2:6]) if len(pos) >= 6 else None, int(opt.get("step", 40)), float(opt.get("blur", 6)),
             num(opt["frame"].split(",")) if "frame" in opt else None, opt.get("areas"), opt.get("mask"))
    elif cmd == "speck" and ("mask" in opt or "box" in opt):
        speck(pos, opt.get("mask"), num(opt["box"].split(",")) if "box" in opt else None, opt.get("paper"), int(opt.get("win", 24)))
    elif cmd == "speck" or (cmd == "layers" and not ("only" in opt or "upto" in opt)):
        sys.exit(__doc__)
    elif cmd == "layers":
        layers(pos[0], pos[1], pos[2], opt.get("only"), opt.get("upto"))
        print("wrote", pos[2])
    elif cmd == "holes":
        holes(pos[0], pos[1], pos[2] if len(pos) > 2 else None, opt.get("layers"), float(opt.get("least", 30)))
        print("wrote", pos[2]) if len(pos) > 2 else None
    elif cmd == "frame":
        frame_of(pos[0], pos[1])
    elif cmd == "over":
        under, upper, paper = (np.array(wash.hexrgb(v), np.float32) for v in (pos[0], pos[1], pos[2] if len(pos) > 2 else "#%02X%02X%02X" % wash.PAPER))
        got = np.clip(under * upper / paper, 0, 255)
        lab = lambda c: cv2.cvtColor(np.float32([[c / 255]]), cv2.COLOR_RGB2Lab)[0, 0]
        tone = lambda c: float(c @ np.array([0.3, 0.59, 0.11], np.float32))
        hue = float(np.hypot(*(lab(got) - lab(upper))[1:]))
        near, dark = tone(under) >= 0.92 * tone(paper), tone(upper) < 80
        ok = (near and hue < 2.5) or (dark and hue < 6)            # on a dark a small shift of hue cannot be seen
        print("#%02X%02X%02X" % tuple(int(v) for v in got) + f"   {tone(upper) - tone(got):.0f} levels darker than {pos[1]} alone, its hue moved by {hue:.1f}   (the lower wash is {100 * tone(under) / tone(paper):.0f} % of the paper)")
        print("-> the lighter one may run under" if ok else "-> shared nodes: neither runs under the other (the lower one would darken and dirty the upper)")
    elif cmd == "ladder":
        ladder(pos, opt)
    elif cmd == "setin":
        setin(*pos[:6], soft=float(opt.get("soft", 1.2)))
    elif cmd == "glaze":
        a, b, paper = (np.array(wash.hexrgb(v), float) for v in (pos[0], pos[1], pos[2] if len(pos) > 2 else "#%02X%02X%02X" % wash.PAPER))
        print("#%02X%02X%02X" % tuple(int(v) for v in np.clip(paper * b / np.maximum(a, 1), 0, 255)))
    if cmd in ("grid", "shapes", "paths", "setin"):
        print("wrote", pos[3] if cmd == "paths" else pos[5] if cmd == "setin" else pos[1])
```
