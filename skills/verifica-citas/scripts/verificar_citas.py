#!/usr/bin/env python3
"""Verifica referencias bibliográficas contra CrossRef, DataCite y PubMed.

Uso:
    python3 verificar_citas.py referencias.txt --salida informe.md [--correo tu@correo.es]

El archivo de entrada lleva una referencia por línea (texto libre, con o sin DOI o PMID).
No necesita instalar nada ni ninguna clave: usa las API públicas de esos registros.
El correo es opcional: sirve para identificarse ante CrossRef y PubMed, como piden sus
guías de uso, y da más margen de peticiones.

Comprueba que el artículo existe y que título, primer autor, año, revista y DOI coinciden
con el registro oficial, y avisa de retractaciones. No comprueba volumen ni páginas, ni
que el artículo diga lo que el texto le atribuye.
"""
import argparse
import difflib
import html
import http.client
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.2"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"]+", re.I)
PMID_RE = re.compile(r"(?i)\bPMID\s*:?\s*(\d{5,9})\b")
URL_DOI_RE = re.compile(r"(?i)(?:https?://)?(?:dx\.)?doi\.org/")
NUMERACION_RE = re.compile(r"^\s*(?:\[\d{1,3}\]|\(\d{1,3}\)|#\d{1,3}[.)]?|\d{1,3}[.)\-])\s+")
LIBRO_RE = re.compile(r"(?i)\b(?:in|en):\s|,\s*(?:eds?|editors?|editore?s?)\b|\(eds?\.?\)|\bedici[oó]n\b|\b\d+(?:st|nd|rd|th|\.?ª)\s*ed\b|\bp\.\s*\d")
AUTOR_INICIAL_RE = re.compile(r"^[A-ZÁÉÍÓÚÑÜ][\w'’\-]+(?: [\w'’\-]+){0,2} [A-Z]{1,3}(?:,|\.| et al)")
NUMERAL_RE = re.compile(r"^(\d+|i{1,3}|iv|v|vi{1,3}|ix|x)$")
LETRAS = str.maketrans({"ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "ß": "ss", "æ": "ae", "Æ": "AE",
                        "đ": "d", "Đ": "D", "œ": "oe", "Œ": "OE"})
VACIAS = {"the", "of", "and", "for", "a", "an", "de", "la", "el", "y", "e", "del", "los", "las", "in", "on",
          "und", "der", "et", "des", "le", "du"}
UMBRAL_TITULO = 0.80
MIN_PALABRAS_TITULO = 4
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
RETIRADA = ("retract", "withdraw", "removal")


class SinConexion(Exception):
    pass


def pedir(url, correo=None):
    agente = "verifica-citas/" + VERSION
    if correo:
        agente += " (mailto:%s)" % correo
    peticion = urllib.request.Request(url, headers={"User-Agent": agente})
    for intento in range(3):
        try:
            with urllib.request.urlopen(peticion, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503) and intento < 2:
                time.sleep(3 * (intento + 1))
                continue
            raise SinConexion("el servidor respondió %s" % e.code)
        except ValueError:
            # Respuesta que no es de la API: portal de la wifi, página de mantenimiento…
            raise SinConexion("respuesta no válida del servidor")
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as e:
            if intento < 2:
                time.sleep(3 * (intento + 1))
                continue
            raise SinConexion(type(e).__name__)


# ---------------------------------------------------------------- texto

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", (texto or "").translate(LETRAS))
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", texto)).strip()


def limpiar_titulo(titulo):
    titulo = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(titulo or "")))
    return re.sub(r"^\s*RETRACTED(?: ARTICLE)?:\s*", "", titulo, flags=re.I).strip()


def extraer_dois(linea):
    dois = []
    for m in DOI_RE.finditer(linea):
        doi = re.split(r"\]\(|[​ ]", m.group(0))[0]
        doi = re.split(r"[;.,]?(?:PMID|PMCID|Epub)\b", doi, flags=re.I)[0]
        while doi and (doi[-1] in ".,;:]}*_>\"'" or (doi[-1] == ")" and doi.count("(") < doi.count(")"))):
            doi = doi[:-1]
        if doi and doi.lower() not in [d.lower() for d in dois]:
            dois.append(doi)
    return dois


