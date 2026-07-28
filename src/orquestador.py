"""
Etapa 4 — Orquestador.
Une identidad + voz + animación en un solo llamado.
Correr solo en Colab (necesita GPU para las etapas 1 y 3).
"""

from src.identidad import generate_avatar_image, resize_for_sadtalker
from src.voz import generate_voiceover
from src.animacion import create_ai_influencer
from src.config import LOLA_CHARACTERISTICS


def init_lola(script_text, characteristics=None, reusar_imagen=None, pose_style=0):
    """Genera un video completo de Lola: imagen + audio + animación.

    parameters:
    script_text (str): guion en español
    characteristics (str): rasgos físicos (None = usar default)
    reusar_imagen (str): ruta a imagen ancla ya generada — evita
                          regenerar la cara cada vez (recomendado)
    pose_style (int): intensidad de movimiento de cabeza (0-45)

    returns: lista de archivos de video generados
    """
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

    results = create_ai_influencer(image_path, audio_path, pose_style=pose_style)
    print("Video(s) generado(s):", results)
    return results
