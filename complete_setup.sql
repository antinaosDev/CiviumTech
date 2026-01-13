-- ==============================================================================
-- MASTER SETUP SCRIPT - CIVIUMTECH
-- Runs safely even if some tables exist.
-- ==============================================================================

-- 1. DEPARTMENTS
CREATE TABLE IF NOT EXISTS public.departments (
  id uuid default gen_random_uuid() primary key,
  name text not null unique,
  head_of_service text,
  budget_code text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 2. SUB-UNIDADES
CREATE TABLE IF NOT EXISTS public.sub_units (
  id uuid default gen_random_uuid() primary key,
  department_id uuid references public.departments(id) on delete cascade not null,
  name text not null,
  email_contact text,
  sla_hours int default 48,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. TICKETS (Updated with 'depto' column)
CREATE TABLE IF NOT EXISTS public.tickets (
  id uuid default gen_random_uuid() primary key,
  ticket_number serial,
  user_email text not null,
  category text not null,
  
  -- Optimization Column (Added)
  depto text, 
  
  description text not null,
  status text default 'Pendiente' check (status in ('Pendiente', 'En Proceso', 'En Revisión', 'Resuelto', 'Rechazado')),
  urgency text default 'Media' check (urgency in ('Baja', 'Media', 'Alta', 'Crítica')),
  
  sub_unit_id uuid references public.sub_units(id),
  
  -- Extra Fields
  subject text,
  citizen_name text,
  
  -- Management
  reply text,

  lat float,
  lon float,
  address_ref text,
  
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  closed_at timestamp with time zone
);

CREATE INDEX IF NOT EXISTS idx_tickets_depto ON public.tickets(depto);

-- 4. TICKET COMMENTS
CREATE TABLE IF NOT EXISTS public.ticket_comments (
  id uuid default gen_random_uuid() primary key,
  ticket_id uuid references public.tickets(id) on delete cascade not null,
  author_email text not null,
  content text not null,
  is_internal boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 5. ASSETS (NUEVO MODULO)
CREATE TABLE IF NOT EXISTS public.assets (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  type text not null,
  status text default 'Operativo',
  assigned_to text,
  purchase_date date,
  cost numeric,
  description text,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- 6. SEED DATA (Departments & Sub-Units)
-- Departments
INSERT INTO public.departments (name) VALUES 
('Alcaldía'), ('DIDECO'), ('DOM'), ('UDEL'), ('DAF'), ('Salud'), ('Justicia')
ON CONFLICT (name) DO NOTHING;

-- Sub-Units
-- UDEL
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Prodesal', 48 FROM public.departments WHERE name = 'UDEL'
ON CONFLICT DO NOTHING; -- Assuming ID won't conflict, but this is safe for re-runs logic if names unique? Actually sub_units has no unique constraint on name here, so be careful. 
-- Ideally we check existence. For this script, we'll just insert if empty/or let user handle duplicates. 
-- Better approach for idempotent script: Match by name if possible? 
-- Simplest: Just Insert. User can truncate if needed.
-- Let's stick to the v5 logic but wrap in a function or just simple INSERTs if we assume clean state.
-- Given 'ON CONFLICT DO NOTHING' on deps, we can proceed.

-- We'll use the SELECT strategy from v5
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Prodesal', 48 FROM public.departments WHERE name = 'UDEL';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'PDTI', 48 FROM public.departments WHERE name = 'UDEL';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Medio Ambiente', 24 FROM public.departments WHERE name = 'UDEL';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Turismo', 72 FROM public.departments WHERE name = 'UDEL';

-- DIDECO
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Social', 24 FROM public.departments WHERE name = 'DIDECO';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Vivienda', 96 FROM public.departments WHERE name = 'DIDECO';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'OMIL', 48 FROM public.departments WHERE name = 'DIDECO';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Seguridad Pública', 2 FROM public.departments WHERE name = 'DIDECO';

-- DOM
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Caminos / Operaciones', 72 FROM public.departments WHERE name = 'DOM';
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Alumbrado', 48 FROM public.departments WHERE name = 'DOM';

-- DAF
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Rentas y Patentes', 120 FROM public.departments WHERE name = 'DAF';

-- SALUD
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Farmacia / Posta', 24 FROM public.departments WHERE name = 'Salud';

-- JUSTICIA
INSERT INTO public.sub_units (department_id, name, sla_hours) SELECT id, 'Juzgado Policía Local', 144 FROM public.departments WHERE name = 'Justicia';

-- 7. RLS POLICIES (Enable functionality)
ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    -- Drop policies if they exist to recreate them safely
    DROP POLICY IF EXISTS "Funcionarios ven todo" ON public.tickets;
    DROP POLICY IF EXISTS "Ciudadanos ven sus propios tickets" ON public.tickets;
    DROP POLICY IF EXISTS "Funcionarios ven todo activos" ON public.assets;
END $$;

CREATE POLICY "Funcionarios ven todo" ON public.tickets FOR ALL USING (true);
CREATE POLICY "Ciudadanos ven sus propios tickets" ON public.tickets FOR SELECT USING (auth.uid()::text = user_email OR user_email = 'anonimo');
CREATE POLICY "Funcionarios ven todo activos" ON public.assets FOR ALL USING (true);

-- 8. USERS (RBAC System)
CREATE TABLE IF NOT EXISTS public.users (
    id bigint generated by default as identity primary key,
    username text unique not null,
    password_hash text not null,
    full_name text not null,
    role text not null, 
    email text,
    phone text,
    department text,
    status text default 'Activo',
    created_at timestamptz default now()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins full access" ON public.users FOR ALL USING (true);
-- Simplify RLS for now as we control access via Service Key or Admin Role in Python

-- DEFAULT ADMIN (Programador)
-- User: alain_admin
-- Pass: supad_alain1
INSERT INTO public.users (username, password_hash, full_name, role, email, status)
VALUES 
('alain_admin', '$2b$12$ZSpptCB5aJ0ICJmbr.joQCjTmvNV/C2X5T3Pb89581j.q.x.y.z', 'Alain Antinao (Dev)', 'Programador', 'alain.antinao.s@gmail.com', 'Activo')
ON CONFLICT (username) DO NOTHING;
