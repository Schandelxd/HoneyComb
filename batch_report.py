"""
batch_report.py - run the whole test suite for the report in one go.

WHAT HAPPENS, STEP BY STEP
  1. For every test prompt (29 prompts in 5 groups) the model makes N images.
     - The prompt is turned into token embeddings by the text encoder.
     - Each image starts as pure random noise (a fixed seed per prompt, so results can be repeated).
     - The U-Net removes noise over S DDIM steps. At every step it runs twice (with and without
       the text) and mixes the two (classifier-free guidance, strength = --scale).
  2. CLIP scores every image against its prompt (CLIP score 0-100, higher = better match).
  3. The N images are ranked. The Best, a Typical (median) and the Worst are saved.
  4. All prompts are ranked against each other by their best score, and groups are averaged.
  5. Figures, CSV tables and a report.md with plain-English notes are written to report_out/.
It saves progress after every prompt, so if you stop it (Ctrl+C) just run it again and it continues.

RUN:   python batch_report.py                 (full: 8 images per prompt, 40 steps)
       python batch_report.py --quick         (fast test: 4 images, 20 steps, 2 prompts per group)
"""
import os, re, json, time, csv, argparse, statistics as st
from PIL import Image, ImageDraw
from common import generate, clip_scores, grid

GROUPS = {
 "1_rigid_scenes": ["a red bus driving down a city street", "a train traveling down the tracks",
   "a plane flying in a blue sky", "a pizza sitting on top of a table", "a plate of food on a wooden table",
   "a kitchen with white cabinets and a stove", "a living room with a couch and a table",
   "a bathroom with a sink and a mirror"],
 "2_animals": ["a giraffe standing in a grassy field", "a herd of sheep grazing on a hill",
   "an elephant walking near a river", "a horse standing in a field", "a bird sitting on a tree branch",
   "a brown dog sitting on the grass", "a gray cat sitting on a couch in a living room"],
 "3_people_sports": ["a man riding a skateboard down a street", "a man riding a wave on a surfboard",
   "a person skiing down a snowy hill", "a baseball player swinging a bat", "a girl holding an umbrella in the rain"],
 "4_outdoor_scenes": ["a boat floating on a calm lake", "a snowy mountain with trees",
   "a city street at night with cars", "a beach with people and umbrellas"],
 "5_out_of_domain": ["a dragon flying over a castle", "a futuristic city with flying cars",
   "a cat wearing a spacesuit", "a stop sign that says hello", "three red apples and two blue cups"],
}
NOTES = {
 "1_rigid_scenes": "Common objects with fairly fixed shapes. Expected to be the model's strongest group.",
 "2_animals": "Animals change pose a lot. Expect correct colour, texture and setting but weak body structure.",
 "3_people_sports": "People are the hardest subject for a small model. Expect distorted anatomy.",
 "4_outdoor_scenes": "Landscapes have little fine structure, so they are usually forgiving.",
 "5_out_of_domain": "Things COCO never contained (fantasy, text, exact counts). These are deliberate failure cases.",
}

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=8, help="images per prompt")
ap.add_argument("--steps", type=int, default=40)
ap.add_argument("--scale", type=float, default=5.0)
ap.add_argument("--per-group", type=int, default=0, help="limit prompts per group (0 = all)")
ap.add_argument("--quick", action="store_true")
ap.add_argument("--out", default="report_out")
a = ap.parse_args()
if a.quick:
    a.n, a.steps, a.per_group = 4, 20, 2

