-- =====================================================================
-- ColorBay Shop · base de datos en la nube (Supabase)
-- Cómo usarlo: Supabase → SQL Editor → New query → pega TODO esto → Run.
-- Se puede volver a correr sin romper nada.
-- =====================================================================

create extension if not exists pgcrypto with schema extensions;

-- ---------- Tablas ----------
create table if not exists public.platform_admins(
  user_id uuid primary key references auth.users(id) on delete cascade
);

create table if not exists public.shops(
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  owner_id    uuid not null references auth.users(id) on delete cascade,
  owner_email text,
  phone       text,
  join_code   text not null unique default upper(substr(md5(gen_random_uuid()::text),1,6)),
  plan        text not null default 'trial' check (plan in ('trial','paid','founder','courtesy')),
  status      text not null default 'active' check (status in ('active','suspended')),
  trial_ends  timestamptz not null default now() + interval '60 days',
  notes       text,
  created_at  timestamptz not null default now()
);
alter table public.shops add column if not exists tier text not null default 'shop';
do $$ begin alter table public.shops add constraint shops_tier_chk check (tier in ('solo','shop','plus'));
exception when duplicate_object then null; end $$;
-- Términos aceptados por el dueño y datos de cobro con Stripe (se llenan solos)
alter table public.shops add column if not exists terms_version   text;
alter table public.shops add column if not exists terms_at        timestamptz;
alter table public.shops add column if not exists stripe_customer text;
alter table public.shops add column if not exists stripe_sub      text;
alter table public.shops add column if not exists paid_until      timestamptz;
-- Código del promotor que recomendó al taller
alter table public.shops add column if not exists ref_code        text;
alter table public.shops add column if not exists ref_at          timestamptz;
alter table public.shops add column if not exists admin_seen_at   timestamptz;   -- cuándo lo revisaste en el panel

create table if not exists public.workers(
  id         uuid primary key default gen_random_uuid(),
  shop_id    uuid not null references public.shops(id) on delete cascade,
  name       text not null,
  role       text not null check (role in ('owner','tech','painter')),
  pin_hash   text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.members(
  user_id    uuid not null references auth.users(id) on delete cascade,
  shop_id    uuid not null references public.shops(id) on delete cascade,
  worker_id  uuid not null references public.workers(id) on delete cascade,
  role       text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, shop_id)
);

create table if not exists public.shop_data(
  shop_id    uuid primary key references public.shops(id) on delete cascade,
  doc        jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.orders(
  shop_id    uuid not null references public.shops(id) on delete cascade,
  id         text not null,
  doc        jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (shop_id, id)
);

-- Precios de cada orden (estimado, pagos, costos) separados, para poder esconderlos a técnicos y pintores.
create table if not exists public.order_money(
  shop_id    uuid not null references public.shops(id) on delete cascade,
  id         text not null,
  doc        jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (shop_id, id)
);

-- Papelera: lo borrado se guarda 30 días y el dueño lo puede recuperar.
create table if not exists public.trash(
  id         uuid primary key default gen_random_uuid(),
  shop_id    uuid not null references public.shops(id) on delete cascade,
  kind       text not null,
  label      text,
  item       jsonb not null,
  deleted_by uuid,
  deleted_at timestamptz not null default now()
);

create table if not exists public.join_fails(
  shop_id uuid not null references public.shops(id) on delete cascade,
  at      timestamptz not null default now()
);

-- ---------- Funciones de permiso ----------
create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from platform_admins where user_id = auth.uid())
$$;

create or replace function public.my_role(s uuid) returns text
language sql stable security definer set search_path = public as $$
  select role from members where shop_id = s and user_id = auth.uid()
$$;

-- El taller está abierto si está activo; si es prueba, que no haya vencido;
-- si paga con Stripe, que su pago siga al corriente (con 7 días de gracia). Nunca se borra nada.
create or replace function public.shop_open(s uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from shops where id = s and status = 'active'
                and (plan <> 'trial' or trial_ends > now())
                and (plan not in ('paid','founder') or paid_until is null or paid_until + interval '7 days' > now()))
$$;

