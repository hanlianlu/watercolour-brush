# Example: winter.py

The drawings file of the winter example: a child in winter clothes, a finished picture in this look painted again (`references/worked-example.md` walks through it). It paints with the engine (`references/engine/`).

Plain Python 3 (3.12 or newer); needs `numpy` and `opencv-python-headless`. It reads and writes local image files only: no network.

**Setup:** copy this folder (`source.png`, `areas.json`, `sheet.png`, `portrait.png`) into the engine folder as `examples/winter/`, and save the code block below, exactly as it is, as `winter.py` inside that copy; it finds `source.png` and `areas.json` beside itself. Then, from the engine folder, run `python3 wash.py examples/winter/winter.py examples/winter/out`.

```python
"""A child in winter clothes: a finished picture in this look painted again ("approved": true in areas.json), so it goes on the source's
own paper, keeps its values and keeps the pale wash behind it. Grid = the source's pixels (780 x 1024).

    python3 wash.py examples/winter/winter.py examples/winter/out             # from the engine folder: sheet, portrait, body, draft (about a minute)
    python3 wash.py examples/winter/winter.py examples/winter/out draft       # one drawing; `draft` is the clothes without the head, 3 s

The first run builds the underdrawing (step 2 of the order of work: areas.json + source.png -> out/under/, a few seconds). sheet.png and
portrait.png beside this file are what it paints. areas.json holds the areas as corrected in step 1 (`regions.py propose`, then by hand),
kept as polygons, so that the build needs nothing but that file and the source. What this file shows (references/winter-clothes.md and
dark-cloth.md walk through it): a padded jacket (the water chosen before any paint; every channel of the quilting one wet gradient that
ends hard on its seam; the darks one wet session that gathers on the seams and runs together; the open fronts as planes; a zip as a
thin dark broken line); a scarf in three
hard-edged value steps that run with its rolls, its knit put in afterwards, uneven and half lost in the wash; a cable-knit sweater that runs under the dark jacket and
meets the scarf on shared nodes; long dark hair (masses, strand bundles, lifted lights, edge strands, flyaways); a child's eyes by
hand; the wash behind as two puddles with a scalloped edge.

    E=examples/winter
    python3 look.py speck $E/source.png mask=$E/out/under/mask-jacket.png                           # before anything: the jacket's water
    python3 look.py tones $E/source.png 60 400 720 1024 step=30                                     # where it is dark, before any shape
    python3 look.py paths $E/winter.py draft $E/source.png $E/out/paths.png scale=1.25 kinds=path,area
    python3 look.py holes $E/winter.py draft                                                        # paper left open inside the local colours
    python3 look.py diff  $E/out/draft.png $E/source.png frame=20,330,740,694 areas=$E/out/under/masks.npz    # steers every round
"""
import os
import shutil

import numpy as np
from wash import ladder, need, ribs, ring, scallop, step_to, strokes_along, toned

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
PAPER = "#FBF8ED"                                     # areas.json's paper: the same picture again is painted on the source's own paper
PORTRAIT, SHEET, BODY, HEAD = (230, 108, 380, 380), (0, 0, 780, 1024), (20, 330, 740, 694), 247
BODY_MASKS = ("skin", "hair", "features")             # the head's areas; the garments are by hand and take their own names

# ---- palettes: each garment's own ladder, read off the source (look.py values at= / look.py ladder), on that paper
JK, J_TURN, J_SHADE, J_DEEP, J_DARK, J_RIB = ladder("#6B748B", "#27374F", "#0E1A2C", on=PAPER, paper=PAPER)      # a puff's lit belly 112, its turn 54, the folds 24
SCF, S_TURN, S_SHADE, S_DEEP, S_DARK, S_RIB = ladder("#9CA7B3", "#5A6A7E", "#3A4658", on=PAPER, paper=PAPER, rich=1.05)   # roll tops 165, shadow 104, valleys 70
CRM, W_TURN, W_SHADE, W_DEEP, W_DARK, W_RIB = ladder("#F2E9D6", "#C4B9A8", "#8B857B", on=PAPER, paper=PAPER)     # cream 234, under the scarf 186, beside the jacket 132

# ---- the water. look.py speck source.png mask=out/under/mask-jacket.png reads 15.5 % at tone 60, 14.3 at 72, 12.6 at 86: more than any wash
# shows by itself, because this source is hatched with pencil all over. The pencil is drawn by hand afterwards; the WASH takes a padded
# jacket's own share (speck / D 6-7: it shows the paper at every value), carried by the paper's grain, not by blotches
PAD = dict(grain=0.12, pool=0.015, sediment=0.05, rim=0.3, broken=0.3)
J_SPECK = lambda tone: 0.85 * 6.5 * float(np.log(248 / tone))
jw = lambda tone, **k: toned(dict(PAD, **k), tone, PAPER, speck=J_SPECK(tone))
jst = lambda frm, to, glaze=J_SHADE, **k: dict(jw(to, **k), wash=glaze, alpha=round(need(glaze, frm, to, PAPER), 3))
SOFTK = dict(grain=0.12, pool=0.02, sediment=0.05, rim=0.35, broken=0.3)                        # the scarf
S_SPECK = lambda tone: 0.8 * 6.5 * float(np.log(248 / tone))
sst = lambda frm, to, glaze=S_SHADE, **k: dict(toned(dict(SOFTK, **k), to, PAPER, speck=S_SPECK(to)), wash=glaze, alpha=round(need(glaze, frm, to, PAPER), 3))
field = lambda F, size, seed, **k: strokes_along(F[0], size, seed=seed, to=F[1], **k)

# ---- outlines. Every edge two garments share is ONE list of nodes
WRAP_LOW = [(384, 470), (396, 480), (412, 492), (432, 502), (455, 512), (480, 519), (497, 521), (506, 516, C)]                        # scarf / sweater
SW_L = [(390, 476), (399, 518), (412, 560), (428, 610), (443, 655), (452, 700), (464, 778), (478, 830), (486, 861), (482, 905), (479, 945), (476, 1040)]   # sweater / left front
SW_R = [(510, 530), (517, 563), (523, 596), (527, 629), (533, 680), (537, 723), (540, 767), (551, 826), (563, 885), (562, 938), (566, 980), (569, 1040)]  # sweater / right front
SCARF = [(309, 378, C), (315, 400), (335, 422), (360, 444), (384, 470, C)] + WRAP_LOW[1:] + [(534, 485), (552, 475), (562, 452), (570, 417), (556, 403), (552, 384), (529, 361), (528, 340, C), (470, 325, C),
         (390, 320, C), (330, 340, C)]
SWEATER = [(384, 470, C)] + WRAP_LOW[1:] + [(510, 530, C)] + SW_R[1:-1] + [(569, 1040, C), (476, 1040, C)] + SW_L[-2:0:-1] + [(390, 476, C)]
JL = [(390, 476, C)] + SW_L[1:-1] + [(476, 1040, C), (150, 1040, C), (165, 1018), (173, 960), (146, 926), (110, 888), (104, 860), (82, 804), (84, 787), (92, 772), (90, 760), (98, 724), (128, 660), (142, 592), (155, 568),
      (146, 552), (162, 500), (160, 472), (172, 446), (190, 420), (250, 386), (300, 388), (344, 414), (380, 446), (394, 464)]
JR = [(506, 516, C), (534, 485), (552, 475), (563, 453, C), (596, 471), (605, 489, C), (588, 520), (595, 533), (601, 561), (623, 606), (630, 652), (642, 671), (662, 714), (660, 755), (679, 773), (682, 787), (669, 811),
      (684, 840), (682, 870), (685, 929), (672, 979), (650, 995), (609, 1020), (600, 1040, C), (569, 1040, C)] + SW_R[-2:0:-1] + [(510, 530, C)]
# what is made: the two zips (the lines their teeth run along)
Z_L = [(313, 458), (318, 480), (330, 503), (347, 528), (364, 552), (380, 578), (390, 612), (398, 650), (407, 685), (416, 720), (424, 760), (432, 800), (437, 840), (441, 880), (441, 915), (440, 950), (438, 985), (436, 1020)]
Z_R = [(600, 490), (590, 510), (578, 535), (566, 560), (556, 585), (549, 622), (545, 660), (543, 690), (543, 720), (545, 750), (548, 780), (553, 815), (558, 850), (563, 885), (568, 920), (572, 960), (576, 1000)]
# the forms: where the sleeves meet the fronts, and the seams of the quilting, drawn left to right
ARM_L = [(300, 470), (290, 560), (288, 660), (284, 760), (296, 850), (330, 905)]                                 # her right sleeve / the left front
ARM_R = [(606, 500), (604, 560), (610, 640), (606, 720), (602, 800), (610, 880), (620, 950), (616, 1040)]        # the right front / her left sleeve
S_L0, S_L1, S_L2 = [(298, 568), (325, 576), (352, 582), (380, 586)], [(290, 706), (330, 716), (375, 724), (418, 730)], [(318, 850), (360, 858), (400, 864), (441, 868)]
S_A0, S_A1, S_A2 = [(160, 534), (210, 545), (260, 556), (294, 562)], [(133, 648), (190, 656), (240, 662), (286, 668)], [(82, 800), (140, 826), (200, 842), (262, 852)]
S_R0, S_R1, S_R2 = [(552, 572), (580, 578), (606, 574)], [(545, 706), (575, 710), (604, 706)], [(556, 842), (585, 848), (610, 842)]
S_B1, S_B2, S_B3, S_B4 = [(612, 662), (628, 666), (644, 674)], [(606, 754), (636, 758), (662, 756)], [(604, 816), (640, 813), (672, 812)], [(610, 880), (650, 876), (686, 872)]
# the fall of the cloth: a pair of guide lines per part, drawn the way the brush goes
F_LS = ([(170, 492), (148, 560), (127, 660), (92, 724), (78, 796)], [(292, 500), (290, 580), (288, 660), (284, 740), (290, 836)])                # her right sleeve, shoulder to elbow
F_LF = ([(74, 800), (140, 826), (200, 842), (262, 852), (318, 868)], [(104, 892), (146, 934), (190, 958), (256, 950), (326, 930)])                # ... forearm, elbow to pocket
F_LB = ([(300, 462), (290, 560), (288, 660), (284, 760), (296, 850), (330, 915), (318, 1040)], [(315, 458), (347, 528), (380, 578), (398, 650), (416, 720), (432, 800), (441, 880), (440, 950), (436, 1040)])
F_LH = ([(170, 956), (160, 1040)], [(334, 916), (322, 1040)])                                                                                    # below the forearm, to the bottom edge
F_LI = ([(313, 456), (347, 528), (380, 578), (398, 650), (416, 720), (432, 800), (441, 880), (440, 950), (436, 1040)], [(390, 498), (399, 518), (428, 610), (443, 655), (464, 778), (486, 861), (479, 945), (476, 1040)])
F_RI = ([(534, 484), (517, 563), (527, 629), (537, 723), (551, 826), (563, 885), (566, 980), (569, 1040)], [(602, 486), (566, 560), (549, 622), (543, 720), (553, 815), (563, 885), (572, 960), (577, 1040)])
F_RB = ([(600, 488), (566, 560), (549, 622), (543, 720), (553, 815), (563, 885), (572, 960), (577, 1040)], [(608, 500), (604, 560), (610, 640), (606, 720), (602, 800), (610, 880), (620, 950), (616, 1040)])
F_RS = ([(606, 500), (604, 560), (610, 640), (606, 720), (602, 800), (610, 880), (620, 950), (616, 1040)], [(612, 510), (623, 606), (642, 671), (662, 714), (679, 773), (684, 840), (692, 929), (674, 979), (640, 1040)])
HEADS = ["skin", "hair"]


def ground():
    """Behind her: the picture's own pale wash, kept because this is the same picture again. It dried as two puddles with a scalloped
    edge (scallop(): lobes and small bays, a rim that a pale wash only shows when it is strong) and a cooler heart dropped in wet."""
    Ls = []
    add = lambda **k: Ls.append(k)
    FIG = HEADS + ["fig"]
    add(name="fig", path=[JL, JR], wobble=0.3, miss=2)                    # as the jacket's paint misses its drawing, so the wash meets it with no line of paper between
    add(name="fig", path=[SCARF, SWEATER], wobble=0.3)
    left = [(262, 262), (200, 290), (140, 336), (100, 400), (88, 470), (96, 540), (66, 596), (60, 660), (96, 706), (200, 720), (300, 600), (300, 380)]
    right = [(540, 372), (600, 388), (652, 428), (692, 480), (706, 560), (700, 640), (728, 700), (724, 770), (692, 812), (600, 820), (560, 600)]
    blot = dict(rim=1.5, broken=0.3, wobble=0, pool=0.03, grain=0.04, out=FIG)
    add(name="blot_l", path=scallop(left, 50, 0.16, seed=5), wash="#DFDEDA", **blot)
    add(name="blot_r", path=scallop(right, 50, 0.16, seed=2), wash="#EAE8E0", **blot)
    add(path=[(70, 560), (130, 540), (150, 620), (124, 690), (72, 680)], wash="#EDEFF1", soft=24, clip="blot_l", out=FIG, rim=0, grade=[((84, 650), 1.0), ((120, 590), 0.6), ((140, 540), 0.1)])
    add(path=[(600, 420), (660, 450), (680, 540), (640, 600), (600, 540)], wash="#F3F3F1", soft=24, clip="blot_r", out=FIG, rim=0)
    return Ls


def sweater():
    Ls = []
    add = lambda **k: Ls.append(k)
    add(name="sw", path=SWEATER, wobble=0.3)
    # the jacket is a dark: the cream may run UNDER its fronts (look.py over), so no line of paper is left along the zips like piping
    under = [(384, 470, C)] + WRAP_LOW[1:] + [(516, 528, C)] + [(x + 7, y) for x, y in SW_R[1:]] + [(x - 7, y) for x, y in SW_L[:0:-1]] + [(383, 478, C)]
    add(name="sw_wide", path=under, wobble=0.3)
    F = ([(384, 474), (412, 590), (439, 660), (458, 780), (480, 862), (473, 946), (470, 1040)], [(516, 528), (529, 596), (539, 680), (546, 767), (569, 885), (572, 980), (575, 1040)])
    add(name="swash", brush=field(F, 26, 50, load=(1.3, 1.9), ends=(-0.5, 0.6), w=(0.8, 1.0, 1.0, 0.8), lap=1.2, angle=2) + [dict(path=[(392, 486), (440, 510), (500, 526)], w=(16, 22, 16), load=2), dict(path=[(474, 900), (472, 960), (470, 1036)], w=(14, 18, 14), load=2),
           dict(path=[(382, 468), (388, 478), (396, 490)], w=(10, 14, 12), load=2)],
        wash=CRM, wet=14, bristle=0.08, clip="sw_wide", **toned(dict(pool=0.04, settle=0.2), 234, PAPER))
    cs = lambda frm, to, glaze=W_SHADE, **k: step_to(glaze, frm, to, dict(pool=0.03, rim=0.25, **k), PAPER)
    # the scarf's cast shadow on the collar: hard along the scarf, wet downwards
    add(path=WRAP_LOW[:-1] + [(506, 516, C), (514, 540), (498, 552, W), (462, 548, W), (428, 536, W), (402, 516, W), (390, 494, W)], **cs(234, 192), wet=5, clip=["sw", "swash"], grade=[((400, 498), 0.8), ((450, 522), 1.0), ((500, 530), 1.0)])
    # it turns under the jacket on both sides: one band each, exact against the jacket, wet towards the front. Her left side (ours: right) stands in the collar's shadow
    add(path=[(390, 476, C)] + SW_L[1:] + [(488, 1040, W), (492, 945, W), (499, 861, W), (478, 778, W), (458, 660, W), (426, 560, W), (410, 524, W)], **cs(234, 196), wet=6, clip=["sw", "swash"],
        grade=[((408, 540), 1.0), ((446, 660), 0.8), ((472, 780), 0.5), ((488, 900), 0.4)])
    add(path=[(510, 530, C)] + SW_R[1:] + [(556, 1040, W), (552, 938, W), (550, 885, W), (530, 767, W), (522, 680, W), (514, 600, W), (504, 556, W)], **cs(234, 200), wet=6, clip=["sw", "swash"],
        grade=[((514, 560), 1.0), ((528, 680), 0.9), ((542, 800), 0.5), ((558, 940), 0.4)])
    add(path=[(506, 516, C), (510, 530), (517, 563), (523, 596), (527, 629), (533, 680, C), (526, 660, W), (517, 610, W), (509, 560, W)], **cs(200, 140, W_DEEP), wet=3, clip=["sw", "swash"])        # the right front's cast shadow
    # the knit, after the form: the ribs of the roll collar (across its band), its lower edge, then three cables
    add(name="collar", stroke=[(398, 530), (440, 541), (480, 546), (512, 540)], w=60, vary=0)
    add(stroke=ribs([(398, 532), (440, 543), (480, 548), (512, 542)], 54, 9, 3, lean=0.1, skip=0.1, jit=1.2), w=(1.6, 3.6, 2.0), color="#E0D4BE", soft=0.5, vary=0.45, alpha=0.9, clip="sw")
    add(stroke=[(404, 562), (440, 572), (480, 575), (514, 566)], w=(2, 4, 3), color="#C9BBA6", feather=-1, alpha=0.55, clip="sw")
    cables = [[(436, 584), (452, 640), (470, 700), (483, 800), (497, 900), (495, 1030)], [(466, 586), (478, 640), (494, 700), (506, 800), (521, 900), (521, 1030)],
              [(496, 584), (506, 640), (518, 700), (529, 800), (545, 900), (548, 1030)]]
    add(cable=cables, width=22, cross=13, color="#DCCFB9", w=(4.2, 6.6), tones=(234, 190), faint=0.8, jit=1.3, skip=0.08, sides=0.8, clip=["sw", "swash"], out="collar")
    return Ls


def scarf():
    Ls = []
    add = lambda **k: Ls.append(k)
    add(name="sc", path=SCARF, wobble=0.3, out=HEADS)
    LIT, HALF, SHADE, DARK = 165, 126, 100, 72
    F_WRAP = ([(312, 360), (366, 362), (430, 384), (480, 398), (528, 352)], [(384, 498), (437, 508), (493, 522), (534, 486), (566, 450)])
    local = field(F_WRAP, 24, 60, load=(1.3, 2.0), ends=(-0.3, 0.6), w=(0.7, 1.0, 1.0, 0.7), lap=1.3, angle=4)
    add(name="scwash", brush=local, wash=SCF, wet=12, bristle=0.08, clip="sc", **toned(SOFTK, LIT, PAPER, speck=S_SPECK(LIT)))
    # ---- three value steps, every one a few HARD-EDGED blocks that run with the wrap; each darker step lies inside the one before and
    # shares its lower (shadow) side. The lights are what the half-tone leaves: the top of each roll, one long shape per roll
    lit = [[(338, 380, C), (380, 384), (424, 396), (456, 408, C), (444, 418), (410, 414), (372, 404), (344, 396)],                                          # the roll under the chin
           [(424, 458, C), (456, 452), (484, 438), (514, 436), (540, 446), (556, 440, C), (552, 462), (528, 470), (498, 462), (470, 470), (440, 474)],                # the big roll in front
           [(536, 388, C), (552, 398), (560, 418), (552, 430, C), (542, 414)]]                                                                                     # where it climbs behind her neck
    add(name="s_lit", path=lit, wobble=0.6)
    half = field(F_WRAP, 18, 63, load=(1.3, 1.9), ends=(-0.3, 0.5), w=(0.6, 1.0, 1.0, 0.7), lap=1.2, angle=4)
    add(brush=half, **sst(LIT, HALF), wet=9, vary=0.15, clip=["sc", "scwash"], out="s_lit")
    shade = [[(330, 414, C), (360, 424), (392, 430), (420, 426, C), (396, 442), (362, 446), (334, 434)],                                                          # the valley between the rolls
             [(396, 472, C), (414, 480), (436, 490), (462, 500), (490, 506), (510, 498), (530, 478), (548, 468, C), (534, 485), (506, 516), (497, 521), (480, 519), (455, 512), (432, 502), (412, 492)],   # the big roll turns under
             [(309, 378, C), (330, 372), (344, 398), (348, 424), (362, 446), (384, 470, C), (360, 448), (335, 426), (315, 400)],                                    # its left end, in the hair's shade
             [(456, 384, C), (476, 396), (500, 410), (514, 398), (522, 360), (500, 349), (478, 366)],                                                              # under the chin
             [(470, 418, C), (496, 414), (524, 420), (540, 414, C), (526, 430), (498, 428)]]                                                                       # one crease on its right
    add(path=shade, **sst(HALF, SHADE), wobble=0.8, wet=4, clip=["sc", "scwash"])
    dark = [[(312, 384, C), (322, 404), (340, 428), (358, 448, C), (344, 440), (326, 422), (314, 402)], [(466, 388, C), (484, 398), (500, 406), (510, 394), (514, 368), (498, 364), (482, 378)],
            [(340, 428, C), (362, 436), (384, 438, C), (364, 446), (344, 440)]]
    add(path=dark, **sst(SHADE, DARK, S_DEEP), wobble=0.8, clip=["sc", "scwash"])
    # the knit of the scarf, after the blocks: soft uneven stitches that run with the wrap, full in the shadows and nearly lost in the
    # lights ("faint", "thin"), many left out ("skip"), no two alike ("jit"): texture, never a pattern that repeats
    add(knit=F_WRAP, pitch=8, stitch=6.5, w=(0.7, 1.8), color="#8D9AAB", alpha=0.75, tones=(LIT, SHADE), faint=0.32, thin=0.6, lean=0.7, loops=0.6, body=0.4, dry=0.5, jit=1.8, skip=0.3,
        clip=["sc", "scwash"])
    add(knit=F_WRAP, pitch=12, stitch=10, w=(1.4, 3.0), color="#9AA6B5", alpha=0.4, tones=(HALF, DARK), faint=0.08, thin=0.3, lean=0.5, loops=0.3, body=0.6, dry=0.6, jit=2.0, skip=0.35, seed=5,
        clip=["sc", "scwash"])                           # and a few broad soft ones in the shadows only
    return Ls


def jacket():
    Ls = []
    add = lambda **k: Ls.append(k)
    add(name="jp", path=[JL, JR], wobble=0.3, miss=2, out=HEADS + ["sc"])
    LOCAL, HALF, TURN, DARK = 110, 72, 50, 30
    # 1. the local colour: one wet session of broad strokes down each part (look.py holes after every change: the hood and the corners no field reaches take a stroke by hand)
    local = sum((field(F, 28, 10 + i, load=(1.3, 2.0), ends=(-0.4, 0.5), w=(0.7, 1.0, 1.0, 0.8), lap=1.2, angle=4) for i, F in enumerate((F_LS, F_LF, F_LB, F_LH, F_LI, F_RI, F_RB, F_RS))), [])
    tops = [dict(path=[(176, 476), (226, 428), (290, 410), (344, 444), (370, 492)], w=(30, 60, 70, 60, 30), load=2), dict(path=[(186, 506), (250, 470), (318, 474)], w=(40, 64, 40), load=2),
            dict(path=[(170, 438), (160, 480), (150, 540), (140, 600)], w=(22, 32, 36, 24), load=2), dict(path=[(90, 740), (84, 790), (100, 850)], w=(16, 24, 16), load=2),
            dict(path=[(300, 468), (310, 505), (330, 545)], w=(20, 30, 24), load=2), dict(path=[(334, 536), (346, 572), (358, 610)], w=(12, 20, 12), load=2),
            dict(path=[(304, 518), (312, 546), (322, 574)], w=(16, 24, 16), load=2), dict(path=[(174, 420), (184, 432), (190, 446)], w=(14, 16, 14), load=2)]
    add(name="jwash", brush=local + tops, wash=JK, wet=14, bristle=0.1, clip="jp", **jw(LOCAL))
    # 2. the lights: the belly of every baffle that faces the light, big and soft; the half-tone is a session over everything else
    lit = [[(182, 500), (230, 486), (276, 496), (282, 528), (236, 536), (186, 528)], [(150, 576), (200, 574), (250, 590), (246, 626), (190, 630), (146, 616)], [(110, 696), (160, 690), (214, 704), (200, 760), (140, 770), (100, 740)],
           [(196, 858), (250, 860), (300, 872), (304, 912), (250, 932), (200, 920)], [(306, 600), (350, 606), (378, 624), (372, 668), (330, 680), (300, 660)], [(352, 752), (412, 766), (404, 812), (358, 818)],
           [(336, 886), (390, 892), (434, 902), (430, 950), (380, 960), (336, 940)], [(622, 880), (660, 876), (686, 920), (670, 975), (632, 990), (616, 940)], [(560, 900), (590, 904), (606, 950), (598, 1000), (566, 1000)],
           [(640, 706), (656, 720), (656, 742), (640, 738)]]
    add(name="j_lit", path=lit, soft=9, wobble=1)
    half = sum((field(F, 22, 30 + i, load=(1.2, 1.8), ends=(-0.5, 0.5), w=(0.6, 1.0, 1.0, 0.7), lap=1.0, angle=5) for i, F in enumerate((F_LS, F_LF, F_LB, F_LH, F_LI, F_RI, F_RB, F_RS))), []) + tops
    add(brush=half, **jst(LOCAL, HALF), wet=10, vary=0.2, clip=["jp", "jwash"], out="j_lit")
    # 3. every baffle of the quilting is ONE wet gradient: thin under the seam above (its lit shoulder), full where it turns under, and
    #    it ENDS HARD on its own seam: that edge is the seam, no line is drawn. Corners on the seam, wet nodes above
    def puff(top, seam, to=TURN, seed=1, frm=HALF, lit=0.08, side=None, **k):
        T, S = [tuple(p[:2]) + (W,) for p in top], [tuple(p[:2]) + (C,) if i in (0, len(seam) - 1) else tuple(p[:2]) for i, p in enumerate(seam)]
        mid = lambda L: np.mean([p[:2] for p in L], axis=0)
        a, b = mid(top), mid(seam)
        g = [(tuple(a), lit), (tuple(a * 0.55 + b * 0.45), 0.5), (tuple(a * 0.15 + b * 0.85), 1.0), (tuple(b), 1.0)]
        add(path=T + S[::-1], **jst(frm, to), wet=8, wobble=0.6, seed=seed, clip=["jp", "jwash"], grade=g + (side or []), **k)
    puff([(304, 492), (322, 506), (344, 530)], S_L0, 48, 1, lit=0.5)                              # the left front, four baffles
    puff([(298, 598), (330, 606), (366, 614), (388, 618)], S_L1, 48, 2)
    puff([(294, 740), (335, 748), (380, 756), (424, 762)], S_L2, 50, 3)
    puff([(322, 882), (365, 890), (405, 896), (441, 900)], [(318, 1016), (365, 1020), (405, 1020), (438, 1016)], 54, 4)
    puff([(172, 492), (220, 482), (280, 490)], S_A0, 64, 5, lit=0.2)                              # her right sleeve: shoulder, upper arm, elbow, forearm
    puff([(156, 560), (205, 570), (255, 580), (292, 586)], S_A1, 50, 6)
    puff([(122, 676), (180, 684), (235, 690), (284, 694)], S_A2, 46, 7, side=[((100, 760), 0.3), ((120, 800), 0.6)])
    puff([(98, 834), (150, 852), (205, 868), (262, 876)], [(106, 892), (146, 934), (190, 958), (256, 950), (324, 930)], 50, 8)
    puff([(552, 600), (580, 606), (606, 602)], S_R1, 44, 9)                                       # the right front
    puff([(546, 734), (575, 738), (604, 734)], S_R2, 48, 10)
    puff([(558, 870), (586, 876), (612, 870)], [(568, 1010), (590, 1014), (616, 1010)], 62, 11)
    puff([(612, 690), (630, 694), (650, 702)], S_B2, 50, 12)                                      # her left sleeve
    puff([(606, 778), (636, 782), (668, 780)], S_B3, 50, 13)
    puff([(604, 836), (640, 834), (676, 834)], S_B4, 52, 14)
    # 4. the collars: planes. The inside of each open front is the darkest flat thing (it stands under the scarf and the hair); the
    #    outer face of the standing collar keeps the half-tone
    add(path=[(313, 456, C), (347, 528), (380, 578), (398, 650, C), (443, 655, C), (428, 610), (412, 560), (399, 518), (390, 476, C), (367, 480), (340, 446)], **jst(HALF, 34), wet=4, clip=["jp", "jwash"],
        grade=[((350, 500), 1.0), ((385, 560), 1.0), ((420, 640), 0.5)])
    add(path=[(506, 516, C), (534, 485), (552, 475, C), (566, 500), (578, 535), (566, 560), (556, 585), (549, 622), (545, 660, C), (533, 680, C), (527, 629), (517, 563)], **jst(HALF, 36), wet=4, clip=["jp", "jwash"],
        grade=[((530, 510), 1.0), ((545, 580), 1.0), ((540, 660), 0.6)])
    # 5. the darks: ONE wet session of a charged brush. In every baffle the dark gathers at the bottom, above its seam: a fat stroke
    #    that sits on the seam with its lower edge and melts upwards into the gradient; where two of them meet, or meet the fold
    #    between sleeve and body, they run together into one dark. Nothing stands alone in a light
    FULL = need(J_DARK, HALF, DARK, PAPER)

    def bold(path, w, to=DARK, frm=TURN, fade=None, **k):
        p = need(J_DARK, frm, to, PAPER) / FULL
        return dict(path=path, w=w, press=tuple(p * f for f in fade) if fade else p, load=k.pop("load", 2.5), **k)
    up = dict(melt=-0.55)                                 # drawn left to right: the upper side melts, the lower one keeps its edge on the seam
    L = [  # her right side (ours: left). The deep fold where the sleeve lies against the body, the darkest thing; it melts into the front
        bold([(296, 684), (292, 728), (290, 775), (294, 816), (306, 852)], (14, 50, 62, 50, 16), to=15, melt=-0.4), bold([(298, 600), (292, 640), (290, 684)], (8, 18, 16), to=30),
        bold([(266, 596), (258, 650), (252, 700), (250, 744)], (14, 30, 32, 16), to=42, frm=HALF, melt=0.5),                    # the sleeve's side that faces the body
        # the sleeve's baffles, each dark on its seam and joined to the fold at its inner end
        bold([(170, 526), (212, 536), (258, 547), (290, 553)], (8, 14, 16, 12), to=44, **up), bold([(140, 636), (190, 644), (240, 650), (284, 656)], (10, 20, 24, 22), to=32, **up),
        bold([(90, 784), (140, 810), (200, 827), (258, 838), (292, 842)], (8, 20, 28, 30, 24), to=26, **up),
        bold([(112, 880), (150, 922), (192, 944), (252, 938), (318, 920)], (8, 16, 20, 18, 12), to=34, **up),
        # the front's baffles the same way, their inner ends lost in the fold, their outer ends in the shade along the zip
        bold([(300, 558), (326, 566), (352, 572), (378, 576)], (10, 16, 16, 10), to=30, **up), bold([(292, 694), (332, 704), (376, 712), (416, 718)], (16, 24, 22, 14), to=30, **up),
        bold([(320, 838), (362, 846), (402, 852), (438, 856)], (16, 24, 22, 14), to=32, **up), bold([(326, 1004), (370, 1008), (410, 1008), (436, 1004)], (10, 18, 18, 10), to=40, **up),
        # the pocket's mouth; the mass under the forearm at the bottom edge; under the hood, behind the hair
        bold([(300, 868), (318, 890), (332, 916)], (10, 20, 10), to=20), bold([(186, 968), (236, 990), (292, 1002)], (20, 44, 32), to=36, melt=-0.4),
        bold([(300, 470), (318, 500), (340, 532), (360, 560)], (14, 28, 26, 10), to=24, frm=HALF), bold([(210, 470), (250, 452), (296, 452)], (12, 22, 12), to=40, frm=HALF)]
    R = [  # her left side: the front stands in the shade of scarf and collar; the fold between front and sleeve; a dark on every seam
        bold([(596, 498), (588, 540), (578, 580), (566, 620)], (10, 22, 22, 10), to=30, frm=HALF), bold([(606, 560), (610, 640), (606, 720), (602, 800), (610, 880)], (6, 14, 12, 14, 8), to=36, fade=(0.8, 1, 0.9, 1, 0.8)),
        bold([(554, 562), (580, 568), (604, 566)], (10, 14, 10), to=30, **up), bold([(548, 694), (576, 700), (602, 696)], (14, 20, 14), to=30, **up), bold([(558, 832), (586, 838), (608, 834)], (14, 20, 14), to=32, **up),
        bold([(612, 654), (628, 658), (644, 666)], (8, 12, 8), to=38, **up), bold([(608, 744), (636, 748), (660, 748)], (12, 18, 10), to=32, **up), bold([(606, 806), (640, 803), (670, 803)], (12, 18, 10), to=34, **up),
        bold([(612, 870), (650, 866), (684, 862)], (12, 18, 10), to=36, **up), bold([(612, 884), (630, 912), (636, 944)], (14, 22, 10), to=28)]
    add(brush=L, wash=J_DARK, alpha=FULL, wet=5, clip=["jp", "jwash"], **jw(DARK, rim=0.3))
    add(brush=R, wash=J_DARK, alpha=FULL, wet=5, clip=["jp", "jwash"], **jw(DARK, rim=0.3))
    # 6. what is made. On a dark jacket a zip is a thin dark line that breaks off and starts again, and two or three tiny glints lifted
    #    on it; a pale tape with ticks across reads as printed stitching
    add(stroke=[Z_L[0:4], Z_L[5:9], Z_L[10:13], Z_L[14:], Z_R[0:4], Z_R[5:8], Z_R[9:12], Z_R[13:]], w=(0.5, 1.5, 1.1, 0.5), color="#0A1422", alpha=0.6, vary=0.5, soft=0.4, clip="jp")
    add(stroke=[[(347, 527), (348.5, 530)], [(416, 719), (417, 722)], [(556, 584), (555, 587)]], w=(0.5, 0.9, 0.5), lift=0.4, vary=0.3)
    return Ls


EYES = ((386, 281), (456, 262))                      # the irises' middles, read off look.py grid at 7x
HAIR, HAIR_LINE = "#2B2A2C", "#5A5350"
# a lock's edge is single strands, not an outline: each begins inside the mass, runs with the silhouette and leaves it at a shallow angle
EDGE = [[(352, 142), (326, 146), (302, 160), (284, 184)], [(300, 176), (282, 212), (266, 252), (250, 296)], [(274, 252), (260, 300), (248, 345), (230, 388)], [(264, 330), (246, 380), (228, 425), (204, 462)],
        [(242, 400), (222, 446), (202, 492), (176, 530)], [(420, 138), (450, 144), (476, 158), (496, 180)], [(500, 200), (516, 240), (530, 284), (542, 322)], [(516, 300), (526, 345), (532, 385), (538, 420)],
        [(506, 350), (512, 382), (512, 408)]]
# her hair where it lies on the jacket and the scarf, outside the hair's mask: bundles and single strands that begin in the mass, no two alike
OVER = [[(300, 400), (318, 440), (338, 480), (352, 520), (360, 560)], [(280, 420), (296, 462), (320, 510), (338, 548)], [(262, 430), (262, 480), (270, 530), (286, 580)], [(236, 470), (226, 520), (222, 566), (226, 604)],
        [(192, 500), (172, 550), (158, 600), (150, 642)], [(508, 398), (516, 424), (518, 444)], [(318, 420), (332, 458), (350, 492)],
        [(270, 380), (262, 430), (252, 482), (236, 530)], [(292, 384), (296, 430), (306, 478), (326, 520)], [(250, 400), (232, 452), (214, 500), (192, 548)], [(284, 400), (276, 452), (278, 506), (292, 552)],
        [(306, 396), (322, 430), (344, 462), (364, 500), (372, 536)], [(216, 470), (196, 520), (176, 556), (164, 578)]]
# flyaways: few, short and faint; each begins IN the hair and lies along the head's outline, lifting off it only a little. None
# stands up from the crown (antennae)
FLY = [[(330, 142), (312, 148), (296, 160), (284, 174)], [(452, 142), (470, 150), (486, 162)], [(262, 300), (252, 322), (244, 346)], [(240, 380), (226, 404), (212, 424)],
       [(214, 450), (198, 476), (182, 498)], [(534, 300), (540, 322), (542, 344)], [(196, 520), (180, 548), (168, 572)]]
LIGHTS = [[(296, 178), (300, 196), (300, 214)], [(306, 172), (312, 192), (314, 212)], [(318, 170), (324, 186)], [(440, 150), (456, 160), (470, 174)], [(450, 146), (466, 154)], [(276, 240), (270, 270), (266, 300)]]


def face():
    """A child's eyes, by hand over the exact pass, thin and pale (alpha 0.3): never a black disc."""
    (ax, ay), (bx, by) = EYES
    return [
        # the iris: one warm dark-brown shape; the pupil only a little darker inside it
        dict(path=[ring((ax, ay), 6.6), ring((bx, by), 6.6)], wash="#5A433B", alpha=0.3, rim=0.2, wobble=0, pool=0, grain=0.04, clip="features"),
        dict(path=[ring((ax + 0.4, ay - 0.4), 3.0), ring((bx - 0.2, by - 0.2), 3.0)], wash="#2E2622", alpha=0.35, rim=0, wobble=0, pool=0, grain=0),
        # the upper lid carries the weight: one tapered stroke, thickest over the iris, running past the outer corner; a thin warm crease above
        dict(stroke=[[(404, 283.5), (396, 277.5), (386, 275), (376, 279), (369, 287), (364, 292)], [(447, 271), (450.5, 262.5), (458, 256.5), (468, 255), (477, 258), (482, 261.5)]],
             w=(0.4, 1.3, 1.9, 1.5, 0.9, 0.3), color="#2A211E", alpha=0.3, vary=0),
        dict(pencil=[[(399, 273.5), (388, 271), (377, 274.5), (369, 281)], [(452, 257.5), (460, 252.5), (470, 251.5), (479, 254.5)]], w=0.7, color="#9A7362", p=(0.3, 0.7, 0.6, 0.2), alpha=0.5),
        # the catchlight on the pupil's upper edge and a second, smaller one beside it: the same side in both eyes, lifted
        dict(path=[ring((ax + 1.6, ay - 2.6), 1.5, n=6), ring((bx - 1.4, by - 1.6), 1.5, n=6)], lift=0.9, wobble=0),
        dict(path=[ring((ax - 2.8, ay + 2.6), 0.8, n=5), ring((bx + 3.4, by + 3.2), 0.8, n=5)], lift=0.45, wobble=0),
        # the lower lid: a soft warm line
        dict(pencil=[[(371, 290.5), (385, 291.5), (399, 287)], [(449, 272.5), (461, 271.5), (474, 266.5)]], w=0.7, color="#B78E7D", p=(0.2, 0.6, 0.2), alpha=0.45),
    ]


def head(frame):
    """Skin and hair through the underdrawing, big and pale to small and dark; then by hand what the brush must say exactly."""
    x0, y0, w, h = frame
    fine = min(1.0, HEAD / 330 * 512 / w)
    s1 = PORTRAIT[2] / (w * fine)                     # sizes below are px of the 512 portrait
    sz = lambda *v: tuple(x * s1 for x in v)
    return [
        dict(study=True, clip="skin", sizes=sz(41, 20, 10, 5, 2.6, 1.3), bands=0.18, rim=0.08, hard=0.3, wet=0.6, tint=0.02, vary=0.04, pool=0.05, grain=0.2, over=0.05, finish=0.9, skip=1.0 * s1),
        dict(study=True, clip="features", sizes=sz(0.85), rim=0, tint=0, vary=0, pool=0, grain=0.05, over=0.03, least=0.01, finish=1.0, wobble=0, skip=0),
        # long straight dark hair: the masses, then strand bundles (few, long, broad, dry: the fall, not every wisp), then strands
        dict(study=True, clip="hair", sizes=sz(30, 15, 7.5, 3.6, 1.8), long=8, hard=0.85, wet=0.25, grain=0.2, finish=0.9),
        dict(hatch=True, clip="hair", length=sz(50, 130), density=0.8, see=6 * s1, w=(0.5, 2.0, 0.4), alpha=0.28, deeper=1.0, dry=0.5),
        dict(hatch=True, clip="hair", length=sz(30, 80), density=1.2, see=3 * s1, w=(0.2, 0.8, 0.2), alpha=0.24, deeper=1.05, dry=0.4),
        dict(stroke=LIGHTS, w=(0.4, 2.0, 1.4, 0.3), lift=0.35, vary=0.4, clip="hair"),                                        # the lights, LAST: lifted streaks along the fall
        dict(stroke=OVER, w=(1.2, 4.2, 3.4, 2.0, 0.4), color=HAIR, alpha=0.85, dry=0.12, vary=0.4, out="skin"),                 # no clip: they leave the mask
        dict(stroke=EDGE, w=(0.3, 1.5, 1.0, 0.25), color=HAIR, alpha=0.75, dry=0.35, vary=0.5),
        dict(pencil=FLY, w=0.55, p=(0.6, 0.5, 0.3, 0.1), color=HAIR_LINE, broken=0.2, alpha=0.7),
    ] + face()


BASE = {"paper": PAPER, "seed": 7}


def figure(frame, out, with_head=True):
    x0, y0, w, h = frame
    fine = min(1.0, HEAD / 330 * 512 / w)
    cut = lambda a: a[y0:y0 + h, x0:x0 + w]
    return dict(BASE, frame=frame, out=out, fine=fine, weave=fine, under=cut(UNDER), masks={k: cut(MASKS[k]) for k in BODY_MASKS},
                layers=ground() + sweater() + scarf() + jacket() + (head(frame) if with_head else []))


DRAWINGS = {"sheet": figure(SHEET, 1024), "portrait": figure(PORTRAIT, 512), "body": figure(BODY, 740), "draft": figure(BODY, 740, False)}
```
