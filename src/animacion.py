"""
Etapa 3 — Animación (lip-sync) con SadTalker.
Requiere GPU y el repo de SadTalker clonado en el mismo entorno
(ver colab_bootstrap.ipynb). Correr solo en Colab.
"""

import glob
import os
import subprocess


class SadTalkerGenerationError(Exception):
    """SadTalker terminó sin producir un video válido, incluso tras
    los reintentos configurados."""


def _snapshot_results_dirs(result_dir="./results"):
    """Nombres de subcarpetas existentes en result_dir en este momento.
    Se usa para detectar, por diferencia, qué carpeta creó una corrida
    de inference.py."""
    if not os.path.isdir(result_dir):
        return set()
    return {
        name
        for name in os.listdir(result_dir)
        if os.path.isdir(os.path.join(result_dir, name))
    }


def _find_output_video(before, result_dir="./results"):
    """Ubica el .mp4 que produjo la corrida más reciente de inference.py,
    comparando el listado actual de result_dir contra el snapshot 'before'
    tomado antes de correrla.

    Lanza SadTalkerGenerationError si la corrida no creó ninguna carpeta
    nueva, si la carpeta nueva no contiene ningún .mp4 directamente adentro
    (por ejemplo, si solo tiene first_frame_dir/ porque el proceso se cortó
    a mitad de camino), o si el .mp4 encontrado pesa 0 bytes.
    """
    after = _snapshot_results_dirs(result_dir)
    new_dirs = after - before

    if not new_dirs:
        raise SadTalkerGenerationError(
            f"SadTalker no se creó ninguna carpeta nueva en {result_dir}"
        )

    newest_dir = max(
        new_dirs, key=lambda name: os.path.getmtime(os.path.join(result_dir, name))
    )
    run_dir = os.path.join(result_dir, newest_dir)

    videos = sorted(glob.glob(os.path.join(run_dir, "*.mp4")))
    if not videos:
        raise SadTalkerGenerationError(
            f"La carpeta de resultado {run_dir} no contiene ningún .mp4 "
            "(probablemente el proceso se cortó a mitad de camino)"
        )

    video_path = videos[0]
    if os.path.getsize(video_path) == 0:
        raise SadTalkerGenerationError(f"El video generado {video_path} pesa 0 bytes")

    return video_path


def liberar_gpu():
    """Libera memoria de GPU antes de correr SadTalker (evita
    CUDNN_STATUS_NOT_INITIALIZED si SDXL/XTTS quedaron cargados)."""
    import torch
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()


def create_ai_influencer(image_path, audio_path, pose_style=0, still=False,
                          result_dir="./results", max_retries=1):
    """Genera el video final de Lola hablando.

    parameters:
    image_path (str): imagen de Lola, idealmente 512x512
    audio_path (str): audio del guion
    pose_style (int): 0-45, intensidad de movimiento de cabeza
    still (bool): True = solo mueve la boca, False = movimiento
                  natural de cabeza (recomendado)
    result_dir (str): carpeta donde SadTalker escribe sus resultados
    max_retries (int): reintentos adicionales si la corrida no produce
                        un .mp4 válido (el fallo silencioso ya conocido
                        de SadTalker — ver README)

    returns: ruta al .mp4 generado

    raises: SadTalkerGenerationError si se agotan los reintentos sin
            obtener un video válido
    """
    cmd = [
        "python3.8", "inference.py",
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", result_dir,
        "--preprocess", "full", "--enhancer", "gfpgan",
        "--pose_style", str(pose_style),
    ]
    if still:
        cmd.append("--still")

    total_attempts = max_retries + 1
    last_error = None

    for attempt in range(1, total_attempts + 1):
        liberar_gpu()
        before = _snapshot_results_dirs(result_dir)
        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            return _find_output_video(before, result_dir)
        except SadTalkerGenerationError as error:
            last_error = error
            print(f"[create_ai_influencer] intento {attempt}/{total_attempts} falló: {error}")
            stderr_tail = (result.stderr or "")[-1000:]
            if stderr_tail:
                print(f"STDERR (últimas líneas):\n{stderr_tail}")
            if attempt < total_attempts:
                print("Reintentando...")

    raise SadTalkerGenerationError(
        f"SadTalker falló tras {total_attempts} intento(s). Último error: {last_error}"
    ) from last_error


def diagnosticar_error(image_path, audio_path, pose_style=0, still=False):
    """Corre lo mismo que create_ai_influencer pero capturando
    STDOUT/STDERR completos — usar si el video no se genera y
    no queda claro por qué.
    """
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
