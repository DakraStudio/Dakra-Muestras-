#!/usr/bin/env python3
"""Construye el sitio Guía Leonida a partir de los archivos de guia-leonida/datos/.

Uso (desde la raíz del repositorio):  python3 guia-leonida/_build/construir.py

Para agregar contenido NO se toca el HTML: se edita datos/*.json y se vuelve a correr.
  - datos/guias.json       guías (estado "publicada" crea su página; "pronto" solo sale bloqueada en la portada)
  - datos/noticias.json    noticias (cada una crea su página)
  - datos/productos.json   productos de afiliado (solo se muestran si config.amazon_tag tiene valor)
  - datos/coleccionables.json  lista para la herramienta de coleccionables
  - datos/config.json      redes, cuentas de ingresos (afiliados, donaciones, producto, AdSense)
"""
import json, hashlib, re, sys
from datetime import datetime, timezone, timedelta
from html import escape as e
from pathlib import Path
from urllib.parse import quote_plus

BASE = Path(__file__).resolve().parent.parent          # guia-leonida/
D = BASE / "datos"
cfg = json.loads((D / "config.json").read_text())
guias = json.loads((D / "guias.json").read_text())
noticias = sorted(json.loads((D / "noticias.json").read_text()), key=lambda n: n["fecha"], reverse=True)
productos = {p["id"]: p for p in json.loads((D / "productos.json").read_text())}
colec = json.loads((D / "coleccionables.json").read_text())

R = cfg["ruta"].rstrip("/")                 # /guia-leonida
URL = cfg["url"].rstrip("/")                # https://dakrastudio.com/guia-leonida
CT = timezone(timedelta(hours=-6))
HOY = datetime.now(CT).date().isoformat()
LANZADO = datetime.now(CT) >= datetime.fromisoformat(cfg["lanzamiento"])
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

def fecha(iso):
    y, m, d = map(int, iso[:10].split("-")); return f"{d} {MESES[m-1]} {y}"

def ver(nombre):
    return hashlib.md5((BASE / "assets" / nombre).read_bytes()).hexdigest()[:8]

publicadas = [g for g in guias if g.get("estado") == "publicada"]
pronto = [g for g in guias if g.get("estado") != "publicada"]
for g in guias:
    if not re.fullmatch(r"[a-z0-9-]+", g["slug"]): sys.exit(f"slug inválido: {g['slug']}")
for n in noticias:
    if not re.fullmatch(r"[a-z0-9-]+", n["slug"]): sys.exit(f"slug inválido: {n['slug']}")

# ---------------------------------------------------------------- piezas comunes
def head(titulo, desc, ruta, jsonld=None, noindex=False, tipo="website"):
    canon = URL + ruta
    extra = ""
    if cfg.get("adsense_client"):
        extra += f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={e(cfg["adsense_client"])}" crossorigin="anonymous"></script>\n'
    if cfg.get("search_console"):
        extra += f'<meta name="google-site-verification" content="{e(cfg["search_console"])}">\n'
    if jsonld:
        extra += '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>\n"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:type" content="{tipo}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="es_US">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="{e(cfg['nombre'])}" href="{R}/feed.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%8C%B4%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;800&family=Pacifico&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}/assets/estilo.css?v={ver('estilo.css')}">
{extra}</head>
"""

def cuerpo_abre(clase=""):
    return f"""<body class="{clase}" data-lanzamiento="{e(cfg['lanzamiento'])}">
<header class="top">
  <div class="wrap">
    <a class="logo" href="{R}/"><b>GUÍA</b><span class="neon">Leonida</span></a>
    <nav><a href="{R}/#guias">Guías</a><a href="{R}/#mapa">Mapa</a><a href="{R}/noticias/">Noticias</a><a href="{R}/herramientas/coleccionables/">Progreso</a></nav>
  </div>
