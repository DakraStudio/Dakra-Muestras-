# ColorBay Shop · cómo prender la nube

Mientras `config.js` esté vacío, la app funciona como demo (todo se guarda en el celular).

## 1. Crear el proyecto (una sola vez, gratis)
1. Entra a supabase.com y crea tu cuenta (puedes usar tu cuenta de GitHub de Dakra Studio).
2. **New project** → nombre `colorbay` → región **East US** → inventa una contraseña de base de datos y guárdala.
3. Espera 1 o 2 minutos a que termine de crearse.

## 2. Crear la base de datos
1. Menú izquierdo → **SQL Editor** → **New query**.
2. Pega todo el archivo `schema.sql` y toca **Run**. Debe decir "Success".

## 3. Ajustes de acceso
1. **Authentication → Sign In / Providers**: activa **Allow anonymous sign-ins** (así entran los trabajadores con código + PIN).
2. En **Email**: apaga **Confirm email** por ahora (si no, cada dueño tiene que confirmar su correo antes de entrar).
3. **Authentication → URL Configuration** → Site URL: `https://dakrastudio.com/colorbay/app.html`

## 4. Pasarle las llaves a Claude
**Project Settings → API Keys**. Copia:
- **Project URL** (`https://xxxx.supabase.co`)
- **Publishable key** (`sb_publishable_...`)

Nunca compartas la **secret key** ni la **service_role**.

## 5. Volverte administrador
1. Abre `dakrastudio.com/colorbay/admin.html` → escribe tu correo y una contraseña → **Crear mi cuenta de administrador**.
2. La página te muestra una línea de SQL: pégala en **SQL Editor** → **Run** → vuelve y toca **Ya lo hice**.

## Cosas a saber
- Plan gratis de Supabase: 500 MB de base de datos y 1 GB de fotos. Supabase pausa los proyectos gratis sin uso por 7 días, pero el robot `.github/workflows/colorbay-keepalive.yml` lo despierta cada 3 días, así que no se pausa ni en vacaciones.
- Cortesía = gratis de por vida. Suspendido = no puede entrar, pero sus datos se quedan guardados.
- "Descargar sus datos" baja órdenes y clientes; las fotos quedan en Supabase → Storage → photos → carpeta del taller.

## Encender el cobro con Stripe (cuando estés listo)

Todo ya está programado; solo está apagado. Mientras `config.js → stripe` esté vacío, nadie ve botones de pago.
**Nunca pegues la llave secreta de Stripe (sk_...) en config.js ni en ninguna página.** Solo va en los "Secrets" de Supabase.

1. **Crea tu cuenta en stripe.com** (gratis; cobran ~2.9% + 30¢ por pago). Empieza en *modo de prueba* (Test mode).
2. **Crea los productos** (Productos → Agregar producto), cada uno con precio *recurrente mensual*:
   Fundador $29 · Solo $35 · Taller $69 · Plus $99. Si quieres, agrega también precios anuales ($350, $690, $990).
   Copia el **ID de cada precio** (empieza con `price_...`).
3. **Crea un Payment Link por cada precio** (Payment Links → Nuevo). En "Después del pago" escoge
   *Redirigir a tu sitio* y pon: `https://dakrastudio.com/colorbay/app.html?paid=1`
   Copia cada enlace (`https://buy.stripe.com/...`) y pégalo en `config.js → stripe` (founder, solo, shop, plus…).
4. **Portal de clientes** (Configuración → Facturación → Portal de clientes): actívalo, permite cancelar, y copia
   el enlace de inicio de sesión del portal en `stripe.portal`.
5. **Sube la función del webhook a Supabase**: Edge Functions → *Deploy a new function* → *Via editor* →
   nombre `stripe-webhook` → pega el archivo `supabase/functions/stripe-webhook/index.ts` → Deploy.
   Luego en la función, en *Details*, **apaga "Enforce JWT verification"** (Stripe no manda esa llave).
6. **Guarda los secretos** (Edge Functions → Secrets):
   - `STRIPE_SECRET_KEY` = tu llave secreta de Stripe (`sk_test_...` para pruebas)
   - `PRICE_TIERS` = `{"price_FUNDADOR":"founder","price_SOLO":"solo","price_TALLER":"shop","price_PLUS":"plus"}`
     (cambia cada `price_...` por los tuyos; los anuales también, con el mismo nivel)
7. **Crea el webhook en Stripe** (Desarrolladores → Webhooks → Agregar destino):
   URL: `https://gjnkwxmkwuqrsbocigdw.supabase.co/functions/v1/stripe-webhook`
   Eventos: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`,
   `customer.subscription.deleted`, `invoice.paid`. Copia el *Signing secret* (`whsec_...`) y guárdalo en Supabase
   como `STRIPE_WEBHOOK_SECRET`.
8. **Prueba** con la tarjeta de prueba `4242 4242 4242 4242` (cualquier fecha futura y CVC). En el panel admin el taller
   debe pasar solo a "Pagado" y mostrar "Stripe: pagado hasta…". Cuando todo funcione, repite los pasos en modo real (Live).

Cómo funciona solo: el dueño toca "pagar" en Ajustes (o en la pantalla de prueba vencida) → paga en Stripe → Stripe avisa
al webhook → el taller queda **Pagado** con su nivel. Si cancela o falla el pago, sigue entrando hasta su fecha pagada
más 7 días de gracia; después se pausa, **sin borrar nada**, y se reactiva en cuanto vuelve a pagar.

## Términos y privacidad

- La página está en `legal.html` (inglés y español).
- Al registrarse hay que marcar la casilla, y **todos** (dueños y trabajadores) los aceptan al entrar a la app. Queda
  guardado en la tabla `consents` (quién, versión, fecha). En el panel admin ves si cada taller ya los aceptó.
- Si algún día cambias los términos: edita `legal.html`, cambia la fecha de versión ahí, en `app.html` (`TERMS_V`) e
  `info.html` (`TERMS_V`). La próxima vez que cada persona entre, se le piden de nuevo automáticamente.
- Los clientes de cada taller ven el enlace de privacidad al pie de cada estimado y factura en PDF.

## Promotores (afiliados) y comisiones

1. En el panel admin, pestaña **Promotores** → **+ Nuevo promotor**: nombre, cómo le pagas (Zelle, Cash App…) y el tipo:
   - **Pago fijo por taller**: por ejemplo $50 cuando el taller lleva 2 pagos.
   - **Porcentaje de cada pago**: por ejemplo 25% de cada mensualidad durante 12 meses.
   También decides cuántos **días gratis extra** gana el taller que use su código (por defecto 30).
2. Copia su **enlace** (`info.html?ref=CODIGO`) y mándaselo. Si un taller entra con ese enlace, el código se llena solo
   al registrarse. También lo pueden escribir a mano, o después en Ajustes → Plan (una sola vez).
3. Cada pago queda registrado: con Stripe se anota solo; si te pagan por Zelle o en efectivo, en la pestaña Talleres
   toca **Registrar pago recibido**. Con cada pago, la comisión se calcula sola.
4. En Promotores ves cuánto le debes a cada uno. Cuando le pagues, toca **Ya le pagué**. Con **Copiar su resumen**
   le mandas por mensaje cuántos talleres lleva y cuánto ha ganado.
