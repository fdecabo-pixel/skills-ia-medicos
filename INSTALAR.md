# Instrucciones de instalación para el agente

**Qué es este archivo.** Las instrucciones que sigue el agente (Claude Code o Codex) cuando el usuario le pide instalar una skill de este repositorio. Si eres una persona, la explicación está en el [README](README.md).

**Para qué sirve.** Para que el usuario no tenga que copiar carpetas a mano: le da la dirección del repositorio a su agente y este hace el resto.

**Por qué es importante.** Una skill son instrucciones que el agente va a ejecutar. Instalarla siguiendo siempre los mismos pasos (un solo sitio, leerla antes, apuntar lo instalado) evita copias duplicadas, herramientas perdidas y skills que nadie ha leído.

## Qué hacer

1. **Averigua qué agente eres y cuál es su carpeta de skills.**
   - Claude Code: `~/.claude/skills/`
   - Codex: `~/.agents/skills/`. En instalaciones anteriores puede ser `~/.codex/skills/`; si existen las dos, usa `~/.agents/skills/`.
   - Si la carpeta no existe, créala (`mkdir -p ~/.claude/skills`).

2. **Decide dónde guardar el repositorio.**
   - Si el usuario tiene una carpeta de infraestructura (por ejemplo `…/00-sistema/infraestructura/`), clónalo allí: `…/infraestructura/skills-ia-medicos/`.
   - Si no la tiene, pregúntale dónde lo quiere. Si no lo sabe, propón `~/infraestructura-ia/skills-ia-medicos/` y ofrécele montar su estructura con la skill `ordena-tu-espacio-de-trabajo`, que después moverá esa carpeta a su sitio.
   - Si el repositorio ya está clonado, actualízalo con `git pull` en lugar de clonarlo otra vez.
   - Si no hay `git`, descarga el ZIP de la rama principal y descomprímelo en esa carpeta.

3. **Antes de enlazar nada, lee el `SKILL.md` de la skill pedida** (y sus guiones, si los tiene) y dile al usuario en dos líneas qué hace y qué necesita.

4. **Enlaza la skill en la carpeta de skills del agente.**
   - Mac y Linux: enlace simbólico con la ruta completa del origen, por ejemplo `ln -s /ruta/completa/infraestructura/skills-ia-medicos/skills/<skill> ~/.claude/skills/<skill>`. Comprueba que el enlace resuelve.
   - Windows: copia la carpeta de la skill. Tras cada actualización del repositorio hay que volver a copiarla.
   - Si ya existe una skill con ese nombre, no la sobrescribas: pregunta.
   - Si el usuario usa los dos agentes, enlázala en los dos.

5. **Apúntalo** en el registro de herramientas del usuario si tiene uno (`INSTALADO.md` en su carpeta de infraestructura): una línea por skill con su nombre, la dirección del repositorio, la fecha y para qué sirve.

6. **Dile cómo usarla**: debe abrir una conversación nueva y pedirla con sus palabras. Dale una frase de ejemplo tomada de la `description` de la skill.

## Qué no hacer

- No instales todas las skills si solo ha pedido una.
- No pidas ni guardes contraseñas ni claves: ninguna skill de este repositorio las necesita para instalarse.
- Durante la instalación no cambies la configuración global del agente.
