---
name: crea-tu-estilo
description: "Guía al usuario para construir su propia skill de estilo de escritura a partir de sus correos y textos reales, de modo que el agente redacte correos y mensajes con su voz. Usar cuando diga «quiero que escribas como yo», «crea mi skill de estilo», «aprende cómo escribo mis correos» o «monta una skill que responda con mi tono»."
---

# Crea tu skill de estilo

Esta skill no escribe con el estilo de nadie: **construye la skill de estilo del usuario**. Al terminar, el usuario tendrá una skill propia (`estilo-<nombre>`) que el agente usará cada vez que redacte un correo o un mensaje en su nombre.

## Antes de empezar

Mira si ya existe la skill resultante (`estilo-<nombre>/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Qué necesitas del usuario

Una de estas dos fuentes:

1. **Acceso a sus correos enviados** mediante el conector de correo de su agente (Gmail u Outlook). Es la mejor fuente: son textos reales, no escritos para la ocasión. Si no ves herramientas de correo disponibles, es que no lo tiene: no lo instales por tu cuenta.
2. **Entre 15 y 20 textos suyos pegados o en una carpeta**: correos, mensajes largos.

**Antes de leer nada, pregunta si desde esa cuenta escribe a pacientes o sobre pacientes.** Si es así, no uses el conector. Usa la opción 2 y pídele, antes de aportar los textos, que elija los que no tengan datos clínicos o que borre él mismo nombres, apellidos, números de historia, teléfonos y fechas de nacimiento. No abras la carpeta hasta que confirme que lo ha hecho. Si aun así aparece un dato identificativo, o si al usar el conector aparece un correo clínico, no lo copies a ningún archivo, deja de leer, avísale y sigue solo con textos que él haya limpiado.

## Fase 1 · Entrevista breve

Pregunta, de una en una:

1. ¿A quién escribes más? (pacientes, compañeros, jefes, instituciones, industria, familia)
2. ¿Hay algo que nunca dirías? (fórmulas que te suenen falsas, tratamientos, palabras)
3. ¿Cómo firmas según a quién escribas?
4. ¿Qué te molesta de los textos que te escribe la IA?

## Fase 2 · Recoger el material

Con conector de correo:

- Busca los correos **enviados** de los últimos 12 meses por trimestres, para no saturar el contexto.
- Quédate con el destinatario, la fecha, el asunto y el arranque de cada mensaje (unos 200 caracteres). Basta para ver saludos, cierres y registro.
- Lee el texto completo solo de 10-15 correos representativos, repartidos entre los tipos de destinatario de la entrevista.
- No guardes los correos en bruto: trabaja con ellos en la conversación y guarda solo los fragmentos ya anonimizados.

Sin conector: usa los textos que el usuario aporte y pídele que indique a quién iba cada uno.

## Fase 3 · Analizar

Extrae, con recuentos y ejemplos literales:

- **Asunto** (si son correos): mayúsculas, longitud, fórmulas.
- **Aperturas**: cómo saluda según el destinatario.
- **Cierres y firma**.
- **Longitud y estructura**: frases cortas o largas, párrafos, listas.
- **Puntuación y tipografía**: comas, paréntesis, rayas, mayúsculas, emojis.
- **Fechas, horas y cifras**: cómo las escribe.
- **Conectores y muletillas reales**.
- **Registro por destinatario**: tú o usted, cercanía, humor.

## Fase 4 · Construir la skill

Crea la carpeta `estilo-<nombre>/` (el nombre de pila del usuario) en la ubicación indicada en «Dónde guardar la skill resultante», con tres archivos:

- `SKILL.md`:
  - cuándo activarse: correos y mensajes en primera persona dirigidos a una persona o institución concreta. No publicaciones, boletines ni guiones, que son cosa del manual de estilo si existe;
  - el procedimiento: leer `voz.md`, calibrar con `ejemplos.md`, identificar al destinatario, redactar, devolver para validar;
  - las **reglas duras** («nunca…»).
- `voz.md`: las costumbres observadas, numeradas por los apartados de la fase 3, cada una con un ejemplo.
- `ejemplos.md`: de 3 a 10 fragmentos reales por tipo de destinatario. Un fragmento es un saludo con su primer párrafo, un cierre completo o un correo corto entero. Si de un tipo hay menos de 3 textos, dilo en el archivo y no rellenes.

Dos cuidados al escribir las reglas:

- **Las reglas duras salen solo de lo que el usuario dijo en la entrevista o confirme expresamente.** Que algo no aparezca en 20 textos no lo convierte en prohibición: lo observado va a `voz.md` como costumbre («casi siempre», «no suele»). Antes de guardar, enséñale la lista de «nunca» y que tache las que no sean ciertas.
- **Todos los ejemplos van anonimizados**, en los tres archivos: nombres de pacientes, familiares y terceros sustituidos por `[Nombre]`; teléfonos, direcciones, correos y números de historia por `[teléfono]`, `[dirección]`, `[correo]`, `[n.º de historia]`.

Añade siempre al `SKILL.md` resultante estas tres reglas:

- «No inventes hechos, relaciones personales ni datos que no estén en el hilo o en lo que el usuario haya dicho.»
- «Devuelve siempre un borrador; no envíes nada.»
- «No copies datos identificativos de pacientes a los archivos de esta skill.»

## Fase 5 · Probar y afinar

1. Pide al usuario un correo real pendiente de responder, sin datos de pacientes, y redáctalo leyendo los tres archivos recién creados.
2. Pídele que lo corrija a mano, como lo enviaría.
3. Compara su versión con la tuya y convierte cada diferencia en una regla nueva de `voz.md`, en un apartado final «Correcciones del usuario».
4. Explícale que puede repetir este paso cuando quiera: «he cambiado esto, añádelo a mi estilo».

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `estilo-<nombre>/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/estilo-<nombre>/`
- Codex: `~/.agents/skills/estilo-<nombre>/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
