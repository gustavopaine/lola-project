"""
Etapa 4 — Orquestador.
Une identidad + voz + animación en un solo llamado.
Correr solo en Colab (necesita GPU para las etapas 1 y 3).
"""

import os
import shutil

from src.identidad import generate_avatar_image, resize_for_sadtalker
from src.voz import generate_voiceover
from src.animacion import create_ai_influencer
from src.config import LOLA_CHARACTERISTICS


def init_lola(script_text, characteristics=None, reusar_imagen=None, pose_style=0,
              guion_id=None, max_retries=1, result_dir="./results"):
    """Genera un video completo de Lola: imagen + audio + animación.

    parameters:
    script_text (str): guion en español
    characteristics (str): rasgos físicos (None = usar default)
    reusar_imagen (str): ruta a imagen ancla ya generada — evita
                          regenerar la cara cada vez (recomendado)
    pose_style (int): intensidad de movimiento de cabeza (0-45)
    guion_id (str): id del guion (ej. "dia_1"). Si se pasa, el video
                     final queda en {result_dir}/{guion_id}.mp4 y, si
                     ese archivo ya existe, se saltea toda la
                     generación (idempotencia — protege de volver a
                     correr la misma celda por error).
    max_retries (int): reintentos de la etapa de SadTalker si falla
                        silenciosamente (ver src/animacion.py)
    result_dir (str): carpeta donde SadTalker escribe sus resultados

    returns: ruta al video final (str)
    """
    if guion_id:
        video_final_path = os.path.join(result_dir, f"{guion_id}.mp4")
        if os.path.exists(video_final_path):
            print("Video ya existe, se saltea la generación:", video_final_path)
            return video_final_path

    if reusar_imagen:
        image_path = reusar_imagen
        print("Reusando imagen existente:", image_path)
    else:
        prompt = characteristics or LOLA_CHARACTERISTICS
        image_path_raw = generate_avatar_image(prompt)
        print("Imagen generada:", image_path_raw)
        image_path = resize_for_sadtalker(image_path_raw)
        print("Imagen redimensionada:", image_path)

    audio_path = generate_voiceover(script_text)
    print("Audio generado:", audio_path)

    video_path = create_ai_influencer(
        image_path, audio_path, pose_style=pose_style,
        result_dir=result_dir, max_retries=max_retries,
    )
    print("Video generado:", video_path)

    if guion_id:
        os.makedirs(result_dir, exist_ok=True)
        shutil.copy2(video_path, video_final_path)
        print("Copiado a:", video_final_path)
        return video_final_path

    return video_path
