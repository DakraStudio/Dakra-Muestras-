"""Agrega el asistente de chat de demostración de Dakra Studio a una muestra.

Uso: python3 tools/addchat.py <carpeta> <config.js>
El config.js define (en JavaScript): CFG = {name, color, color2, ink, bg, font, display, tel, telTxt, maps, address, H (horario por día, 0 = domingo, [abre, cierra] o null)},
INTENTS (lista {k, re, en(), es()}), CHIPS {en:[[k,texto]], es:[...]}, TXT {en:{hi,ph,fb}, es:{...}}.
El idioma del chat sigue a <html lang> de la página y se vuelve a dibujar al tocar cualquier botón de idioma.
"""
import sys
from pathlib import Path

CSS = """
/* ---- Asistente de chat (Dakra Studio) ---- */
.bot-btn{position:fixed;right:max(16px,env(safe-area-inset-right,0px));bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:60;border:0;cursor:pointer;background:var(--bc);color:#fff;font:700 15px var(--bf);padding:12px 18px;border-radius:999px;box-shadow:0 8px 24px rgba(0,0,0,.3);display:flex;align-items:center;gap:8px}
.bot-btn .ping{width:10px;height:10px;border-radius:50%;background:#7CFFB2;box-shadow:0 0 0 4px rgba(124,255,178,.3)}
.bot{position:fixed;right:max(16px,env(safe-area-inset-right,0px));bottom:calc(80px + env(safe-area-inset-bottom,0px));z-index:61;width:min(370px,calc(100vw - 32px));height:min(540px,calc(100vh - 140px));background:#fff;border-radius:18px;box-shadow:0 18px 50px rgba(0,0,0,.35);display:flex;flex-direction:column;overflow:hidden;border:2px solid var(--bi)}
.bot[hidden]{display:none}
.bot .bh{background:var(--bc2);color:#fff;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;gap:8px}
.bot .bh b{font:400 22px/1 var(--bd);display:block;color:#fff}
.bot .bh small{font:13px var(--bf);color:rgba(255,255,255,.85)}
.bot .x{background:none;border:0;color:#fff;font-size:26px;cursor:pointer;line-height:1;padding:2px 8px}
.bot .log{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:8px;background:var(--bb)}
.bm{max-width:86%;padding:9px 12px;border-radius:14px;font:15px/1.4 var(--bf);white-space:pre-line;color:var(--bi)}
.bm.b{background:#fff;border:1px solid rgba(0,0,0,.12);align-self:flex-start;border-bottom-left-radius:4px}
.bm.u{background:var(--bc);color:#fff;align-self:flex-end;border-bottom-right-radius:4px}
.bm a{color:var(--bc2);font-weight:700;text-decoration:underline}
.bot .chips2{display:flex;gap:6px;overflow-x:auto;padding:8px 10px;border-top:1px solid rgba(0,0,0,.1);background:#fff}
.bot .chips2 button{flex:none;border:1.5px solid var(--bi);background:#fff;border-radius:999px;padding:6px 12px;font:600 13px var(--bf);cursor:pointer;color:var(--bi)}
.bot form{display:flex;gap:8px;padding:10px;background:#fff;border-top:1px solid rgba(0,0,0,.1)}
.bot input{flex:1;min-width:0;border:1.5px solid rgba(0,0,0,.2);border-radius:10px;padding:10px 12px;font:16px var(--bf);color:var(--bi)}
.bot form button{border:0;background:var(--bc);color:#fff;font:700 14px var(--bf);border-radius:10px;padding:0 16px;cursor:pointer}
.bot .demo-tag{font:11px var(--bf);text-align:center;color:#666;padding:4px 0 8px;background:#fff}
@media(max-width:640px){.bot{height:min(500px,calc(100vh - 120px))}}
"""

