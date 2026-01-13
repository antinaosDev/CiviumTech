-- Add 'depto' column to tickets to match Python filtering logic
ALTER TABLE public.tickets 
ADD COLUMN IF NOT EXISTS depto text;

-- Optional: Index for performance
CREATE INDEX IF NOT EXISTS idx_tickets_depto ON public.tickets(depto);
