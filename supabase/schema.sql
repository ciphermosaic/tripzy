-- Run this once in the Supabase SQL editor for the Tripzy project.
create table if not exists public.trips (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  destination text not null,
  days integer not null check (days between 1 and 14),
  travelers integer not null check (travelers between 1 and 20),
  trip_data jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists trips_user_created_at_idx
  on public.trips (user_id, created_at desc);

alter table public.trips enable row level security;

create policy "Users can read their own trips"
  on public.trips for select to authenticated
  using (auth.uid() = user_id);
