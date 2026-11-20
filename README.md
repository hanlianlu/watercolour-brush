# watercolour-brush

An [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) for Claude that paints **pencil-and-wash watercolour illustrations as code**: portraits, figures, clothes and small spot art, in a quiet picture-book look.

![two portraits painted with the skill](docs/portraits.jpg)

Each picture is a sheet of cold-press paper and a stack of layers: transparent washes that multiply over each other, wet sessions of brush strokes that melt into one another inside a hard outer edge, graded washes, dry brush, granulation, blooms, lifted lights and broken graphite lines. The same drawing file always paints the same pixels, so a set stays in one hand and any stroke can be adjusted by editing a number. No image model is involved.

The skill is two parts, kept apart on purpose:

- **The brush system** (`scripts/`): paper, pigment, water and strokes as deterministic Python (numpy + OpenCV). It does exactly what it is told.
- **The painter's guide** (`SKILL.md`, `references/`): how Claude studies a source picture, blocks in the values, decides region by region where the darks and the dry paper go, paints faces and hands by hand, and compares the result with the source until it holds up. A good picture comes from those decisions, not from defaults, so there is no one-click mode.

## Examples

Both examples ship with the skill, with their source pictures and the full painting scripts. Left: the source; right: the painting.

![a man in a moss-green cable cardigan, source and painting](docs/cardigan.jpg)

![a girl in a navy padded jacket and a blue-grey scarf, source and painting](docs/winter.jpg)

Paint them yourself, from `skills/watercolour-brush/`:

```bash
uv run scripts/wash.py references/examples/cardigan/cardigan.py references/examples/cardigan/out
uv run scripts/wash.py references/examples/winter/winter.py references/examples/winter/out
uv run scripts/wash.py references/examples/persimmon/persimmon.py out/         # a small persimmon, every kind of mark once
uv run scripts/selftest.py
```

## Install

**Claude Code (plugin):**

```
/plugin marketplace add hanlianlu/watercolour-brush
/plugin install watercolour-brush@watercolour-brush
```

**As a plain skill:** copy `skills/watercolour-brush/` into `~/.claude/skills/` (Claude Code), or zip that folder and upload it under Customize → Skills on claude.ai (code execution must be on).

Then ask Claude for something like *"paint this sketch as a watercolour portrait"* or *"add three more portraits that match these watercolours"*.

## What's inside

```
skills/watercolour-brush/
  SKILL.md                     when to use it, the brush system, the painter's guide step by step
  scripts/wash.py              the engine: paper, washes, brush sessions, knit, graphite, water effects
  scripts/regions.py           proposes areas from a source picture and builds the underdrawing
  scripts/look.py              looking tools: values, edges, tones, differences against the source
  scripts/selftest.py          checks the engine end to end
  references/style.md          the measured style rules (values, edges, faces, hair, ground)
  references/*.md              starting values, dark cloth, winter clothes, the worked examples
  references/examples/         the two examples above, runnable
  references/examples/persimmon/   a minimal drawings file
```

## What it runs

Only local Python scripts, through [uv](https://docs.astral.sh/uv/). Each script declares its dependencies inline with exact versions (`numpy`, `opencv-python-headless`), which uv installs from PyPI the first time. The scripts read and write image files in the folders you give them. They make no network requests and send nothing anywhere.

## License

[MIT](LICENSE), code, docs and example pictures alike. Pictures you paint with it are yours.