def texto_sin_ids(linea):
    """La referencia sin numeración inicial y sin DOI, PMID ni sus direcciones web."""
    linea = NUMERACION_RE.sub("", linea)
    linea = PMID_RE.sub(" ", DOI_RE.sub(" ", linea))
    linea = URL_DOI_RE.sub(" ", linea)
    return re.sub(r"(?i)\[?\bdoi\b\]?\s*:?\(?", " ", linea)


def sin_ids(linea):
    return normalizar(texto_sin_ids(linea))


def titulo_corto(titulo):
    return 0 < len(normalizar(limpiar_titulo(titulo)).split()) < MIN_PALABRAS_TITULO


def _cobertura(t, r):
    if not t or not r:
        return 0.0
    if t in r:
        return 1.0
    m = difflib.SequenceMatcher(None, t, r, autojunk=False)
    return sum(b.size for b in m.get_matching_blocks() if b.size >= 4) / len(t)


def parecido(titulo, referencia):
    """Qué parte del título oficial aparece en la referencia (0 a 1).

    Muchas referencias citan solo el título principal, sin el subtítulo ni el
    acrónimo entre paréntesis, así que se prueba también con esa forma corta.
    Un título oficial de menos de cuatro palabras («Asthma») solo cuenta si
    aparece en la referencia como un tramo completo entre signos de puntuación.
    """
    titulo = limpiar_titulo(titulo)
    if not normalizar(titulo):
        return 0.0
    if titulo_corto(titulo):
        tramos = [normalizar(s) for s in re.split(r"[.?!:;]\s", texto_sin_ids(referencia) + " ")]
        return 1.0 if normalizar(titulo) in tramos else 0.0
    r = normalizar(referencia)
    corto = re.sub(r"\([^)]*\)", " ", titulo.split(":")[0])
    formas = [normalizar(titulo)]
    if len(normalizar(corto).split()) >= MIN_PALABRAS_TITULO:
        formas.append(normalizar(corto))
    return max(_cobertura(f, r) for f in formas)


def palabras_distintas(titulo, referencia):
    """Palabras significativas del título oficial que no están en la referencia.

    Sirve para distinguir «Part 1» de «Part 2» o «2018 update» de «2019 update»,
    que comparten casi todo el título. Si la referencia omite el subtítulo entero,
    no se cuenta como diferencia.
    """
    titulo = limpiar_titulo(titulo)
    t, r = normalizar(titulo).split(), normalizar(referencia).split()
    n = len(normalizar(titulo.split(":")[0]).split())
    m = difflib.SequenceMatcher(None, t, r, autojunk=False)
    vistas = {i for b in m.get_matching_blocks() for i in range(b.a, b.a + b.size)}
    if not any(i >= n for i in vistas):
        t = t[:n]
    return [p for i, p in enumerate(t) if i not in vistas and (len(p) > 3 or NUMERAL_RE.match(p))]


# ---------------------------------------------------------------- registros

def crossref_por_doi(doi, correo):
    datos = pedir("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"), correo)
    return datos["message"] if datos else None


def datacite_por_doi(doi, correo):
    """DOI reales que no están en CrossRef: arXiv, Zenodo, tesis, conjuntos de datos."""
    datos = pedir("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/"), correo)
    a = ((datos or {}).get("data") or {}).get("attributes")
    if not a:
        return None
    autores = a.get("creators") or []
    familia = (autores[0].get("familyName") or "") if autores else ""
    return {"title": [(a.get("titles") or [{}])[0].get("title", "")],
            "container-title": [a.get("publisher") if isinstance(a.get("publisher"), str) else ""],
            "issued": {"date-parts": [[a.get("publicationYear")]]},
            "author": [{"family": familia}] if familia else [],
            "DOI": a.get("doi") or doi, "type": "datacite", "_fuente": "DataCite"}


