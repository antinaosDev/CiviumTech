-- MIGRATION SCRIPT FOR MUNISMART CHOLCHOL
-- Run this in your Supabase SQL Editor

-- 1. EXTEND TICKETS TABLE
ALTER TABLE public.tickets 
ADD COLUMN IF NOT EXISTS log JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS is_draft BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS requires_social_report BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS applicant_rut TEXT,
ADD COLUMN IF NOT EXISTS is_indap BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS location_lat FLOAT,
ADD COLUMN IF NOT EXISTS location_lon FLOAT;

-- 2. CREATE NEW DEPARTMENTS (CHOLCHOL SPECIFIC)
DO $$
DECLARE
    v_udel uuid;
    v_dideco uuid;
    v_dom uuid;
    v_daf uuid;
    v_secmu uuid;
    v_salud uuid;
    v_educacion uuid;
BEGIN
    -- UDEL (New Node)
    INSERT INTO public.departments (name, code) VALUES ('UDEL (Desarrollo Económico)', 'UDEL') RETURNING id INTO v_udel;
    INSERT INTO public.departments (name, code, parent_id) VALUES 
        ('Prodesal/PDTI', 'UDEL_AGRO', v_udel),
        ('Medio Ambiente', 'UDEL_AMBIENTE', v_udel),
        ('Turismo', 'UDEL_TURISMO', v_udel);

    -- DIDECO (Update or Insert if missing - simplistic approach: Insert new ones)
    -- We assume the previous 'DIDECO' exists, but let's ensure we have the specific sub-units
    -- Fetch existing DIDECO id if exists, else create
    SELECT id INTO v_dideco FROM public.departments WHERE code = 'DIDECO';
    IF v_dideco IS NULL THEN
         INSERT INTO public.departments (name, code) VALUES ('DIDECO', 'DIDECO') RETURNING id INTO v_dideco;
    END IF;

    -- Ensure DIDECO sub-units
    INSERT INTO public.departments (name, code, parent_id) VALUES 
        ('Asuntos Indígenas', 'DIDECO_INDIGENA', v_dideco)
    ON CONFLICT (code) DO NOTHING; -- Avoid duplicates if code constraint exists

    -- DOM
    SELECT id INTO v_dom FROM public.departments WHERE code = 'DOM';
    IF v_dom IS NULL THEN
         INSERT INTO public.departments (name, code) VALUES ('DOM', 'DOM') RETURNING id INTO v_dom;
    END IF;
    INSERT INTO public.departments (name, code, parent_id) VALUES 
        ('Edificación', 'DOM_EDIFICACION', v_dom)
    ON CONFLICT (code) DO NOTHING;

    -- DAF
    SELECT id INTO v_daf FROM public.departments WHERE code = 'DAF';
    IF v_daf IS NULL THEN
         INSERT INTO public.departments (name, code) VALUES ('DAF', 'DAF') RETURNING id INTO v_daf;
    END IF;
    INSERT INTO public.departments (name, code, parent_id) VALUES 
        ('Adquisiciones', 'DAF_ADQUISICIONES', v_daf)
    ON CONFLICT (code) DO NOTHING;

    -- SECRETARÍA MUNICIPAL
    INSERT INTO public.departments (name, code) VALUES ('Secretaría Municipal', 'SECMU') RETURNING id INTO v_secmu;
    INSERT INTO public.departments (name, code, parent_id) VALUES 
        ('Participación Ciudadana', 'SECMU_PARTICIPACION', v_secmu),
        ('Juntas de Vecinos', 'SECMU_JJVV', v_secmu);

    -- SERVICIOS TRASPASADOS
    -- Check for existing OTRAS_SALUD
    SELECT id INTO v_salud FROM public.departments WHERE code = 'OTRAS_SALUD';
    -- We can update its name or parent if needed, but for now we leave as is or add specific children if needed.
    
END $$;
