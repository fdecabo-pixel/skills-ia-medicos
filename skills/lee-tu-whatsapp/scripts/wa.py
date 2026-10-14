#!/usr/bin/python3
"""Lector de WhatsApp para Mac (solo lectura) y borradores de mensaje.

Lee la copia local de los chats que guarda la app de WhatsApp de escritorio.
No escribe nunca en ella ni se conecta a WhatsApp. «enviar» solo abre un
borrador en la app: el envío lo hace siempre el usuario pulsando «Enviar».

Uso:
  wa.py chats [--buscar TEXTO] [--sin-leer] [--limite N]
  wa.py leer CHAT [--dias N | --desde AAAA-MM-DD --hasta AAAA-MM-DD] [--limite N]
  wa.py buscar TEXTO [--chat CHAT] [--dias N] [--limite N]
  wa.py descargar [CHAT] [--tipo audio|imagen|video|documento|todo] [--dias N] [--destino CARPETA]
  wa.py enviar CHAT "texto"

CHAT = parte del nombre (da igual tildes y mayúsculas), parte del teléfono o #número de chat.
"""
import argparse
import datetime as dt
import re
import shutil
import sqlite3
import subprocess
import sys
import unicodedata
import urllib.parse
from pathlib import Path

WA = Path.home() / "Library/Group Containers/group.net.whatsapp.WhatsApp.shared"
MEDIA = WA / "Message"
EPOCA_APPLE = 978307200  # WhatsApp cuenta los segundos desde el 1-1-2001

# Tipos de mensaje identificados en la base de datos; el resto sale como «otro contenido»
TIPOS = {1: "imagen", 2: "vídeo", 3: "audio", 4: "contacto", 5: "ubicación",
         8: "documento", 11: "gif", 15: "sticker"}
TIPOS_DESCARGA = {"audio": (3,), "imagen": (1,), "video": (2, 11), "documento": (8,),
                  "todo": (1, 2, 3, 8, 11)}
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# 0 = individual, 1 = grupo, 4 = grupo de comunidad (fuera: estados, difusión y canales).
# La fecha sale de los mensajes: a los chats fijados WhatsApp les suma miles de años en
# ZLASTMESSAGEDATE para ordenarlos arriba, así que ese campo solo sirve para saber si lo están.
SQL_CHATS = """
SELECT s.Z_PK AS pk, s.ZPARTNERNAME AS nombre, s.ZCONTACTJID AS jid, s.ZSESSIONTYPE AS tipo,
       u.ultimo, s.ZUNREADCOUNT AS sin_leer, s.ZARCHIVED AS archivado,
       s.ZLASTMESSAGEDATE > strftime('%s', 'now') - 978307200 + 31536000 AS fijado
FROM ZWACHATSESSION s
LEFT JOIN (SELECT ZCHATSESSION, MAX(ZMESSAGEDATE) AS ultimo FROM ZWAMESSAGE GROUP BY ZCHATSESSION) u
       ON u.ZCHATSESSION = s.Z_PK
WHERE s.ZSESSIONTYPE IN (0, 1, 4){quitados}
ORDER BY u.ultimo IS NULL, u.ultimo DESC"""

SQL_MENSAJES = """
SELECT m.ZMESSAGEDATE AS fecha, m.ZISFROMME AS yo, m.ZTEXT AS texto, m.ZMESSAGETYPE AS tipo,
       g.ZCONTACTNAME AS autor, s.ZPARTNERNAME AS chat, s.ZSESSIONTYPE AS tipo_chat,
       mi.ZMEDIALOCALPATH AS ruta, mi.ZMOVIEDURATION AS duracion, mi.ZTITLE AS titulo
FROM ZWAMESSAGE m
JOIN ZWACHATSESSION s ON s.Z_PK = m.ZCHATSESSION
LEFT JOIN ZWAGROUPMEMBER g ON g.Z_PK = m.ZGROUPMEMBER
LEFT JOIN ZWAMEDIAITEM mi ON mi.Z_PK = m.ZMEDIAITEM
WHERE s.ZSESSIONTYPE IN (0, 1, 4) AND m.ZMESSAGEDATE IS NOT NULL{duplicados}{filtros}
ORDER BY m.ZMESSAGEDATE DESC
LIMIT ?"""

