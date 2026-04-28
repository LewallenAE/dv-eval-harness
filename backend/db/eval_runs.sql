create table if not exists eval_runs (
  id uuid primary key default gen_random_uuid(),
  actions jsonb not null default '[]'::jsonb,
  case_id text not null,
  constitutional_violations jsonb not null default '[]'::jsonb,
  evidence jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  penalties jsonb not null default '[]'::jsonb,
  proposed_fix text not null default '',
  r_total double precision not null default 0.0,
  root_cause text not null default '',
  scores jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table eval_runs
  add column if not exists actions jsonb not null default '[]'::jsonb,
  add column if not exists case_id text not null default 'unknown',
  add column if not exists constitutional_violations jsonb not null default '[]'::jsonb,
  add column if not exists evidence jsonb not null default '[]'::jsonb,
  add column if not exists metadata jsonb not null default '{}'::jsonb,
  add column if not exists penalties jsonb not null default '[]'::jsonb,
  add column if not exists proposed_fix text not null default '',
  add column if not exists r_total double precision not null default 0.0,
  add column if not exists root_cause text not null default '',
  add column if not exists scores jsonb not null default '{}'::jsonb,
  add column if not exists created_at timestamptz not null default now();

create index if not exists eval_runs_created_at_idx on eval_runs (created_at desc);
create index if not exists eval_runs_case_id_idx on eval_runs (case_id);
