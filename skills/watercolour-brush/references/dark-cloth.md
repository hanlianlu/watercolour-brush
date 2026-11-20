# Watercolour brush — dark garments, smooth cloth, and five marks of a wet brush

How a dark garment keeps its depth without turning to speckled grey, how its darks are laid, and five marks that only
a wet brush makes. The dark garment of the worked examples is the padded jacket of `examples/winter/winter.py`
(`jacket()`); names in backticks are that file's unless a snippet defines its own.

## 1. Dark is density: the water is cut back as the value falls
`"grain"`, `"pool"`, `"settle"` and `"sediment"` are shares of a wash's pigment, so what the eye sees of them grows with the
pigment's density `D = ln(paper / tone)`. Measured on flat squares (speck = fine std of luminance ÷ mean luminance on a
flat patch; `look.py speck IMG mask=… | box=…` finds the flat patches of an area and prints it at three tones):

| the wash arrives at | D | engine defaults (grain 0.1, pool 0.08) | the guide's local colour (settle 0.35, sediment 0.1) | the guide's core (settle 0.4, sediment 0.2) | `toned()` multiplies by |
|---|---|---|---|---|---|
| 150 (a mid-tone sage) | 0.43 | 2.6 % | 3.9 % | 5.4 % | 1 |
| 100 | 0.84 | 4.9 % | 7.2 % | 11 % | 0.51 |
| 64 | 1.29 | 7.5 % | 11 % | 17 % | 0.33 |
| 45 (black wool) | 1.64 | 9.5 % | 13.5 % | 19 % | 0.26 |

Speck ≈ D × √((55·grain)² + (60·sediment)² + (36·pool)² + (6.5·settle)²) per cent. A smooth cloth (a wool coat) reads
3.1–3.5 % at tone 104–135 and 4.3 % at tone 55 (bare paper 0.5 %): about the same at every value, speck / D 2.5–4. So on
it the numbers of "Watercolour character" are right at a mid-tone and four times too strong on black: speckled grey
wool. **That is one fabric, not a law.** A padded jacket reads 6–10 % (speck / D 6–7: it shows the paper at every
value), a soft scarf the same: painted with this section's numbers they are a flat gouache poster (`winter-clothes.md` 0).

- **Step one: measure the source's garment** (`look.py speck SRC mask=under/mask-NAME.png`), then
  `toned(KIND, tone, PAPER, speck=measured)`: the four are scaled, up or down, to what this fabric shows at that tone.
- **Unmeasured, or when the measurement says smooth (speck / D under 4)**: every wash takes the water of the tone it
  ARRIVES at by the plain rule, `toned(KIND, tone, PAPER)`: the four × 0.43 / D (never raised); `step_to()` does it for a
  nested step. Nested glazes speckle on the same paper pits, so their specks add up: toning each by its own arrival
  keeps the total where a mid-tone has it (measured specks go in at × 0.85 for the same reason).
- **The local colour of a garment that is mostly dark** takes the water of the garment's *median* tone
  (`toned(FLAT, 96, PAPER)`): most of it ends under the darks, and its specks show through them.
- **Smooth cloth** (wool, a coat: no texture, read by its planes): `"settle"` off and `"pool"` 0.02 (their 10–25 px
  blotches turn a plane into a sponge; the speck measure does not see them, your eye does at 1:1), `"sediment"` 0.05, no
  `"ragged"` and no `"dry"` on a wet shadow (stippled sponge at 0.4 already), no `"bloom"` in a dark (a pale stray blob):

      FLAT = dict(pool=0.02, sediment=0.05, rim=0.3, broken=0.3, dry=0.4)     # a local colour
      WET = dict(pool=0.02, sediment=0.05, rim=0.15, broken=0.4)              # a shadow laid wet
      CAST = dict(pool=0.02, sediment=0.06, rim=0.3, broken=0.3)              # a cast shadow
      BOLD = dict(pool=0.02, sediment=0.05, rim=0.35, broken=0.3)             # the darks of a charged brush

  A knit keeps the guide's numbers, toned.