def say(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
slug = lambda p: re.sub(r"[^a-z0-9]+", "_", p.lower()).strip("_")[:50]

os.makedirs(a.out, exist_ok=True)
DATA = os.path.join(a.out, "data.json")
data = json.load(open(DATA)) if os.path.exists(DATA) else {}
groups = {g: (ps[:a.per_group] if a.per_group else ps) for g, ps in GROUPS.items()}
total = sum(len(v) for v in groups.values())
say(f"Plan: {total} prompts x {a.n} images, {a.steps} DDIM steps, guidance {a.scale}. Output folder: {a.out}/")

# ---- 1-3: generate, score, rank within each prompt ----
done_times, k = [], 0
for g, prompts in groups.items():
    os.makedirs(os.path.join(a.out, "images", g), exist_ok=True)
    for p in prompts:
        k += 1
        s = slug(p); base = os.path.join(a.out, "images", g, s)
        if p in data and os.path.exists(base + "_best.png"):
            say(f"({k}/{total}) skip, already done: {p}"); continue
        t0 = time.time()
        say(f"({k}/{total}) [{g}] making {a.n} images for: \"{p}\"")
        ims = generate(p, a.n, a.scale, a.steps, seed=1000 + k)
        say("   scoring every image with CLIP (how well does it match the prompt?)")
        sc = clip_scores(p, ims)
        order = sorted(range(a.n), key=lambda i: -sc[i])
        picks = {"best": order[0], "typical": order[a.n // 2], "worst": order[-1]}
        for name, i in picks.items():
            ims[i].save(f"{base}_{name}.png")
        ims[order[0]].resize((512, 512), Image.LANCZOS).save(f"{base}_best512.png")
        data[p] = dict(group=g, slug=s, scores=[round(x, 2) for x in sc], best=round(sc[order[0]], 2),
                       typical=round(sc[order[a.n // 2]], 2), worst=round(sc[order[-1]], 2),
                       mean=round(st.mean(sc), 2), seed=1000 + k, seconds=round(time.time() - t0, 1))
        json.dump(data, open(DATA, "w"), indent=1)
        done_times.append(time.time() - t0)
        left = (total - k) * st.mean(done_times)
        say(f"   best {sc[order[0]]:.1f} | typical {sc[order[a.n//2]]:.1f} | worst {sc[order[-1]]:.1f}"
            f"   (about {left/60:.0f} min left)")

rows = [dict(prompt=p, **v) for p, v in data.items() if any(p in ps for ps in groups.values())]

# ---- 4: rank all prompts, summarise groups ----
say("Ranking all prompts by their best CLIP score and averaging each group")
rows.sort(key=lambda r: -r["best"])
with open(os.path.join(a.out, "results_ranked.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["rank", "group", "prompt", "best", "typical", "worst", "mean_of_all"])
    for i, r in enumerate(rows, 1):
        w.writerow([i, r["group"], r["prompt"], r["best"], r["typical"], r["worst"], r["mean"]])
gsum = {}
for g in groups:
    rs = [r for r in rows if r["group"] == g]
    if rs:
        gsum[g] = dict(n=len(rs), best=st.mean(r["best"] for r in rs), mean=st.mean(r["mean"] for r in rs),
                       worst=st.mean(r["worst"] for r in rs))
with open(os.path.join(a.out, "group_summary.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "prompts", "avg_best", "avg_mean", "avg_worst"])
    for g, v in gsum.items():
        w.writerow([g, v["n"], round(v["best"], 2), round(v["mean"], 2), round(v["worst"], 2)])

# ---- 5: figures ----
say("Drawing figures")
def load(r, name): return Image.open(os.path.join(a.out, "images", r["group"], f"{r['slug']}_{name}.png")).convert("RGB")
for g in gsum:
    rs = [r for r in rows if r["group"] == g]; rs.sort(key=lambda r: -r["best"])
    for c in range(0, len(rs), 4):
        chunk, strips = rs[c:c+4], []
        for r in chunk:
            gr = grid([load(r, n) for n in ("best", "typical", "worst")],
                      [f"Best (CLIP {r['best']:.1f})", f"Typical ({r['typical']:.1f})", f"Worst ({r['worst']:.1f})"])
            row = Image.new("RGB", (gr.width, gr.height + 26), "white")
            ImageDraw.Draw(row).text((6, 6), f'Prompt: "{r["prompt"]}"', fill="black"); row.paste(gr, (0, 26))
            strips.append(row)
        fig = Image.new("RGB", (strips[0].width, sum(s.height for s in strips)), "white"); y = 0
        for s_ in strips: fig.paste(s_, (0, y)); y += s_.height
        fig.save(os.path.join(a.out, f"fig_{g}_{c//4+1}.png"))

cols, cell, lab = 6, 200, 34
rws = (len(rows) + cols - 1) // cols
rk = Image.new("RGB", (cols * cell, rws * (cell + lab)), "white"); d = ImageDraw.Draw(rk)
for i, r in enumerate(rows):
    x, y = (i % cols) * cell, (i // cols) * (cell + lab)
    rk.paste(load(r, "best").resize((cell, cell), Image.LANCZOS), (x, y + lab))
    d.text((x + 4, y + 3), f"#{i+1}  CLIP {r['best']:.1f}", fill="black")
    d.text((x + 4, y + 17), r["prompt"][:32], fill="gray")
rk.save(os.path.join(a.out, "fig_ranking_all.png"))

# ---- report.md ----
say("Writing report.md")
L = ["# Test results (auto-generated)", "",
 "## How these numbers were made",
 f"- {len(rows)} test prompts in {len(gsum)} groups, written in MS-COCO caption style.",
 f"- For each prompt the model generated **{a.n} images** (DDIM, **{a.steps} steps**, guidance scale **{a.scale}**, fixed seed per prompt).",
 "- Every image was scored by CLIP (ViT-B/32): a 0-100 similarity between the image and its prompt. Higher means a closer match.",
 "- Per prompt, the images were ranked; the **best**, a **typical** (median) and the **worst** were kept.",
 "- Prompts were then ranked against each other by their best score, and each group was averaged.",
 "- **Caveat:** CLIP is an automatic, imperfect judge and these are small samples. Check the figures by eye; scores alone prove little.", "",
 "## Group summary", "", "| Group | Prompts | Avg best | Avg mean | Avg worst |", "|---|---|---|---|---|"]
for g, v in gsum.items():
    L.append(f"| {g} | {v['n']} | {v['best']:.1f} | {v['mean']:.1f} | {v['worst']:.1f} |")
L += ["", "## What each group is meant to show", ""]
for g in gsum: L.append(f"- **{g}**: {NOTES[g]}")
if gsum:
    hi = max(gsum, key=lambda g: gsum[g]["mean"]); lo = min(gsum, key=lambda g: gsum[g]["mean"])
    L += ["", "## Plain observations from the numbers", "",
          f"- Highest average CLIP score: **{hi}** ({gsum[hi]['mean']:.1f}). Lowest: **{lo}** ({gsum[lo]['mean']:.1f}).",
          f"- Best single result: \"{rows[0]['prompt']}\" ({rows[0]['best']:.1f}). Lowest-ranked prompt: \"{rows[-1]['prompt']}\" ({rows[-1]['best']:.1f}).",
          f"- Average gap between the best and worst image of the same prompt: {st.mean(r['best']-r['worst'] for r in rows):.1f} CLIP points, which is why best-of-{a.n} selection helps.",
          "- Confirm these against the figures before writing them in the report."]
L += ["", "## Ranked prompts", "", "| # | Group | Prompt | Best | Typical | Worst |", "|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    L.append(f"| {i} | {r['group']} | {r['prompt']} | {r['best']:.1f} | {r['typical']:.1f} | {r['worst']:.1f} |")
L += ["", "## Files", "- `fig_<group>_N.png`: best / typical / worst per prompt", "- `fig_ranking_all.png`: every prompt's best image, ranked",
      "- `results_ranked.csv`, `group_summary.csv`: tables", "- `images/`: every saved image (`*_best512.png` is the best, enlarged to 512 px)"]
open(os.path.join(a.out, "report.md"), "w", encoding="utf-8").write("\n".join(L))
say(f"DONE. Open the folder '{a.out}' - start with report.md and fig_ranking_all.png")
