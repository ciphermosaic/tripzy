# Tripzy — Project Memory

Last updated: 2026-09-27

## What was created

This repository started with only product, architecture, and phase documents. A working MVP structure was created from scratch:

- `frontend/` — React + Vite + TypeScript client
- `backend/` — FastAPI service
- `README.md` — local setup instructions
- `.gitignore` and environment-variable examples

## Implemented frontend

- Editorial, responsive Tripzy landing page with navigation, hero, planner, process section, itinerary, budget view, and contextual chat interface.
- Natural-language planner form that calls `POST /api/trips/plan`.
- Chat UI that calls `POST /api/chat` and can update a currently loaded itinerary.
- Visual map-style itinerary panel and budget breakdown.
- A real WebGL 3D globe was added in `frontend/src/GlobeScene.tsx` using Three.js / React Three Fiber. It includes rotation, star field, destination lights, and curved travel-route arcs.
- `frontend/src/globe.css` supplies responsive sizing for the 3D canvas.

## Implemented backend

- FastAPI app in `backend/app/main.py` with `/health`, `/api/trips/plan`, and `/api/chat`.
- Tool-first data layer in `backend/app/services/travel_data.py`:
  - Nominatim geocoding
  - Overpass / OpenStreetMap places
  - Open-Meteo weather
  - OSRM route geometry
- Deterministic itinerary engine in `backend/app/services/planner.py` with date, budget, and destination inference.
- Chat supports simple changes such as cheaper, relaxed / less travel, and remove stop, as well as packing and weather answers.
- The current planner deliberately works without an LLM key. `GROQ_API_KEY` remains documented as a future enhancement, but LangGraph/Groq are **not wired in yet**.

## Dependencies and local environment

- Frontend packages were installed successfully. `frontend/node_modules` and `frontend/package-lock.json` now exist.
- Added frontend 3D packages: `three`, `@react-three/fiber`, and `@react-three/drei`.
- Python was not available in the execution environment. Therefore FastAPI dependencies and backend tests could not be installed/run here.
- A prior Vite static preview at port 5173 returned HTTP 200 before the 3D changes. Attempts to start a separate dev server on port 5174 did not remain reachable. All Vite processes started for this workspace were stopped at the user’s request.

## Current status

Source changes are saved. No local project preview server should be running after this handoff.

The 3D source is present but needs a clean local verification:

```powershell
cd frontend
npm install
npm run dev
```

Then visit `http://localhost:5173`.

For the backend, install Python 3.11+ first, then:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Recommended next phases

1. Verify and refine the 3D globe in-browser, including a `prefers-reduced-motion` / WebGL fallback.
2. Install and run Python; validate FastAPI endpoints and tool failures.
3. Replace the placeholder visual map with Leaflet + OpenStreetMap markers and route polylines.
4. Add a real LangGraph + Groq planning/modification workflow behind the existing API, keeping tool data authoritative.
5. Add tests, persistence (Supabase), authentication, Docker, and deployment only after the planning path is stable.
