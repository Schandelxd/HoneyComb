"""
FastAPI backend for HoneyComb Text-to-Image Diffusion Studio.
POST /api/generate  →  returns base64-encoded PNG(s).
Loads model weights from Hugging Face Hub (MasterMAGE/t2i-coco-128-clipL) via model_loader.
"""

import os
import io
import base64
from typing import Optional, List

os.environ["TF_USE_LEGACY_KERAS"] = "1"

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import numpy as np
import tensorflow as tf

from model_loader import (
    get_pipeline,
    ModelPipeline,
    ModelLoaderError,
    ModelDownloadError,
    ModelAuthError,
    ModelWeightsError,
    ModelOOMError,
    IMAGE_SIZE,
    get_hf_credentials,
)

# ── Singleton Model Initialization at Startup ─────────────────────────────
_pipeline: Optional[ModelPipeline] = None
_init_error: Optional[str] = None


def initialize_model():
    """Initializes the model pipeline once at application startup."""
    global _pipeline, _init_error
    try:
        print("[app] Initializing HoneyComb model pipeline once at startup...")
        _pipeline = get_pipeline()
        _init_error = None
        print(f"[app] Model ready ({_pipeline.model.count_params():,} parameters).")
    except ModelAuthError as e:
        _init_error = f"Authentication Error: {e}"
        print(f"[app] { _init_error}")
    except ModelDownloadError as e:
        _init_error = f"Download Error: {e}"
        print(f"[app] {_init_error}")
    except ModelWeightsError as e:
        _init_error = f"Weights Architecture Error: {e}"
        print(f"[app] {_init_error}")
    except ModelOOMError as e:
        _init_error = f"Out of Memory Error: {e}"
        print(f"[app] {_init_error}")
    except Exception as e:
        _init_error = f"Unexpected model initialization failure: {e}"
        print(f"[app] {_init_error}")


# Run singleton initialization
initialize_model()

# ── FastAPI Application ──────────────────────────────────────────────────
app = FastAPI(
    title="HoneyComb Text-to-Image Diffusion Studio",
    description="Text-to-Image diffusion model trained from scratch with real-time web studio.",
    version="2.0.0"
)


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt describing the image to generate")
    n: int = Field(1, ge=1, le=4, description="Number of images to generate (batch size)")
    scale: float = Field(5.0, ge=1.0, le=20.0, description="Classifier-Free Guidance (CFG) scale")
    steps: int = Field(30, ge=5, le=100, description="Number of DDIM sampling steps (default: 30)")
    seed: Optional[int] = Field(42, description="Random seed for deterministic generation (None for random)")


class GenerateResponse(BaseModel):
    images: List[str]                  # list of base64 PNG strings
    image: Optional[str] = None        # single base64 PNG string for convenience
    repo_id: Optional[str] = None      # source repository
    error: Optional[str] = None


@app.get("/api/model_info")
def model_info():
    """Returns status and configuration of the loaded diffusion model."""
    repo_id, weights_file, has_token = get_hf_credentials()
    return {
        "status": "ready" if _pipeline is not None else "error",
        "error": _init_error,
        "repo_id": repo_id,
        "weights_file": weights_file,
        "has_token": bool(has_token),
        "image_size": f"{IMAGE_SIZE}x{IMAGE_SIZE}",
        "parameters": _pipeline.model.count_params() if _pipeline else 0,
    }


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """
    Generates synthetic 128x128 images from a textual prompt using DDIM sampling.
    """
    global _pipeline, _init_error

    # Check if startup model loading encountered an error
    if _init_error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model unavailable. {_init_error}"
        )

    # Ensure pipeline is loaded
    if _pipeline is None:
        try:
            _pipeline = get_pipeline()
        except ModelAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Hugging Face Authentication Error: {e}. Please check HF_TOKEN in your .env file."
            )
        except ModelDownloadError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Weights Download Failure: {e}."
            )
        except ModelWeightsError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model Weights Architecture Mismatch: {e}."
            )
        except ModelOOMError as e:
            raise HTTPException(
                status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                detail=f"System Out of Memory during model loading: {e}."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model loading failure: {e}"
            )

    # Execute generation with targeted error handling
    try:
        images_uint8 = _pipeline.generate(
            prompt=req.prompt,
            n=req.n,
            scale=req.scale,
            steps=req.steps,
            seed=req.seed
        )
    except ModelOOMError as e:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail=f"Out of Memory (OOM) during sampling: {e}. Try generating fewer images (n=1) or reducing steps."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {e}"
        )

    # Convert uint8 numpy arrays [128, 128, 3] to base64 PNGs
    out_b64 = []
    from PIL import Image
    for arr in images_uint8:
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, format="PNG")
        out_b64.append(base64.b64encode(buf.getvalue()).decode("utf-8"))

    repo_id, _, _ = get_hf_credentials()
    return GenerateResponse(
        images=out_b64,
        image=out_b64[0] if out_b64 else None,
        repo_id=repo_id
    )


# ── Static UI Mounting ───────────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(static_dir, "index.html"))
