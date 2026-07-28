# Proyecto Lola — BIG GOOD

Influencer virtual de IA para el food truck BIG GOOD. Este proyecto usa un
esquema **híbrido**: el código se edita y versiona en VS Code (Windows),
pero la ejecución pesada (generación de imagen/voz/video) corre en
Google Colab, porque requiere una GPU que tu máquina local no tiene.

## Por qué este esquema

Tu GPU local (NVIDIA GeForce 920M) no soporta las versiones de CUDA que
necesitan SDXL ni SadTalker. En vez de forzarlo, separamos:

- **Local (VS Code)**: escribir y organizar el código, versionarlo con Git.
- **Colab (nube, GPU gratis)**: ejecutar la generación real.

## Estructura del proyecto

```
lola-project/
├── README.md
├── requirements.txt          <- solo para referencia (Colab instala aparte)
├── .env.example               <- variables de entorno (API keys)
├── src/
│   ├── config.py               <- rasgos fijos de Lola, guiones
│   ├── identidad.py             <- Etapa 1: generación de imagen (SDXL)
│   ├── voz.py                   <- Etapa 2: generación de audio (gTTS / XTTS-v2)
│   ├── animacion.py              <- Etapa 3: SadTalker (lip-sync)
│   └── orquestador.py            <- Etapa 4: une todo (init_lola)
├── examples/
│   ├── source_image/            <- imágenes generadas de Lola
│   └── driven_audio/             <- audios generados
└── colab_bootstrap.ipynb        <- notebook que clona este repo en Colab
```

## Flujo de trabajo recomendado

1. **Editás el código acá, en VS Code**, en la carpeta `src/`.
2. **Subís los cambios a GitHub** (repo propio, puede ser privado):
   ```
   git add .
   git commit -m "ajuste de prompt de Lola"
   git push
   ```
3. **En Colab**, en vez de pegar código celda por celda, cloná tu propio repo:
   ```python
   !git clone https://github.com/TU_USUARIO/lola-project.git
   %cd lola-project
   ```
4. Corrés el notebook `colab_bootstrap.ipynb` (incluido acá), que instala
   dependencias e importa tus módulos de `src/` ya actualizados.

Así cada vez que edites algo en VS Code, con un `git push` + `git pull` en
Colab tenés la versión más nueva corriendo, sin copiar/pegar celdas a mano.

## Setup local en VS Code (solo para editar)

1. Instalá [Python 3.11](https://www.python.org/downloads/) en Windows
   (marcá "Add to PATH" durante la instalación).
2. Instalá la extensión **Python** de Microsoft en VS Code.
3. Abrí esta carpeta en VS Code: `Archivo > Abrir carpeta...`
4. Creá un entorno virtual (no vas a poder correr la parte de GPU acá,
   pero sirve para que el editor no marque errores de imports):
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Nota: `torch`, `diffusers` y `TTS` van a instalar la versión CPU — no
   uses este entorno para generar nada, solo para que VS Code reconozca
   las librerías y te dé autocompletado/detección de errores al editar.

## Setup en Colab (ejecución real)

Ver `colab_bootstrap.ipynb` — clona este repo y corre los módulos de
`src/` en la GPU de Colab.

## Imagen ancla de Lola

A diferencia del resto de las imágenes/audios generados (que están
excluidos del repo por peso, ver `.gitignore`), la imagen ancla oficial
**sí se versiona**, porque es la referencia fija de identidad del
personaje y conviene tenerla siempre disponible junto con el código.

Para que quede incluida:

1. Descargá `lola_512.png` desde Colab (la imagen ancla ya elegida).
2. Copiala a `examples/source_image/lola_512.png` en este proyecto local.
3. Subila con Git como cualquier otro archivo:
   ```
   git add examples/source_image/lola_512.png
   git commit -m "Agregar imagen ancla oficial de Lola"
   git push
   ```

Así, cada vez que clones el repo en una sesión nueva de Colab, la imagen
ya está ahí en `examples/source_image/lola_512.png` — no hace falta
subirla a mano cada vez, ni regenerarla.

## Variables de entorno

Copiá `.env.example` a `.env` y completá tus claves (OpenAI, Hugging Face).
En Colab, seguí usando Secrets (`userdata.get(...)`) como hasta ahora —
`.env` es solo para cuando en el futuro migres a un servidor propio con GPU.