- Check: `look.py speck` on your render, same mask: within 1.5 points of the source's at each of the three tones.

## 2. Values by measurement, not by eye
- **The ladder's lit colour on a black garment** is the lightest tone it shows anywhere (the rim of a collar, 92), not
  its usual tone: the local colour is the lightest wash, everything else is a step down from it.
- **Nested steps.** Read the tones off the source (`look.py values SRC at=x,y/x,y/…`: lit 152, half-tone 114, shadow
  66, deep 42, say) and let `need(glaze, frm, to, PAPER)` give each alpha: `ln(to / frm) / ln(glaze / paper)`.
  `step_to(SHADE, 114, 66, WET, PAPER)` returns `{"wash", "alpha"}` and the toned water in one. A checked point that
  misses by more than 15 is a shape drawn too big or too small, not an alpha.
- A shape with `"clip"` to the garment and `"out"` of its lit planes starts from the tone under it: name the two or three
  big tones once (`LOCAL, HALF, DARK = …`) and write every step as from → to.
- **The paper.** A finished picture painted again: the sheet's `"paper"` is the source's (`areas.json`; `build` prints the
  line) and `ladder(…, on=PAPER, paper=PAPER)`; with the engine's paper every colour comes out lighter and cooler. A new
  picture from any other source: the sheet keeps the engine's paper and only `on=` is the source's.

## 3. Which garment is the upper wash
Nothing light goes over a dark. A near-white shirt under a darker cardigan runs under it (`cardigan.py`; only near-white:
whatever lies under a garment darkens it and pulls it to its hue, cream under a blue-grey scarf is mud; `look.py over`,
`winter-clothes.md` 5); a black turtleneck under a lighter coat would blacken the lapels. **The darker garment is painted
second, whichever is "on top" in life**, and the edge the two share is ONE list of nodes used by both outlines (in
`winter.py` the scarf and the sweater meet on `WRAP_LOW`, the sweater and the jacket's fronts on `SW_L` and `SW_R`): two
hand-drawn outlines that only nearly agree leave a paper sliver here and a double-dark stripe there. Light faces lying on the dark garment (lapels, a collar) are named areas;
the dark garment's washes need no `"out"` when the nodes are shared.

## 4. The darks: few, big, laid once (and the lights left alone)
Twenty shadow shapes filled with strokes, laid into the damp and built up in nested steps, give soft clouds, folds
that are blurred columns and single strokes of even width (sausages); half-darks laid nearly everywhere leave the
darks without force, because no light shape stands beside them. Instead:
- **Read the garment in rows of tones, before any shape** (`look.py tones SRC x0 y0 x1 y1 step=30`): per row of 30 px,
  where it is dark, half-dark, light. A coat's darks are five or so (behind the neck and along the shoulder's ridge, a
  sleeve's mass, the fold of the body, a lapel's cast shadow, a hook under the cuff); a whole side and both lapels may
  be LIGHT. Read by eye on a zoomed grid, a fold lands 30 px out.
- **The lights first**: `"lit"` shapes, soft-edged and big, that the half-tone keeps `"out"` of; small faces (lapels, a
  collar) one small step under the local colour. Then `look.py diff RENDER SRC mask=…` (blurred 6 px, a cell every
  40 px): the light shapes within 15 before any dark goes in.