def crossref_por_texto(texto, correo):
    url = "https://api.crossref.org/works?rows=8&query.bibliographic=" + urllib.parse.quote(texto[:400])
    datos = pedir(url, correo)
    return datos["message"]["items"] if datos else []


def _extra(correo):
    return "&tool=verifica-citas" + ("&email=" + urllib.parse.quote(correo) if correo else "")


def _obra_pubmed(pmid, r):
    doi = next((i.get("value") for i in r.get("articleids", []) if i.get("idtype") == "doi"), None)
    anio = re.match(r"\d{4}", r.get("pubdate", "") or "")
    autores = r.get("authors") or []
    personal = bool(autores) and autores[0].get("authtype") == "Author"
    return {"title": [(r.get("title") or "").rstrip(".")],
            "container-title": [r.get("fulljournalname", "")],
            "issued": {"date-parts": [[int(anio.group(0)) if anio else None]]},
            "author": [{"family": autores[0]["name"].rsplit(" ", 1)[0]}] if personal else [],
            "DOI": doi or "", "_pmid": pmid, "_tipos": r.get("pubtype", []), "_fuente": "PubMed"}


def pubmed_resumenes(ids, correo):
    if not ids:
        return []
    time.sleep(0.4)
    datos = pedir(EUTILS + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids) + _extra(correo))
    resultado = (datos or {}).get("result", {})
    return [_obra_pubmed(i, resultado[i]) for i in ids if resultado.get(i, {}).get("title")]


def pubmed_buscar(termino, correo, maximo=5):
    datos = pedir(EUTILS + "esearch.fcgi?db=pubmed&retmode=json&retmax=%d&term=" % maximo
                  + urllib.parse.quote(termino) + _extra(correo))
    return (datos or {}).get("esearchresult", {}).get("idlist", [])


def pubmed_por_doi(doi, correo):
    ids = pubmed_buscar(doi + "[doi]", correo)
    obras = pubmed_resumenes(ids, correo) if len(ids) == 1 else []
    return obras[0] if obras else None


def pubmed_por_pmid(pmid, correo):
    obras = pubmed_resumenes([pmid], correo)
    return obras[0] if obras else None


def primer_citado(linea):
    """El primer autor tal como lo cita la referencia («García-López E»)."""
    autores = re.split(r"\.\s", texto_sin_ids(linea), maxsplit=1)[0]
    return re.split(r",|;|\bet al\b|\by\b|\band\b|&", autores, maxsplit=1)[0].strip()[:80]


def pubmed_por_titulo(linea, correo):
    """Candidatos de PubMed para referencias que CrossRef no localiza por el texto.

    En una referencia al estilo Vancouver el título es el segundo tramo; si no
    da resultado, se prueba con el tramo más largo que no sea una lista de autores.
    """
    tramos = [s.strip() for s in re.split(r"\.\s", texto_sin_ids(linea)) if normalizar(s)]
    if len(tramos) < 2:
        return []
    resto = [s for s in tramos[1:] if not re.search(r"\d{4};|\d+\(\d+\)", s) and len(normalizar(s).split()) >= 2]
    candidatos = []
    for s in ([tramos[1]] if len(normalizar(tramos[1]).split()) >= 2 else []) + sorted(resto, key=len, reverse=True)[:1]:
        if s not in candidatos:
            candidatos.append(s)
    apellido = re.sub(r"\s+[A-Z]{1,3}$", "", primer_citado(linea)).strip()
    anios = re.findall(r"(?<![:\-–\d])\b((?:19|20)\d{2})\b(?!\s*[-–]\s*\d)", texto_sin_ids(linea))
    for titulo in candidatos:
        consulta = normalizar(titulo) + "[Title]"
        ids = []
        if apellido and anios:
            ids = pubmed_buscar("%s AND %s[Author] AND %s[dp]" % (consulta, apellido, anios[0]), correo)
            time.sleep(0.4)
        if not ids and apellido:
            ids = pubmed_buscar(consulta + " AND " + apellido + "[Author]", correo)
        if not ids:
            time.sleep(0.4)
            ids = pubmed_buscar(consulta, correo)
        if ids:
            return pubmed_resumenes(ids, correo)
        time.sleep(0.4)
    return []