</header>
<div class="hud" aria-hidden="true">
  <div class="clock" id="clock">00:00</div>
  <div class="cash" id="cash">$000000000</div>
  <div class="stars" id="stars"><span>★</span><span>★</span><span>★</span><span>★</span><span>★</span></div>
</div>
"""

def pie():
    redes = "".join(f'<a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["nombre"])}</a>' for r in cfg["redes"])
    afil = '<p>Algunos enlaces de esta página son de afiliado: si compras, podemos recibir una pequeña comisión sin costo extra para ti.</p>' if cfg.get("amazon_tag") else ""
    return f"""<footer>
  <div class="wrap">
    <p class="social">{redes}<a href="{R}/feed.xml">RSS</a><a href="{R}/privacidad/">Privacidad</a></p>
    <p>Guía Leonida es un sitio de fans <b>no oficial</b>. No está afiliado ni respaldado por Rockstar Games ni Take-Two Interactive. Grand Theft Auto y sus marcas pertenecen a sus respectivos dueños.</p>
    {afil}
    <p>© {HOY[:4]} Guía Leonida · Un proyecto de <a href="https://dakrastudio.com/">Dakra Studio</a></p>
  </div>
</footer>
<div class="toast" id="toast"><b>Muy pronto</b><span>Esta guía se publica en cuanto salga el juego</span></div>
<script src="{R}/assets/app.js?v={ver('app.js')}"></script>
</body>
</html>
"""

def caja_afiliados(ids):
    tag = cfg.get("amazon_tag")
    if not tag: return ""
    filas = []
    for i in ids:
        p = productos.get(i)
        if not p: continue
        url = f"https://www.amazon.com/s?k={quote_plus(p['busqueda'])}&tag={quote_plus(tag)}"
        filas.append(f'<div class="prod"><span><b>{e(p["nombre"])}</b><small>{e(p["nota"])}</small></span><a href="{e(url)}" target="_blank" rel="sponsored nofollow noopener">Ver precio</a></div>')
    if not filas: return ""
    return f'<div class="box"><h3>Equipo recomendado</h3>{"".join(filas)}<p class="fine">Enlaces de afiliado de Amazon.</p></div>'

def caja_apoyo():
    partes = []
    if cfg.get("producto_url"):
        precio = f" · {e(cfg['producto_precio'])}" if cfg.get("producto_precio") else ""
        partes.append(f'<p>Todas las ubicaciones, coches y métodos de dinero en un solo archivo.</p><a class="btn p" href="{e(cfg["producto_url"])}" target="_blank" rel="noopener">{e(cfg["producto_nombre"])}{precio}</a>')
    if cfg.get("donaciones_url"):
        partes.append(f'<p>¿Te sirvió? Ayúdanos a seguir publicando guías gratis.</p><a class="btn s" href="{e(cfg["donaciones_url"])}" target="_blank" rel="noopener">☕ Invítanos un café</a>')
    if not partes: return ""
    return f'<div class="box support"><h3>Apoya a Guía Leonida</h3>{"".join(partes)}</div>'

def caja_redes():
    btns = "".join(f'<li><a href="{e(r["url"])}" target="_blank" rel="noopener">Síguenos en {e(r["nombre"])} →</a></li>' for r in cfg["redes"])
    return f'<div class="box"><h3>Un truco nuevo cada día</h3><ul>{btns}</ul></div>'

def tarjeta(g):
    if g.get("estado") == "publicada":
        return f"""<a class="card" href="{R}/guias/{g['slug']}/" data-cat="{e(g['cat'])}">
      <div class="meta"><span class="ico">{e(g.get('ico','★'))}</span><span class="tag">{e(g['cat'])}</span><span class="badge ok">Nueva · {fecha(g['actualizado'])}</span></div>
      <h3>{e(g['titulo'])}</h3><p>{e(g['resumen'])}</p></a>"""
    lock = "Llega muy pronto" if LANZADO else "Se desbloquea el 19 de noviembre"
    return f"""<div class="card pronto" data-cat="{e(g['cat'])}" role="button" tabindex="0">
      <div class="meta"><span class="ico">{e(g.get('ico','★'))}</span><span class="tag">{e(g['cat'])}</span><span class="badge">🔒 Bloqueada</span></div>
      <h3>{e(g['titulo'])}</h3><p>{e(g['resumen'])}</p><span class="lock">{lock}</span></div>"""

def item_noticia(n):
    return f"""<a class="news" href="{R}/noticias/{n['slug']}/">
      <div class="meta"><span class="tag lbl-{e(n['etiqueta'])}">{e(n['etiqueta'])}</span><span>{fecha(n['fecha'])}</span></div>
      <h3>{e(n['titulo'])}</h3><p>{e(n['resumen'])}</p></a>"""

def escribir(ruta, html):
    p = BASE / ruta.strip("/") / "index.html" if not ruta.endswith(".xml") else BASE / ruta.strip("/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(re.sub(r"\n\s*\n+", "\n", html))

# ---------------------------------------------------------------- portada
MAPA = """<svg viewBox="0 0 400 470" role="img" aria-label="Mapa ilustrado de las seis regiones de Leonida">
<g class="wave" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="2"><path d="M0 430 q20 -8 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0"/><path d="M0 300 q20 -8 40 0 t40 0 t40 0 t40 0"/><path d="M300 190 q20 -8 40 0 t40 0 t40 0"/><path d="M310 400 q20 -8 40 0 t40 0 t40 0"/></g>
<g class="reg" data-r="kalaga"><path d="M40 40 L330 34 L326 112 L46 116 Z" fill="#2f9e5b"/><text x="186" y="80" text-anchor="middle">MOUNT KALAGA</text></g>
<g class="reg" data-r="gellhorn"><path d="M46 116 L170 114 L172 196 L120 214 L58 168 Z" fill="#c9783c"/><text x="112" y="158" text-anchor="middle">PORT</text><text x="112" y="174" text-anchor="middle">GELLHORN</text></g>
<g class="reg" data-r="ambrosia"><path d="M170 114 L326 112 L312 238 L184 240 L172 196 Z" fill="#b5a23a"/><ellipse cx="246" cy="196" rx="30" ry="16" fill="#3b7bd1" stroke="#12081f" stroke-width="3"/><text x="246" y="150" text-anchor="middle">AMBROSIA</text></g>
<g class="reg" data-r="grassrivers"><path d="M184 240 L250 240 L254 356 L214 344 L192 290 Z" fill="#3d8a7a"/><text x="222" y="300" text-anchor="middle">GRASS</text><text x="222" y="316" text-anchor="middle">RIVERS</text></g>
<g class="reg" data-r="vice"><path d="M250 240 L312 238 L322 316 L296 366 L254 356 Z" fill="#ff3d8b"/><text x="286" y="300" text-anchor="middle">VICE</text><text x="286" y="316" text-anchor="middle">CITY</text></g>
<g class="reg" data-r="keys"><circle cx="262" cy="392" r="9" fill="#22e1d6"/><circle cx="238" cy="408" r="8" fill="#22e1d6"/><circle cx="212" cy="420" r="7" fill="#22e1d6"/><circle cx="186" cy="428" r="7" fill="#22e1d6"/><circle cx="160" cy="432" r="6" fill="#22e1d6"/><text x="200" y="455" text-anchor="middle">LEONIDA KEYS</text></g>
<g class="pin" id="pin"><path d="M286 250 c-9 0 -15 7 -15 15 c0 11 15 24 15 24 s15 -13 15 -24 c0 -8 -6 -15 -15 -15z" fill="#ffd166" stroke="#12081f" stroke-width="3"/><circle cx="286" cy="265" r="5" fill="#12081f"/></g>
</svg>"""

PALMA = '<path d="M104 320 C112 230 92 150 112 70" stroke-width="13"/><path d="M112 70 Q60 40 8 70" stroke-width="10"/><path d="M112 70 Q70 10 30 18" stroke-width="10"/><path d="M112 70 Q120 0 160 8" stroke-width="10"/><path d="M112 70 Q170 40 196 84" stroke-width="10"/><path d="M112 70 Q150 80 168 132" stroke-width="9"/><path d="M112 70 Q70 90 46 140" stroke-width="9"/>'

def portada():
    cats = ["Todas"] + list(dict.fromkeys(g["cat"] for g in publicadas + pronto))
    chips = "".join(f'<button class="chip {"on" if c == "Todas" else ""}" data-c="{e(c)}">{e(c)}</button>' for c in cats)
    tarjetas = "".join(tarjeta(g) for g in publicadas + pronto)
    titulares = [n["titulo"] for n in noticias[:6]] or ["GTA 6 sale el 19 de noviembre en PS5 y Xbox Series"]
    track = "".join(f"<span>★ {e(t)}</span>" for t in titulares) * 2
    ultimas = "".join(item_noticia(n) for n in noticias[:4])
    mapa_url = next((f"{R}/guias/{g['slug']}/" for g in publicadas if g["cat"] == "Mapa"), f"{R}/")
    kicker = "Ya disponible en PS5 y Xbox Series" if LANZADO else "La espera está por terminar"
    hype = [("6", "regiones", "De las playas de Vice City a la montaña de Kalaga."), ("2", "protagonistas", "Jason y Lucia, juntos en una historia criminal."),
            ("13", "años de espera", "Desde GTA 5 en 2013 no había un GTA nuevo."), ("1", "estado entero", "Por primera vez, un estado completo y no una sola ciudad.")]
    hype_html = "".join(f'<div class="stat"><strong>{a}</strong><span>{b}</span><p>{c}</p></div>' for a, b, c in hype)
    sub_guias = "Llegan guías nuevas todos los días. Las bloqueadas se abren en cuanto haya información verificada." if LANZADO else "Las guías bloqueadas se abren en cuanto salga el juego. Vuelve el jueves."
    apoyo = caja_apoyo()
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": cfg["nombre"], "url": URL + "/", "inLanguage": "es",
              "description": cfg["descripcion"], "publisher": {"@type": "Organization", "name": "Dakra Studio", "url": "https://dakrastudio.com/"}}
    html = head("Guía Leonida · Guías de GTA 6 en español: trucos, dinero, coches y mapa", cfg["descripcion"], "/", jsonld)
    html += """<body class="home" data-lanzamiento="%s">
