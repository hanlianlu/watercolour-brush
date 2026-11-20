# Watercolour brush — the look, measured

The pencil-and-wash picture-book look this brush is built for, as rules and numbers. Colours are sampled means; sizes are
in px of a 512 px portrait unless given in head units (u = half the distance between the eyes). A project with its own
set of finished pictures measures them the same way (`look.py values`, `texture`, `speck`) and paints to those.

## Paper
- Cold-press, warm off-white: `#EDE6D9` … `#F8F4EA` between sheets; the engine's default is `#F5F1E7`. A finished
  picture painted again goes on its own paper (`starting-values.md`).
- The tooth is visible but quiet: on bare paper the brightness wanders by 1.2–1.8 levels of 255 (`look.py texture`,
  fine std; the engine's default `"tooth"` reads 1.5), in features from under 1 px to about 4 px, plus a slow
  mottling 20–35 px across. Anything stronger reads as a texture overlay (at 2.4 it is the first thing an eye picks out).
- Most of the sheet around the figure stays bare. Behind one shoulder there is a faint neutral-cool smudge,
  86–96 % of the paper's brightness (`#CBC7C0` … `#ECE7DD`), soft all round (painted so: SKILL.md, "Behind").
  A larger sheet may carry more: a pale wash behind each shoulder, 94 % of the paper, dried with a scalloped edge
  and a faint rim, a cooler heart (80 %) dropped in wet (`dark-cloth.md` 5, `scallop()`). They belong to a picture
  that has them and is painted again; a new picture is not given them.

## Pencil
- Fine graphite, about 1 px, never a closed outline: it breaks, changes pressure, and is strongest where one form
  overlaps another (under the jaw, where the collar meets the neck, at a lapel).
- On skin the line is warm brown (`#8A5F4C`), on hair and cloth dark grey.
- Loose hairs fly off the silhouette as single thin arcs.
- Eyelid, crease and laughter lines are pencil; brows are a dry-brush stroke with a few pencil hairs.

## Skin
- Light `#EDD0B3` / `#EAB794`; middle `#DEA887` / `#E5AD8D`; shadow `#C48668` → `#AE795D`; the deepest note, under
  the chin, `#965F43`. Lips `#CD7462`. The face is mostly middle tone: the lights are small (forehead, bridge
  and tip of the nose, tops of the cheeks, chin) and are lifted out or left.
- Blush is wet-in-wet on cheeks, nose tip and ears; on the nose it goes as deep as `#C98161`.
- One shadow glaze: under the chin (hard along the jaw, dying down the neck), the near side of the nose, under
  the nose, under the lower lip, the eye sockets, under the hair on the forehead.
- No cel edges on a face, and no blur either: a form turns with a glaze that has one hard and one wet side;
  creases (smile folds, bags under the eyes) are small shapes with a crisp edge.
- Features are kept: freckles, age spots, lines. No smoothing, no whitening.

## Features (head units, origin between the eyes)
- Eye: 1.0 u wide (inner corner 0.52, outer 1.52), opening 0.3 u; smiling 0.2 u with the lower lid pushed up into
  an arch. Small, precise, dark: the iris nearly fills the opening, a paper highlight about 2 px.
  The upper lash line is the darkest line of the face and runs past the outer corner.
- Brows at −0.6 … −0.9 u. Nose base at 1.45–1.5 u, wings ±0.65 u; nostrils are two short dark arcs, the tip a
  lifted light over a blush.
- Mouth line at 1.9–2.0 u, corners ±0.96; lower edge of the lower lip 2.5–2.65 u and soft. Smiles are closed or
  barely parted: a dark line that turns up at the corners, a thin upper lip darker than the lower.
  A crescent of white teeth reads as cartoon. A source that smiles with its teeth keeps them as drawn (they are
  features): a warm band no lighter than the light on the forehead, no line between tooth and tooth. Teeth are
  never invented, never whitened, never closed over.
- Chin 3.4–3.5 u; face half-width about 2.2 u (the far side narrower when the head turns).
- Exact first, then loose: eye shape, single or double lid, face shape, brows, nose and mouth are drawn
  precisely; the brushwork around them summarises.

## A three-quarter head (heads turned 20° to 40°)
- The unit is half the eye distance *as drawn*, so it shrinks with the turn and everything else grows against it:
  at 30° vertical measures are 1.15 times the frontal ones (mouth line 2.3 u, chin 3.9–4.0 u; at 40° the chin is 4.5 u).
- Near eye about 1.08 u wide, far eye about 0.7 u; opening a quarter of the width; iris half under the upper lid.
- The nose leaves the middle: at 30° the tip sits about 0.6 u towards the far side (0.85 u at 40°) and its far edge
  is the one place on the nose where a pencil line belongs; the near wing and a nostril arc show, the far wing hides.
- The middle of the mouth is about 0.3 u towards the far side; the far half of the mouth is the shorter one.
- Far contour of the face at −1.5 … −1.8 u (it dips at the eye socket and swells at the cheek); near side out to
  about 3 u, where the ear begins; the back of the hair reaches 4–4.5 u.
- Glasses: the far lens about 0.7 as wide as the near one and crossing the far contour; the rim line changes
  weight and breaks where the light catches it.

## How the light and shadow shapes of a face are cut
- A large light shape: the front of the forehead, the bridge of the nose, the top of the near cheek.
- One connected middle tone for the near side plane, from the temple past the outer eye corner down to the jaw,
  with a fairly definite edge; a darker strip in front of the ear.
- Sockets as two shapes that wrap the eyes, darkest beside the bridge; the near side of the nose as one wedge,
  hard along the ridge; a small dark under the tip; a fold from the wing of the nose to the corner of the mouth,
  crisp on the cheek side and dying towards the mouth; a thin shadow under the lower lip; the neck darkest
  right under the jaw.
- The shapes are angular, 10–40 px, two or three values deep, and no line surrounds them.

## Hair
- Two or three layered washes and paper left as the light. Grey hair: wash `#ADA399`, darks `#66615D` … `#57534F`,
  lights bare paper; only its depths (under a curl, behind the ear, a few per cent of it) go as dark as any hair
  (darkest 1 % at 26). Black masses on a silver head and no depth at all are both wrong (`starting-values.md`).
- Every lock has a hard edge on the shadow side; strands are dry-brush strokes that follow the lock and skip on
  the tooth; a few pencil lines on top. Curls differ in size and direction, the mass has a light side and a
  shadowed back, loose hairs leave the edge.
- Skin and hair run into each other softly at the hairline.

## Clothes
- Looser than the face: bigger shapes, deeper values than the skin (a dark sweater goes down to `#202926`), folds
  with one crisp edge. Form in three flat steps (light, half-tone, core): see "Form before surface" in SKILL.md;
  how the washes dry: "Watercolour character" there.
- Fabric texture is visible and follows the form. A chunky knit is rows of short dashes that wrap the tube; a fine
  rib is a thin line every 7–8 px of a 1024 sheet over the whole garment, broken and uneven in pressure, never ruled
  (the `"knit"` brush, after the form; its grooves are about two thirds of the ground at every value); smooth cloth
  (a wool coat) has none and reads by its planes and by a few big darks laid once; padded nylon is channels, each a
  gradient ending on its seam, with joined darks, and shows the paper's grain; a soft scarf is hard-edged value
  blocks along its folds; a cable knit is plaits (`winter-clothes.md`).
- The body turns with the head: one shoulder short, the other running off the picture.
- Towards the bottom corners the paint may thin out into bare paper.

## Three garments, as this look paints them
- **A chunky sweater**: three flat steps with dried edges; the dark takes the lower half of the upper arm; the knit
  is rows of dashes that wrap the tube, swallowed in the dark; darkest 5 % at 31.
- **A fine-ribbed top**: the light is a narrow band down each form, the rest angular shadow shapes in two or three
  values; ribs over everything; a paler strip at the far edge of the sleeve; 5 % at 60.
- **A wool coat**: no texture at all: a lit shoulder plane, a broad wet turn into a dark that takes half the sleeve,
  the lapel's hard cast shadow as the darkest thing; 5 % at 34.
- What the water does in all three: pigment that settles unevenly inside a wash and granulates in the darks; shadow
  edges that are wet for a stretch and then dry hard, a little toothed, never a smooth gradient from end to end; a
  few dried edges that cross a form; a pale backrun here and there inside a shadow; specks of bare paper where the
  brush skipped; along the silhouette a sliver of paper between paint and pencil in one place and paint over the
  line in another; a loose pencil drawing that the paint does not exactly follow. None of it is everywhere: the
  lights stay quiet, and every form still has one exact edge.

## How this look paints a head
- **Eyes**: the upper lid has weight (one tapered dark stroke that runs past the outer corner); pupil and
  catchlight are placed by hand, the same side in both eyes; the lower lid is a faint pencil line or nothing.
- **Age**: three to five kind lines (two or three by each eye, the smile folds, a soft crease under the eye, two
  faint wavy lines on the forehead); straight parallel lines look ruled, a net looks like a tinted drawing. The
  lines by an eye begin 4–5 px off its corner and begin faint (`p` 0.4–0.5 rising, alpha 0.5–0.6): drawn from the
  corner at full pressure they are long lashes.
- **Hair**: masses first, hard-edged round paper lights; many small dry strokes that follow each curl and carry
  the darks; the source's own line work said again as loose graphite; a few flyaways, pale, thin and tapering,
  that run along the silhouette and lift off it (radial ones look like static, dark looped ones like wire).
  Short dark hair is not curls: one `study` at the touch sizes below and ONE `hatch` of broad strokes (`w` to 2.2,
  `length` 14–40, `density` 1.5, `deeper` 1.05); two dense passes give wiry wool. Its spiky tips lie outside the
  mask: tapered strokes that begin 10–15 px inside the mass (begun at the silhouette they float round the head).
- **Long straight dark hair**: the short-hair values lose its lights. Strand bundles (long broad dry strokes along the
  fall), lights lifted LAST as two or three thin streaks per lock, the lock's edge single strands that leave the
  silhouette at a shallow angle, flyaways that begin in the hair (`winter-clothes.md` 8).
- **A child**: the eye is 1.04 u wide and 0.44 u open, the iris nearly half of it: one warm dark-brown shape in two
  values with a small pupil and a catchlight on its edge, the weight in the upper lid; a black disc is a manga eye.
  Hand strokes over an exact pass at alpha 0.3 (`winter-clothes.md` 9). Eyes at 43 % of a portrait's height.
- **Collar and chin**: a cast shadow under the chin and where the collar lies on the neck, hard on the casting
  edge, dying away; this is where a portrait gets its depth. A garment's collar is planes: `winter-clothes.md` 2.
- **Glasses**: a thin pale line with a broken darker arc below; never an even ring. Each rim is two strokes whose
  width changes, with a gap where the light catches it (upper left): `arc(c, rx, ry, 250, 395)` and
  `arc(c, rx, ry, 50, 205)`. One closed stroke of one width is the even ring. Dark metal frames: the same two
  strokes per rim, thin and pale where the exact features pass has already painted them, and a thread of silver
  lifted just inside the rim, in pieces (`dark-cloth.md` 5).
- **Teeth**: as the source drew them, toned (see "Features"); a closed smile is not preferred to the source's.

## Framing of a portrait
- 512 × 512, head and shoulders; the top of the hair's mass 3–6 % below the top edge (tousled hair: its flyaways
  there and its mass at 9 %); head 60–70 % of the height; eyes at 38–42 %; the whole face inside the inscribed
  circle. With tall hair the three cannot all hold: keep the hair top and the head size, and let the eyes fall
  where they then fall. A finished picture painted again takes its own portrait's frame (`look.py frame`).
