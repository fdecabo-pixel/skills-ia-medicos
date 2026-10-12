---
name: concurso-cierre-charla
description: "Guía al usuario para montar su skill de concurso de cierre de charla. A partir de los temas de una sesión genera las preguntas tipo test con su estilo y las deja listas para su plataforma de concursos (Kahoot, Wooclap, Mentimeter u otra). Usar cuando diga «hazme un concurso para el final de la charla», «prepara un kahoot de esta sesión», «quiero gamificar mis clases» o «monta mi skill de concursos»."
---

# Tu concurso de cierre de charla

Un concurso corto al final de una charla fija las ideas principales y deja buen recuerdo. Esta skill construye la skill del usuario: con su formato, su tono y su plataforma.

## Antes de empezar

Mira si ya existe la skill resultante (`concurso-charla/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Fase 1 · Entrevista

De una en una:

1. ¿Qué plataforma usas? (Kahoot, Wooclap, Mentimeter, otra, o ninguna todavía)
2. ¿Cuántas preguntas y cuánto tiempo por pregunta? Propuesta si no lo sabe: 5 preguntas, 4 opciones, 1 correcta, 20 segundos.
3. ¿Qué tono? (serio, con una opción de humor por pregunta, mixto)
4. ¿Hay premio? Si lo hay, la última pregunta puede valer doble; se activa a mano en la plataforma después de importar.
5. ¿Para qué público sueles hablar? (residentes, compañeros, estudiantes, pacientes)

## Fase 2 · Cómo se sube a cada plataforma

Compruébalo en la ayuda oficial de su plataforma antes de escribir la skill, porque cambia. Situación en octubre de 2026:

- **Kahoot**: importa una hoja de cálculo `.xlsx` con su plantilla oficial (pregunta, cuatro respuestas, tiempo y respuesta correcta). Límites: pregunta de 120 caracteres como máximo, respuesta de 75, solo texto, tiempo de la lista que ofrece la plantilla y una sola respuesta correcta (varias correctas exigen plan de pago). Ruta en la aplicación: Create → Add → Import → Import spreadsheet.
- **Wooclap**: importa un archivo de Excel con su propia plantilla, que se descarga desde su diálogo «Import from an Excel file» con la sesión iniciada: pídesela al usuario.
- **Mentimeter**: no importa preguntas desde un archivo. Entrega el borrador listo para copiar y pegar.

Descarga siempre la plantilla oficial vigente desde la ayuda de la plataforma. Si no puedes, pide al usuario que la baje él y te diga dónde está. No uses copias antiguas ni supongas las columnas.

## Fase 3 · Construir la skill

Crea `concurso-charla/SKILL.md` en la ubicación indicada en «Dónde guardar la skill resultante», con este procedimiento:

1. **Recoger los temas**: de las diapositivas, del guion o de lo que el usuario cuente, sin datos de pacientes reales. Una pregunta por idea principal de la charla, no por detalle. Si hay más ideas que preguntas, propón cuáles entran y deja elegir.
2. **Redactar el borrador** con su formato y los límites de caracteres de su plataforma. Normas de una buena pregunta:
   - se entiende al primer vistazo;
   - una sola respuesta claramente correcta, basada en lo dicho en la charla;
   - las incorrectas serias son verosímiles y de longitud parecida;
   - si hay opción de humor, una por pregunta, y cambia de posición;
   - la correcta cambia de posición entre preguntas;
   - nada de «todas las anteriores».
3. **Enseñar el borrador y esperar su conformidad.** No se crea nada en la plataforma sin ese paso.
4. **Dejarlo listo para subir**: rellenar la plantilla oficial con un guion (en Python, el paquete `openpyxl` en un entorno propio: `python3 -m venv .venv` y `.venv/bin/pip install openpyxl`). Después reabrir el archivo y contar caracteres. Si no se puede generar el archivo, entregar una tabla para que el usuario la pegue en la plantilla.
5. **Verificar** tras la importación: pedir al usuario una captura o el enlace de vista previa y comparar, pregunta a pregunta, texto, respuesta correcta, tiempo y puntos dobles con lo aprobado.

Si el usuario quiere que el agente lo cree directamente en la plataforma con el navegador, explícale que eso exige que él inicie sesión en una ventana del navegador; el agente no pide ni guarda su contraseña.

## Fase 4 · Probar

Pídele los temas de su próxima charla y genera el concurso completo. Si puede importarlo en ese momento, hacedlo y verificad; si no, la prueba se cierra con el archivo validado. Ajusta la skill con lo que cambie.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `concurso-charla/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/concurso-charla/`
- Codex: `~/.agents/skills/concurso-charla/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