# La copia guarda a veces el mismo mensaje dos veces (mismo ZSTANZAID en el mismo chat);
# se queda uno solo, preferiblemente el que tiene el adjunto ya descargado. El «+» delante de
# d.ZCHATSESSION obliga a buscar por el índice de ZSTANZAID: por chat, la consulta pasa de
# 0,01 s a 10 s. Si una versión de WhatsApp no tiene ese índice, se quita el «+».
SQL_DUPLICADOS = """
  AND NOT EXISTS (
      SELECT 1 FROM ZWAMESSAGE d LEFT JOIN ZWAMEDIAITEM di ON di.Z_PK = d.ZMEDIAITEM
      WHERE d.ZSTANZAID = m.ZSTANZAID AND {mas}d.ZCHATSESSION = m.ZCHATSESSION AND d.Z_PK <> m.Z_PK
        AND ((di.ZMEDIALOCALPATH IS NOT NULL) > (mi.ZMEDIALOCALPATH IS NOT NULL)
             OR ((di.ZMEDIALOCALPATH IS NOT NULL) = (mi.ZMEDIALOCALPATH IS NOT NULL)
                 AND d.Z_PK < m.Z_PK)))"""
ESQUEMA = {}  # columnas e índices de esta versión de WhatsApp; lo rellena abrir()


def salir(mensaje, codigo=1):
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


def normalizar(texto):
    """Minúsculas y sin tildes, para buscar sin que importe cómo se escribió."""
    if not texto:
        return ""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def kebab(texto, maximo=40):
    return re.sub(r"[^a-z0-9]+", "-", normalizar(texto))[:maximo].strip("-") or "sin-nombre"


def abrir(nombre):
    """Abre una base de datos de WhatsApp en modo solo lectura."""
    try:
        con = sqlite3.connect((WA / nombre).as_uri() + "?mode=ro", uri=True)
        con.execute("SELECT 1 FROM sqlite_master LIMIT 1")
    except sqlite3.OperationalError as e:
        salir(f"No puedo abrir {nombre} ({e}). ¿Está instalada WhatsApp para Mac y tiene esta "
              "aplicación «Acceso total al disco» (Ajustes del Sistema > Privacidad y seguridad)?")
    con.row_factory = sqlite3.Row
    con.create_function("norm", 1, normalizar, deterministic=True)
    if nombre == "ChatStorage.sqlite" and not ESQUEMA:
        columnas = lambda t: {f[1] for f in con.execute(f"PRAGMA table_info({t})")}
        ESQUEMA["removed"] = "ZREMOVED" in columnas("ZWACHATSESSION")
        ESQUEMA["stanza"] = "ZSTANZAID" in columnas("ZWAMESSAGE")
        ESQUEMA["indice"] = any(
            [f[2] for f in con.execute(f"PRAGMA index_info('{i[1]}')")][:1] == ["ZSTANZAID"]
            for i in con.execute("PRAGMA index_list('ZWAMESSAGE')"))
    return con


def sql_chats():
    return SQL_CHATS.format(quitados=" AND COALESCE(s.ZREMOVED, 0) = 0" if ESQUEMA.get("removed") else "")


def mapa_lid():
    """Contactos que WhatsApp guarda con identificador oculto (@lid) → su teléfono.

    Si falta LID.sqlite (otras versiones de WhatsApp), devuelve {} y esos contactos quedan sin teléfono."""
    if not (WA / "LID.sqlite").exists():
        return {}
    try:
        filas = abrir("LID.sqlite").execute(
            "SELECT ZIDENTIFIER, ZPHONENUMBER FROM ZWAZACCOUNT WHERE ZPHONENUMBER IS NOT NULL").fetchall()
    except sqlite3.OperationalError:
        return {}
    return {jid: re.sub(r"\D", "", tel) for jid, tel in filas}


def numero(jid, lid):
    usuario, _, dominio = (jid or "").partition("@")
    if dominio == "s.whatsapp.net":
        return usuario
    return lid.get(jid) if dominio == "lid" else None


def a_fecha(ts):
    return dt.datetime.fromtimestamp(ts + EPOCA_APPLE)