create or replace function public.can_use(s uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select (public.my_role(s) is not null and public.shop_open(s)) or public.is_admin()
$$;

-- ¿Esta persona puede ver precios? Dueño siempre; técnico o pintor solo si el dueño lo permite.
create or replace function public.money_ok(s uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select public.can_use(s) and (
    public.is_admin() or public.my_role(s) = 'owner'
    or (public.my_role(s) = 'tech'    and coalesce((select (doc->'settings'->>'techPrices')::boolean    from shop_data where shop_id = s), false))
    or (public.my_role(s) = 'painter' and coalesce((select (doc->'settings'->>'painterPrices')::boolean from shop_data where shop_id = s), false)))
$$;

-- ---------- Seguridad por fila ----------
alter table public.platform_admins enable row level security;
alter table public.shops           enable row level security;
alter table public.workers         enable row level security;
alter table public.members         enable row level security;
alter table public.shop_data       enable row level security;
alter table public.orders          enable row level security;
alter table public.join_fails      enable row level security;
alter table public.order_money     enable row level security;
alter table public.trash           enable row level security;

drop policy if exists shops_read   on public.shops;
drop policy if exists shops_admin  on public.shops;
drop policy if exists members_read on public.members;
drop policy if exists workers_read on public.workers;
drop policy if exists data_read    on public.shop_data;
drop policy if exists data_write   on public.shop_data;
drop policy if exists orders_read  on public.orders;
drop policy if exists orders_ins   on public.orders;
drop policy if exists orders_upd   on public.orders;
drop policy if exists orders_del   on public.orders;
drop policy if exists money_read   on public.order_money;
drop policy if exists money_ins    on public.order_money;
drop policy if exists money_upd    on public.order_money;
drop policy if exists money_del    on public.order_money;
drop policy if exists trash_read   on public.trash;
drop policy if exists trash_ins    on public.trash;
drop policy if exists trash_del    on public.trash;

create policy shops_read   on public.shops     for select using (public.my_role(id) is not null or public.is_admin());
create policy shops_admin  on public.shops     for update using (public.is_admin()) with check (public.is_admin());
create policy members_read on public.members   for select using (user_id = auth.uid() or public.is_admin());
create policy workers_read on public.workers   for select using (public.can_use(shop_id));
create policy data_read    on public.shop_data for select using (public.can_use(shop_id));
create policy data_write   on public.shop_data for update using (public.can_use(shop_id)) with check (public.can_use(shop_id));
create policy orders_read  on public.orders    for select using (public.can_use(shop_id));
create policy orders_ins   on public.orders    for insert with check (public.can_use(shop_id));
create policy orders_upd   on public.orders    for update using (public.can_use(shop_id)) with check (public.can_use(shop_id));
create policy orders_del   on public.orders    for delete using (public.can_use(shop_id) and public.my_role(shop_id) = 'owner');
create policy money_read   on public.order_money for select using (public.money_ok(shop_id));
create policy money_ins    on public.order_money for insert with check (public.money_ok(shop_id));
create policy money_upd    on public.order_money for update using (public.money_ok(shop_id)) with check (public.money_ok(shop_id));
create policy money_del    on public.order_money for delete using (public.money_ok(shop_id) and (public.my_role(shop_id) = 'owner' or public.is_admin()));
create policy trash_read   on public.trash for select using (public.can_use(shop_id) and (public.my_role(shop_id) = 'owner' or public.is_admin()));
create policy trash_ins    on public.trash for insert with check (public.can_use(shop_id));
create policy trash_del    on public.trash for delete using (public.can_use(shop_id) and (public.my_role(shop_id) = 'owner' or public.is_admin()));

-- Nadie puede leer el PIN cifrado desde la app.
revoke select on public.workers from anon, authenticated;
grant  select (id, shop_id, name, role, created_at) on public.workers to authenticated;
revoke all on public.join_fails, public.platform_admins from anon, authenticated;

-- ---------- Acciones (RPC) ----------
-- Crear el taller del dueño (lo usa el registro de prueba gratis).
create or replace function public.create_shop(p_name text, p_owner text, p_pin text, p_phone text default null)
returns uuid language plpgsql security definer set search_path = public, extensions as $$
declare s uuid; w uuid; em text;
begin
  if auth.uid() is null then raise exception 'not_signed_in'; end if;
  if coalesce((auth.jwt() ->> 'is_anonymous')::boolean, false) then raise exception 'anonymous_not_allowed'; end if;
  if p_pin !~ '^[0-9]{4}$' then raise exception 'bad_pin'; end if;
  select shop_id into s from members where user_id = auth.uid() and role = 'owner' limit 1;
  if s is not null then return s; end if;
  select email into em from auth.users where id = auth.uid();
  insert into shops(name, owner_id, owner_email, phone) values (p_name, auth.uid(), em, p_phone) returning id into s;
  insert into workers(shop_id, name, role, pin_hash) values (s, p_owner, 'owner', crypt(p_pin, gen_salt('bf'))) returning id into w;
  insert into members(user_id, shop_id, worker_id, role) values (auth.uid(), s, w, 'owner');
  insert into shop_data(shop_id, doc) values (s, jsonb_build_object(
    'settings',  jsonb_build_object('shop', p_name, 'rate', 55, 'paintRate', 45, 'tax', 9.75, 'theme', 'auto'),
    'customers', '[]'::jsonb,
    'paint',     jsonb_build_object('library', '[]'::jsonb, 'mixes', '[]'::jsonb, 'stock', '[]'::jsonb)));
  return s;
end $$;

-- Un trabajador entra con el código del taller y su PIN.
-- Devuelve un error en vez de fallar, para poder contar los intentos.
create or replace function public.join_shop(p_code text, p_pin text)
returns json language plpgsql security definer set search_path = public, extensions as $$
declare s shops; w workers;
begin
  if auth.uid() is null then return json_build_object('error', 'not_signed_in'); end if;
  select * into s from shops where join_code = upper(trim(p_code));
  if s.id is null then return json_build_object('error', 'bad_code'); end if;
  if (select count(*) from join_fails where shop_id = s.id and at > now() - interval '15 minutes') >= 20 then
    return json_build_object('error', 'too_many_attempts');
  end if;
  select * into w from workers where shop_id = s.id and role <> 'owner' and pin_hash = crypt(p_pin, pin_hash) limit 1;
  if w.id is null then
    insert into join_fails(shop_id) values (s.id);
    return json_build_object('error', 'bad_pin');
  end if;
  if not public.shop_open(s.id) then return json_build_object('error', 'shop_closed'); end if;
  insert into members(user_id, shop_id, worker_id, role) values (auth.uid(), s.id, w.id, w.role)
    on conflict (user_id, shop_id) do update set worker_id = excluded.worker_id, role = excluded.role;
  return json_build_object('shop_id', s.id, 'worker_id', w.id, 'role', w.role);
end $$;

create or replace function public.add_worker(p_shop uuid, p_name text, p_role text, p_pin text)
returns uuid language plpgsql security definer set search_path = public, extensions as $$
declare w uuid;
begin
  if public.my_role(p_shop) is distinct from 'owner' or not public.shop_open(p_shop) then raise exception 'not_allowed'; end if;
  if p_role not in ('tech', 'painter') then raise exception 'bad_role'; end if;
  if p_pin !~ '^[0-9]{4}$' then raise exception 'bad_pin'; end if;
  if exists(select 1 from workers where shop_id = p_shop and pin_hash = crypt(p_pin, pin_hash)) then raise exception 'pin_taken'; end if;
  -- Límite de personas por nivel: Solo = solo el dueño, Taller = 5, Plus = sin límite.
  if (select tier from shops where id = p_shop) = 'solo' then raise exception 'limit_reached'; end if;
  if (select tier from shops where id = p_shop) = 'shop' and (select count(*) from workers where shop_id = p_shop) >= 5 then raise exception 'limit_reached'; end if;
  insert into workers(shop_id, name, role, pin_hash) values (p_shop, p_name, p_role, crypt(p_pin, gen_salt('bf'))) returning id into w;
  return w;
end $$;

create or replace function public.update_worker(p_shop uuid, p_worker uuid, p_name text, p_role text, p_pin text default null)
returns void language plpgsql security definer set search_path = public, extensions as $$
declare cur text;
begin
  if public.my_role(p_shop) is distinct from 'owner' then raise exception 'not_allowed'; end if;
  select role into cur from workers where id = p_worker and shop_id = p_shop;
  if cur is null then raise exception 'not_found'; end if;
  if cur <> 'owner' and p_role not in ('tech', 'painter') then raise exception 'bad_role'; end if;
  if p_pin is not null and p_pin <> '' then
    if p_pin !~ '^[0-9]{4}$' then raise exception 'bad_pin'; end if;
    if exists(select 1 from workers where shop_id = p_shop and id <> p_worker and pin_hash = crypt(p_pin, pin_hash)) then raise exception 'pin_taken'; end if;
    update workers set pin_hash = crypt(p_pin, gen_salt('bf')) where id = p_worker;
  end if;
  update workers set name = coalesce(nullif(trim(p_name), ''), name), role = case when cur = 'owner' then 'owner' else p_role end where id = p_worker;
  update members set role = (select role from workers where id = p_worker) where worker_id = p_worker;
end $$;

create or replace function public.remove_worker(p_shop uuid, p_worker uuid)
returns void language plpgsql security definer set search_path = public as $$
begin
  if public.my_role(p_shop) is distinct from 'owner' then raise exception 'not_allowed'; end if;
  delete from workers where id = p_worker and shop_id = p_shop and role <> 'owner';
end $$;

-- ---------- Panel de administrador (solo Dakra Studio) ----------
drop function if exists public.admin_shops();
drop function if exists public.admin_update_shop(uuid, text, text, timestamptz, text);
create or replace function public.admin_shops()
returns table(id uuid, name text, owner_email text, phone text, plan text, tier text, status text, trial_ends timestamptz,
              join_code text, notes text, created_at timestamptz, orders bigint, workers bigint, last_activity timestamptz,
              terms_version text, terms_at timestamptz, paid_until timestamptz, stripe_sub text, ref_code text,
              admin_seen_at timestamptz, stripe_customer text)
language sql stable security definer set search_path = public as $$
  select s.id, s.name, s.owner_email, s.phone, s.plan, s.tier, s.status, s.trial_ends, s.join_code, s.notes, s.created_at,
         (select count(*) from orders o where o.shop_id = s.id),
         (select count(*) from workers w where w.shop_id = s.id),
         greatest((select max(o.updated_at) from orders o where o.shop_id = s.id),
                  (select d.updated_at from shop_data d where d.shop_id = s.id)),
         s.terms_version, s.terms_at, s.paid_until, s.stripe_sub, s.ref_code, s.admin_seen_at, s.stripe_customer
  from shops s where public.is_admin() order by s.created_at desc
$$;

create or replace function public.admin_update_shop(p_shop uuid, p_plan text, p_status text, p_trial_ends timestamptz, p_notes text, p_tier text default null)
returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.is_admin() then raise exception 'not_admin'; end if;
  update shops set plan = p_plan, status = p_status, trial_ends = coalesce(p_trial_ends, trial_ends), notes = p_notes,
                   tier = coalesce(p_tier, tier)
   where id = p_shop;
end $$;

create or replace function public.admin_export(p_shop uuid) returns jsonb
language sql stable security definer set search_path = public as $$
  select case when public.is_admin() then jsonb_build_object(
    'shop',    (select to_jsonb(s) - 'owner_id' from shops s where s.id = p_shop),
    'data',    (select doc from shop_data where shop_id = p_shop),
    'orders',  (select coalesce(jsonb_agg(doc), '[]'::jsonb) from orders where shop_id = p_shop),
    'money',   (select coalesce(jsonb_object_agg(id, doc), '{}'::jsonb) from order_money where shop_id = p_shop),
    'trash',   (select coalesce(jsonb_agg(jsonb_build_object('kind', kind, 'label', label, 'item', item, 'deleted_at', deleted_at)), '[]'::jsonb) from trash where shop_id = p_shop),
    'workers', (select coalesce(jsonb_agg(jsonb_build_object('name', name, 'role', role)), '[]'::jsonb) from workers where shop_id = p_shop))
  end
$$;


-- ---------- Mantener despierta la base de datos ----------
-- Supabase pausa los proyectos gratis sin actividad por 7 días (no borra nada).
-- Un robot de GitHub llama a esta función cada 3 días para que nunca se pause,
-- aunque los talleres se tomen vacaciones.
create table if not exists public.heartbeat(id int primary key default 1, at timestamptz not null default now());
alter table public.heartbeat enable row level security;
revoke all on public.heartbeat from anon, authenticated;
create or replace function public.keep_alive() returns timestamptz
language sql security definer set search_path = public as $$
  insert into heartbeat(id, at) values (1, now()) on conflict (id) do update set at = now() returning at
$$;
grant execute on function public.keep_alive() to anon, authenticated;

-- ---------- Términos y privacidad: quién aceptó, qué versión y cuándo ----------
-- Si cambias la versión en la app, todos (dueños y trabajadores) la vuelven a aceptar al entrar.
create table if not exists public.consents(
  id          bigserial primary key,
  user_id     uuid not null references auth.users(id) on delete cascade,
  shop_id     uuid references public.shops(id) on delete cascade,
  role        text,
  version     text not null,
  accepted_at timestamptz not null default now(),
  agent       text
);
create index if not exists consents_user_idx on public.consents(user_id, version);
alter table public.consents enable row level security;
revoke all on public.consents from anon, authenticated;
grant select on public.consents to authenticated;
drop policy if exists consents_own on public.consents;
create policy consents_own on public.consents for select to authenticated using (user_id = auth.uid() or public.is_admin());

create or replace function public.accept_terms(p_version text, p_shop uuid default null, p_agent text default null)
returns void language plpgsql security definer set search_path = public as $$
declare r text;
begin
  if auth.uid() is null then raise exception 'not_signed_in'; end if;
  if p_shop is not null then
    r := public.my_role(p_shop);
    if r is null then raise exception 'not_member'; end if;
  end if;
  insert into consents(user_id, shop_id, role, version, agent) values (auth.uid(), p_shop, r, left(p_version, 40), left(p_agent, 300));
  if r = 'owner' then update shops set terms_version = left(p_version, 40), terms_at = now() where id = p_shop; end if;
end $$;
grant execute on function public.accept_terms(text, uuid, text) to authenticated;

-- ---------- Promotores (afiliados), pagos y comisiones ----------
-- Cada promotor tiene un código. El taller lo escribe al registrarse (o llega con su enlace).
-- Cada pago que registra un taller (a mano en el panel o solo con Stripe) calcula la comisión automáticamente.
create table if not exists public.promoters(
  id             uuid primary key default gen_random_uuid(),
  code           text not null unique check (code ~ '^[A-Z0-9]{3,20}$'),
  name           text not null,
  phone          text,
  email          text,
  payout         text,                       -- cómo se le paga: Zelle, Cash App, PayPal…
  mode           text not null default 'flat' check (mode in ('flat','recurring')),
  amount         numeric(10,2) not null default 50,  -- flat: dólares por taller · recurring: porcentaje de cada pago
  after_payments int not null default 2,     -- flat: se gana cuando el taller lleva este número de pagos
  months         int not null default 12,    -- recurring: cuántos pagos cuentan
  bonus_days     int not null default 30,    -- días extra de prueba para el taller que usa el código
  active         boolean not null default true,
  notes          text,
  created_at     timestamptz not null default now()
);
create table if not exists public.payments(
  id       bigserial primary key,
  shop_id  uuid not null references public.shops(id) on delete cascade,
  amount   numeric(10,2) not null check (amount >= 0),
  paid_at  timestamptz not null default now(),
  source   text not null default 'manual',   -- manual o stripe
  ext_id   text unique,                      -- id de la factura de Stripe (evita contarla dos veces)
  note     text
);
create table if not exists public.commissions(
  id          bigserial primary key,
  promoter_id uuid not null references public.promoters(id) on delete cascade,
  shop_id     uuid not null references public.shops(id) on delete cascade,
  payment_id  bigint references public.payments(id) on delete set null,
  kind        text not null,                 -- flat (pago único) o month (porcentaje de un pago)
  amount      numeric(10,2) not null,
  status      text not null default 'owed' check (status in ('owed','paid')),
  created_at  timestamptz not null default now(),
  paid_at     timestamptz,
  note        text
);
-- Un promotor también puede ser un taller cliente: gana meses gratis en vez de dinero
alter table public.promoters add column if not exists shop_id uuid references public.shops(id) on delete set null;
alter table public.promoters drop constraint if exists promoters_mode_check;
alter table public.promoters add constraint promoters_mode_check check (mode in ('flat','recurring','credit'));
create unique index if not exists promoters_shop_uq on public.promoters(shop_id) where shop_id is not null;
-- Acuerdo del promotor: enlace privado para aceptarlo y ver sus números; W-9; fin de la relación
alter table public.promoters add column if not exists accept_token     uuid not null default gen_random_uuid();
alter table public.promoters add column if not exists accepted_at      timestamptz;
alter table public.promoters add column if not exists accepted_name    text;
alter table public.promoters add column if not exists accepted_email   text;
alter table public.promoters add column if not exists accepted_version text;
alter table public.promoters add column if not exists accepted_agent   text;
alter table public.promoters add column if not exists w9_received      boolean not null default false;
alter table public.promoters add column if not exists ended_at         timestamptz;
alter table public.promoters add column if not exists end_type         text check (end_type in ('sin_causa','con_causa'));
alter table public.promoters add column if not exists end_reason       text;
create unique index if not exists promoters_token_uq on public.promoters(accept_token);
-- Comisiones anuladas (reembolsos) y descuentos por reembolso
alter table public.commissions drop constraint if exists commissions_status_check;
alter table public.commissions add constraint commissions_status_check check (status in ('owed','paid','void'));
alter table public.payments add column if not exists refunded_at timestamptz;
create index if not exists payments_shop_idx on public.payments(shop_id);
create index if not exists commissions_promoter_idx on public.commissions(promoter_id, status);
alter table public.promoters   enable row level security;
alter table public.payments    enable row level security;
alter table public.commissions enable row level security;
revoke all on public.promoters, public.payments, public.commissions from anon, authenticated;
grant select, insert, update on public.promoters, public.payments, public.commissions to authenticated;
grant usage, select on sequence public.payments_id_seq, public.commissions_id_seq to authenticated;
drop policy if exists promoters_admin on public.promoters;
create policy promoters_admin on public.promoters for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists payments_admin on public.payments;
create policy payments_admin on public.payments for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists commissions_admin on public.commissions;
create policy commissions_admin on public.commissions for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- Calcula la comisión sola cada vez que entra un pago
-- Mes gratis para el taller que recomendó: se aplica solo cuando se puede.
--  · En prueba: se le suman 30 días.   · Cortesía: no lo necesita.
--  · Paga con Stripe: el webhook le pone saldo a favor en Stripe (su siguiente mes sale gratis).
--  · Paga a mano: queda en Pendientes para que no le cobres un mes.
create or replace function public.apply_credit(p_id bigint) returns text
language plpgsql security definer set search_path = public as $$
declare c commissions; rs shops;
begin
  select * into c from commissions where id = p_id and kind = 'credit' and status = 'owed';
  if not found then return 'none'; end if;
  select s.* into rs from promoters p join shops s on s.id = p.shop_id where p.id = c.promoter_id;
  if not found then return 'manual'; end if;
  if rs.plan = 'trial' then
    update shops set trial_ends = greatest(trial_ends, now()) + interval '30 days' where id = rs.id;
    update commissions set status = 'paid', paid_at = now(), note = 'Se sumaron 30 días a su prueba' where id = p_id;
    return 'trial';
  elsif rs.plan = 'courtesy' then
    update commissions set status = 'paid', paid_at = now(), note = 'Tiene cortesía; no aplica' where id = p_id;
    return 'courtesy';
  elsif rs.stripe_customer is not null then
    return 'stripe';
  end if;
  return 'manual';
end $$;
revoke all on function public.apply_credit(bigint) from public, anon, authenticated;

create or replace function public.payment_commission() returns trigger
language plpgsql security definer set search_path = public as $$
declare pr promoters; n int; cid bigint;
begin
  if new.amount <= 0 then return new; end if;
  select p.* into pr from shops s join promoters p on p.code = s.ref_code where s.id = new.shop_id;
  if not found or pr.end_type = 'con_causa' then return new; end if;
  select count(*) into n from payments where shop_id = new.shop_id and amount > 0 and refunded_at is null;
  if pr.mode in ('flat','credit') then
    if n >= pr.after_payments and (
         (pr.mode = 'flat' and coalesce((select sum(amount) from commissions where promoter_id = pr.id and shop_id = new.shop_id
                                          and kind in ('flat','clawback') and status <> 'void'), 0) <= 0)
      or (pr.mode = 'credit' and not exists(select 1 from commissions where promoter_id = pr.id and shop_id = new.shop_id
                                          and kind = 'credit' and status <> 'void'))) then
      insert into commissions(promoter_id, shop_id, payment_id, kind, amount)
      values (pr.id, new.shop_id, new.id, case when pr.mode = 'credit' then 'credit' else 'flat' end, case when pr.mode = 'credit' then 1 else pr.amount end)
      returning id into cid;
      if pr.mode = 'credit' then perform public.apply_credit(cid); end if;
    end if;
  elsif n <= pr.months then
    insert into commissions(promoter_id, shop_id, payment_id, kind, amount)
    values (pr.id, new.shop_id, new.id, 'month', round(new.amount * pr.amount / 100, 2));
  end if;
  return new;
end $$;
drop trigger if exists payments_commission on public.payments;
create trigger payments_commission after insert on public.payments for each row execute function public.payment_commission();

-- El dueño escribe el código del promotor (una sola vez). Si está en prueba, gana los días extra.
create or replace function public.set_referral(p_shop uuid, p_code text) returns text
language plpgsql security definer set search_path = public as $$
declare c text := upper(regexp_replace(coalesce(p_code, ''), '[^A-Za-z0-9]', '', 'g')); pr promoters; s shops;
begin
  if public.my_role(p_shop) is distinct from 'owner' then raise exception 'not_owner'; end if;
  select * into s from shops where id = p_shop;
  if s.ref_code is not null then return 'already'; end if;
  if s.created_at < now() - interval '30 days' then return 'late'; end if;
  select * into pr from promoters where code = c and active and ended_at is null;
  if not found or pr.shop_id = p_shop or (pr.mode <> 'credit' and pr.accepted_at is null) then return 'invalid'; end if;
  update shops set ref_code = c, ref_at = now(),
         trial_ends = case when plan = 'trial' and pr.bonus_days > 0
                           then greatest(trial_ends, now()) + make_interval(days => pr.bonus_days) else trial_ends end
   where id = p_shop;
  return 'ok';
end $$;
grant execute on function public.set_referral(uuid, text) to authenticated;

-- Cada taller tiene su propio enlace para recomendar a otros talleres (gana 1 mes gratis por cada uno que se quede pagando)
create or replace function public.my_referral(p_shop uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare pr promoters; s shops; base text; c text; i int := 0;
begin
  if public.my_role(p_shop) is distinct from 'owner' then raise exception 'not_owner'; end if;
  select * into pr from promoters where shop_id = p_shop;
  if not found then
    select * into s from shops where id = p_shop;
    base := left(upper(regexp_replace(coalesce(s.name, 'TALLER'), '[^A-Za-z0-9]', '', 'g')), 10);
    if length(base) < 3 then base := 'TALLER'; end if;
    loop
      c := base || lpad((floor(random() * 90) + 10)::int::text, 2, '0');
      exit when not exists(select 1 from promoters where code = c);
      i := i + 1; if i > 50 then c := base || floor(random() * 9000 + 1000)::int::text; exit; end if;
    end loop;
    insert into promoters(code, name, phone, mode, amount, after_payments, bonus_days, shop_id, notes)
    values (c, coalesce(s.name, 'Taller'), s.phone, 'credit', 1, 2, 30, p_shop, 'Taller cliente (enlace creado desde la app)')
    returning * into pr;
  end if;
  return jsonb_build_object('code', pr.code, 'active', pr.active,
    'referred', (select count(*) from shops where ref_code = pr.code),
    'earned', (select count(*) from commissions where promoter_id = pr.id and kind = 'credit'));
end $$;
grant execute on function public.my_referral(uuid) to authenticated;

-- Panel: marcar un mes gratis como ya aplicado a mano (talleres que pagan sin Stripe)
create or replace function public.admin_apply_credit(p_id bigint, p_note text default null) returns text
language plpgsql security definer set search_path = public as $$
declare r text;
begin
  if not public.is_admin() then raise exception 'not_admin'; end if;
  r := public.apply_credit(p_id);
  if r in ('manual', 'stripe') then
    update commissions set status = 'paid', paid_at = now(), note = coalesce(p_note, 'Aplicado a mano: no se le cobró un mes') where id = p_id;
  end if;
  return r;
end $$;
grant execute on function public.admin_apply_credit(bigint, text) to authenticated;

-- Reembolso: el pago deja de contar; su comisión se anula, o si ya se pagó, se descuenta de la siguiente
create or replace function public.refund_payment(p_id bigint) returns void
language plpgsql security definer set search_path = public as $$
declare c commissions;
begin
  update payments set refunded_at = coalesce(refunded_at, now()) where id = p_id;
  for c in select * from commissions where payment_id = p_id and kind <> 'clawback' loop
    if c.status = 'owed' then
      update commissions set status = 'void', note = 'Anulada: el pago se reembolsó' where id = c.id;
    elsif c.status = 'paid' and c.kind <> 'credit' and not exists(select 1 from commissions where payment_id = p_id and kind = 'clawback' and promoter_id = c.promoter_id) then
      insert into commissions(promoter_id, shop_id, payment_id, kind, amount, note)
      values (c.promoter_id, c.shop_id, p_id, 'clawback', -c.amount, 'Descuento: el taller recibió reembolso');
    end if;
  end loop;
end $$;
revoke all on function public.refund_payment(bigint) from public, anon, authenticated;
grant execute on function public.refund_payment(bigint) to service_role;
create or replace function public.admin_refund_payment(p_id bigint) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.is_admin() then raise exception 'not_admin'; end if;
  perform public.refund_payment(p_id);
end $$;
grant execute on function public.admin_refund_payment(bigint) to authenticated;

-- Portal del promotor (con su enlace privado): ver su acuerdo, aceptarlo y ver sus números.
-- Solo ve el nombre y el estado de los talleres que él trajo; nunca datos del taller.
create or replace function public.promoter_portal(p_token uuid) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare pr promoters;
begin
  select * into pr from promoters where accept_token = p_token;
  if not found then return null; end if;
  return jsonb_build_object(
    'name', pr.name, 'code', pr.code, 'mode', pr.mode, 'amount', pr.amount, 'after_payments', pr.after_payments,
    'months', pr.months, 'bonus_days', pr.bonus_days, 'active', pr.active and pr.ended_at is null, 'payout', pr.payout,
    'accepted_at', pr.accepted_at, 'accepted_name', pr.accepted_name, 'accepted_version', pr.accepted_version,
    'ended_at', pr.ended_at, 'end_type', pr.end_type,
    'shops', coalesce((select jsonb_agg(jsonb_build_object('name', s.name, 'since', s.ref_at,
        'status', case when s.status <> 'active' then 'paused' when s.plan in ('paid','founder') then 'paying' when s.plan = 'trial' then 'trial' else 'other' end) order by s.ref_at)
      from shops s where s.ref_code = pr.code), '[]'::jsonb),
    'owed', coalesce((select sum(amount) from commissions where promoter_id = pr.id and status = 'owed' and kind <> 'credit'), 0),
    'payable', coalesce((select sum(amount) from commissions where promoter_id = pr.id and status = 'owed' and kind <> 'credit'
                          and (kind = 'clawback' or created_at <= now() - interval '30 days')), 0),
    'paid', coalesce((select sum(amount) from commissions where promoter_id = pr.id and status = 'paid' and kind <> 'credit'), 0),
    'payouts', coalesce((select jsonb_agg(jsonb_build_object('date', d, 'amount', t) order by d desc)
      from (select paid_at::date d, sum(amount) t from commissions where promoter_id = pr.id and status = 'paid' and kind <> 'credit' group by 1) x), '[]'::jsonb));
end $$;
grant execute on function public.promoter_portal(uuid) to anon, authenticated;

create or replace function public.promoter_accept(p_token uuid, p_name text, p_email text, p_payout text, p_version text, p_agent text default null)
returns text language plpgsql security definer set search_path = public as $$
declare pr promoters;
begin
  select * into pr from promoters where accept_token = p_token;
  if not found then return 'invalid'; end if;
  if length(trim(coalesce(p_name, ''))) < 3 then return 'name'; end if;
  update promoters set accepted_at = now(), accepted_name = left(trim(p_name), 120), accepted_email = left(nullif(trim(coalesce(p_email, '')), ''), 160),
         accepted_version = left(p_version, 40), accepted_agent = left(p_agent, 300),
         payout = coalesce(nullif(left(trim(coalesce(p_payout, '')), 160), ''), payout),
         email = coalesce(email, left(nullif(trim(coalesce(p_email, '')), ''), 160))
   where id = pr.id;
  return 'ok';
end $$;
grant execute on function public.promoter_accept(uuid, text, text, text, text, text) to anon, authenticated;

-- Panel: marcar un taller como revisado
create or replace function public.admin_seen(p_shop uuid) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.is_admin() then raise exception 'not_admin'; end if;
  update shops set admin_seen_at = now() where id = p_shop;
end $$;
grant execute on function public.admin_seen(uuid) to authenticated;

-- Para el panel: poner o quitar a mano quién recomendó a un taller (sin días extra)
create or replace function public.admin_set_ref(p_shop uuid, p_code text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.is_admin() then raise exception 'not_admin'; end if;
  update shops set ref_code = nullif(upper(regexp_replace(coalesce(p_code, ''), '[^A-Za-z0-9]', '', 'g')), ''),
                   ref_at = case when coalesce(p_code, '') = '' then null else coalesce(ref_at, now()) end
   where id = p_shop;
end $$;
grant execute on function public.admin_set_ref(uuid, text) to authenticated;

-- ---------- Fotos ----------
insert into storage.buckets(id, name, public) values ('photos', 'photos', false) on conflict (id) do nothing;

drop policy if exists colorbay_photos_read   on storage.objects;
drop policy if exists colorbay_photos_insert on storage.objects;
drop policy if exists colorbay_photos_update on storage.objects;
drop policy if exists colorbay_photos_delete on storage.objects;
create policy colorbay_photos_read   on storage.objects for select to authenticated
  using (bucket_id = 'photos' and public.can_use(((storage.foldername(name))[1])::uuid));
create policy colorbay_photos_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'photos' and public.can_use(((storage.foldername(name))[1])::uuid));
create policy colorbay_photos_update on storage.objects for update to authenticated
  using (bucket_id = 'photos' and public.can_use(((storage.foldername(name))[1])::uuid));
create policy colorbay_photos_delete on storage.objects for delete to authenticated
  using (bucket_id = 'photos' and public.can_use(((storage.foldername(name))[1])::uuid));

-- ---------- Cambios en vivo entre celulares ----------
do $$ begin
  begin alter publication supabase_realtime add table public.orders;    exception when others then null; end;
  begin alter publication supabase_realtime add table public.shop_data; exception when others then null; end;
  begin alter publication supabase_realtime add table public.order_money; exception when others then null; end;
end $$;
