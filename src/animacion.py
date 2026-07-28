"""
Etapa 3 — Animación (lip-sync) con SadTalker.
Requiere GPU y el repo de SadTalker clonado en el mismo entorno
(ver colab_bootstrap.ipynb). Correr solo en Colab.
"""

import os


def liberar_gpu():
    """Libera memoria de GPU antes de correr SadTalker (evita
    CUDNN_STATUS_NOT_INITIALIZED si SDXL/XTTS quedaron cargados)."""
    import torch
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()


def create_ai_influencer(image_path, audio_path, pose_style=0, still=False):
    """Genera el video final de Lola hablando.

    parameters:
    image_path (str): imagen de Lola, idealmente 512x512
    audio_path (str): audio del guion
    pose_style (int): 0-45, intensidad de movimiento de cabeza
    still (bool): True = solo mueve la boca, False = movimiento
                  natural de cabeza (recomendado)

    returns: lista de archivos generados en ./results/
    """
    liberar_gpu()

    still_flag = "--still" if still else ""

    os.system(
        f"python3.8 inference.py "
        f"--driven_audio {audio_path} "
        f"--source_image {image_path} "
        f"--result_dir ./results "
        f"--preprocess full --enhancer gfpgan "
        f"--pose_style {pose_style} {still_flag}"
    )
    return sorted(os.listdir("./results/"))


def diagnosticar_error(image_path, audio_path, pose_style=0, still=False):
    """Corre lo mismo que create_ai_influencer pero capturando
    STDOUT/STDERR completos — usar si el video no se genera y
    no queda claro por qué.
    """
    import subprocess
    liberar_gpu()

    cmd = [
        "python3.8", "inference.py",
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", "./results",
        "--preprocess", "full", "--enhancer", "gfpgan",
        "--pose_style", str(pose_style),
    ]
    if still:
        cmd.append("--still")

    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:\n", result.stdout[-3000:])
    print("=" * 50)
    print("STDERR:\n", result.stderr[-3000:])
    print("Return code:", result.returncode)
    return result