def a_ts(fecha):
    try:
        return dt.datetime.strptime(fecha, "%Y-%m-%d").timestamp() - EPOCA_APPLE
    except ValueError:
        salir(f"Fecha no válida: {fecha} (formato AAAA-MM-DD)")


def rango(a):
    """--dias N = hoy y los N-1 días anteriores; --desde/--hasta mandan si se indican."""
    desde = hasta = None
    if a.dias is not None and a.dias < 1:
        salir("--dias tiene que ser 1 o más (1 = solo hoy)")
    if a.dias:
        hoy = dt.datetime.combine(dt.date.today(), dt.time())
        desde = (hoy - dt.timedelta(days=a.dias - 1)).timestamp() - EPOCA_APPLE
    if a.desde:
        desde = a_ts(a.desde)
    if a.hasta:
        hasta = a_ts(a.hasta) + 86400  # incluye el día entero
    return desde, hasta


def describir(c):
    partes = [f"#{c['pk']} {c['nombre'] or c['jid']}", "grupo" if c["tipo"] else "individual"]
    if c["ultimo"]:
        partes.append(f"último {a_fecha(c['ultimo']):%d-%m-%Y %H:%M}")
    pendientes = c["sin_leer"] or 0
    if pendientes > 0:
        partes.append(f"{pendientes} sin leer")
    elif pendientes < 0:
        partes.append("marcado como no leído")
    if c["fijado"]:
        partes.append("fijado")
    if c["archivado"]:
        partes.append("archivado")
    return " · ".join(partes)


def elegir_chat(con, consulta):
    chats = con.execute(sql_chats()).fetchall()
    if consulta.startswith("#") and consulta[1:].isdigit():
        encontrados = [c for c in chats if c["pk"] == int(consulta[1:])]
    else:
        q = normalizar(consulta).strip()
        encontrados = [c for c in chats if normalizar(c["nombre"]) == q]
        if not encontrados:
            digitos = re.sub(r"\D", "", consulta)
            lid = mapa_lid() if len(digitos) >= 6 else {}
            encontrados = [c for c in chats
                           if (q and q in normalizar(c["nombre"]))
                           or (len(digitos) >= 6 and digitos in (numero(c["jid"], lid) or ""))]
    if not encontrados:
        salir(f"No hay ningún chat que coincida con «{consulta}». Prueba: wa.py chats --buscar …")
    if len(encontrados) > 1:
        print(f"«{consulta}» coincide con {len(encontrados)} chats; repite con el #número del que quieras:")
        for c in encontrados[:25]:
            print("  " + describir(c))
        sys.exit(3)
    return encontrados[0]


def mensajes(con, chat=None, desde=None, hasta=None, tipos=None, texto=None, limite=100):
    filtros, params = [], []
    if chat:
        filtros.append("m.ZCHATSESSION = ?")
        params.append(chat["pk"])
    if desde is not None:
        filtros.append("m.ZMESSAGEDATE >= ?")
        params.append(desde)
    if hasta is not None:
        filtros.append("m.ZMESSAGEDATE < ?")
        params.append(hasta)
    if tipos:
        filtros.append(f"m.ZMESSAGETYPE IN ({','.join('?' * len(tipos))})")
        params.extend(tipos)
    if texto:
        filtros.append("(norm(m.ZTEXT) LIKE ? OR norm(mi.ZTITLE) LIKE ?)")
        params += [f"%{normalizar(texto)}%"] * 2
    duplicados = SQL_DUPLICADOS.format(mas="+" if ESQUEMA.get("indice") else "") if ESQUEMA.get("stanza") else ""
    sql = SQL_MENSAJES.format(duplicados=duplicados, filtros="".join(f" AND {f}" for f in filtros))
    return con.execute(sql, params + [limite]).fetchall()[::-1]  # del más antiguo al más reciente


def autor(r):
    if r["yo"]:
        return "Yo"
    return (r["chat"] if r["tipo_chat"] == 0 else r["autor"]) or "?"


def archivo(r):
    """Ruta del adjunto si WhatsApp ya lo ha descargado en el Mac."""
    if r["ruta"] and (MEDIA / r["ruta"]).exists():
        return MEDIA / r["ruta"]
    return None