ENGINE = r"""
(function(){
  const L=()=>(document.documentElement.lang||"").slice(0,2)==="en"?"en":"es";


  const DN={es:["domingo","lunes","martes","miércoles","jueves","viernes","sábado"],en:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]};
  const fmt=h=>{const hr=Math.floor(h),m=Math.round((h-hr)*60);return(((hr+11)%12)+1)+(m?":"+String(m).padStart(2,"0"):"")+(hr>=12?" pm":" am")};
  function now(){const p=new Intl.DateTimeFormat("en-US",{timeZone:"America/Chicago",weekday:"short",hour:"numeric",minute:"numeric",hour12:false}).formatToParts(new Date());const g=t=>p.find(x=>x.type===t).value;return{d:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].indexOf(g("weekday")),h:(parseInt(g("hour"),10)%24)+parseInt(g("minute"),10)/60}}
  window.STATUS=function(){const t=now(),r=CFG.H[t.d];
    if(r&&t.h>=r[0]&&t.h<r[1])return{en:`Yes, we're open right now ✅ until ${fmt(r[1])}.`,es:`¡Sí! Ahorita estamos abiertos ✅ hasta las ${fmt(r[1])}.`};
    let d=t.d,first=true;for(let i=0;i<8;i++){const x=CFG.H[d];if(x&&(!first||t.h<x[0]))break;d=(d+1)%7;first=false}
    const today=d===t.d;return{en:`We're closed right now. We open ${today?"today":DN.en[d]} at ${fmt(CFG.H[d][0])}.`,es:`Ahorita estamos cerrados. Abrimos ${today?"hoy":"el "+DN.es[d]} a las ${fmt(CFG.H[d][0])}.`}};
  window.HOURS=l=>[1,2,3,4,5,6,0].map(d=>{const r=CFG.H[d],n=DN[l][d];return `${n[0].toUpperCase()+n.slice(1)}: ${r?fmt(r[0])+" – "+fmt(r[1]):(l==="es"?"cerrado":"closed")}`}).join("\n");

  const log=document.getElementById("botLog"),HIST=[];
  const chipLabel=(k,l)=>{const c=CHIPS[l].find(x=>x[0]===k);return c?c[1]:null};
  function answer(q,k){const l=L();if(k){const it=INTENTS.find(i=>i.k===k);return it?it[l]():TXT[l].fb}const it=INTENTS.find(i=>i.re.test(q));return it?it[l]():TXT[l].fb}
  function bubble(w,h,t){const m=document.createElement("div");m.className="bm "+w;if(t)m.textContent=h;else m.innerHTML=h;log.appendChild(m)}
  function draw(){const l=L();log.innerHTML="";HIST.forEach(h=>{if(h.who==="hi")bubble("b",TXT[l].hi);else if(h.who==="u")bubble("u",h.k?(chipLabel(h.k,l)||h.q):h.q,true);else if(h.pending)bubble("b","…",true);else bubble("b",answer(h.q,h.k))});log.scrollTop=log.scrollHeight}
  function ask(q,k){HIST.push({who:"u",q,k});const r={who:"b",q,k,pending:true};HIST.push(r);draw();setTimeout(()=>{r.pending=false;draw()},450)}
  function chips(){const l=L();document.getElementById("botChips").innerHTML=CHIPS[l].map(([k,t])=>`<button type="button" data-k="${k}">${t}</button>`).join("");
    document.querySelectorAll("#botChips button").forEach(b=>b.addEventListener("click",()=>ask(b.textContent,b.dataset.k)));
    const i=document.getElementById("botIn");i.placeholder=TXT[l].ph;i.setAttribute("aria-label",TXT[l].ph);
    document.querySelectorAll(".bot-l").forEach(e=>e.textContent=e.dataset[l])}
  const bot=document.getElementById("bot"),btn=document.getElementById("botBtn");
  function open(o){bot.hidden=!o;btn.setAttribute("aria-expanded",o);if(o&&!HIST.length)HIST.push({who:"hi"});if(o)draw()}
  btn.addEventListener("click",()=>open(bot.hidden));
  document.getElementById("botX").addEventListener("click",()=>open(false));
  document.getElementById("botForm").addEventListener("submit",e=>{e.preventDefault();const i=document.getElementById("botIn"),q=i.value.trim();if(!q)return;i.value="";ask(q,null)});
  /* Cuando la página cambia de idioma, el chat también */
  new MutationObserver(()=>{chips();draw()}).observe(document.documentElement,{attributes:true,attributeFilter:["lang"]});
  chips();
})();
"""

def build(folder, cfgfile):
    page = Path(folder) / "index.html"
    s = page.read_text(encoding="utf-8")
    if 'id="botBtn"' in s:
        raise SystemExit("Esta muestra ya tiene asistente.")
    cfg = Path(cfgfile).read_text(encoding="utf-8")
    import re
    m = lambda k: re.search(k + r'\s*:\s*"([^"]*)"', cfg).group(1)
    vars_ = f':root{{--bc:{m("color")};--bc2:{m("color2")};--bi:{m("ink")};--bb:{m("bg")};--bf:{m("font")};--bd:{m("display")}}}'
    html = f"""
<button class="bot-btn" id="botBtn" type="button" aria-controls="bot" aria-expanded="false"><span class="ping" aria-hidden="true"></span><span class="bot-l" data-es="¿Preguntas? Chatea" data-en="Questions? Chat">¿Preguntas? Chatea</span></button>
<div class="bot" id="bot" role="dialog" aria-label="{m("name")} assistant" hidden>
  <div class="bh"><div><b>{m("name")}</b><small class="bot-l" data-es="Asistente · responde al instante" data-en="Assistant · instant answers">Asistente · responde al instante</small></div><button class="x" id="botX" type="button" aria-label="Cerrar">×</button></div>
  <div class="log" id="botLog" aria-live="polite"></div>
  <div class="chips2" id="botChips"></div>
  <form id="botForm"><input id="botIn" autocomplete="off" aria-label="Escribe tu pregunta"><button type="submit" class="bot-l" data-es="Enviar" data-en="Send">Enviar</button></form>
  <div class="demo-tag bot-l" data-es="Asistente de demostración creado por Dakra Studio" data-en="Demo assistant built by Dakra Studio">Asistente de demostración creado por Dakra Studio</div>
</div>
<script>
{cfg}
{ENGINE}
</script>
"""
    s = s.replace("</style>", vars_ + CSS + "</style>", 1)
    i = s.rindex("</body>")
    s = s[:i] + html + s[i:]
    page.write_text(s, encoding="utf-8")
    print("ok", page)

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
