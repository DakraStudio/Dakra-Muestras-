// ColorBay Shop · Webhook de Stripe (Supabase Edge Function)
// Stripe avisa aquí cada vez que alguien paga, renueva o cancela, y esta función actualiza el taller solo.
//
// Secretos que necesita (Supabase → Edge Functions → Secrets). NUNCA van en config.js ni en la página:
//   STRIPE_SECRET_KEY      sk_live_... (o sk_test_... para pruebas)
//   STRIPE_WEBHOOK_SECRET  whsec_...   (lo da Stripe al crear el webhook)
//   PRICE_TIERS            {"price_xxx":"solo","price_yyy":"shop","price_zzz":"plus","price_fff":"founder"}
// SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY ya los pone Supabase automáticamente.
//
// Cada pago queda registrado en la tabla payments, y eso calcula solo la comisión del promotor (si lo hay).
// Importante: esta función nunca borra datos. Si alguien cancela o no paga, solo deja de estar al corriente
// (paid_until) y la app se pausa 7 días después de esa fecha. Al volver a pagar, se reactiva sola.

import Stripe from "npm:stripe@17";
import { createClient } from "npm:@supabase/supabase-js@2";

const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY") ?? "", { httpClient: Stripe.createFetchHttpClient() });
const crypto = Stripe.createSubtleCryptoProvider();
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

let TIERS: Record<string, string> = {};
try { TIERS = JSON.parse(Deno.env.get("PRICE_TIERS") ?? "{}"); } catch { TIERS = {}; }

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// Fecha hasta la que está pagado (sirve con versiones nuevas y viejas de la API de Stripe)
function periodEnd(sub: Stripe.Subscription): string | null {
  // deno-lint-ignore no-explicit-any
  const s = sub as any;
  const ts = s.current_period_end ?? s.items?.data?.[0]?.current_period_end ?? null;
  return ts ? new Date(ts * 1000).toISOString() : null;
}

function tierOf(sub: Stripe.Subscription): string | null {
  const price = sub.items?.data?.[0]?.price?.id;
  return price && TIERS[price] ? TIERS[price] : null;
}

// Pasa la información de la suscripción al taller
async function applySub(sub: Stripe.Subscription, shopId?: string | null) {
  const t = tierOf(sub);
  const patch: Record<string, unknown> = {
    stripe_sub: sub.id,
    stripe_customer: typeof sub.customer === "string" ? sub.customer : sub.customer?.id,
  };
  const active = ["active", "trialing", "past_due"].includes(sub.status);
  // Activo: pagado hasta el fin del periodo. Cancelado: se respeta lo que ya pagó (no se acorta ni se borra nada).
  const end = sub.status === "canceled" && sub.ended_at ? new Date(sub.ended_at * 1000).toISOString() : periodEnd(sub);
  if (end) patch.paid_until = end;
  if (active || sub.status === "canceled") {
    if (t === "founder") { patch.plan = "founder"; patch.tier = "shop"; }
    else { patch.plan = "paid"; if (t) patch.tier = t; }
  }
  let q = db.from("shops").update(patch);
  if (shopId && UUID.test(shopId)) q = q.eq("id", shopId);
  else q = q.eq("stripe_sub", sub.id);
  const { error } = await q;
  if (error) throw new Error("db: " + error.message);
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("ok");
  const sig = req.headers.get("stripe-signature");
  const body = await req.text();
  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(body, sig ?? "", Deno.env.get("STRIPE_WEBHOOK_SECRET") ?? "", undefined, crypto);
  } catch (e) {
    return new Response("firma inválida: " + (e as Error).message, { status: 400 });
  }

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const s = event.data.object as Stripe.Checkout.Session;
        const shopId = s.client_reference_id;
        if (!shopId || !UUID.test(shopId)) break; // pago que no viene de la app
        if (s.subscription) {
          const sub = await stripe.subscriptions.retrieve(typeof s.subscription === "string" ? s.subscription : s.subscription.id);
          await applySub(sub, shopId);
        }
        break;
      }
      case "customer.subscription.created":
      case "customer.subscription.updated":
      case "customer.subscription.deleted": {
        const sub = event.data.object as Stripe.Subscription;
        await applySub(sub, (sub.metadata?.shop_id as string) || null);
        break;
      }
      case "invoice.paid": {
        // deno-lint-ignore no-explicit-any
        const inv = event.data.object as any;
        const subId = inv.subscription ?? inv.parent?.subscription_details?.subscription;
        if (!subId) break;
        const sid = typeof subId === "string" ? subId : subId.id;
        await applySub(await stripe.subscriptions.retrieve(sid));
        // Registrar el pago: con esto se calculan solas las comisiones de los promotores
        const { data: shop } = await db.from("shops").select("id").eq("stripe_sub", sid).maybeSingle();
        if (!shop) throw new Error("taller aún no ligado a la suscripción"); // Stripe reintenta en unos minutos
        if ((inv.amount_paid ?? 0) > 0) {
          const { error } = await db.from("payments").upsert(
            { shop_id: shop.id, amount: inv.amount_paid / 100, paid_at: new Date((inv.status_transitions?.paid_at ?? inv.created) * 1000).toISOString(), source: "stripe", ext_id: inv.id },
            { onConflict: "ext_id", ignoreDuplicates: true });
          if (error) throw new Error("db: " + error.message);
        }
        break;
      }
    }
  } catch (e) {
    // Stripe reintenta solo si respondemos con error, así nunca se pierde un pago.
    return new Response("error: " + (e as Error).message, { status: 500 });
  }
  return new Response(JSON.stringify({ received: true }), { headers: { "content-type": "application/json" } });
});
