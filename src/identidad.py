"""
Etapa 1 — Identidad visual de Lola.
Genera la imagen base con SDXL. Requiere GPU (correr en Colab).
"""

import os
import gc
from src.config import LOLA_CHARACTERISTICS


def generate_avatar_image(image_prompt=None, out_path="examples/source_image/lola.png", steps=40):
    """Genera la imagen base de Lola con SDXL.

    Import de torch/diffusers hecho DENTRO de la función a
    propósito: así este archivo se puede importar en local
    (VS Code) sin GPU sin que falle, para autocompletado/lint.
    Solo falla si de verdad llamás a esta función sin GPU.
    """
    import torch
    from diffusers import DiffusionPipeline

    prompt = image_prompt or LOLA_CHARACTERISTICS

    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        variant="fp16",
    ).to("cuda")

    image = pipe(prompt, num_inference_steps=steps).images[0]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    image.save(out_path)

    del pipe
    gc.collect()
    torch.cuda.empty_cache()

    return out_path


def resize_for_sadtalker(image_path, size=512):
    """Redimensiona la imagen a 512x512 (SDXL genera en 1024x1024,
    y SadTalker rinde mejor/más estable con imágenes más chicas).
    """
    from PIL import Image

    out_path = image_path.replace(".png", f"_{size}.png")
    img = Image.open(image_path)
    img.resize((size, size)).save(out_path)
    return out_path
