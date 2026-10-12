---
name: monta-tu-manual-de-estilo
description: "Guía al usuario para montar su propio manual de estilo para lo que publica (redes, boletín, vídeo, web), con estructuras por canal, palabras vetadas y reglas contra el tono de IA. Usar cuando diga «quiero un manual de estilo», «que mis publicaciones no suenen a IA», «define cómo escribimos en mi marca» o «monta las reglas de redacción de mi consulta o servicio»."
---

# Monta tu manual de estilo

La skill de estilo personal sirve para correos. Esta construye otra cosa: **el manual de lo que el usuario publica** (redes, boletín, guiones, web), para que cualquier texto salga con la misma voz y con una estructura pensada para cada canal.

## Antes de empezar

Mira si ya existe la skill resultante (`manual-de-estilo-<marca>/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Fase 1 · Entrevista

De una en una:

1. ¿En nombre de quién se publica? (tú, tu consulta, tu servicio, una sociedad)
2. ¿Para quién escribes? Describe a una persona concreta.
3. ¿En qué canales publicas y con qué frecuencia?
4. ¿Qué quieres que haga el lector al terminar de leer, en cada canal?
5. ¿Qué te gusta de cómo escriben otras cuentas o autores? Si no recuerda nombres, basta con qué le gusta. Va a `voz.md`.
6. ¿Qué palabras, promesas o tonos quedan prohibidos? (por ejemplo, superlativos, alarmismo, promesas de curación)
7. ¿Qué límites clínicos y legales hay que respetar? Pregunta expresamente por estos tres: no diagnosticar, no citar fármacos por su marca y normas de publicidad sanitaria.

## Fase 2 · Material

Pide publicaciones propias que le parezcan buenas, al menos 3 por canal, y, si las tiene, 2 o 3 que no le gusten. Si de un canal hay menos de 3, dilo y marca sus reglas como provisionales.

## Fase 3 · Construir el manual

Crea la carpeta `manual-de-estilo-<marca>/` en la ubicación indicada en «Dónde guardar la skill resultante», con:

- `SKILL.md`: cuándo activarse (antes de redactar cualquier texto que se publique en nombre de esa marca) y el orden de trabajo: leer `voz.md`, elegir canal, elegir estructura en `estructuras.md`, redactar, pasar `control.md`.
- `voz.md`: quién habla, a quién, registro, y la lista de palabras y fórmulas vetadas.
- `estructuras.md`: una o dos estructuras por canal, cada una con su esqueleto y un ejemplo.
- `control.md`: la lista de comprobación final.

**Las estructuras salen primero de su material.** De las publicaciones buenas de cada canal saca el esqueleto real: bloques, orden, rótulos que se repiten, número de pasos, etiquetas, llamada final. Enséñaselo y que lo confirme. Solo si un canal no tiene material, propón estructuras conocidas (problema, agitación, solución; antes, después, puente; caso, enseñanza, acción) y deja las que elija. Lo que tienen en común las buenas va a `estructuras.md` y a `voz.md`; lo que hay que evitar de las malas, a la lista de vetadas y a `control.md`.

La lista de control incluye siempre:

- Ninguna palabra ni fórmula de la lista de vetadas de `voz.md`.
- Ninguna afirmación clínica va más allá de lo que sostiene la evidencia: marca cada afirmación clínica del texto y pide al usuario que la confirme o dé la fuente. No la des por buena tú.
- Sin rasgos típicos de texto de IA (tríadas de adjetivos, rayas largas, «no es X, es Y» como adorno, adjetivos huecos, cierres grandilocuentes), salvo los que el usuario use de verdad en sus publicaciones buenas: esos se anotan como excepción.
- Términos médicos en castellano correcto, sin anglicismos innecesarios.
- Una sola llamada a la acción por texto, la que el usuario definió para ese canal.
- Los límites clínicos y legales de la entrevista.

## Fase 4 · Probar

Redacta una publicación real para el canal que más use, leyendo los cuatro archivos. Pídele que la corrija y convierte cada corrección en una línea del manual. Indícale que el manual se mantiene vivo: cada vez que rechace un texto, la razón se añade.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `manual-de-estilo-<marca>/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/manual-de-estilo-<marca>/`
- Codex: `~/.agents/skills/manual-de-estilo-<marca>/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
