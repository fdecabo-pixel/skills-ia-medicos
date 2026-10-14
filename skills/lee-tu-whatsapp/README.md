# Lee tu WhatsApp

> Tu agente resume chats, busca mensajes y descarga audios de tu WhatsApp para Mac, sin enviar nada.

## Qué es

Una skill con un pequeño programa que lee la copia de tus chats que la app de WhatsApp para Mac guarda en tu ordenador. No se conecta a WhatsApp ni usa conectores no oficiales: solo lee lo que ya está en tu Mac.

## Para qué sirve

- Saber qué tienes sin leer y resumir un grupo con mucho movimiento.
- Encontrar un dato que alguien te mandó por WhatsApp hace semanas (una fecha, una dirección, un documento).
- Descargar los audios de un chat para pasarlos a texto.
- Dejar una respuesta redactada en el chat para que tú la revises y la envíes.

## Por qué es importante

Buena parte de la coordinación del día a día (congresos, grupos de trabajo, cursos, el servicio) pasa por WhatsApp, y la información se pierde entre cientos de mensajes. Con esta skill tu agente puede buscar ahí como busca en tus archivos. Lo hace sin conectarse a tu cuenta, que es lo que hacen los conectores no oficiales y lo que puede provocar que WhatsApp la bloquee.

## Qué necesitas

- Un Mac con la app de WhatsApp para Mac vinculada a tu móvil (no sirve WhatsApp Web ni Windows; con WhatsApp Business no está probada).
- Claude Code o Codex.
- Python 3. Si no lo tienes, el Mac ofrece instalarlo la primera vez: basta con aceptar.
- Dar a tu terminal o editor el permiso «Acceso total al disco» (la skill te explica cómo y cómo retirarlo).
- Ninguna clave ni cuenta.

## Cómo se usa

Una vez instalada, abre una conversación nueva con tu agente y pídelo con tus palabras. Por ejemplo:

- «¿Tengo WhatsApps sin leer?»
- «Resúmeme lo que se ha hablado esta semana en el grupo del congreso.»
- «Busca en WhatsApp la dirección que me mandó Marta.»
- «Descarga el audio que me mandó Luis ayer.»

## Qué te deja

Resúmenes y búsquedas en la conversación, los audios y adjuntos en tu carpeta de Descargas y, si lo pides, la respuesta escrita en el chat a falta de que pulses Enviar.

## Límites y garantías

- **Nunca envía**: el botón Enviar lo pulsas siempre tú.
- **Lo que lee el agente sale de tu ordenador** hacia el proveedor de la IA. No la uses con chats de pacientes: el agente no siempre puede saber que un chat lo es. Si aparecen datos clínicos, para y te avisa.
- Solo ve lo que WhatsApp para Mac ya ha descargado: los audios antiguos hay que abrirlos antes en la app.
- La copia se actualiza solo mientras WhatsApp para Mac está abierta.

---

Instalación: ver la [portada del repositorio](../../README.md#cómo-se-instala-una-skill). Las instrucciones que sigue el agente están en [`SKILL.md`](SKILL.md).
