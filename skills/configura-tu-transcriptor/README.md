# Configura tu transcriptor

> De una nota de voz, una reunión o una clase a texto, acta o apuntes.

## Qué es

Una skill configurable. Instala en tu ordenador un programa de transcripción (Whisper) y te deja una skill propia que convierte tus audios en el documento que suelas necesitar.

## Para qué sirve

- Pasar a texto notas de voz y dictados.
- Sacar el acta de una reunión con acuerdos y pendientes.
- Convertir una clase grabada en apuntes.

## Por qué es importante

Los servicios de transcripción en línea suben tu audio a servidores ajenos. En una nota de voz de un médico se cuela información de pacientes con facilidad. Aquí el audio se transcribe dentro de tu ordenador y no se sube a ningún sitio.

## Qué necesitas

- Claude Code o Codex.
- Un ordenador razonablemente moderno; la primera vez se descarga un modelo de hasta 1,5 GB.
- Unos 20 minutos de instalación.

## Cómo se usa

Una vez instalada, abre una conversación nueva con tu agente y pídelo con tus palabras. Por ejemplo:

- «Monta un transcriptor.»
- «Pasa a texto esta nota de voz.»

## Qué te deja

El transcriptor instalado, tu vocabulario habitual (fármacos, nombres, siglas) y una skill `transcribir`.

## Límites y garantías

- **El audio no sale de tu ordenador, pero el texto que el agente lea sí viaja a la nube.** Si un audio contiene datos de pacientes, la skill lo transcribe a un archivo sin leerlo y eres tú quien lo anonimiza antes de pedir un acta o un resumen.
- No inventa lo que no se entiende: lo marca como dudoso.

---

Instalación: ver la [portada del repositorio](../../README.md#cómo-se-instala-una-skill). Las instrucciones que sigue el agente están en [`SKILL.md`](SKILL.md).
