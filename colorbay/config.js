// ColorBay Shop · conexión a la nube (Supabase)
// url:  Project URL  (https://xxxx.supabase.co)
// key:  Publishable key (sb_publishable_...). Es pública por diseño: la seguridad la ponen las reglas de la base de datos.
// NUNCA pongas aquí la "secret key" ni la "service_role" (ni de Supabase ni de Stripe).
// Mientras url y key estén vacíos, la app funciona en modo demo (todo se guarda en el celular).
window.COLORBAY_CONFIG = {
  url: "https://gjnkwxmkwuqrsbocigdw.supabase.co",
  key: "sb_publishable_SRY_mGOQSFon0_V9Htlkcg_fedkdDlD",

  // Cobro con Stripe (apagado). Para encenderlo, pega aquí los "Payment Links" de Stripe (https://buy.stripe.com/...).
  // Vacío = no aparece ningún botón de pago. Pasos completos en supabase/LEEME.md → "Encender el cobro con Stripe".
  stripe: {
    founder: "",   // Taller a precio de fundador · $29/mes
    solo:    "",   // Solo · $35/mes
    shop:    "",   // Taller · $69/mes
    plus:    "",   // Plus · $99/mes
    solo_y:  "",   // Solo anual · $350/año (opcional)
    shop_y:  "",   // Taller anual · $690/año (opcional)
    plus_y:  "",   // Plus anual · $990/año (opcional)
    portal:  ""    // Enlace del portal de clientes de Stripe (para ver o cancelar la suscripción)
  }
};
