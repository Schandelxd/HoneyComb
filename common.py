import os
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
import numpy as np, tensorflow as tf, torch
from PIL import Image
from huggingface_hub import hf_hub_download
from transformers import CLIPModel, CLIPProcessor
from architecture import TextToImageUNet
from diffusion import GaussianDiffusion
from text_encoder import TextEncoder

REPO = "geeteshcodes/t2i-coco-128-clipL"
print("Loading model...")
model = TextToImageUNet(base_filters=128, text_dim=768)
model([tf.zeros([1, 128, 128, 3]), tf.zeros([1], tf.int32), tf.zeros([1, 24, 769])], training=False)

weights = "t2i_weights_v2.h5"
if not os.path.exists(weights):
    import glob
    cached = glob.glob(os.path.expanduser(
        r"~\.cache\huggingface\hub\models--geeteshcodes--t2i-coco-128-clipL\snapshots\*\t2i_weights_v2.h5"))
    if cached:
        weights = cached[0]
    else:
        weights = hf_hub_download(REPO, "t2i_weights_v2.h5")
model.load_weights(weights)
encoder = TextEncoder()
diffusion = GaussianDiffusion(timesteps=1000)

print("Loading CLIP scorer...")
clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
clip_proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def generate(prompt, n=1, scale=5.0, steps=30, seed=None):
    """Returns a list of PIL images (128x128)."""
    if seed is not None:
        tf.random.set_seed(seed)
    emb = tf.convert_to_tensor(encoder.encode([prompt] * n), tf.float32)
    imgs = diffusion.sample_text_to_image(model=model, text_emb=emb, shape=[n, 128, 128, 3],
                                          guidance_scale=scale, ddim_steps=steps)
    arr = ((imgs.numpy() + 1.0) * 127.5).clip(0, 255).astype("uint8")
    return [Image.fromarray(a) for a in arr]


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
