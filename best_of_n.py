"""Make N images, keep the best ones by CLIP score, save them bigger.
Run: python best_of_n.py "a brown dog sitting on the grass" --n 8 --keep 2"""
import argparse
from common import generate, clip_scores

ap = argparse.ArgumentParser()
ap.add_argument("prompt")
ap.add_argument("--n", type=int, default=8)
ap.add_argument("--keep", type=int, default=2)
ap.add_argument("--scale", type=float, default=5.0)
ap.add_argument("--steps", type=int, default=40)
a = ap.parse_args()

ims = generate(a.prompt, a.n, a.scale, a.steps)
sc = clip_scores(a.prompt, ims)
order = sorted(range(a.n), key=lambda i: -sc[i])[: a.keep]
for rank, i in enumerate(order, 1):
    from PIL import Image
    ims[i].resize((512, 512), Image.LANCZOS).save(f"best_{rank}.png")
    print(f"best_{rank}.png  CLIP score {sc[i]:.1f}")
