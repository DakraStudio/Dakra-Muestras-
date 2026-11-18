/* Guía Leonida · interacciones de la página (sin datos: el contenido viene en el HTML) */
(function () {
  const $ = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const LANZ = Date.parse(document.body.dataset.lanzamiento || "2026-11-19T00:00:00-06:00");

  /* Intro: una vez por visita, solo en la portada */
  const intro = $("#intro");
  if (intro) {
    let visto = false;
    try { visto = sessionStorage.getItem("gl-intro") === "1"; sessionStorage.setItem("gl-intro", "1"); } catch (e) {}
    if (visto || reduce) intro.style.display = "none";
    else { const out = () => intro.classList.add("out"); intro.addEventListener("click", out); setTimeout(out, 1900); }
  }

  /* HUD: hora, dinero que sube al bajar y estrellas */
  function hud() {
    const c = $("#clock"); if (!c) return;
    const d = new Date();
    c.textContent = String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
    const h = document.documentElement, pct = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight);
    $("#cash").textContent = "$" + String(Math.round(pct * 999999)).padStart(9, "0");
    const n = Math.min(5, Math.floor(pct * 6));
    $$("#stars span").forEach((s, i) => s.classList.toggle("on", i < n));
  }
  addEventListener("scroll", hud, { passive: true }); hud(); setInterval(hud, 15000);

  /* Cuenta regresiva o "ya disponible" */
  function cuenta() {
    const el = $("#count"); if (!el) return;
    const falta = LANZ - Date.now();
    if (falta > 0) {
      const d = Math.floor(falta / 864e5), h = Math.floor(falta / 36e5) % 24, m = Math.floor(falta / 6e4) % 60, s = Math.floor(falta / 1e3) % 60;
      const p = n => String(n).padStart(2, "0");
      el.innerHTML = [[d, "días"], [p(h), "horas"], [p(m), "min"], [p(s), "seg"]].map(([n, t]) => `<div><strong>${n}</strong><small>${t}</small></div>`).join("");
    } else {
      el.innerHTML = `<div class="live">LEONIDA ESTÁ ABIERTA · Guías nuevas cada día</div>`;
      const k = $("#kicker"); if (k) k.textContent = "Ya disponible en PS5 y Xbox Series";
      $$("[data-antes]").forEach(e => e.textContent = e.dataset.despues);
    }
  }
  cuenta(); setInterval(cuenta, 1000);

  /* Mapa de regiones */
  const REG = {
    vice: ["Vice City", "Sureste", "La gran ciudad de Leonida, inspirada en Miami: playas, luces de neón, hoteles Art Deco, Little Cuba y un puerto de cruceros.", [286, 250]],
    keys: ["Leonida Keys", "Sur", "Una cadena de islas tropicales al sur de Vice City, con pueblos pequeños y mucho viaje por agua.", [238, 378]],
    grassrivers: ["Grassrivers", "Suroeste", "Manglares inspirados en los Everglades. Caimanes, aerodeslizadores y cosas más raras escondidas entre el agua.", [222, 262]],
    gellhorn: ["Port Gellhorn", "Noroeste", "La costa olvidada de Leonida: moteles baratos, atracciones cerradas y centros comerciales vacíos alrededor de un puerto.", [112, 126]],
    ambrosia: ["Ambrosia", "Centro", "Pueblo industrial junto al Lago Leonida, dominado por la refinería de azúcar Allied Crystal y con presencia de motociclistas.", [246, 124]],
    kalaga: ["Mount Kalaga", "Norte", "Parque nacional en la frontera norte: bosque, caza, pesca y caminos para motos de montaña.", [186, 44]]
  };
  function region(k) {
    const info = $("#info"), r = REG[k]; if (!info || !r) return;
    $$(".reg").forEach(g => g.classList.toggle("on", g.dataset.r === k));
    const pin = $("#pin"); if (pin) pin.setAttribute("transform", `translate(${r[3][0] - 286} ${r[3][1] - 250})`);
    info.innerHTML = `<span class="tag">${r[1]} de Leonida</span><h3>${r[0]}</h3><p>${r[2]}</p>
      <p class="hint"><a href="${info.dataset.guia}">Ver la guía completa del mapa →</a></p>
      <div class="regbtns">${Object.entries(REG).map(([id, x]) => `<button class="chip ${id === k ? "on" : ""}" data-k="${id}">${x[0]}</button>`).join("")}</div>`;
    info.querySelectorAll(".chip").forEach(b => b.onclick = () => region(b.dataset.k));
  }
  $$(".reg").forEach(g => g.addEventListener("click", () => region(g.dataset.r)));
  region("vice");

  /* Filtro y búsqueda de guías */
  const lista = $("#lista");
  if (lista) {
    const cards = $$("#lista .card"), q = $("#q");
    const norm = s => (s || "").toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");
    let filtro = "Todas";
    const aplicar = () => {
      const t = norm(q ? q.value : ""); let vis = 0;
      cards.forEach(c => { const ok = (filtro === "Todas" || c.dataset.cat === filtro) && (!t || norm(c.textContent).includes(t)); c.hidden = !ok; if (ok) vis++; });
      const e = $("#vacio"); if (e) e.hidden = vis > 0;
    };
    $$("#chips .chip").forEach(b => b.onclick = () => { filtro = b.dataset.c; $$("#chips .chip").forEach(x => x.classList.toggle("on", x === b)); aplicar(); });
    if (q) q.addEventListener("input", aplicar);
  }

  /* Aviso al tocar una guía bloqueada */
  const toast = $("#toast");
  $$(".card.pronto").forEach(c => c.addEventListener("click", () => {
    if (!toast) return;
    toast.classList.add("on"); clearTimeout(toast._t); toast._t = setTimeout(() => toast.classList.remove("on"), 2200);
  }));

  /* Aparecer al bajar */
  const io = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .12 }) : null;
  $$(".reveal").forEach(el => io ? io.observe(el) : el.classList.add("in"));

  /* Herramienta de coleccionables: guarda el avance en este navegador */
  const box = $("#checklist"), datos = $("#coleccionables-data");
  if (box && datos) {
    let marcados = {};
    try { marcados = JSON.parse(localStorage.getItem("gl-coleccionables") || "{}"); } catch (e) {}
    const guardar = () => { try { localStorage.setItem("gl-coleccionables", JSON.stringify(marcados)); } catch (e) {} };
    const cats = JSON.parse(datos.textContent).categorias || [];
    const total = cats.reduce((n, c) => n + c.items.length, 0);
    const pintar = () => {
      const hechos = Object.values(marcados).filter(Boolean).length;
      $("#avance").textContent = `${hechos} de ${total}`;
      $("#barra").style.width = (total ? hechos / total * 100 : 0) + "%";
    };
    box.innerHTML = cats.map(c => `<div class="check-cat"><h2>${c.nombre}</h2>${c.items.map(it => {
      const id = c.id + ":" + it.id, on = !!marcados[id];
      return `<label class="check-item ${on ? "done" : ""}"><input type="checkbox" data-id="${id}" ${on ? "checked" : ""}><span><b>${it.nombre}</b><small>${it.donde || ""}</small></span></label>`;
    }).join("")}</div>`).join("");
    box.querySelectorAll("input").forEach(i => i.addEventListener("change", () => {
      marcados[i.dataset.id] = i.checked; i.closest(".check-item").classList.toggle("done", i.checked); guardar(); pintar();
    }));
    pintar();
  }
})();
