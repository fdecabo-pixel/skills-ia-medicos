---
name: configura-tu-cierre
description: "Guía al usuario para montar su ritual de cierre de sesión con una skill propia que, al terminar de trabajar con el agente, guarda el estado del proyecto y los aprendizajes, de modo que la siguiente sesión arranque con contexto. Usar cuando diga «el agente no se acuerda de lo que hicimos ayer», «quiero que guarde lo aprendido», «monta mi memoria de proyectos» o «configura un cierre del día»."
---

# Configura tu cierre de sesión

Un agente empieza cada conversación sin recordar la anterior, como un compañero que entra de guardia sin pase. Esta skill monta **el pase de guardia**: una skill propia de cierre y los archivos de memoria donde se escribe.

## Antes de empezar

Mira si ya existe la skill resultante (`cierre/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Fase 1 · Entrevista

De una en una:

1. ¿En qué carpeta guardas tu trabajo con el agente? Si no hay una o está desordenada, monta antes la estructura con la skill `ordena-tu-espacio-de-trabajo`; si no tiene esa skill instalada, propón una sola carpeta de trabajo con una subcarpeta por proyecto.
2. ¿Qué proyectos tienes abiertos ahora mismo?
3. ¿Usas un solo agente o varios (Claude Code, Codex)? Si son varios, la memoria debe ser un único sitio que lean todos.
4. ¿Qué te gustaría que recordara siempre? (cómo te gusta que te expliquen las cosas, qué no hacer nunca, formatos preferidos)

## Fase 2 · Montar la estructura

1. **Un archivo de estado por proyecto**, en la carpeta de cada proyecto: `CLAUDE.md` si usa solo Claude Code, `AGENTS.md` si usa solo Codex. Si usa los dos, escribe el contenido en `AGENTS.md` y deja en `CLAUDE.md` una sola línea, `@AGENTS.md`, que hace que Claude Code lea el otro archivo. Contenido mínimo: qué es el proyecto, estado actual, decisiones tomadas, siguiente paso y una bitácora con fecha. Si el proyecto ya tiene archivo de estado, complétalo; no lo rehagas.
2. **Una carpeta de memoria general**, fuera de los proyectos (si ya tiene la estructura de `ordena-tu-espacio-de-trabajo`, es `00-sistema/memoria/`; no crees otra), con un archivo por aprendizaje y un índice `MEMORY.md` de una línea por archivo. Nombre de cada archivo: `<tipo>-<asunto>.md` (por ejemplo `trampa-excel-cambia-fechas.md`). Tres tipos bastan:
   - forma de trabajar (una corrección o preferencia, con su porqué). Lo que contestó a la pregunta 4 se guarda aquí, un archivo por preferencia;
   - receta (algo técnico que funcionó y se repetirá);
   - trampa (algo que falló y cómo se resolvió).
3. **Las instrucciones generales del agente** (`~/.claude/CLAUDE.md` en Claude Code, `~/.codex/AGENTS.md` en Codex). Añade al final, sin borrar lo que haya (si el archivo o su carpeta no existen, créalos), dos líneas: dónde está la memoria y que hay que leer su índice al empezar.

Antes de crear nada, enseña la estructura propuesta y espera su conformidad. No muevas ni renombres carpetas existentes sin permiso.

## Fase 3 · Construir la skill de cierre

Crea `cierre/SKILL.md` en la ubicación indicada en «Dónde guardar la skill resultante», con este procedimiento adaptado a sus rutas:

1. Identificar en qué proyecto se ha trabajado; si hay duda, preguntar.
2. Decir al usuario en 3-5 líneas qué se ha hecho y qué se propone guardar, y esperar su confirmación.
3. Actualizar el archivo de estado del proyecto: entrada de bitácora con fecha, estado, siguiente paso y los archivos creados o cambiados, indicando cuál es la versión vigente y dónde está.
4. Guardar en la memoria general solo lo que servirá en otro proyecto. Antes de crear un archivo, buscar si ya existe uno que lo cubra y actualizarlo.
5. Resumir qué archivos se han tocado.

Regla de oro que debe figurar en la skill: lo específico de un proyecto va a su archivo de estado; lo que servirá en otro proyecto va a la memoria general; lo que solo importa en esta conversación no se guarda.

## Fase 4 · Probar

La skill recién creada no se carga hasta abrir una conversación nueva, así que ahora sigue a mano los pasos del `cierre/SKILL.md` que acabas de escribir. Si en esta sesión no se ha trabajado en ningún proyecto, pide al usuario uno y lo último que hizo en él. Después, pídele que abra una conversación nueva y pregunte «¿en qué estado está el proyecto X?» para comprobar que el agente lo sabe.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `cierre/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/cierre/`
- Codex: `~/.agents/skills/cierre/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
- En la memoria no se guardan claves ni datos de pacientes; tampoco listas de tareas pasajeras.
