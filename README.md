# Tripzy

An API-driven travel planning MVP with a polished React interface. It turns a natural-language trip request into a weather-aware itinerary using free public data services.

## What works

- Natural-language trip planning (`Plan 4 days in Goa for ₹15,000`)
- Live Nominatim geocoding, Open-Meteo weather, Overpass nearby places, and OSRM route data
- Budget estimate and day-by-day itinerary
- Contextual trip chat for packing/weather questions and simple itinerary changes
- Graceful tool failure behavior; the plan remains usable if nearby places or routing are unavailable

## Run locally

Start the API from `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Start the web app from `frontend` in a second terminal:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Supabase setup

Tripzy uses Supabase email/password authentication and saves each generated
trip for its signed-in user. Run `supabase/schema.sql` once in the Supabase
SQL editor, then fill in the Supabase variables in both `.env` files. The
frontend uses the project URL and anon key; the backend uses the service-role
key, which must never be exposed in a `VITE_` variable or committed to git.

## Notes

The current planning implementation is intentionally deterministic and tool-first so it works with no key. `GROQ_API_KEY` is reserved in `backend/.env.example` for a later structured LLM planning node; it is never sent to the browser. Public API providers have fair-use limits, so production should add caching and a server-side rate limiter.