- **Then ONE session of a charged brush**, when the half-tone is dry (no `"settle"`, hardly any `"pool"`, a rim;
  `"wet"` 1.5: where two strokes meet they are one dark, nothing levels out, nothing glazes), in one colour, the alpha
  that takes the half-tone straight to the dark: `FULL = need(J_DARK, HALF, DARK, PAPER)`. Five to fifteen strokes per
  garment half, each a decision: `bold(path, widths, to=…, frm=…)` gives a width at every node and the pressure that
  takes the tone under it (`frm`) to the tone read off the source (`to`):

      def bold(path, w, to=DARK, frm=TURN, fade=None, **k):
          p = need(J_DARK, frm, to, PAPER) / FULL
          return dict(path=path, w=w, press=tuple(p * f for f in fade) if fade else p, load=k.pop("load", 2.5), **k)

  - **A width at every node**: a point where the brush is set down, a swell of 60–90, a lift. Never one width.
  - **ONE side keeps its edge, the other is given away**: a fold's hard edge is the fold; its other half thins away
    into the plane beside it (`"melt"` 0.4–0.6: the half-dark flank is this stroke's own melting side, not a second
    wash). A side that only brushed the paper is `"drag"`. Sign: positive is the right hand of someone walking along
    the path.
  - **Ends**: `"cut"` askew where the brush was set down flat; one end dissolves (`fade`, a pressure falling along the
    stroke; or `"load"` just under 1 with a short `"dries"`: the last bristles break up on the tooth).
  - **Nothing over a dark, nothing over a light.** The plane between two darks stays the half-tone.
- **A garment painted wet** (a padded jacket) takes the same session at `"wet"` 4–6: its darks sit on the seams and run
  together where they meet (`winter-clothes.md` 1).
- **Cast** (under a lapel, under a collar's free edge) is still a filled shape: one glaze, hard all round, the darkest
  thing; never shadow + nested core (a halo). **Small exact faces** (lapels, a collar) are filled shapes too.
- **What goes wrong**: sausages (even width, round ends); shards (both sides crisp and both ends cut: a dark like cut
  paper; melt one side, let one end go); a plank detached from its mass (overlap it with the mass and fade its end);
  a stroke that runs dry too early (`"load"` 0.86 empties the lower half of a sleeve: keep loads of darks at 1 or
  above and thin the end with `fade`); black capsules at the hem; a paler strip inside a dark (the half-tone has a gap
  there: every dark shows what is under it, so look at the half-tone alone first).
A long edge read at three points is 40 px out in between: read a node every 40–50 px, then `look.py paths` over the source.

## 5. Five marks
**A wet gradient inside one shape or session** (`"grade"`): the wash's strength at a few points; between them it flows
with no edge, and the outline keeps its own edges. A lapel's face, a little darker up its middle, light at its lower
end; every channel of a quilted jacket (`puff()` in `winter.py`):

    add(path=FACE, **step_to(SHADE, 148, 110, WET, PAPER), clip="face", out=["edge", "lit"], grade=[((462, 880), 1.0), ((425, 1000), 0.4), ((385, 1100), 0.0)])

`"fade"` (two points, full to nothing) is the special case. Flat nested steps where the source has one graded wash give
a code-made picture away first. Give the strengths real range (1 to 0.3); 1 to 0.7 still reads flat.

**A garment is painted in strokes** (SKILL.md, "Large areas are painted in strokes": filled shapes, however well graded,
stay a mosaic of flat lenses, and a hem of tongues added to an outline reads as a comb):

    F_B = (FRONT_EDGE, SLEEVE_SIDE)                                          # a field: two guide lines down the fall of the cloth
    field = lambda F, size, seed, **k: strokes_along(F[0], size, seed=seed, to=F[1], **k)
    add(name="wash", brush=local + extra + hems, wash=LOCAL_COLOUR, wet=18, clip="paint", out=FACES)                # the local colour: one wet session
    add(brush=half + extra, **step_to(SHADE, LIT, HALF, WET, PAPER), wet=12, vary=0.22, clip=["paint", "wash"], out=FACES + ["lit"])
    add(brush=darks, wash=DARK_GLAZE, alpha=FULL, wet=1.5, clip=["paint", "wash"], out=FACES, **toned(BOLD, 50, PAPER))   # the darks: section 4

**The hem is the ends of strokes** (`hem()`): the garment's area is open below the lines where the solid paint stops
(a `HEM` line per part), the fields' strokes end there at unequal lengths and a few are dragged on (unequal distances, lengths,
widths, angles and loads; loads under 1 run dry on the tooth; a WET end is kept a lobe, broader than long, by
`hem(reach=)`: narrow and wet it is a drip). On a coat that thins out at its hem the half-tone's own ends are fewer and
shorter, so the pale wash shows beyond them (a jacket whose dark runs to its edge: `winter-clothes.md` 4). A dark that is
dragged out of a sleeve is a session of its own in the dark's mixed colour, read off the source (`"#4E4E52"`, say): a
glaze alone on bare paper is a cold grey; its strokes are thin, cut askew and half dry (`cut=(0, 35)`, `drag=0.25`,
loads 0.35–0.75: wet, with round ends, they are capsules). What goes wrong: five equal black fingers (a comb: ranges
too narrow), a blade of bare paper inside the local colour (two fields that do not meet: wide `lap`, and the session
looked at alone, `look.py holes`), everything a step too dark (strokes cover more than shapes do: tones read in rows,
targets stepped).

