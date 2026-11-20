# Engine: selftest.py

The engine's promises, checked by painting: one assertion per promise. It imports `wash.py`, `regions.py` and `look.py`.

Plain Python 3 (3.12 or newer); needs `numpy` and `opencv-python-headless`. It reads and writes local image files only: no network.

**Setup, once per project:** save the code block below, exactly as it is, as `selftest.py` in the project's engine folder (for example `art/watercolour/`), beside the other engine files (`wash.py`, `regions.py`, `look.py` and `selftest.py`; see "Engine setup" in `SKILL.md`). They import each other, so all four stay in one folder. Run it with `python3 selftest.py` after changing `wash.py` or `regions.py`; it ends with `selftest ok`.

```python
"""The engine's promises, checked by painting (run it after changing wash.py):  python3 selftest.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wash                                                       # noqa: E402

lum = lambda img: img.astype(float) @ np.array([0.11, 0.59, 0.3])
paint = lambda *layers: lum(wash.draw({"frame": (0, 0, 256), "out": 256, "tooth": 0, "layers": list(layers)}))

# 1. A wash that runs off the frame stays whole at the frame's edge: the hand's wobble must not pull bare paper in from outside.
band = [(40, 200, "c"), (216, 200, "c"), (216, 400, "c"), (40, 400, "c")]                     # runs 144 units off the bottom
edge = paint({"path": band, "wash": "#39383D", "wobble": 4, "rim": 0, "pool": 0, "grain": 0})[-6:, 60:196]
assert edge.max() < 90, f"bare paper bitten into the bottom edge (lightest {edge.max():.0f}, paint is about 57)"

# 2. A named shape wholly outside the frame exists as an empty area: "clip" on it paints nothing, "out" keeps nothing off.
away = [(600, 600), (700, 600), (700, 700), (600, 700)]
box = [(60, 60, "c"), (196, 60, "c"), (196, 196, "c"), (60, 196, "c")]
mid = paint({"name": "away", "path": away}, {"path": box, "wash": "#39383D", "clip": "away"}, {"path": box, "wash": "#9DA785", "out": "away", "wobble": 0})[100:156, 100:156].mean()
assert 140 < mid < 175, f"expected the sage wash only (about 158), got {mid:.0f}"

# 3. What the water does. One flat sage square (top edge on row 60, about 158 inside); each option keeps its one promise.
sage = {"path": box, "wash": "#9DA785", "wobble": 0, "rim": 0, "pool": 0, "grain": 0}
flat, top, inside = paint(sage), (slice(58, 63), slice(70, 186)), (slice(100, 156), slice(100, 156))
ring = np.zeros(flat.shape, bool)
ring[60:196, 60:196], ring[64:192, 64:192] = True, False            # the 4 px just inside the outline
with_ = lambda **k: paint(dict(sage, **k))
assert np.array_equal(with_(ragged=3, settle=0.4, dry=0.6), with_(ragged=3, settle=0.4, dry=0.6)), "the same layer must paint the same pixels"
assert abs(with_(miss=4) - flat)[inside].max() < 3 < 40 < abs(with_(miss=4) - flat).max(), "miss: the outline moves, the inside stays"
assert abs(with_(ragged=3) - flat)[inside].max() < 3 < 40 < abs(with_(ragged=3) - flat).max(), "ragged: the edge crawls, the inside stays"
assert abs(with_(ragged=3) - with_(ragged=3, seed=2)).max() > 40, "seed: another throw for one layer"
assert with_(dry=0.8)[59, 70:186].std() > flat[59, 70:186].std() + 6, "dry: a hard edge crumbles along its length"
assert (flat - with_(settle=0.5))[ring].mean() > (flat - with_(settle=0.5))[72:184, 72:184].mean() + 3, "settle: paint gathers in a band inside the edge"
assert with_(sediment=0.3)[inside].std() > flat[inside].std() + 2, "sediment: specks inside the wash"
assert with_(rim=1, broken=0.5)[top].std(1).mean() > with_(rim=1)[top].std(1).mean() + 2, "broken: the rim comes and goes"
bloom = paint(sage, {"path": [(100, 100, "c"), (156, 100, "c"), (156, 156, "c"), (100, 156, "c")], "bloom": 0.6, "ragged": 0, "wobble": 0, "broken": 0})
assert bloom[128, 128] > flat[128, 128] + 8 and bloom[99:104, 110:146].min() < flat[128, 128] - 8, "bloom: lighter inside, a dark line at its edge"
specks = (paint(sage, {"path": box, "sparkle": 1.0})[inside] > 225).mean()
assert 0.002 < specks < 0.2, f"sparkle: a few specks of bare paper, not a hole (share {specks:.3f})"

# 4. The paper's default tooth is the look's quiet one (fine std of luminance on bare paper 1.2-1.8; at 2.4 it reads as an overlay).
bare = wash.draw({"frame": (0, 0, 256), "out": 256, "layers": []}).astype(np.float32) @ np.array([0.11, 0.59, 0.3], np.float32)
import cv2                                                         # noqa: E402
tooth = float((bare - cv2.GaussianBlur(bare, (0, 0), 6)).std())
assert 1.2 < tooth < 1.8, f"default paper tooth reads {tooth:.2f}, the look wants 1.2-1.8"

# 5. A ladder is the garment's own: over LOCAL, SHADE gives the source's shadow (hue and all), every later step is darker.
hexrgb = lambda h: np.array(wash.hexrgb(h), float)
local, turn, shade, deep, dark, rib = wash.ladder("#B7B485", "#6D7857", "#2E4132", on="#FCF8E5")
got, want = hexrgb(local) * hexrgb(shade) / wash.PAPER, hexrgb("#6D7857") / hexrgb("#FCF8E5") * wash.PAPER
assert abs(got - want).max() < 3, f"SHADE over LOCAL should read as the source's shadow on our paper ({want.round()}), got {got.round()}"
lums = [hexrgb(c) @ (0.3, 0.59, 0.11) for c in (turn, shade, deep, dark)]
assert lums == sorted(lums, reverse=True), "the glazes of a ladder get darker step by step"

# 6. The ribs of a knit have no kinks: no two nodes of a piece fall on one spot (that makes S-shaped scribbles in short pieces).
pieces = wash.runs([(0, 0), (10, 300), (0, 600)], [(200, 0), (260, 300), (220, 600)], 7.5, seed=3)
gap = min(np.linalg.norm(np.diff(np.array(p), axis=0), axis=1).min() for p in pieces)
assert gap > 6, f"two nodes of one rib nearly on one spot ({gap:.1f} px apart)"

# 7. Dark garments. need(): a nested step lands on the tone asked for. toned(): the same water speckles a dark no more than a mid-tone.
grey = lambda tone: "#%02X%02X%02X" % ((int(tone),) * 3)
flatk = dict(wobble=0, rim=0, pool=0, grain=0)
got = paint(dict(path=box, wash=grey(150), **flatk), dict(path=box, wash=grey(110), alpha=wash.need(grey(110), 150, 64), **flatk))[inside].mean()
assert abs(got - 64) < 3, f"need: a glaze from 150 should arrive at 64, got {got:.0f}"
speck = lambda tone, k: (lambda im: float((im - cv2.GaussianBlur(im, (0, 0), 6))[inside].std() / im[inside].mean()))(paint(dict(path=box, wash=grey(tone), wobble=0, rim=0, **k)).astype(np.float32))
water = dict(sediment=0.2, settle=0.4)
assert speck(45, water) > 2.5 * speck(150, water) and speck(45, wash.toned(water, 45)) < 1.3 * speck(150, wash.toned(water, 150)), "toned: on a dark the water is cut back to what a mid-tone shows"
assert wash.ladder("#B7B485", "#6D7857", on="#FCF8E5", paper="#F4E9D9") == wash.ladder("#B7B485", "#6D7857", on="#FCF8E5", paper=(244, 233, 217)), "ladder: the sheet's paper as hex or RGB"

# 8. A wet gradient inside one shape ("grade"): dark where it was loaded, pale where it was not, no edge between, the outline still hard.
g = paint(dict(sage, grade=[((70, 128), 1.0), ((186, 128), 0.15)]))
row = cv2.GaussianBlur(g, (0, 0), 3)[128, 66:190]
assert g[128, 70] < flat[128, 70] + 4 and g[128, 186] > flat[128, 186] + 40 and np.abs(np.diff(row)).max() < 4 and g[128, 63] < 200 < g[128, 57], "grade: one wash, loaded here and thin there"

# 9. A brush stroke ("brush"): the same pixels every time; more paint where it was set down than at its end; with a low load it
#    breaks up before its end, with a full one it stays solid.
tone = "#39383D"
one = lambda load, **k: paint(dict(brush=[[(128, 30), (128, 128), (128, 226)]], w=24, load=load, wash=tone, wobble=0, rim=0, pool=0, grain=0, bristle=0, vary=0, **k))
full, short = one(2.0), one(0.7)
assert np.array_equal(full, one(2.0)), "brush: the same layer must paint the same pixels"
assert full[40:70, 122:134].mean() < full[186:216, 122:134].mean() - 3, "brush: the deposit falls with the distance from where the brush was set down"
assert (full[180:215, 120:136] < 150).mean() > 0.97 and 0.03 < (short[150:215, 118:138] < 150).mean() < 0.7 and (short[40:80, 120:136] < 150).mean() > 0.97, "brush: a low load breaks up before the end"
# 10. A wet session: two strokes of unequal strength run into each other (no step between them), wet over wet does not glaze, and the
#     session's outer edge stays hard. With "wet": 0 each stroke dried first: the overlap is darker than either. "clip" holds them in.
pair = lambda **k: paint(dict(brush=[dict(path=[(108, 40), (108, 216)], press=1.0), dict(path=[(140, 40), (140, 216)], press=0.6)], w=44, load=3, fall=0, wash=tone, wobble=0, rim=0, pool=0, grain=0,
                              bristle=0, vary=0, **k))
melted, glazed = pair(wet=14), pair(wet=0)
row = melted[128, 90:160]
assert np.abs(np.diff(row)).max() < 6 and row[-1] - row[0] > 25, "wet: the strokes' boundary melts into a gradient"
assert abs(melted[128, 124] - melted[128, 100]) < 30 and glazed[128, 124] < glazed[128, 100] - 12, "wet over wet levels out; dry strokes glaze where they overlap"
assert melted[128, 84] > 215 and melted[128, 90] < 90, "wet: the session's outer edge stays hard"
held = paint(dict(name="held", path=[(60, 100, "c"), (200, 100, "c"), (200, 160, "c"), (60, 160, "c")], wobble=0), dict(brush=[[(128, 30), (128, 226)]], w=30, wash=tone, clip="held"))
assert held[60, 128] > 215 and held[130, 128] < 100, "clip: strokes stay inside the area"
# 11. The helpers lay strokes by decision, never as a comb: the same for a seed, unequal in width, load, length and angle; inside a
#     shape they stay in it; a hem's strokes cross its line by unequal lengths. And 200 strokes on an 888 x 1184 sheet take seconds.
ga, gb = [(60, 40), (50, 480)], [(420, 40), (440, 480)]
ss = wash.strokes_along(ga, 30, seed=3, to=gb)
span = lambda st: np.linalg.norm(np.subtract(st["path"][-1], st["path"][0]))
lean = lambda st: np.degrees(np.arctan2(*np.subtract(st["path"][-1], st["path"][0])))
assert ss == wash.strokes_along(ga, 30, seed=3, to=gb) and ss != wash.strokes_along(ga, 30, seed=4, to=gb), "strokes_along: one seed, one throw"
assert all(np.std([f(st) for st in ss]) > lim for f, lim in ((span, 20), (lean, 1.0), (lambda st: st["load"], 0.1), (lambda st: max(st["w"]), 2))), "strokes_along: unequal lengths, angles, loads, widths"
disc = [(250 + 90 * np.cos(a), 260 + 90 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)]
inside = wash.strokes_along([(250, 100), (250, 420)], 20, seed=1, within=disc)
assert inside and all(np.hypot(x - 250, y - 260) < 140 for st in inside for x, y in st["path"]), "strokes_along(within=): the strokes of a shape stay about it"
hs = wash.hem([(40, 200), (440, 200)], 9, lengths=(10, 80), seed=2)
ends = [st["path"][-1][1] - 200 for st in hs]
assert len(hs) == 9 and 8 <= min(ends) and max(ends) <= 82 and np.std(ends) > 8 and np.std(np.diff([st["path"][1][0] for st in hs])) > 4, "hem: unequal stroke ends at unequal distances"
import time                                                       # noqa: E402
many = wash.strokes_along([(60, 60), (40, 1100)], 34, seed=1, to=[(820, 60), (850, 1100)], length=(0.1, 0.16), lap=0.8)
t0 = time.time()
wash.draw({"frame": (0, 0, 888, 1184), "out": 888, "layers": [dict(brush=many[:200], wash=tone, wet=12)]})
assert len(many) >= 200 and time.time() - t0 < 20, f"200 strokes on an 888 x 1184 sheet took {time.time() - t0:.0f} s"

# 12. A light along an edge: a "lift" on a stroke takes a thread of paint off a dark wash and leaves the rest alone.
dark = dict(path=box, wash="#39383D", **flatk)
lifted = paint(dark, dict(stroke=[(70, 128), (186, 128)], w=1.6, lift=0.85, vary=0))
assert lifted[128, 100:160].mean() > paint(dark)[128, 100:160].mean() + 60 and abs(lifted[120, 100:160].mean() - paint(dark)[120, 100:160].mean()) < 3, "lift on a stroke: a sharp light"
assert np.allclose(np.array(wash.beside([(0, 0), (100, 0)], 3)), [(0, 3), (100, 3)]), "beside: to the right hand of someone walking along the line"

# 13. A scalloped wash (scallop()): lobes and sharp bays round the same area, and its dried rim darker than its inside.
blot = [(128 + 70 * np.cos(a), 128 + 70 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)]
sc = wash.scallop(blot, 40, seed=3)
area = lambda nodes: cv2.contourArea(wash.flow(nodes).astype(np.float32))
assert sum("c" in n[2:] for n in sc) >= 4 and 0.85 < area(sc) / area(blot) < 1.3 and sc == wash.scallop(blot, 40, seed=3), "scallop: lobes round the same shape, the same every time"
pale = paint(dict(path=sc, wash="#E2D8CA", rim=2, wobble=0, pool=0, grain=0))
m = (pale < pale[128, 128] + 6).astype(np.uint8)
edge_band = (m > 0) & (cv2.erode(m, np.ones((5, 5), np.uint8)) == 0)
assert pale[edge_band].mean() < pale[100:156, 100:156].mean() - 1.0, "scallop: a pale wash shows its dried edge"

# 14. Starting values do not jump at the border of two rows, and a finished source ("approved": true) is not pushed.
import regions                                                    # noqa: E402
v = lambda p50, p5: dict(p1=30, p5=p5, p50=p50, chroma=4)
ga, gb = regions.starting("cloth", v(94, 39))[1], regions.starting("cloth", v(97, 39))[1]
assert max(abs(x - y) for x, y in zip(ga, gb)) < 0.03, f"a median 3 levels apart should give nearly the same gains, got {ga} and {gb}"
assert regions.starting("cloth", v(60, 30))[1] == [1.0, 1.0, 1.0, 0.0] and regions.starting("cloth", v(150, 90))[1] == [1.2, 1.0, 1.3, 0.0], "inside a row the gains are the table's"
assert regions.starting("hair", v(170, 120), approved=True)[1] == [1.0, 1.0, 1.0, 0.0], "a finished source keeps its values"

# 15. A charged stroke ("cut", "melt", "drag", "press" along it): cut ends are askew, not round; the melting side thins away with no
#     edge while the other keeps its own; the dragged side breaks up on the tooth; a pressure that falls lets an end dissolve.
ch = lambda **k: paint(dict(brush=[dict(path=[(128, 30), (128, 226)], **k)], w=40, load=3, fall=0, wash=tone, wobble=0, rim=0, pool=0, grain=0, bristle=0, vary=0, wet=1.5))
plain, askew, melted, dragged, lifted = ch(), ch(cut=30), ch(melt=0.6), ch(drag=0.5), ch(press=(1, 1, 0.2))
assert plain[18, 128] < 100 and plain[42, 114] < 100 and askew[18, 128] > 200 and askew[42, 142] < 100 and askew[42, 114] > 200, "cut: the end is cut askew, its right-hand corner trailing"
row = cv2.GaussianBlur(melted, (0, 0), 1.5)[128, 100:160]
assert row[44] < 90 and melted[128, 153] > 215 and np.abs(np.diff(row[:30])).max() < 25 < 100 < np.abs(np.diff(melted[128, 140:156])).max() and row[12] > 170, "melt: one side keeps its edge, the other thins away without one"
assert 0.05 < (dragged[60:200, 110:124] < 150).mean() < 0.8 and (dragged[60:200, 132:145] < 150).mean() > 0.97, "drag: one side of the stroke breaks up on the tooth"
assert lifted[205, 128] > lifted[60, 128] + 60, "press along a stroke: its end dissolves"

# 16. The stitches of a knit ("knit"): the same pixels every time; they run down their field; full where the paint under them is
#     dark and faint in the light; and never a ruled pattern (the grooves stand at unequal distances, break off, wander).
ground = [dict(path=[(-9, -9, "c"), (265, -9, "c"), (265, 265, "c"), (-9, 265, "c")], wash=grey(170), **flatk),
          dict(path=[(128, -9, "c"), (265, -9, "c"), (265, 265, "c"), (128, 265, "c")], wash=grey(110), alpha=wash.need(grey(110), 170, 90), **flatk)]
kn = lambda **k: paint(*ground, dict(dict(knit=([(8, -9), (8, 265)], [(248, -9), (248, 265)]), pitch=9, stitch=6, color=grey(150), tones=(170, 90)), **k))
bare, knitted = paint(*ground), kn()
assert np.array_equal(knitted, kn()), "knit: the same layer must paint the same pixels"
mark = (bare - knitted) / bare                                    # how much of the light the stitches take, whatever is under them
assert mark[20:236, 150:240].mean() > 2.5 * mark[20:236, 16:106].mean() > 0.002, "knit: full in the shadow, faint (but there) in the light"
assert np.abs(np.diff(mark[20:236, 150:240], axis=1)).mean() > 1.8 * np.abs(np.diff(mark[20:236, 150:240], axis=0)).mean(), "knit: the marks run along the field"
prof = mark[20:236, 140:246].mean(0) - mark[20:236, 140:246].mean()
ac = np.correlate(prof, prof, "full")[len(prof) - 1:] / (prof @ prof)
assert ac[6:13].max() < 0.6, f"knit: the grooves must not stand as a ruled grid (autocorrelation at the pitch {ac[6:13].max():.2f})"
t0 = time.time()
wash.draw({"frame": (0, 0, 888, 1184), "out": 888, "layers": [dict(path=[(0, 0, "c"), (888, 0, "c"), (888, 1184, "c"), (0, 1184, "c")], wash=grey(120)),
                                                             dict(knit=([(40, 40), (40, 1140)], [(850, 40), (850, 1140)]), pitch=8.5, color=grey(150))]})
assert time.time() - t0 < 20, f"a knit over an 888 x 1184 sheet took {time.time() - t0:.0f} s"

# 17. One layer alone (draw(only=)): the others lay no paint but keep their names, so "clip" still holds. And a "brush" session reports
#     what it covered (watch=): a stroke that leaves part of its clip open can be found (look.py holes).
two = {"frame": (0, 0, 256), "out": 256, "tooth": 0, "layers": [dict(name="sq", path=box, wash=grey(150), **flatk), dict(brush=[[(128, 30), (128, 226)]], w=40, load=3, wash=tone, clip="sq", name="st")]}
alone, seen = lum(wash.draw(two, only={1})), []
assert alone[128, 80] > 225 and alone[128, 128] < 100 and alone[45, 128] > 225, "only=: the square lays no paint, the stroke is still clipped to it"
wash.draw(two, watch=seen)
(_, cover, kept), = seen
assert ((kept > 0.5) & (cover < 0.5)).mean() > 0.15 and ((kept > 0.5) & (cover > 0.5)).mean() > 0.05, "watch=: the part of its clip a session left open can be seen"
# 18. The water by measurement (toned(speck=)): the wash shows about the speck asked for, at a mid-tone and on a dark, up as well as down.
import io, contextlib                                             # noqa: E402
for tone_, want in ((101, 6.2), (48, 10.0)):
    im = paint(dict(path=box, wash=grey(tone_), wobble=0, rim=0, **wash.toned(dict(grain=0.12, pool=0.015, sediment=0.05), tone_, speck=want))).astype(np.float32)
    got = 100 * float((im - cv2.GaussianBlur(im, (0, 0), 6))[100:156, 100:156].std() / im[100:156, 100:156].mean())
    assert abs(got - want) < 0.35 * want, f"toned(speck={want}) at tone {tone_} painted a speck of {got:.1f} %"
assert wash.toned(None, 48, speck=14)["grain"] > 0.1 > wash.toned(None, 48)["grain"], "toned: a measured speck may raise the water, the unmeasured rule only cuts it"
err = io.StringIO()
with contextlib.redirect_stderr(err):
    assert wash.need(grey(110), 64, 150) == 0 and "paints nothing" in err.getvalue(), "need: a step the wrong way round paints nothing, and says so"
# 19. A hem never drips (hem(reach=)): a wet end runs no further beyond the line than its own width; a dry one is dragged on.
wet_ends, dry_ends = wash.hem([(40, 200), (440, 200)], 12, lengths=(20, 90), seed=2, w=(14, 26), load=(1.2, 2.0)), wash.hem([(40, 200), (440, 200)], 12, lengths=(20, 90), seed=2, w=(14, 26), load=(0.5, 0.9))
assert all(st["path"][-1][1] - 200 <= max(st["w"][-1], 20) + 0.01 for st in wet_ends) and max(st["path"][-1][1] - 200 for st in dry_ends) > 60, "hem: wet ends are lobes, dry ends are dragged on"
# 20. The plaits of a cable knit ("cable"): the same pixels every time; wedges on both sides of the middle line that lean opposite ways;
#     stronger in the shadow; and no printed pattern along the cable (unequal distances, lengths and weights).
cb = lambda **k: paint(*ground, dict(dict(cable=[[(64, -9), (64, 265)], [(192, -9), (192, 265)]], width=34, cross=16, color=grey(150), tones=(170, 90), sides=0), **k))
cabled = cb()
assert np.array_equal(cabled, cb()), "cable: the same layer must paint the same pixels"
cm = (bare - cabled) / bare
assert cm[20:236, 176:208].mean() > 1.15 * cm[20:236, 48:80].mean() > 0.01, "cable: fuller in the shadow, clearly there in the light"
gx, gy = np.gradient(cv2.GaussianBlur(cm, (0, 0), 1.2))
lean_of = lambda sl: float((gx[sl] * gy[sl]).sum())                # the sign of a mark's slant
assert lean_of((slice(20, 236), slice(48, 63))) * lean_of((slice(20, 236), slice(65, 80))) < 0, "cable: the two sides lean opposite ways"
prof = cm[20:236, 48:63].mean(1) - cm[20:236, 48:63].mean()
ac = np.correlate(prof, prof, "full")[len(prof) - 1:] / (prof @ prof)
assert ac[12:40].max() < 0.75, f"cable: the crossings must not repeat like a print (autocorrelation {ac[12:40].max():.2f})"
# 21. The painter's instruments (look.py): a picture against itself differs nowhere; rows of tones and a speck come out of a file.
import look, tempfile                                             # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    f = str(Path(tmp) / "a.png")
    cv2.imwrite(f, wash.draw({"frame": (0, 0, 256), "out": 256, "layers": [dict(path=box, wash=grey(100), wobble=0)]}))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        look.diff(f, f)
        look.tones(f, step=64)
        look.speck([f], box=(70, 70, 186, 186))
    said = out.getvalue()
    assert "within 15: 100 %" in said and "speck" in said and " 96 " in said.replace("  ", " "), "look.py diff / tones / speck"
print("selftest ok")
```