def contenido(r):
    t, texto, titulo = r["tipo"], (r["texto"] or "").strip(), (r["titulo"] or "").strip()
    if t in (0, 7):  # texto y enlaces
        return texto
    if t == 6:  # avisos del grupo («X añadió a Y»); sin texto no aportan nada
        return f"[aviso del grupo] {texto}" if texto else ""
    if t == 3:
        segundos = int(r["duracion"] or 0)
        estado = "" if archivo(r) else " · no descargado en el Mac"
        return f"[audio {segundos // 60}:{segundos % 60:02d}{estado}]"
    detalle = "" if t in (4, 5, 15) else (texto or titulo)  # pie de foto o nombre del documento
    return f"[{TIPOS.get(t, 'otro contenido')}]" + (f" {detalle}" if detalle else "")


def imprimir(filas, con_chat=False):
    dia = None
    for r in filas:
        linea = contenido(r)
        if not linea:
            continue
        f = a_fecha(r["fecha"])
        if f.date() != dia:
            dia = f.date()
            print(f"\n── {DIAS_SEMANA[f.weekday()]} {f:%d-%m-%Y} ──")
        chat = f"[{r['chat']}] " if con_chat else ""
        print(f"{f:%H:%M} {chat}{autor(r)}: " + linea.replace("\n", "\n      "))


def cmd_chats(a):
    chats = abrir("ChatStorage.sqlite").execute(sql_chats()).fetchall()
    if a.buscar:
        chats = [c for c in chats if normalizar(a.buscar) in normalizar(c["nombre"])]
    if a.sin_leer:
        chats = [c for c in chats if c["sin_leer"]]
    for c in chats[:a.limite]:
        print(describir(c))
    if len(chats) > a.limite:
        print(f"… y {len(chats) - a.limite} más (usa --limite)")


def cmd_leer(a):
    con = abrir("ChatStorage.sqlite")
    chat = elegir_chat(con, a.chat)
    filas = mensajes(con, chat, *rango(a), limite=a.limite)
    print(describir(chat))
    if not filas:
        print("Sin mensajes en ese periodo.")
        return
    imprimir(filas)
    if len(filas) == a.limite:
        print(f"\n(Solo los {a.limite} más recientes del periodo; usa --limite para ver más)")


def cmd_buscar(a):
    con = abrir("ChatStorage.sqlite")
    chat = elegir_chat(con, a.chat) if a.chat else None
    filas = mensajes(con, chat, *rango(a), texto=a.texto, limite=a.limite)
    if not filas:
        print(f"Nada con «{a.texto}».")
        return
    imprimir(filas, con_chat=chat is None)
    if len(filas) == a.limite:
        print(f"\n(Solo los {a.limite} más recientes; usa --limite para ver más)")


def cmd_descargar(a):
    con = abrir("ChatStorage.sqlite")
    chat = elegir_chat(con, a.chat) if a.chat else None
    filas = mensajes(con, chat, *rango(a), tipos=TIPOS_DESCARGA[a.tipo], limite=a.limite)
    if not filas:
        print("No hay adjuntos de ese tipo en el periodo.")
        return
    destino = Path(a.destino).expanduser()
    try:
        destino.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        salir(f"No puedo crear la carpeta {destino} ({e}). Prueba con otra en --destino.")
    copiados, faltan = [], []
    for r in filas:
        origen = archivo(r)
        if not origen:
            faltan.append(r)
            continue
        partes = ["whatsapp", kebab(TIPOS[r["tipo"]]), kebab(r["chat"])]
        if r["tipo_chat"] or r["yo"]:
            partes.append(kebab(autor(r)))
        if r["tipo"] == 8 and (r["texto"] or r["titulo"]):
            partes.append(kebab(Path(r["texto"] or r["titulo"]).stem))
        partes.append(f"{a_fecha(r['fecha']):%Y-%m-%d-%H%M}")
        base, ext = "-".join(partes), origen.suffix.lower()
        final, n = destino / f"{base}{ext}", 2
        while final.exists() and final.stat().st_size != origen.stat().st_size:
            final, n = destino / f"{base}-{n}{ext}", n + 1
        if not final.exists():
            try:
                shutil.copy2(origen, final)
            except OSError as e:
                salir(f"No puedo copiar a {destino} ({e}). Si el agente funciona en un entorno aislado, "
                      "pide permiso para ejecutar la orden fuera de él o usa --destino con otra carpeta.")
        copiados.append(final)
    for ruta in copiados:
        print(f"✔ {ruta}")
    if faltan:
        print(f"\n⚠ {len(faltan)} sin descargar en el Mac (WhatsApp aún no los ha traído del móvil):")
        for r in faltan[-20:]:
            print(f"  {a_fecha(r['fecha']):%d-%m-%Y %H:%M} · {r['chat']} · {autor(r)}: {contenido(r)}")
        print("  → Ábrelos en WhatsApp para Mac (reproducir o descargar) y repite la orden.")
    if len(filas) == a.limite:
        print(f"\n(Solo los {a.limite} adjuntos más recientes; usa --limite para traer más)")


