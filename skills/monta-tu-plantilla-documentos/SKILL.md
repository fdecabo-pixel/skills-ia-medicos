---
name: monta-tu-plantilla-documentos
description: "Guía al usuario para montar su plantilla de documentos con su imagen (guías para pacientes, protocolos, apuntes, propuestas) y una skill propia que convierte un texto en PDF maquetado con control de calidad. Usar cuando diga «quiero que mis documentos salgan con mi logo y colores», «maqueta mis guías siempre igual», «monta una plantilla para mis PDF» o «hazme un sistema de documentos»."
---

# Monta tu plantilla de documentos

Construye un sistema sencillo: el usuario escribe o dicta el contenido y el agente entrega un PDF con su imagen, siempre igual y revisado.

## Antes de empezar

Mira si ya existe la skill resultante (`documento-<marca>/`) en la carpeta de skills del agente. Si existe, no repitas el montaje: úsala, o pregunta al usuario si quiere rehacerla.

## Fase 1 · Entrevista

De una en una:

1. ¿Qué documentos haces a menudo? (hojas para pacientes, protocolos del servicio, apuntes de clase, propuestas)
2. ¿Tienes logo? Pide el archivo. Si no tiene, se trabaja con el nombre en texto.
3. ¿Qué colores y qué tipo de letra usas? Si no lo sabe, pide un documento suyo que le guste y sácalos de ahí.
4. ¿Qué debe aparecer siempre? (pie con datos de contacto, aviso legal, fecha de revisión)
5. ¿Qué no debe aparecer nunca? Si responde con una categoría («marcas comerciales de fármacos», «otros centros»), pídele ejemplos y guarda una lista concreta, un término por línea, que irá al archivo `terminos-vetados.txt` de la plantilla.
6. ¿Tamaño y destino? (A4 para imprimir, lectura en móvil)
7. ¿Dónde guardas tus documentos? Si no lo sabe, propón una carpeta con el nombre de su marca dentro de su carpeta de documentos (`~/Documents/<marca>/` en Mac y Windows).

## Fase 2 · Montar el motor

El motor más simple es **HTML + CSS convertido a PDF con el navegador que ya tenga** (Chrome o Edge), manejado por un guion de Python. Si ya tiene `pandoc` o `weasyprint`, puedes usarlos en su lugar.

Crea la carpeta `plantilla-documentos/` dentro de la carpeta de la pregunta 7, con:

- Un entorno propio de Python con el paquete `markdown` (convierte el texto a HTML): `python3 -m venv .venv` y `.venv/bin/pip install markdown` (en Windows, `.venv\Scripts\pip`). No instales en el Python del sistema: en Mac y Linux actuales da error. Si no hay Python: en Mac, `xcode-select --install`; en Windows, `winget install Python.Python.3.12`.
- `plantilla.html` y `estilos.css` con su logo, colores, tipografía, portada, cabecera y pie. La cabecera y el pie se repiten en cada página con las cajas de margen de `@page` (`@top-left`, `@bottom-left`…), que necesitan Chrome o Edge actualizados.
- `terminos-vetados.txt`, con la lista de la pregunta 5.
- `generar.py`: recibe un archivo de texto en Markdown y devuelve el PDF. Tres cosas que debe hacer:
  - activar las extensiones `tables` y `admonition` de `markdown`; sin ellas las tablas y las cajas de aviso salen como texto;
  - llamar al navegador con `--headless=new --no-pdf-header-footer --print-to-pdf=<salida>` y una carpeta de perfil temporal propia (`--user-data-dir`). Sin `--no-pdf-header-footer`, cada página lleva impresas la fecha y la ruta interna del archivo;
  - no esperar a que el navegador se cierre solo, porque a veces no lo hace: lanzarlo con un límite de tiempo, esperar a que el PDF exista y deje de crecer, cerrar el proceso y borrar el perfil temporal.
- La fecha de revisión la da el usuario en cada documento; si falta, el guion se detiene y la pide. Nunca pone la de hoy por defecto.
- `ejemplo.md`: un documento de muestra con todos los elementos: títulos, listas, tabla, caja de aviso (`!!! aviso "Título"` y el texto con cuatro espacios de sangría) e imagen. Si no hay imagen, crea una figura sencilla de relleno.
- La forma de mirar las páginas, resuelta y probada: `pymupdf` en el mismo entorno (vale en Mac, Windows y Linux) o `pdftoppm` si ya está instalado.

