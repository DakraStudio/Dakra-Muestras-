-- ColorBay · Candado con PIN (noviembre 2026)
-- Qué hace: cada vez que se abre la app, pide el PIN de 4 dígitos.
-- Cómo instalarlo: Supabase → SQL Editor → New query → pega TODO este archivo → Run. Solo se hace una vez.
-- Mientras no lo corras, la app sigue funcionando igual que antes (sin candado).

create or replace function public.check_pin(p_shop uuid, p_pin text)
returns json language plpgsql security definer set search_path = public, extensions as $$
declare m members; w workers;
begin
  if auth.uid() is null then return json_build_object('error', 'not_signed_in'); end if;
  select * into m from members where user_id = auth.uid() and shop_id = p_shop;
  if m.user_id is null then return json_build_object('error', 'not_member'); end if;
  if (select count(*) from join_fails where shop_id = p_shop and at > now() - interval '15 minutes') >= 20 then
    return json_build_object('error', 'too_many_attempts');
  end if;
  select * into w from workers where shop_id = p_shop and pin_hash = crypt(p_pin, pin_hash) limit 1;
  if w.id is null then
    insert into join_fails(shop_id) values (p_shop);
    return json_build_object('error', 'bad_pin');
  end if;
  if w.id = m.worker_id then return json_build_object('ok', true); end if;
  return json_build_object('other', true, 'role', w.role);
end $$;
revoke all on function public.check_pin(uuid, text) from public, anon;
grant execute on function public.check_pin(uuid, text) to authenticated;
