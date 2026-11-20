# Example: cardigan.py

The drawings file of the cardigan example: a man in a cable cardigan, a new picture painted from a pale pencil-and-tint sketch (`references/worked-example.md` walks through it). It paints with the engine (`references/engine/`).

Plain Python 3 (3.12 or newer); needs `numpy` and `opencv-python-headless`. It reads and writes local image files only: no network.

**Setup:** copy this folder (`source.png`, `areas.json`, `sheet.png`, `portrait.png`) into the engine folder as `examples/cardigan/`, and save the code block below, exactly as it is, as `cardigan.py` inside that copy; it finds `source.png` and `areas.json` beside itself. Then, from the engine folder, run `python3 wash.py examples/cardigan/cardigan.py examples/cardigan/out`.

```python
"""One figure in one file: a man in a cable cardigan, a NEW picture painted from a pale pencil-and-tint sketch. Head, neck, shirt
and trousers go through the underdrawing, the face is finished by hand, the cardigan is painted by hand. Grid = the source's pixels (780 x 1024).

    python3 wash.py examples/cardigan/cardigan.py examples/cardigan/out            # from the engine folder: sheet, portrait, body, draft (about a minute)
    python3 wash.py examples/cardigan/cardigan.py examples/cardigan/out portrait   # one drawing: 7 s; `draft` (the cardigan alone): 3 s

The first run builds the underdrawing (step 2 of the order of work: areas.json + source.png -> out/under/, a few seconds; it prints the
row of starting values every area falls in). sheet.png and portrait.png beside this file are what it paints. areas.json holds the areas
as corrected in step 1 (`regions.py propose`, then by hand), kept as polygons, so that the build needs nothing but that file and the source.
figure() is the part to copy: ground, cardigan, head. Areas that come from the underdrawing ("masks": skin, hair, features, shirt,
trousers, knit) and shapes named by hand (figure, cardigan, paint, arm_l, arm_r, wash, light, shade, bands, plait) share one list of
names, and equal names add up. The cardigan's washes and shadows are brush strokes laid in fields; its stitches and cables are put in
AFTER the form with the "knit" and "cable" brushes, which read the values under them (SKILL.md, "Large areas are painted in strokes").

    E=examples/cardigan
    python3 look.py shapes $E/source.png $E/out/shapes.png mask=$E/out/under/mask-knit.png          # where the source put light and shadow
    python3 look.py paths  $E/cardigan.py draft $E/source.png $E/out/paths.png scale=1.3 kinds=path,area
    python3 look.py values $E/out/portrait.png areas=$E/out/under/masks.npz frame=170,52,389,389    # the checks after the first render
"""
import os
import shutil

import numpy as np
from wash import ladder, ribs, ring, strokes_along

HERE = os.path.dirname(os.path.abspath(__file__))


def underdrawing():
    """Step 2 of the order of work, at run time: areas.json and the source -> out/under/ (under.npy, masks.npz, mask-NAME.png, areas.png)."""
    src, areas, dst = os.path.join(HERE, "source.png"), os.path.join(HERE, "areas.json"), os.path.join(HERE, "out", "under")
    made = os.path.join(dst, "under.npy")
    if not os.path.exists(made) or os.path.getmtime(made) < max(os.path.getmtime(src), os.path.getmtime(areas)):
        import regions
        os.makedirs(dst, exist_ok=True)
        shutil.copy(areas, dst)
        regions.build(src, os.path.join(dst, "areas.json"))
    return np.load(made), dict(np.load(os.path.join(dst, "masks.npz")))


UNDER, MASKS = underdrawing()
C, W = "c", "w"
PORTRAIT, SHEET, BODY = (170, 52, 389, 389), (0, 0, 780, 1024), (90, 300, 690, 724)     # the portrait: hair top 4 % under the edge, head 70 % of the height, eyes at 40 %
HEAD = 272                                           # hair top to chin, source px: it sets "fine" and "weave" for every frame
# ---------------------------------------------------------------- the cardigan: its outline (nodes_of the "knit" mask, eps 4, then corrected on look.py grid)
V_R = [(476, 322, C), (479, 334), (470, 354), (452, 374), (420, 416), (385, 462), (355, 503), (334, 534, C)]            # the V's edge, his left (shared with the shirt)
V_L = [(323, 503), (314, 468), (309, 438), (306, 410), (300, 388, C)]                                                  # ... his right, upwards
CARD = V_R + V_L + [(286, 394), (262, 408), (232, 428), (198, 454), (186, 482), (176, 560), (162, 639), (151, 661), (150, 690), (125, 748), (124, 790), (116, 812), (120, 840), (113, 862), (118, 900),
                    (116, 938, C), (132, 946), (142, 976, C), (156, 982, C), (178, 942, C), (188, 959), (240, 994), (311, 1011), (344, 1001), (392, 1001), (441, 991), (522, 955, C), (573, 1005),
                    (583, 1023, C), (648, 974), (678, 905), (700, 865), (710, 830), (722, 814), (724, 780), (724, 740), (716, 698), (708, 640), (698, 570), (682, 505), (665, 452), (629, 412),
                    (575, 385), (520, 360), (488, 322)]
# The forms, decided before any paint. The light is the source's: from the upper right, a little in front. The trunk lies over his
# right arm (TRUNK_L is that edge), his left arm lies over the trunk (ARM_IN)
TRUNK_L = [(205, 470), (200, 520), (202, 580), (206, 640), (214, 700), (212, 760), (201, 800), (203, 830), (188, 868), (180, 905), (178, 942)]
ARM_IN = [(548, 532), (551, 600), (555, 660), (560, 720), (566, 765), (558, 805), (548, 845), (536, 885), (522, 955)]
ARM_L = [(548, 532, C)] + ARM_IN[1:] + [(583, 1023, C), (770, 1023, C), (770, 380, C), (560, 380, C)]
ARM_R = [(205, 470, C)] + TRUNK_L[1:] + [(156, 990, C), (100, 1000, C), (100, 420, C), (200, 440, C)]
BAND_L = [(294, 396), (298, 438), (303, 478), (311, 514), (323, 546)]                    # middle lines of the ribbed bands
BAND_R = [(490, 340), (464, 382), (434, 424), (400, 468), (370, 508), (347, 544)]
PLACKET = [(330, 556), (326, 602), (318, 660), (310, 712), (300, 765), (291, 813), (284, 865), (280, 912), (279, 950), (279, 985), (280, 1008)]
BUTTONS = [(326, 602), (310, 712), (291, 813), (280, 912), (279, 985)]
HEM = [[(184, 950), (215, 972), (258, 992)], [(302, 996), (350, 992), (400, 990), (450, 980), (500, 960), (522, 946)]]
CUFFS = [[(120, 936), (146, 958), (172, 946)], [(528, 950), (556, 978), (586, 1010)]]
CABLES = [[(262, 440), (262, 520), (260, 600), (256, 680), (248, 760), (240, 840), (234, 925)], [(406, 590), (404, 680), (400, 760), (394, 840), (388, 940)],
          [(455, 445), (457, 520), (455, 600), (450, 680), (445, 760), (440, 850), (436, 930)], [(658, 470), (674, 560), (686, 640), (692, 720), (688, 790)], [(172, 520), (160, 600), (148, 680), (138, 760), (134, 830)]]
# the lie of the cloth: three fields that together cover the garment (his right arm, the trunk, his left arm), drawn from above the shoulder to below the hem
BIG = [([(214, 380), (180, 520), (160, 640), (124, 760), (112, 880), (120, 990)], [(246, 372), (203, 520), (206, 640), (212, 760), (203, 830), (180, 905), (176, 990)]),
       ([(244, 372), (200, 520), (204, 640), (210, 760), (201, 830), (178, 905), (186, 1010)], [(552, 300), (549, 532), (555, 660), (566, 765), (548, 845), (522, 955), (530, 1010)]),
       ([(548, 300), (547, 532), (553, 660), (564, 765), (546, 845), (520, 955), (575, 1024)], [(650, 380), (694, 520), (712, 660), (724, 780), (700, 860), (650, 970), (600, 1024)])]
# the same forms for the shadows' strokes: the trunk left of the placket, right of it, his right arm, his left upper arm, his left forearm
FIELDS = [([(232, 420), (204, 520), (208, 640), (214, 760), (203, 830), (182, 905), (190, 990)], [(300, 390), (312, 500), (322, 600), (306, 712), (288, 813), (277, 912), (277, 1000)]),
          ([(350, 548), (334, 660), (318, 770), (304, 870), (298, 1000)], [(549, 532), (555, 660), (566, 765), (548, 845), (522, 955)]),
          ([(196, 440), (180, 520), (160, 640), (124, 760), (112, 880), (120, 960)], [(205, 470), (202, 580), (212, 720), (203, 830), (180, 905), (176, 960)]),
          ([(548, 532), (553, 660), (566, 765)], [(660, 450), (706, 640), (722, 770)]),
          ([(566, 765), (640, 770), (722, 790)], [(522, 955), (560, 990), (600, 1020)])]
# where the light falls: ONE plane per form, on the side that faces the light, running along the form
LIGHTS = [[(350, 566), (396, 492), (452, 432), (512, 426), (536, 500), (538, 610), (528, 720), (500, 800), (446, 850), (384, 866), (344, 820), (332, 720), (338, 630)],          # the trunk: the chest, his left front
          [(566, 398), (622, 420), (664, 470), (694, 560), (706, 650), (716, 740), (704, 800), (664, 806), (640, 730), (622, 650), (604, 570), (588, 480)],                      # his left arm: shoulder and outer side
          [(196, 470), (184, 540), (172, 620), (158, 690), (136, 760), (126, 830), (140, 850), (160, 770), (176, 700), (186, 620), (192, 540)]]                                  # his right arm: its outer side
SAGE, TURN, SHADE, DEEP, DARK, RIB = ladder("#B2B086", "#697155", "#414B3B", on="#FBF9EE")
GROOVE = "#A6AA8C"                                                          # look.py glaze GROUND GROOVE: a groove is two thirds of its ground
MISS = 1.8
POOL = dict(settle=0.25, sediment=0.12, broken=0.4)                         # a step inside a shadow: paint gathers, its rim comes and goes
CORE = dict(settle=0.4, sediment=0.18)                                      # a core: heavy pigment that granulates


def ground():
    """Behind him: paper, and one faint grey smudge behind a shoulder, kept out of the figure, no rim."""
    return [dict(name="figure", path=CARD, wobble=0.5),
            dict(path=[(556, 322), (632, 344), (690, 410), (716, 500), (700, 560), (640, 500), (596, 420)], wash="#DEDFDC", bleed=18, soft=8, out=["figure", "hair", "skin", "shirt"], alpha=0.5, pool=0.25, rim=0)]


def cardigan():
    Ls = []
    add = lambda **k: Ls.append(k)
    add(name="cardigan", path=CARD, wobble=0.5)                              # the drawing: the pencil keeps to it
    add(name="paint", path=CARD, wobble=0.5, miss=MISS)                      # the paint strays from it
    add(name="arm_l", path=ARM_L, wobble=0.3, clip="cardigan")
    add(name="arm_r", path=ARM_R, wobble=0.3, clip="cardigan")
    # the shirt runs UNDER the cardigan (near-white under a mid-tone: nothing is lost): its shadowed edge along the V, laid first, so
    # that where the paint misses the drawing there is shirt and not a line of bare paper like piping
    add(stroke=[[n[:2] for n in V_R], [V_R[-1][:2]] + [n[:2] for n in V_L]], w=9, color="#D9D4C9", soft=1.5, vary=0, out=["skin", "hair"])
    # 1. the local colour: one wet session of broad loaded strokes down each form; then, dry on dry, a second of narrower strokes kept off the lights
    field = lambda F, size, seed, **k: strokes_along(F[0], size, seed=seed, to=F[1], **k)
    over = lambda fields, size, seed, **k: [s for i, F in enumerate(fields) for s in field(F, size, seed + i, **k)]
    fill = lambda shape, F, size, seed, **k: strokes_along(F[0], size, seed=seed, to=F[1], within=shape, **k)
    add(name="wash", brush=over(BIG, 24, 10, load=(1.3, 2.0), lap=1.3, w=(0.8, 1, 1, 0.8), ends=(0.2, 1.0), angle=3), wash=SAGE, alpha=1.12, wet=11, bristle=0.1, clip="paint",
        pool=0.03, grain=0.12, sediment=0.1, settle=0.3, rim=0.3, broken=0.3)
    for p in LIGHTS:
        add(name="light", path=p, soft=16, wobble=2.0)
    add(brush=over(BIG, 13, 20, load=(1.0, 1.7), lap=0.9, length=(0.25, 0.55), ends=(-0.5, 1.0), angle=4), wash=TURN, alpha=0.7, wet=8, vary=0.1, bristle=0.12, clip=["paint", "wash"], out="light",
        pool=0.04, grain=0.05, settle=0.2, rim=0.12, broken=0.5)
    # 2. the forms turn. Every shadow is a decision: where it starts, swells and ends, which edge is hard; each is laid as strokes of
    #    its form's field. The trunk left of the placket turns away from the light: one slow wet turn ...
    T_L, T_R, A_R, A_U, A_F = FIELDS
    add(name="shade", brush=fill([(232, 430, C), (262, 420), (290, 440), (296, 520), (300, 600), (290, 700), (272, 800), (258, 900), (250, 990), (186, 990), (182, 905), (203, 830), (212, 760), (206, 640), (200, 520)], T_L, 17, 30, load=(1.2, 1.9), lap=0.8),
        wash=SHADE, alpha=0.4, wet=9, soft=7, settle=0.3, sediment=0.12, rim=0.1, clip="paint", out="arm_r")
    #    ... the valley under his left arm, on the trunk: a wedge that starts at the armpit as a line, swells at the waist and thins again
    add(name="shade", brush=fill([(548, 540, C), (538, 600), (522, 680), (510, 760), (512, 830), (500, 890), (470, 940), (522, 955, C), (548, 845), (566, 765), (555, 660)], T_R, 16, 31, load=(1.2, 1.9), lap=0.8),
        wash=SHADE, alpha=0.5, wet=9, soft=7, settle=0.3, sediment=0.12, rim=0.1, clip="paint", out="arm_l")
    add(brush=fill([(548, 560, C), (541, 640), (536, 720), (540, 790), (534, 850), (520, 900), (540, 890, C), (550, 845), (566, 765), (555, 660)], T_R, 12, 32, load=(1.3, 2.0), lap=0.9),
        wash=DEEP, wet=6, soft=2.5, alpha=0.65, clip="paint", out="arm_l", rim=0.2, **CORE)
    add(brush=[dict(path=[(549, 548), (551, 610), (554, 670), (559, 730), (562, 764)], w=(3, 9, 12, 10, 4), load=2)], wash=DARK, alpha=0.5, wet=1.5, melt=-0.5, clip="paint", out="arm_l", rim=0.3, **CORE)
    #    his right arm, where the trunk lies over it: its inner side is the dark one (the trunk stands between it and the light)
    add(name="shade", brush=fill([(204, 480, C), (200, 560), (204, 640), (212, 720), (210, 770), (200, 810), (186, 870), (178, 930), (160, 900), (166, 820), (178, 760), (182, 690), (176, 620), (180, 540)], A_R, 12, 35, load=(1.2, 1.8), lap=0.8),
        wash=SHADE, wet=5, alpha=0.6, clip="arm_r", rim=0.3, **POOL)
    add(brush=fill([(204, 540, C), (203, 620), (210, 700), (210, 765), (200, 808), (192, 850, C), (190, 790), (196, 730), (194, 660), (192, 590)], A_R, 10, 37, load=(1.2, 1.8), lap=0.8),
        wash=DEEP, wet=4, soft=2, alpha=0.62, clip="arm_r", rim=0.2, **CORE)
    add(brush=fill([(120, 800, C), (150, 786), (180, 800), (170, 870), (150, 930), (124, 930), (114, 870)], A_R, 12, 38, load=(0.9, 1.6), lap=0.7), wash=TURN, wet=5, alpha=0.7, vary=0.2, clip="arm_r", rim=0.25, **POOL)
    #    his left arm: lit along its outer side; its dark is the side that faces the trunk, an angular plane on the upper arm and one
    #    on the forearm, with the crook between them
    add(name="shade", brush=fill([(550, 540, C), (586, 560), (614, 640), (624, 720), (612, 774, C), (566, 765), (556, 660)], A_U, 14, 40, load=(1.2, 1.9), lap=0.8), wash=SHADE, alpha=0.4, wet=8, soft=7,
        settle=0.3, sediment=0.12, rim=0.1, clip="arm_l")
    add(brush=fill([(552, 580, C), (570, 620), (582, 700), (584, 764, C), (566, 765), (557, 680)], A_U, 11, 43, load=(0.9, 1.6), lap=0.7, length=(0.3, 0.6)), wash=TURN, wet=5, alpha=0.8, vary=0.25, bristle=0.3,
        clip="arm_l", rim=0.15, **POOL)
    add(name="shade", brush=fill([(566, 770, C), (612, 778), (656, 802), (634, 852), (598, 902), (562, 950), (530, 950, C), (540, 885), (550, 845), (560, 805)], A_F, 13, 41, load=(1.2, 1.9), lap=0.8), wash=SHADE, wet=8, soft=6,
        alpha=0.45, clip="arm_l", rim=0.1, settle=0.3, sediment=0.12, grade=[((572, 800), 1.0), ((560, 900), 0.9), ((620, 820), 0.5), ((650, 810), 0.15)])
    add(brush=fill([(552, 600, C), (562, 660), (570, 720), (572, 762, C), (563, 762), (557, 700)], A_U, 9, 42, load=(1.2, 1.8), lap=0.9), wash=DEEP, wet=4, alpha=0.45, clip="arm_l", rim=0.2, **CORE)
    #    the body's cloth gathers above the hem band and turns under: a belt of shadow, hard on the band, wet upwards
    belt = [(184, 936, C), (214, 958), (258, 976), (300, 980), (350, 978), (400, 976), (450, 966), (500, 946), (524, 930, C), (500, 918, W), (450, 940, W), (400, 950, W), (350, 954, W), (300, 954, W), (258, 946, W), (214, 928, W)]
    add(path=belt, wash=SHADE, alpha=0.75, wet=7, clip="paint", out="arm_l", rim=0.25, **POOL)
    add(path=[(300, 980, C), (350, 978), (400, 976), (450, 966), (500, 946), (524, 930, C), (506, 934, W), (450, 954, W), (400, 963, W), (350, 966, W), (300, 968, W)], wash=DEEP, alpha=0.45, wet=4, clip="paint", out="arm_l", rim=0.2, **CORE)
    #    the crook of his left arm: a fold, crisp on the forearm's side, and the forearm's own edge where it lies on the trunk
    add(path=[(566, 764, C), (600, 766), (640, 780), (662, 800, C), (630, 796, W), (596, 786, W), (570, 780, W)], wash=DEEP, alpha=0.5, wet=4, clip="arm_l", rim=0.3, **CORE)
    add(stroke=[(560, 806), (550, 846), (538, 886), (526, 940)], w=(3, 9, 8, 3), feather=-1, alpha=0.6, color=SHADE, clip="arm_l")
    # 3. one backrun, deep inside the shadow; folds where the cloth is pulled: at the armpits and in the crook of his left arm
    add(path=[(506, 700), (522, 690), (534, 700, W), (538, 730, W), (530, 756, W), (514, 760), (504, 740)], bloom=0.35, rim=1.2, wet=5, clip="paint", out="arm_l")
    f = dict(color=SHADE, clip="paint")
    #    under the shirt's collar the bands stand in its shadow: two cast shadows, hard on the collar's side
    add(path=[(287, 398, C), (300, 390, C), (306, 430), (303, 474, W), (294, 478, W), (289, 440)], wash=SHADE, alpha=0.8, wet=5, clip="paint", rim=0.3, **POOL)
    add(path=[(476, 322, C), (491, 326, C), (486, 352, W), (468, 380, W), (452, 374), (470, 354)], wash=SHADE, alpha=0.6, wet=5, clip="paint", rim=0.3, **POOL)
    add(stroke=[(566, 766), (604, 770), (646, 792)], w=(2, 8, 2), feather=1, alpha=0.6, **f)
    add(stroke=[(548, 540), (560, 500), (580, 470)], w=(2, 6, 2), feather=-1, alpha=0.45, **f)
    add(stroke=[(204, 480), (214, 450), (232, 430)], w=(2, 5, 2), feather=1, alpha=0.4, **f)
    # 4. the knit, AFTER the form: plain ribs down the three big fields, kept off the bands and off a strip along each cable; then the cables
    add(name="bands", stroke=[BAND_L, BAND_R], w=24, vary=0)
    add(name="bands", stroke=PLACKET, w=40, vary=0)
    add(name="bands", stroke=HEM, w=30, vary=0)
    add(name="bands", stroke=CUFFS, w=26, vary=0)
    add(name="plait", stroke=CABLES, w=26, vary=0)
    add(knit=BIG, pitch=8.5, stitch=5, w=(0.5, 1.1), color=GROOVE, alpha=0.9, tones=(165, 110), faint=0.5, clip="paint", out=["bands", "plait"])
    add(cable=CABLES, width=26, cross=13, color=GROOVE, w=(4.5, 7.0), tones=(165, 110), faint=0.85, jit=1.3, sides=0.8, clip="paint", out="bands")
    # 5. what must read as made: the bands (a thin cast shadow beside them, ribs across), the buttons
    add(stroke=[(490, 352), (462, 394), (432, 436), (398, 480), (368, 520), (350, 548)], w=(3, 5, 4), feather=-1, alpha=0.7, **f)
    add(stroke=[(286, 398), (289, 440), (294, 480), (301, 516), (312, 548)], w=(3, 5, 4), feather=1, alpha=0.7, **f)
    add(stroke=[(352, 560), (347, 602), (339, 660), (331, 712), (321, 765), (312, 813), (305, 865), (301, 912), (300, 960)], w=(4, 9, 7, 5), color=SHADE, feather=-1, alpha=0.7, clip="paint")
    band = dict(w=1.0, color=RIB, p=(0.5, 0.9, 0.5), broken=0.2, wobble=0.3, vary=0.4, clip="paint")
    add(pencil=ribs(BAND_L, 22, 5.5, 1, lean=0.2) + ribs(BAND_R, 24, 5.5, 2, lean=-0.25), alpha=0.5, **band)
    add(pencil=ribs(PLACKET, 38, 5.5, 3), alpha=0.45, **band)
    add(stroke=HEM + CUFFS, w=28, color=TURN, alpha=0.6, clip="paint", soft=2.5)
    add(pencil=sum((ribs(h, 28, 5.5, 4 + i, skip=0.1) for i, h in enumerate(HEM + CUFFS)), []), alpha=0.55, **band)
    for b in BUTTONS:                                                # buttons: cast shadow, the button with a dried rim, a glint, an arc
        add(path=ring((b[0] - 2, b[1] + 2.5), 10.5), wash=SHADE, soft=2, alpha=0.8, clip="paint", wobble=0)
        add(path=ring(b, 9), wash="#5D5B52", alpha=1.0, rim=0.9, wobble=0.3, grain=0.05, pool=0)
        add(path=ring((b[0] + 2, b[1] - 2.5), 3, n=6), lift=0.35, soft=1.2, wobble=0)
        add(pencil=[(b[0] - 7, b[1] + 5), (b[0], b[1] + 9.5), (b[0] + 8, b[1] + 4.5)], w=1.0, p=(0.4, 0.9, 0.4), broken=0.1)
    # 6. pencil, last and little: the overlaps, the silhouette in pieces
    g = dict(w=1.1, broken=0.45, wobble=0.5)
    add(pencil=TRUNK_L[1:], p=(0.2, 0.6, 0.9, 0.8, 0.5, 0.8, 0.4), **g)
    add(pencil=ARM_IN, p=(0.5, 0.9, 0.7, 0.9, 0.4, 0.7, 0.3), **g)
    add(pencil=[n[:2] for n in V_R[2:]], p=(0.3, 0.7, 0.5, 0.9), **g)
    add(pencil=[(334, 534)] + [n[:2] for n in V_L], p=(0.9, 0.5, 0.3, 0.6), **g)
    add(pencil=[(232, 428), (198, 454), (186, 482), (176, 560), (162, 639)], p=(0.2, 0.7, 0.9, 0.5, 0.2), **g)
    add(pencil=[(150, 690), (125, 748), (124, 790), (116, 812), (120, 840)], p=(0.2, 0.6, 0.4, 0.8, 0.4), **g)
    add(pencil=[(520, 360), (575, 385), (628, 413), (663, 453), (680, 505)], p=(0.3, 0.8, 0.9, 0.3), **g)
    add(pencil=[(705, 640), (713, 698), (722, 740), (721, 780), (719, 812)], p=(0.2, 0.7, 0.5, 0.9, 0.4), **g)
    add(pencil=[(696, 862), (673, 902), (643, 971), (583, 1023)], p=(0.3, 0.8, 0.6, 0.3), **g)
    add(pencil=[(188, 959), (240, 994), (311, 1011), (392, 1001), (441, 991), (522, 955)], p=(0.3, 0.7, 0.4, 0.8, 0.3), **g)
    return Ls


EYES = ((310, 215.2), (384, 204.2))                                         # the irises' middles, read off look.py grid at 6x
DARK_EYE, SKIN_LINE = "#2A1F1A", "#8A6250"


def face():
    """By hand, where the brush has to be exact: thin and pale over the exact pass, each mark a decision read off the grid."""
    (ax, ay), (bx, by) = EYES
    moustache = [[(336, 272), (328, 279), (318, 287), (310, 292)], [(344, 272), (338, 281), (330, 289)], [(350, 273), (348, 281), (345, 287)], [(357, 271), (360, 279), (364, 284)],
                 [(366, 269), (373, 276), (381, 282)], [(376, 269), (386, 275), (396, 282)], [(386, 270), (395, 275), (402, 282)], [(326, 275), (317, 281), (309, 288)]]
    return [
        # the upper lids carry the weight: one tapered stroke each, running past the outer corner
        dict(stroke=[[(326.5, 216.5), (319, 212.2), (311, 210.6), (303, 213), (296.5, 218.5), (293.5, 221)], [(368, 207), (374.5, 201.8), (383.5, 199.5), (392, 201.2), (399, 204.6), (403.5, 207.4)]],
             w=(0.4, 1.2, 1.7, 1.3, 0.8, 0.3), color=DARK_EYE, alpha=0.75, vary=0),
        # the irises: one warm dark shape each, the pupil a little darker inside it; catchlights on the same side in both eyes
        dict(path=[ring((ax, ay), 4.6), ring((bx, by), 4.6)], wash="#5E4636", alpha=0.55, rim=0.3, wobble=0, pool=0, grain=0.04, clip="skin"),
        dict(path=[ring((ax, ay + 0.2), 2.2), ring((bx, by + 0.2), 2.2)], wash="#1E1512", alpha=0.8, rim=0, wobble=0, pool=0, grain=0),
        dict(path=[ring((ax + 2.4, ay - 2.5), 1.05, n=6), ring((bx + 2.4, by - 2.7), 1.05, n=6)], lift=1.0, wobble=0),
        # brows: a dry-brush stroke and a few pencil hairs
        dict(stroke=[[(283, 198), (295, 191.5), (309, 188.5), (322, 190.5), (331, 195)], [(357, 186.5), (371, 180), (387, 178.5), (400, 182.5), (410, 190)]], w=(1.0, 3.4, 3.8, 2.6, 0.8), color="#6C6864", dry=0.45, alpha=0.5, vary=0.1),
        dict(pencil=[[(290, 194), (297, 189.5)], [(302, 190.5), (310, 187.5)], [(315, 189.5), (323, 190)], [(364, 183.5), (372, 179)], [(378, 179.5), (387, 177.5)], [(392, 180), (401, 182)]], w=0.7, color="#55504C", p=(0.4, 0.9), alpha=0.6),
        # nostrils and the line of the mouth
        dict(stroke=[[(323, 262.5), (329, 266), (337, 265)], [(360, 264.5), (366, 259.5), (373.5, 262)]], w=(0.4, 1.3, 0.5), color="#5A3A30", alpha=0.55, vary=0),
        dict(stroke=[(315, 294.4), (330, 296.6), (350, 296.2), (369, 292.8), (384, 288.4)], w=(0.3, 0.9, 1.1, 0.8, 0.3), color="#7A463C", alpha=0.45, vary=0),
        # the moustache: short dry strokes that fall away from its middle, then a few light hairs lifted
        dict(stroke=moustache, w=(0.5, 1.6, 0.5), color="#77736F", dry=0.5, alpha=0.5, vary=0.4),
        dict(stroke=[[(340, 273), (333, 283)], [(354, 273), (357, 283)], [(371, 271), (379, 279)], [(392, 273), (399, 279)]], w=(0.3, 0.8, 0.3), lift=0.5, vary=0.3),
        # three kind lines by each eye: they begin a few px off the corner and begin faint
        dict(pencil=[[(291, 219.5), (285.5, 217.5), (281, 213.5)], [(291, 222.5), (285, 223.5), (280, 224.5)], [(406, 208), (412, 206.5), (417.5, 203)], [(406.5, 211), (413, 212.5), (419, 214.5)], [(405, 214), (411, 218.5), (415, 223.5)]],
             w=0.75, color=SKIN_LINE, p=(0.4, 0.6, 0.1), broken=0.2, alpha=0.5),
        # the smile folds, said once each
        dict(pencil=[[(379, 253), (390, 264), (398, 276), (402, 287)], [(320, 258), (310, 268), (303, 279)]], w=0.75, color=SKIN_LINE, p=(0.2, 0.7, 0.5, 0.1), broken=0.3, alpha=0.38),
    ]


def head(frame):
    """Shirt, trousers, skin and hair through the underdrawing, big and pale to small and dark, then the face by hand. The hair is
    grey on a pale source: areas.json gives it one step more than its row (gain 1.75, curve 1.8) and the dry strokes go deeper
    ("deeper" 1.9), until its darkest 1 / 5 % read 21 / 41 in the portrait with a median of 175: dark in its depths only."""
    x0, y0, w, h = frame
    fine = min(1.0, HEAD / 330 * 512 / w)            # head height in output px / 330 x 512 / out, at most 1
    s1 = PORTRAIT[2] / (w * fine)                    # sizes below are px of the 512 portrait
    sz = lambda *v: tuple(x * s1 for x in v)
    return fine, [
        dict(study=True, clip="shirt", sizes=sz(38, 19, 9.4, 4.3), bands=0.16, rim=0.25, finish=0.5),
        dict(trace=True, clip="shirt", color="#5B544F", skip=1.4 * s1, over=0.12, w=0.8, alpha=0.7),
        dict(study=True, clip="trousers", sizes=sz(38, 19, 9.4, 4.3), bands=0.16, rim=0.3, hard=0.6, finish=0.4),
        dict(study=True, clip="skin", sizes=sz(41, 20, 10, 5, 2.6, 1.3), bands=0.18, rim=0.08, hard=0.3, wet=0.6, tint=0.02, vary=0.04, pool=0.05, over=0.05, finish=0.9, skip=1.0 * s1),
        dict(study=True, clip="features", sizes=sz(0.85), rim=0, tint=0, vary=0, pool=0, grain=0.05, over=0.03, least=0.01, finish=1.0, wobble=0, skip=0),
        # short grey hair: masses, hard-edged round paper lights; dry strokes that carry the darks; small hard passes; the source's lines as loose graphite
        dict(study=True, clip="hair", sizes=sz(34, 17, 8.5), long=4, skip=1.2 * s1, bands=0.14, rim=0.35, hard=0.8, wet=0.3, vary=0.15),
        dict(hatch=True, clip="hair", length=sz(5, 17), density=2.6, see=1.7 * s1, w=(0.4, 1.3, 0.4), alpha=0.6, deeper=1.9, dry=0.4),
        dict(study=True, clip="hair", sizes=sz(4.3, 2.0, 1.1), long=5, skip=0.85 * s1, bands=0.1, rim=0.3, hard=0.9, wet=0.2, finish=0.8, least=0.02),
        dict(hatch=True, clip="hair", length=sz(3.4, 8.5), density=1.6, see=1.3 * s1, w=(0.3, 0.9, 0.3), alpha=0.5, deeper=1.6, dry=0.3),
        dict(trace=True, clip="hair", skip=1.2 * s1, color="#5B544F", w=0.8, full=0.18, over=0.03, broken=0.3),
    ] + face()


def figure(frame, out, with_head=True):
    x0, y0, w, h = frame
    fine, H = head(frame)
    return {"frame": frame, "out": out, "seed": 31, "weave": fine, "fine": fine, "under": UNDER[y0:y0 + h, x0:x0 + w], "masks": {k: v[y0:y0 + h, x0:x0 + w] for k, v in MASKS.items()},
            "layers": ground() + cardigan() + (H if with_head else [])}


DRAWINGS = {"sheet": figure(SHEET, 1024), "portrait": figure(PORTRAIT, 512), "body": figure(BODY, 690), "draft": figure(BODY, 690, False)}
```