# ---------------------------------------------------------------- comparación

def ficha(obra):
    titulo = limpiar_titulo((obra.get("title") or [""])[0])
    revista = html.unescape((obra.get("container-title") or [""])[0] or "")
    partes = ((obra.get("issued") or {}).get("date-parts") or [[None]])[0] or [None]
    autores = obra.get("author") or []
    primero = (autores[0].get("family") or "") if autores else ""
    return titulo, revista, partes[0], primero


def _apellido(texto):
    """Apellido normalizado y sin diferencias de grafía (Müller = Mueller)."""
    return re.sub(r"([aou])e", r"\1", normalizar(texto))


def autor_coincide(primero, linea):
    """True si el primer autor oficial es el primero citado; "desplazado" si
    figura entre los autores pero no en primer lugar; False si no figura; None
    si no se conoce el primer autor oficial."""
    oficial = _apellido(primero)
    if not oficial:
        return None
    formas = [oficial]
    partes = oficial.split()
    if len(partes) > 1 and len(partes[0]) >= 4:
        formas.append(partes[0])          # «García E» por «Garcia-Lopez»
    citado = _apellido(primer_citado(linea))
    if any(re.search(r"\b%s\b" % re.escape(f), citado) for f in formas):
        return True
    autores = _apellido(re.split(r"\.\s", texto_sin_ids(linea), maxsplit=1)[0])
    return "desplazado" if re.search(r"\b%s\b" % re.escape(oficial), autores) else False


def anios_citados(obra, linea):
    """Años escritos en la referencia, sin contar los del propio título, los de un
    intervalo de páginas (2013-24) ni los que siguen a dos puntos (volumen:páginas)."""
    texto = texto_sin_ids(linea)
    titulo = ficha(obra)[0]
    if titulo:
        texto = re.sub(re.escape(titulo), " ", texto, flags=re.I)
        texto = re.sub(re.escape(titulo.split(":")[0]), " ", texto, flags=re.I)
    return [int(a) for a in re.findall(r"(?<![:\-–\d])\b((?:19|20)\d{2})\b(?!\s*[-–]\s*\d)", texto)]


def anio_coincide(obra, linea, exacto=False):
    """True, False, o None si falta el año en el registro o en la referencia."""
    anio = ficha(obra)[2]
    citados = anios_citados(obra, linea)
    if not anio or not citados:
        return None
    return any(abs(int(anio) - a) <= (0 if exacto else 1) for a in citados)


