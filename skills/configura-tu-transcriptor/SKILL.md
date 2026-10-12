---
name: configura-tu-transcriptor
description: "Guía al usuario para montar su flujo de audio a documento. Instala un transcriptor que funciona en su propio ordenador y crea una skill propia que convierte audios (notas de voz, reuniones, clases) en texto, acta, apuntes o borrador de correo. Usar cuando diga «quiero transcribir audios», «pasa a texto mis notas de voz», «saca el acta de esta reunión» o «monta un transcriptor»."
---

# Configura tu transcriptor

Monta un transcriptor **local**: el audio se convierte en texto dentro del ordenador del usuario, sin subirlo a ningún servicio.

**El límite que hay que explicar desde el principio:** el audio no sale del ordenador, pero todo texto que el agente lea sí viaja a la nube. Si un audio contiene datos de pacientes, el agente lo transcribe a un archivo **sin leerlo** y es el usuario quien lo anonimiza a mano antes de pedir nada más.

## Antes de empezar

Mira si ya existe la skill resultante (`transcribir/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Fase 1 · Entrevista

De una en una:

1. ¿Qué ordenador usas? (Mac con procesador Apple, Mac con Intel, Windows, Linux)
2. ¿De dónde vienen tus audios? (notas de voz de mensajería, grabadora del móvil, grabaciones de reuniones o clases)
3. ¿Qué quieres obtener casi siempre? (texto literal, acta con acuerdos, apuntes ordenados, borrador de correo)
4. ¿En qué carpeta sueles dejarlos y dónde quieres las transcripciones? Si no lo sabe, propón una subcarpeta `transcripciones/` junto a los audios.
5. ¿Hay nombres propios, fármacos o siglas que se repitan? Se usarán como vocabulario de ayuda.

## Fase 2 · Instalar y medir

1. Comprueba qué hay ya instalado: `ffmpeg` (convierte formatos de audio) y algún motor Whisper (el modelo de transcripción).
2. Instala lo que falte, explicando cada paso antes de ejecutarlo. Siempre en un entorno propio, nunca con `pip install` a secas (en Mac y Linux actuales da error): `python3 -m venv ~/transcriptor` y `~/transcriptor/bin/pip install <paquete>`.
   - Mac con procesador Apple: paquete `mlx-whisper`, mucho más rápido en ese procesador. Necesita `ffmpeg` (`brew install ffmpeg` si tiene Homebrew); si no tiene Homebrew, usa `faster-whisper`, que no lo necesita.
   - Mac con Intel: `faster-whisper`.
   - Windows: `winget install Python.Python.3.12`; después `py -m venv %USERPROFILE%\transcriptor` y `%USERPROFILE%\transcriptor\Scripts\pip install faster-whisper`.
   - Linux: `sudo apt install python3-venv` y `faster-whisper`.
   - `faster-whisper` no trae orden de terminal: escribe un guion `transcribir.py` que reciba el audio, guarde el texto en un archivo y no imprima nada por pantalla.
   - El paquete alternativo se llama `openai-whisper`. Nunca instales `whisper` a secas: es otro programa.
3. Elige el modelo. Empieza por `large-v3-turbo` (en `mlx-whisper` se llama `mlx-community/whisper-large-v3-turbo`). Si el ordenador va justo, baja a `small` (en `mlx-whisper`, `mlx-community/whisper-small-mlx`). Avisa de que la primera vez se descarga el modelo (alrededor de 1,5 GB el grande; unos cientos de MB el pequeño) y hace falta internet solo ese día.
4. Haz una prueba con un audio corto **sin datos de pacientes** (pídele que grabe una nota de prueba), mide cuánto tarda y enséñale el resultado.

Anota la ruta completa de cada programa: irán escritas en la skill. Si el motor llama a `ffmpeg` por su nombre, la orden debe anteponer su carpeta al PATH (por ejemplo `PATH=/opt/homebrew/bin:$PATH …` en un Mac con procesador Apple).

## Fase 3 · Construir la skill

Crea `transcribir/SKILL.md` en la ubicación indicada en «Dónde guardar la skill resultante», con:

1. **Rutas fijas** de los programas, el modelo elegido y la orden exacta.
2. **Localizar el audio**: si no se da ruta, buscar el más reciente en su carpeta habitual y confirmar cuál es si hay varios.
3. **Preguntar antes de transcribir si el audio contiene datos de pacientes.**
   - Si los contiene: transcribir sin mostrar el texto (en `mlx-whisper` y `openai-whisper`, `--verbose False` y salida solo a archivo; con `faster-whisper`, el guion solo escribe en el archivo), no abrir ni leer el archivo, decirle dónde está y terminar. Acta, apuntes o correo, solo cuando el usuario diga que lo ha anonimizado él.
   - Si no los contiene: seguir con los pasos siguientes.
4. **Transcribir** en su idioma (`--language es`), pasando su vocabulario habitual como ayuda (opción `--initial-prompt "…"` en `mlx-whisper` y `openai-whisper`; `initial_prompt=` en `faster-whisper`). Si el audio es largo, lanzarlo de forma que no bloquee la conversación.
5. **Comprobar que el archivo de texto existe y no está vacío.** Algunos motores no avisan cuando fallan.
6. **Entregar** según lo que pida; si no lo dice, preguntar una vez entre sus formatos de la entrevista:
   - literal: tal cual, sin corregir;
   - acta: temas, acuerdos y pendientes con responsable;
   - apuntes: ordenado por apartados;
   - correo: borrador, nunca enviado.
7. **Reglas**: no inventar nada que no esté en el audio; si una cifra o un nombre no se entiende, marcarlo como dudoso en vez de adivinar; abrir el resultado al terminar (`open` en Mac, `start` en Windows, `xdg-open` en Linux).

## Fase 4 · Probar

Transcribe un audio real sin datos de pacientes, entrégalo en su formato favorito y corrige con él los nombres mal entendidos; añádelos al vocabulario de la skill.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `transcribir/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/transcribir/`
- Codex: `~/.agents/skills/transcribir/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
- Los audios con información clínica se transcriben solo en local y el agente no lee su texto. No los subas a servicios en línea.
