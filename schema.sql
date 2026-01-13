-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. UTILS (Enums)
create type user_role as enum ('PROGRAMADOR', 'ADMIN', 'USER_CIUDADANO', 'USER_FUNCIONARIO');
create type ticket_status as enum ('RECIBIDO', 'EN_PROCESO', 'FINALIZADO');
create type ticket_priority as enum ('BAJA', 'MEDIA', 'ALTA', 'URGENTE');

-- 2. DEPARTMENTS (Organigrama)
create table public.departments (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    parent_id uuid references public.departments(id),
    code text unique -- Human readable code for routing logic (e.g. 'DIDECO', 'DOM')
);

-- 3. USERS (Profiles)
create table public.users (
    id uuid references auth.users(id) on delete cascade primary key,
    email text,
    full_name text,
    role user_role default 'USER_CIUDADANO',
    department_id uuid references public.departments(id), -- Null for citizens
    created_at timestamptz default now()
);

-- 4. TICKETS
create table public.tickets (
    id uuid primary key default uuid_generate_v4(),
    ticket_number serial, -- For easy reference like #105
    title text not null,
    description text not null,
    category text not null,
    subcategory text,
    status ticket_status default 'RECIBIDO',
    priority ticket_priority default 'MEDIA',
    
    user_id uuid references public.users(id) not null, -- Creator
    assigned_department_id uuid references public.departments(id),
    
    evidence_url text, -- Link to Supabase Storage
    
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- 5. ROW LEVEL SECURITY (RLS)

-- Enable RLS
alter table public.users enable row level security;
alter table public.tickets enable row level security;
alter table public.departments enable row level security;

-- POLICIES FOR DEPARTMENTS
-- Everyone can read departments (to select in forms)
create policy "Departments are viewable by everyone" 
on public.departments for select using (true);

-- Only PROGRAMADOR can insert/update/delete departments (handled manually or by super admin)
create policy "Programmer can manage departments" 
on public.departments for all 
using ( (select role from public.users where id = auth.uid()) = 'PROGRAMADOR' );


-- POLICIES FOR USERS
-- Users can read their own profile
create policy "Users can view own profile" 
on public.users for select 
using ( auth.uid() = id );

-- Admins and Programmers can view all profiles
create policy "Admins/Programmers can view all profiles"
on public.users for select
using ( 
  (select role from public.users where id = auth.uid()) in ('ADMIN', 'PROGRAMADOR') 
);

-- POLICIES FOR TICKETS

-- 1. PROGRAMADOR: All Access
create policy "Programmer full access tickets"
on public.tickets for all
using ( (select role from public.users where id = auth.uid()) = 'PROGRAMADOR' );

-- 2. ADMIN (Director): Access to tickets in their department (OR sub-departments if we implement recursive logic, for now direct match)
create policy "Admin view tickets in dept"
on public.tickets for select
using (
  (select role from public.users where id = auth.uid()) = 'ADMIN' 
  AND 
  assigned_department_id = (select department_id from public.users where id = auth.uid())
);

create policy "Admin update tickets in dept"
on public.tickets for update
using (
  (select role from public.users where id = auth.uid()) = 'ADMIN' 
  AND 
  assigned_department_id = (select department_id from public.users where id = auth.uid())
);

-- 3. FUNCIONARIO: View assigned tickets (Currently assigned to Dept. We could add assigned_to_user_id for more granularity, keeping it simple as requested)
-- Assuming Officials see all tickets in their specific Unit (Department)
create policy "Funcionario view tickets in their unit"
on public.tickets for select
using (
  (select role from public.users where id = auth.uid()) = 'USER_FUNCIONARIO' 
  AND 
  assigned_department_id = (select department_id from public.users where id = auth.uid())
);

create policy "Funcionario update tickets in their unit"
on public.tickets for update
using (
  (select role from public.users where id = auth.uid()) = 'USER_FUNCIONARIO' 
  AND 
  assigned_department_id = (select department_id from public.users where id = auth.uid())
);

-- 4. CITIZEN: View and Create own tickets
create policy "Citizens can view own tickets"
on public.tickets for select
using (
  user_id = auth.uid()
);

create policy "Citizens can create tickets"
on public.tickets for insert
with check (
  auth.uid() = user_id
);


-- SEED DATA (Organigrama Cholchol)
-- Uses a DO block to insert and link IDs

DO $$
DECLARE
    -- Top Level
    v_alcaldia uuid;
    v_dideco uuid;
    v_dom uuid;
    v_daf uuid;
    v_otras uuid;
BEGIN
    -- 1. ALCALDÍA
    insert into public.departments (name, code) values ('Alcaldía y Administración', 'ALC') returning id into v_alcaldia;
    
    insert into public.departments (name, code, parent_id) values 
    ('Alcalde', 'ALC_ALCALDE', v_alcaldia),
    ('Concejo Municipal', 'ALC_CONCEJO', v_alcaldia),
    ('Administración Municipal', 'ALC_ADMIN', v_alcaldia),
    ('Secretaría Municipal', 'ALC_SEC', v_alcaldia),
    ('Asesoría Jurídica', 'ALC_JURIDICA', v_alcaldia),
    ('Control (Transparencia)', 'ALC_CONTROL', v_alcaldia),
    ('Gabinete (Prensa)', 'ALC_GABINETE', v_alcaldia),
    ('Informática', 'ALC_IT', v_alcaldia);

    -- 2. DIDECO
    insert into public.departments (name, code) values ('DIDECO (Desarrollo Comunitario)', 'DIDECO') returning id into v_dideco;
    
    insert into public.departments (name, code, parent_id) values 
    ('Ayuda Social', 'DIDECO_SOCIAL', v_dideco),
    ('OMIL', 'DIDECO_OMIL', v_dideco),
    ('Adulto Mayor', 'DIDECO_AM', v_dideco),
    ('Vivienda', 'DIDECO_VIVIENDA', v_dideco),
    ('Autoconsumo', 'DIDECO_AUTO', v_dideco),
    ('Vínculos', 'DIDECO_VINCULOS', v_dideco),
    ('Prog. Puente', 'DIDECO_PUENTE', v_dideco),
    ('Infancia', 'DIDECO_INFANCIA', v_dideco),
    ('Prog. Mujer', 'DIDECO_MUJER', v_dideco),
    ('Seguridad Pública', 'DIDECO_SEGURIDAD', v_dideco),
    ('OLN', 'DIDECO_OLN', v_dideco),
    ('SENDA', 'DIDECO_SENDA', v_dideco),
    ('UDEL', 'DIDECO_UDEL', v_dideco);

    -- 3. DOM
    insert into public.departments (name, code) values ('DOM (Obras Municipales)', 'DOM') returning id into v_dom;

    insert into public.departments (name, code, parent_id) values 
    ('Tránsito', 'DOM_TRANSITO', v_dom),
    ('Operaciones', 'DOM_OPS', v_dom),
    ('Bodega', 'DOM_BODEGA', v_dom);

    -- 4. DAF
    insert into public.departments (name, code) values ('DAF (Administración y Finanzas)', 'DAF') returning id into v_daf;

    insert into public.departments (name, code, parent_id) values 
    ('Finanzas', 'DAF_FINANZAS', v_daf),
    ('Rentas', 'DAF_RENTAS', v_daf),
    ('Patentes', 'DAF_PATENTES', v_daf),
    ('Tesorería', 'DAF_TESORERIA', v_daf),
    ('RRHH', 'DAF_RRHH', v_daf);

    -- 5. OTRAS
    insert into public.departments (name, code) values ('Otras Direcciones', 'OTRAS') returning id into v_otras;
    
    insert into public.departments (name, code, parent_id) values
    ('Educación', 'OTRAS_EDUCACION', v_otras),
    ('Salud', 'OTRAS_SALUD', v_otras),
    ('SECPLAN', 'OTRAS_SECPLAN', v_otras),
    ('Juzgado de Policía Local', 'OTRAS_JPL', v_otras);

END $$;