def cmd_enviar(a):
    con = abrir("ChatStorage.sqlite")
    chat = elegir_chat(con, a.chat)
    nombre = chat["nombre"] or chat["jid"]
    telefono = numero(chat["jid"], mapa_lid()) if chat["tipo"] == 0 else None
    if telefono:
        consulta = urllib.parse.urlencode({"phone": telefono, "text": a.texto},
                                          quote_via=urllib.parse.quote)
        subprocess.run(["open", f"whatsapp://send?{consulta}"], check=True)
        print(f"Borrador abierto en el chat de «{nombre}». NO se ha enviado: revísalo y pulsa Enviar.")
    else:
        subprocess.run(["pbcopy"], input=a.texto.encode("utf-8"), check=True)
        subprocess.run(["open", "-a", "WhatsApp"], check=True)
        motivo = ("es un grupo y WhatsApp no deja abrir borradores en grupos" if chat["tipo"]
                  else "no tiene teléfono localizable")
        print(f"«{nombre}» {motivo}. Texto copiado al portapapeles y WhatsApp abierto: "
              "entra en el chat, pega con ⌘V y pulsa Enviar.")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="WhatsApp para Mac: leer, buscar, descargar adjuntos "
                                            "y abrir borradores (nunca envía).")
    sub = p.add_subparsers(dest="orden", required=True)

    def periodo(sp):
        sp.add_argument("--dias", type=int, help="hoy y los N-1 días anteriores (1 = solo hoy)")
        sp.add_argument("--desde", help="AAAA-MM-DD")
        sp.add_argument("--hasta", help="AAAA-MM-DD (incluido)")

    s = sub.add_parser("chats", help="lista los chats, del más reciente al más antiguo")
    s.add_argument("--buscar")
    s.add_argument("--sin-leer", action="store_true")
    s.add_argument("--limite", type=int, default=30)
    s.set_defaults(func=cmd_chats)

    s = sub.add_parser("leer", help="muestra la conversación de un chat")
    s.add_argument("chat")
    periodo(s)
    s.add_argument("--limite", type=int, default=100)
    s.set_defaults(func=cmd_leer)

    s = sub.add_parser("buscar", help="busca un texto en todos los chats o en uno")
    s.add_argument("texto")
    s.add_argument("--chat")
    periodo(s)
    s.add_argument("--limite", type=int, default=50)
    s.set_defaults(func=cmd_buscar)

    s = sub.add_parser("descargar", help="copia audios u otros adjuntos (por defecto a Descargas)")
    s.add_argument("chat", nargs="?")
    s.add_argument("--tipo", choices=list(TIPOS_DESCARGA), default="audio")
    periodo(s)
    s.add_argument("--limite", type=int, default=20)
    s.add_argument("--destino", default="~/Downloads")
    s.set_defaults(func=cmd_descargar)

    s = sub.add_parser("enviar", help="abre un borrador en WhatsApp (NO envía)")
    s.add_argument("chat")
    s.add_argument("texto")
    s.set_defaults(func=cmd_enviar)

    a = p.parse_args()
    try:
        a.func(a)
    except sqlite3.OperationalError as e:
        salir(f"Esta versión de WhatsApp para Mac guarda los datos de otra forma y no puedo leerlos ({e}).")


if __name__ == "__main__":
    main()
