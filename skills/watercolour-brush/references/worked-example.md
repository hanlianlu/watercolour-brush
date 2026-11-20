# Watercolour brush — the worked examples, decision by decision

Read beside SKILL.md (its "Engine setup" says how to save the engine and each example's code block as `.py` files). Two pictures, each one file and one command, painted by the order of work. Between them they show
both kinds of job: a new picture from a sketch, and a finished picture painted again.

    python3 wash.py examples/cardigan/cardigan.py examples/cardigan/out
    python3 wash.py examples/winter/winter.py examples/winter/out

## `examples/cardigan/`: a new picture from a pale sketch (`cardigan.py`, `areas.json`, `source.png`, `sheet.png`, `portrait.png`)
A man of sixty-five, half-length, in a moss-green cable cardigan over a white shirt. Start a new figure from this file.

0. **Study.** The source is a tinted pencil drawing. Lines this look does not draw: the net of hatching over the cardigan
   and the net of wrinkles on the face; behind him grey blots on both sides. What must read as made: five buttons on a
   ribbed band, the V band, cuffs, the hem band, the cables. The light is the source's own: upper right, a little in front.
1. **Areas** (`regions.py propose … k=16`, then `areas.json`). The proposal called everything cloth and the hair
   "behind". Corrected: hair, two regions `"within"` a box round the head; skin, two regions `"within"` a polygon round
   face and neck, and two polygons for the wrists; shirt, its regions `"within"` a polygon round collar and V, the cuffs
   added, the blot behind the collar `"cut"`; `knit` (the cardigan is painted by hand, its mask is for measuring).
2. **Starting values.** `build` prints the rows: hair "grey or fair, pale" (1.45 / 0.35 / 1.55), skin "pale", shirt
   "light", knit "mid, pale". By the checks after the first portrait (grey hair: 20–30 / 40–60 at its darkest 1 / 5 %,
   median over 140) the hair takes two steps more (`gain` 1.75, `curve` 1.8) and its hatch `deeper` 1.9, as a pale
   source does: it reads 21 / 41 with a median of 175, dark in its depths only. Skin takes `colour` 1.1: median 188,
   chroma 19. A silver head, a white shirt and a mid-tone garment make a light picture: the portrait reads 62 / 105,
   detail 2.69 / 0.55, paper tooth 1.68.
3. **The cardigan, by hand** (`cardigan()`, six steps). Its water: `look.py speck` on the source reads 8–10 % at
   speck / D 20, which is the pencil hatching and not a wash, so the knit keeps the guide's mid-tone numbers.
   - *Forms first*: the trunk lies over his right arm (`TRUNK_L`), his left arm over the trunk (`ARM_IN`); one lit plane
     per form on the side that faces the light (`LIGHTS`).
   - *Palette*: `ladder("#B2B086", "#697155", "#414B3B", on="#FBF9EE")`, three colours read off this cardigan. A light
     subject gets a garment one step deeper: local colour at alpha 1.12, the second wash at 0.7 off the lights.
   - *Shadows, each a decision*: the trunk's left side one slow wet turn; under his left arm a wedge that starts at the
     armpit as a line and swells at the waist, a core inside it, then one charged stroke; his right arm dark on the
     side the trunk stands in front of; his left arm a soft turn, a nested step, the crook as one crisp fold; a belt of
     shadow where the body's cloth gathers above the hem band; two cast shadows under the shirt's collar.
   - *Knit after form*: one `"knit"` layer (pitch 8.5, stitch 5, the colour two thirds of its ground) kept `"out"` of
     the bands and of a strip along each cable (`"plait"`); then five cables (`"cable"`, width 26, cross 13).
   - *Made things*: bands with a thin cast shadow and `ribs()` across; buttons (cast shadow, disc, glint, arc); the shirt
     runs UNDER the V (a stroke of its shadow tone laid first), so the missing paint leaves no line of paper.
   - On the knit's mask the sheet reads 46 / 68 against the source's 73 / 96 (a pale source painted a step deeper),
     chroma 20 against 19.
4. **The face, by hand** (`face()`), thin over the exact pass: one tapered stroke per upper lid, an iris and a pupil a
   little darker inside it, catchlights on the same side, brows as a dry stroke with pencil hairs, nostrils, the line
   of the mouth, the moustache as short dry strokes with a few hairs lifted, three kind lines by each eye that begin off
   the corner and begin faint, the smile folds once each.
5. **Behind**: the blots dropped; paper and one soft smudge (`ground()`).

## `examples/winter/`: a finished picture painted again (`winter.py`, `areas.json`, `source.png`, `sheet.png`, `portrait.png`)
A girl of ten in a navy padded jacket, a blue-grey scarf and a cream cable sweater; long dark hair.

0. **Study.** The source is already a watercolour in this look, so `"approved": true`: nothing is pushed, the sheet
   takes the source's paper (`PAPER`), and the pale wash behind her stays. Not drawn again: the scribble over jacket and
   hair. What must read as made: two zips, the collar's ribs, the cables, the scarf's knit.
1. **Areas**: skin and hair by regions (the pale halo of flyaways left out of the hair: flyaways are drawn by hand);
   scarf, sweater and jacket only as masks to measure with. The head goes through the underdrawing at gains 1 and
   comes out close to the source, which is right for the same picture again; the work is in the garments.
2. **Order**, because washes multiply: the wash behind, the sweater (light), the scarf, the jacket (dark), then the head,
   the hair that lies on the clothes, the face. Scarf and sweater meet on `WRAP_LOW`; the cream runs 7 px under the
   jacket's fronts (`sw_wide`: the jacket is a dark, `look.py over`); the jacket is kept `"out"` of the scarf.
3. **The jacket** (`jacket()`, `winter-clothes.md` 0–3). Water first: `look.py speck` reads 12.6–15.5 % (speck / D 11–12),
   more than a wash shows alone, because the source is hatched all over; the wash takes a padded jacket's own share
   (`J_SPECK`: speck / D 6.5, × 0.85) and the render reads 5.6–8.3 %. Tones read in rows (`look.py tones`): lit bellies
   110, half-tone 72, a baffle's turn 50, darks 30, the fold between sleeve and body 15. Then: local colour in strokes;
   ten lit shapes; the half-tone over the rest; fourteen baffles, each one `puff()`; the inside of both open fronts
   as graded planes; one WET session of darks per side (`bold()`, `"wet"` 5): in every baffle a fat stroke that sits on
   its seam and melts upwards, all of them running into the fold between sleeve and body, which is ONE fat stroke,
   widths 14 to 62; the zips as thin dark broken lines with three tiny glints lifted on them.
4. **Steering with `look.py diff`**: a garment's rounds follow its table. A whole garment 20 off is its local colour:
   the cream's lit colour is read off its lightest point (234), the jacket's off its lit bellies (110). A block of +40
   is a dark drawn too narrow (the fold), a column of −50 along the silhouette an outline 8 px too wide (the elbow). A
   scarf is drawn from rows of tones (`look.py tones … step=20`), not from its outline inwards. The sheet reads jacket
   55 / 81 % of points within 15 / 25, scarf 54 / 79, sweater 72 / 87.
5. **The scarf** (`scarf()`): 165 / 126 / 100 / 72. One reserved light per roll, the half-tone over the rest, five shadow
   blocks inside it, three darks inside those, all long with the wrap; then its knit, uneven, full in the shadows and
   nearly lost in the lights.
6. **The sweater** (`sweater()`): the scarf's cast shadow on the collar, a band where it turns under each front, the
   right front's cast shadow; `ribs()` across the roll collar; three cables.
7. **Hair** (`head()`, `winter-clothes.md` 8): masses, two passes of long dry strokes, lights lifted last, then by hand
   the bundles that lie on jacket and scarf (`OVER`), the edge strands (`EDGE`) and a few short, faint flyaways along
   the outline (`FLY`). It reads 12 / 21 at its darkest 1 / 5 %, the source 18 / 27.
8. **A child's eyes** (`face()`, `winter-clothes.md` 9): a warm iris at alpha 0.3, a pupil only a little darker, the lid
   strokes at 0.3, two catchlights lifted, a soft lower lid. Her teeth stay as the source drew them.
9. **Behind** (`ground()`): two puddles with a scalloped edge and a cooler heart, the figure's area named with the
   jacket's own `"miss"` so that wash and jacket meet without a line of paper. The portrait (hair top 4 % under the
   edge, eyes at 43 %) reads 15 / 28, detail 2.92 / 0.65, paper tooth 1.57: dark hair fills much of it, as in the source.