<div id="intro" aria-hidden="true"><div class="big">Bienvenido a Leonida</div><div class="neon">Guía Leonida</div><div class="bar"><i></i></div><small>Cargando el estado del sol</small></div>
""" % e(cfg["lanzamiento"])
    html += cuerpo_abre("home").split("\n", 1)[1]
    html += f"""<main id="inicio">
  <div class="hero">
    <div class="sun"></div>
    <svg class="palm l" viewBox="0 0 200 320" aria-hidden="true">{PALMA}</svg>
    <svg class="palm r" viewBox="0 0 200 320" aria-hidden="true">{PALMA}</svg>
    <div class="floor"></div>
    <div class="wrap hero-in">
      <span class="kicker" id="kicker">{kicker}</span>
      <h1>GTA 6<span class="neon">en español</span></h1>
      <p class="lead">Más de una década esperando. Vice City vuelve, y esta vez trae todo un estado. Aquí vas a encontrar cada secreto, cada coche y cada truco para hacer dinero, explicado en tu idioma.</p>
      <div class="count" id="count"></div>
      <div class="btns"><a class="btn p" href="#guias">Ver las guías</a><a class="btn s" href="#mapa">Explorar Leonida</a></div>
    </div>
  </div>
  <div class="ticker" aria-label="Noticias"><div class="lbl">ÚLTIMA HORA</div><div class="track">{track}</div></div>

  <section id="guias" class="reveal">
    <div class="wrap">
      <h2>Guías <span class="neon">de Leonida</span></h2>
      <p class="sub">{sub_guias}</p>
      <div class="tools"><input id="q" type="search" placeholder="Buscar: trucos, dinero, coche, secreto..." aria-label="Buscar guías"></div>
      <div class="chips" id="chips">{chips}</div>
      <div class="grid" id="lista">{tarjetas}</div>
      <p class="empty" id="vacio" hidden>Todavía no hay guías con esa búsqueda.</p>
    </div>
  </section>

  <section id="noticias" class="reveal">
    <div class="wrap">
      <h2>Noticias <span class="neon">de hoy</span></h2>
      <p class="sub">Lo último de GTA 6, marcado como confirmado, descubierto por jugadores o rumor. Sin inventos.</p>
      <div class="newslist">{ultimas}</div>
      <p style="margin-top:16px"><a class="btn s" href="{R}/noticias/">Todas las noticias</a></p>
    </div>
  </section>

  <section id="espera" class="reveal">
    <div class="wrap">
      <h2>Lo que te espera <span class="neon">en Leonida</span></h2>
      <div class="hype">{hype_html}</div>
    </div>
  </section>

  <section id="mapa" class="reveal">
    <div class="wrap">
      <h2>Explora <span class="neon">Leonida</span></h2>
      <p class="sub">Leonida es el estado ficticio donde pasa GTA 6, inspirado en Florida. Toca cada región para conocerla.</p>
      <div class="mapwrap"><div class="map">{MAPA}</div><div class="info" id="info" data-guia="{mapa_url}"></div></div>
    </div>
  </section>

  <section class="reveal">
    <div class="wrap">
      <div class="mini-cta"><div><h2 style="font-size:30px;margin:0">Lleva tu progreso</h2><p class="sub" style="margin:4px 0 0">Marca coches, coleccionables y logros. Se guarda en tu teléfono.</p></div><a class="btn p" href="{R}/herramientas/coleccionables/">Abrir mi progreso</a></div>
      {('<div style="margin-top:18px">' + apoyo + '</div>') if apoyo else ''}
    </div>
  </section>

  <section class="cta reveal">
    <div class="wrap">
      <h2>No te pierdas <span class="neon">nada</span></h2>
      <p class="sub" style="margin-inline:auto">Un truco nuevo cada día en video. Síguenos y llega a Leonida con ventaja.</p>
      <div class="btns">{"".join(f'<a class="btn {"p" if i == 0 else "s"}" href="{e(r["url"])}" target="_blank" rel="noopener">Seguir en {e(r["nombre"])}</a>' for i, r in enumerate(cfg["redes"]))}</div>
    </div>
  </section>
