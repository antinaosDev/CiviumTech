-- ==============================================================================
-- MUNISMART CHOLCHOL V5: ESQUEMA DE BASE DE DATOS GOVTECH
-- Arquitecto: Senior GovTech Dev
-- Descripción: Tablas relacionales para gestión municipal, organigrama y tickets.
-- ==============================================================================

-- 1. TABLA MAESTRA DE DEPARTAMENTOS (Direcciones)
create table public.departments (
  id uuid default gen_random_uuid() primary key,
  name text not null unique, -- Ej: DIDECO, DOM, UDEL
  head_of_service text, -- Nombre del Director
  budget_code text, -- Código Presupuestario (Simulado)
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 2. TABLA DE SUB-UNIDADES (Oficinas Específicas)
create table public.sub_units (
  id uuid default gen_random_uuid() primary key,
  department_id uuid references public.departments(id) on delete cascade not null,
  name text not null, -- Ej: OMIL, Prodesal, Caminos
  email_contact text, -- Email jefatura unidad
  sla_hours int default 48, -- Tiempo máximo respuesta
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. TABLA DE TICKETS (Solicitudes Ciudadanas)
create table public.tickets (
  id uuid default gen_random_uuid() primary key,
  ticket_number serial, -- Correlativo simple (REQ-1, REQ-2)
  user_email text not null, -- Email del ciudadano (Auth linkeado conceptualmente)
  category text not null, -- Ej: "Reparación de Camino"
  description text not null,
  status text default 'Pendiente' check (status in ('Pendiente', 'En Proceso', 'Resuelto', 'Rechazado')),
  urgency text default 'Media' check (urgency in ('Baja', 'Media', 'Alta', 'Critica')),
  
  -- Derivación Automática
  sub_unit_id uuid references public.sub_units(id),
  
  -- Georreferenciación
  lat float,
  lon float,
  address_ref text,
  
  -- Trazabilidad
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  closed_at timestamp with time zone
);

-- 4. TABLA DE COMENTARIOS / TRAZABILIDAD (Chat Interno)
create table public.ticket_comments (
  id uuid default gen_random_uuid() primary key,
  ticket_id uuid references public.tickets(id) on delete cascade not null,
  author_email text not null, -- Quién escribió
  content text not null,
  is_internal boolean default false, -- TRUE = Solo funcionarios, FALSE = Visible ciudadano
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ==============================================================================
-- SEED DATA (POBLADO INICIAL SEGÚN ORGANIGRAMA REAL)
-- ==============================================================================

-- DIRECTORIOS PRINCIPALES
INSERT INTO public.departments (name) VALUES 
('Alcaldía'), ('DIDECO'), ('DOM'), ('UDEL'), ('DAF'), ('Salud'), ('Justicia');

-- SUB-UNIDADES (Mapeo estricto del Prompt)
-- UDEL
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Prodesal', 48 FROM public.departments WHERE name = 'UDEL';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'PDTI', 48 FROM public.departments WHERE name = 'UDEL';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Medio Ambiente', 24 FROM public.departments WHERE name = 'UDEL';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Turismo', 72 FROM public.departments WHERE name = 'UDEL';

-- DIDECO
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Social', 24 FROM public.departments WHERE name = 'DIDECO';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Vivienda', 96 FROM public.departments WHERE name = 'DIDECO';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'OMIL', 48 FROM public.departments WHERE name = 'DIDECO';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Seguridad Pública', 2 FROM public.departments WHERE name = 'DIDECO';

-- DOM
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Caminos / Operaciones', 72 FROM public.departments WHERE name = 'DOM';
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Alumbrado', 48 FROM public.departments WHERE name = 'DOM';

-- DAF
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Rentas y Patentes', 120 FROM public.departments WHERE name = 'DAF';

-- SALUD
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Farmacia / Posta', 24 FROM public.departments WHERE name = 'Salud';

-- JUSTICIA
INSERT INTO public.sub_units (department_id, name, sla_hours)
SELECT id, 'Juzgado Policía Local', 144 FROM public.departments WHERE name = 'Justicia';

-- ==============================================================================
-- POLÍTICAS DE SEGURIDAD (RLS) - SIMPLIFICADO PARA PROTOTIPO
-- ==============================================================================
alter table public.tickets enable row level security;

-- 1. Ciudadanos ven SOLO sus tickets
create policy "Ciudadanos ven sus propios tickets"
on public.tickets for select
using (auth.uid()::text = user_email OR user_email = 'anonimo');

-- 2. Admins/Funcionarios ven TODO (En prod se refina por rol en JWT)
create policy "Funcionarios ven todo"
on public.tickets for all
using (true); 
