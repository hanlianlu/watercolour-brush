# Watercolour brush — a padded jacket, a scarf in folds, a cable knit, long hair, a child's eyes, a place behind

The garments are where a code-made picture is told at 1:1, so most of this is about garments. Everything here is in one
runnable file, `examples/winter/winter.py` (a child in a dark padded jacket, a scarf and a cable-knit collar; long dark
hair; the names below are that file's), and the cables of a whole garment are in `examples/cardigan/cardigan.py`.

## 0. Measure before choosing the water (a step, before any garment is painted)

    python3 look.py speck SOURCE mask=out/under/mask-jacket.png
      at tone  60: speck 15.5 %   speck / D 10.9   toned(KIND, 60, PAPER, speck=15.5)
      at tone  72: speck 14.3 %   speck / D 11.6   …
      at tone  86: speck 12.6 %   speck / D 11.9   …

How much paper a wash shows is the fabric's, not the engine's. A smooth coat (`dark-cloth.md` 1) reads 3.1–4.3 % at every
tone (speck / D 2.5–4): its water is cut back as it darkens. A padded jacket painted as a plain wash reads 6–10 % (speck / D
6–7 at every tone): it shows the paper all the way down, and `toned()` without a measurement gives a flat gouache poster.
The jacket above reads more still, because that source is also hatched with pencil all over. So:
- **The speck goes into the wash**: `toned(KIND, tone, PAPER, speck=measured)` scales `"grain"`, `"pool"`, `"settle"`, `"sediment"`
  to it, up or down (`jw()`, `jst()` in the file). Without `speck=` it is the smooth-cloth rule (0.43 / D), for when the source
  measures 3–4 % or there is no source to measure. Pencil hatching in the flat patches counts as speck too (the jacket
  above; a tinted drawing reads speck / D 20): then the WASH takes the fabric's own share (`J_SPECK`: speck / D 6.5) and
  the pencil is drawn by hand, as much of it as this look draws.
- **Which of the four carries it.** `"grain"` and `"sediment"` are the paper's grain (1–4 px): that is what a speck is. `"pool"` is
  blotches 10–20 px across: on a dark it reads as clouds, a "mottled" jacket. Keep `"pool"` at 0.015–0.02 on dark or
  padded cloth and let grain carry the number (`PAD`); the slow unevenness of a real wash comes from `"grade"` and from
  strokes of unequal strength, not from noise.
- **Check your render with the same command**: within 1.5 points of a plain wash at each tone (under a hatched source by
  the hatching's share: `winter.py` reads 5.6–8.3 %). Nested washes speckle on the same pits and add up, about 1.7 over
  at tone 60, so the chosen values go in at × 0.85.
- **Stroke load follows the same reading**: where the source's wash is whole (no specks of bare paper inside the garment),
  loads are 1.3–2; loads under 1 only where the source itself breaks up (the hem of a sleeve).

## 1. A padded jacket: dark, not smooth, quilted (`jacket()`)
Three things, in this order, and each is one decision per channel of the quilting:
1. **The local colour**, the puffs' bellies: one wet session of broad strokes down every part, as for any garment.
2. **Every channel is ONE wet gradient** (`puff(top, seam, to, …)`): a filled shape from just under the seam above to the seam
   below, `"grade"`d from nearly nothing at its top (the puff's lit shoulder) to full where it turns under, **wet nodes
   along its top, corners on its seam: it ends HARD on its own seam. That edge is the seam.** No line is drawn (thin dark
   lines across read as wires; two or three pieces of 20–30 px, alpha 0.4, are the most a seam takes, where both sides are
   light). A sleeve is also a tube: give the gradient a few more points so that it stays thin down the lit side (`side=`).
3. **The darks: one session of a charged brush** (`bold()`, the alpha straight from the half-tone to the dark; the deepest,
   a fold where sleeve and body meet or the chest under a collar, a step further). `"wet"` 1.5 where the strokes keep
   their shape; `"wet"` 4–6 where the jacket is painted wet and the darks run together (`winter.py`: in every baffle a
   fat stroke sits on its seam with its lower edge and melts upwards, `"melt"` −0.55, and all of them join the fold
   between sleeve and body). Two kinds of stroke, and they touch:
   - **masses**: two or three FAT strokes side by side (widths 40–60) that are one dark when they meet (the chest under the
     collar, the gap between sleeve and front, the band above a seam). A side that should dissolve into the channel takes
     `"melt"` 0.4; never both sides.
   - **creases**: paddles, 16–30 wide with a blunt tip (the last width 6–10, not 3: needles are grass), 40–100 long, that
     **spring from a mass or from a seam**, so their feet are lost in the dark they join, and fan out: never two parallel,
     never a row of equal ones along a seam (a picket fence), never one that stands alone in a light (a loose leaf).
   Read where they are in rows of tones (`look.py tones SRC x0 y0 x1 y1 step=16`): the dark gathers at the BOTTOM of a
   channel, above its seam, and half-dark paddles hang from the seam above.
- A side of the figure that stands in shade takes a second half-tone session first so the darks have little left to do;
  lights are then only what the half-tones kept out of.
- Steer with `look.py diff draft.png source.png frame=… areas=…`: a block of +30 is a mass left out, a block of −20 a channel
  graded too far, a column of −50 along the silhouette an outline drawn too wide.
- **What goes wrong**: mottled clouds (`"pool"`); a scaffold of dark planks on a light ground (strokes 16 wide where the
  source has a mass: make them fat, lay them side by side, melt one side); thorns; a picket fence; wires for seams; a
  self-crossing channel shape (top and seam drawn in opposite directions: `look.py paths` before the first render).

## 2. A collar is planes (step 4 in `jacket()`: the open fronts)
Four things, each said once: **the face** (a named filled shape, its own value, one step off what it lies on, graded
lighter towards the fold's ridge); **the inside** (the lining, the darkest flat thing: a fat dark stroke beside the
neck); **the cast shadow** under the free edge (the mass of the darks begins exactly there, hard along the edge: the dark
session is kept `"out"` of the face, or the face is painted first and the darks clipped away); **the edge's thickness**, a
thread of light along the free edge, lifted, in pieces. A collar without its cast shadow is a flat wing; without its
inside it has no neck in it.

## 3. What is made, on a dark garment (zip, snaps)
- **A zip** on a dark garment is a thin dark line that breaks off and starts again (a `"stroke"` in pieces, w 0.5–1.5,
  alpha 0.6, `"soft"` 0.4, in a colour deeper than the garment's dark) and two or three tiny glints lifted on it (`"lift"`
  0.4, 3 px long). Never a pale tape with ticks across it, and no rows of lifted flecks along a seam, a front edge or
  a sleeve: both read as printed stitching.
- **A snap** is a light thing, so it is reserved before any wash, never lifted afterwards: a pale disc
  (`ring(c, 5.2, squash=0.8)`, `#B9BBC2`, rim 0.6) and one dark arc under it.

## 4. The hem, without drips or a second tier
- **A drip is a wet stroke end that is longer than it is wide.** A hem stroke that ends wet (load 1 or more) is a lobe:
  `hem(…, reach=1.0)` keeps it no further beyond the line than its own end width; only strokes that run dry (load under 1)
  are dragged on as far as `lengths`. A fringe is the exception (`reach=None`: thin strands are the point).
- Hem strokes are as broad as the wash's own (`w` 34–60 on a jacket), never a third of them.
- **The fields' guide lines END on the hem line**: strokes that run past it overshoot.
- **Where the hem line sits** is read, not tried: `look.py tones` along the bottom shows the row where paint gives way to
  paper; the line goes 10–15 above it (the lobes add that much). Then one `diff` row tells which way to move it.
- A jacket whose dark runs to its edge has no paler second tier: its darks' last strokes cross the hem too. "The
  half-tone's ends are fewer and shorter" (`dark-cloth.md` 5) is for a coat whose hem thins out.

## 5. Which garment runs under which: by value AND by hue
Washes multiply, so whatever lies under a garment darkens it by its own tone and pulls it to its own hue.
`python3 look.py over UNDER UPPER [PAPER]` prints the result. The lighter garment runs under the darker one **only if**
- the lower one is near paper (its tone 92 % of the paper's or more: a white shirt), **or** the upper one is a dark (under
  tone 80, where a tenth is six levels and no hue survives); **and**
- at mid-tone the two are not of opposite temperature. Cream (×0.89, warm) under a blue-grey scarf at 120–160 gives a dirty
  grey-green and a scarf 14 levels too dark.
Otherwise the two **meet on one shared list of nodes**: neither runs under the other, and the line between them is said
by the upper one's cast shadow on the lower, not left as piping. In `winter.py`: scarf and sweater meet on `WRAP_LOW`
(blue-grey over cream is the forbidden pair), and the cream runs 7 px under the dark jacket's fronts (`sw_wide`). **Against the head's masks** (skin, hair): a hand-drawn
garment is drawn generously under neck and hair and its named area takes `out=["skin", "hair"]`; otherwise slivers of
paper stand between outline and mask.

## 6. A scarf in folds: three or four hard-edged value blocks (`scarf()`)
A soft scarf wound round a neck is not a tube and not a surface to be stitched all over: it is flat blocks with hard
edges, light, half-tone, shadow, dark (`look.py shapes SRC … blur=1.5,5` shows them).
- **The lights are what the half-tone leaves**: the top of every roll, ONE long shape per roll, reserved (`"s_lit"`, hard,
  no `"soft"`); the half-tone is a session over everything else.
- **Each darker step is a few filled paths inside the step before it** (shadow inside half-tone, dark inside shadow),
  lying on its lower side, long in the direction of the wrap, with pointed ends that cross the roll at a slant. Hard
  edges, a rim, `"wet"` 4 so that a node or two can run.
- **When hard-edged blocks are right, and when they are camouflage.** Right: every block is long ALONG a fold; the steps
  are nested and share the fold's shadow side, so reading across a roll the values go light, half, shadow, dark, once;
  the lights of one roll join into one shape. Camouflage: blocks with no long axis; a dark island inside a light or a
  light island inside a dark; steps side by side instead of inside one another; several lights per roll; equal sizes.
  The rule of SKILL.md ("several small lights in one form: camouflage") stands: a scarf is several forms, one per roll,
  and each has one light.
- A knitted scarf takes its stitches AFTER the blocks, and they are texture, not pattern: one `"knit"` layer along the
  wrap, full in the shadows and nearly lost in the lights (`"faint"` 0.3, `"thin"` 0.6), uneven (`"jit"` 1.8, `"skip"` 0.3),
  then a few broad soft ones in the shadows only. Equal plaits or ticks on every roll read as a printed repeat.
- A tail that hangs: its blocks are vertical, the side turned to the jacket is the shadow, the fringe is
  `hem(…, reach=None)` in thin strokes of very unequal length, twice (local colour, then fewer in the half-tone).

## 7. A cable knit (`"cable"`; `sweater()` here, a whole garment in `cardigan.py` step 4)
`"knit"` is a fine rib. A cable is a braid: after the form, one layer

    add(cable=[MID, MID, MID], width=22, cross=13, color="#DCCFB9", w=(4.2, 6.6), tones=(234, 190), faint=0.8, jit=1.3, skip=0.08, sides=0.8, clip=["sw", "swash"], out="collar")

- `MID`: the middle line of each cable, drawn down the garment (they lean and close in as the garment does); `"width"` and
  `"cross"` read off the source at 4x. The mark is the shadow under a strand: a plump teardrop that leans in from the
  cable's side towards its middle, left and right in turn, half a crossing apart; `"sides"` are the broken grooves that
  set a cable off. `"faint"` stays high (0.85): a cable shows in the light.
- Never `ribs()` in alternating lean (a printed herringbone), never `"jit"` under 1. Count the cables on the source and
  set them as it does: close together they are a cable sweater (`sweater()`); apart, they are panels, and the plain
  knitting between them is a `"knit"` layer kept `"out"` of a band along each cable (`cardigan.py`: `"plait"`). Cables
  on a plain wash, evenly spaced, are stripes of ornament. A collar or a band is `ribs()` across it, as ever.

## 8. Long straight dark hair (through the underdrawing; `head()`)
Short-hair values lose the lights under the hatch and leave a solid shape with a soft outline. Instead:

    dict(study=True, clip="hair", sizes=(30, 15, 7.5, 3.6, 1.8), long=8, hard=0.85, wet=0.25, grain=0.2, finish=0.9)        # the masses
    dict(hatch=True, clip="hair", length=(50, 130), density=0.8, see=6, w=(0.5, 2.0, 0.4), alpha=0.28, deeper=1.0, dry=0.5)  # strand bundles
    dict(hatch=True, clip="hair", length=(30, 80), density=1.2, see=3, w=(0.2, 0.8, 0.2), alpha=0.24, deeper=1.05, dry=0.4)  # strands
    dict(stroke=LIGHTS, w=(0.4, 2.0, 1.4, 0.3), lift=0.35, vary=0.4, clip="hair")                                           # lights, LAST
    dict(stroke=OVER, w=(1.2, 4.2, 3.4, 2.0, 0.4), color=HAIR, alpha=0.85, dry=0.12, vary=0.4, out="skin")                  # where it lies on the clothes: no clip
    dict(stroke=EDGE, w=(0.3, 1.5, 1.0, 0.25), color=HAIR, alpha=0.75, dry=0.35, vary=0.5)                                   # no clip
    dict(pencil=FLY, w=0.55, p=(0.6, 0.5, 0.3, 0.1), color=HAIR_LINE, broken=0.2, alpha=0.7)

- **Strand bundles**: few, long, broad dry strokes that follow the big lie (`"see"` 6: the fall, not every wisp), then finer
  ones. `"deeper"` stays at 1.0–1.05: at 1.1 and 1.15 the darkest 1 % falls from 28 to 17. Their `"alpha"` (0.24–0.35) is set
  by the check: the hair's darkest 5 % within 5 of the source's.
- **Lights are lifted streaks**, after everything: per lock two or three long thin tapering strokes side by side along the
  fall, then none; nodes read off `look.py grid` (guessed, they fall on bare paper and are clipped away). `"lift"` 0.3–0.4:
  at 0.55 they are scratches in the paint.
- **A lock's edge is single strands, not an outline** (`EDGE`): tapered dry strokes that begin 15–30 px inside the mass, run
  with the silhouette and leave it at a shallow angle. Unequal: three alike are a second contour, and so is one that
  runs outside the mass all its length (`look.py paths` over the source shows where the mass ends).
- **Hair that lies on the clothes** (`OVER`) is outside the hair's mask: bundles and single strands that begin high in the
  mass and break up its lower end, no two parallel (a comb), hardly dry (`"dry"` 0.12: on a dark garment a dry strand
  breaks into a dotted line).
- **Flyaways** (`FLY`): few, short and faint. Each begins IN the hair and lies along the head's outline, lifting off it only
  a little; pressure falls to nothing. Begun on bare paper they are stray scratches; standing up from the crown they
  are antennae.

## 9. A child's eyes (`head()`)
A child's eye is 1.04 u wide and 0.44 u open (an adult's: 1.0 and 0.3), the iris 0.44 u, nearly half the eye. So little is
needed to turn it into a black dot.
- **The iris is one warm dark-brown shape in two values**: under the lid `#493833` (61), its lower third lighter and
  warmer (`#5A433B`, 73). The pupil is 40 % of the iris and only 20 levels darker (39): never a black disc on top. After the
  exact pass read three points (`look.py values SHEET at=…`: pupil, upper iris, lower iris); if the lower iris reads under
  60, lift a crescent there (`"lift"` 0.25–0.35), opposite the catchlight.
- **The catchlight** sits on the pupil's upper edge, about 3 px on an 800 px sheet, with a second smaller one beside it; the
  same side in both eyes, as the source has it; lifted (`ring(c, 1.5)`, `"lift"` 0.9).
- **The upper lid carries the weight**: one tapered stroke, thickest over the iris, running 6–8 px past the outer corner,
  and a thin warm crease 3 px above (`#9A7362`). By hand over an exact pass at **alpha 0.3**, not 0.45 (manga).
- The white of the eye is never paper (225, warm grey, darker under the lid); the lower lid is a soft warm line
  (`#B78E7D`) or nothing. Head units for a child: the eyes sit lower in the head (43 % of a portrait), the features closer.

## 10. Behind the figure (`ground()`)
The ground of a new picture is paper and one quiet smudge behind a shoulder (SKILL.md, "Behind"; `cardigan.py`). A
finished picture painted again keeps what it has: its own pale wash (`winter.py`: two puddles by `scallop()`, a cooler
heart dropped in; `dark-cloth.md` 5) or a real place, said softly; "softly" is low contrast, not blur. Painted first,
kept `"out"` of the figure: one named area of all its outlines, the jacket's part with the jacket's own `"miss"`, so
that wash and garment meet with no line of paper between.
- **A stone wall**: every stone one PALE wash (170–215 on paper 243), a rounded block in its course, its colour a little off
  its neighbour's (warm grey, cool grey, greenish), its edge thin and dried unevenly (`"rim"` 0.4, `"broken"` 0.5, two wet
  nodes, `"ragged"` 0.6, `"wobble"` 0.6); joints are 5–8 px of paper left between blocks, never a dark line; one joint has a
  soft shadow; one stone gets a second colour dropped in (`"soft"` 9, no rim).
- **The sea**: a band whose one hard edge is the horizon (wet below), and a few half-dry strokes (`"load"` 0.85–1.05,
  `"drag"` 0.35) that leave lines of paper.
- **What goes wrong**: everything `"soft"` 3.5 (out of focus, an airbrush); `"wobble"` 1.5 and `"ragged"` 1.2 (the blocks
  swell into each other: pebbles, a wall of hard blobs); a block of eight nodes (the curve bulges past them: a node at the
  middle of every side). Nothing behind has a hem: no stroke there ends wet in bare paper below a shape.

## 11. Small things that cost a render
- `masks.npz` is float32 0..1 at the source's size, and masks cover the FRAME: cut them for a body frame (`winter.py`).
  In `areas.json` the area written first wins where two overlap.
- `look.py holes` finds paper left inside a named session, `look.py layers` shows one layer or session alone.
- `python3 wash.py helpers [NAME …]` prints every helper's own manual. `toned()` sets `"grain"` and `"pool"` too: they
  are the engine's defaults, part of a wash's water. `need()` for a step written the wrong way round returns 0 and says so.
- Your own scripts: plain `python3 …` in the environment that runs the engine (numpy 2.5.5 and opencv-python-headless 5.1.0.95 are the tested versions).