</main>
"""
    html += pie()
    escribir("/", html)

# ---------------------------------------------------------------- guía
def pagina_guia(g):
    ruta = f"/guias/{g['slug']}/"
    secciones = ""
    for s in g.get("secciones", []):
        secciones += f"<h2>{e(s['titulo'])}</h2>"
        secciones += "".join(f"<p>{e(p)}</p>" for p in s.get("parrafos", []))
        if s.get("lista"): secciones += "<ul>" + "".join(f"<li>{e(i)}</li>" for i in s["lista"]) + "</ul>"
        if s.get("pasos"): secciones += "<ol>" + "".join(f"<li>{e(i)}</li>" for i in s["pasos"]) + "</ol>"
    fuentes = " · ".join(f'<a href="{e(f["u"])}" target="_blank" rel="noopener">{e(f["t"])}</a>' for f in g.get("fuentes", []))
    otras = [x for x in publicadas if x["slug"] != g["slug"]][:6]
    rel = "".join(f'<li><a href="{R}/guias/{x["slug"]}/">{e(x.get("ico","★"))} {e(x["titulo"])}</a></li>' for x in otras)
    lateral = caja_afiliados(g.get("productos", [])) + caja_apoyo() + (f'<div class="box"><h3>Más guías</h3><ul>{rel}</ul></div>' if rel else "") + caja_redes()
    desc = g.get("resumen", "")
    jsonld = {"@context": "https://schema.org", "@type": "Article", "headline": g["titulo"], "description": desc, "inLanguage": "es",
              "datePublished": g.get("publicada", g["actualizado"]), "dateModified": g["actualizado"], "mainEntityOfPage": URL + ruta,
              "author": {"@type": "Organization", "name": "Guía Leonida"}, "publisher": {"@type": "Organization", "name": "Dakra Studio", "url": "https://dakrastudio.com/"}}
    html = head(f"{g.get('seo', g['titulo'])} · Guía Leonida", desc, ruta, jsonld, tipo="article") + cuerpo_abre()
    html += f"""<main>
  <div class="band"><div class="wrap">
    <div class="crumbs"><a href="{R}/">Guía Leonida</a> › <a href="{R}/#guias">Guías</a> › {e(g['cat'])}</div>
    <h1>{e(g['titulo'])}</h1>
    <p>{e(desc)}</p>
    <div class="tagline"><span class="pill">{e(g.get('ico','★'))} {e(g['cat'])}</span><span class="pill">Actualizada el {fecha(g['actualizado'])}</span></div>
  </div></div>
  <div class="wrap article">
    <article class="prose">
      <p class="lead">{e(g.get('intro',''))}</p>
      {secciones}
      {('<div class="sources">Fuentes: ' + fuentes + '</div>') if fuentes else ''}
    </article>
    <aside class="side">{lateral}</aside>
  </div>
