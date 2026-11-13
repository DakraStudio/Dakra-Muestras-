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

-- El taller está abierto si está activo y, si es prueba, no ha vencido.
create or replace function public.shop_open(s uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from shops where id = s and status = 'active'
                and (plan <> 'trial' or trial_ends > now()))
$$;

create or replace function public.can_use(s uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select (public.my_role(s) is not null and public.shop_open(s)) or public.is_admin()
$$;

-- ---------- Seguridad por fila ----------
alter table public.platform_admins enable row level security;
alter table public.shops           enable row level security;
alter table public.workers         enable row level security;
alter table public.members         enable row level security;
alter table public.shop_data       enable row level security;
alter table public.orders          enable row level security;
alter table public.join_fails      enable row level security;

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
  insert into workers(shop_id, name, role, pin_hash) values (p_shop, p_name, p_role, crypt(p_pin, gen_salt('bf'))) returning id into w;
  return w;
end $$;

create or replace function public.remove_worker(p_shop uuid, p_worker uuid)
returns void language plpgsql security definer set search_path = public as $$
begin
  if public.my_role(p_shop) is distinct from 'owner' then raise exception 'not_allowed'; end if;
  delete from workers where id = p_worker and shop_id = p_shop and role <> 'owner';
end $$;

-- ---------- Panel de administrador (solo Dakra Studio) ----------
create or replace function public.admin_shops()
returns table(id uuid, name text, owner_email text, phone text, plan text, status text, trial_ends timestamptz,
              join_code text, notes text, created_at timestamptz, orders bigint, workers bigint, last_activity timestamptz)
language sql stable security definer set search_path = public as $$
  select s.id, s.name, s.owner_email, s.phone, s.plan, s.status, s.trial_ends, s.join_code, s.notes, s.created_at,
         (select count(*) from orders o where o.shop_id = s.id),
         (select count(*) from workers w where w.shop_id = s.id),
         greatest((select max(o.updated_at) from orders o where o.shop_id = s.id),
                  (select d.updated_at from shop_data d where d.shop_id = s.id))
  from shops s where public.is_admin() order by s.created_at desc
$$;

create or replace function public.admin_update_shop(p_shop uuid, p_plan text, p_status text, p_trial_ends timestamptz, p_notes text)
returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.is_admin() then raise exception 'not_admin'; end if;
  update shops set plan = p_plan, status = p_status, trial_ends = coalesce(p_trial_ends, trial_ends), notes = p_notes
   where id = p_shop;
end $$;

create or replace function public.admin_export(p_shop uuid) returns jsonb
language sql stable security definer set search_path = public as $$
  select case when public.is_admin() then jsonb_build_object(
    'shop',    (select to_jsonb(s) - 'owner_id' from shops s where s.id = p_shop),
    'data',    (select doc from shop_data where shop_id = p_shop),
    'orders',  (select coalesce(jsonb_agg(doc), '[]'::jsonb) from orders where shop_id = p_shop),
    'workers', (select coalesce(jsonb_agg(jsonb_build_object('name', name, 'role', role)), '[]'::jsonb) from workers where shop_id = p_shop))
  end
$$;

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
end $$;
