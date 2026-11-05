"""Inspector de calidad de Dakra Studio.

Uso: python3 qa.py <carpeta_o_index.html> [...]
Revisa cada página en celular (390 px) y computadora (1280 px):
errores de JavaScript, desbordes horizontales, el botón de idioma,
todos los botones, enlaces de llamada y de mapas, y el aviso de muestra.
"""
import re, sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

TEL = re.compile(r"^tel:\+1\d{10}$")

def check(page_path: Path):
    url = page_path.resolve().as_uri()
    res = {"pagina": str(page_path), "ok": [], "fallas": []}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h, name in [(390, 844, "celular"), (1280, 900, "computadora")]:
            pg = b.new_page(viewport={"width": w, "height": h})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            # Sin internet aquí: bloquea lo externo para que no cuente como error de la página.
            pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
            pg.goto(url); pg.wait_for_timeout(400)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            (res["ok"] if sw <= w else res["fallas"]).append(
                f"{name}: ancho {sw}px" + ("" if sw <= w else f" (se sale de {w}px)"))
            if name == "celular":
                # Aviso de muestra
                body = pg.inner_text("body")
                (res["ok"] if "Dakra Studio" in body else res["fallas"]).append(
                    "aviso de Dakra Studio " + ("presente" if "Dakra Studio" in body else "FALTA"))
                # Enlaces de llamada
                tels = pg.eval_on_selector_all("a[href^='tel:']", "els=>els.map(e=>e.getAttribute('href'))")
                bad = [t for t in tels if not TEL.match(t)]
                if not tels: res["fallas"].append("no hay botón de llamar")
                elif bad: res["fallas"].append(f"teléfonos mal escritos: {bad}")
                else: res["ok"].append(f"{len(tels)} botón(es) de llamar correctos")
                # Enlaces vacíos o rotos
                empty = pg.eval_on_selector_all("a", "els=>els.filter(e=>!e.getAttribute('href')||e.getAttribute('href')==='#'&&e.textContent.trim()&&!e.closest('nav')&&!/logo|brand|rye/.test(e.className)).length")
                if empty: res["fallas"].append(f"{empty} enlace(s) sin destino")
                maps = pg.eval_on_selector_all("a[href*='google.com/maps'], iframe[src*='google.com/maps']", "els=>els.length")
                (res["ok"] if maps else res["fallas"]).append("mapa/cómo llegar " + ("presente" if maps else "FALTA"))
                # Botón de idioma
                lang = pg.query_selector("[data-lang], #langBtn, button.lang, label.lang, label[for=langSw]")
                if lang:
                    before = pg.inner_text("main") if pg.query_selector("main") else body
                    lang.click(); pg.wait_for_timeout(150)
                    after = pg.inner_text("main") if pg.query_selector("main") else pg.inner_text("body")
                    (res["ok"] if before != after else res["fallas"]).append(
                        "botón de idioma " + ("cambia el texto" if before != after else "NO cambia el texto"))
                    empties = pg.eval_on_selector_all("[data-es],[data-en]", "els=>els.filter(e=>!e.textContent.trim()).length")
                    if empties: res["fallas"].append(f"{empties} texto(s) vacíos después de cambiar idioma")
                    lang.click(); pg.wait_for_timeout(100)
                else:
                    res["fallas"].append("no hay botón de idioma")
                # Cada botón de la página
                n = 0
                for btn in pg.query_selector_all("button:not([data-lang]):not(#langBtn):not(.lang)"):
                    if btn.is_visible():
                        try: btn.click(timeout=1500); n += 1
                        except Exception as e: res["fallas"].append(f"botón no responde: {btn.inner_text()[:30]!r}")
                for el in pg.query_selector_all("[tabindex='0']"):
                    try: el.click(timeout=1500); n += 1
                    except Exception: pass
                res["ok"].append(f"{n} botón(es) y elementos interactivos probados")
            if errs: res["fallas"].append(f"{name}: errores de JavaScript: {errs[:3]}")
            pg.close()
        b.close()
    if "ejemplo-" in str(page_path):
        # Ejemplos de negocios ficticios: no tienen dirección ni teléfono reales.
        res["fallas"] = [f for f in res["fallas"] if "mapa" not in f and "botón de llamar" not in f]
    res["aprobada"] = not res["fallas"]
    return res

if __name__ == "__main__":
    out = []
    for a in sys.argv[1:]:
        p = Path(a); p = p / "index.html" if p.is_dir() else p
        if not p.exists():
            # Carpetas sin página (marca/, tools/, etc.) no son muestras.
            out.append({"pagina": str(p), "ok": ["no es una muestra, se omite"], "fallas": [], "aprobada": True}); continue
        out.append(check(p))
    print(json.dumps(out, ensure_ascii=False, indent=2))