</main>
"""
    html += pie()
    escribir(ruta, html)

# ---------------------------------------------------------------- noticias
def pagina_noticia(n):
    ruta = f"/noticias/{n['slug']}/"
    cuerpo = "".join(f"<p>{e(p)}</p>" for p in n.get("cuerpo", []))
    fuentes = " · ".join(f'<a href="{e(f["u"])}" target="_blank" rel="noopener">{e(f["t"])}</a>' for f in n.get("fuentes", []))
    aviso = '<p class="pend" style="margin:0 0 16px"><b>Rumor</b>Esto todavía no está confirmado por Rockstar. Lo actualizaremos si cambia.</p>' if n["etiqueta"] == "RUMOR" else ""
    otras = "".join(f'<li><a href="{R}/noticias/{x["slug"]}/">{e(x["titulo"])}</a></li>' for x in [y for y in noticias if y["slug"] != n["slug"]][:5])
    rel = "".join(f'<li><a href="{R}/guias/{x["slug"]}/">{e(x.get("ico","★"))} {e(x["titulo"])}</a></li>' for x in publicadas[:4])
    lateral = caja_apoyo() + (f'<div class="box"><h3>Más noticias</h3><ul>{otras}</ul></div>' if otras else "") + (f'<div class="box"><h3>Guías</h3><ul>{rel}</ul></div>' if rel else "") + caja_redes()
    jsonld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": n["titulo"], "description": n["resumen"], "inLanguage": "es",
              "datePublished": n["fecha"], "dateModified": n.get("actualizado", n["fecha"]), "mainEntityOfPage": URL + ruta,
              "author": {"@type": "Organization", "name": "Guía Leonida"}, "publisher": {"@type": "Organization", "name": "Dakra Studio", "url": "https://dakrastudio.com/"}}
    html = head(f"{n['titulo']} · Guía Leonida", n["resumen"], ruta, jsonld, tipo="article") + cuerpo_abre()
    html += f"""<main>
  <div class="band"><div class="wrap">
    <div class="crumbs"><a href="{R}/">Guía Leonida</a> › <a href="{R}/noticias/">Noticias</a></div>
    <h1>{e(n['titulo'])}</h1>
    <div class="tagline"><span class="pill lbl-{e(n['etiqueta'])}">{e(n['etiqueta'])}</span><span class="pill">{fecha(n['fecha'])}</span></div>
  </div></div>
  <div class="wrap article">
    <article class="prose">{aviso}<p class="lead">{e(n['resumen'])}</p>{cuerpo}{('<div class="sources">Fuentes: ' + fuentes + '</div>') if fuentes else ''}</article>
    <aside class="side">{lateral}</aside>
  </div>
