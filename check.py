import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import h5py, tensorflow as tf
from architecture import TextToImageUNet
from model_loader import download_weights

p = download_weights()
with h5py.File(p, "r") as f:
    saved = [n.decode() if isinstance(n, bytes) else n for n in f.attrs["layer_names"]]

model = TextToImageUNet(base_filters=128, text_dim=768)
model([tf.zeros([1,128,128,3]), tf.zeros([1], tf.int32), tf.zeros([1,24,769])], training=False)
mine = [l.name for l in model.layers]

print("FILE :", len(saved), saved)
print("CODE :", len(mine), mine)
print("ONLY IN FILE:", [n for n in saved if n not in mine])
print("ONLY IN CODE:", [n for n in mine if n not in saved])