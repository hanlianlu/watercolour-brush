# Watercolour brush — starting values, by what the source is like

Gains that lift a pale source turn a full one black; a ladder of glazes copied from another garment drags this one
towards that garment's hue. So nothing here is copied from an example: every starting value is picked by a
measurement of *this* source, and checked by a measurement of the first render.

## 1. Measure the source

    python3 look.py values SOURCE areas=under/masks.npz      # per area: darkest 1 / 5 %, median, mean colour, chroma

`regions.py build` prints the same lines, picks the row below for every area, and prints what the underdrawing then
measures next to what to aim for. (`masks.npz`: float32, 0..1, the source's size; they cover the drawing's FRAME.) Put `"gain": [gain, colour, curve, warm]` on an area in `areas.json` to overrule it.

- **Near the border of two rows the gains are a mixture of both**, in a straight line across a band round the border
  (medians: ±8 round 190 for skin, ±10 round 140 for hair and round 95 and 190 for cloth; the 5 % level: ±6 to ±8), and
  `build` prints the shares ("cloth, mid, full 53 % + cloth, dark, full 47 %"). A polygon moved by a few pixels then
  moves the gains by a hundredth (a hard switch of rows would move a coat's darks from 30 / 39 to 20 / 29).
- **The source is already a finished picture in this look, and the job is that picture again**: `"approved": true` in
  `areas.json`. Every area keeps its values (gains 1), every aim is "as the source, within 5", and the sheet is painted
  on the source's own paper (`build` prints the line; `ladder(…, on=PAPER, paper=PAPER)`). On the engine's paper the
  same washes come out lighter and cooler, because `under.npy` is what the paint lets through, not a picture.
- **The paper otherwise**: a new picture keeps the engine's paper; only `ladder(…, on=)` takes the source's.

## 2. The underdrawing (`fuller(D, gain, colour, curve, warm)` per area)

| the area in the source | how you know (luminance, 0–255) | gain | colour | curve | warm | aim, in the render |
|---|---|---|---|---|---|---|
| skin, pale | median over 190 | 1.25 | 1.0 | 1.1 | 0 | median 178–188 |
| skin, full | median 190 or less | 1.05 | 1.0 | 1.0 | 0 | median 178–188 where the face is lit; a darker skin, or a face turned from the light (164, say), stays as the source has it |
| … strong in colour (hot, rosy, orange) | chroma of the mean over 29 | | 0.9 | | | chroma 22–28: cool the colour, leave the tone |
| hair, grey / silver / fair, pale | median over 140, 5 % over 95 | 1.45 | 0.35 | 1.55 | 0.06 | 1 % at 20–30, 5 % at 40–60, median over 140 |
| hair, grey / silver / fair, full | median over 140, 5 % at 95 or less | 1.15 | 0.5 | 1.2 | 0.05 | the same: dark in its depths only, the masses grey, the lights paper |
| hair, dark, pale | median 140 or less, 5 % over 55 | 1.4 | 0.9 | 1.4 | 0 | 5 % at 29–45, 1 % at 24–36 |
| hair, dark, full | median 140 or less, 5 % at 55 or less | 1.0 | 1.0 | 1.0 | 0 | as the source, within 5 |
| cloth, light (a cream shirt) | median over 190 | 1.15 | 0.9 | 1.15 | 0 | 5 % stays over 140: paper and the shadows cast on it |
| cloth, mid, pale (sage, denim) | median 95–190, 5 % over 70 | 1.2 | 1.0 | 1.3 | 0 | 5 % at 45–60, 1 % at 28–40 |
| cloth, mid, full | median 95–190, 5 % at 70 or less | 1.05 | 1.0 | 1.1 | 0 | as the source, within 5 |
| cloth, dark, pale | median under 95, 5 % over 45 | 1.3 | 1.0 | 1.3 | 0 | 5 % at 28–35 |
| cloth, dark, full | median under 95, 5 % at 45 or less | 1.0 | 1.0 | 1.0 | 0 | as the source, within 5 |

What the numbers are: finished portraits in this look read skin median 188–191 where the face is lit, chroma 19–24;
dark hair 24–36 / 29–53 at 1 / 5 %; a grey head 26 / 53 with a median of 126; garments 5 % at 31, 34 and 60. The aims
are for the area in a 512 portrait (`look.py values PORTRAIT areas=under/masks.npz frame=x0,y0,w,h`); the underdrawing
that `build` prints lands within about 5 of them, a sheet at 1:1 reads darker at the 1 % level (its thin lines are not
averaged away). Three ways to get grey hair wrong: the pale row's gains on a full source (darkest 1 % at 12: black
hair on a silver head); gains so timid that the portrait's 1 % stays at 59 (the palest of any row by far); and
gains that look right in a row while the hair itself reads 11 / 29. A grey head that sits well reads 22 / 41–46 with
a median near 150. A grey-haired subject stays the lightest of a row; its darks are the depths of the hair, pupils,
lash line, and a garment one step deeper than a pale source.

## 3. The paint that goes with each row

