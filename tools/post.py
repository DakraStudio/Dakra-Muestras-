"""Generador de imágenes de marca de Dakra Studio (1080x1080, para Facebook, Instagram y Nextdoor).

Uso: python3 tools/post.py publicacion.json salida.png

El JSON lleva "estilo" y sus textos:
  {"estilo":"frase", "etiqueta":"...", "titulo":"...", "texto":"..."}
  {"estilo":"pasos", "titulo":"...", "pasos":["...","..."], "nota":"..."}
  {"estilo":"chat",  "titulo":"...", "chat":[["cliente","..."],["bot","..."]], "nota":"..."}
Colores de la marca: azul marino #101B3B, cian #3DD6D0, blanco. Logo <D/>.
"""
import json, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = H = 1080
NAVY, NAVY2, PANEL = (16, 27, 59), (15, 26, 54), (29, 46, 92)
CYAN, WHITE, SOFT, AMBER = (61, 214, 208), (255, 255, 255), (169, 182, 218), (255, 201, 77)

def font(weight, size):
    for p in [f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf",
              f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if weight in ('Bold','ExtraBold','SemiBold') else ''}.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def block(d, x, y, text, f, fill, maxw, gap=1.18):
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=fill); y += int(f.size * gap)
    return y

def base():
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for gx in range(30, W, 44):
        for gy in range(30, H, 44):
            d.ellipse((gx-1.5, gy-1.5, gx+1.5, gy+1.5), fill=(34, 48, 92))
    d.rectangle((0, H-130, W, H), fill=NAVY2)
    lf = font("Bold", 46)
    d.text((64, H-92), "<D/>", font=lf, fill=CYAN)
    d.text((64 + d.textlength("<D/>", font=lf) + 20, H-90), "Dakra Studio", font=font("Bold", 42), fill=WHITE)
    sf = font("Medium", 30); s = "dakrastudio@gmail.com"
    d.text((W-64-d.textlength(s, font=sf), H-82), s, font=sf, fill=SOFT)
    return im, d

def frase(p):
    im, d = base(); y = 130
    if p.get("etiqueta"):
        ef = font("Bold", 30); tw = d.textlength(p["etiqueta"], font=ef)
        d.rounded_rectangle((64, y, 64+tw+44, y+58), 29, fill=CYAN)
        d.text((86, y+11), p["etiqueta"], font=ef, fill=NAVY); y += 110
    y = block(d, 64, y, p["titulo"], font("ExtraBold", 84), WHITE, W-128, 1.12) + 30
    d.rectangle((64, y, 160, y+8), fill=CYAN); y += 50
    block(d, 64, y, p.get("texto", ""), font("Medium", 40), SOFT, W-128, 1.4)
    return im

def pasos(p):
    im, d = base()
    y = block(d, 64, 110, p["titulo"], font("ExtraBold", 70), WHITE, W-128, 1.12) + 40
    nf, tf = font("Bold", 40), font("SemiBold", 38)
    for i, s in enumerate(p["pasos"], 1):
        lines = wrap(d, s, tf, W-128-110)
        h = max(96, 34 + len(lines)*48)
        d.rounded_rectangle((64, y, W-64, y+h), 22, fill=PANEL)
        d.ellipse((88, y+(h-64)//2, 152, y+(h+64)//2), fill=CYAN)
        n = str(i); d.text((120-d.textlength(n, font=nf)/2, y+(h-64)//2+8), n, font=nf, fill=NAVY)
        ty = y + (h - len(lines)*48)//2 - 2
        for ln in lines: d.text((178, ty), ln, font=tf, fill=WHITE); ty += 48
        y += h + 18
    if p.get("nota"): block(d, 64, y+10, p["nota"], font("Bold", 36), AMBER, W-128)
    return im

def chat(p):
    im, d = base()
    y = block(d, 64, 100, p["titulo"], font("ExtraBold", 66), WHITE, W-128, 1.12) + 36
    bf = font("Medium", 34)
    for who, t in p["chat"]:
        lines = wrap(d, t, bf, 640)
        bw = max(d.textlength(l, font=bf) for l in lines) + 56
        bh = len(lines)*44 + 36
        x = W-64-bw if who == "cliente" else 64
        fill, col = (CYAN, NAVY) if who == "cliente" else (PANEL, WHITE)
        d.rounded_rectangle((x, y, x+bw, y+bh), 26, fill=fill)
        ty = y + 16
        for l in lines: d.text((x+28, ty), l, font=bf, fill=col); ty += 44
        y += bh + 18
    if p.get("nota"): block(d, 64, y+14, p["nota"], font("Bold", 34), AMBER, W-128)
    return im

if __name__ == "__main__":
    p = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    {"frase": frase, "pasos": pasos, "chat": chat}[p["estilo"]](p).save(sys.argv[2], optimize=True)
    print(sys.argv[2])
