import os
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
import numpy as np, tensorflow as tf, torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
from model_loader import get_pipeline

print("Loading model via model_loader...")
pipeline = get_pipeline()
model = pipeline.model
diffusion = pipeline.diffusion
encoder = pipeline.encoder

print("Loading CLIP scorer...")
clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
clip_proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def generate(prompt, n=1, scale=5.0, steps=30, seed=None):
    """Returns a list of PIL images (128x128)."""
    imgs = pipeline.generate(prompt=prompt, n=n, scale=scale, steps=steps, seed=seed)
    return [Image.fromarray(a) for a in imgs]


def clip_scores(prompt, images):
    """CLIP score (0-100, higher = image matches the prompt better)."""
    inp = clip_proc(text=[prompt], images=images, return_tensors="pt", padding=True)
    with torch.no_grad():
        out = clip(**inp)
    return (100 * out.logits_per_image[:, 0] / clip.logit_scale.exp()).clamp(min=0).tolist()


def grid(images, labels=None, size=256):
    from PIL import ImageDraw
    pad = 22 if labels else 0
    g = Image.new("RGB", (size * len(images), size + pad), "white")
    d = ImageDraw.Draw(g)
    for i, im in enumerate(images):
        g.paste(im.resize((size, size), Image.LANCZOS), (i * size, pad))
        if labels:
            d.text((i * size + 6, 5), labels[i], fill="black")
    return g
