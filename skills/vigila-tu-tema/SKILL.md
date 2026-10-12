---
name: vigila-tu-tema
description: "Guía al usuario para montar su vigilancia bibliográfica periódica con una skill propia que cada mes busca lo publicado sobre su tema en PubMed (y otras fuentes que tenga conectadas), lo verifica y le entrega un resumen fiable para revisar. Usar cuando diga «quiero estar al día de mi tema», «avísame de lo nuevo que se publique sobre…», «monta una alerta bibliográfica» o «revisión mensual de novedades»."
---

# Vigila tu tema cada mes

Construye la skill de vigilancia del usuario: mismo tema, misma búsqueda, cada mes, con cada referencia comprobada.

## Antes de empezar

Mira si ya existe la skill resultante (`novedades-<tema>/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Qué necesita

- El **conector de PubMed**, si su agente lo tiene. Si no, la búsqueda se hace con la API pública de PubMed (E-utilities), que no necesita clave ni instalar nada.
- Opcional: Consensus, Elicit o Semantic Scholar si ya los usa. No instales nada que no tenga.

## Fase 1 · Entrevista

De una en una:

1. ¿Qué tema quieres vigilar? Pide que lo acote: enfermedad, intervención o fármacos, población.
2. ¿Qué te interesa y qué no? (ensayos, vida real, guías, seguridad; excluir estudios en animales, pediatría, casos aislados)
3. ¿Cada cuánto? (mensual por defecto)
4. ¿Qué quieres recibir? (texto con enlaces, borrador de correo, resumen para una sesión clínica)
5. ¿Hay revistas o grupos que no quieras perderte?

## Fase 2 · Diseñar y validar la búsqueda

1. Traduce el tema a una estrategia de PubMed y enséñasela. **Todo concepto debe ir también en texto libre (`[tiab]`), no solo como descriptor MeSH**: los artículos recién publicados aún no tienen descriptores y una búsqueda solo por MeSH los pierde.
2. Ejecútala para los últimos 3 meses por fecha de entrada en PubMed. Si salen demasiados resultados irrelevantes o faltan artículos que el usuario conoce, ajústala con él.
3. Deja escrita la estrategia final: será siempre la misma, para que los meses sean comparables.

## Fase 3 · Construir la skill

Crea `novedades-<tema>/SKILL.md` en la ubicación indicada en «Dónde guardar la skill resultante», con:

1. **Alcance fijado**: tema, inclusiones y exclusiones. No se vuelve a preguntar.
2. **Ventana**: por fecha de entrada en PubMed (`[edat]`). La primera vez, los últimos 30 días. Después, desde 7 días antes de la última ejecución; los solapes los resuelve el registro.
3. **Registro**: un archivo `revisados.tsv` en la carpeta de la skill, con una línea por PMID revisado (o por DOI, si no tiene PMID), con su fecha y su estado (entregado o descartado), y la fecha de la última ejecución. Ningún PMID del registro se vuelve a presentar.
4. **Búsqueda**: la estrategia validada, en PubMed y en las demás fuentes conectadas. Si no hay conector de PubMed, escribe en la skill las dos llamadas a la API pública:
   - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=500&datetype=edat&mindate=AAAA/MM/DD&maxdate=AAAA/MM/DD&term=<estrategia>` para obtener los PMID;
   - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=<PMID>` para título, autores, DOI, tipo de publicación y resumen;
   - como máximo 3 peticiones por segundo.
5. **Quitar duplicados** por DOI y, si no hay, por título.
6. **Verificar** cada artículo que vaya a aparecer: que existe, que el DOI lleva a ese artículo y que no está retractado. Con la skill `verifica-citas` si está instalada (búscala en la carpeta de skills del agente). Si no, comprueba que `https://api.crossref.org/works/<DOI>` devuelve el mismo título y que el tipo de publicación en PubMed no es «Retracted Publication».
7. **Filtrar** leyendo título y resumen: aplicar aquí las exclusiones (los descriptores no bastan en artículos recientes) y quedarse con lo que es novedad de verdad: resultado nuevo, dato de vida real, actualización de guía, señal de seguridad.
8. **Redactar** agrupando por subtema, con un apartado para revisiones sistemáticas y metaanálisis. Por artículo: título, autores, revista y año, una o dos frases con el hallazgo, enlace a PubMed y DOI. Si PubMed no trae resumen, no redactes hallazgo: indica «sin resumen disponible» y deja los enlaces.
9. **Entregar** en el formato elegido, guardado en una subcarpeta `entregas/`, siempre como material para revisar.

Reglas que deben figurar en la skill:

- Ninguna referencia que no se haya verificado.
- No afirmar más de lo que el estudio sostiene; indicar diseño y tamaño de muestra cuando limiten la conclusión.
- Si en un subtema no hay novedades, decirlo de forma expresa.
- Nunca envía ni publica: solo deja el material.

## Fase 4 · Probar y programar

Ejecuta la primera vigilancia y revísala con el usuario.

Si quiere que salte sola, hay dos opciones:

- **En su ordenador (recomendada, porque lee el registro)**: una tarea programada mensual que ejecute el agente sin ventana. En Claude Code, `claude -p "ejecuta la skill novedades-<tema>"`; en Codex, `codex exec "ejecuta la skill novedades-<tema>"`. Se programa con las tareas del sistema: launchd en Mac, cron en Linux, el Programador de tareas en Windows. Solo salta con el ordenador encendido. Sin ventana el agente no puede pedir permiso: deja autorizado de antemano solo lo que necesita (leer y escribir en la carpeta de la skill y consultar eutils.ncbi.nlm.nih.gov y api.crossref.org) y no uses la opción que salta todos los permisos. Prueba la orden a mano antes de programarla.
- **Rutina en la nube del agente**: solo si la carpeta de la skill y su registro están en un sitio que esa rutina pueda leer y escribir; si no, repetirá artículos.

En los dos casos el resultado se guarda en `entregas/` y no se envía a nadie.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `novedades-<tema>/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/novedades-<tema>/`
- Codex: `~/.agents/skills/novedades-<tema>/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
