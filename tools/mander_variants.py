"""Genera 3 variantes "rudas" de la muestra MANDER a partir de mander-store/index.html.
Uso: python3 tools/mander_variants.py
Crea mander-store/rudo-1/, rudo-2/ y rudo-3/ (cada una un index.html que usa ../img/).
"""
import re
from pathlib import Path

BASE = Path("mander-store/index.html").read_text(encoding="utf-8")

NOISE = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
# Máscara de "desgaste": agujeritos al azar para que la tinta se vea gastada
WORN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='w'%3E"
        "%3CfeTurbulence type='fractalNoise' baseFrequency='.55' numOctaves='2' seed='7'/%3E"
        "%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -2.6 0 0 0 2.05'/%3E%3C/filter%3E"
        "%3Crect width='100%25' height='100%25' filter='url(%23w)'/%3E%3C/svg%3E")

ROUGH_SVG = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="rough"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/></filter></svg>"""

# Base oscura común: invierte la paleta clara de la muestra original
DARK = f"""
/* ===== Base oscura (Dakra Studio) ===== */
:root{{--bone:#100f0e;--bone-2:#1c1a18;--ink:#efe8dc;--line:#34302c;--mute:#9b9087;--deep:#0a0908}}
body{{background:var(--bone);color:var(--ink)}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.07;background-image:url("{NOISE}")}}
main,header,footer{{position:relative;z-index:1}}
.demo{{background:#ffd34d;color:#111}} .demo a{{color:#111}} .demo b{{background:#111;color:#ffd34d}}
.bar{{background:rgba(16,15,14,.88);border-bottom:1px solid var(--line)}}
.sub,.info p,.steps span{{color:#b9ada2}}
.prod{{background:#191715;border-color:#2e2a27;box-shadow:none}}
.prod:hover{{box-shadow:none}}
.gal{{background:#e8e8e8}}
.thumbs{{background:#141211;border-top-color:#2e2a27}} .thumbs button{{background:#222}}
.sizes button{{background:transparent;border-color:#3b3632;color:var(--ink)}}
.sizes button:hover{{border-color:var(--ink)}}
.sizes button[aria-pressed=true]{{background:var(--ink);color:#100f0e}}
.btn.ink{{background:var(--ink);color:#100f0e}}
.btn.bone{{background:var(--ink);color:#100f0e}}
.dark{{background:#0b0a09;color:var(--ink)}}
.details figcaption{{background:#100f0e;color:var(--ink);border:1px solid #3b3632}}
.steps li{{background:#191715;border-color:#2e2a27}}
footer{{background:#080707;color:#8e847b}}
.drawer{{background:#141211}} .dh{{border-bottom-color:#2e2a27}} .dfoot{{border-top-color:#2e2a27}}
.items li{{border-bottom-color:#2e2a27}} .items img{{border-color:#3b3632}} .qty{{border-color:#3b3632}}
.co{{background:#100f0e}} .co-top{{border-bottom-color:#2e2a27}}
.panel{{background:#191715;border-color:#2e2a27}}
.f input,.f select{{background:#100f0e;border-color:#3b3632;color:var(--ink)}}
.f input[readonly]{{background:#1c1a18;color:#a9a097}}
.ship label{{border-color:#3b3632}} .ship label:has(input:checked){{border-color:var(--ink)}}
.stepper li{{background:#1c1a18;color:#7f766e}} .stepper li.on{{background:var(--ink);color:#100f0e}}
.sum li{{border-bottom-color:#2e2a27}} .sum img{{border-color:#3b3632}}
.toast{{background:var(--ink);color:#100f0e}}
.lang{{border-color:var(--ink)}} .lang button[aria-pressed=true]{{background:var(--ink);color:#100f0e}}
.ig{{background:#0b0a09}}
:root{{--bb:#141211;--bi:#efe8dc}}
.bot{{background:#141211;color:#efe8dc;border-color:#2e2a27}}
.bot .log .bm.b,.bot .bm.b{{background:#211e1b;color:#efe8dc;border-color:#2e2a27}}
.bot form input,#botIn{{background:#100f0e;color:#efe8dc;border-color:#3b3632}}
.bot .chips2 button{{background:transparent;color:#efe8dc;border-color:#3b3632}}
.bot .demo-tag{{color:#8e847b}}
.bot .chips2,.bot form,.bot .demo-tag{{background:#141211;border-top-color:#2e2a27}} .bm.b a{{color:#ff8a80}}
.worn{{-webkit-mask-image:url("{WORN}");mask-image:url("{WORN}");-webkit-mask-size:300px;mask-size:300px}}
"""

V = {}

# ---------- 1. CONCRETO: grafiti, cinta y concreto ----------
V["rudo-1"] = dict(
 name="Concreto",
 fonts="family=UnifrakturCook:wght@700&family=Archivo:wdth,wght@62..100,400..900",
 hero="""
  <section class="hero h1v" aria-label="MANDER">
    <div class="slab"></div>
    <div class="tape t1" aria-hidden="true"><span>MANDER ✦ MANDER ✦ MANDER ✦ MANDER ✦ MANDER ✦ MANDER ✦ MANDER ✦ MANDER ✦</span></div>
    <div class="tape t2" aria-hidden="true"><span>STREETWEAR ✦ STREETWEAR ✦ STREETWEAR ✦ STREETWEAR ✦ STREETWEAR ✦ STREETWEAR ✦</span></div>
    <div class="h1v-in">
      <div class="stamp" aria-hidden="true">
        <svg viewBox="0 0 400 400"><circle cx="200" cy="200" r="178" fill="none" stroke="#d11a1a" stroke-width="16"/><circle cx="200" cy="200" r="150" fill="none" stroke="#d11a1a" stroke-width="3" stroke-dasharray="2 9"/></svg>
        <svg class="m" viewBox="0 0 100 130"><use href="#mask"/></svg>
        <svg class="s s1"><use href="#spark"/></svg><svg class="s s2"><use href="#spark"/></svg><svg class="s s3"><use href="#spark"/></svg><svg class="s s4"><use href="#spark"/></svg>
      </div>
      <div class="copy">
        <h1 class="worn">Mander</h1>
        <p class="lead"><span class="t-es">Hecho para la calle. Rojo lavado, letras góticas y el pasamontañas.</span><span class="t-en">Made for the streets. Washed red, gothic letters and the ski mask.</span></p>
        <div class="cta">
          <a class="btn red jag" href="#shop"><span class="t-es">Comprar ahora</span><span class="t-en">Shop now</span></a>
          <a class="btn out jag" href="https://www.instagram.com/mander.store/" target="_blank" rel="noopener">@mander.store</a>
        </div>
      </div>
    </div>
    <div class="marquee" aria-hidden="true"><div id="mq"></div></div>
  </section>""",
 css=f"""
:root{{--wash:#d11a1a;--wash-hi:#ee2a2a}}
.h2{{color:var(--ink);transform:rotate(-1.5deg);display:inline-block;filter:url(#rough)}}
.h1v{{background:#121110;color:var(--ink);padding:48px 16px 0;text-align:left}}
.h1v .slab{{position:absolute;inset:0;z-index:-2;background:radial-gradient(45% 55% at 72% 45%,rgba(209,26,26,.28),transparent 70%),radial-gradient(30% 40% at 15% 85%,rgba(255,255,255,.05),transparent 70%),url("{NOISE}"),#121110;background-size:auto,auto,240px,auto;animation:wash 16s ease-in-out infinite alternate}}
.h1v-in{{position:relative;max-width:1100px;margin:0 auto;display:grid;grid-template-columns:.9fr 1.1fr;align-items:center;gap:24px;min-height:min(70vh,640px)}}
.stamp{{position:relative;width:min(80vw,420px);aspect-ratio:1;justify-self:center;transform:rotate(-10deg);filter:url(#rough);animation:thud .9s cubic-bezier(.2,1.4,.3,1) both}}
.stamp svg:first-child{{position:absolute;inset:0;width:100%;height:100%;animation:spin 50s linear infinite}}
.stamp .m{{position:absolute;left:50%;top:50%;width:42%;transform:translate(-50%,-52%);color:#efe8dc}}
.stamp .s{{position:absolute;width:9%;height:9%;color:#efe8dc;animation:twinkle 2.2s ease-in-out infinite}}
.s1{{left:20%;top:28%}} .s2{{left:72%;top:24%;animation-delay:.5s!important}} .s3{{left:74%;top:64%;animation-delay:1s!important}} .s4{{left:18%;top:66%;animation-delay:1.5s!important}}
.h1v h1{{font:700 clamp(84px,15vw,200px)/.8 var(--goth);color:var(--wash);transform:rotate(-4deg);margin:0 0 10px -6px;text-shadow:6px 6px 0 #000;animation:rise .9s .15s cubic-bezier(.2,.8,.2,1) both}}
.h1v .lead{{margin:22px 0 26px;color:#cfc4b8;max-width:34ch;font-weight:600}}
.h1v .cta{{justify-content:flex-start}}
.jag{{clip-path:polygon(0 8%,6% 0,30% 6%,52% 0,78% 5%,100% 0,97% 50%,100% 100%,70% 94%,45% 100%,20% 95%,0 100%,3% 52%);border-radius:0!important}}
.btn.out{{border-color:var(--ink);color:var(--ink)}}
.tape{{position:absolute;left:-10%;right:-10%;z-index:-1;background:#efe8dc;color:#121110;font:900 20px var(--body);font-stretch:68%;letter-spacing:.12em;padding:8px 0;white-space:nowrap;overflow:hidden;box-shadow:0 8px 20px rgba(0,0,0,.5);opacity:.92}}
.tape span{{display:inline-block;animation:slide 30s linear infinite}}
.t1{{top:22%;transform:rotate(-8deg)}} .t2{{bottom:24%;transform:rotate(5deg);background:var(--wash);color:#fff}}
.t2 span{{animation-direction:reverse}}
.marquee{{background:#efe8dc;border-color:#000;margin-top:40px;transform:rotate(-1deg);width:104%;margin-left:-2%}}
.marquee div{{color:#121110}} .marquee svg{{color:var(--wash)}}
.prod{{border:2px solid #2e2a27;border-radius:4px}}
.prod:hover{{transform:rotate(-.6deg) translateY(-3px);border-color:var(--wash)}}
.tagnew{{border-radius:2px;transform:rotate(-4deg)}}
.btn{{border-radius:4px}} .btn.red{{background:var(--wash)}}
.steps li{{border-radius:4px;transform:rotate(var(--r2,0deg))}} .steps li:nth-child(2){{--r2:1deg}} .steps li:nth-child(3){{--r2:-1deg}}
.steps li::before{{border-radius:2px;filter:url(#rough)}}
.details figure{{border-radius:2px;filter:grayscale(.15) contrast(1.08)}}
.ig .h2{{color:var(--wash);text-shadow:5px 5px 0 #000}}
@keyframes thud{{from{{opacity:0;transform:rotate(-30deg) scale(1.6)}}to{{opacity:1;transform:rotate(-10deg) scale(1)}}}}
@media (max-width:860px){{.t1{{top:9%}}.t2{{top:34%;bottom:auto}}.h1v-in{{grid-template-columns:1fr;text-align:center}}.h1v .cta{{justify-content:center}}.h1v .lead{{margin-inline:auto}}.stamp{{width:min(70vw,320px)}}}}
""")

# ---------- 2. PRECAUCIÓN: cinta de peligro, etiquetas y código de barras ----------
V["rudo-2"] = dict(
 name="Precaución",
 fonts="family=UnifrakturCook:wght@700&family=Anton&family=Archivo:wdth,wght@62..100,400..900",
 hero="""
  <section class="hero h2v" aria-label="MANDER">
    <div class="hz hz-t" aria-hidden="true"></div>
    <div class="h2v-in">
      <div class="big">
        <p class="kick">✦ <span class="t-es">Nuevo drop</span><span class="t-en">New drop</span> ✦</p>
        <h1><span class="ln">MAN</span><span class="ln">DER</span></h1>
        <p class="goth">Streetwear</p>
      </div>
      <div class="label" aria-hidden="true">
        <div class="lab-top"><span>MANDER</span><span>№ 01</span></div>
        <div class="lab-emb"><svg viewBox="0 0 400 400"><circle cx="200" cy="200" r="170" fill="none" stroke="#fff" stroke-width="12"/></svg><svg class="m" viewBox="0 0 100 130"><use href="#mask"/></svg><svg class="s s1"><use href="#spark"/></svg><svg class="s s2"><use href="#spark"/></svg><svg class="s s3"><use href="#spark"/></svg></div>
        <div class="bars"></div>
        <div class="lab-bot"><span>HANDLE WITH ATTITUDE</span></div>
      </div>
    </div>
    <p class="lead"><span class="t-es">Zip hoodies rojo lavado y playeras oversize. Sin rodeos: elige tu talla y paga con tarjeta.</span><span class="t-en">Washed red zip hoodies and oversized tees. No fuss: pick your size and pay by card.</span></p>
    <div class="cta">
      <a class="btn red" href="#shop"><span class="t-es">Comprar ahora</span><span class="t-en">Shop now</span></a>
      <a class="btn out" href="https://www.instagram.com/mander.store/" target="_blank" rel="noopener">@mander.store</a>
    </div>
    <div class="marquee" aria-hidden="true"><div id="mq"></div></div>
    <div class="hz hz-b" aria-hidden="true"></div>
  </section>""",
 css="""
:root{--wash:#e10600;--wash-hi:#ff1a14;--anton:'Anton',Impact,sans-serif}
.h2{font:400 clamp(52px,9vw,110px)/.9 var(--anton);text-transform:uppercase;letter-spacing:.01em}
.h2v{background:#0a0a0a;color:#fff;padding:0 16px;text-align:center}
.hz{height:26px;margin:0 -16px;background:repeating-linear-gradient(-45deg,#e10600 0 22px,#0a0a0a 22px 44px);background-size:62px 62px;animation:hz 1.6s linear infinite}
.hz-t{margin-bottom:34px}
@keyframes hz{to{background-position:62px 0}}
.h2v-in{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1.2fr .8fr;gap:30px;align-items:center;text-align:left}
.kick{font:800 14px var(--body);letter-spacing:.2em;color:var(--wash);text-transform:uppercase}
.h2v h1{font:400 clamp(110px,21vw,270px)/.82 var(--anton);letter-spacing:-.01em;margin:6px 0 0;position:relative}
.h2v h1 .ln{display:block;position:relative;animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.h2v h1 .ln:nth-child(2){animation-delay:.12s;color:transparent;-webkit-text-stroke:3px #fff}
.h2v h1 .ln::after{content:attr(data-t)}
.goth{font:700 clamp(40px,6vw,72px)/1 var(--goth);color:var(--wash);transform:rotate(-5deg);margin:-10px 0 0 8px}
.label{background:#f2f0ea;color:#0a0a0a;border:3px solid #0a0a0a;outline:3px solid #f2f0ea;padding:14px;transform:rotate(4deg);box-shadow:12px 12px 0 var(--wash);animation:pop .9s .2s cubic-bezier(.2,1.3,.3,1) both;max-width:340px;justify-self:center;width:100%}
.lab-top,.lab-bot{display:flex;justify-content:space-between;font:400 22px var(--anton);letter-spacing:.06em;border-bottom:3px solid #0a0a0a;padding-bottom:6px}
.lab-bot{border:0;border-top:3px solid #0a0a0a;padding:6px 0 0;font-size:14px;font-family:var(--body);font-weight:900;justify-content:center}
.lab-emb{position:relative;aspect-ratio:1;background:var(--wash);margin:12px 0;overflow:hidden}
.lab-emb svg:first-child{position:absolute;inset:6%;width:88%;height:88%}
.lab-emb .m{position:absolute;left:50%;top:50%;width:38%;transform:translate(-50%,-52%);color:#fff;animation:float 5s ease-in-out infinite}
.lab-emb .s{position:absolute;width:10%;height:10%;color:#fff;animation:twinkle 2s ease-in-out infinite}
.lab-emb .s1{left:18%;top:26%}.lab-emb .s2{left:72%;top:30%;animation-delay:.6s}.lab-emb .s3{left:70%;top:66%;animation-delay:1.2s}
.bars{height:44px;background:repeating-linear-gradient(90deg,#0a0a0a 0 3px,transparent 3px 5px,#0a0a0a 5px 6px,transparent 6px 10px,#0a0a0a 10px 14px,transparent 14px 16px);margin-bottom:8px}
.h2v .lead{max-width:44ch;margin:30px auto 24px;color:#d8d8d8;font-weight:600}
.btn{border-radius:0;text-transform:uppercase;letter-spacing:.06em;font-family:var(--anton);font-weight:400;font-size:18px}
.btn.red{background:var(--wash);box-shadow:5px 5px 0 #fff}
.btn.out{border:3px solid #fff}
.marquee{background:var(--wash);border:0;margin:40px -16px 0;transform:rotate(-2deg) scale(1.04)}
.marquee div{color:#fff;font-family:var(--anton);font-weight:400;letter-spacing:.1em;font-size:20px}
.marquee svg{color:#0a0a0a}
.prod{border:3px solid #f2f0ea;border-radius:0;background:#0f0f0f}
.prod:hover{transform:translate(-4px,-4px);box-shadow:8px 8px 0 var(--wash)}
.info h3{font-family:var(--anton);font-weight:400;text-transform:uppercase;letter-spacing:.03em;font-size:22px}
.price{font-family:var(--anton);font-weight:400;color:var(--wash)}
.info::after{content:"";display:block;height:26px;margin-top:4px;background:repeating-linear-gradient(90deg,#f2f0ea 0 2px,transparent 2px 4px,#f2f0ea 4px 7px,transparent 7px 9px,#f2f0ea 9px 10px,transparent 10px 13px);opacity:.5}
.tagnew{border-radius:0;background:#0a0a0a;color:#ffd34d;border:2px solid #ffd34d}
.sizes button{border-radius:0;font-family:var(--anton);font-weight:400}
.thumbs button{border-radius:0}
.steps li{border-radius:0;border:3px solid #f2f0ea}
.steps li::before{border-radius:0;font-family:var(--anton)}
.details figure{border-radius:0;border:3px solid #f2f0ea}
.details figcaption{border-radius:0;font-family:var(--anton);font-weight:400;letter-spacing:.05em;text-transform:uppercase}
.ig .h2{font-size:clamp(46px,9vw,110px)}
.dh h2,.done h3{font-family:var(--anton);font-weight:400;text-transform:uppercase}
.panel,.card,.stepper li,.f input,.ship label{border-radius:0!important}
@media (max-width:860px){.h2v-in{grid-template-columns:1fr;text-align:center}.goth{margin-left:0}.label{max-width:260px}}
""")

# ---------- 3. TINTA: estilo tatuaje flash, marco gótico y rayos ----------
V["rudo-3"] = dict(
 name="Tinta",
 fonts="family=UnifrakturCook:wght@700&family=Archivo:wdth,wght@62..100,400..900",
 hero="""
  <section class="hero h3v" aria-label="MANDER">
    <div class="dots" aria-hidden="true"></div>
    <div class="frame">
      <i class="c tl"></i><i class="c tr"></i><i class="c bl"></i><i class="c br"></i>
      <div class="emb" aria-hidden="true">
        <svg class="rays" viewBox="0 0 400 400"><g id="ray" fill="#b3120f"><path d="M200 200 L192 0 L208 0Z"/></g></svg>
        <svg class="ring" viewBox="0 0 400 400"><circle cx="200" cy="200" r="120" fill="#0d0b0a" stroke="#efe8dc" stroke-width="8"/><circle cx="200" cy="200" r="106" fill="none" stroke="#efe8dc" stroke-width="2"/></svg>
        <svg class="m" viewBox="0 0 100 130"><use href="#mask"/></svg>
        <svg class="s s1"><use href="#spark"/></svg><svg class="s s2"><use href="#spark"/></svg><svg class="s s3"><use href="#spark"/></svg><svg class="s s4"><use href="#spark"/></svg>
      </div>
      <h1>Mander</h1>
      <svg class="ribbon" viewBox="0 0 520 80" aria-hidden="true"><path d="M20 20 L60 14 L60 64 L20 70 L36 44Z M500 20 L460 14 L460 64 L500 70 L484 44Z" fill="#7a0c0a"/><path d="M60 8 Q260 -6 460 8 L460 62 Q260 48 60 62Z" fill="#b3120f" stroke="#efe8dc" stroke-width="3"/><text x="260" y="44" text-anchor="middle" font-family="Archivo,sans-serif" font-weight="900" font-size="22" letter-spacing="8" fill="#efe8dc">STREETWEAR</text></svg>
      <p class="lead"><span class="t-es">Tinta, calle y el pasamontañas. Ropa con carácter para quien no pide permiso.</span><span class="t-en">Ink, streets and the ski mask. Gear with character for those who don't ask permission.</span></p>
      <div class="cta">
        <a class="btn red" href="#shop"><span class="t-es">Comprar ahora</span><span class="t-en">Shop now</span></a>
        <a class="btn out" href="https://www.instagram.com/mander.store/" target="_blank" rel="noopener">@mander.store</a>
      </div>
    </div>
    <div class="marquee" aria-hidden="true"><div id="mq"></div></div>
  </section>""",
 css="""
:root{--wash:#b3120f;--wash-hi:#d01a16}
.h2{color:var(--ink);text-shadow:4px 4px 0 var(--wash)}
.h3v{background:#0d0b0a;color:var(--ink);padding:36px 16px 0}
.dots{position:absolute;inset:0;z-index:-1;background:radial-gradient(circle,#2a2522 1.2px,transparent 1.6px) 0 0/14px 14px;-webkit-mask-image:radial-gradient(70% 60% at 50% 45%,transparent 30%,#000 100%);mask-image:radial-gradient(70% 60% at 50% 45%,transparent 30%,#000 100%)}
.frame{position:relative;max-width:760px;margin:0 auto;padding:34px 18px 34px;border:3px solid var(--ink);outline:1px solid var(--ink);outline-offset:6px}
.frame .c{position:absolute;width:22px;height:22px;background:var(--wash);border:3px solid var(--ink);transform:rotate(45deg)}
.c.tl{left:-13px;top:-13px}.c.tr{right:-13px;top:-13px}.c.bl{left:-13px;bottom:-13px}.c.br{right:-13px;bottom:-13px}
.emb{position:relative;width:min(70vw,360px);aspect-ratio:1;margin:0 auto;animation:pop 1s cubic-bezier(.2,1.3,.3,1) both}
.emb svg{position:absolute;inset:0;width:100%;height:100%}
.rays{animation:spin 70s linear infinite;opacity:.9}
.emb .m{inset:auto;left:50%;top:50%;width:30%;height:auto;transform:translate(-50%,-52%);color:var(--ink)}
.emb .s{width:8%;height:8%;inset:auto;color:var(--ink);animation:twinkle 2.4s ease-in-out infinite}
.emb .s1{left:30%;top:33%}.emb .s2{left:63%;top:32%;animation-delay:.6s}.emb .s3{left:64%;top:60%;animation-delay:1.2s}.emb .s4{left:29%;top:60%;animation-delay:1.8s}
.h3v h1{font:700 clamp(80px,15vw,170px)/.85 var(--goth);color:var(--ink);text-shadow:5px 5px 0 var(--wash),10px 10px 0 #000;margin-top:-18px;animation:rise .9s .2s cubic-bezier(.2,.8,.2,1) both}
.ribbon{width:min(90%,420px);margin:6px auto 0;display:block}
.h3v .lead{color:#cfc4b8;margin:16px auto 22px}
.btn.out{border-color:var(--ink);color:var(--ink)}
.btn.red{background:var(--wash);border:2px solid var(--ink)}
.marquee{background:#0d0b0a;border-color:var(--ink);margin-top:44px}
.marquee div{color:var(--ink);font-family:var(--goth);font-weight:700;letter-spacing:.04em;font-size:24px}
.marquee svg{color:var(--wash)}
.prod{border:3px double var(--ink);border-radius:6px;outline:1px solid #3b3632;outline-offset:4px}
.prod:hover{transform:translateY(-4px);box-shadow:0 0 0 2px var(--wash)}
.info h3{font:700 24px/1 var(--goth);letter-spacing:.01em}
.tagnew{background:var(--ink);color:#0d0b0a;border-radius:2px}
.steps li{border:3px double var(--ink)}
.steps li::before{background:transparent;color:var(--ink);border:2px solid var(--ink);box-shadow:3px 3px 0 var(--wash)}
.details figure{border:3px double var(--ink);border-radius:4px}
.details img{filter:contrast(1.1) saturate(.95)}
.ig .h2{text-shadow:5px 5px 0 var(--wash),10px 10px 0 #000}
@media (max-width:600px){.frame{padding:24px 10px}}
""")


def build(folder, v):
    s = BASE
    # fuentes
    s = re.sub(r'<link href="https://fonts.googleapis.com/css2\?[^"]+" rel="stylesheet">',
               f'<link href="https://fonts.googleapis.com/css2?{v["fonts"]}&display=swap" rel="stylesheet">', s, count=1)
    s = s.replace("<title>MANDER · Streetwear</title>", f'<title>MANDER · Streetwear · Diseño {v["name"]}</title>', 1)
    # portada
    a = s.index('<section class="hero"')
    b = s.index("</section>", a) + len("</section>")
    s = s[:a] + v["hero"].strip() + s[b:]
    # estilos: base oscura + variante, al final del <style>
    i = s.index("</style>")
    s = s[:i] + DARK + v["css"] + "\n" + s[i:]
    # filtro áspero
    s = s.replace("<body>", "<body>\n" + ROUGH_SVG, 1)
    # rayos de la variante 3 (24 rayos)
    if folder == "rudo-3":
        rays = "".join(f'<use href="#ray" transform="rotate({k*15} 200 200)"/>' for k in range(1, 24))
        s = s.replace('<path d="M200 200 L192 0 L208 0Z"/></g>', '<path d="M200 200 L192 0 L208 0Z"/></g>' + rays, 1)
    # rutas de imágenes
    s = s.replace('src="img/', 'src="../img/').replace('data-src="img/', 'data-src="../img/')
    out = Path("mander-store") / folder / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding="utf-8")
    print("ok", out)


if __name__ == "__main__":
    for k, v in V.items():
        build(k, v)
