"""
Model Loader for HoneyComb Text-to-Image Diffusion Model.
Handles Hugging Face Hub downloading, model caching, architecture instantiation,
singleton lifecycle management, and structured error handling.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np

# Ensure TensorFlow legacy Keras mode is active
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import tensorflow as tf
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import (
    GatedRepoError,
    RepositoryNotFoundError,
    EntryNotFoundError,
    HfHubHTTPError,
)

from architecture import TextToImageUNet
from diffusion import GaussianDiffusion
from text_encoder import TextEncoder

logger = logging.getLogger("honeycomb.model_loader")

# --- Configuration with Environment Variable Overrides ---
DEFAULT_REPO_ID = "MasterMAGE/t2i-coco-128-clipL"
DEFAULT_WEIGHTS_FILE = "t2i_weights_v2.h5"

IMAGE_SIZE = int(os.environ.get("MODEL_IMAGE_SIZE", "128"))
TEXT_DIM = int(os.environ.get("MODEL_TEXT_DIM", "768"))
TOKEN_LEN = int(os.environ.get("MODEL_TOKEN_LEN", "24"))
TIMESTEPS = int(os.environ.get("MODEL_TIMESTEPS", "1000"))
BASE_FILTERS = int(os.environ.get("MODEL_BASE_FILTERS", "128"))


# --- Custom Exception Hierarchy ---
class ModelLoaderError(Exception):
    """Base exception for model loading and inference failures."""
    pass


class ModelDownloadError(ModelLoaderError):
    """Raised when downloading model weights from Hugging Face Hub fails."""
    pass


class ModelAuthError(ModelLoaderError):
    """Raised when Hugging Face repository access requires authentication."""
    pass


class ModelWeightsError(ModelLoaderError):
    """Raised when loaded weights shape or layer count mismatches the architecture."""
    pass


class ModelOOMError(ModelLoaderError):
    """Raised when system or GPU runs out of memory during loading or inference."""
    pass


def get_hf_credentials() -> Tuple[str, str, Optional[str]]:
    """
    Extracts repo_id, filename, and optional token from environment variables.
    """
    repo_id = (
        os.environ.get("HF_MODEL_REPO")
        or os.environ.get("HF_REPO_ID")
        or os.environ.get("HF_REPO")
        or DEFAULT_REPO_ID
    ).strip()

    filename = (
        os.environ.get("HF_WEIGHTS_FILE")
        or os.environ.get("WEIGHTS_FILE")
        or DEFAULT_WEIGHTS_FILE
    ).strip()

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        token = token.strip()
        if not token:
            token = None

    return repo_id, filename, token


def download_weights(
    repo_id: Optional[str] = None,
    filename: Optional[str] = None,
    token: Optional[str] = None
) -> str:
    """
    Downloads model weights from Hugging Face Hub (or retrieves from local cache).
    """
    env_repo, env_file, env_token = get_hf_credentials()
    repo_id = repo_id or env_repo
    filename = filename or env_file
    token = token if token is not None else env_token

    # Check local file in workspace first if present
    if os.path.isfile(filename):
        logger.info(f"Using local weights file found at '{filename}'")
        return os.path.abspath(filename)

    # 1. Check local Hugging Face cache first (fast & offline safe)
    try:
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=token,
            local_files_only=True,
        )
        logger.info(f"Weights resolved from local HF cache at: {downloaded_path}")
        return downloaded_path
    except Exception:
        pass

    logger.info(f"Downloading/Resolving '{filename}' from Hugging Face repo '{repo_id}'...")
    try:
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=token,
        )
        logger.info(f"Weights successfully resolved at: {downloaded_path}")
        return downloaded_path
    except GatedRepoError as e:
        msg = (
            f"Repository '{repo_id}' is gated or private. "
            f"Please set a valid HF_TOKEN in your environment or .env file. Details: {e}"
        )
        logger.error(msg)
        raise ModelAuthError(msg) from e
    except RepositoryNotFoundError as e:
        # Check if missing token could be the cause for private repo
        if not token:
            msg = (
                f"Repository '{repo_id}' not found on Hugging Face Hub. "
                f"If the repository is private, please configure HF_TOKEN in .env. Details: {e}"
            )
            logger.error(msg)
            raise ModelAuthError(msg) from e
        else:
            msg = f"Repository '{repo_id}' does not exist on Hugging Face Hub: {e}"
            logger.error(msg)
            raise ModelDownloadError(msg) from e
    except EntryNotFoundError as e:
        msg = f"Weights file '{filename}' does not exist in repository '{repo_id}': {e}"
        logger.error(msg)
        raise ModelDownloadError(msg) from e
    except HfHubHTTPError as e:
        status_code = getattr(e.response, "status_code", None)
        if status_code in (401, 403):
            msg = f"Authentication failed (HTTP {status_code}) for '{repo_id}'. Please check HF_TOKEN in .env: {e}"
            logger.error(msg)
            raise ModelAuthError(msg) from e
        msg = f"HTTP error communicating with Hugging Face Hub ({e}): {e}"
        logger.error(msg)
        raise ModelDownloadError(msg) from e
    except Exception as e:
        msg = (
            f"Failed to download or load model weights '{filename}' from '{repo_id}': {e}. "
            f"Please verify your network connection or provide weights locally."
        )
        logger.error(msg)
        raise ModelDownloadError(msg) from e


def build_and_load_model(weights_path: str, base_filters: int = BASE_FILTERS) -> TextToImageUNet:
    """
    Instantiates the TextToImageUNet, runs dummy build pass, and loads trained weights.
    """
    logger.info(f"Instantiating TextToImageUNet (base_filters={base_filters}, text_dim={TEXT_DIM})...")
    try:
        model = TextToImageUNet(base_filters=base_filters, text_dim=TEXT_DIM)
        dummy_inputs = [
            tf.zeros([1, IMAGE_SIZE, IMAGE_SIZE, 3], dtype=tf.float32),
            tf.zeros([1], dtype=tf.int32),
            tf.zeros([1, TOKEN_LEN, TEXT_DIM + 1], dtype=tf.float32),
        ]
        # Build model graph with dummy input
        model(dummy_inputs, training=False)
    except (tf.errors.ResourceExhaustedError, MemoryError) as e:
        msg = f"Out of memory allocating U-Net model graph: {e}"
        logger.error(msg)
        raise ModelOOMError(msg) from e
    except Exception as e:
        msg = f"Failed to build TextToImageUNet architecture: {e}"
        logger.error(msg)
        raise ModelWeightsError(msg) from e

    logger.info(f"Loading weights into model from '{weights_path}'...")
    try:
        model.load_weights(weights_path)
        logger.info(f"Successfully loaded model weights ({model.count_params():,} parameters).")
        return model
    except (ValueError, KeyError) as e:
        msg = (
            f"Weights shape or layer count mismatch loading '{weights_path}' into TextToImageUNet: {e}. "
            f"Verify that base_filters={base_filters} and text_dim={TEXT_DIM} match the checkpoint configuration."
        )
        logger.error(msg)
        raise ModelWeightsError(msg) from e
    except (tf.errors.ResourceExhaustedError, MemoryError) as e:
        msg = f"Out of memory loading weights from '{weights_path}': {e}"
        logger.error(msg)
        raise ModelOOMError(msg) from e
    except Exception as e:
        msg = f"Unexpected failure loading weights from '{weights_path}': {e}"
        logger.error(msg)
        raise ModelWeightsError(msg) from e


class ModelPipeline:
    """
    Thread-safe Singleton wrapper managing model, diffusion sampler, and text encoder.
    Loaded once at application startup.
    """
    _instance: Optional["ModelPipeline"] = None

    def __init__(self):
        logger.info("Initializing ModelPipeline singleton...")
        repo_id, filename, _ = get_hf_credentials()
        self.weights_path = download_weights()
        self.model = build_and_load_model(self.weights_path)
        self.diffusion = GaussianDiffusion(timesteps=TIMESTEPS)
        logger.info("Initializing TextEncoder...")
        try:
            self.encoder = TextEncoder()
        except (tf.errors.ResourceExhaustedError, MemoryError) as e:
            msg = f"Out of memory initializing TextEncoder: {e}"
            logger.error(msg)
            raise ModelOOMError(msg) from e
        logger.info("ModelPipeline initialization complete.")

    @classmethod
    def get_instance(cls) -> "ModelPipeline":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate(
        self,
        prompt: str,
        n: int = 1,
        scale: float = 5.0,
        steps: int = 30,
        seed: Optional[int] = 42
    ) -> List[np.ndarray]:
        """
        Samples n synthetic images (128x128x3 uint8) from the prompt.
        """
        if seed is not None:
            import random
            random.seed(seed)
            np.random.seed(seed)
            tf.random.set_seed(seed)

        prompts = [prompt] * n
        try:
            text_emb = tf.convert_to_tensor(self.encoder.encode(prompts), tf.float32)
        except (tf.errors.ResourceExhaustedError, MemoryError) as e:
            raise ModelOOMError(f"Out of memory encoding prompt tokens: {e}") from e

        shape = [n, IMAGE_SIZE, IMAGE_SIZE, 3]
        try:
            raw_imgs = self.diffusion.sample_text_to_image(
                self.model,
                text_emb,
                shape,
                guidance_scale=scale,
                ddim_steps=steps,
            )
        except (tf.errors.ResourceExhaustedError, MemoryError) as e:
            raise ModelOOMError(f"Out of memory during diffusion reverse sampling: {e}") from e

        # Convert from [-1, 1] float tensor to uint8 numpy array [0, 255]
        images_uint8 = []
        for i in range(n):
            arr = ((raw_imgs[i].numpy() + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
            images_uint8.append(arr)

        return images_uint8


# Module-level convenience functions
def get_pipeline() -> ModelPipeline:
    return ModelPipeline.get_instance()


def get_model() -> TextToImageUNet:
    return get_pipeline().model


def get_diffusion() -> GaussianDiffusion:
    return get_pipeline().diffusion


def get_text_encoder() -> TextEncoder:
    return get_pipeline().encoder
