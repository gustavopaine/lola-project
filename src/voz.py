"""
Etapa 2 — Voz de Lola.
Versión simple con gTTS (funciona en CPU, no necesita GPU) y
versión de voz clonada con XTTS-v2 (necesita GPU).
"""

import os


def generate_voiceover(text, filename="examples/driven_audio/lola_audio.wav", lang="es"):
    """Genera audio con gTTS. Corre en CPU, no requiere GPU."""
    from gtts import gTTS

    tts = gTTS(text, lang=lang)
    tts.save("temp.mp3")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    os.system(f"ffmpeg -y -i temp.mp3 -ar 16000 -ac 1 {filename}")
    os.remove("temp.mp3")
    return filename


def generate_voiceover_clonada(text, filename="examples/driven_audio/lola_audio.wav",
                                referencia="voz_referencia_lola.wav"):
    """Genera audio con voz clonada (XTTS-v2). Requiere GPU —
    correr solo en Colab. El modelo se carga la primera vez que
    se llama y queda en memoria para las siguientes llamadas.
    """
    global _xtts_model
    from TTS.api import TTS

    if "_xtts_model" not in globals():
        _xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    _xtts_model.tts_to_file(
        text=text,
        speaker_wav=referencia,
        language="es",
        file_path=filename,
    )
    return filename
