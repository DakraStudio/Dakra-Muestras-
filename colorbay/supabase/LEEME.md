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
- Plan gratis de Supabase: 500 MB de base de datos y 1 GB de fotos. Se pausa si nadie lo usa en 7 días (con un taller usándolo diario no pasa).
- Cortesía = gratis de por vida. Suspendido = no puede entrar, pero sus datos se quedan guardados.
- "Descargar sus datos" baja órdenes y clientes; las fotos quedan en Supabase → Storage → photos → carpeta del taller.
