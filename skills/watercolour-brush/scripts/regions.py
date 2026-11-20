#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy==2.5.5", "opencv-python-headless==5.1.0.95"]
# ///
"""Areas and underdrawing from a source picture: steps 1 and 2 of the order of work, a few seconds each.

    uv run regions.py propose SOURCE OUT_DIR [k=9]
        Cuts the source into regions by colour and place and writes OUT_DIR/regions.png: every region tinted, outlined
        and numbered, source coordinates along the border. Prints one line per region (id, a guess of what it is, its box,
        its share of the picture, its colour) and writes the guesses as OUT_DIR/areas.json, the file you correct.
        (An areas.json that is already there is kept: delete it to start again.)

    uv run regions.py build SOURCE OUT_DIR/areas.json
        Your areas -> masks.npz, areas.png (read it at 1:1) and one mask-NAME.png each; the underdrawing with its
        corrections -> under.npy, underdrawing.png. Prints per area what the source measures there, the row of
        references/starting-values.md it falls in and the gains used. Correct areas.json, build again, look again.

areas.json:

    {"paper": "#FBF6E3",                         the source's own paper as measured (change it only if it is wrong)
     "approved": false,                          true: the source is already a finished picture in this look and you paint the
                                                 same picture again: no area is pushed (gains 1), and the sheet takes this paper
     "areas": {                                  where two overlap, the one written first wins
       "features": {"kind": "features", "auto": true, "add": [[[418,366],[474,368],[446,380]]]},
       "skin":  {"kind": "skin",  "regions": [3, 8], "lines": 0.38},
       "hair":  {"kind": "hair",  "regions": [2], "within": [[[290,140],[740,140],[740,530],[290,530]]]},
       "card":  {"kind": "cloth", "regions": [4, 5], "at": [[600, 900]], "cut": [], "holes": true},
       "shirt": {"kind": "cloth", "regions": [7], "gain": [1.3, 0.8, 1.2, 0.0]}}}

    "regions"   ids read off regions.png        "at"      points: the region under each is taken too
    "add"/"cut" polygons in source px, added to / cut out of the area (a curve through the points; "c" third value: a corner)
    "within"    polygons: the regions count only inside them (cut by place first, then by colour)
    "holes"     true fills holes (buttons and a brooch belong to the cardigan)
    "kind"      skin | hair | cloth | features. "features" (eyes, nose, mouth, anything to keep exactly as drawn) takes no
                pixels from the others: it is a mask of its own, and skin keeps its lines there. "auto": the dark blobs in the face
    "gain"      [gain, colour, curve, warm] instead of the table's row (fuller(), below). Near the border of two rows `build`
                mixes them, so the gains do not jump when a polygon moves a few pixels
    "lines"     skin only: how much of the thin dark lines is mixed back after they are closed over (0.38; 0 = none, 1 = all)

In a drawings file:  UNDER = np.load("under.npy");  MASKS = dict(np.load("masks.npz"))  ->  {"under": UNDER, "masks": MASKS, ...}.
Both are float32 at the source's size: masks 0..1 (1: in the area), under.npy what the paint lets through per channel (0..1, not a
picture). They cover the drawing's FRAME: for a frame that is only part of the source (a body, a draft) cut them the same way,
v[y0:y0 + h, x0:x0 + w]; given whole, they are squeezed into the frame.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wash                                                       # noqa: E402

LUM = np.array([0.3, 0.59, 0.11], np.float32)
hexc = lambda c: "#%02X%02X%02X" % tuple(int(round(float(v))) for v in c)
ell = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(max(r, 1)) + 1,) * 2)


def read(src, paper=None):
    """-> the source as RGB floats, and its paper colour (the lighter half of its border unless given)."""
    im = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
    assert im is not None, f"cannot read {src}"
    if im.ndim == 2:
        im = np.dstack([im] * 3)
    rgb = im[..., 2::-1].astype(np.float32)
    if im.shape[2] == 4:                                          # a cut-out: lay it on white
        a = im[..., 3:].astype(np.float32) / 255
        rgb = rgb * a + 255 * (1 - a)
    if paper is None:
        h, w = rgb.shape[:2]
        b = max(4, int(0.03 * min(h, w)))
        edge = np.vstack([rgb[:b].reshape(-1, 3), rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])   # not the bottom: figures run off it
        paper = np.median(edge[edge.mean(1) >= np.percentile(edge.mean(1), 50)], 0)
    else:
        paper = np.array(wash.hexrgb(paper) if isinstance(paper, str) else paper, np.float32)
    return rgb, paper.astype(np.float32)


def poly(shape, nodes, soft=0.0):
    """A filled curve through nodes (source px) as a mask of `shape`."""
    m = np.zeros(shape, np.uint8)
    cv2.fillPoly(m, [np.round(wash.flow([tuple(n) for n in nodes]) * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    m = m.astype(np.float32) / 255
    return cv2.GaussianBlur(m, (0, 0), soft) if soft else m


def fuller(D, gain=1.0, colour=1.0, curve=1.0, warm=0.0):
    """Density made fuller: more pigment (gain; curve > 1 deepens the darks more than the lights), more or less colour
    (the spread between the channels), and a push towards warm (less blue let through)."""
    m = D.mean(-1, keepdims=True)
    out = (m + colour * (D - m)) * gain * (np.maximum(m, 1e-4) / 0.5) ** (curve - 1)
    return np.clip(out + warm * m * np.array([-0.5, 0.0, 0.5], np.float32), 0, None)


# ---------------------------------------------------------------- step 1: regions

def lab_of(rgb):
    return cv2.cvtColor(np.clip(rgb / 255, 0, 1).astype(np.float32), cv2.COLOR_RGB2Lab)


def regions(rgb, paper, k=9, small=256):
    """-> label map at full size (0 = bare paper), per-label rows (id, guess, box, share, colour)."""
    h, w = rgb.shape[:2]
    s = small / w
    sm = cv2.resize(rgb, (small, int(round(h * s))), interpolation=cv2.INTER_AREA)
    lab = cv2.bilateralFilter(lab_of(sm), 5, 6, 3)
    hh, ww = lab.shape[:2]
    away = np.linalg.norm((lab - lab_of(paper[None, None])[0, 0]) * (0.6, 1, 1), axis=-1)
    bare = (cv2.GaussianBlur(away, (0, 0), 1.0) < 5).astype(np.uint8)
    n, cc, st, _ = cv2.connectedComponentsWithStats(bare, connectivity=8)
    rim = np.unique(np.concatenate([cc[0], cc[:, 0], cc[:, -1]]))
    paperish = np.isin(cc, [i for i in range(1, n) if i in rim or st[i, 4] > 0.01 * hh * ww])
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    feat = np.dstack([0.45 * lab[..., 0], lab[..., 1], lab[..., 2], 0.05 * xx, 0.05 * yy])     # hue before lightness: a garment's shadow stays with it
    pts = feat[~paperish]
    cv2.setRNGSeed(1)
    _, _, cen = cv2.kmeans(pts[np.random.default_rng(1).choice(len(pts), min(len(pts), 30000), replace=False)], k, None,
                           (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.3), 3, cv2.KMEANS_PP_CENTERS)
    cl = np.full((hh, ww), -1, np.int32)
    cl[~paperish] = np.argmin(((pts[:, None] - cen[None]) ** 2).sum(-1), 1)
    cl = cv2.medianBlur((cl + 1).astype(np.uint8), 5).astype(np.int32) - 1
    lab_map, nreg = np.zeros((hh, ww), np.int32), 0                # connected pieces of each cluster
    for c in range(k):
        n, cc = cv2.connectedComponents((cl == c).astype(np.uint8), connectivity=4)
        lab_map[cc > 0] = cc[cc > 0] + nreg
        nreg += n - 1
    least = 0.0025 * hh * ww                                       # crumbs join the neighbour nearest in colour
    for _ in range(40):
        ids, counts = np.unique(lab_map[lab_map > 0], return_counts=True)
        tiny = ids[counts < least]
        if not len(tiny):
            break
        mean = {i: lab[lab_map == i].mean(0) for i in ids}
        for i in tiny[np.argsort(counts[counts < least])]:
            m = lab_map == i
            ring_ = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m
            near = [j for j in np.unique(lab_map[ring_]) if j != i]
            if not near:
                continue
            col = lab[m].mean(0)
            j = min(near, key=lambda j: np.linalg.norm(col - (mean[j] if j else lab_of(paper[None, None])[0, 0])) + (12 if j == 0 else 0))
            lab_map[m] = j
    ids, counts = np.unique(lab_map[lab_map > 0], return_counts=True)
    order = ids[np.argsort(-counts)]
    renum = np.zeros(lab_map.max() + 1, np.int32)
    renum[order] = np.arange(1, len(order) + 1)
    lab_map = renum[lab_map]
    nreg = len(order)
    # ---- full size: the small map enlarged; along its borders every pixel goes to the neighbouring region nearest in colour
    big = cv2.GaussianBlur(lab_of(rgb), (0, 0), max(0.8, 0.0012 * w))
    means = np.vstack([lab_of(paper[None, None])[0, 0]] + [lab[lab_map == i].mean(0) for i in range(1, nreg + 1)]).astype(np.float32)
    best, bestd = None, None
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            sh = cv2.resize(np.roll(np.roll(lab_map, dy, 0), dx, 1).astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
            d = ((big - means[sh]) ** 2 * (0.5, 1, 1)).sum(-1) + (0 if (dx == 0 and dy == 0) else 30)   # stay, unless clearly the other
            if best is None:
                best, bestd = sh, d
            else:
                take = d < bestd
                best, bestd = np.where(take, sh, best), np.where(take, d, bestd)
    full = cv2.medianBlur(best.astype(np.uint8), 5)
    return full, guesses(full, lab_of(rgb), paper)


def guesses(full, lab, paper):
    """What each region probably is, by colour and place: skin, hair, cloth1.., behind. A guess, to be corrected."""
    h, w = full.shape
    ids = [i for i in np.unique(full) if i > 0]
    rows = {}
    for i in ids:
        m = full == i
        ys, xs = np.nonzero(m)
        c = lab[m].mean(0)
        edge = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~m
        rows[i] = dict(id=int(i), box=(int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), share=float(m.mean()), lab=c,
                       mid=(float(xs.mean()), float(ys.mean())), paper=float((full[edge] == 0).mean()) if edge.any() else 0.0,
                       hue=float(np.degrees(np.arctan2(c[2], c[1]))), chroma=float(np.hypot(c[1], c[2])), guess="cloth")
    fig = full > 0
    top = np.nonzero(fig.any(1))[0].min() if fig.any() else 0
    warm = [r for r in rows.values() if 25 < r["hue"] < 75 and 9 < r["chroma"] < 48 and r["lab"][0] > 45]
    face = max((r for r in warm if r["mid"][1] < top + 0.5 * (h - top)), key=lambda r: r["share"], default=None)
    pl = lab_of(paper[None, None])[0, 0]
    if face is not None:
        for r in warm:
            if np.linalg.norm((r["lab"] - face["lab"]) * (0.4, 1, 1)) < 14:
                r["guess"] = "skin"
        skin = np.isin(full, [r["id"] for r in rows.values() if r["guess"] == "skin"]).astype(np.uint8)
        n, cc = cv2.connectedComponents(skin)                      # the face: the skin that hangs together with its biggest piece
        head = cc == cc[full == face["id"]][0]
        ys = np.nonzero(head.any(1))[0]
        fh = min(ys.max() - ys.min() + 1, 1.3 * head.sum(1).max())
        ring_ = cv2.dilate(head.astype(np.uint8), ell(0.3 * fh)).astype(bool)
        ring_[int(ys.min() + 0.85 * fh):] = False
        for r in rows.values():                                    # what rings the face above the chin is hair, pale or not
            if r["guess"] == "cloth" and (ring_ & (full == r["id"])).sum() > 0.3 * (full == r["id"]).sum():
                r["guess"] = "hair"
    for r in rows.values():                                        # a pale wash that lies open to the paper is behind the figure, not of it
        if r["guess"] == "cloth" and r["lab"][0] > pl[0] - 22 and r["chroma"] < 14 and r["paper"] > 0.45:
            r["guess"] = "behind"
    cloth = sorted((r for r in rows.values() if r["guess"] == "cloth"), key=lambda r: -r["share"])
    kinds = []                                                     # garments: regions of one hue are one garment, light and shadow alike
    for r in cloth:
        for j, members in enumerate(kinds):
            if min(np.linalg.norm((r["lab"] - c) * (0.5, 1, 1)) for c in members) < 10:
                members.append(r["lab"])
                r["guess"] = f"cloth{j + 1}"
                break
        else:
            kinds.append([r["lab"]])
            r["guess"] = f"cloth{len(kinds)}"
    return [rows[i] for i in ids]


def overlay(rgb, labels, names, out):
    """The source, paled, with every label tinted, outlined and named, and source coordinates along the border."""
    h, w = labels.shape
    im = (0.55 * rgb[..., ::-1] + 0.45 * 255).astype(np.float32)
    ids = [i for i in np.unique(labels) if i > 0]
    for n, i in enumerate(ids):
        m = (labels == i).astype(np.uint8)
        col = cv2.cvtColor(np.uint8([[[int(180 * ((n * 0.381966) % 1)), 200, 235]]]), cv2.COLOR_HSV2BGR)[0, 0].astype(np.float32)
        im[m > 0] = 0.62 * im[m > 0] + 0.38 * col
        cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(im, cs, -1, tuple(float(v) * 0.55 for v in col), max(1, w // 700))
    im = np.ascontiguousarray(np.clip(im, 0, 255).astype(np.uint8))
    step = 100 if w > 600 else 50
    f = max(0.4, w / 2300)
    for x in range(step, w, step):
        cv2.line(im, (x, 0), (x, 10), (0, 0, 255), 1)
        cv2.putText(im, str(x), (x + 2, 22), cv2.FONT_HERSHEY_SIMPLEX, f, (0, 0, 255), 1, cv2.LINE_AA)
    for y in range(step, h, step):
        cv2.line(im, (0, y), (10, y), (0, 0, 255), 1)
        cv2.putText(im, str(y), (12, y + 4), cv2.FONT_HERSHEY_SIMPLEX, f, (0, 0, 255), 1, cv2.LINE_AA)
    for i in ids:                                                  # the name where the region is thickest
        m = (labels == i).astype(np.uint8)
        d = cv2.distanceTransform(np.pad(m, 1), cv2.DIST_L2, 3)[1:-1, 1:-1]
        y, x = np.unravel_index(np.argmax(d), d.shape)
        t = str(names.get(i, i))
        (tw, th), _ = cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 1.3 * f, 1)
        x0, y0 = int(np.clip(x - tw / 2, 2, w - tw - 2)), int(np.clip(y + th / 2, th + 2, h - 2))
        im[y0 - th - 2:y0 + 4, x0 - 2:x0 + tw + 2] = 0.25 * im[y0 - th - 2:y0 + 4, x0 - 2:x0 + tw + 2] + 0.75 * 255
        cv2.putText(im, t, (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1.3 * f, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imwrite(str(out), im)


def propose(src, out_dir, k=9):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rgb, paper = read(src)
    full, rows = regions(rgb, paper, k)
    np.save(out / "regions.npy", full)
    overlay(rgb, full, {r["id"]: f'{r["id"]} {r["guess"]}' for r in rows}, out / "regions.png")
    lum = lambda r: int(cv2.cvtColor(np.float32([[r["lab"]]]), cv2.COLOR_Lab2RGB)[0, 0] @ LUM * 255)
    print(f"paper {hexc(paper)}   {len(rows)} regions   look at {out / 'regions.png'}")
    for r in rows:
        col = cv2.cvtColor(np.float32([[r["lab"]]]), cv2.COLOR_Lab2RGB)[0, 0] * 255
        print(f'{r["id"]:3d}  {r["guess"]:7s} box {str(r["box"]):24s} {100 * r["share"]:5.1f} %  {hexc(col)} lum {lum(r):3d}  open to paper {r["paper"]:.2f}')
    areas, kind = {"features": {"kind": "features", "auto": True, "add": []}}, lambda g: "cloth" if g.startswith("cloth") else g
    for g in sorted({r["guess"] for r in rows if r["guess"] != "behind"}, key=lambda g: (g.startswith("cloth"), g != "skin", g)):
        areas[g] = {"kind": kind(g), "regions": [r["id"] for r in rows if r["guess"] == g]}
    if not (out / "areas.json").exists():
        body = ",\n".join(f'  {json.dumps(n)}: {json.dumps(a)}' for n, a in areas.items())
        (out / "areas.json").write_text('{"paper": "%s",\n "approved": false,\n "areas": {\n%s}}\n' % (hexc(paper), body))
        print("wrote", out / "areas.json", "(rename the areas, move regions between them, add polygons; then: build)")
    else:
        print("kept the", out / "areas.json", "that is there")


# ---------------------------------------------------------------- step 2: areas as corrected, and the underdrawing

ROWS = {  # references/starting-values.md, section 2: [gain, colour, curve, warm], and what to aim for where the source is pale
    "skin, pale": ([1.25, 1.0, 1.1, 0.0], "median 178-188 where the face is lit"), "skin, full": ([1.05, 1.0, 1.0, 0.0], "median 178-188 where the face is lit; a darker skin, or a face turned from the light: as the source"),
    "hair, grey or fair, pale": ([1.45, 0.35, 1.55, 0.06], "1 % at 20-30, 5 % at 40-60, median over 140"), "hair, grey or fair, full": ([1.15, 0.5, 1.2, 0.05], "1 % at 20-30, 5 % at 40-60, median over 140"),
    "hair, dark, pale": ([1.4, 0.9, 1.4, 0.0], "5 % at 29-45, 1 % at 24-36"), "hair, dark, full": ([1.0, 1.0, 1.0, 0.0], "as the source, within 5"),
    "cloth, light": ([1.15, 0.9, 1.15, 0.0], "5 % stays over 140: paper and its shadows"),
    "cloth, mid, pale": ([1.2, 1.0, 1.3, 0.0], "5 % at 45-60, 1 % at 28-40"), "cloth, mid, full": ([1.05, 1.0, 1.1, 0.0], "as the source, within 5"),
    "cloth, dark, pale": ([1.3, 1.0, 1.3, 0.0], "5 % at 28-35"), "cloth, dark, full": ([1.0, 1.0, 1.0, 0.0], "as the source, within 5")}


def starting(kind, v, approved=False):
    """The row(s) of references/starting-values.md an area falls in -> (row, [gain, colour, curve, warm], what to aim for).
    v: what the source measures in the area (`look.py values SRC areas=masks.npz` prints the same). Near the border of
    two rows the gains are a mixture of both (a straight line across the band given at each border below), so an area
    whose polygon moves by a few pixels keeps its gains. `approved`: the source is already a finished picture in this
    look and the job is the same picture again: nothing is pushed."""
    if kind not in ("skin", "hair", "cloth"):
        return "as drawn", [1.0, 1.0, 1.0, 0.0], ""
    if approved:
        return "a finished source, as it is", [1.0, 1.0, 1.0, 0.0], "as the source, within 5"
    p5, p50, ch = v["p5"], v["p50"], v["chroma"]
    share = lambda x, at, half: float(np.clip((x - (at - half)) / (2.0 * half), 0, 1))      # 0 under the band, 1 over it
    parts = {}                                                     # row -> its share
    if kind == "skin":
        pale = share(p50, 190, 8)
        parts = {"skin, pale": pale, "skin, full": 1 - pale}
    elif kind == "hair":
        grey = share(p50, 140, 10)                                 # grey, silver, fair: dark in its depths only; the masses stay grey, the lights paper
        gp, dp = share(p5, 95, 8), share(p5, 55, 6)
        parts = {"hair, grey or fair, pale": grey * gp, "hair, grey or fair, full": grey * (1 - gp), "hair, dark, pale": (1 - grey) * dp, "hair, dark, full": (1 - grey) * (1 - dp)}
    else:
        light, mid = share(p50, 190, 10), share(p50, 95, 10)
        mp, dp = share(p5, 70, 8), share(p5, 45, 6)
        parts = {"cloth, light": light, "cloth, mid, pale": (1 - light) * mid * mp, "cloth, mid, full": (1 - light) * mid * (1 - mp),
                 "cloth, dark, pale": (1 - mid) * dp, "cloth, dark, full": (1 - mid) * (1 - dp)}
    parts = {k: w for k, w in parts.items() if w > 0.005}
    g = [round(sum(w * ROWS[k][0][i] for k, w in parts.items()) / sum(parts.values()), 3) for i in range(4)]
    first = max(parts, key=parts.get)
    row = first if len(parts) == 1 else " + ".join(f"{k} {100 * w / sum(parts.values()):.0f} %" for k, w in sorted(parts.items(), key=lambda kw: -kw[1]))
    if kind == "skin":                                             # stronger in colour than skin in this look: cooled, tone unchanged
        g[1] = round(1.0 - 0.1 * share(ch, 29, 2), 3)
        row += ", strong colour" if ch > 29 else ""
    return row, g, ROWS[first][1] + (", chroma 22-28" if kind == "skin" else "")


def measure(rgb, m):
    px = rgb[m > 0.5]
    if not len(px):
        return dict(p1=0, p5=0, p50=0, chroma=0, mean=np.zeros(3))
    p = np.percentile(px @ LUM, (1, 5, 50))
    lab = lab_of(px.mean(0)[None, None])[0, 0]
    return dict(p1=float(p[0]), p5=float(p[1]), p50=float(p[2]), chroma=float(np.hypot(lab[1], lab[2])), mean=px.mean(0))


def build(src, areas_json):
    out = Path(areas_json).parent
    spec = json.loads(Path(areas_json).read_text())
    rgb, paper = read(src, spec.get("paper"))
    h, w = rgb.shape[:2]
    u = w / 1024                                                   # sizes below are px of a 1024-wide sheet
    full = np.load(out / "regions.npy") if (out / "regions.npy").exists() else np.zeros((h, w), np.uint8)
    T = np.clip(rgb / paper, 0.02, 1.0)
    D = -np.log(T)
    polys = lambda ps, soft=0.0: np.clip(sum((poly((h, w), p, soft) for p in ps), np.zeros((h, w), np.float32)), 0, 1)
    masks, kinds, taken = {}, {}, np.zeros((h, w), bool)
    for name, a in spec["areas"].items():
        kind = kinds[name] = a.get("kind", "cloth")
        ids = list(a.get("regions", [])) + [int(full[int(y), int(x)]) for x, y in a.get("at", [])]
        m = np.isin(full, [i for i in ids if i > 0])
        if a.get("within"):
            m &= polys(a["within"]) > 0.5
        if a.get("add"):
            m |= polys(a["add"]) > 0.5
        if a.get("cut"):
            m &= ~(polys(a["cut"]) > 0.5)
        if a.get("holes"):                                         # the bottom edge is closed: a figure runs off it
            sea = np.pad(np.vstack([m, np.ones((1, w), bool)]).astype(np.uint8), 1)[:-1]
            cv2.floodFill(sea, None, (0, 0), 2)
            m = sea[1:, 1:-1][:h] != 2
        if kind == "features":
            masks[name] = np.clip(polys(a.get("add", []), 1.5 * u), 0, 1)
            continue
        m &= ~taken
        taken |= m
        masks[name] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0 * u)
    skin = np.clip(sum((m for n, m in masks.items() if kinds[n] == "skin"), np.zeros((h, w), np.float32)), 0, 1)
    for name, a in spec["areas"].items():                          # "auto": the dark blobs inside the face (eyes, brows, nostrils, the mouth)
        if kinds[name] == "features" and a.get("auto") and skin.any():
            n, cc, st, _ = cv2.connectedComponentsWithStats((skin > 0.5).astype(np.uint8))
            face = cc == 1 + np.argmax([st[i, 4] * (st[i, 1] < 0.6 * h) for i in range(1, n)])
            ys = np.nonzero(face.any(1))[0]
            fh = min(ys.max() - ys.min() + 1, 1.2 * face.sum(1).max())
            face[int(ys.min() + 0.95 * fh):] = False               # not the neck
            inner = cv2.erode(face.astype(np.uint8), ell(0.05 * fh)) > 0
            d = D.mean(-1)
            dark = (d - cv2.blur(d, (int(0.25 * fh) | 1,) * 2) > 0.11) & inner
            blobs = cv2.dilate(cv2.morphologyEx(dark.astype(np.uint8), cv2.MORPH_OPEN, ell(0.007 * fh)), ell(0.022 * fh))
            masks[name] = np.clip(masks[name] + cv2.GaussianBlur(blobs.astype(np.float32), (0, 0), 1.5 * u), 0, 1)
    feats = np.clip(sum((m for n, m in masks.items() if kinds[n] == "features"), np.zeros((h, w), np.float32)), 0, 1)
    # ---- the underdrawing: every area as the paint will want it. Nothing outside the areas: what is behind the figure is yours to paint
    out_d, cover = np.zeros_like(D), np.zeros((h, w), np.float32)
    ours = paper if spec.get("approved") else np.array(wash.PAPER, np.float32)      # the paper the sheet will be painted on
    said = lambda v: f"{v['p1']:3.0f} {v['p5']:3.0f} {v['p50']:3.0f} {hexc(v['mean'])} chroma {v['chroma']:2.0f}"
    print("area: luminance at the darkest 1 %, 5 %, median, mean colour | row of starting-values.md: gain, colour, curve, warm | the underdrawing then | aim")
    for name, a in spec["areas"].items():
        kind, m = kinds[name], masks[name]
        if kind == "features":
            continue
        v = measure(rgb, m)
        row, g, aim = starting(kind, v, bool(spec.get("approved")))
        if "gain" in a:
            row, g = "yours", list(a["gain"]) + [1.0, 1.0, 1.0, 0.0][len(a["gain"]):]
        Dk = D
        if kind == "skin":                                         # thin dark lines closed over, then a little smoothing; features stay as drawn;
            r = max(1, int(round(u)))                              # a breath of the lines is mixed back (without them an old face loses ten years)
            Ts = cv2.bilateralFilter(cv2.erode(cv2.dilate(T, ell(r)), ell(r)), 9, 0.06, 3 * u)
            keep = cv2.GaussianBlur(feats, (0, 0), 2.0 * u)[..., None]
            lines = float(a.get("lines", 0.38))
            Dk = (1 - lines) * -np.log(Ts * (1 - keep) + T * keep) + lines * -np.log(cv2.GaussianBlur(T, (0, 0), 0.7 * u))
        elif kind == "hair":                                       # its washes without the line work, which the pencil follows (trace)
            Dk = -np.log(cv2.GaussianBlur(T, (0, 0), 0.6 * u))
        Dk = fuller(Dk, *g)
        out_d += m[..., None] * Dk
        cover += m
        print(f"{name:8s} {said(v)} | {row}: {g[0]:.2f} {g[1]:.2f} {g[2]:.2f} {g[3]:.2f} | {said(measure(np.exp(-Dk) * ours, m))} | {aim}")
    under = np.exp(-(out_d / np.maximum(cover, 1e-3)[..., None]) * (cover[..., None] > 0.02)).astype(np.float32)
    np.save(out / "under.npy", under)
    np.savez_compressed(out / "masks.npz", **{k: v.astype(np.float32) for k, v in masks.items()})
    for k, v in masks.items():
        cv2.imwrite(str(out / f"mask-{k}.png"), (255 * v).astype(np.uint8))
    cv2.imwrite(str(out / "underdrawing.png"), np.clip(under * ours, 0, 255).astype(np.uint8)[..., ::-1])
    labels, names = np.zeros((h, w), np.uint8), {}
    for i, (name, m) in enumerate((n, m) for n, m in masks.items() if kinds[n] != "features"):
        labels[m > 0.5], names[i + 1] = i + 1, name
    labels[feats > 0.5], names[len(names) + 1] = len(names) + 1, "features"
    overlay(rgb, labels, names, out / "areas.png")
    print("wrote", out / "areas.png", out / "underdrawing.png", "under.npy masks.npz mask-*.png   (after the first render: look.py values, and the table's check)")
    print(f'paper: the source\'s is {hexc(paper)}. The same picture again ("approved": true): put "paper": "{hexc(paper)}" on the sheet and ladder(..., on="{hexc(paper)}", '
          f'paper="{hexc(paper)}"). A new picture: leave the sheet\'s paper alone and ladder(..., on="{hexc(paper)}").')


if __name__ == "__main__":
    a = [v for v in sys.argv[1:] if "=" not in v]
    opt = dict(v.split("=", 1) for v in sys.argv[1:] if "=" in v)
    if len(a) == 3 and a[0] == "propose":
        propose(a[1], a[2], int(opt.get("k", 9)))
    elif len(a) == 3 and a[0] == "build":
        build(a[1], a[2])
    else:
        sys.exit(__doc__)
