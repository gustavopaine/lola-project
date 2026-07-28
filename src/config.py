"""
Configuración central del proyecto Lola.
Acá viven los rasgos fijos del personaje y los guiones —
cambiar esto acá se refleja en todos los módulos.
"""

# -----------------------------------------------------------
# Rasgos fijos de Lola — NO cambiar entre generaciones de
# imagen, o la cara pierde consistencia.
# Acortado para entrar en el límite de 77 tokens de CLIP (SDXL).
# -----------------------------------------------------------
LOLA_CHARACTERISTICS = (
    "amateur smartphone selfie, 25-year-old Argentine woman, Patagonia, "
    "long dark brown wavy hair with highlights, honey-brown eyes, freckles, "
    "natural makeup, genuine smile, black tank top, arm extended selfie angle, "
    "golden hour lighting, food truck background, string lights, "
    "shot on iPhone, natural skin texture, candid influencer photo, not studio"
)

# -----------------------------------------------------------
# Rutas por defecto (relativas a la raíz del proyecto en Colab)
# -----------------------------------------------------------
RUTA_IMAGEN_ANCLA = "examples/source_image/lola_512.png"
RUTA_AUDIO_DEFAULT = "examples/driven_audio/lola_audio.wav"
RUTA_VOZ_REFERENCIA = "voz_referencia_lola.wav"

# -----------------------------------------------------------
# Guiones del plan de contenido (agregar más a medida que se
# escriban — ver Biblia de Marca / Plan de contenido)
# -----------------------------------------------------------
SCRIPT_DIA_1 = (
    "Hola, soy Lola, la embajadora virtual de BIG GOOD. "
    "Soy un personaje creado con inteligencia artificial, y estoy acá para "
    "mostrarte la comida más abundante y sabrosa de la Patagonia. "
    "¿Ya probaste el shawarma de BIG GOOD? Acá se viene a comer en serio. "
    "Seguime para que te muestre todo lo que estamos cocinando."
)

GUIONES = {
    "dia_1": SCRIPT_DIA_1,
    # "dia_3": "...",
    # "dia_5": "...",
}
