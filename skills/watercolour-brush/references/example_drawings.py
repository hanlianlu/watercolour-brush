"""A minimal watercolour-brush drawings file: a persimmon on a 512 grid. Every kind of mark is used once.

    uv run scripts/wash.py references/example_drawings.py out/        # from the skill's folder; out/persimmon.png
"""
C, W = "c", "w"
BODY = [(256, 150), (345, 165), (400, 250), (385, 345), (256, 385), (127, 345), (112, 250), (167, 165)]
LEAVES = [[(256, 168, C), (215, 140), (160, 150, C), (200, 175), (230, 200, C)],
          [(256, 168, C), (300, 138), (355, 152, C), (315, 178), (282, 200, C)],
          [(256, 168, C), (245, 205), (262, 232, C), (275, 200)]]

DRAWINGS = {
    "persimmon": {
        "frame": (0, 0, 512), "out": 512, "seed": 3,
        "layers": [
            {"name": "fruit", "path": BODY},                                                        # reserved first, so the smudge stays off it
            {"name": "leaves", "path": LEAVES},
            {"path": [(300, 330), (470, 300), (500, 380), (380, 420), (250, 400)], "wash": "#C9CBD0", "bleed": 14, "out": "fruit", "alpha": 0.8},
            {"path": [(130, 372), (256, 392), (400, 372), (430, 398), (256, 412), (100, 398)], "wash": "#A9A6AC", "soft": 5, "out": "fruit"},
            {"path": BODY, "wash": "#F2B25E", "out": "leaves"},                                     # first wash
            {"path": [(256, 230, W), (400, 250), (385, 345), (256, 385), (127, 345), (150, 300, W)], "wash": "#E8833A", "wet": 14, "clip": "fruit", "out": "leaves"},
            {"path": [(330, 240, W), (400, 250), (385, 345), (256, 385), (200, 372, W), (320, 330, W)], "wash": "#C4572B", "wet": 10, "clip": "fruit", "alpha": 0.7},
            {"path": [(170, 250), (215, 225), (235, 255), (195, 285)], "wash": "#E8553A", "bleed": 8, "alpha": 0.5},   # a blush, wet in wet
            {"path": [(180, 205), (215, 190), (228, 208), (192, 225)], "lift": 0.75, "soft": 5},     # the highlight, lifted
            {"path": LEAVES, "wash": "#8A9A5B"},
            {"path": LEAVES, "wash": "#566B3C", "fade": ((256, 170), (256, 140)), "rim": 0},
            {"stroke": [(256, 168), (258, 150), (266, 136)], "w": (5, 4, 6), "color": "#6B5138", "dry": 0.3},
            {"stroke": [[(150, 330), (256, 372), (360, 335)], [(140, 300), (256, 350), (372, 305)]], "w": (1, 7, 1), "color": "#B8552E", "dry": 0.7, "alpha": 0.6},
            {"stroke": [(256, 205), (250, 290), (256, 380)], "w": (4, 26, 6), "color": "#D9763A", "feather": -1, "alpha": 0.45, "clip": "fruit"},   # a crease: hard on one side
            {"pencil": [(256, 150), (345, 165), (400, 250), (385, 345), (256, 385), (127, 345), (112, 250), (167, 165), (250, 151)], "p": (0.5, 1, 0.4, 0.9, 0.5)},
            {"pencil": LEAVES[0] + LEAVES[0][:1], "w": 0.8},
            {"pencil": LEAVES[1] + LEAVES[1][:1], "w": 0.8},
        ],
    },
}