</main>
"""
    html += pie()
    escribir(ruta, html)

def indice_noticias():
    lista = "".join(item_noticia(n) for n in noticias) or '<p class="empty">Muy pronto.</p>'
    html = head("Noticias de GTA 6 en español · Guía Leonida", "Las últimas noticias de GTA 6 y GTA 6 Online en español, marcadas como confirmadas, descubiertas por jugadores o rumores.", "/noticias/") + cuerpo_abre()
    html += f"""<main>
  <div class="band"><div class="wrap"><div class="crumbs"><a href="{R}/">Guía Leonida</a> › Noticias</div><h1>Noticias de GTA 6</h1><p>Todo lo nuevo de Leonida, cada día. Cada noticia dice si está confirmada, si la descubrieron los jugadores o si es un rumor.</p></div></div>
  <section><div class="wrap"><div class="newslist">{lista}</div></div></section>
</main>
"""
    html += pie()
    escribir("/noticias/", html)

# ---------------------------------------------------------------- herramienta y legales
def herramienta():
    vacia = not any(c.get("items") for c in colec.get("categorias", []))
    datos_json = json.dumps(colec, ensure_ascii=False).replace("</", "<\\/")
    if vacia:
        contenido = '<div class="pend"><b>Muy pronto</b>Aquí vas a poder marcar cada coche, coleccionable y logro de GTA 6. Se llena en cuanto haya listas verificadas del juego.</div>'
    else:
        contenido = f'<p>Llevas <b id="avance">0</b> completados. Tu avance se guarda en este teléfono o computadora.</p><div class="progress"><i id="barra"></i></div><div id="checklist"></div><script type="application/json" id="coleccionables-data">{datos_json}</script>'
    html = head("Mi progreso en GTA 6: coleccionables y logros · Guía Leonida", "Marca los coches, coleccionables y logros de GTA 6 que ya tienes. Gratis y en español.", "/herramientas/coleccionables/", noindex=vacia) + cuerpo_abre()
    html += f"""<main>
  <div class="band"><div class="wrap"><div class="crumbs"><a href="{R}/">Guía Leonida</a> › Herramientas</div><h1>Mi progreso en GTA 6</h1><p>Marca lo que ya conseguiste y ve cuánto te falta para el 100%.</p></div></div>
  <section><div class="wrap">{contenido}</div></section>