**A sharp light along an edge.** A band of light is paper kept from the half-tone, not paint taken off: name a stroke just
inside the edge and keep the face's second wash `"out"` of it; a thread of paper on the very edge is a `"lift"` on a
stroke, in pieces; `beside(line, d)` moves a line sideways for a stitch line and
for the dark thread of a lapel's thickness outside it. Corners take all nodes as `"c"` (flowing nodes swell the ends
into drops).

    add(name="edge", stroke=beside(EDGE, 2.4), w=4.2, soft=0.9)                       # the band, 4 px, just inside the edge
    add(path=FACE, **step_to(SHADE, 132, 92, WET, PAPER), clip="face", out="edge")    # the face goes darker, the band stays
    add(stroke=[EDGE[1:7], EDGE[7:13]], w=(0.5, 1.2, 0.5), lift=0.8)                  # the thread of paper against the dark
    add(stroke=beside(EDGE[2:9], 5.6), w=(0.5, 1.0, 0.6), color="#4A4543", alpha=0.32, soft=0.4)   # the stitch line

**A wash behind that dried with a scalloped edge** (`scallop()`): lobes of unequal width meeting in small bays, painted pale
and flat with a strong rim (a pale wash shows little of it: `"rim"` 1.4–2), and a cooler heart dropped in wet (`"soft"`
24–30, graded, clipped to the blot). Colours from the source: `look.py glaze PAPER_THERE BLOT_THERE` is the wash, `glaze
BLOT_THERE HEART_THERE` the heart. Only where the source has such a wash and is painted again (`ground()` in
`winter.py`); a new picture keeps the plain ground and one soft smudge (`ground()` in `cardigan.py`), and a rim on THAT
smudge is a grey cut-out.

    dict(name="blot", path=scallop(OUTLINE, 56, 0.16, seed=5), wash="#E8DED0", rim=1.4, broken=0.3, wobble=0, pool=0.03, grain=0.04, out=FIGURE)

**Silver inside a metal rim**: after the dark rim strokes, a thread of light just inside them, lifted, in pieces, never all
the way round: `dict(stroke=[beside(RIM_TOP[1:6], 1.5), …], w=(0.4, 0.9, 0.5), lift=0.75)`. Frames that lie inside the
`features` mask are already painted by the exact pass: hand strokes on top are thin and pale (w 0.6–1.6, alpha
0.45–0.6), or the frames double into heavy black. The same holds for lash lines and pupils over an exact pass of a
full source (alpha 0.45, not 0.8; a child's big irises: 0.3, `winter-clothes.md` 9). A far lens seen against the paper
is a cool tint (`#D3D8D6`, soft, 0.8) off skin and hair.
