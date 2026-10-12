# Verifica tus citas

> Comprueba que las referencias de un texto existen y que sus datos son correctos.

## Qué es

Un verificador de bibliografía. Le das una lista de referencias y las contrasta, una a una, con los registros oficiales: CrossRef y DataCite (donde se registran los DOI) y PubMed.

## Para qué sirve

- Revisar la bibliografía de un manuscrito, un trabajo de fin de grado, una sesión clínica o una guía antes de entregarla.
- Comprobar las referencias que te ha dado una IA.
- Saber si alguno de los artículos que citas ha sido retractado.

## Por qué es importante

Una IA puede escribir una referencia perfecta en apariencia que no existe, o pegar el título de un artículo con el DOI de otro. Publicar o presentar una cita así es un error serio y fácil de evitar. Comprobarlas a mano lleva varios minutos por referencia; aquí son tres o cuatro segundos por referencia (unos tres minutos para 50).

## Qué necesitas

- Claude Code o Codex.
- Conexión a internet y Python 3, un programa gratuito que el agente usa por debajo (si falta, te ayuda a instalarlo).
- Ninguna clave ni cuenta.

## Cómo se usa

Una vez instalada, abre una conversación nueva con tu agente y pídelo con tus palabras. Por ejemplo:

- «Verifica las citas de este documento.»
- «¿Estas referencias son reales?»
- «Revisa los DOI de mi manuscrito.»

## Qué te deja

Un informe con cada referencia clasificada: ✅ verificada, ⚠️ dudosa (con la diferencia concreta: título, primer autor, año, revista, DOI o PMID), ❌ no localizada o 🚫 retractada. Y, si quieres, la bibliografía corregida con los datos oficiales.

## Límites y garantías

- Comprueba que el artículo existe y que sus datos coinciden. **No comprueba que diga lo que tú le atribuyes**: eso exige leerlo.
- «No localizada» no significa «inventada»: libros, capítulos, páginas web y revistas no indexadas no suelen estar en estos registros.
- No comprueba volumen ni páginas.

---

Instalación: ver la [portada del repositorio](../../README.md#cómo-se-instala-una-skill). Las instrucciones que sigue el agente están en [`SKILL.md`](SKILL.md).