| | value |
|---|---|
| hair `hatch` | `deeper` 1.2 (source full) to 1.9 (pale), `alpha` 0.5–0.6; a second pass of short strokes (`length` 4–10, `deeper` 1.2) if `look.py texture` reads under 3.0 |
| a garment by hand | `SAGE, TURN, SHADE, DEEP, DARK, RIB = ladder(lit, shadow, dark, on=source_paper)` from three colours read off this garment (`look.py ladder SOURCE lit=x,y shadow=x,y dark=x,y` prints the line); local colour at alpha 1; second wash `TURN` off the lights at 0.5 (source full) to 0.8 (pale) |
| its steps | by measurement: read lit, half-tone, shadow and deep off the source (`look.py values SRC at=…`) and let `need(glaze, frm, to)` give each alpha; the water of each wash by the tone it arrives at, `toned()` / `step_to()` (`dark-cloth.md`) |
| its colour | chroma on the garment's mask within 1 of the source's; if it reads greyer (pencil, knit lines and specks of paper grey a wash), `ladder(…, rich=1.2)` |
| its darks | source full: 1 / 5 % within 5 of the source's on the garment's mask; source pale: about 12–20 under the source's, never under the row's aim |
| paper | `"tooth"` 1 (the default) reads 1.5 with `look.py texture`, inside the look's 1.2–1.8 |
| a sheet | `"fine"` and `"weave"` = head height in output px (hair top to chin) / 330 × 512 / `"out"`, at most 1: 0.65 for a half-length at 1024, 1 for a 512 portrait. `study` / `hatch` sizes are px of a 512 picture times `"fine"`: to say them in grid units, multiply by 512 / (frame width × fine) |
| a small face | the head under 250 px high in the output: paint it apart at face scale and set it in (`look.py setin`); above that, paint it in the sheet |

## 4. After the first render (do not skip: one line here saves three renders)

    python3 look.py values SHEET SOURCE areas=under/masks.npz                     # pictures on the source's grid
    python3 look.py values PORTRAIT areas=under/masks.npz frame=220,84,600,600    # a frame of it
    python3 look.py texture PORTRAIT APPROVED.jpg

- Darkest 1 % of the whole 512 portrait under 25: something is over-pushed. On a light subject it is the hair or
  the garment; on a dark one the garment's core glazes. Never answer by lightening skin.
- Grey hair (its area, in the portrait) whose median is under 140 or whose 1 % is under 18: black hair on a
  silver head. Its 1 % over 35: no depth, the picture will be picked out of a row as pale. Dark hair whose 5 % is
  over 50: washed out. One step is `gain` ∓0.1 with `curve` ∓0.1; the hatch `deeper` changes the result less.
- Skin median outside 178–188 on a lit face, or chroma over 28: change `gain` or `colour` by 0.1 and build again (one
  second). The number to hold is the underdrawing's: the finished skin reads up to 5 under it (`over`, pencil, frames).
- A garment's mean hue has moved against the source (olive towards teal, navy towards violet): the glazes are not
  this garment's. Run `look.py ladder` on this source and use what it prints.
- Paper tooth outside 1.2–1.8: a `"tooth"` was set by hand, or `"weave"` does not fit the frame.
- Detail (512 portrait) depends on the subject, so compare with a finished portrait nearest in kind, or with the
  source's own crop when you paint a finished picture again (within 0.3 / 0.06). Portraits in this look read: sleek
  short hair and plain cloth 2.11 / 0.45, a bob and a shirt 2.80 / 0.46, long straight hair 3.00 / 0.55 and 3.56 / 0.61,
  curls, a bun, a knit 4.02 / 0.65 and 4.30 / 0.60. Under 2.1 / 0.45 it is too soft; over 4.3 / 0.65 it is busy. More
  than 0.5 under its like: add small hard passes and pencil, not darker hair strokes (they blacken a grey head
  before they sharpen it).
- Speck (`look.py speck SHEET mask=under/mask-NAME.png`, and the same on the source) more than 1.5 points off the
  source's at any of the three tones: the water does not fit this fabric (`winter-clothes.md` 0). With no source to
  measure: over 5 % on smooth cloth is pepper (`dark-cloth.md` 1).
- A garment painted by hand at the source's own values: `look.py diff SHEET SOURCE areas=under/masks.npz` (a body
  frame: `frame=x0,y0,w,h`). Its table steers every round after the first; a garment that is close has more than half
  of its points within 15 and four fifths within 25. It measures tone in place, not manner: a render can score well
  and still be clouds (read it at 1:1 beside the source). Where the values are pushed (a pale source), read the
  table for its pattern (which blocks are too light or too dark against the rest), not for its totals.
- A finished picture painted again: its washes show the paper's grain everywhere, so the `study` of skin and hair
  takes `"grain"` 0.2–0.22 (never over 0.3) and the garments their measured water; detail at the 1 px scale is
  compared after that.

## 5. What a round costs

On an idle machine: `regions.py` 3 s a step; a hand-painted garment without the head 2 s; a 512 portrait or an 888 px
sheet with a head 7–10 s; a 1024 × 1344 sheet with a knit and several studies 25 s to 1 min (`study`, `hatch` and `trace`
are most of it; four times that on a loaded machine). Work in a frame round the passage you are painting (`"body"`),
without the head while you lay shapes out (`"draft"`); a draft at half `"out"` is too coarse to judge an edge.