def revista_coincide(revista, linea):
    """True si la revista oficial aparece en la referencia, completa o abreviada
    («N Engl J Med» por «New England Journal of Medicine»). None si no hay revista."""
    oficial = [p for p in normalizar(re.sub(r"\([^)]*\)", " ", revista)).split() if p not in VACIAS]
    if not oficial:
        return None
    citadas = [p for p in sin_ids(linea).split() if p not in VACIAS]
    siglas = "".join(p[0] for p in oficial)
    if len(oficial) == 1:
        return oficial[0] in citadas
    if len(siglas) >= 3 and siglas in citadas:
        return True
    if len(oficial) == 2 and oficial[1] == "journal":     # «Rhinology journal» citada como «Rhinology»
        return oficial[0] in citadas
    for k in (0, 1):                      # la abreviatura puede saltarse la primera palabra
        resto = oficial[k:]
        if len(resto) < 2:
            break
        minimo = max(2, (len(resto) + 1) // 2)
        for i in range(len(citadas)):
            j = 0
            while j < len(resto) and i + j < len(citadas) and resto[j].startswith(citadas[i + j]):
                j += 1
            if j >= minimo:
                return True
    return False


def buscar_por_texto(linea, correo):
    """Devuelve (obra aceptada o None, obra solo parecida o None, ¿hay varios registros válidos?).

    Para aceptar un candidato hallado por el texto hace falta que el título
    coincida y, además, dos de estas tres cosas: primer autor, año y revista. Un
    título parecido con otro autor y otra revista es otro artículo, no una errata.
    Si el título oficial es muy corto o la referencia parece un libro, el primer
    autor y el año son obligatorios.
    """
    candidatos = crossref_por_texto(linea, correo)
    time.sleep(0.4)
    if not any(parecido(ficha(o)[0], linea) >= UMBRAL_TITULO and autor_coincide(ficha(o)[3], linea) is True
               and anio_coincide(o, linea) is True for o in candidatos):
        candidatos += pubmed_por_titulo(linea, correo)
    validos, parecida = [], None
    for obra in candidatos:
        titulo = ficha(obra)[0]
        if parecido(titulo, linea) < UMBRAL_TITULO or palabras_distintas(titulo, linea):
            continue
        autor_ok = autor_coincide(ficha(obra)[3], linea) is True
        anio_ok = anio_coincide(obra, linea) is True
        revista_ok = revista_coincide(ficha(obra)[1], linea) is True
        estricto = titulo_corto(titulo) or bool(LIBRO_RE.search(linea))
        sin_anio = anio_coincide(obra, linea) is None       # la referencia no trae año: no cuenta en contra
        if (autor_ok and anio_ok) if estricto else (autor_ok + anio_ok + revista_ok >= 2 or (autor_ok and sin_anio)):
            validos.append((autor_ok, revista_ok, anio_coincide(obra, linea, exacto=True) is True, anio_ok,
                            obra.get("type") == "journal-article" or bool(obra.get("_pmid")), obra))
        else:
            parecida = parecida or obra
    if not validos:
        return None, parecida, False
    validos.sort(key=lambda v: v[:5], reverse=True)
    mejores = {(v[5].get("DOI") or "").lower() for v in validos if v[:5] == validos[0][:5]}
    return validos[0][5], None, len(mejores - {""}) > 1


def descripcion(obra):
    titulo, revista, anio, primero = ficha(obra)
    return "%s (%s, %s%s)" % (titulo, primero or "sin autor personal", anio or "s. f.",
                             ", doi:" + obra["DOI"] if obra.get("DOI") else "")


def estado_editorial(obra, tipos_pubmed):
    """Devuelve (retirada, parcial, es_nota, expresion_de_preocupacion)."""
    avisos = [(a.get("type") or "").lower() for a in obra.get("updated-by", []) or []]
    completos = [a for a in avisos if "partial" not in a]
    retirada = any(r in a for a in completos for r in RETIRADA) or "Retracted Publication" in tipos_pubmed
    parcial = any("partial" in a for a in avisos)
    es_nota = any(r in (a.get("type") or "").lower() for a in obra.get("update-to", []) or [] for r in RETIRADA) \
        or "Retraction of Publication" in tipos_pubmed
    preocupacion = any("concern" in a for a in avisos) or "Expression of Concern" in tipos_pubmed
    return retirada, parcial, es_nota, preocupacion


def completar_con_pubmed(obra, correo, notas):
    """Devuelve (pmid, tipos de publicación, primer autor según PubMed)."""
    if obra.get("_pmid"):
        return obra["_pmid"], obra.get("_tipos", []), ficha(obra)[3]
    if not obra.get("DOI"):
        return None, [], ""
    try:
        time.sleep(0.4)
        pm = pubmed_por_doi(obra["DOI"], correo)
    except SinConexion:  # PubMed caído no invalida lo comprobado en el registro de DOI
        notas.append("No se pudo consultar PubMed; no se ha comprobado allí si está retractada.")
        return None, [], ""
    if not pm:
        notas.append("No figura en PubMed (puede ser normal: libro, congreso, prepublicación o revista no indexada).")
        return None, [], ""
    return pm["_pmid"], pm.get("_tipos", []), ficha(pm)[3]


def verificar(linea, correo):
    linea = urllib.parse.unquote(linea)
    dois = extraer_dois(linea)
    doi = dois[0] if dois else None
    m = PMID_RE.search(linea)
    pmid_citado = m.group(1) if m else None
    res = {"referencia": linea, "pmid": None, "notas": []}
    notas, dudas = res["notas"], []
    solo_ids = len(sin_ids(linea).split()) < MIN_PALABRAS_TITULO
    obra, por_doi, por_pmid = None, False, False

    if len(dois) > 1:
        notas.append("La línea contiene más de un DOI; se ha comprobado el primero (%s)." % doi)
    if doi:
        obra = crossref_por_doi(doi, correo) or datacite_por_doi(doi, correo)
        por_doi = obra is not None
        if obra is None:
            dudas.append("El DOI indicado (%s) no existe en CrossRef ni en DataCite, o está mal copiado." % doi)
    if obra is None and pmid_citado:
        time.sleep(0.4)
        obra = pubmed_por_pmid(pmid_citado, correo)
        por_pmid = obra is not None
        if obra is None:
            dudas.append("El PMID indicado (%s) no existe en PubMed." % pmid_citado)
            pmid_citado = None
    if obra is None and not solo_ids:
        obra, parecida, varios = buscar_por_texto(linea, correo)
        if obra:
            notas.append("Localizada por el título en %s%s." % (
                obra.get("_fuente", "CrossRef"),
                "; DOI propuesto: " + obra["DOI"] if obra.get("DOI") else "; sin DOI registrado"))
            if varios:
                notas.append("Hay varios registros con este título, autor y año: confirma el DOI antes de usarlo.")
        elif parecida:
            notas.append("Lo más parecido que existe no coincide lo suficiente (otro autor, otro año u otra "
                         "revista): %s. No lo tomes por la misma referencia." % descripcion(parecida))

    if obra is None:
        res["veredicto"] = "NO LOCALIZADA"
        if LIBRO_RE.search(linea):
            aviso = ("Parece un libro o un capítulo: estos registros no suelen incluirlos. Compruébalo en el "
                     "catálogo de la editorial o de una biblioteca; no la des por inventada.")
        else:
            aviso = ("No aparece en los registros. Puede estar mal escrita, ser antigua o de una revista no "
                     "indexada, o ser inventada: búscala a mano antes de usarla.")
        res["notas"] = dudas + notas + [aviso]
        return res

    titulo, revista, anio, primero = ficha(obra)
    pmid, tipos, primero_pubmed = completar_con_pubmed(obra, correo, notas)
    primero = primero or primero_pubmed
    if not primero and obra.get("_pmid") and obra.get("DOI"):
        try:
            time.sleep(0.3)
            primero = ficha(crossref_por_doi(obra["DOI"], correo) or {})[3]
        except SinConexion:
            pass
    res.update(titulo=titulo, revista=revista, anio=anio, autor=primero, doi_real=obra.get("DOI"), pmid=pmid)

    if pmid_citado and not por_pmid:
        if pmid and pmid != pmid_citado:
            dudas.append("El PMID indicado (%s) corresponde a otro artículo; el de este es %s." % (pmid_citado, pmid))
        elif not pmid:
            dudas.append("El PMID indicado (%s) no se pudo relacionar con este artículo." % pmid_citado)

    titulo_ok, autor_ok = True, None
    if not solo_ids:
        titulo_ok = parecido(titulo, linea) >= UMBRAL_TITULO
        distintas = palabras_distintas(titulo, linea) if titulo_ok and not titulo_corto(titulo) else []
        if not titulo_ok and titulo_corto(titulo):
            dudas.append("No se pudo contrastar el título: el oficial («%s») tiene menos de cuatro palabras y "
                         "no aparece tal cual en la referencia." % titulo)
        elif not titulo_ok:
            dudas.append("El título de la referencia no coincide con el del registro oficial.")
        elif distintas:
            titulo_ok = False
            dudas.append("El título difiere del oficial en: %s. Puede ser otra parte o edición del mismo trabajo."
                         % ", ".join(distintas[:6]))
        elif titulo_corto(titulo):
            notas.append("Título muy corto: la coincidencia se apoya en el autor y el año.")
    if not solo_ids or re.search(r"[a-z]{3}", sin_ids(linea)):
        autor_ok = autor_coincide(primero, linea)
        if autor_ok is False:
            dudas.append("El primer autor oficial (%s) no aparece en la referencia." % primero)
        elif autor_ok == "desplazado":
            dudas.append("El primer autor oficial (%s) figura en la referencia, pero no en primer lugar." % primero)
        elif autor_ok is None and AUTOR_INICIAL_RE.match(texto_sin_ids(linea).strip()):
            dudas.append("El registro oficial no incluye autores personales (autoría colectiva o registro "
                         "incompleto): los autores citados no se han podido confirmar.")
    if anio_coincide(obra, linea) is False:
        dudas.append("El año no coincide (oficial: %s)." % anio)
    if not solo_ids and titulo_ok and obra.get("type", "journal-article") == "journal-article" \
            and anios_citados(obra, linea) and revista_coincide(revista, linea) is False:
        dudas.append("La revista citada no parece la oficial («%s»)." % revista)
    if solo_ids and not dudas:
        notas.append("Solo se aportó el identificador: comprueba que el artículo es el que querías citar.")
    if obra.get("subtype") == "preprint" or obra.get("type") == "posted-content":
        notas.append("Es una prepublicación, sin revisión por pares.")

    retirada, parcial, es_nota, preocupacion = estado_editorial(obra, tipos)
    doi_ajeno = (por_doi or por_pmid) and not solo_ids and not titulo_ok and autor_ok is False
    citada_retractada = False
    if doi_ajeno:
        time.sleep(0.4)
        buena, _, _ = buscar_por_texto(linea, correo)
        if buena and (buena.get("DOI") or "").lower() != (obra.get("DOI") or "").lower():
            dudas.append("El identificador pertenece a otro artículo. El citado podría ser %s."
                         % (buena.get("DOI") or "PMID " + str(buena.get("_pmid"))))
            _, tipos_buena, _ = completar_con_pubmed(buena, correo, [])
            citada_retractada = estado_editorial(buena, tipos_buena)[0]
            if citada_retractada:
                dudas.append("El artículo citado está retractado.")
        if retirada:
            dudas.append("El identificador indicado pertenece a otro artículo, que además está retractado.")
    if es_nota and not retirada:
        dudas.append("Este identificador corresponde a una nota de retractación o retirada, no al artículo original.")
    if parcial:
        dudas.append("Tiene una retractación parcial: revisa qué parte se ha retirado.")
    if preocupacion:
        dudas.append("El editor ha publicado una expresión de preocupación sobre este artículo.")

    res["notas"] = dudas + notas
    if citada_retractada or (retirada and not doi_ajeno):
        res["veredicto"] = "RETRACTADA"
    else:
        res["veredicto"] = "DUDOSA" if dudas else "VERIFICADA"
    return res


# ---------------------------------------------------------------- informe

def informe(resultados, total):
    orden = ["RETRACTADA", "NO LOCALIZADA", "DUDOSA", "VERIFICADA"]
    marca = {"RETRACTADA": "🚫", "NO LOCALIZADA": "❌", "DUDOSA": "⚠️", "VERIFICADA": "✅"}
    cuenta = {v: sum(1 for r in resultados if r["veredicto"] == v) for v in orden}
    out = ["# Informe de verificación de citas", ""]
    if len(resultados) < total:
        out += ["**Informe parcial: comprobadas %d de %d referencias.**" % (len(resultados), total), ""]
    out += ["Total: %d · " % len(resultados) + " · ".join("%s %s: %d" % (marca[v], v.lower(), cuenta[v]) for v in orden), ""]
    for v in orden:
        grupo = [r for r in resultados if r["veredicto"] == v]
        if not grupo:
            continue
        out += ["## %s %s (%d)" % (marca[v], v.capitalize(), len(grupo)), ""]
        for r in grupo:
            out.append("**%d.** %s" % (r["n"], NUMERACION_RE.sub("", r["referencia"])))
            if r.get("titulo"):
                out.append("- Registro oficial: %s. *%s*, %s. Primer autor: %s." % (
                    r["titulo"], r.get("revista") or "sin revista", r.get("anio") or "s. f.", r.get("autor") or "—"))
                enlaces = (["DOI: https://doi.org/%s" % r["doi_real"]] if r.get("doi_real") else []) \
                    + (["PubMed: https://pubmed.ncbi.nlm.nih.gov/%s/" % r["pmid"]] if r.get("pmid") else [])
                if enlaces:
                    out.append("- " + " · ".join(enlaces))
            for nota in r["notas"]:
                out.append("- %s" % nota)
            out.append("")
    return "\n".join(out)


def leer_referencias(ruta):
    try:
        bruto = open(ruta, "rb").read()
    except OSError:
        sys.exit("No encuentro el archivo «%s». Comprueba la ruta." % ruta)
    codificaciones = ["utf-8-sig", "utf-16", "cp1252"]
    if bruto[:2] in (b"\xff\xfe", b"\xfe\xff"):
        codificaciones.insert(0, "utf-16")
    texto = None
    for codificacion in codificaciones:
        try:
            texto = bruto.decode(codificacion)
            break
        except UnicodeError:
            continue
    if texto is None:
        texto = bruto.decode("utf-8", errors="replace")
    lineas = [l.strip() for l in texto.splitlines()]
    lineas = [l for l in lineas if l and not re.match(r"#(\s|$)", l)]
    # Si la lista va numerada, una línea sin número es la continuación de la anterior
    # (pasa al copiar la bibliografía de un PDF).
    numeradas = sum(1 for l in lineas if NUMERACION_RE.match(l))
    if len(lineas) >= 3 and numeradas >= 0.6 * len(lineas):
        unidas = []
        for l in lineas:
            if unidas and not NUMERACION_RE.match(l):
                unidas[-1] += " " + l
            else:
                unidas.append(l)
        if len(unidas) != len(lineas):
            print("Aviso: %d líneas sin numerar se han unido a la referencia anterior."
                  % (len(lineas) - len(unidas)), file=sys.stderr)
        lineas = unidas
    return lineas


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Verifica referencias contra CrossRef, DataCite y PubMed.")
    p.add_argument("archivo", help="Texto con una referencia por línea")
    p.add_argument("--correo", help="Tu correo, para identificarte ante CrossRef y PubMed (opcional)")
    p.add_argument("--salida", help="Archivo .md donde guardar el informe (por defecto, pantalla)")
    a = p.parse_args()
    lineas = leer_referencias(a.archivo)
    if not lineas:
        sys.exit("El archivo no contiene ninguna referencia.")
    if a.salida:
        try:
            open(a.salida, "w", encoding="utf-8").write("# Informe de verificación de citas\n\nEn curso…\n")
        except OSError:
            sys.exit("No puedo escribir en «%s». Comprueba que la carpeta existe." % a.salida)
    resultados, fallos_seguidos = [], 0
    for n, linea in enumerate(lineas, 1):
        print("Comprobando %d de %d…" % (n, len(lineas)), file=sys.stderr)
        try:
            r = verificar(linea, a.correo)
            fallos_seguidos = 0
        except SinConexion as e:
            fallos_seguidos += 1
            if fallos_seguidos == 3 and len(resultados) == 2:
                sys.exit("No consigo conectar con los registros (%s). Comprueba la conexión a internet; si la hay, "
                         "puede que este Python no tenga bien los certificados: prueba con otro Python." % e)
            r = {"referencia": linea, "veredicto": "DUDOSA",
                 "notas": ["No se pudo comprobar por un fallo de conexión (%s). Repite más tarde." % e]}
        except Exception as e:  # un fallo con una referencia no debe perder las demás
            r = {"referencia": linea, "veredicto": "DUDOSA",
                 "notas": ["No se pudo comprobar por un error interno (%s). Compruébala a mano." % type(e).__name__]}
        r["n"] = n
        resultados.append(r)
        if a.salida:  # se guarda tras cada referencia: si el proceso se corta, queda lo hecho
            open(a.salida, "w", encoding="utf-8").write(informe(resultados, len(lineas)))
        time.sleep(0.3)
    if a.salida:
        print("Informe guardado en %s" % a.salida, file=sys.stderr)
    else:
        print(informe(resultados, len(lineas)))


if __name__ == "__main__":
    main()
