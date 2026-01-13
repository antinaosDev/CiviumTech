-- TABLA DE ACTIVOS (Gestión de Patrimonio/Inventario)
create table public.assets (
  id uuid default gen_random_uuid() primary key,
  name text not null, -- Nombre del activo (ej: Camioneta Ford)
  type text not null, -- Tipo (Vehículo, Mobiliario, Equipo Computacional, etc)
  status text default 'Operativo', -- Operativo, En Mantención, De Baja
  assigned_to text, -- Funcionario o Departamento responsable
  purchase_date date,
  cost numeric,
  description text,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- RLS Policies (Simplificado)
alter table public.assets enable row level security;

create policy "Funcionarios ven todo activos"
on public.assets for all
using (true);
