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


def _snapshot_results_entries(result_dir="./results"):
    """Nombres de archivos y carpetas existentes en result_dir en este
    momento. Se usa para detectar, por diferencia, qué generó una corrida
    de inference.py."""
    if not os.path.isdir(result_dir):
        return set()
    return set(os.listdir(result_dir))


def _find_output_video(before, result_dir="./results"):
    """Ubica el .mp4 que produjo la corrida más reciente de inference.py,
    comparando el listado actual de result_dir contra el snapshot 'before'
    tomado antes de correrla.

    inference.py, cuando termina bien, mueve el video final a un .mp4
    suelto directamente en result_dir (ej. results/2026_08_10_14.30.45.mp4)
    y borra la carpeta de trabajo temporal que usó — salvo que se pase
    --verbose, cosa que no hacemos. Si el proceso se corta a mitad de
    camino, esa carpeta temporal queda huérfana en vez de reemplazada por
    el .mp4. Por eso hay que mirar tanto archivos nuevos como carpetas
    nuevas.

    Lanza SadTalkerGenerationError si la corrida no generó nada nuevo, si
    lo nuevo no incluye ningún .mp4 (por ejemplo, si solo quedó la carpeta
    temporal con first_frame_dir/ porque el proceso se cortó a mitad de
    camino), o si el .mp4 encontrado pesa 0 bytes.
    """
    after = _snapshot_results_entries(result_dir)
    new_entries = after - before

    if not new_entries:
        raise SadTalkerGenerationError(
            f"SadTalker no generó ninguna salida nueva en {result_dir}"
        )

    candidates = []
    for name in new_entries:
        path = os.path.join(result_dir, name)
        if os.path.isfile(path) and path.endswith(".mp4"):
            candidates.append(path)
        elif os.path.isdir(path):
            candidates.extend(glob.glob(os.path.join(path, "*.mp4")))

    if not candidates:
        raise SadTalkerGenerationError(
            f"SadTalker generó algo nuevo en {result_dir} pero sin ningún .mp4 "
            f"(probablemente el proceso se cortó a mitad de camino): {sorted(new_entries)}"
        )

    video_path = max(candidates, key=os.path.getmtime)
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
        before = _snapshot_results_entries(result_dir)
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
