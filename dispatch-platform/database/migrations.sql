CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.dispatch_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    compute_target TEXT NOT NULL CHECK (compute_target IN ('LOCAL_GPU', 'NEBIUS_CLOUD')),
    raw_payload JSONB NOT NULL,
    graph_data JSONB,
    hamiltonian_spec JSONB,
    optimal_bitstring TEXT,
    solution_json JSONB,
    telemetry JSONB
);

CREATE INDEX IF NOT EXISTS idx_dispatch_runs_user_id ON public.dispatch_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_dispatch_runs_created_at ON public.dispatch_runs(created_at DESC);

ALTER TABLE public.dispatch_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own dispatch runs" 
ON public.dispatch_runs FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own dispatch runs" 
ON public.dispatch_runs FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own dispatch runs" 
ON public.dispatch_runs FOR UPDATE 
USING (auth.uid() = user_id);