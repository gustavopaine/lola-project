# Proyecto Lola — BIG GOOD

Influencer virtual de IA para el food truck BIG GOOD. Esquema híbrido:
código editado/versionado en VS Code (Windows), ejecución pesada
(imagen/voz/video) en Google Colab (GPU gratuita).

## Estructura del proyecto

```
lola-project/
├── README.md
├── requirements.txt
├── .env.example
├── colab_bootstrap.ipynb      <- notebook con TODOS los fixes ya aplicados
├── src/
│   ├── config.py               <- rasgos fijos de Lola, guiones
│   ├── identidad.py             <- Etapa 1: imagen (SDXL)
│   ├── voz.py                    <- Etapa 2: audio (gTTS / XTTS-v2)
│   ├── animacion.py                <- Etapa 3: SadTalker (lip-sync)
│   └── orquestador.py               <- Etapa 4: une todo (init_lola)
└── examples/
    └── source_image/lola_512.png    <- imagen ancla oficial (versionada)
```

## Cómo arrancar una sesión nueva de Colab

1. Abrí `colab_bootstrap.ipynb` en Colab (subilo o abrilo desde tu Drive).
2. Activá GPU: Entorno de ejecución → Cambiar tipo de entorno de
   ejecución → GPU.
3. Corré **todas las celdas en orden**, de la 1 a la 15. Ya incluyen
   todos los parches necesarios (ver tabla de troubleshooting abajo) —
   no deberías necesitar diagnosticar nada de cero.

## Troubleshooting — problemas ya resueltos en el bootstrap

Esta tabla documenta errores reales que aparecieron armando el proyecto,
para no perder tiempo re-diagnosticándolos si algo cambia en el futuro
(por ejemplo, si SadTalker actualiza su repo y alguna URL deja de servir).

| Síntoma | Causa | Fix (ya aplicado en el notebook) |
|---|---|---|
| `python3.8: No module named pip` | La build de python3.8 (deadsnakes) no trae pip preinstalado | `apt-get install python3.8-venv` + `ensurepip` (Celda 4) |
| `python3.8: No module named ensurepip` | Mismo motivo — falta el paquete venv | Igual que arriba |
| pip instala todo en python3.8 aunque uses `!pip install` a secas | El `ensurepip` de la celda 4 deja el comando `pip` global apuntando a python3.8 | Usar siempre `!python -m pip install ...` para el entorno principal (Celda 11) |
| Fallo de compilación `basicsr`, `filterpy`, `lmdb` (`bdist_wheel` error) | Faltan headers de compilación para python3.8 | `apt-get install python3.8-dev` (Celda 4) |
| `ModuleNotFoundError: torchvision.transforms.functional_tensor` | `basicsr` fue escrito para una versión vieja de torchvision; el módulo se eliminó en versiones nuevas | Parche con `sed` sobre `basicsr/data/degradations.py` (Celda 7) |
| `stabilityai/stable-diffusion-2-1` da 401/404 en Hugging Face | Stability AI deprecó ese repo (dic. 2025) | Usamos SDXL (`stable-diffusion-xl-base-1.0`) en su lugar |
| `RuntimeError: CUDNN_STATUS_NOT_INITIALIZED` | La GPU se queda sin memoria libre porque el pipeline de SDXL sigue cargado cuando corre SadTalker | `identidad.py` libera la GPU automáticamente después de generar la imagen (`torch.cuda.empty_cache()`) |
| `FileNotFoundError: ./checkpoints/epoch_20.pth` | `download_models.sh` descarga del release `v0.0.2-rc`, pero ese archivo específico solo existe en el release `v0.0.2` (sin "-rc") | Descarga manual desde la URL correcta (Celda 9) |
| Video con 0 segundos / carpeta de resultado solo con `first_frame_dir` | El proceso de SadTalker se corta silenciosamente a mitad de camino (por errores que `os.system()` no muestra) | Usar `diagnosticar_error()` de `src/animacion.py`, que captura STDOUT/STDERR completos con `subprocess` |
| `inference.py` no encuentra la imagen/no genera nada | Hay que estar parado en la carpeta `SadTalker/` para correr `inference.py`, pero las rutas de imagen son relativas a `lola-project/` | Usar ruta **absoluta** para la imagen y `os.chdir()` a `SadTalker/` antes de generar (Celda 13) |
| El notebook solo mueve la boca, no la cabeza | El flag `--still` limita el movimiento a los labios | Se sacó `--still` de `create_ai_influencer` (por defecto ahora es `still=False`) |
| CLIP trunca el prompt de SDXL ("The following part of your input was truncated...") | El prompt superaba 77 tokens | `LOLA_CHARACTERISTICS` en `config.py` está acortado para entrar en el límite |

## Imagen ancla de Lola

La imagen ancla oficial (`examples/source_image/lola_512.png`) está
versionada en este repo — no hace falta regenerarla en cada sesión
nueva de Colab. El `.gitignore` excluye el resto de imágenes generadas
por peso, pero hace una excepción explícita para esta.

## Variables de entorno

Copiá `.env.example` a `.env` para referencia local. En Colab, seguí
usando Secrets (`userdata.get(...)`) para `OPENAI_API_KEY` y `HF_TOKEN`.

## Flujo de trabajo

1. Editás código en VS Code.
2. `git add . && git commit -m "..." && git push`.
3. En Colab: `colab_bootstrap.ipynb` → correr todas las celdas.
4. Nuevos guiones van en `src/config.py`, diccionario `GUIONES`.

`init_lola` acepta un `guion_id` (ej. `"dia_1"`) que identifica el video
final (`./results/dia_1.mp4`). Si ese archivo ya existe, la corrida se
saltea por completo — así podés re-correr la Celda 13 sin miedo a
regenerar un video que ya tenías. La etapa de SadTalker además reintenta
automáticamente (`max_retries`, default 1) si detecta el fallo silencioso
ya conocido (ver tabla de troubleshooting).

## Tests

La lógica de reintentos/verificación/idempotencia (sin GPU) tiene tests:

```
pip install -r requirements-dev.txt
pytest
```
