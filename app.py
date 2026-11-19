"""
FastAPI backend for the Text-to-Image Diffusion web app.
POST /api/generate  →  returns base64-encoded PNG(s).
"""

import os, io, base64
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import numpy as np
import tensorflow as tf

from architecture import TextToImageUNet
from diffusion import GaussianDiffusion
from text_encoder import TextEncoder

IMAGE_SIZE = 128
TEXT_DIM = 768
TOKEN_LEN = 24
TIMESTEPS = 1000
BASE_FILTERS = 128

# ── Load model once at startup ──────────────────────────────────────────
def _load():
    import glob
    from huggingface_hub import hf_hub_download
    weights = "t2i_weights_v2.h5"
    if not os.path.exists(weights):
        cached = glob.glob(os.path.expanduser(
            r"~\.cache\huggingface\hub\models--geeteshcodes--t2i-coco-128-clipL\snapshots\*\t2i_weights_v2.h5"))
        if cached:
            weights = cached[0]
        else:
            weights = hf_hub_download(repo_id="geeteshcodes/t2i-coco-128-clipL", filename=weights)
    model = TextToImageUNet(base_filters=BASE_FILTERS, text_dim=TEXT_DIM)
    dummy = [
        tf.zeros([1, IMAGE_SIZE, IMAGE_SIZE, 3], tf.float32),
        tf.zeros([1], tf.int32),
        tf.zeros([1, TOKEN_LEN, TEXT_DIM + 1], tf.float32),
    ]
    model(dummy, training=False)
    model.load_weights(weights)
    return model

print("[app] Loading diffusion model …")
_model = _load()
_diffusion = GaussianDiffusion(timesteps=TIMESTEPS)
print("[app] Loading text encoder …")
_encoder = TextEncoder()
print("[app] Ready.")

# ── FastAPI app ─────────────────────────────────────────────────────────
app = FastAPI(title="Stable Diffusion T2I")

class GenerateRequest(BaseModel):
    prompt: str
    n: int = Field(1, ge=1, le=4)
    scale: float = Field(5.0, ge=1.0, le=20.0)
    steps: int = Field(30, ge=5, le=100)
    seed: int = 42

class GenerateResponse(BaseModel):
    images: list[str]                  # list of base64 PNG strings
    image: str | None = None          # single base64 PNG string for convenience

@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    import random
    random.seed(req.seed)
    np.random.seed(req.seed)
    tf.random.set_seed(req.seed)
    prompts = [req.prompt] * req.n
    text_emb = tf.convert_to_tensor(_encoder.encode(prompts), tf.float32)
    shape = [req.n, IMAGE_SIZE, IMAGE_SIZE, 3]
    imgs = _diffusion.sample_text_to_image(
        _model, text_emb, shape,
        guidance_scale=req.scale,
        ddim_steps=req.steps,
    )
    # Convert [-1,1] → uint8 PNG → base64
    out = []
    for i in range(req.n):
        arr = ((imgs[i].numpy() + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, format="PNG")
        out.append(base64.b64encode(buf.getvalue()).decode())
    return GenerateResponse(images=out, image=out[0] if out else None)

# ── Serve static UI ─────────────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(static_dir, "index.html"))