- Posture open, relaxed, confident: shoulders broad and level, the head may lean. Light from the upper left.
- Charm first: the person should be someone you like at a glance.

## Measured values (512 px portrait)
- Values: a portrait reaches luminance 25–35 at its darkest 1 % and 35–50 at 5 % (dark hair, dark clothes, pupils,
  frames). A light subject (silver hair, mid-tone clothes) reaches the 1 % (25–35) through pupils, lash line and
  the depths of the hair, and stays lighter at 5 % (65–90) whatever is done: give it a garment one step deeper
  rather than a pale one, and leave it the lightest of a row.
- Detail (mean |Laplacian| of luminance after a 1 px and a 3 px blur) runs with the subject, 2.1–4.3 / 0.45–0.65:
  2.1 for sleek short hair and plain cloth, 4.0–4.3 for curls and knits (the list: `starting-values.md`, 4).
  Skin is smooth: wash steps on a cheek are under 3 % of tone; hard edges sit only at features, creases and cast
  shadows.
- Touch sizes that match: skin 40 → 1.2 px in six passes, hair 30 → 1.8 px, cloth 60 → 3.5 px.

## What gives a code-made picture away
- An invented face: plausible, never lovely. Observe one (SKILL.md, part 2). A face put together from other people's
  portraits is a relative of them in a wig, with a made-up hairline and neck; a head built from solids is a figurine.
