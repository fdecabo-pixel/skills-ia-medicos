---
name: verifica-citas
description: "Comprueba que las referencias bibliográficas de un texto existen de verdad y que sus datos son correctos, contrastándolas con CrossRef, DataCite y PubMed, y avisa de las retractadas. Usar cuando el usuario diga «verifica estas citas», «comprueba la bibliografía», «¿estas referencias son reales?», «revisa los DOI de mi manuscrito» o antes de entregar cualquier texto con referencias generado con IA."
---

# Verifica tus citas

Un modelo de lenguaje puede escribir una referencia con aspecto impecable que no existe, o mezclar el título de un artículo con el DOI de otro. Esta skill comprueba cada referencia contra tres registros públicos: **CrossRef** y **DataCite** (los registros oficiales de los DOI) y **PubMed**.

Funciona igual en Claude Code y en Codex. No necesita ninguna clave: usa las API públicas y gratuitas de esos servicios. Solo requiere Python 3. Si al ejecutar la orden el sistema dice que no lo encuentra, instálalo con el usuario antes de seguir (en Mac basta con aceptar el aviso de instalación que aparece; en Windows, desde python.org o la tienda de Microsoft).

## Procedimiento

1. **Reunir las referencias.** Extrae la bibliografía del documento que indique el usuario y escríbela en un archivo de texto, **una referencia por línea**, tal como aparece, con su DOI o su PMID si los lleva.
   - Si no puedes abrir el documento (Word, PDF), pide al usuario que pegue la bibliografía o la guarde como texto.
   - No corrijas nada: se comprueba lo que hay. Lo único que se retoca es unir en una sola línea la referencia que haya quedado partida al copiarla de un PDF.
   - Comprueba que el número de líneas coincide con el número de referencias.

2. **Ejecutar el verificador**, que está en la carpeta `scripts/` de esta skill:

   ```
   python3 <carpeta de esta skill>/scripts/verificar_citas.py referencias.txt --salida informe-citas.md
   ```

   - En Windows la orden puede ser `python` o `py` en lugar de `python3`.
   - Tarda de 3 a 4 segundos por referencia. Con más de 25, lánzalo en segundo plano o con un límite de tiempo de 10 minutos. El informe se va guardando tras cada referencia, así que si el proceso se corta queda lo hecho.
   - Si el usuario quiere, añade `--correo su@correo.es`. CrossRef y PubMed piden identificarse y a cambio dan más margen; es opcional y no es una clave.

3. **Leer el informe.** Cada referencia recibe uno de cuatro veredictos:

   | Veredicto | Qué significa | Qué hacer |
   |---|---|---|
   | 🚫 Retractada | El artículo existe pero ha sido retirado | No citarlo como evidencia; avisar al usuario |
   | ❌ No localizada | No aparece en ningún registro, o lo único parecido es otro artículo | No darla por buena ni por inventada: hay que buscarla a mano (PubMed, la revista) antes de decidir. No sustituirla por el artículo parecido |
   | ⚠️ Dudosa | Se ha encontrado un artículo que coincide solo en parte: falla el título, el primer autor, el año, la revista, el DOI o el PMID | Puede ser el mismo artículo con datos mal copiados u otro distinto. Enseñar la diferencia y que decida el usuario |
   | ✅ Verificada | Existe y título, primer autor, año y revista coinciden con el registro oficial | Nada |

4. **Presentar el resultado** al usuario empezando por los problemas: primero las retractadas, luego las no localizadas, luego las dudosas. Para cada una, la referencia original, lo que dice el registro oficial y la corrección propuesta.

5. **Corregir solo con permiso.** Propón la bibliografía corregida con los datos oficiales (título, revista, año, DOI). No sustituyas una referencia no localizada por otra «parecida»: eso lo decide el usuario.

## Límites que hay que explicar al usuario

- **Comprueba que el artículo existe y que sus datos coinciden. No comprueba que el artículo diga lo que el texto le atribuye.** Eso exige leer el artículo: ofrécelo como paso siguiente para las afirmaciones importantes.
- No comprueba volumen, número ni páginas.
- «No localizada» no significa «inventada». Libros, capítulos, tesis, páginas web, comunicaciones a congresos, artículos antiguos sin DOI y revistas no indexadas pueden no estar en estos registros.
- Una referencia que solo trae el DOI o el PMID se da por verificada si el identificador existe; el informe lo advierte para que el usuario confirme que es el artículo que quería.
- Si los autores del registro oficial son un grupo (un consorcio, un comité), los autores citados no se pueden confirmar y la referencia sale como dudosa.
- Detecta retractaciones, retiradas y expresiones de preocupación del editor que consten en CrossRef o en PubMed; una retractación muy reciente puede no figurar todavía.
- Si hay un fallo de conexión, la referencia queda como dudosa con el aviso correspondiente: repetir más tarde.

## Reglas que no se saltan

- Nunca des por buena una referencia sin haberla pasado por el verificador o haberla abierto en su fuente.
- Nunca inventes un DOI, un PMID ni un dato bibliográfico para «arreglar» una referencia.
- No hacen falta contraseñas ni claves; no pidas ninguna.
