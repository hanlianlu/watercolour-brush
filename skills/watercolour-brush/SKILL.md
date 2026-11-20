---
name: watercolour-brush
description: Paint pencil-and-wash watercolour illustrations (portraits, figures, clothes, spot art) as deterministic code, no image model. Use to repaint a sketch in this look or add pictures matching a set.
---

# Watercolour brush

Two things, kept apart: a **brush system** (paper, pigment, water and strokes as code; deterministic) and a **painter's
guide** (how to make a picture with it). The system does what it is told; a good picture comes from the decisions in
the guide, made by looking. No "defaults only" mode: every automatic step is a proposal that you paint over. The engine is
four code blocks in `references/engine/`, the guide's files are in `references/`; every command is run from the engine folder.

**Engine setup, once per project:** the engine ships as four Markdown files in `references/engine/` (`wash.md`, `regions.md`,
`look.md`, `selftest.md`), each holding one code block. Save the four blocks, unchanged, as `wash.py`, `regions.py`, `look.py`
and `selftest.py` in one folder of the project (for example `art/watercolour/`; if they are already there, reuse them). They
are plain Python 3 (3.12 or newer) and need `numpy` and `opencv-python-headless`: install them as the packages' own pages say
([numpy](https://pypi.org/project/numpy/), [opencv-python-headless](https://pypi.org/project/opencv-python-headless/); the engine was tested with numpy 2.5.5 and opencv-python-headless 5.1.0.95). Then `python3 selftest.py` checks
the setup. **To start from an example**, copy its folder from `references/examples/NAME/` (`source.png`, `areas.json`, …) into
the engine folder as `examples/NAME/` and save its code block (`references/examples/NAME/NAME.md`) as `NAME.py` inside that
copy: the example finds its data beside itself (`persimmon` has no data: just its block, as `examples/persimmon/persimmon.py`).
Every command below is run from the engine folder, e.g. `python3 wash.py examples/cardigan/cardigan.py examples/cardigan/out`.

## Part 1: the brush system (`references/engine/`; each file's docstring is its manual, printed when run without arguments)

- `wash.py` — the engine. A picture is a sheet of cold-press paper and a list of layers.
  `python3 wash.py DRAWINGS.py OUT_DIR [name …]`; painted at 2x and reduced; any size to 2K.
  - **Paint**: transparent washes that multiply (lights are paper kept dry with `"out"` or taken off with `"lift"`); hard
    edges with a rim, wet stretches (`"w"` nodes), `"soft"`, `"bleed"`; `"grade"`, a wet gradient inside one shape; dry
    brush, `"feather"` strokes; graphite. **`"brush"`: a wet session of loaded brush strokes**, the unit of every large
    area: each as wide as it is pressed (`"w"`), breaking up where its `"load"` runs out; inside the session they melt
    into each other (`"wet"`), its outer boundary is one hard edge; ends `"cut"` askew, ONE side that `"melt"`s or `"drag"`s.
    **`"knit"`** and **`"cable"`**: stitches and plaits, put in after the form, their strength read off the values under them.
    A layer with a `"name"` is an area others `"clip"` to or keep `"out"` of; `"eyes"` and `"head"` give head units.
  - **Water** (off unless asked for; "Watercolour character" says where and how much): `"miss"`, `"ragged"`, `"dry"`,
    `"settle"`, `"sediment"`, `"broken"`, the layers `"bloom"` and `"sparkle"`, a layer's own `"seed"`. **From an
    underdrawing** (`"under"`, `"masks"`): `study` (washes, big and pale to small and dark), `hatch`, `trace`.
  - **Helpers** (`from wash import …`; `python3 wash.py helpers` prints every argument). A garment's values:
    `ladder` (its glazes from the source's colours), `need` (the alpha from one measured tone to the next), `toned` (a
    wash's water at the tone it arrives at, by the speck MEASURED on the source), `step_to` (both). Strokes:
    `strokes_along` (a field between two guide lines, or a shape you drew, filled with strokes that follow the form),
    `hem` (the unequal stroke ends a garment stops in: lobes, never drips). Marks: `runs`, `ribs`, `ring`, `arc`,
    `beside`, `scallop`. `nodes_of` roughs a silhouette; it is never for a shadow shape.
- `regions.py` — steps 1 and 2, seconds each. `propose SOURCE DIR` cuts the source into numbered regions and guesses
  `areas.json`; you correct it (ids, points, polygons; `"approved": true`); `build` makes masks, underdrawing, starting values.
- `look.py` — the painter's eyes and instruments; nothing in it paints; all in the source's pixel coordinates.
  **Reading the source**: `grid` (zoomed, with coordinates: every node is read off it, one per 40–50 px of a long edge;
  by eye still 10–15 px out), `tones` (rows of tones), `shapes` (an area in four values; for looking, not tracing),
  `values` (darkest 1 / 5 / 25 / 50 %, colour), `speck` (how much paper a garment's washes show: its water), `ladder`,
  `glaze`, `over`, `frame`. **Checking yourself**: `paths` (your marks over the source), `layers` (one layer or session
  ALONE, or the sheet up to layer N), `holes` (paper left open inside a session), `diff` (render minus source, cell by
  cell, and per area the share of points within 15 / 25: it steers a garment's rounds), `texture`, `setin`.
- `selftest.py` — one line per promise of the engine; run it after changing `wash.py` or `regions.py`.

### How the paint behaves
- **Washes multiply.** `light = paper × (colour / paper) ^ alpha`, per channel: a wash's colour is what it gives on
  bare paper; over paint it is a multiplier, and the same wash twice gives `colour²`. So a garment is one local
  colour and a ladder of glazes that is **this garment's own**: `SAGE, TURN, SHADE, DEEP, DARK, RIB = ladder(lit,
  shadow, dark, on=source_paper)`, from three colours read off the source (a copied ladder carries the other garment's
  hue). How strong a glaze goes is arithmetic, not eye: `need(SHADE, 114, 66)` is the alpha that takes tone 114 to 66.
- **Nothing light goes over something dark.** A button, a snap, a highlight on a dark wash comes out black unless it is
  reserved or lifted (`worked-example.md`, `winter-clothes.md` 3). So the **darker of two garments is painted second**,
  whichever lies on top in life, on ONE shared list of nodes. The lighter one runs UNDER it only if it is near paper
  or the upper one is a dark, never warm under cool at mid-tone (cream under blue-grey: mud): `look.py over UNDER UPPER`.
- **Dark is density, and the water is measured.** `"grain"`, `"pool"`, `"settle"`, `"sediment"` are shares of the pigment
  and show more as the value falls. `look.py speck SRC mask=…` reads what THIS fabric shows (a smooth coat 3–4 %, a
  padded jacket 6–10 %); `toned(KIND, tone, PAPER, speck=…)` gives each wash that (`dark-cloth.md` 1, `winter-clothes.md` 0).
- **Edges.** Hard edges get a rim. A `"w"` node softens a band about 3 × `"wet"` wide. `"clip"` / `"out"` cut hard and
  leave no rim: say that edge with a core shadow or the pencil. Shapes that share an edge share `"wobble"`.
- **Size and chance.** Paths, widths and `"wet"` are grid units; the brush's marks and the paper are sized against the
  picture (`"fine"`, `"weave"`; `starting-values.md`). A layer's chance is its own: its `"seed"` throws again.

## Part 2: the painter's guide

Read `style.md` first (the look, measured). Start a picture from one of the two worked examples, each one file and one
command (set up as in "Engine setup"): `examples/cardigan/cardigan.py` (a NEW picture from a pale sketch: head and face, grey hair, a cable cardigan
over a light shirt, plain paper behind) or `examples/winter/winter.py` (a finished picture painted AGAIN: a child, long
dark hair, a dark padded jacket, a scarf, a cable sweater, its own wash behind). `worked-example.md` walks through both;
`dark-cloth.md` and `winter-clothes.md` hold the garments' rules.

### What it can and cannot do
It repaints **surface, not manner**: paper, depth, wash edges, pencil. Identity, proportions and the way a face is
drawn come from the source; a cartoon stays a cartoon. The guide is written for people; small things take the same
marks (`references/examples/persimmon/persimmon.md`). It **cannot invent a face**: start from a drawing of this very person that already has
the charm; if it is not "what a lovely person" at a glance, stop. A code-made picture is told at 1:1 by its LARGE
GARMENTS first, then by ground and hair: that is where the looking and the hand work go.

### The order of work
0. **Study, then decide.** Put the source at 1:1 beside the pictures yours must sit with (the set it joins; with no
   set, `style.md`) and write down, before painting: which lines this look would not draw (a net of wrinkles, a closed
   contour, ink), what is behind the figure, what must read as made (frames, buttons, a zip). **A source that is already
   a finished picture in this look, to be painted again**: `"approved": true` in `areas.json`, the sheet on the source's
   paper, its ground kept; `look.py frame` finds the frame of a portrait that was cut from it.
1. **Areas.** `regions.py propose`, read `regions.png`, correct `areas.json`, `build`, read `areas.png` at 1:1.
   Cut by place first (`"within"`, polygons), then by colour; a few rounds of seconds, hand-drawn garments as polygons.
2. **Underdrawing corrections**, made by `build`: fuller values per area by what the source measures there
   (`starting-values.md`); thin dark lines on skin closed over, a third mixed back; features as drawn.
3. **Big washes**, pale, painted round the lights, **in strokes** (the next section). Clothes by hand, first; head,
   neck and hands through the underdrawing. Before the first paint: `look.py speck` (each garment's water), `tones`
   (where it is dark), `paths` (your outlines over the source). Tones are measured and stepped (`need`), not guessed.
4. **Shadows: every one is your decision.** Ten to twenty per garment: where it starts, swells and ends, which edge is
   hard, its nodes read off `look.py grid`; then laid as strokes. Never a threshold of the source traced into paths
   (`nodes_of`, a mask): mottled mud, airbrush clouds, contour-map islands, and slower than twenty decisions.
5. **Darks: committed late, and once.** Depths of the hair, under collar and chin, cores of folds, pupils, the upper
   lash line; never by darkening skin. On a garment: after the half-tone has dried, few, big and JOINED, each one
   charged stroke straight to its tone ("The darks", below); in steps a dark becomes a soft cloud.
6. **Texture after form** (a knit, cables): one layer over the finished values; a form that does not read without it
   goes back to step 4. 7. **Features**: one exact pass, then by hand, thin and pale. 8. **Pencil last**, and little:
   where one form overlaps another. 9. **Lifts** for the few lost lights. Stop when a stroke would explain the clear.

### Large areas are painted in strokes
A garment built of filled shapes is a mosaic of flat lenses, however right its values. A painter's unit there is the
stroke: a loaded brush dragged along the form, wide then narrowing, running dry. Every wash of a large garment is a
**session** of strokes (`"brush"`), big and pale first, dry, then smaller and darker (both examples).
- **Fields.** Per form, two guide lines drawn the way the brush goes: down a sleeve, with the fall of the cloth, along
  a shoulder's ridge. `strokes_along(a, spacing, to=b)` lays the strokes; you give ranges (`load`, `length`, `angle`,
  `ends`; width by `spacing` and `lap`) and a `seed`, never one value: equal strokes are a comb.
- **The local colour**: one wet session of broad loaded strokes (`load` 1.3–2, `lap` 0.8–1.3, `"wet"` 14–18), clipped
  to the garment, named. Look at it alone (`look.py layers … only=NAME`, `look.py holes`): where a sliver of paper
  stays open, one more stroke by hand. **The half-tone**: narrower strokes of unequal strength (`"wet"` 7–12, `"vary"`
  0.2), clipped to the first. **A slow turn**: its field's strokes `within=SHAPE`, `"soft"` into the damp, `"grade"`d.
- **The darks** (`winter.py`, `jacket()` step 5; `dark-cloth.md` 4). First `look.py tones`: where it is dark, where it stays light.
  Lights are shapes too: reserve them big (`"lit"`). Then ONE session of a charged brush (`"wet"` 1.5, alpha `need(DARK,
  HALF, 44)`: one colour, no steps), ten to fifteen strokes: a width per node (a point, a swell of 60–90, a lift),
  `"cut"` ends, ONE side kept, the other given away (`"melt"`, `"drag"`), an end that dissolves; paler turns by `"press"`.
- **The hem is the ends of strokes.** The garment's area is open there: the fields' guide lines END on the hem line,
  `hem(line, n, lengths, angles)` adds broad strokes. A wet end is a lobe, broader than long (narrow and wet: a DRIP;
  `hem(reach=)`); only strokes that run dry are dragged on, in the dark's own mixed colour (a glaze alone is cold grey).
- **A knit** (`cardigan.py` step 4): washes and forms as for any cloth, but calm (`"bristle"` 0.1, wide `"wet"`). Then ONE
  `"knit"` layer over the garment, `"out"` of bands and cuffs: `"pitch"` and `"stitch"` measured at 4x, colour `look.py glaze
  GROUND GROOVE`, `"tones"` its light and half-tone; a groove is two thirds of its ground at EVERY value (`"faint"` 0.5).
- **Filled shapes stay right** for the small, the flat and the exact: a lapel's face, a collar, a cast shadow with
  two hard edges, a cuff's bulge, buttons, the wash behind. **What goes wrong**: translucent ribbons (crisp darks across
  crisp darks); a comb at the hem; drips; pinstripes (`lap` too small, loads too low); airbrush (all `"soft"`); mottled
  clouds (`"pool"` on a dark); values gone dark (strokes cover more than shapes did). Darks: sausages, shards, a grey
  veil, loose leaves, a picket fence. Knit: thorns, corduroy, scratches, a printed herringbone (`winter-clothes.md`).

### Form before surface
A clean shape with texture on it is still flat: exact outlines, calm washes and ribs give a balloon for an arm.
Decide the volume before any paint; `look.py shapes` shows where the source put it.
- **Forms and their order.** A trunk, two upper arms, two forearms: tubes. Which lies in front of which? Name the
  front ones as areas; a shadow on the form behind is then cut by them (`"out"`), and its free edge can be loose.
- **The light** is ONE for a picture and for a whole set (a source's own light is kept). Every form gets three steps: the
  **light** on the side facing it; a **half-tone** where it turns; a **core** just before the far edge, darkest where
  another form lies against it (armpit, under a collar). A knit's steps keep their strokes' edges; smooth cloth is graded.
- **How big, and what shape.** Half-tone and core together cover about half of each form *by area*, the core a
  third of that; never as bands of even width down its length (a watermelon on a hanging arm). A shadow has a start,
  a swell and an end, and its ends cross the form at a slant. At most one edge runs along a form. Darker steps lie
  **inside one another** and share the dark side (as islands: camouflage; hard-edged blocks that are nested and run
  along a fold are right: `winter-clothes.md` 6). A cast shadow is one glaze, hard all round.
- **The light is one plane per form**, along it on the lit side: a reserved shape with `"soft"` 8–16 (several small
  lights in one form: camouflage). A form in front of a dark one keeps a light edge: the dark then reads as depth.
- **Which edge.** Hard where a form ends or a shadow is cast; soft where a form turns, widest for the slow turn of a
  trunk or shoulder. **Folds** only where cloth is pulled or pushed, across the form. Squint at 25 %; `look.py values`.

### Watercolour character
Form and values can be right and the picture still reads as a vector drawing or an airbrush: every edge tidy, every
wash even. Say once how each *kind* of wash dries (`POOL`, `CORE` in `cardigan.py`; `PAD`, `SOFTK` in `winter.py`; `FLAT`,
`WET`, `CAST` in `dark-cloth.md` 1). The numbers below are a mid-tone knit's; a source's own garment is measured (`look.py speck`).
- **The paint misses the drawing.** Name the garment twice: as drawn, and as painted (the same path with `"miss"`
  2–3 px of a 1024 sheet). Washes clip to the paint, the pencil keeps to the drawing: slivers of paper and small
  overruns along the silhouette. A near-white garment under it (a shirt) runs under it, or it leaves a line like piping.
- **Edges dry unevenly, where a wash is a filled shape.** `"dry"` 0.5, rim `"broken"` 0.3; a step inside a shadow:
  `"ragged"` 2–3: the edge crawls and dries hard along some stretches (throw again with `"seed"`). A dried edge or two
  that *cross* a form are wanted; not on an edge that runs along a form (stripes), nor on a slow wide turn.
- **Pigment settles.** `"settle"` 0.3–0.4 (0.5 mottles a light). `"sediment"`: 0.1 in the local colour, 0.12 in
  half-tones, 0.18–0.25 in dark cool glazes; above 0.3 it is pepper. `"pool"` 0.03–0.05 (on a dark 0.02: clouds).
- **Backruns**: `"bloom"` 0.35–0.4 on a shape 40–60 px across, open on one side, deep inside a shadow; one to three
  on a garment. **Sparkle**: one `"sparkle"` 0.2–0.3 layer through lights the brush crossed fast. **The opposite
  failure is mottled mud**: keep the lights quiet, one edge of every shadow exact, one accident per passage; halve.

### How this look paints things
Eyes, age lines, hair, glasses, teeth, collar and chin: `style.md`, "How this look paints a head".
- **Clothes, by hand**, in the six steps of `cardigan.py`: areas (the garment as drawn and as painted, the
  forms in front); the palette from `ladder()`, local colour and second wash in strokes, lit planes reserved; the forms
  turning (one ladder, no other colours) and their folds; the knit over the form; what must read as made (`ribs()`
  across bands and cuffs, buttons, a brooch the eye can name); pencil last. Dark or smooth clothes: `dark-cloth.md`.
  A padded jacket (each channel one wet gradient ending hard on its seam; joined darks), a collar as planes, a zip, a
  scarf in folds, a cable knit, long straight hair, a child's eyes (never a black dot): `winter-clothes.md`.
- **A body is not left to a `study` of the source** (thresholded folds come out as speckle and lace): by hand, its
  darks measured (`starting-values.md`). **Hands** in front of it get the care of a face.
- **Behind**: paper, and one faint grey smudge behind a shoulder (`"bleed"` 24, `"soft"` 10, alpha 0.5, `"pool"` 0.25,
  kept `"out"` of the figure, no rim). A finished picture painted again keeps its own washes (`scallop()`) or its
  place (a wall, the sea: pale and low in contrast, not blurred; `winter-clothes.md` 10).
- `worked-example.md`: a light thing on a dark wash, keeping accepted parts (`setin`), a small face.

### Look, compare, adjust
Read your own PNG at 1:1 after every change, beside the source and beside the set it joins; zoom a doubtful passage
to 3x; measure with `look.py values`, `diff` (its table steers a garment best), `speck` and `texture`, against
`starting-values.md`; change one thing at a time. Before showing anyone: the picture at 292 and 128 px (in a row of
its set, at a random place, if it joins one) AND the garments beside the source at 1:1; say honestly whether yours can
be picked out and by what. Charm first: eyes open, a person you like at a glance; a face that is not lovely is repainted.

## Gotchas
- Layers paint in order; `"clip"` / `"out"` only see names already defined. Names given by hand and the `"masks"` of
  the underdrawing are one list, and equal names add up: give a hand-drawn shape a name no mask has. `"under"` and
  `"masks"` cover the FRAME: cut them for a body frame (`v[y0:y0 + h, x0:x0 + w]`).
- An edge between a `"w"` node and a plain node is half wet: a cut line in a glaze means the next node needs `"w"`.
  `"feather": 1` (and `"melt"`, `"drag"`): the right of someone walking along the path (down the page: the viewer's left).
- A `study` reads what is already on the sheet and can only darken: keep the underdrawing's lights clean.
- Proposed regions fail on some sources (hair swallows a shirt, a pale wash behind joins the figure): that is what
  `areas.json` is for. A garment's mask takes in its pale halo and slivers of paper: its 95 % is not a paint value.
