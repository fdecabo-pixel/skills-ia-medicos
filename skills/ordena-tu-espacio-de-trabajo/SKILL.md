---
name: ordena-tu-espacio-de-trabajo
description: "Guía al usuario para montar y mantener una estructura de carpetas ordenada para trabajar con su agente, con una carpeta de trabajo con grupos temáticos, un archivo .md de estado en cada proyecto, un catálogo y una carpeta de infraestructura donde viven las skills y los MCP que instala. Usar cuando diga «tengo las carpetas hechas un lío», «organiza mi espacio de trabajo», «¿dónde guardo esto?», «el agente no encuentra mis proyectos» o «monta una estructura de carpetas»."
---

# Ordena tu espacio de trabajo

Un agente trabaja mejor cuando sabe dónde está cada cosa, igual que un residente nuevo rinde más en un servicio con los protocolos en su sitio. Esta skill monta la estructura del usuario y le deja otra skill propia para mantenerla.

La idea central: **cada carpeta de proyecto lleva un archivo .md que explica qué es y en qué estado está.** El agente lee ese archivo al empezar y no hay que contárselo todo cada vez.

## Antes de empezar

Mira si ya existe la skill resultante (`orden-<nombre>/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Fase 1 · Mirar antes de tocar

1. Pregunta dónde guarda ahora lo que hace con el agente (Escritorio, Documentos, Descargas, la nube) y, antes de listar nada, en cuáles de esas carpetas hay datos de pacientes, contraseñas o copias de seguridad. Esas no se listan.
2. Lista las demás **sin abrir los archivos** y sin mover nada.
   - Si al listar aparecen archivos con nombres de pacientes, deja de listar esa carpeta y pásala a «No tocar».
   - Si una carpeta, por su nombre, parece contener historias clínicas o datos de pacientes, no entres en ella ni listes su contenido.
   - Si ves un archivo que por su nombre guarda contraseñas, no lo abras ni lo muevas: avisa al usuario de que conviene pasarlo a un gestor de contraseñas.
   - Anota las rutas de unas y otros, junto con las carpetas de la nube o compartidas, en una lista «No tocar».
3. Pregunta, de una en una:
   - ¿En qué ámbitos trabajas? (asistencia, docencia, investigación, gestión, divulgación, asuntos personales)
   - ¿Qué proyectos tienes abiertos ahora?
   - ¿Usas un agente o varios (Claude Code, Codex)?
   - ¿Hay carpetas sincronizadas con la nube o compartidas con otras personas? Esas no se mueven.

## Fase 2 · Proponer la estructura

Propón algo así, adaptado a sus ámbitos, y explícalo antes de crear nada. La carpeta `trabajo/` se crea en su carpeta personal (`~/trabajo/`) salvo que prefiera otro sitio; nunca dentro de una carpeta sincronizada con la nube.

```
trabajo/
├── AGENTS.md                  ← mapa de entrada: qué hay, dónde, y la lista «No tocar»
├── CLAUDE.md                  ← una sola línea: @AGENTS.md
├── 00-sistema/
│   ├── catalogo.md            ← una línea por proyecto: nombre, carpeta, para qué
│   ├── memoria/               ← aprendizajes que sirven en varios proyectos
│   └── infraestructura/       ← skills y MCP instalados
├── 01-<ámbito>/
│   └── <proyecto>/
│       ├── AGENTS.md          ← estado del proyecto
│       └── …
├── 02-<ámbito>/
└── buzon/                     ← donde el usuario deja material sin clasificar
```

Criterios:

- **Pocos grupos de primer nivel**, numerados, uno por ámbito. Entre 4 y 7.
- **Nombres de carpeta que se expliquen solos**, en minúsculas y con guiones: `curso-residentes-otoscopia`, no `curso2` ni `nuevo final`. Los archivos conservan su nombre salvo que el usuario pida renombrarlos.
- **Un proyecto, una carpeta.** Capturas, descargas y borradores van dentro del proyecto, no sueltos. Si un ámbito no tiene proyectos, crea en él una carpeta de material permanente con nombre descriptivo (`protocolos-y-plantillas`) y su archivo de estado.
- **Lo personal, aparte** del trabajo, en una carpeta hermana (`~/personal/`).
- **Los datos clínicos reales no entran en esta estructura.** Siguen donde el centro o la ley exijan.

## Fase 3 · El .md de cada carpeta

Crea en cada proyecto su archivo de estado con esta plantilla, rellenada con lo que el usuario cuente:

```
# <Nombre del proyecto>

## Estado
- Qué es: una frase.
- Fase actual (fecha): …
- Siguiente paso: …

## Decisiones
- (fecha) qué se decidió y por qué.

## Reglas
- Lo que no debe hacerse en este proyecto.

## Bitácora
- (fecha) qué se hizo.
```

Si usa Claude Code y Codex, escribe el contenido en `AGENTS.md` y deja en `CLAUDE.md` una sola línea, `@AGENTS.md`, que hace que Claude Code lea el otro archivo. Si usa solo Claude Code, basta `CLAUDE.md`.

El archivo de la raíz es el mapa: qué grupos hay, dónde está el catálogo, dónde la memoria, la lista «No tocar» y la regla «lee el estado del proyecto antes de actuar».

Para que el agente encuentre el mapa aunque arranque en otra carpeta, añade a sus instrucciones generales (`~/.claude/CLAUDE.md` en Claude Code, `~/.codex/AGENTS.md` en Codex), sin borrar lo que haya y creando el archivo si no existe, una línea con la ruta real: «Mi espacio de trabajo está en `<ruta>`; lee el archivo de su raíz (`AGENTS.md` o `CLAUDE.md`) antes de actuar».

## Fase 4 · La carpeta de infraestructura

Aquí viven las herramientas que el usuario instala desde GitHub: skills y MCP (un MCP es un conector entre el agente y otra aplicación). Tenerlas en un sitio conocido evita perderlas y permite actualizarlas.

- Cada repositorio clonado, en su carpeta: `00-sistema/infraestructura/<nombre>/`. Un repositorio puede traer varias skills.
- Un archivo `00-sistema/infraestructura/INSTALADO.md` con una línea por skill o MCP en uso: nombre, repositorio de origen (o «propia»), fecha y para qué la usa.
- Las **skills** se enlazan desde la carpeta de skills del agente (`~/.claude/skills/`, `~/.agents/skills/`) con un enlace simbólico, que es un acceso directo: el archivo está en un solo sitio y los dos agentes lo ven. En Windows, si los enlaces dan problemas, se copia la carpeta.
- Las **claves** de los MCP nunca van en esta carpeta: se guardan en `~/.config/<servicio>/` y aquí solo se anota la ruta.
- Si ya hay herramientas instaladas en otro sitio (por ejemplo `~/infraestructura-ia/`), propón moverlas aquí, rehaz los enlaces y comprueba que resuelven.

Enseña al usuario la forma de instalar a partir de ahora, que es dársela al agente:

> Instala la skill X del repositorio <dirección>. Clónalo en mi carpeta de infraestructura, enlaza la skill en mi agente y apúntalo en INSTALADO.md.

Antes de instalar cualquier cosa de un repositorio ajeno, lee su contenido y dile al usuario qué hace y qué permisos pide. Una skill o un MCP son instrucciones y programas que el agente ejecutará.

## Fase 5 · Migrar sin perder nada

1. Enseña la tabla «carpeta actual → carpeta nueva» y espera su conformidad.
2. **Mueve, no borres.** Ningún archivo se elimina en esta fase.
3. **No sobrescribas.** Si en destino ya existe un archivo con el mismo nombre, déjalo en origen y pregunta. Los duplicados se conservan los dos.
4. Mueve proyecto a proyecto y comprueba tras cada uno que los archivos están en destino.
5. Lo que no sepas clasificar sin abrirlo va a `buzon/` y se pregunta.
6. No toques carpetas de aplicaciones, de la nube ni del sistema, ni nada de la lista «No tocar».
7. Al terminar, escribe el catálogo y enseña la lista de carpetas de origen que han quedado vacías. Es la única excepción a la regla de no borrar: se borran solo con su sí expreso, una a una.

## Fase 6 · Construir la skill de mantenimiento

Crea `orden-<nombre>/SKILL.md` (el nombre de pila del usuario) con sus rutas reales, la lista «No tocar» y estas reglas:

1. Todo archivo nuevo va dentro de su proyecto. Nada suelto en la raíz ni en el Escritorio.
2. Proyecto nuevo: carpeta con nombre que se explique solo, su archivo de estado y su línea en el catálogo.
3. Al recibir material en `buzon/`: clasificar solo lo que el usuario encargue, conservar el original hasta comprobar la copia y anotar origen y destino.
4. Revisión cuando el usuario la pida: proyectos sin archivo de estado, archivos sueltos, entradas del catálogo que ya no existen, estados sin actualizar desde hace meses. Se entrega como lista de propuestas; el usuario decide.
5. Borrar exige siempre confirmación expresa.

## Fase 7 · Probar

Pide al usuario que abra una conversación nueva en la carpeta de trabajo y pregunte «¿qué proyectos tengo y en qué estado están?». Si el agente responde bien sin más explicación, la estructura funciona.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `orden-<nombre>/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/orden-<nombre>/`
- Codex: `~/.agents/skills/orden-<nombre>/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Guarda la skill en la carpeta de infraestructura que acabas de montar, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use (en Windows, cópiala y repite la copia tras cada cambio) y apúntala en `INSTALADO.md` como «propia».

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
- No leas ni muevas carpetas con datos clínicos reales, credenciales o copias de seguridad.
- Antes de mover o renombrar algo, enséñalo y espera el sí.
