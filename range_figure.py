"""Makes fig_range.png: for each prompt, the best, a typical (median) and the worst result of N,
ranked by CLIP score. Run: python range_figure.py"""
import argparse
from PIL import Image, ImageDraw
from common import generate, clip_scores, grid

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=8)
ap.add_argument("--steps", type=int, default=40)
ap.add_argument("--scale", type=float, default=5.0)
a = ap.parse_args()

PROMPTS = ["a gray cat sitting on a couch in a living room",
           "a brown dog sitting on the grass",
           "a plate of food on a wooden table",
           "a red bus driving down a city street"]

rows = []
for p in PROMPTS:
    ims = generate(p, a.n, a.scale, a.steps)
    sc = clip_scores(p, ims)
    order = sorted(range(a.n), key=lambda i: -sc[i])
    picks = [("Best", order[0]), ("Typical", order[a.n // 2]), ("Worst", order[-1])]
    g = grid([ims[i] for _, i in picks], [f"{name} (CLIP {sc[i]:.1f})" for name, i in picks])
    row = Image.new("RGB", (g.width, g.height + 26), "white")
    ImageDraw.Draw(row).text((6, 6), f'Prompt: "{p}"', fill="black")
    row.paste(g, (0, 26))
    rows.append(row)
    print("done:", p)

fig = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)), "white")
y = 0
for r in rows:
    fig.paste(r, (0, y)); y += r.height
fig.save("fig_range.png")
print("Saved fig_range.png")