## Recipes for particular cases
- **A light thing on a dark wash** (a button, a gold brooch, a highlight) comes out black unless the paint is taken
  off first:

      {"path": LEAF_SHIFTED, "wash": SHADE, "soft": 2},              # its cast shadow, 2 px down and right
      {"path": LEAF, "lift": 0.85, "rim": 0},                        # back to paper
      {"path": LEAF, "wash": "#D6C283", "rim": 0.7},                 # the gold, on that paper

- **Keeping accepted parts** (a head, hands): name their area in the drawing, paint the garment under their
  edge, and lay them back with `look.py setin`. The accepted picture must be in the same frame (warp it there
  first if it was painted in another); with the same `seed`, `weave`, frame and `out` it also has the same paper.
- **A small face in a large sheet** is painted separately at face scale (its own frame, features at their own
  size) and set back into the sheet with a soft edge; at sheet scale the brush is too coarse for a face.
- **Is the source hot or pale?** Gains that lift a pale source turn a full one black and a rosy one orange-red.
  `starting-values.md` has the table, the measurement that picks the row and the checks after the first render.

## What does not work
- A face built from other people's portraits: a relative of them in a wig. A head built from solids with no
  picture: a painted figurine. The brush cannot supply drawing.
- A base with an inked outline: the outline and symbol features survive the repaint.
- A garment from a `study` of the blurred source plus thresholded fold shapes: speckle and lace. Clean hand-drawn
  shapes with no decision about forms and light: flat, a balloon arm.
- Granulation by raising `"grain"` (0.3 and more): the paper's coarse tooth comes through as blotches. Use
  `"sediment"` for a pigment that granulates and leave `"grain"` near 0.1.