- A dead-frontal, mirror-symmetric face and body with a closed contour; an open mouth with a white crescent of teeth.
- Softness everywhere. Use hard-and-wet shapes and a few dark accents instead of blurred glazes.
- Tidiness everywhere: even washes, smooth graded edges, paint that fills the drawing exactly. It reads as a vector
  drawing or an airbrush however right the form is ("Watercolour character" in SKILL.md).
- Blush as two discs; skin of one even colour.
- Perfect geometry (circles of glasses, even collar wings, even outline weight); one curl stamped all over.
- Clothes as flat shapes with an even texture.
- Hair that is only soft washes (it wants bristly dry strokes on top); pencil too thin to be seen.
- A base with inked contours: the outline survives as a dark even line round face and hair, and this look has no
  such line. A base built from solids: even gradients, symmetric symbol features, no folds.
- A repainted picture of another manner: paper, depth and wash edges become this look's, the drawing does not.
  Outlined cartoon features still read as cartoon.
- Next to a tinted-drawing source this look is: no scratchy wrinkle lines (form by wash, three laugh lines in
  pencil), darks about twice as deep, plain paper behind.
- A bottom edge that dissolves in scallops: a portrait runs off the bottom; thin the paint only towards the corners.
- **Form**: shadows as bands of even width down a hanging arm, each with a dried edge (a watermelon); several small
  lights or several separate pools inside one form (camouflage); a smudge behind with a rim (a grey cut-out); paper
  tooth at 2.4; a garment whose hue has drifted from the source's (glazes copied from another picture); black
  depths all over a silver head; glasses as one even closed stroke; a brooch of equal discs (berries); a shirt cut
  off at the cardigan's paint (piping).
- **Dark and smooth cloth** (`dark-cloth.md`): flat graded steps where one wet wash graded inside a shape belongs; a
  hem cut as an outline (lobes) instead of the ends of brush strokes; lapel lights lifted dull instead of reserved;
  soft clouds behind where washes dry with a scalloped edge; black wool speckled grey by a mid-tone's water; a long
  edge read at three points and 40 px out; shadow shapes traced from a threshold (mud, clouds, contour islands).
- **Winter clothes** (`winter-clothes.md`): a dark padded jacket as mottled clouds with loose leaf strokes instead of
  joined darks that spring from its seams; no collar construction; a scarf as one band instead of three or four
  hard-edged values along its folds; a cable knit as a printed herringbone; a wall of hard round blobs; drips at
  the hem; eyes as black dots; a lock of hair as a solid shape with a soft outline.
- At 292 and 128 px none of the garment faults show: look at the garments at 1:1 beside the source.