Genera el ejemplo, mira las páginas y comprueba que cabecera y pie no pisan el texto antes de seguir.

## Fase 3 · Construir la skill

Crea `documento-<marca>/SKILL.md` en la ubicación indicada en «Dónde guardar la skill resultante», con:

1. Dónde está la plantilla y la orden exacta para generar el PDF, con rutas completas.
2. Cómo se escribe cada elemento (tabla, caja de aviso, imagen).
3. El procedimiento: recibir el contenido, pasarlo a Markdown, pedir la fecha de revisión, generar, **revisar** y abrir el PDF (`open` en Mac, `start` en Windows, `xdg-open` en Linux).
4. La **revisión obligatoria** antes de entregar, con sus órdenes exactas:
   - convertir las páginas a imagen y mirarlas una a una: ningún título al final de página, ninguna tabla o figura cortada;
   - extraer el texto del PDF final y trabajar sobre él, no sobre el Markdown;
   - buscar en ese texto cada término de `terminos-vetados.txt` y, además, leerlo entero buscando casos de la misma categoría que no estén en la lista; cada hallazgo nuevo se añade a la lista;
   - comprobar que aparece lo que debe aparecer siempre;
   - nombre de archivo que explique el contenido, sin espacios (por ejemplo `guia-cuidados-tras-amigdalectomia.pdf`).
5. Si el documento es para pacientes: lenguaje llano, sin siglas sin explicar y sin sustituir la indicación del médico.

## Fase 4 · Probar

Pide un documento real corto, genéralo, enséñale las páginas y ajusta la plantilla con sus comentarios. Cada ajuste se queda en la plantilla, no en el documento.

## Dónde guardar la skill resultante

Pregunta al usuario qué agente usa. La carpeta `documento-<marca>/` (nombre en minúsculas, sin tildes ni espacios) va en la carpeta de skills de ese agente:

- Claude Code: `~/.claude/skills/documento-<marca>/`
- Codex: `~/.agents/skills/documento-<marca>/`. En instalaciones anteriores puede ser `~/.codex/skills/`: si existen las dos o ninguna, usa `~/.agents/skills/`.

Si la carpeta de skills no existe, créala antes. Si el usuario tiene una carpeta de infraestructura (la monta la skill `ordena-tu-espacio-de-trabajo`), guarda allí la skill, en `infraestructura/skills-propias/`, enlázala desde la carpeta de skills de cada agente que use y apúntala en `INSTALADO.md`. Si no la tiene, guárdala en la carpeta de un agente y, si usa los dos, enlázala desde la del otro. En Windows, en lugar de enlazar, copia la carpeta y repite la copia tras cada cambio. La skill debe existir en un solo sitio: dos copias acaban siendo distintas.

El formato es el mismo en los dos agentes: un archivo `SKILL.md` con una cabecera (`name`, igual al nombre de la carpeta, y `description`) y, debajo, las instrucciones. Pregunta al usuario con qué frases lo pediría y escríbelas en la `description`, para que el agente active la skill sin que él tenga que recordar el nombre. Avísale de que la skill nueva estará disponible cuando abra una conversación nueva.

## Reglas que no se saltan

- **Ninguna contraseña, clave de API ni token dentro de la skill ni de sus archivos.** Si hace falta una clave, se guarda en un archivo aparte fuera de la carpeta de la skill (por ejemplo `~/.config/<servicio>/credenciales.txt`, con permisos solo para el usuario) y la skill cita únicamente la ruta.
- **Ningún dato identificativo de pacientes.** El agente funciona en la nube: lo que lee sale del ordenador.
- **Una pregunta cada vez y en lenguaje llano.** El usuario es profesional sanitario, no programador: explica cada término técnico la primera vez.
- **Enseña el resultado y pide validación** antes de darlo por bueno. Lo que el usuario corrija se incorpora a la skill.
- **No envíes, publiques ni borres nada.** Esta skill prepara; el usuario decide.
