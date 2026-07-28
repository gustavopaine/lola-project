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

SCRIPT_DIA_3 = (
    "Uy, esto tiene una pinta... a ver, a ver. Mmm, no, esperá. Esto "
    "está buenísimo. El shawarma de BIG GOOD tiene una salsa que no sé "
    "ni qué tiene pero no puedo parar. Andá a probarlo, en serio."
)

SCRIPT_DIA_7 = (
    "Bueno, me preguntaron un montón cuál es mi combo favorito, así "
    "que les cuento: para mí no hay nada como el shawarma con papas y "
    "una jugosa bien fría. Pero contame vos, ¿cuál es el tuyo? "
    "Dejámelo en los comentarios que lo leo todo."
)

SCRIPT_DIA_9 = (
    "Miren el tamaño de esto. Esta es la hamburguesa gigante de BIG "
    "GOOD, con doble carne y cheddar derretido. Si tenés hambre de "
    "verdad, esta es la tuya."
)

SCRIPT_DIA_11 = (
    "Hoy les muestro cómo es un día acá en BIG GOOD. Desde que "
    "prendemos la parrilla tempranito hasta que llega la primera cola "
    "de gente con hambre. Esto no para en todo el día, y la verdad "
    "que me encanta."
)

SCRIPT_DIA_13 = (
    "Atención, esta semana tenemos una promo que no se pueden perder: "
    "shawarma más papas más bebida a un precio que no van a creer. "
    "Solo por tiempo limitado, así que no esperes mucho."
)

GUIONES = {
    "dia_1": SCRIPT_DIA_1,
    "dia_3": SCRIPT_DIA_3,
    "dia_7": SCRIPT_DIA_7,
    "dia_9": SCRIPT_DIA_9,
    "dia_11": SCRIPT_DIA_11,
    "dia_13": SCRIPT_DIA_13,
    # dia_5 y dia_14 son contenido visual/interactivo, sin guion hablado
}