</main>
"""
    html += pie()
    escribir("/herramientas/coleccionables/", html)

def privacidad():
    html = head("Privacidad y avisos · Guía Leonida", "Política de privacidad, cookies, publicidad y enlaces de afiliado de Guía Leonida.", "/privacidad/") + cuerpo_abre()
    html += f"""<main>
  <div class="band"><div class="wrap"><div class="crumbs"><a href="{R}/">Guía Leonida</a> › Privacidad</div><h1>Privacidad y avisos</h1><p>Actualizado el {fecha(HOY)}.</p></div></div>
  <div class="wrap article"><article class="prose">
    <h2>Quiénes somos</h2><p>Guía Leonida es un sitio de fans de GTA 6 en español, hecho por Dakra Studio (Tennessee, EE. UU.). No está afiliado ni respaldado por Rockstar Games ni Take-Two Interactive. Contacto: dakrastudio@gmail.com.</p>
    <h2>Qué datos guardamos</h2><p>No pedimos registro ni guardamos tus datos personales. La herramienta "Mi progreso" guarda lo que marcas solo en tu propio navegador (almacenamiento local); nosotros no lo vemos.</p>
    <h2>Cookies y publicidad</h2><p>Podemos mostrar anuncios de Google AdSense. Google y sus socios pueden usar cookies para mostrar anuncios según tus visitas a este y otros sitios. Puedes desactivar los anuncios personalizados en <a href="https://adssettings.google.com" target="_blank" rel="noopener">la configuración de anuncios de Google</a>. Más información en <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener">cómo usa Google las cookies en publicidad</a>.</p>
    <h2>Enlaces de afiliado</h2><p>Algunos enlaces a tiendas, como Amazon, son de afiliado. Si compras a través de ellos podemos recibir una pequeña comisión sin costo extra para ti. Como afiliado de Amazon, ganamos con las compras que cumplan los requisitos.</p>
    <h2>Contenido</h2><p>Las guías se basan en fuentes públicas que citamos en cada página y en nuestras propias partidas. Marcamos como "rumor" lo que no está confirmado. Las marcas, nombres e imágenes de Grand Theft Auto pertenecen a sus dueños.</p>
  </article><aside class="side">{caja_redes()}</aside></div>
