"""Makes the figures + numbers for the report. Run: python evaluate.py"""
import csv, argparse, statistics as st
from common import generate, clip_scores, grid

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", type=int, default=8, help="how many prompts for the CLIP table")
ap.add_argument("--n", type=int, default=4, help="images per prompt for best-of-N")
ap.add_argument("--steps", type=int, default=30)
a = ap.parse_args()

PROMPTS = ["a brown dog sitting on the grass", "a plate of food on a table",
           "a man riding a skateboard", "a cat sleeping on a couch",
           "a red bus on a city street", "a girl holding an umbrella",
           "a bowl of fruit on a kitchen counter", "a horse standing in a field",
           "a bird sitting on a branch", "a pizza on a wooden table"][: a.prompts]
P = PROMPTS[0]

# Figure 1: guidance sweep
scales = [1, 3, 5, 7.5, 10]
ims = [generate(P, 1, s, a.steps, seed=42)[0] for s in scales]
grid(ims, [f"guidance {s}" for s in scales]).save("fig_guidance.png")

# Figure 2: steps sweep
steps = [10, 20, 30, 50]
ims = [generate(P, 1, 5.0, s, seed=42)[0] for s in steps]
grid(ims, [f"{s} steps" for s in steps]).save("fig_steps.png")
print("Saved fig_guidance.png and fig_steps.png")

# Table: CLIP score. CFG off (scale 1) vs CFG on (scale 5), plain vs best-of-N
rows = []
for name, sc in [("CFG off (scale 1)", 1.0), ("CFG on (scale 5)", 5.0)]:
    single, avg, best = [], [], []
    for i, p in enumerate(PROMPTS):
        ims = generate(p, a.n, sc, a.steps, seed=100 + i)
        s = clip_scores(p, ims)
        single.append(s[0]); avg.append(st.mean(s)); best.append(max(s))
        print(f"{name} | {p} | first={s[0]:.1f} best={max(s):.1f}")
    rows.append([name, round(st.mean(single), 2), round(st.mean(avg), 2), round(st.mean(best), 2)])

with open("results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["setting", "CLIP score (1 image)", f"CLIP score (mean of {a.n})", f"CLIP score (best of {a.n})"])
    w.writerows(rows)
print("\nsetting | 1 image | mean | best-of-N")
for r in rows:
    print(" | ".join(map(str, r)))
print("Saved results.csv")
