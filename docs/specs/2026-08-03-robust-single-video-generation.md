# Generación robusta de un video (retries + idempotencia)

Status: Implemented (2026-08-03)

## Review summary

Esto hace más confiable el llamado a `init_lola(...)` para generar UN video
por vez: detecta automáticamente si SadTalker falló silenciosamente (el
problema ya documentado en el README: "video de 0 segundos / carpeta con
solo `first_frame_dir`"), reintenta esa etapa hasta 1 vez más si falla, y
evita regenerar un video que ya existe si volvés a correr la misma celda por
error. No procesa varios guiones en batch — eso quedó explícitamente
descartado en la conversación de diseño (ver Non-goals).

Elementos que van más allá de lo pedido literalmente ("un comando con
reintentos"):

- **[added] `init_lola` devuelve la ruta a un único video en vez de
  `sorted(os.listdir('./results/'))`.** Necesario para que "robusto" tenga
  sentido: hoy `res[-1]` en el notebook asume que el video correcto es el
  último en orden alfabético entre las carpetas de `results/`, lo cual es
  frágil. Esto cambia el tipo de retorno y obliga a actualizar las celdas
  13-15 de `colab_bootstrap.ipynb`.
- **[added] Parámetro nuevo `guion_id`** (ej. `"dia_1"`) para nombrar el
  video final (`results/dia_1.mp4`) y habilitar el chequeo de idempotencia.
  Es opcional — sin él, el comportamiento es como antes (sin idempotencia,
  sin copia con nombre limpio).
- **[added] Tests con pytest** para la lógica de detección/verificación/
  reintentos (no toca las etapas GPU). Acordado explícitamente con el
  usuario (TDD para la parte testeable localmente).

Lo que esto NO hace: no procesa múltiples guiones en una corrida, no agrega
reintentos a las etapas de imagen (SDXL) o voz (gTTS/XTTS) — solo a
SadTalker, que es la etapa señalada como inestable —, y no toca la
convención de nombre de archivo de audio en `voz.py`.

## Contexto y decisiones ya tomadas

- Alcance: un video por llamado a `init_lola`, no batch. (Se descartó
  explícitamente procesar todo `GUIONES` de una corrida.)
- Manejo de fallos de SadTalker: reintentar automáticamente (no ilimitado),
  loguear el error si se agotan los reintentos.
- Idempotencia: si el video ya existe (identificado por `guion_id`), no
  regenerar nada.
- TDD: sí, para la lógica pura Python (sin GPU) — detección de carpeta de
  salida, verificación de mp4 válido, loop de reintentos, chequeo de
  idempotencia.
- Proceso: commits directos en `main`, sin PR ni code review formal (proyecto
  de un solo desarrollador).

## Diseño

### `src/animacion.py`

Nueva excepción `SadTalkerGenerationError(Exception)` — se lanza cuando se
agotan los reintentos sin obtener un video válido. El mensaje incluye la
razón (sin carpeta nueva / sin mp4 / mp4 vacío) y la cola de stderr del
último intento, para no perder el diagnóstico que hoy solo daba
`diagnosticar_error()`.

Dos helpers nuevos, testeables sin GPU (no importan `torch` ni corren
`inference.py`):

```python
def _snapshot_results_dirs(result_dir="./results") -> set[str]:
    """Nombres de subcarpetas existentes en result_dir ahora mismo."""

def _find_output_video(before: set[str], result_dir="./results") -> str:
    """Compara contra el snapshot 'before', ubica la carpeta nueva que creó
    esta corrida de inference.py, y devuelve la ruta al .mp4 que contiene.
    Lanza SadTalkerGenerationError si: no hay carpeta nueva, la carpeta
    nueva no tiene ningún .mp4 directamente adentro (ej. solo
    first_frame_dir/), o el .mp4 encontrado pesa 0 bytes.
    """
```

`create_ai_influencer` pasa a tomar snapshot antes de cada intento, correr
`inference.py` con `subprocess.run(capture_output=True, text=True)` (en vez
de `os.system`, para tener stderr disponible en el mensaje de error), y
verificar con `_find_output_video`. Nueva firma:

```python
def create_ai_influencer(image_path, audio_path, pose_style=0, still=False,
                          result_dir="./results", max_retries=1):
    """... devuelve la ruta al .mp4 generado (str), no una lista de
    carpetas. Reintenta hasta max_retries veces si la verificación falla;
    si se agotan los intentos, lanza SadTalkerGenerationError."""
```

`diagnosticar_error` no cambia — sigue siendo la herramienta manual
documentada en el README para inspeccionar un fallo a mano.

### `src/orquestador.py`

`init_lola` suma `guion_id=None`, `max_retries=1`, `result_dir="./results"`:

```python
def init_lola(script_text, characteristics=None, reusar_imagen=None,
               pose_style=0, guion_id=None, max_retries=1,
               result_dir="./results"):
```

Comportamiento:

1. Si `guion_id` está presente y `{result_dir}/{guion_id}.mp4` ya existe:
   imprime un mensaje de skip y devuelve esa ruta sin tocar imagen/audio/
   SadTalker.
2. Si no, corre las etapas de imagen y audio como hoy (sin cambios).
3. Llama a `create_ai_influencer(..., max_retries=max_retries)`. Si lanza
   `SadTalkerGenerationError`, se propaga tal cual (no se atrapa en
   `init_lola` — con un solo guion por llamado no hay "siguiente" al cual
   seguir, así que el fallo debe ser visible, no silencioso).
4. Si tuvo éxito y hay `guion_id`: copia (`shutil.copy2`) el video verificado
   a `{result_dir}/{guion_id}.mp4` y devuelve esa ruta.
5. Si no hay `guion_id`: devuelve la ruta que dio `create_ai_influencer` tal
   cual (sin copiar/renombrar) — compatible con usos ad-hoc sin plan de
   contenido.

### `colab_bootstrap.ipynb`

Actualizar celdas 13-15 al nuevo contrato:

```python
res = init_lola(
    SCRIPT_DIA_1,
    guion_id="dia_1",
    reusar_imagen='/content/lola-project/examples/source_image/lola_512.png'
)
print(res)  # ./results/dia_1.mp4
```

```python
from IPython.display import Video
Video(res, embed=True, width=400)
```

```python
from google.colab import files
files.download(res)
```

### `README.md`

Agregar una línea breve en "Flujo de trabajo" mencionando `guion_id` y que
re-correr la celda no regenera un video ya hecho.

### Tests (nuevos, TDD)

`requirements-dev.txt` nuevo: `pytest`.

- `tests/test_animacion.py`: `_snapshot_results_dirs` / `_find_output_video`
  contra un filesystem temporal real (`tmp_path`) cubriendo: éxito (carpeta
  nueva con un .mp4 válido), sin carpeta nueva, carpeta nueva solo con
  `first_frame_dir/`, .mp4 de 0 bytes. `create_ai_influencer` con
  `subprocess.run` y `liberar_gpu` mockeados (`monkeypatch`): éxito al
  primer intento, éxito recién en el reintento, y falla agotando
  `max_retries` (verifica que lance `SadTalkerGenerationError`).
- `tests/test_orquestador.py`: `init_lola` con las cuatro etapas mockeadas —
  verifica que con `guion_id` y video ya existente se saltee todo, y que sin
  ese archivo se llame a las etapas y se copie el resultado al nombre final.

Correr con `pytest` desde la raíz del repo.

## Non-goals (descartados en la conversación)

- **Batch de todos los guiones en una corrida** — se preguntó explícitamente
  y el usuario eligió mantener un video por llamado. Si más adelante se
  quiere, esta base (idempotencia + reintentos por guion) es lo que haría
  viable iterar sobre `GUIONES` sin re-trabajo — ver ledger abajo.
- **Reintentos en las etapas de imagen (SDXL) o voz (gTTS/XTTS)** — el
  usuario señaló específicamente a SadTalker como la etapa inestable; no hay
  evidencia de fallos intermitentes en las otras etapas, así que no se
  agrega complejidad especulativa ahí.
- **Convención de nombre de archivo de audio por guion_id en `voz.py`** — no
  hace falta para que la idempotencia funcione (si el video ya existe, la
  etapa de audio ni se llama), y tocar `voz.py` no forma parte de lo pedido.
- **Consolidar `diagnosticar_error` con la nueva lógica de reintentos** —
  sigue siendo una herramienta manual válida tal como la documenta el
  README; no se modifica en esta iteración.

## Deferred aspects

- **Batch de todos los `GUIONES` pendientes en una corrida.** Por qué: el
  usuario lo descartó para esta iteración a favor de robustecer el llamado
  individual primero. Condición de retorno: si en el uso real se vuelve
  tedioso llamar `init_lola` a mano por cada guion. Encaje: recorrería
  `GUIONES.items()` reusando exactamente el chequeo de idempotencia y el
  loop de reintentos que esta spec introduce — no requeriría rediseño, solo
  un wrapper nuevo en `orquestador.py`.
- **Naming de audio por `guion_id` en `voz.py`.** Por qué: fuera de alcance
  de esta iteración (ver Non-goals). Condición de retorno: si se implementa
  el batch de arriba, ahí sí haría falta para no pisar el audio de un guion
  con el del siguiente dentro de la misma corrida. Encaje: mismo patrón que
  el naming de video (`{result_dir}/{guion_id}.mp4`), aplicado a
  `examples/driven_audio/{guion_id}.wav`.

## Implementation guidance
- TDD: on, para `src/animacion.py` (helpers + retry loop) y
  `src/orquestador.py` (idempotencia). No aplica a las etapas GPU-only
  (SDXL, XTTS, SadTalker real) — esas no se pueden correr localmente.
- Isolation: checkout actual (`main`), sin rama aparte — acordado con el
  usuario.
- Verify: `pytest` desde la raíz del repo debe pasar antes de dar cualquier
  tarea por terminada. No hay typecheck/linter configurado en el proyecto.
- Review: sin review formal — acordado con el usuario (proyecto de un solo
  desarrollador). Validación real queda pendiente de que el usuario corra el
  flujo en Colab.
- Scope: construir solo lo que especifica este documento — no expandir a
  batch ni a las otras etapas.
- Deferred aspects: reconciliado arriba — sin tracker externo (el proyecto
  no usa uno).
- Build order: (1) `_snapshot_results_dirs` / `_find_output_video` +
  `SadTalkerGenerationError` con sus tests, (2) `create_ai_influencer` con
  retry loop y sus tests, (3) `init_lola` con idempotencia/copia y sus
  tests, (4) actualizar `colab_bootstrap.ipynb` (celdas 13-15), (5)
  actualizar `README.md`.
- Routing: todo en el orquestador (esta sesión) — es un cambio acotado a 3
  archivos + notebook + README, no amerita delegar a un subagente por
  eficiencia de tokens.
- Orchestrator: sesión actual, esfuerzo medio — lógica directa de
  filesystem/subprocess, sin componentes algorítmicamente complejos.