</main>
"""
    html += pie()
    escribir("/privacidad/", html)

# ---------------------------------------------------------------- sitemap y RSS
def sitemap_y_feed():
    urls = [("/", HOY), ("/noticias/", noticias[0]["fecha"] if noticias else HOY), ("/privacidad/", HOY)]
    urls += [(f"/guias/{g['slug']}/", g["actualizado"]) for g in publicadas]
    urls += [(f"/noticias/{n['slug']}/", n.get("actualizado", n["fecha"])) for n in noticias]
    if any(c.get("items") for c in colec.get("categorias", [])): urls.append(("/herramientas/coleccionables/", HOY))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{URL}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    (BASE / "sitemap.xml").write_text(sm)
    items = [(n["titulo"], f"/noticias/{n['slug']}/", n["fecha"], n["resumen"]) for n in noticias] + [(g["titulo"], f"/guias/{g['slug']}/", g["actualizado"], g["resumen"]) for g in publicadas]
    items.sort(key=lambda x: x[2], reverse=True)
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
    rss += f"<title>{e(cfg['nombre'])}</title><link>{URL}/</link><description>{e(cfg['descripcion'])}</description><language>es</language>\n"
    for t, u, d, r in items[:30]:
        dt = datetime.fromisoformat(d + "T12:00:00-06:00").strftime("%a, %d %b %Y %H:%M:%S -0600")
        rss += f"<item><title>{e(t)}</title><link>{URL}{u}</link><guid>{URL}{u}</guid><pubDate>{dt}</pubDate><description>{e(r)}</description></item>\n"
    rss += "</channel></rss>\n"
    (BASE / "feed.xml").write_text(rss)

# ---------------------------------------------------------------- limpieza de páginas viejas
def limpiar():
    for carpeta, vivos in (("guias", {g["slug"] for g in publicadas}), ("noticias", {n["slug"] for n in noticias})):
        raiz = BASE / carpeta
        if not raiz.exists(): continue
        for sub in raiz.iterdir():
            if sub.is_dir() and sub.name not in vivos and (sub / "index.html").exists():
                (sub / "index.html").unlink(); sub.rmdir()

if __name__ == "__main__":
    limpiar()
    portada()
    for g in publicadas: pagina_guia(g)
    indice_noticias()
    for n in noticias: pagina_noticia(n)
    herramienta()
    privacidad()
    sitemap_y_feed()
    print(f"Listo: {len(publicadas)} guías, {len(pronto)} bloqueadas, {len(noticias)} noticias. Lanzado: {LANZADO}.")
